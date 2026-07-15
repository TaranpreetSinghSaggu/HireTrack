from flask_restful import Resource
from utils.gemini import generate_gemini_content
import os

from flask import current_app, g, request, send_file
from models import db, CompanyProfile, JobPosition, Application, ApplicationStatusHistory, StudentProfile, Interview, Placement
from utils.auth_decorators import jwt_required
from utils.mail_utils import send_email
from datetime import datetime, timezone
import json
import requests
from werkzeug.utils import secure_filename
from celery.result import AsyncResult
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


def allowed_pdf(file_storage):
    if not file_storage or not file_storage.filename:
        return False
    return file_storage.filename.lower().endswith(".pdf")


def save_uploaded_pdf(file_storage, folder, filename):
    if not allowed_pdf(file_storage):
        raise ValueError("Only PDF files are accepted")

    file_storage.seek(0, os.SEEK_END)
    size = file_storage.tell()
    file_storage.seek(0)
    if size <= 0:
        raise ValueError("Uploaded PDF is empty")
    if size > 8 * 1024 * 1024:
        raise ValueError("PDF must be smaller than 8 MB")

    os.makedirs(folder, exist_ok=True)
    safe_name = secure_filename(filename)
    path = os.path.join(folder, safe_name)
    file_storage.save(path)
    return path


def send_application_email(application, subject, body):
    student = application.student
    if student and student.user and student.user.email:
        send_email(student.user.email, subject, body)


def record_status(application, status, feedback=None):
    db.session.add(ApplicationStatusHistory(
        application_id=application.id,
        status="Offer" if status == "Selected" else status,
        feedback=feedback,
    ))


def serialize_applicant(application, company):
    job = application.job
    student = application.student
    if not job or job.company_id != company.id:
        return None

    match = calculate_candidate_match(student, job) if student else {}
    interview = Interview.query.filter_by(application_id=application.id).first()
    return {
        "application_id": application.id,
        "job_id": job.id,
        "job_title": job.title,
        "student_id": student.id if student else None,
        "student_name": student.name if student else "Deleted User",
        "student_contact": student.contact if student else None,
        "student_branch": student.branch if student else None,
        "student_year": student.year if student else None,
        "student_degree": student.degree if student else None,
        "student_institution": student.institution if student else None,
        "student_cgpa": student.cgpa if student else None,
        "student_skills": student.skills if student else None,
        "student_experience": student.experience if student else None,
        "has_resume": bool(student and student.resume_path),
        "resume_filename": student.resume_filename if student else None,
        "status": "Offer" if application.status == "Selected" else application.status,
        "feedback": application.notes,
        "application_date": application.application_date.isoformat() if application.application_date else None,
        "match": match,
        "interview": {
            "interview_date": interview.interview_date.isoformat(),
            "interview_link": interview.interview_link,
            "venue": interview.venue,
            "notes": interview.notes,
        } if interview else None,
        "offer": {
            "salary": application.offer_salary,
            "joining_date": application.offer_joining_date.isoformat() if application.offer_joining_date else None,
            "remarks": application.offer_remarks,
            "has_letter": bool(application.offer_letter_path),
        } if application.offer_salary is not None or application.offer_letter_path else None,
    }


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
    if not current_app.config.get("GEMINI_API_KEY"):
        return []

    skills_required = job.skills_required or job.title or "general technical skills"
    prompt = (
        "Generate exactly 5 interview questions.\n"
        f"Job title: {job.title}\n"
        f"Skills required: {skills_required}\n"
        "Keep the questions simple, technical, and suitable for campus placement interviews.\n"
        "Return only a JSON array of strings."
    )

    try:
        content_ai = generate_gemini_content(prompt, temperature=0.3, timeout=15)

        if content_ai.startswith("```"):
            lines = content_ai.splitlines()
            if len(lines) >= 3:
                content_ai = "\n".join(lines[1:-1]).strip()

        parsed = json.loads(content_ai)
        if isinstance(parsed, list) and len(parsed) >= 5:
            return parsed[:5]
    except Exception as error:
        print(f"Gemini job question generation failed: {error}")

    return FALLBACK_COMPANY_QUESTIONS


class CompanyDashboard(Resource):
    @jwt_required(role="company")
    def get(self):
        company = g.current_company
        jobs = JobPosition.query.filter_by(company_id=company.id).all()
        job_ids = [job.id for job in jobs]

        total_applications = 0
        pipeline_counts = {status: 0 for status in ["Applied", "Shortlisted", "Interview", "Offer", "Placed", "Rejected"]}

        if job_ids:
            total_applications = Application.query.filter(
                Application.job_id.in_(job_ids)
            ).count()
            for application in Application.query.filter(Application.job_id.in_(job_ids)).all():
                status = "Offer" if application.status == "Selected" else application.status
                if status in pipeline_counts:
                    pipeline_counts[status] += 1

        upcoming_interviews = []
        for interview in Interview.query.join(Application).join(JobPosition).filter(
            JobPosition.company_id == company.id,
            Interview.interview_date >= datetime.now(timezone.utc),
        ).order_by(Interview.interview_date.asc()).limit(5).all():
            upcoming_interviews.append({
                "application_id": interview.application_id,
                "student_name": interview.application.student.name if interview.application.student else "Unknown",
                "job_title": interview.application.job.title if interview.application.job else "Unknown",
                "interview_date": interview.interview_date.isoformat(),
                "venue": interview.venue,
                "interview_link": interview.interview_link,
            })

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
            "shortlisted_count": pipeline_counts["Shortlisted"],
            "selected_count": pipeline_counts["Offer"] + pipeline_counts["Placed"],
            "pipeline_counts": pipeline_counts,
            "upcoming_interviews": upcoming_interviews,
            "pending_actions": pipeline_counts["Applied"] + pipeline_counts["Shortlisted"],
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

        return [serialize_applicant(application, company) for application in Application.query.filter_by(job_id=job.id).all()], 200


