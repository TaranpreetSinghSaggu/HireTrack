from flask_restful import Resource
from flask import current_app, request
from models import db, CompanyProfile, JobPosition, Application, StudentProfile
from utils.jwt_utils import extract_token, decode_token
from datetime import datetime
import os
import json
import requests


FALLBACK_COMPANY_QUESTIONS = [
    "Explain your experience with the main skills required for this role.",
    "How would you solve a real project problem related to this job?",
    "What challenges did you face in a recent technical project?",
    "How do you test and improve the quality of your work?",
    "Why are you a good fit for this position?",
]


def parse_deadline(value):
    if value is None:
        return None

    if not isinstance(value, str):
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def get_company_from_request():
    token = extract_token(request)
    if not token:
        return None, None, ({"error": "Token missing"}, 401)

    data = decode_token(token)
    if "error" in data:
        return None, None, (data, 401)

    if data["role"] != "company":
        return None, None, ({"error": "Access denied"}, 403)

    company = CompanyProfile.query.filter_by(user_id=data["user_id"]).first()
    if not company:
        return None, None, ({"error": "Company not found"}, 404)

    return data, company, None


def get_company_job(company, job_id):
    job = JobPosition.query.get(job_id)
    if not job:
        return None, ({"error": "Job not found"}, 404)

    if job.company_id != company.id:
        return None, ({"error": "Unauthorized"}, 403)

    return job, None


def normalize_skills(value):
    if not value:
        return []

    text = str(value).lower()
    for separator in ["\n", ";", "|", "/"]:
        text = text.replace(separator, ",")

    skills = []
    for part in text.split(","):
        skill = part.strip()
        if skill and skill not in skills:
            skills.append(skill)

    return skills


def calculate_candidate_match(student, job):
    student_skills = normalize_skills(student.skills)
    job_skills = normalize_skills(job.skills_required)

    matched_skills = [skill for skill in job_skills if skill in student_skills]
    missing_skills = [skill for skill in job_skills if skill not in student_skills]

    skills_score = 0
    if job_skills:
        skills_score = int((len(matched_skills) / len(job_skills)) * 70)

    cgpa_score = 30
    if job.min_cgpa is not None:
        if student.cgpa is None or student.cgpa < job.min_cgpa:
            cgpa_score = 0

    score = min(skills_score + cgpa_score, 100)

    if score >= 80 and not missing_skills:
        decision_hint = "Strong candidate"
    elif score >= 60:
        if missing_skills:
            decision_hint = f"Good candidate but needs {missing_skills[0]}"
        else:
            decision_hint = "Good candidate"
    else:
        if missing_skills:
            decision_hint = f"Weak match, missing {missing_skills[0]}"
        else:
            decision_hint = "Weak match"

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "breakdown": {
            "skills_score": skills_score,
            "cgpa_score": cgpa_score,
        },
        "decision_hint": decision_hint,
    }


def is_student_match(student, job):
    job_skills = normalize_skills(job.skills_required)
    student_skills = normalize_skills(student.skills)

    if job.min_cgpa is not None:
        if student.cgpa is None or student.cgpa < job.min_cgpa:
            return False

    if not job_skills:
        return True

    matched = [skill for skill in job_skills if skill in student_skills]
    return len(matched) > 0


