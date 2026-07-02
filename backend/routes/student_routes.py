from flask_restful import Resource
from flask import current_app, g, request
from models import db, StudentProfile, JobPosition, Application, CompanyProfile, Interview, Placement
from utils.auth_decorators import jwt_required
from datetime import datetime, timezone
import json
import re
import requests
from utils.cache import cache_get_json, cache_set_json


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


def utc_now():
    return datetime.now(timezone.utc)


def as_utc(value):
    if not value:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def is_open_approved_job(job):
    deadline = as_utc(job.application_deadline)
    return job.status == "Approved" and deadline is not None and deadline > utc_now()


def get_eligibility_reasons(student, job):
    reasons = []

    if job.min_cgpa is not None:
        if student.cgpa is None or student.cgpa < job.min_cgpa:
            reasons.append(f"CGPA must be at least {job.min_cgpa}")

    if job.eligible_year is not None:
        if student.year is None or student.year != job.eligible_year:
            reasons.append(f"Student year must be {job.eligible_year}")

    if job.eligible_branches:
        allowed_branches = [
            branch.strip().lower()
            for branch in job.eligible_branches.split(",")
            if branch.strip()
        ]
        student_branch = (student.branch or "").strip().lower()
        if allowed_branches and student_branch not in allowed_branches:
            reasons.append("Student branch is not eligible")

    return reasons


def is_student_eligible(student, job):
    return len(get_eligibility_reasons(student, job)) == 0


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
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()

        if content.startswith("```"):
            lines = content.splitlines()
            if len(lines) >= 3:
                content = "\n".join(lines[1:-1]).strip()

        questions = json.loads(content)
        if isinstance(questions, list):
            return questions[:5]

    except (requests.RequestException, KeyError, IndexError, json.JSONDecodeError) as error:
        print(f"AIPIPE question generation failed, using fallback: {error}")

    return get_fallback_questions(skill)


class StudentDashboard(Resource):
    @jwt_required(role="student")
    def get(self):
        student = g.current_student
        return {
            "name": student.name,
            "cgpa": student.cgpa,
            "branch": student.branch,
            "year": student.year,
            "skills": student.skills,
        }, 200


class ApplyJob(Resource):
    @jwt_required(role="student")
    def post(self):
        student = g.current_student
        data = request.get_json(silent=True) or {}
        job_id = data.get("job_id")

        job = db.session.get(JobPosition, job_id)

        if not job:
            return {"error": "Job not found"}, 404

        if not is_open_approved_job(job):
            return {"error": "Job is not open for applications"}, 400

        company = db.session.get(CompanyProfile, job.company_id)
        if not company or not company.is_approved or company.is_blacklisted:
            return {"error": "Company is not eligible for applications"}, 400

        eligibility_reasons = get_eligibility_reasons(student, job)
        if eligibility_reasons:
            return {
                "error": "Student is not eligible for this drive",
                "reasons": eligibility_reasons,
            }, 400

        existing = Application.query.filter_by(student_id=student.id, job_id=job_id).first()
        if existing:
            return {"error": "Already applied"}, 400

        app = Application(student_id=student.id, job_id=job_id)
        db.session.add(app)
        db.session.commit()

        return {"message": "Applied successfully"}, 201


class ViewApplications(Resource):
    @jwt_required(role="student")
    def get(self):
        student = g.current_student
        apps = Application.query.filter_by(student_id=student.id).order_by(
            Application.application_date.desc()
        ).all()

        result = []
        for application in apps:
            job = db.session.get(JobPosition, application.job_id)
            company = db.session.get(CompanyProfile, job.company_id) if job else None
            interview = Interview.query.filter_by(application_id=application.id).first()

            result.append(
                {
                    "application_id": application.id,
                    "job_id": application.job_id,
                    "job_title": job.title if job else "Unknown",
                    "company_name": company.name if company else "Unknown",
                    "status": application.status,
                    "application_date": application.application_date.isoformat()
                    if application.application_date
                    else None,
                    "notes": application.notes,
                    "interview": {
                        "interview_date": interview.interview_date.isoformat(),
                        "interview_link": interview.interview_link,
                        "venue": interview.venue,
                        "notes": interview.notes,
                    }
                    if interview
                    else None,
                }
            )

        return result, 200