class CompanyApplicants(Resource):
    @jwt_required(role="company")
    def get(self):
        company = g.current_company
        query = Application.query.join(JobPosition).filter(JobPosition.company_id == company.id)

        job_id = request.args.get("job_id", type=int)
        status_filter = request.args.get("status", "").strip()
        search = request.args.get("search", "").strip()
        if job_id:
            query = query.filter(Application.job_id == job_id)
        if status_filter:
            if status_filter == "Offer":
                query = query.filter(Application.status.in_(["Offer", "Selected"]))
            else:
                query = query.filter(Application.status == status_filter)
        if search:
            query = query.join(StudentProfile).filter(StudentProfile.name.ilike(f"%{search}%"))

        result = [serialize_applicant(application, company) for application in query.order_by(Application.application_date.desc()).all()]
        return [item for item in result if item], 200


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
            "Shortlisted": ["Rejected"],
            "Interview": ["Rejected"],
            "Offer": ["Rejected"],
            "Selected": ["Placed", "Rejected"],
        }
        allowed = valid_transitions.get(application.status, [])
        if status not in allowed:
            return {
                "error": f"Cannot move from '{application.status}' to '{status}'",
                "allowed": allowed,
            }, 400

        feedback = data.get("feedback", data.get("notes"))
        if status == "Rejected" and not str(feedback or "").strip():
            return {"error": "Feedback is required when rejecting an applicant"}, 400

        application.status = status
        if feedback is not None:
            application.notes = str(feedback).strip()
        if status == "Placed" and not Placement.query.filter_by(application_id=application.id).first():
            db.session.add(Placement(
                application_id=application.id,
                student_id=application.student_id,
                company_id=job.company_id,
                position=job.title,
                salary=job.salary,
            ))
        record_status(application, status, application.notes)
        db.session.commit()

        send_application_email(
            application,
            f"Application update: {job.title} - {status}",
            f"Your application for {job.title} at {company.name} is now marked as {status}.\n\n"
            f"Feedback: {application.notes or 'No additional feedback was provided.'}\n\n"
            "Please sign in to HireTrack for the full application details.",
        )

        return {"message": "Application status updated"}, 200


class CreateOffer(Resource):
    @jwt_required(role="company")
    def post(self, application_id):
        company = g.current_company
        application = db.session.get(Application, application_id)
        if not application:
            return {"error": "Application not found"}, 404

        job = db.session.get(JobPosition, application.job_id)
        if not job or job.company_id != company.id:
            return {"error": "Unauthorized"}, 403
        if application.status != "Interview":
            return {"error": "An offer can only be created after an interview"}, 400

        salary_value = request.form.get("salary", "").strip()
        try:
            salary = int(salary_value) if salary_value else job.salary
        except ValueError:
            return {"error": "Salary must be a whole number"}, 400

        joining_date = parse_optional_datetime(request.form.get("joining_date"))
        if request.form.get("joining_date") and not joining_date:
            return {"error": "Invalid joining_date"}, 400

        feedback = request.form.get("feedback", "").strip()
        if not feedback:
            return {"error": "Offer feedback is required"}, 400

        offer_letter = request.files.get("offer_letter")
        if not allowed_pdf(offer_letter):
            return {"error": "A PDF offer letter is required"}, 400

        offer_folder = os.path.join(current_app.config["UPLOAD_FOLDER"], "offers")
        offer_filename = f"offer_application_{application.id}.pdf"
        try:
            offer_path = save_uploaded_pdf(offer_letter, offer_folder, offer_filename)
        except ValueError as error:
            return {"error": str(error)}, 400

        application.status = "Offer"
        application.notes = feedback
        application.offer_salary = salary
        application.offer_joining_date = joining_date
        application.offer_remarks = request.form.get("remarks", "").strip() or None
        application.offer_letter_path = offer_path
        record_status(application, "Offer", feedback)
        db.session.commit()

        send_application_email(
            application,
            f"You received an offer for {job.title}",
            f"{company.name} has shared an offer for {job.title}.\n\n"
            f"Salary: {salary or 'Not specified'}\n"
            f"Joining date: {joining_date.isoformat() if joining_date else 'Not specified'}\n"
            f"Feedback: {feedback}\n\n"
            "Sign in to HireTrack to review and download the offer letter.",
        )
        return {"message": "Offer created", "status": "Offer"}, 201


