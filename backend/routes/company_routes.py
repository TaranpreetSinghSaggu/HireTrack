from flask_restful import Resource
from flask import current_app, g, request
from models import db, CompanyProfile, JobPosition, Application, StudentProfile, Interview, Placement
from utils.auth_decorators import jwt_required
from datetime import datetime, timezone
import json
import requests
from utils.cache import cache_delete, cache_get_json, cache_set_json, delete_pattern


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
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None

    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_optional_datetime(value):
    if not value:
        return None
    return parse_deadline(value)


def get_company_job(company, job_id):
    job = db.session.get(JobPosition, job_id)
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

        parsed = json.loads(content)
        if isinstance(parsed, list) and len(parsed) >= 5:
            return parsed[:5]
    except (requests.RequestException, KeyError, IndexError, json.JSONDecodeError) as error:
        print(f"AIPIPE job question generation failed, using fallback: {error}")

    return FALLBACK_COMPANY_QUESTIONS


class CompanyDashboard(Resource):
    @jwt_required(role="company")
    def get(self):
        company = g.current_company
        jobs = JobPosition.query.filter_by(company_id=company.id).all()
        job_ids = [job.id for job in jobs]

        total_applications = 0
        shortlisted_count = 0
        selected_count = 0

        if job_ids:
            total_applications = Application.query.filter(
                Application.job_id.in_(job_ids)
            ).count()
            shortlisted_count = Application.query.filter(
                Application.job_id.in_(job_ids),
                Application.status == "Shortlisted",
            ).count()
            selected_count = Application.query.filter(
                Application.job_id.in_(job_ids),
                Application.status.in_(["Selected", "Placed"]),
            ).count()

        return {
            "company_id": company.id,
            "company_name": company.name,
            "industry": company.industry,
            "location": company.location,
            "website": company.website,
            "hr_contact": company.hr_contact,
            "total_jobs": len(jobs),
            "active_jobs": sum(1 for job in jobs if job.status == "Approved"),
            "pending_jobs": sum(1 for job in jobs if job.status == "Pending"),
            "closed_jobs": sum(1 for job in jobs if job.status == "Closed"),
            "total_applications": total_applications,
            "shortlisted_count": shortlisted_count,
            "selected_count": selected_count,
            "placement_drives": [
                {
                    "job_id": job.id,
                    "title": job.title,
                    "status": job.status,
                    "applicant_count": Application.query.filter_by(job_id=job.id).count(),
                }
                for job in jobs
            ],
        }, 200


class CreateJob(Resource):
    @jwt_required(role="company")
    def post(self):
        company = g.current_company
        data = request.get_json(silent=True) or {}

        deadline = parse_deadline(data.get("application_deadline"))

        if not deadline:
            return {"error": "Invalid application_deadline"}, 400

        if not data.get("title") or not data.get("description"):
            return {"error": "title and description are required"}, 400

        job = JobPosition(
            company_id=company.id,
            title=data.get("title"),
            description=data.get("description"),
            salary=data.get("salary"),
            benefits=data.get("benefits"),
            skills_required=data.get("skills_required"),
            experience_required=data.get("experience_required"),
            location=data.get("location"),
            min_cgpa=data.get("min_cgpa"),
            eligible_branches=data.get("eligible_branches"),
            eligible_year=data.get("eligible_year"),
            application_deadline=deadline,
            status="Pending"
        )

        db.session.add(job)
        db.session.commit()

        delete_pattern("student_jobs*")
        cache_delete(f"company_jobs_{company.id}")

        return {"message": "Job created"}, 201


