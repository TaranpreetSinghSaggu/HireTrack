from datetime import datetime, timedelta , timezone

from celery_worker import celery_app
from models import JobPosition, StudentProfile
from utils.mail_utils import send_email


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

        if job.application_deadline < now or job.application_deadline > end_time:
            continue

        students = StudentProfile.query.all()
        for student in students:
            if not student.user or not student.user.email:
                continue

            if not student_matches_job(student, job):
                continue

            body = (
                f"Reminder: The job '{job.title}' has an application deadline on "
                f"{job.application_deadline.isoformat()}."
            )
            send_email(student.user.email, "Placement Deadline Reminder", body)
            reminders_sent += 1

    return {"reminders_sent": reminders_sent}
