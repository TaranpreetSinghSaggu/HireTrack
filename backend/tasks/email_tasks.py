from datetime import datetime, timedelta, timezone

from celery_worker import celery_app
from models import Application, Interview, JobPosition, StudentProfile, db
from utils.mail_utils import send_email


def as_utc(value):
    if not value:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def student_matches_job(student, job):
    if job.min_cgpa is not None:
        if student.cgpa is None or student.cgpa < job.min_cgpa:
            return False

    if job.eligible_year is not None and student.year is not None:
        if student.year != job.eligible_year:
            return False

    if job.eligible_branches and student.branch:
        branches = [branch.strip().lower() for branch in job.eligible_branches.split(",") if branch.strip()]
        if branches and student.branch.lower() not in branches:
            return False

    return True


@celery_app.task(name="tasks.email_tasks.send_deadline_reminders")
def send_deadline_reminders():
    now = datetime.now(timezone.utc)
    end_time = now + timedelta(days=2)

    jobs = JobPosition.query.filter_by(status="Approved").all()
    reminders_sent = 0

    for job in jobs:
        if not job.application_deadline:
            continue

        application_deadline = as_utc(job.application_deadline)
        if not application_deadline:
            continue

        if application_deadline < now or application_deadline > end_time:
            continue

        students = StudentProfile.query.all()
        for student in students:
            if not student.user or not student.user.email:
                continue

            if not student_matches_job(student, job):
                continue

            body = (
                f"Reminder: The job '{job.title}' has an application deadline on "
                f"{application_deadline.isoformat()}."
            )
            send_email(student.user.email, "Placement Deadline Reminder", body)
            reminders_sent += 1

    return {"reminders_sent": reminders_sent}


@celery_app.task(name="tasks.email_tasks.send_interview_reminders")
def send_interview_reminders():
    now = datetime.now(timezone.utc)
    reminder_window = now + timedelta(hours=24)
    reminders_sent = 0

    interviews = Interview.query.all()
    for interview in interviews:
        interview_date = as_utc(interview.interview_date)
        if not interview_date:
            continue

        if interview_date < now or interview_date > reminder_window:
            continue

        application = db.session.get(Application, interview.application_id)
        if not application:
            continue

        student = db.session.get(StudentProfile, application.student_id)
        if not student or not student.user or not student.user.email:
            continue

        job = db.session.get(JobPosition, application.job_id)
        job_title = job.title if job else "your scheduled interview"

        body = (
            f"Reminder: You have an interview for '{job_title}' "
            f"on {interview_date.isoformat()}."
        )
        if interview.interview_link:
            body += f"\nInterview Link: {interview.interview_link}"
        if interview.venue:
            body += f"\nVenue: {interview.venue}"

        send_email(student.user.email, "Interview Reminder - HireTrack", body)
        reminders_sent += 1

    return {"interview_reminders_sent": reminders_sent}
