from flask_restful import Resource
from flask import current_app, request
from models import db, StudentProfile, JobPosition, Application
from utils.jwt_utils import extract_token, decode_token
from datetime import datetime
import json
import os
import re
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError
import requests


KNOWN_SKILLS = [
    "python",
    "java",
    "c",
    "c++",
    "javascript",
    "typescript",
    "sql",
    "mysql",
    "postgresql",
    "html",
    "css",
    "flask",
    "django",
    "react",
    "vue",
    "node.js",
    "node",
    "mongodb",
    "aws",
    "docker",
    "git",
    "machine learning",
    "data structures",
    "algorithms",
    "dsa",
]

FALLBACK_QUESTIONS = {
    "python": [
        "What are Python lists and tuples, and how are they different?",
        "What is the difference between a function and a lambda in Python?",
        "How does exception handling work in Python?",
        "What is the use of dictionaries in Python?",
        "Explain the difference between shallow copy and deep copy in Python.",
    ],
    "sql": [
        "What is the difference between WHERE and HAVING in SQL?",
        "What is a JOIN and what are its common types?",
        "What is normalization in DBMS?",
        "How does GROUP BY work in SQL?",
        "What is the difference between DELETE, TRUNCATE, and DROP?",
    ],
    "java": [
        "What is the difference between JDK, JRE, and JVM?",
        "What is method overloading and method overriding in Java?",
        "What is inheritance in Java?",
        "What is the difference between interface and abstract class?",
        "What is exception handling in Java?",
    ],
    "default": [
        "Tell me about yourself.",
        "What are your strengths and weaknesses?",
        "Describe a challenging project you worked on.",
        "How do you approach problem solving?",
        "Why do you want this role?",
    ],
}


def get_student_from_request():
    token = extract_token(request)
    if not token:
        return None, None, ({"error": "Token missing"}, 401)

    data = decode_token(token)
    if "error" in data:
        return None, None, (data, 401)

    if data["role"] != "student":
        return None, None, ({"error": "Access denied"}, 403)

    student = StudentProfile.query.filter_by(user_id=data["user_id"]).first()
    if not student:
        return None, None, ({"error": "Student not found"}, 404)

    return data, student, None


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


def extract_skills_from_text(text):
    lowered_text = text.lower()
    found_skills = []

    for skill in KNOWN_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, lowered_text) and skill not in found_skills:
            found_skills.append(skill)

    return found_skills


def extract_email_from_text(text):
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    if match:
        return match.group(0)
    return None


def extract_name_from_text(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return None

    first_line = lines[0]
    if re.fullmatch(r"[A-Za-z ]{3,60}", first_line):
        return first_line

    return None


def get_job_required_skills(job):
    job_skills = normalize_skills(job.skills_required)
    if job_skills:
        return job_skills

    return extract_skills_from_text(job.description or "")


def calculate_readiness(student, job):
    student_skills = normalize_skills(student.skills)
    job_skills = get_job_required_skills(job)

    matched_skills = [skill for skill in job_skills if skill in student_skills]
    missing_skills = [skill for skill in job_skills if skill not in student_skills]

    skill_score = 0
    if job_skills:
        skill_score = int((len(matched_skills) / len(job_skills)) * 70)

    cgpa_ok = True
    cgpa_score = 30
    if job.min_cgpa is not None:
        cgpa_ok = student.cgpa is not None and student.cgpa >= job.min_cgpa
        cgpa_score = 30 if cgpa_ok else 0

    score = min(skill_score + cgpa_score, 100)

    suggestions = []
    for skill in missing_skills[:3]:
        suggestions.append(f"Learn {skill}")
    if job.min_cgpa is not None and not cgpa_ok:
        suggestions.append(f"Improve CGPA to at least {job.min_cgpa}")
    if not suggestions:
        suggestions.append("Keep practicing aptitude and interview questions")

    return {
        "score": score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "cgpa_ok": cgpa_ok,
        "suggestions": suggestions,
    }


def get_fallback_questions(skill):
    return FALLBACK_QUESTIONS.get(skill.lower(), FALLBACK_QUESTIONS["default"])


def generate_ai_questions(skill):
    api_key = current_app.config["AIPIPE_API_KEY"]

    if not api_key:
        return get_fallback_questions(skill)

    prompt = f"""
    Generate exactly 5 interview questions for the skill '{skill}'.
    Keep them short, practical, and student-friendly.
    Return only a JSON array.
    """

    try:
        response = requests.post(
            "https://aipipe.org/openrouter/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-4.1-nano",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
            },
            timeout=15,
        )

        data = response.json()

        content = data["choices"][0]["message"]["content"].strip()

        # clean markdown if present
        if content.startswith("```"):
            content = content.strip("`")
            if content.startswith("json"):
                content = content[4:].strip()

        questions = json.loads(content)

        if isinstance(questions, list):
            return questions[:5]

    except Exception:
        pass

    return get_fallback_questions(skill)