class ViewApplicants(Resource):
    @jwt_required(role="company")
    def get(self, job_id):
        company = g.current_company
        job, job_error = get_company_job(company, job_id)
        if job_error:
            return job_error

        apps = Application.query.filter_by(job_id=job.id).all()
        result = []
        for application in apps:
            student = db.session.get(StudentProfile, application.student_id)
            result.append(
                {
                    "application_id": application.id,
                    "student_id": application.student_id,
                    "student_name": student.name if student else "Deleted User",
                    "student_contact": student.contact if student else None,
                    "student_branch": student.branch if student else None,
                    "student_year": student.year if student else None,
                    "student_cgpa": student.cgpa if student else None,
                    "student_skills": student.skills if student else None,
                    "status": application.status,
                    "application_date": application.application_date.isoformat()
                    if application.application_date
                    else None,
                    "notes": application.notes,
                }
            )

        return result, 200


class CompanyJobs(Resource):
    @jwt_required(role="company")
    def get(self):
        company = g.current_company
        cache_key = f"company_jobs_{company.id}"
        cached_jobs = cache_get_json(cache_key)
        if cached_jobs:
            return cached_jobs, 200

        jobs = JobPosition.query.filter_by(company_id=company.id).all()

        result = [
            {
                "id": job.id,
                "title": job.title,
                "description": job.description,
                "salary": job.salary,
                "benefits": job.benefits,
                "skills_required": job.skills_required,
                "experience_required": job.experience_required,
                "location": job.location,
                "min_cgpa": job.min_cgpa,
                "eligible_branches": job.eligible_branches,
                "eligible_year": job.eligible_year,
                "status": job.status,
                "application_deadline": job.application_deadline.isoformat() if job.application_deadline else None
            } for job in jobs
        ]

        cache_set_json(cache_key, result)

        return result, 200


class UpdateCompanyJob(Resource):
    @jwt_required(role="company")
    def patch(self, job_id):
        company = g.current_company
        job, job_error = get_company_job(company, job_id)
        if job_error:
            return job_error

        if job.status != "Pending":
            return {"error": "Only pending jobs can be updated"}, 400

        data = request.get_json(silent=True) or {}
        if not data:
            return {"error": "No data provided"}, 400

        if "title" in data:
            job.title = data.get("title")
        if "description" in data:
            job.description = data.get("description")
        if "salary" in data:
            job.salary = data.get("salary")
        if "benefits" in data:
            job.benefits = data.get("benefits")
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

        delete_pattern("student_jobs*")
        cache_delete(f"company_jobs_{company.id}")

        return {"message": "Job updated"}, 200


class UpdateApplicationStatus(Resource):
    @jwt_required(role="company")
    def patch(self, application_id):
        company = g.current_company
        application = db.session.get(Application, application_id)
        if not application:
            return {"error": "Application not found"}, 404

        job = db.session.get(JobPosition, application.job_id)
        if not job or job.company_id != company.id:
            return {"error": "Unauthorized"}, 403

        data = request.get_json(silent=True) or {}
        if not data:
            return {"error": "No data provided"}, 400

        status = data.get("status")
        valid_transitions = {
            "Applied": ["Shortlisted", "Rejected"],
            "Shortlisted": ["Interview", "Rejected"],
            "Interview": ["Offer", "Selected", "Rejected"],
            "Offer": ["Placed", "Rejected"],
            "Selected": ["Placed", "Rejected"],
        }
        allowed = valid_transitions.get(application.status, [])
        if status not in allowed:
            return {
                "error": f"Cannot move from '{application.status}' to '{status}'",
                "allowed": allowed,
            }, 400

        application.status = status
        if "notes" in data:
            application.notes = data.get("notes")

        placement = Placement.query.filter_by(application_id=application.id).first()
        if status in ["Selected", "Placed"]:
            if not placement:
                placement = Placement(
                    application_id=application.id,
                    student_id=application.student_id,
                    company_id=job.company_id,
                    position=job.title,
                    salary=job.salary,
                )
                db.session.add(placement)

            if "position" in data:
                placement.position = data.get("position")
            if "salary" in data:
                placement.salary = data.get("salary")
            if "joining_date" in data:
                placement.joining_date = parse_optional_datetime(data.get("joining_date"))
            if "offer_letter" in data:
                placement.offer_letter = data.get("offer_letter")
            if "remarks" in data:
                placement.remarks = data.get("remarks")
        elif status == "Rejected" and placement:
            db.session.delete(placement)

        db.session.commit()

        return {"message": "Application status updated"}, 200