class PlaceCandidate(Resource):
    @jwt_required(role="company")
    def post(self, application_id):
        company = g.current_company
        application = db.session.get(Application, application_id)
        if not application:
            return {"error": "Application not found"}, 404
        job = db.session.get(JobPosition, application.job_id)
        if not job or job.company_id != company.id:
            return {"error": "Unauthorized"}, 403
        if application.status != "Offer":
            return {"error": "Only offered candidates can be placed"}, 400

        data = request.get_json(silent=True) or {}
        joining_date = parse_optional_datetime(data.get("joining_date")) or application.offer_joining_date
        placement = Placement.query.filter_by(application_id=application.id).first()
        if not placement:
            placement = Placement(
                application_id=application.id,
                student_id=application.student_id,
                company_id=company.id,
                position=job.title,
            )
            db.session.add(placement)

        placement.salary = application.offer_salary or job.salary
        placement.joining_date = joining_date
        placement.remarks = data.get("remarks") or application.offer_remarks
        placement.offer_letter = application.offer_letter_path
        application.status = "Placed"
        record_status(application, "Placed", placement.remarks)
        db.session.commit()

        send_application_email(
            application,
            f"Placement confirmed: {job.title}",
            f"Your placement for {job.title} at {company.name} has been confirmed.\n\n"
            f"Joining date: {joining_date.isoformat() if joining_date else 'Not specified'}\n\n"
            "Please sign in to HireTrack for your placement record.",
        )
        return {"message": "Candidate marked as placed", "status": "Placed"}, 200


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
                    "application_id": application.id,
                    "student_id": application.student_id,
                    "student_name": student.name,
                    "student_branch": student.branch,
                    "student_cgpa": student.cgpa,
                    "student_skills": student.skills,
                    "status": application.status,
                    "score": match["score"],
                    "matched_skills": match["matched_skills"],
                    "missing_skills": match["missing_skills"],
                    "breakdown": match["breakdown"],
                    "decision_hint": match["decision_hint"],
                }
            )

        results.sort(key=lambda item: item["score"], reverse=True)
        return results, 200


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
        record_status(application, "Interview", application.notes)
        db.session.commit()

        send_application_email(
            application,
            f"Interview scheduled: {job.title}",
            f"Your interview for {job.title} at {company.name} is scheduled for {interview_date.isoformat()}.\n\n"
            f"Link: {interview.interview_link or 'Not specified'}\n"
            f"Venue: {interview.venue or 'Not specified'}\n"
            f"Notes: {interview.notes or 'None'}",
        )

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


class CompanyInterviews(Resource):
    @jwt_required(role="company")
    def get(self):
        company = g.current_company
        job_id = request.args.get("job_id", type=int)
        query = Interview.query.join(Application).join(JobPosition).filter(
            JobPosition.company_id == company.id
        )
        if job_id:
            query = query.filter(JobPosition.id == job_id)

        result = []
        for interview in query.order_by(Interview.interview_date.asc()).all():
            application = interview.application
            job = application.job
            student = application.student
            result.append({
                "interview_id": interview.id,
                "application_id": application.id,
                "job_id": job.id if job else None,
                "job_title": job.title if job else "Unknown",
                "student_name": student.name if student else "Unknown",
                "interview_date": interview.interview_date.isoformat(),
                "interview_link": interview.interview_link,
                "venue": interview.venue,
                "notes": interview.notes,
                "application_status": "Offer" if application.status == "Selected" else application.status,
            })
        return result, 200


class CompanyResume(Resource):
    @jwt_required(role="company")
    def get(self, application_id):
        company = g.current_company
        application = db.session.get(Application, application_id)
        if not application or not application.job or application.job.company_id != company.id:
            return {"error": "Application not found"}, 404
        student = application.student
        if not student or not student.resume_path or not os.path.isfile(student.resume_path):
            return {"error": "Resume not available"}, 404
        return send_file(
            student.resume_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=student.resume_filename or f"resume_student_{student.id}.pdf",
        )


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


class CompanyExportDownload(Resource):
    @jwt_required(role="company")
    def get(self, task_id):
        company = g.current_company
        from celery_worker import celery_app

        task_result = AsyncResult(task_id, app=celery_app)
        if not task_result.successful():
            return {"error": "Export is not ready"}, 409

        result = task_result.result or {}
        file_path = result.get("file_path") if isinstance(result, dict) else None
        expected_prefix = f"applications_company_{company.id}_"
        if not file_path or not os.path.basename(file_path).startswith(expected_prefix):
            return {"error": "Export not found"}, 404

        export_folder = os.path.abspath(current_app.config["EXPORT_FOLDER"])
        safe_path = os.path.abspath(file_path)
        if not safe_path.startswith(export_folder + os.sep) or not os.path.isfile(safe_path):
            return {"error": "Export not found"}, 404

        return send_file(safe_path, mimetype="text/csv", as_attachment=True, download_name=os.path.basename(safe_path))
