import csv
import os
from datetime import datetime , timezone

from celery_worker import celery_app
from models import Application, JobPosition, StudentProfile


@celery_app.task(name="tasks.export_tasks.export_applications")
def export_applications(student_id):
    student = StudentProfile.query.get(student_id)
    if not student:
        return {"error": "Student not found"}

    applications = Application.query.filter_by(student_id=student_id).all()

    export_folder = celery_app.conf.get("EXPORT_FOLDER")
    if not export_folder:
        export_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")

    os.makedirs(export_folder, exist_ok=True)

    filename = f"applications_student_{student_id}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.csv"
    file_path = os.path.join(export_folder, filename)

    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["application_id", "job_id", "job_title", "status", "application_date"])

        for application in applications:
            job = JobPosition.query.get(application.job_id)
            writer.writerow(
                [
                    application.id,
                    application.job_id,
                    job.title if job else "",
                    application.status,
                    application.application_date.isoformat() if application.application_date else "",
                ]
            )

    return {"file_path": file_path}