class StudentJobs(Resource):
    @jwt_required(role="student")
    def get(self):
        company_query = request.args.get("company", "").strip().lower()
        position_query = request.args.get("position", "").strip().lower()
        skills_query = request.args.get("skills", "").strip().lower()
        eligible_only = request.args.get("eligible_only", "").strip().lower() == "true"
        cache_key = f"student_jobs:{company_query}:{position_query}:{skills_query}:{eligible_only}"

        cached_jobs = cache_get_json(cache_key)
        if cached_jobs:
            return cached_jobs, 200

        jobs = JobPosition.query.filter_by(status="Approved").all()

        result = []
        for job in jobs:
            if not is_open_approved_job(job):
                continue

            company = db.session.get(CompanyProfile, job.company_id)
            if not company or not company.is_approved or company.is_blacklisted:
                continue

            if company_query and company_query not in company.name.lower():
                continue
            if position_query and position_query not in job.title.lower():
                continue
            if skills_query and skills_query not in (job.skills_required or "").lower():
                continue

            eligibility_reasons = get_eligibility_reasons(g.current_student, job)
            is_eligible = len(eligibility_reasons) == 0
            if eligible_only and not is_eligible:
                continue

            result.append(
                {
                    "id": job.id,
                    "company_id": job.company_id,
                    "company_name": company.name,
                    "title": job.title,
                    "description": job.description,
                    "location": job.location,
                    "salary": job.salary,
                    "benefits": job.benefits,
                    "skills_required": job.skills_required,
                    "experience_required": job.experience_required,
                    "min_cgpa": job.min_cgpa,
                    "eligible_branches": job.eligible_branches,
                    "eligible_year": job.eligible_year,
                    "is_eligible": is_eligible,
                    "eligibility_reasons": eligibility_reasons,
                    "application_deadline": job.application_deadline.isoformat(),
                }
            )

        cache_set_json(cache_key, result)

        return result, 200


class StudentJobDetail(Resource):
    @jwt_required(role="student")
    def get(self, job_id):
        job = db.session.get(JobPosition, job_id)
        if not job:
            return {"error": "Job not found"}, 404

        if not is_open_approved_job(job):
            return {"error": "Job not found"}, 404

        company = db.session.get(CompanyProfile, job.company_id)
        if not company or not company.is_approved or company.is_blacklisted:
            return {"error": "Job not found"}, 404

        return {
            "id": job.id,
            "company_id": job.company_id,
            "company_name": company.name,
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
            "is_eligible": is_student_eligible(g.current_student, job),
            "eligibility_reasons": get_eligibility_reasons(g.current_student, job),
            "application_deadline": job.application_deadline.isoformat(),
            "status": job.status
        }, 200


class UpdateStudentProfile(Resource):
    @jwt_required(role="student")
    def patch(self):
        student = g.current_student
        data = request.get_json(silent=True) or {}
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
        if "contact" in data:
            student.contact = data.get("contact")
        if "name" in data:
            student.name = data.get("name")
        if "degree" in data:
            student.degree = data.get("degree")
        if "institution" in data:
            student.institution = data.get("institution")
        if "passout_year" in data:
            student.passout_year = data.get("passout_year")
        if "experience" in data:
            student.experience = data.get("experience")

        db.session.commit()

        return {"message": "Profile updated"}, 200


class UploadResume(Resource):
    @jwt_required(role="student")
    def post(self):
        student = g.current_student
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
        student.resume_filename = (
            f"resume_student_{student.id}_{utc_now().strftime('%Y%m%d%H%M%S')}.txt"
        )
        db.session.commit()

        return {
            "message": "Resume parsed successfully",
            "name": extracted_name,
            "email": extracted_email,
            "skills": extracted_skills,
            "resume_filename": student.resume_filename,
        }, 200