def generate_job_questions(job):
    api_key = current_app.config["AIPIPE_API_KEY"]
    if not api_key:
        return FALLBACK_COMPANY_QUESTIONS

    skills_required = job.skills_required or job.title or "general technical skills"
    prompt = (
        "Generate exactly 5 interview questions.\n"
        f"Job title: {job.title}\n"
        f"Skills required: {skills_required}\n"
        "Keep the questions simple, technical, and suitable for campus placement interviews.\n"
        "Return only a JSON array of strings."
    )

    payload = {
        "model": "openai/gpt-4.1-nano",
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "temperature": 0.3,
    }

    try:
        response = requests.post(
            "https://aipipe.org/openrouter/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        body = response.json()
        content = body["choices"][0]["message"]["content"].strip()

        if content.startswith("```"):
            lines = content.splitlines()
            if len(lines) >= 3:
                content = "\n".join(lines[1:-1]).strip()
    except Exception:
        return FALLBACK_COMPANY_QUESTIONS

    try:
        parsed = json.loads(content)
        if isinstance(parsed, list) and len(parsed) >= 5:
            return parsed[:5]
    except Exception:
        pass

    return FALLBACK_COMPANY_QUESTIONS


class CompanyDashboard(Resource):
    def get(self):
        token = extract_token(request)
        data = decode_token(token)

        if data["role"] != "company":
            return {"error": "Access denied"}, 403

        company = CompanyProfile.query.filter_by(user_id=data["user_id"]).first()
        jobs = JobPosition.query.filter_by(company_id=company.id).all()

        return {"total_jobs": len(jobs)}


class CreateJob(Resource):
    def post(self):
        token = extract_token(request)
        data_token = decode_token(token)

        if data_token["role"] != "company":
            return {"error": "Access denied"}, 403

        data = request.get_json()

        company = CompanyProfile.query.filter_by(user_id=data_token["user_id"]).first()

        job = JobPosition(
            company_id=company.id,
            title=data.get("title"),
            description=data.get("description"),
            application_deadline=data.get("application_deadline"),
            status="Pending"
        )

        db.session.add(job)
        db.session.commit()

        return {"message": "Job created"}, 201


class ViewApplicants(Resource):
    def get(self, job_id):
        token = extract_token(request)
        data = decode_token(token)

        if data["role"] != "company":
            return {"error": "Access denied"}, 403

        company = CompanyProfile.query.filter_by(user_id=data["user_id"]).first()
        job = JobPosition.query.get(job_id)

        if job.company_id != company.id:
            return {"error": "Unauthorized"}, 403

        apps = Application.query.filter_by(job_id=job_id).all()

        return [
            {
                "student_name": StudentProfile.query.get(a.student_id).name,
                "status": a.status
            } for a in apps
        ]


class CompanyJobs(Resource):
    def get(self):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data = decode_token(token)

        if "error" in data:
            return data, 401

        if data["role"] != "company":
            return {"error": "Access denied"}, 403

        company = CompanyProfile.query.filter_by(user_id=data["user_id"]).first()
        if not company:
            return {"error": "Company not found"}, 404

        jobs = JobPosition.query.filter_by(company_id=company.id).all()

        return [
            {
                "id": job.id,
                "title": job.title,
                "status": job.status,
                "application_deadline": job.application_deadline.isoformat() if job.application_deadline else None
            } for job in jobs
        ], 200


class UpdateCompanyJob(Resource):
    def patch(self, job_id):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data_token = decode_token(token)

        if "error" in data_token:
            return data_token, 401

        if data_token["role"] != "company":
            return {"error": "Access denied"}, 403

        company = CompanyProfile.query.filter_by(user_id=data_token["user_id"]).first()
        if not company:
            return {"error": "Company not found"}, 404

        job = JobPosition.query.get(job_id)
        if not job:
            return {"error": "Job not found"}, 404

        if job.company_id != company.id:
            return {"error": "Unauthorized"}, 403

        if job.status != "Pending":
            return {"error": "Only pending jobs can be updated"}, 400

        data = request.get_json()
        if not data:
            return {"error": "No data provided"}, 400

        if "title" in data:
            job.title = data.get("title")
        if "description" in data:
            job.description = data.get("description")
        if "salary" in data:
            job.salary = data.get("salary")
        if "skills_required" in data:
            job.skills_required = data.get("skills_required")
        if "experience_required" in data:
            job.experience_required = data.get("experience_required")
        if "location" in data:
            job.location = data.get("location")
        if "min_cgpa" in data:
            job.min_cgpa = data.get("min_cgpa")
        if "eligible_branches" in data:
            job.eligible_branches = data.get("eligible_branches")
        if "eligible_year" in data:
            job.eligible_year = data.get("eligible_year")
        if "application_deadline" in data:
            parsed_deadline = parse_deadline(data.get("application_deadline"))
            if not parsed_deadline:
                return {"error": "Invalid application_deadline"}, 400
            job.application_deadline = parsed_deadline

        db.session.commit()

        return {"message": "Job updated"}, 200


class UpdateApplicationStatus(Resource):
    def patch(self, application_id):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data_token = decode_token(token)

        if "error" in data_token:
            return data_token, 401

        if data_token["role"] != "company":
            return {"error": "Access denied"}, 403

        company = CompanyProfile.query.filter_by(user_id=data_token["user_id"]).first()
        if not company:
            return {"error": "Company not found"}, 404

        application = Application.query.get(application_id)
        if not application:
            return {"error": "Application not found"}, 404

        job = JobPosition.query.get(application.job_id)
        if not job or job.company_id != company.id:
            return {"error": "Unauthorized"}, 403

        data = request.get_json()
        if not data:
            return {"error": "No data provided"}, 400

        status = data.get("status")
        if status not in ["Shortlisted", "Rejected"]:
            return {"error": "Invalid status"}, 400

        application.status = status
        db.session.commit()

        return {"message": "Application status updated"}, 200


class CandidateMatchScores(Resource):
    def get(self, job_id):
        _, company, error = get_company_from_request()
        if error:
            return error

        job, job_error = get_company_job(company, job_id)
        if job_error:
            return job_error

        applications = Application.query.filter_by(job_id=job.id).all()
        results = []

        for application in applications:
            student = StudentProfile.query.get(application.student_id)
            if not student:
                continue

            match = calculate_candidate_match(student, job)
            results.append(
                {
                    "student_name": student.name,
                    "score": match["score"],
                    "matched_skills": match["matched_skills"],
                    "missing_skills": match["missing_skills"],
                    "breakdown": match["breakdown"],
                    "decision_hint": match["decision_hint"],
                }
            )

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:10], 200


class MarketInsight(Resource):
    def get(self, job_id):
        _, company, error = get_company_from_request()
        if error:
            return error

        job, job_error = get_company_job(company, job_id)
        if job_error:
            return job_error

        students = StudentProfile.query.all()
        total_students = len(students)
        matching_students = 0

        for student in students:
            if is_student_match(student, job):
                matching_students += 1

        match_percentage = 0
        if total_students > 0:
            match_percentage = round((matching_students / total_students) * 100, 2)

        if match_percentage >= 60:
            availability = "High"
            insight = "Good talent supply is available for this job."
        elif match_percentage >= 30:
            availability = "Medium"
            insight = "Talent supply is moderate for this job."
        else:
            availability = "Low"
            insight = "Talent supply is limited for this job."

        return {
            "total_students": total_students,
            "matching_students": matching_students,
            "match_percentage": match_percentage,
            "availability": availability,
            "insight": insight,
        }, 200


class JobInterviewQuestions(Resource):
    def get(self, job_id):
        _, company, error = get_company_from_request()
        if error:
            return error

        job, job_error = get_company_job(company, job_id)
        if job_error:
            return job_error

        questions = generate_job_questions(job)
        return {"questions": questions}, 200
