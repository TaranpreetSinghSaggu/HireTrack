"""Add one complete, repeatable company demo dataset to the local database."""

import os
from datetime import datetime, timedelta, timezone

from app import create_app
from models import (
    Application,
    ApplicationStatusHistory,
    CompanyProfile,
    Interview,
    JobPosition,
    Placement,
    StudentProfile,
    User,
    db,
)


COMPANY_EMAIL = "demo.company@hiretrack.local"
COMPANY_PASSWORD = "DemoCompany123!"
STUDENT_PASSWORD = "DemoStudent123!"


def get_user(email, role, password):
    account = User.query.filter_by(email=email).first()
    if not account:
        account = User(email=email, role=role)
        account.set_password(password)
        db.session.add(account)
        db.session.flush()
    account.status = "active"
    return account


def pdf_bytes(title):
    text = title.replace("(", "\\(").replace(")", "\\)")
    stream = f"BT /F1 16 Tf 72 740 Td ({text}) Tj ET"
    return (
        "%PDF-1.4\n"
        "1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        "2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj\n"
        "3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]"
        f"/Resources<</Font<</F1<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>>>>/Contents 4 0 R>>endobj\n"
        f"4 0 obj<</Length {len(stream)}>>stream\n{stream}\nendstream endobj\n"
        "xref\n0 5\n0000000000 65535 f \n"
        "0000000009 00000 n \n0000000058 00000 n \n0000000115 00000 n \n"
        "0000000300 00000 n \ntrailer<</Size 5/Root 1 0 R>>\nstartxref\n390\n%%EOF"
    ).encode("latin-1")


def save_pdf(folder, filename, title):
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    with open(path, "wb") as file:
        file.write(pdf_bytes(title))
    return path


def get_company():
    account = get_user(COMPANY_EMAIL, "company", COMPANY_PASSWORD)
    profile = CompanyProfile.query.filter_by(user_id=account.id).first()
    if not profile:
        profile = CompanyProfile(user_id=account.id)
        db.session.add(profile)
    profile.name = "PPA Demo Technologies"
    profile.industry = "Software and Analytics"
    profile.location = "Bengaluru"
    profile.hr_contact = "Neha Kapoor"
    profile.website = "https://demo.hiretrack.local"
    profile.is_approved = True
    profile.approved_by_admin = True
    profile.is_blacklisted = False
    db.session.flush()
    return profile


def get_student(key, name, email, branch, cgpa, year, skills, contact):
    account = get_user(email, "student", STUDENT_PASSWORD)
    profile = StudentProfile.query.filter_by(user_id=account.id).first()
    if not profile:
        profile = StudentProfile(user_id=account.id)
        db.session.add(profile)
    profile.name = name
    profile.contact = contact
    profile.branch = branch
    profile.cgpa = cgpa
    profile.year = year
    profile.degree = "B.Tech"
    profile.institution = "PPA Institute of Technology"
    profile.passout_year = 2026 if year == 4 else 2027
    profile.skills = skills
    profile.experience = f"{name} completed a practical campus project using {skills.split(',')[0]} and REST APIs."
    profile.resume_filename = f"{key}_resume.pdf"
    db.session.flush()
    return profile


def get_job(company, key, title, description, salary, skills, status, deadline_days):
    job = JobPosition.query.filter_by(company_id=company.id, title=title).first()
    if not job:
        job = JobPosition(company_id=company.id, title=title, description=description)
        db.session.add(job)
    job.description = description
    job.salary = salary
    job.benefits = "Mentor support, learning budget, flexible work hours"
    job.skills_required = skills
    job.experience_required = "Fresher / 0-1 years"
    job.location = "Bengaluru / Hybrid"
    job.min_cgpa = 7.0
    job.eligible_branches = "Computer Science, Information Technology, Data Science"
    job.eligible_year = 4
    job.application_deadline = datetime.now(timezone.utc) + timedelta(days=deadline_days)
    job.status = status
    db.session.flush()
    return job


def add_history(application, statuses, feedback):
    ApplicationStatusHistory.query.filter_by(application_id=application.id).delete(
        synchronize_session=False
    )
    for status in statuses:
        db.session.add(ApplicationStatusHistory(
            application_id=application.id,
            status=status,
            feedback=feedback if status in ("Shortlisted", "Offer", "Rejected", "Placed") else None,
        ))


def get_application(student, job, statuses, feedback):
    application = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
    if not application:
        application = Application(student_id=student.id, job_id=job.id)
        db.session.add(application)
        db.session.flush()
    application.status = statuses[-1]
    application.notes = feedback
    application.application_date = datetime.now(timezone.utc) - timedelta(days=6)
    add_history(application, statuses, feedback)
    return application


