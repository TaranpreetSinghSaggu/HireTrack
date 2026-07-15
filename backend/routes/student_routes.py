from datetime import datetime, timezone
from io import BytesIO
import os
import json
import re
import requests

from flask import current_app, g, request, send_file
from flask_restful import Resource
from werkzeug.utils import secure_filename

from models import db, StudentProfile, JobPosition, Application, ApplicationStatusHistory, CompanyProfile, Interview, Placement
from utils.auth_decorators import jwt_required
from utils.resume_ai import analyze_resume_ai
from utils.gemini import generate_gemini_content

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


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


def extract_phone_from_text(text):
    match = re.search(r"(\+?\d{1,3}[-.\s]?)?\d{10}|(\+?\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,4})", text)
    if match:
        return match.group(0)
    return None


def extract_contact_from_text(text):
    email = extract_email_from_text(text)
    return email or extract_phone_from_text(text) or ""


def extract_degree_from_text(text):
    degrees = ["b.tech", "b.e.", "be", "btech", "bsc", "b.sc", "ba", "b.a", "ma", "m.a", "mtech", "m.tech", "mba", "m.b.a"]
    for line in text.lower().splitlines():
        for degree in degrees:
            if degree in line:
                return degree.upper()
    return ""


def extract_institution_from_text(text):
    keywords = ["university", "college", "institute", "iit", "nit"]
    for line in text.splitlines():
        if any(keyword in line.lower() for keyword in keywords):
            cleaned = line.strip().rstrip(".,")
            if len(cleaned) > 3 and len(cleaned) < 100:
                return cleaned
    return ""


def extract_branch_from_text(text):
    branches = ["computer science", "cse", "mechanical", "civil", "electrical", "electronics", "it", "information technology", "ece", "chemical"]
    text_lower = text.lower()
    for branch in branches:
        if branch in text_lower:
            return branch.title()
    return ""


def extract_year_from_text(text):
    match = re.search(r"(?:year|y|yr)[:\s]*([1-4])", text.lower())
    if match:
        return int(match.group(1))
    return None


def extract_passout_year_from_text(text):
    match = re.search(r"(?:passout|pass out|graduation|graduate|graduated)[:\s]*(\d{4})", text.lower())
    if match:
        return int(match.group(1))
    return None


def extract_cgpa_from_text(text):
    match = re.search(r"(?:cgpa|gpa)[:\s]*(\d+\.?\d*)", text.lower())
    if match:
        cgpa = float(match.group(1))
        if 0 <= cgpa <= 10:
            return cgpa
    return None


def extract_experience_from_text(text):
    lines = text.splitlines()
    exp_lines = []
    found_exp = False
    for line in lines:
        if "experience" in line.lower() or "work" in line.lower():
            found_exp = True
            continue
        if found_exp and line.strip():
            if "education" in line.lower() or "skill" in line.lower():
                break
            exp_lines.append(line.strip())
    return " ".join(exp_lines[:5])[:500] if exp_lines else ""


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


def serialize_student_profile(student):
    return {
        "name": student.name,
        "cgpa": student.cgpa,
        "branch": student.branch,
        "year": student.year,
        "skills": student.skills,
        "contact": student.contact,
        "degree": student.degree,
        "institution": student.institution,
        "passout_year": student.passout_year,
        "experience": student.experience,
        "resume_filename": student.resume_filename,
        "has_resume": bool(student.resume_path),
    }


def serialize_job(job, company, student):
    eligibility_reasons = get_eligibility_reasons(student, job)
    already_applied = Application.query.filter_by(
        student_id=student.id,
        job_id=job.id,
    ).first() is not None

    return {
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
        "is_eligible": len(eligibility_reasons) == 0,
        "eligibility_reasons": eligibility_reasons,
        "already_applied": already_applied,
        "application_deadline": job.application_deadline.isoformat(),
    }


def extract_text_from_pdf(file_storage):
    if PdfReader is None:
        raise ValueError("PDF support is not installed. Please install pypdf.")

    pdf_bytes = file_storage.read()
    if not pdf_bytes:
        raise ValueError("Uploaded PDF is empty")

    try:
        reader = PdfReader(BytesIO(pdf_bytes))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as error:
        raise ValueError("Could not read text from this PDF") from error

    return "\n".join(pages).strip()


def get_resume_text_from_request():
    uploaded_file = request.files.get("resume")

    if uploaded_file and uploaded_file.filename:
        filename = uploaded_file.filename.lower()
        if not filename.endswith(".pdf"):
            raise ValueError("Only PDF resumes are accepted")
        return extract_text_from_pdf(uploaded_file), uploaded_file.filename

    data = request.get_json(silent=True) or {}
    resume_text = data.get("resume_text", "").strip()
    if resume_text:
        return resume_text, None

    raise ValueError("Upload a PDF resume or paste resume text")


