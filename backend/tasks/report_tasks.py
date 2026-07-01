from celery_worker import celery_app
from models import Application, CompanyProfile, JobPosition, Placement
from utils.mail_utils import send_email


@celery_app.task(name="tasks.report_tasks.generate_monthly_report")
def generate_monthly_report():
    total_jobs = JobPosition.query.count()
    total_applications = Application.query.count()

    placement_count = Placement.query.count()
    selected_count = Application.query.filter(
        Application.status.in_(["Selected", "Placed"])
    ).count()
    total_selected = placement_count if placement_count > 0 else selected_count

    admin_report_html = f"""
    <h2>Monthly Placement Report</h2>
    <p>Total Jobs Posted: {total_jobs}</p>
    <p>Total Applications: {total_applications}</p>
    <p>Total Selected/Placed Students: {total_selected}</p>
    """

    admin_email = getattr(celery_app.conf, "ADMIN_EMAIL", "admin@ppa.com")
    send_email(admin_email, "Monthly Placement Report - HireTrack", admin_report_html, html=True)

    companies = CompanyProfile.query.filter_by(
        is_approved=True,
        is_blacklisted=False,
    ).all()
    company_reports_sent = 0

    for company in companies:
        if not company.user or not company.user.email:
            continue

        jobs = JobPosition.query.filter_by(company_id=company.id).all()
        job_ids = [job.id for job in jobs]
        if not job_ids:
            continue

        company_applications = Application.query.filter(
            Application.job_id.in_(job_ids)
        ).all()

        shortlisted = sum(1 for app in company_applications if app.status == "Shortlisted")
        interview = sum(1 for app in company_applications if app.status == "Interview")
        selected = sum(
            1 for app in company_applications if app.status in ["Selected", "Placed"]
        )
        rejected = sum(1 for app in company_applications if app.status == "Rejected")

        company_report_html = f"""
        <h2>Monthly Placement Report - {company.name}</h2>
        <p>Total Job Postings: {len(job_ids)}</p>
        <p>Total Applications Received: {len(company_applications)}</p>
        <p>Shortlisted: {shortlisted}</p>
        <p>Interview: {interview}</p>
        <p>Selected/Placed: {selected}</p>
        <p>Rejected: {rejected}</p>
        """

        if send_email(
            company.user.email,
            f"Monthly Placement Report - {company.name}",
            company_report_html,
            html=True,
        ):
            company_reports_sent += 1

    return {
        "total_jobs": total_jobs,
        "total_applications": total_applications,
        "total_selected": total_selected,
        "company_reports_sent": company_reports_sent,
    }