class CandidateMatchScores(Resource):
    @jwt_required(role="company")
    def get(self, job_id):
        company = g.current_company
        job, job_error = get_company_job(company, job_id)
        if job_error:
            return job_error

        applications = Application.query.filter_by(job_id=job.id).all()
        results = []

        for application in applications:
            student = db.session.get(StudentProfile, application.student_id)
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
    @jwt_required(role="company")
    def get(self, job_id):
        company = g.current_company
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
    @jwt_required(role="company")
    def get(self, job_id):
        company = g.current_company
        job, job_error = get_company_job(company, job_id)
        if job_error:
            return job_error

        questions = generate_job_questions(job)
        return {"questions": questions}, 200


class ScheduleInterview(Resource):
    @jwt_required(role="company")
    def post(self, application_id):
        company = g.current_company
        application = db.session.get(Application, application_id)
        if not application:
            return {"error": "Application not found"}, 404

        job = db.session.get(JobPosition, application.job_id)
        if not job or job.company_id != company.id:
            return {"error": "Unauthorized"}, 403

        if application.status != "Shortlisted":
            return {"error": "Can only schedule interview for shortlisted candidates"}, 400

        if Interview.query.filter_by(application_id=application.id).first():
            return {"error": "Interview already scheduled"}, 400

        data = request.get_json(silent=True) or {}
        interview_date = parse_deadline(data.get("interview_date"))
        if not interview_date:
            return {"error": "Invalid interview_date"}, 400

        interview = Interview(
            application_id=application.id,
            interview_date=interview_date,
            interview_link=data.get("interview_link"),
            venue=data.get("venue"),
            notes=data.get("notes"),
        )
        db.session.add(interview)
        application.status = "Interview"
        if data.get("notes"):
            application.notes = data.get("notes")
        db.session.commit()

        return {"message": "Interview scheduled", "interview_id": interview.id}, 201


class GetInterviewsForJob(Resource):
    @jwt_required(role="company")
    def get(self, job_id):
        company = g.current_company
        job, job_error = get_company_job(company, job_id)
        if job_error:
            return job_error

        applications = Application.query.filter_by(job_id=job.id).all()
        result = []
        for application in applications:
            interview = Interview.query.filter_by(application_id=application.id).first()
            if not interview:
                continue

            student = db.session.get(StudentProfile, application.student_id)
            result.append(
                {
                    "interview_id": interview.id,
                    "application_id": application.id,
                    "student_id": application.student_id,
                    "student_name": student.name if student else "Unknown",
                    "interview_date": interview.interview_date.isoformat(),
                    "interview_link": interview.interview_link,
                    "venue": interview.venue,
                    "notes": interview.notes,
                    "application_status": application.status,
                }
            )

        result.sort(key=lambda item: item["interview_date"])
        return result, 200


class CloseJob(Resource):
    @jwt_required(role="company")
    def patch(self, job_id):
        company = g.current_company
        job, job_error = get_company_job(company, job_id)
        if job_error:
            return job_error

        if job.status != "Approved":
            return {"error": "Only approved jobs can be closed"}, 400

        job.status = "Closed"
        db.session.commit()

        delete_pattern("student_jobs*")
        cache_delete(f"company_jobs_{company.id}")

        return {"message": "Job closed"}, 200


class ExportCompanyApplications(Resource):
    @jwt_required(role="company")
    def post(self):
        company = g.current_company
        from tasks.export_tasks import export_company_applications

        task = export_company_applications.delay(company.id)
        return {"task_id": task.id}, 202