def parse_resume_text(resume_text):
    ai_result = analyze_resume_ai(resume_text)

    if ai_result:
        extracted_name = ai_result.get("name") or extract_name_from_text(resume_text)
        extracted_contact = ai_result.get("contact") or extract_contact_from_text(resume_text)
        extracted_degree = ai_result.get("degree") or extract_degree_from_text(resume_text)
        extracted_institution = ai_result.get("institution") or extract_institution_from_text(resume_text)
        extracted_branch = ai_result.get("branch") or extract_branch_from_text(resume_text)
        extracted_year = ai_result.get("year") or extract_year_from_text(resume_text)
        extracted_passout_year = ai_result.get("passout_year") or extract_passout_year_from_text(resume_text)
        extracted_cgpa = ai_result.get("cgpa") or extract_cgpa_from_text(resume_text)
        extracted_skills = ai_result.get("skills") or extract_skills_from_text(resume_text)
        extracted_experience = ai_result.get("experience") or extract_experience_from_text(resume_text)
    else:
        extracted_name = extract_name_from_text(resume_text)
        extracted_contact = extract_contact_from_text(resume_text)
        extracted_degree = extract_degree_from_text(resume_text)
        extracted_institution = extract_institution_from_text(resume_text)
        extracted_branch = extract_branch_from_text(resume_text)
        extracted_year = extract_year_from_text(resume_text)
        extracted_passout_year = extract_passout_year_from_text(resume_text)
        extracted_cgpa = extract_cgpa_from_text(resume_text)
        extracted_skills = extract_skills_from_text(resume_text)
        extracted_experience = extract_experience_from_text(resume_text)

    cleaned_skills = []
    for skill in extracted_skills:
        skill_text = str(skill).strip()
        if skill_text and skill_text not in cleaned_skills:
            cleaned_skills.append(skill_text)

    return {
        "name": extracted_name,
        "contact": extracted_contact,
        "degree": extracted_degree,
        "institution": extracted_institution,
        "branch": extracted_branch,
        "year": extracted_year,
        "passout_year": extracted_passout_year,
        "cgpa": extracted_cgpa,
        "skills": cleaned_skills,
        "experience": extracted_experience,
    }


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


def generate_ai_questions(skill):
    if not current_app.config.get("GEMINI_API_KEY"):
        raise RuntimeError("AI question generation is not configured")

    prompt = f"""
    Generate exactly 5 interview questions for the skill '{skill}'.
    Keep them short, practical, and student-friendly.
    Return only a JSON array.
    """

    try:
        content = generate_gemini_content(prompt, temperature=0.3, timeout=15)

        if content.startswith("```"):
            lines = content.splitlines()
            if len(lines) >= 3:
                content = "\n".join(lines[1:-1]).strip()

        questions = json.loads(content)
        if isinstance(questions, list):
            return questions[:5]

    except (requests.RequestException, KeyError, IndexError, json.JSONDecodeError) as error:
        print(f"Gemini question generation failed: {error}")
        raise RuntimeError("AI question generation is temporarily unavailable") from error

    raise RuntimeError("AI returned an invalid question response")


def generate_ai_weekly_plan(student, missing_skills):
    if not current_app.config.get("GEMINI_API_KEY"):
        raise RuntimeError("AI weekly planning is not configured")

    prompt = f"""
    Create exactly 5 concise weekly placement-preparation tasks for this student.
    Student branch: {student.branch or 'not provided'}
    Current skills: {student.skills or 'not provided'}
    Missing skills for suitable jobs: {', '.join(missing_skills[:5]) or 'not identified'}
    Return only a JSON array of strings. Do not use generic filler.
    """
    try:
        content = generate_gemini_content(prompt, temperature=0.3, timeout=15)
        if content.startswith("```"):
            content = "\n".join(content.splitlines()[1:-1]).strip()
        plan = json.loads(content)
        if isinstance(plan, list) and all(isinstance(item, str) for item in plan):
            return plan[:5]
    except (requests.RequestException, KeyError, IndexError, json.JSONDecodeError) as error:
        print(f"Gemini weekly plan generation failed: {error}")
        raise RuntimeError("AI weekly planning is temporarily unavailable") from error
    raise RuntimeError("AI returned an invalid weekly plan response")


