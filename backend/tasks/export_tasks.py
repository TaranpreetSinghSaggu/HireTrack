import csv
import os
from datetime import datetime , timezone

from celery_worker import celery_app
from models import Application, CompanyProfile, JobPosition, Placement, StudentProfile, db
from utils.mail_utils import send_email


@celery_app.task(name="tasks.export_tasks.export_applications")
def export_applications(student_id):
    student = db.session.get(StudentProfile, student_id)
    if not student:
        return {"error": "Student not found"}

    applications = Application.query.filter_by(student_id=student_id).all()

    export_folder = getattr(celery_app.conf, "EXPORT_FOLDER", None)
    if not export_folder:
        export_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")

    os.makedirs(export_folder, exist_ok=True)

    filename = f"applications_student_{student_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.csv"
    file_path = os.path.join(export_folder, filename)

    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "type",
                "application_id",
                "job_id",
                "job_title",
                "status",
                "application_date",
                "placement_id",
                "company_id",
                "position",
                "salary",
                "joining_date",
                "placed_date",
            ]
        )

        for application in applications:
            job = db.session.get(JobPosition, application.job_id)
            placement = Placement.query.filter_by(application_id=application.id).first()
            writer.writerow(
                [
                    "application",
                    application.id,
                    application.job_id,
                    job.title if job else "",
                    application.status,
                    application.application_date.isoformat() if application.application_date else "",
                    placement.id if placement else "",
                    placement.company_id if placement else "",
                    placement.position if placement else "",
                    placement.salary if placement else "",
                    placement.joining_date.isoformat()
                    if placement and placement.joining_date
                    else "",
                    placement.placed_date.isoformat()
                    if placement and placement.placed_date
                    else "",
                ]
            )

    if student.user and student.user.email:
        send_email(
            student.user.email,
            "Your Application Export is Ready - HireTrack",
            (
                "Your application history export has been completed.\n\n"
                f"File: {filename}\n"
                f"Total applications exported: {len(applications)}\n\n"
                "Please contact your placement coordinator to access the file."
            ),
        )

    return {"file_path": file_path, "total_exported": len(applications)}


@celery_app.task(name="tasks.export_tasks.export_company_applications")
def export_company_applications(company_id):
    company = db.session.get(CompanyProfile, company_id)
    if not company:
        return {"error": "Company not found"}

    jobs = JobPosition.query.filter_by(company_id=company_id).all()

    export_folder = getattr(celery_app.conf, "EXPORT_FOLDER", None)
    if not export_folder:
        export_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")

    os.makedirs(export_folder, exist_ok=True)

    filename = f"applications_company_{company_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.csv"
    file_path = os.path.join(export_folder, filename)

    total_exported = 0
    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "application_id",
                "job_id",
                "job_title",
                "job_benefits",
                "student_id",
                "student_name",
                "status",
                "application_date",
                "placement_id",
            ]
        )

        for job in jobs:
            applications = Application.query.filter_by(job_id=job.id).all()
            for application in applications:
                student = db.session.get(StudentProfile, application.student_id)
                placement = Placement.query.filter_by(application_id=application.id).first()
                writer.writerow(
                    [
                        application.id,
                        job.id,
                        job.title,
                        job.benefits,
                        application.student_id,
                        student.name if student else "Unknown",
                        application.status,
                        application.application_date.isoformat()
                        if application.application_date
                        else "",
                        placement.id if placement else "",
                    ]
                )
                total_exported += 1

    if company.user and company.user.email:
        send_email(
            company.user.email,
            "Your Applications Export is Ready - HireTrack",
            (
                "Your applications export has been completed.\n\n"
                f"File: {filename}\n"
                f"Total applications exported: {total_exported}\n\n"
                "Please contact your HireTrack coordinator to access the file."
            ),
        )

    return {"file_path": file_path, "total_exported": total_exported}