def seed():
    company = get_company()

    students = {
        "aarav": get_student("aarav", "Aarav Demo", "aarav.demo@hiretrack.local", "Computer Science", 8.6, 4, "Python, SQL, Flask, Git", "+91 90000 00001"),
        "diya": get_student("diya", "Diya Demo", "diya.demo@hiretrack.local", "Information Technology", 8.3, 4, "Vue, JavaScript, APIs, SQL", "+91 90000 00002"),
        "rohan": get_student("rohan", "Rohan Demo", "rohan.demo@hiretrack.local", "Data Science", 8.8, 4, "Python, Pandas, SQL, Power BI", "+91 90000 00003"),
        "isha": get_student("isha", "Isha Demo", "isha.demo@hiretrack.local", "Computer Science", 7.9, 4, "Java, Spring Boot, SQL, Docker", "+91 90000 00004"),
        "kabir": get_student("kabir", "Kabir Demo", "kabir.demo@hiretrack.local", "Information Technology", 7.5, 4, "Testing, Selenium, APIs, SQL", "+91 90000 00005"),
        "meera": get_student("meera", "Meera Demo", "meera.demo@hiretrack.local", "Computer Science", 8.1, 4, "Python, Machine Learning, SQL, Communication", "+91 90000 00006"),
    }

    jobs = {
        "frontend": get_job(company, "frontend", "Frontend Engineer", "Build accessible Vue screens and connect them to Flask APIs.", 800000, "Vue, JavaScript, APIs, SQL", "Approved", 20),
        "backend": get_job(company, "backend", "Backend Developer Intern", "Support Flask services, database queries, and background jobs.", 650000, "Python, Flask, SQL, Redis", "Approved", 14),
        "data": get_job(company, "data", "Data Analyst Trainee", "Prepare reports and explain product and placement data.", 600000, "Python, SQL, Power BI, Communication", "Closed", -2),
        "qa": get_job(company, "qa", "QA Automation Intern", "Create practical API and browser tests for internal tools.", 500000, "Selenium, APIs, SQL, Git", "Pending", 25),
    }

    applications = [
        ("aarav", "frontend", ["Applied"], "Application received."),
        ("diya", "frontend", ["Applied", "Shortlisted"], "Good frontend project work."),
        ("rohan", "frontend", ["Applied", "Shortlisted", "Interview"], "Strong communication and UI understanding."),
        ("isha", "backend", ["Applied", "Shortlisted", "Interview", "Offer"], "Strong backend fundamentals after the interview."),
        ("meera", "backend", ["Applied", "Shortlisted", "Interview", "Offer", "Placed"], "Excellent Python and data work."),
        ("kabir", "data", ["Applied", "Rejected"], "Needs more SQL reporting practice."),
    ]
    app_records = {}
    for student_key, job_key, statuses, feedback in applications:
        app_records[(student_key, job_key)] = get_application(
            students[student_key], jobs[job_key], statuses, feedback
        )

    interview_folder = os.path.join(os.path.dirname(__file__), "uploads", "resumes")
    offer_folder = os.path.join(os.path.dirname(__file__), "uploads", "offers")
    for key, student in students.items():
        student.resume_path = save_pdf(interview_folder, f"{key}_resume.pdf", f"Resume - {student.name}")

    interview_specs = [
        (("rohan", "frontend"), 3, "https://meet.hiretrack.local/demo-frontend", "Virtual interview", "Bring your portfolio."),
        (("isha", "backend"), 5, "", "PPA Demo Office", "Backend and database round."),
    ]
    for app_key, days_ahead, link, venue, notes in interview_specs:
        application = app_records[app_key]
        interview = Interview.query.filter_by(application_id=application.id).first()
        if not interview:
            interview = Interview(application_id=application.id)
            db.session.add(interview)
        interview.interview_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)
        interview.interview_link = link
        interview.venue = venue
        interview.notes = notes

    offer_path = save_pdf(offer_folder, "demo_company_meera_offer.pdf", "Offer Letter - PPA Demo Technologies")
    for student_key, job_key, joining_days in (("isha", "backend", 30), ("meera", "backend", 20)):
        application = app_records[(student_key, job_key)]
        application.offer_salary = jobs[job_key].salary
        application.offer_joining_date = datetime.now(timezone.utc) + timedelta(days=joining_days)
        application.offer_remarks = "Please bring your original documents on joining day."
        application.offer_letter_path = offer_path

    placed_application = app_records[("meera", "backend")]
    placement = Placement.query.filter_by(application_id=placed_application.id).first()
    if not placement:
        placement = Placement(application_id=placed_application.id)
        db.session.add(placement)
    placement.student_id = students["meera"].id
    placement.company_id = company.id
    placement.position = jobs["backend"].title
    placement.salary = jobs["backend"].salary
    placement.joining_date = placed_application.offer_joining_date
    placement.remarks = "Placement confirmed for the backend team."
    placement.offer_letter = offer_path

    db.session.commit()
    return {
        "company": company.name,
        "company_email": COMPANY_EMAIL,
        "company_password": COMPANY_PASSWORD,
        "student_password": STUDENT_PASSWORD,
        "jobs": len(jobs),
        "applications": len(app_records),
    }


if __name__ == "__main__":
    application = create_app()
    with application.app_context():
        print(seed())