class StudentDashboard(Resource):
    def get(self):
        token = extract_token(request)
        data = decode_token(token)

        if "error" in data:
            return data, 401

        if data["role"] != "student":
            return {"error": "Access denied"}, 403

        student = StudentProfile.query.filter_by(user_id=data["user_id"]).first()

        return {
            "name": student.name,
            "cgpa": student.cgpa
        }


class ApplyJob(Resource):
    def post(self):
        token = extract_token(request)
        data_token = decode_token(token)

        if "error" in data_token:
            return data_token, 401

        if data_token["role"] != "student":
            return {"error": "Access denied"}, 403

        data = request.get_json()
        job_id = data.get("job_id")

        student = StudentProfile.query.filter_by(user_id=data_token["user_id"]).first()
        job = JobPosition.query.get(job_id)

        if not job:
            return {"error": "Job not found"}, 404

        existing = Application.query.filter_by(student_id=student.id, job_id=job_id).first()
        if existing:
            return {"error": "Already applied"}, 400

        app = Application(student_id=student.id, job_id=job_id)
        db.session.add(app)
        db.session.commit()

        return {"message": "Applied successfully"}, 201


class ViewApplications(Resource):
    def get(self):
        token = extract_token(request)
        data = decode_token(token)

        if "error" in data:
            return data, 401

        if data["role"] != "student":
            return {"error": "Access denied"}, 403

        student = StudentProfile.query.filter_by(user_id=data["user_id"]).first()

        apps = Application.query.filter_by(student_id=student.id).all()

        return [
            {
                "id": a.id,
                "job_id": a.job_id,
                "status": a.status
            } for a in apps
        ]


class StudentJobs(Resource):
    def get(self):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data = decode_token(token)

        if "error" in data:
            return data, 401

        if data["role"] != "student":
            return {"error": "Access denied"}, 403

        now = datetime.utcnow()
        jobs = JobPosition.query.filter_by(status="Approved").all()

        result = []
        for job in jobs:
            if job.application_deadline and job.application_deadline > now:
                result.append(
                    {
                        "id": job.id,
                        "title": job.title,
                        "description": job.description,
                        "location": job.location,
                        "salary": job.salary,
                        "application_deadline": job.application_deadline.isoformat()
                    }
                )

        return result, 200


class StudentJobDetail(Resource):
    def get(self, job_id):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data = decode_token(token)

        if "error" in data:
            return data, 401

        if data["role"] != "student":
            return {"error": "Access denied"}, 403

        job = JobPosition.query.get(job_id)
        if not job:
            return {"error": "Job not found"}, 404

        now = datetime.utcnow()
        if job.status != "Approved" or not job.application_deadline or job.application_deadline <= now:
            return {"error": "Job not found"}, 404

        return {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "salary": job.salary,
            "skills_required": job.skills_required,
            "experience_required": job.experience_required,
            "location": job.location,
            "min_cgpa": job.min_cgpa,
            "eligible_branches": job.eligible_branches,
            "eligible_year": job.eligible_year,
            "application_deadline": job.application_deadline.isoformat(),
            "status": job.status
        }, 200


class UpdateStudentProfile(Resource):
    def patch(self):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data_token = decode_token(token)

        if "error" in data_token:
            return data_token, 401

        if data_token["role"] != "student":
            return {"error": "Access denied"}, 403

        student = StudentProfile.query.filter_by(user_id=data_token["user_id"]).first()
        if not student:
            return {"error": "Student not found"}, 404

        data = request.get_json()
        if not data:
            return {"error": "No data provided"}, 400

        if "skills" in data:
            student.skills = data.get("skills")
        if "cgpa" in data:
            student.cgpa = data.get("cgpa")
        if "branch" in data:
            student.branch = data.get("branch")
        if "year" in data:
            student.year = data.get("year")

        db.session.commit()

        return {"message": "Profile updated"}, 200


class UploadResume(Resource):
    def post(self):
        _, student, error = get_student_from_request()
        if error:
            return error

        data = request.get_json()
        if not data:
            return {"error": "No data provided"}, 400

        resume_text = data.get("resume_text", "").strip()
        if not resume_text:
            return {"error": "resume_text is required"}, 400

        extracted_skills = extract_skills_from_text(resume_text)
        extracted_name = extract_name_from_text(resume_text)
        extracted_email = extract_email_from_text(resume_text)

        student.skills = ", ".join(extracted_skills)
        db.session.commit()

        return {
            "message": "Resume parsed successfully",
            "name": extracted_name,
            "email": extracted_email,
            "skills": extracted_skills,
        }, 200