class StudentDashboard(Resource):
    @jwt_required(role="student")
    def get(self):
        student = g.current_student
        applications = Application.query.filter_by(student_id=student.id).all()
        application_ids = [application.id for application in applications]
        interviews_count = Interview.query.filter(
            Interview.application_id.in_(application_ids)
        ).count() if application_ids else 0
        selected_count = sum(
            1 for application in applications
            if application.status in ["Selected", "Offer", "Placed"]
        )
        offer_count = sum(1 for application in applications if application.status == "Offer")
        placed_count = sum(1 for application in applications if application.status == "Placed")

        recent_jobs = []
        jobs = JobPosition.query.filter_by(status="Approved").order_by(
            JobPosition.created_at.desc()
        ).limit(5).all()
        for job in jobs:
            if not is_open_approved_job(job):
                continue
            company = db.session.get(CompanyProfile, job.company_id)
            if not company or not company.is_approved or company.is_blacklisted:
                continue
            recent_jobs.append(
                {
                    "id": job.id,
                    "title": job.title,
                    "company_name": company.name,
                    "location": job.location,
                }
            )

        return {
            **serialize_student_profile(student),
            "stats": {
                "applications": len(applications),
                "interviews": interviews_count,
                "selected": selected_count,
                "offers": offer_count,
                "placed": placed_count,
            },
            "recent_jobs": recent_jobs,
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
        db.session.add(ApplicationStatusHistory(application_id=app.id, status="Applied"))
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
                    "status": "Offer" if application.status == "Selected" else application.status,
                    "application_date": application.application_date.isoformat()
                    if application.application_date
                    else None,
                    "notes": application.notes,
                    "history": [
                        {
                            "status": history.status,
                            "feedback": history.feedback,
                            "created_at": history.created_at.isoformat() if history.created_at else None,
                        }
                        for history in application.status_history
                    ] or [{
                        "status": "Offer" if application.status == "Selected" else application.status,
                        "feedback": application.notes,
                        "created_at": application.application_date.isoformat() if application.application_date else None,
                    }],
                    "offer": {
                        "salary": application.offer_salary,
                        "joining_date": application.offer_joining_date.isoformat()
                        if application.offer_joining_date else None,
                        "remarks": application.offer_remarks,
                        "has_letter": bool(application.offer_letter_path),
                    } if application.offer_salary is not None or application.offer_letter_path else None,
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

            result.append(serialize_job(job, company, g.current_student))

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
    def get(self):
        return serialize_student_profile(g.current_student), 200

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

        uploaded_file = request.files.get("resume")
        try:
            resume_text, original_filename = get_resume_text_from_request()
        except ValueError as error:
            return {"error": str(error)}, 400

        if not resume_text:
            return {"error": "Could not find readable text in the resume"}, 400

        parsed_data = parse_resume_text(resume_text)

        if parsed_data["skills"]:
            student.skills = ", ".join(parsed_data["skills"])
        if parsed_data["name"]:
            student.name = parsed_data["name"]
        if parsed_data["contact"]:
            student.contact = parsed_data["contact"]
        if parsed_data["degree"]:
            student.degree = parsed_data["degree"]
        if parsed_data["institution"]:
            student.institution = parsed_data["institution"]
        if parsed_data["branch"]:
            student.branch = parsed_data["branch"]
        if parsed_data["year"]:
            student.year = parsed_data["year"]
        if parsed_data["passout_year"]:
            student.passout_year = parsed_data["passout_year"]
        if parsed_data["cgpa"]:
            student.cgpa = parsed_data["cgpa"]
        if parsed_data["experience"]:
            student.experience = parsed_data["experience"]

        student.resume_filename = secure_filename(original_filename) if original_filename else (
            f"resume_student_{student.id}_{utc_now().strftime('%Y%m%d%H%M%S')}.txt"
        )
        if uploaded_file and uploaded_file.filename:
            resume_folder = os.path.join(current_app.config["UPLOAD_FOLDER"], "resumes")
            os.makedirs(resume_folder, exist_ok=True)
            stored_name = f"resume_student_{student.id}.pdf"
            uploaded_file.seek(0)
            uploaded_file.save(os.path.join(resume_folder, stored_name))
            student.resume_path = os.path.join(resume_folder, stored_name)
        db.session.commit()

        return {
            "message": "Resume parsed successfully",
            "name": parsed_data["name"],
            "contact": parsed_data["contact"],
            "degree": parsed_data["degree"],
            "institution": parsed_data["institution"],
            "branch": parsed_data["branch"],
            "year": parsed_data["year"],
            "passout_year": parsed_data["passout_year"],
            "cgpa": parsed_data["cgpa"],
            "skills": parsed_data["skills"],
            "experience": parsed_data["experience"],
            "resume_filename": student.resume_filename,
        }, 200


class StudentOfferLetter(Resource):
    @jwt_required(role="student")
    def get(self, application_id):
        application = db.session.get(Application, application_id)
        if not application or application.student_id != g.current_student.id:
            return {"error": "Application not found"}, 404
        if not application.offer_letter_path or not os.path.isfile(application.offer_letter_path):
            return {"error": "Offer letter not available"}, 404
        return send_file(
            application.offer_letter_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"offer_{application.id}.pdf",
        )


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

        try:
            questions = generate_ai_questions(skill)
        except RuntimeError as error:
            return {"error": str(error)}, 503
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

        try:
            weekly_plan = generate_ai_weekly_plan(student, missing_skills)
        except RuntimeError as error:
            return {"error": str(error)}, 503

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
                    "offer_letter": bool(placement.offer_letter),
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
            result = task_result.result
            if isinstance(result, dict):
                response["result"] = {
                    key: value for key, value in result.items() if key != "file_path"
                }
            else:
                response["result"] = result
        elif task_result.failed():
            response["result"] = str(task_result.result)

        return response, 200