class StudentJobReadiness(Resource):
    @jwt_required(role="student")
    def get(self, job_id):
        student = g.current_student
        job = db.session.get(JobPosition, job_id)
        if not job:
            return {"error": "Job not found"}, 404

        if not is_open_approved_job(job):
            return {"error": "Job not found"}, 404

        result = calculate_readiness(student, job)
        return result, 200


class InterviewQuestions(Resource):
    @jwt_required(role="student")
    def get(self):
        skill = request.args.get("skill", "").strip()
        if not skill:
            return {"error": "skill is required"}, 400

        questions = generate_ai_questions(skill)
        return {"questions": questions}, 200


class StudentStrategy(Resource):
    @jwt_required(role="student")
    def get(self):
        student = g.current_student
        now = utc_now()
        available_jobs = JobPosition.query.filter_by(status="Approved").all()
        open_jobs = [
            job for job in available_jobs
            if is_open_approved_job(job)
        ]

        applied_jobs = []
        applications = Application.query.filter_by(student_id=student.id).all()
        for application in applications:
            job = db.session.get(JobPosition, application.job_id)
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
                    "application_deadline": as_utc(job.application_deadline),
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
    @jwt_required(role="student")
    def get(self, application_id):
        student = g.current_student
        application = db.session.get(Application, application_id)
        if not application:
            return {"error": "Application not found"}, 404

        if application.student_id != student.id:
            return {"error": "Access denied"}, 403

        job = db.session.get(JobPosition, application.job_id)
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


class StudentInterviews(Resource):
    @jwt_required(role="student")
    def get(self):
        student = g.current_student
        applications = Application.query.filter_by(student_id=student.id).all()
        result = []
        for application in applications:
            interview = Interview.query.filter_by(application_id=application.id).first()
            if not interview:
                continue

            job = db.session.get(JobPosition, application.job_id)
            company = db.session.get(CompanyProfile, job.company_id) if job else None
            result.append(
                {
                    "interview_id": interview.id,
                    "application_id": application.id,
                    "job_id": application.job_id,
                    "job_title": job.title if job else "Unknown",
                    "company_name": company.name if company else "Unknown",
                    "interview_date": interview.interview_date.isoformat(),
                    "interview_link": interview.interview_link,
                    "venue": interview.venue,
                    "notes": interview.notes,
                    "application_status": application.status,
                }
            )

        result.sort(key=lambda item: item["interview_date"])
        return result, 200


class StudentPlacements(Resource):
    @jwt_required(role="student")
    def get(self):
        student = g.current_student
        placements = Placement.query.filter_by(student_id=student.id).all()
        result = []
        for placement in placements:
            application = db.session.get(Application, placement.application_id)
            job = db.session.get(JobPosition, application.job_id) if application else None
            company = db.session.get(CompanyProfile, placement.company_id)
            result.append(
                {
                    "placement_id": placement.id,
                    "application_id": placement.application_id,
                    "job_id": job.id if job else None,
                    "job_title": job.title if job else placement.position,
                    "company_name": company.name if company else "Unknown",
                    "position": placement.position,
                    "salary": placement.salary,
                    "joining_date": placement.joining_date.isoformat()
                    if placement.joining_date
                    else None,
                    "placed_date": placement.placed_date.isoformat()
                    if placement.placed_date
                    else None,
                    "offer_letter": placement.offer_letter,
                    "remarks": placement.remarks,
                }
            )

        return result, 200


class ExportApplications(Resource):
    @jwt_required(role="student")
    def post(self):
        student = g.current_student
        from tasks.export_tasks import export_applications

        task = export_applications.delay(student.id)
        return {"task_id": task.id}, 202


class TaskStatus(Resource):
    @jwt_required()
    def get(self, task_id):
        from celery.result import AsyncResult
        from celery_worker import celery_app

        task_result = AsyncResult(task_id, app=celery_app)

        response = {"status": task_result.status}
        if task_result.successful():
            response["result"] = task_result.result
        elif task_result.failed():
            response["result"] = str(task_result.result)

        return response, 200