class StudentJobReadiness(Resource):
    def get(self, job_id):
        _, student, error = get_student_from_request()
        if error:
            return error

        job = JobPosition.query.get(job_id)
        if not job:
            return {"error": "Job not found"}, 404

        now = datetime.utcnow()
        if job.status != "Approved" or not job.application_deadline or job.application_deadline <= now:
            return {"error": "Job not found"}, 404

        result = calculate_readiness(student, job)
        return result, 200


class InterviewQuestions(Resource):
    def get(self):
        _, _, error = get_student_from_request()
        if error:
            return error

        skill = request.args.get("skill", "").strip()
        if not skill:
            return {"error": "skill is required"}, 400

        questions = generate_ai_questions(skill)
        return {"questions": questions}, 200


class StudentStrategy(Resource):
    def get(self):
        _, student, error = get_student_from_request()
        if error:
            return error

        now = datetime.utcnow()
        available_jobs = JobPosition.query.filter_by(status="Approved").all()
        open_jobs = [
            job for job in available_jobs
            if job.application_deadline and job.application_deadline > now
        ]

        applied_jobs = []
        applications = Application.query.filter_by(student_id=student.id).all()
        for application in applications:
            job = JobPosition.query.get(application.job_id)
            if job:
                applied_jobs.append(job)

        readiness_results = []
        for job in open_jobs:
            readiness = calculate_readiness(student, job)
            readiness_results.append(
                {
                    "job_id": job.id,
                    "title": job.title,
                    "score": readiness["score"],
                    "missing_skills": readiness["missing_skills"],
                    "application_deadline": job.application_deadline,
                }
            )

        readiness_results.sort(key=lambda item: item["score"], reverse=True)

        recommended_jobs = []
        for item in readiness_results[:5]:
            recommended_jobs.append(
                {
                    "job_id": item["job_id"],
                    "title": item["title"],
                    "score": item["score"],
                }
            )

        urgent_actions = []
        for item in readiness_results:
            days_left = (item["application_deadline"] - now).days
            if days_left <= 7:
                urgent_actions.append(
                    {
                        "job_id": item["job_id"],
                        "title": item["title"],
                        "deadline": item["application_deadline"].isoformat(),
                    }
                )

        missing_skills = []
        for item in readiness_results[:5]:
            for skill in item["missing_skills"]:
                if skill not in missing_skills:
                    missing_skills.append(skill)

        weekly_plan = [
            "Solve 10 DSA problems",
            "Revise core subjects for 3 hours",
            "Practice 5 interview questions",
        ]
        for skill in missing_skills[:2]:
            weekly_plan.append(f"Spend 2 hours learning {skill}")

        readiness_score = 0
        if readiness_results:
            top_scores = [item["score"] for item in readiness_results[:3]]
            readiness_score = int(sum(top_scores) / len(top_scores))

        return {
            "readiness_score": readiness_score,
            "missing_skills": missing_skills,
            "weekly_plan": weekly_plan,
            "recommended_jobs": recommended_jobs,
            "urgent_actions": urgent_actions,
            "applied_jobs_count": len(applied_jobs),
        }, 200


class ApplicationAnalysis(Resource):
    def get(self, application_id):
        _, student, error = get_student_from_request()
        if error:
            return error

        application = Application.query.get(application_id)
        if not application:
            return {"error": "Application not found"}, 404

        if application.student_id != student.id:
            return {"error": "Access denied"}, 403

        job = JobPosition.query.get(application.job_id)
        if not job:
            return {"error": "Job not found"}, 404

        readiness = calculate_readiness(student, job)
        reasons = []
        suggestions = []

        if readiness["missing_skills"]:
            reasons.append("Missing required skills")
            for skill in readiness["missing_skills"][:3]:
                suggestions.append(f"Learn {skill}")

        if not readiness["cgpa_ok"]:
            reasons.append("CGPA is below job requirement")
            suggestions.append(f"Improve CGPA to at least {job.min_cgpa}")

        if application.status == "Rejected" and not reasons:
            reasons.append("Competition may have been stronger for this role")
            suggestions.append("Practice aptitude, projects, and interview communication")

        if not reasons:
            reasons.append("Your profile matched the job reasonably well")
            suggestions.append("Keep applying to similar roles and practice interviews")

        return {
            "reasons": reasons,
            "improvement_suggestions": suggestions,
        }, 200
