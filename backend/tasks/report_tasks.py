from celery_worker import celery_app
from models import Application, JobPosition, Placement
from utils.mail_utils import send_email


@celery_app.task(name="tasks.report_tasks.generate_monthly_report")
def generate_monthly_report():
    total_jobs = JobPosition.query.count()
    total_applications = Application.query.count()

    placement_count = Placement.query.count()
    selected_count = Application.query.filter_by(status="Selected").count()
    total_selected = placement_count if placement_count > 0 else selected_count

    report_html = f"""
    <h2>Monthly Placement Report</h2>
    <p>Total Jobs: {total_jobs}</p>
    <p>Total Applications: {total_applications}</p>
    <p>Total Selected Students: {total_selected}</p>
    """

    admin_email = celery_app.conf.get("ADMIN_EMAIL", "admin@ppa.com")
    send_email(admin_email, "Monthly Placement Report", report_html, html=True)

    return {
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "total_selected": total_selected,
    }
