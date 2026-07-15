from datetime import datetime, timezone
import os

from flask import current_app, request, send_file
from flask_restful import Resource

from models import Application, CompanyProfile, JobPosition, Placement, StudentProfile, User, db
from utils.auth_decorators import jwt_required
from utils.cache import cache_delete, cache_get_json, cache_set_json, delete_pattern
from utils.mail_utils import send_email


def clear_admin_cache():
    cache_delete("admin_dashboard")
    delete_pattern("admin_companies*")
    delete_pattern("admin_students*")


def notify_admin_action(user, action):
    """Notify the account holder about an administrative change."""
    if not user or not user.email:
        return
    send_email(
        user.email,
        f"Account update: {action} - HireTrack",
        f"An administrator has {action.lower()} for your HireTrack account.",
    )


def write_pdf_report(file_path):
    """Create a dependency-free PDF using the built-in Helvetica font."""
    lines = ["HireTrack Administration Report", f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", ""]
    lines.append("STUDENTS")
    for student in StudentProfile.query.order_by(StudentProfile.name).all():
        lines.append(f"{student.name} | {student.contact or '-'} | {student.branch or '-'} | CGPA: {student.cgpa or '-'} | Skills: {student.skills or '-'}")
    lines.extend(["", "COMPANIES"])
    for company in CompanyProfile.query.order_by(CompanyProfile.name).all():
        status = "Blocked" if company.is_blacklisted else ("Approved" if company.is_approved else "Pending")
        lines.append(f"{company.name} | {company.industry or '-'} | {company.location or '-'} | {status}")
    lines.extend(["", "STUDENT-COMPANY RELATIONSHIPS"])
    for application in Application.query.order_by(Application.application_date.desc()).all():
        student_name = application.student.name if application.student else "Unknown"
        company_name = application.job.company.name if application.job and application.job.company else "Unknown"
        job_title = application.job.title if application.job else "Unknown"
        lines.append(f"{student_name} | {company_name} | {job_title} | {application.status} | {'Placed' if application.placement else '-'}")

    def escape(text):
        return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    pages = [lines[index:index + 46] for index in range(0, len(lines), 46)] or [[]]
    objects = ["<< /Type /Catalog /Pages 2 0 R >>", "<< /Type /Pages /Kids [" + " ".join(f"{3 + index * 2} 0 R" for index in range(len(pages))) + f"] /Count {len(pages)} >>"]
    for index, page_lines in enumerate(pages):
        page_id = 3 + index * 2
        content_id = page_id + 1
        stream = "BT /F1 9 Tf 36 806 Td 12 TL " + " ".join(f"({escape(line)[:150]}) Tj T*" for line in page_lines) + " ET"
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /Contents {content_id} 0 R >>")
        objects.append(f"<< /Length {len(stream.encode('latin-1', 'replace'))} >>\nstream\n{stream}\nendstream")
    output = "%PDF-1.4\n"
    offsets = [0]
    for number, obj in enumerate(objects, start=1):
        offsets.append(len(output.encode("latin-1", "replace")))
        output += f"{number} 0 obj\n{obj}\nendobj\n"
    xref = len(output.encode("latin-1", "replace"))
    output += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n" + "".join(f"{offset:010d} 00000 n \n" for offset in offsets[1:])
    output += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF"
    with open(file_path, "wb") as pdf_file:
        pdf_file.write(output.encode("latin-1", "replace"))


class AdminDashboard(Resource):
    @jwt_required(role="admin")
    def get(self):
        cached_dashboard = cache_get_json("admin_dashboard")
        if cached_dashboard:
            return cached_dashboard, 200

        result = {
            "total_users": User.query.count(),
            "total_students": StudentProfile.query.count(),
            "total_companies": CompanyProfile.query.count(),
            "total_jobs": JobPosition.query.count(),
            "total_applications": Application.query.count(),
            "pending_companies": CompanyProfile.query.filter_by(
                is_approved=False,
                is_blacklisted=False,
            ).count(),
            "pending_jobs": JobPosition.query.filter_by(status="Pending").count(),
        }

        cache_set_json("admin_dashboard", result)

        return result, 200


class PublicDashboard(Resource):
    """A privacy-safe overview for the public landing dashboard."""

    def get(self):
        status_counts = {
            status: Application.query.filter_by(status=status).count()
            for status in ("Applied", "Shortlisted", "Interview", "Offer", "Selected", "Placed")
        }
        active_jobs = JobPosition.query.filter_by(status="Approved").count()
        placements = Placement.query.join(Application).filter(Application.status == "Placed").count()
        students = StudentProfile.query.count()

        recent_jobs = (
            JobPosition.query.filter_by(status="Approved")
            .order_by(JobPosition.created_at.desc())
            .limit(4)
            .all()
        )

        return {
            "total_students": students,
            "total_companies": CompanyProfile.query.filter_by(
                is_approved=True, is_blacklisted=False
            ).count(),
            "active_jobs": active_jobs,
            "total_applications": Application.query.count(),
            "placement_rate": round((placements / students) * 100, 1) if students else 0,
            "application_funnel": status_counts,
            "recent_jobs": [
                {
                    "id": job.id,
                    "title": job.title,
                    "company": job.company.name if job.company else "Company",
                    "location": job.location,
                    "salary": job.salary,
                    "min_cgpa": job.min_cgpa,
                    "application_deadline": job.application_deadline.isoformat()
                    if job.application_deadline else None,
                }
                for job in recent_jobs
            ],
        }, 200


class ViewCompanies(Resource):
    @jwt_required(role="admin")
    def get(self):
        name_query = request.args.get("name", "").strip()
        industry_query = request.args.get("industry", "").strip()
        status_filter = request.args.get("status", "").strip()
        cache_key = f"admin_companies:{name_query}:{industry_query}:{status_filter}"

        cached_companies = cache_get_json(cache_key)
        if cached_companies:
            return cached_companies, 200

        query = CompanyProfile.query
        if name_query:
            query = query.filter(CompanyProfile.name.ilike(f"%{name_query}%"))
        if industry_query:
            query = query.filter(CompanyProfile.industry.ilike(f"%{industry_query}%"))
        if status_filter == "approved":
            query = query.filter_by(is_approved=True, is_blacklisted=False)
        elif status_filter == "pending":
            query = query.filter_by(is_approved=False, is_blacklisted=False)
        elif status_filter == "blacklisted":
            query = query.filter_by(is_blacklisted=True)

        companies = query.order_by(CompanyProfile.created_at.desc()).all()
        result = [
            {
                "id": c.id,
                "name": c.name,
                "industry": c.industry,
                "location": c.location,
                "website": c.website,
                "hr_contact": c.hr_contact,
                "is_approved": c.is_approved,
                "approved_by_admin": c.approved_by_admin,
                "is_blacklisted": c.is_blacklisted,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            } for c in companies
        ]

        cache_set_json(cache_key, result)

        return result, 200


class ViewStudents(Resource):
    @jwt_required(role="admin")
    def get(self):
        name_query = request.args.get("name", "").strip()
        contact_query = request.args.get("contact", "").strip()
        cache_key = f"admin_students:{name_query}:{contact_query}"

        cached_students = cache_get_json(cache_key)
        if cached_students:
            return cached_students, 200

        query = StudentProfile.query
        if name_query:
            query = query.filter(StudentProfile.name.ilike(f"%{name_query}%"))
        if contact_query:
            query = query.filter(StudentProfile.contact.ilike(f"%{contact_query}%"))

        students = query.order_by(StudentProfile.created_at.desc()).all()
        result = [
            {
                "id": s.id,
                "name": s.name,
                "contact": s.contact,
                "branch": s.branch,
                "year": s.year,
                "cgpa": s.cgpa,
                "skills": s.skills,
                "degree": s.degree,
                "institution": s.institution,
                "passout_year": s.passout_year,
                "experience": s.experience,
                "user_id": s.user_id,
                "status": s.user.status if s.user else "active",
            }
            for s in students
        ]

        cache_set_json(cache_key, result)

        return result, 200


class ApproveCompany(Resource):
    @jwt_required(role="admin")
    def post(self, company_id):
        company = db.session.get(CompanyProfile, company_id)
        if not company:
            return {"error": "Company not found"}, 404

        company.is_approved = True
        company.approved_by_admin = True

        db.session.commit()
        clear_admin_cache()
        notify_admin_action(company.user, "approved your company")

        return {"message": "Company approved"}, 200


class RemoveCompany(Resource):
    @jwt_required(role="admin")
    def delete(self, company_id):
        company = db.session.get(CompanyProfile, company_id)
        if not company:
            return {"error": "Company not found"}, 404

        company_cache_id = company.id
        user = db.session.get(User, company.user_id)

        notify_admin_action(user, "removed your company account")

        Placement.query.filter_by(company_id=company.id).delete()
        db.session.delete(company)
        if user:
            db.session.delete(user)
        db.session.commit()

        clear_admin_cache()
        delete_pattern("student_jobs*")
        cache_delete(f"company_jobs_{company_cache_id}")

        return {"message": "Company and related data removed"}, 200


class ApproveJob(Resource):
    @jwt_required(role="admin")
    def post(self, job_id):
        job = db.session.get(JobPosition, job_id)
        if not job:
            return {"error": "Job not found"}, 404

        job.status = "Approved"

        db.session.commit()
        clear_admin_cache()
        notify_admin_action(job.company.user if job.company else None, f"approved the {job.title} job posting")

        delete_pattern("student_jobs*")
        cache_delete(f"company_jobs_{job.company_id}")

        return {"message": "Job approved"}, 200


class RejectJob(Resource):
    @jwt_required(role="admin")
    def delete(self, job_id):
        job = db.session.get(JobPosition, job_id)
        if not job:
            return {"error": "Job not found"}, 404

        company_id = job.company_id
        company_user = job.company.user if job.company else None
        job_title = job.title
        db.session.delete(job)
        db.session.commit()

        clear_admin_cache()
        delete_pattern("student_jobs*")
        cache_delete(f"company_jobs_{company_id}")
        notify_admin_action(company_user, f"removed the {job_title} job posting")

        return {"message": "Job posting removed"}, 200


class ViewJobs(Resource):
    @jwt_required(role="admin")
    def get(self):
        status_filter = request.args.get("status", "").strip()
        query = JobPosition.query
        if status_filter:
            query = query.filter_by(status=status_filter)

        jobs = query.order_by(JobPosition.created_at.desc()).all()

        return [
            {
                "id": job.id,
                "company_id": job.company_id,
                "company_name": job.company.name if job.company else None,
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
                "application_deadline": job.application_deadline.isoformat() if job.application_deadline else None,
                "created_at": job.created_at.isoformat() if job.created_at else None,
            } for job in jobs
        ], 200


class ViewAllApplications(Resource):
    @jwt_required(role="admin")
    def get(self):
        status_filter = request.args.get("status", "").strip()
        query = Application.query
        if status_filter:
            query = query.filter_by(status=status_filter)

        applications = query.order_by(Application.application_date.desc()).all()
        result = []
        for application in applications:
            student = db.session.get(StudentProfile, application.student_id)
            job = db.session.get(JobPosition, application.job_id)
            company = db.session.get(CompanyProfile, job.company_id) if job else None
            result.append(
                {
                    "application_id": application.id,
                    "student_name": student.name if student else "Unknown",
                    "student_id": application.student_id,
                    "job_title": job.title if job else "Unknown",
                    "job_id": application.job_id,
                    "company_name": company.name if company else "Unknown",
                    "status": application.status,
                    "notes": application.notes,
                    "application_date": application.application_date.isoformat()
                    if application.application_date
                    else None,
                }
            )

        return result, 200


class BlacklistCompany(Resource):
    @jwt_required(role="admin")
    def patch(self, company_id):
        company = db.session.get(CompanyProfile, company_id)
        if not company:
            return {"error": "Company not found"}, 404

        body = request.get_json(silent=True) or {}
        is_blacklisted = body.get("is_blacklisted")

        if type(is_blacklisted) is not bool:
            return {"error": "is_blacklisted must be true or false"}, 400

        company.is_blacklisted = is_blacklisted
        db.session.commit()
        clear_admin_cache()
        notify_admin_action(
            company.user,
            "blocked your company" if is_blacklisted else "unblocked your company",
        )

        delete_pattern("student_jobs*")
        cache_delete(f"company_jobs_{company.id}")

        return {"message": "Company blacklist updated"}, 200


class UpdateUserStatus(Resource):
    @jwt_required(role="admin")
    def patch(self, user_id):
        user = db.session.get(User, user_id)
        if not user:
            return {"error": "User not found"}, 404

        body = request.get_json(silent=True) or {}
        status = body.get("status")

        if status not in ["active", "blocked"]:
            return {"error": "Invalid status"}, 400

        user.status = status
        db.session.commit()
        clear_admin_cache()
        notify_admin_action(user, "blocked your account" if status == "blocked" else "unblocked your account")

        return {"message": "User status updated"}, 200


class ExportAdminReport(Resource):
    @jwt_required(role="admin")
    def get(self):
        export_folder = current_app.config["EXPORT_FOLDER"]
        os.makedirs(export_folder, exist_ok=True)
        filename = f"hiretrack_admin_report_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.pdf"
        file_path = os.path.join(export_folder, filename)
        write_pdf_report(file_path)
        return send_file(file_path, mimetype="application/pdf", as_attachment=True, download_name=filename)


class PlacementAnalytics(Resource):
    @jwt_required(role="admin")
    def get(self):
        total_students = StudentProfile.query.count()
        total_companies = CompanyProfile.query.count()
        total_jobs = JobPosition.query.count()
        total_applications = Application.query.count()

        placement_count = Placement.query.join(Application).filter(Application.status == "Placed").count()
        total_selected = Application.query.filter(Application.status == "Offer").count()
        total_placed = placement_count

        placement_rate = 0
        if total_students > 0:
            placement_rate = round((total_placed / total_students) * 100, 2)

        top_companies = []
        if placement_count > 0:
            company_hires = {}
            placements = Placement.query.join(Application).filter(Application.status == "Placed").all()
            for placement in placements:
                company = db.session.get(CompanyProfile, placement.company_id)
                if not company:
                    continue
                company_hires[company.name] = company_hires.get(company.name, 0) + 1

            sorted_companies = sorted(
                company_hires.items(),
                key=lambda item: item[1],
                reverse=True,
            )
            top_companies = [name for name, _ in sorted_companies[:5]]

        recent_activity = []
        recent_applications = Application.query.order_by(Application.application_date.desc()).limit(5).all()
        for application in recent_applications:
            recent_activity.append(
                {
                    "student_id": application.student_id,
                    "job_id": application.job_id,
                    "status": application.status,
                }
            )

        return {
            "total_students": total_students,
            "total_companies": total_companies,
            "total_jobs": total_jobs,
            "total_applications": total_applications,
            "total_selected": total_selected,
            "total_placed": total_placed,
            "placement_rate": placement_rate,
            "top_companies": top_companies,
            "recent_activity": recent_activity,
        }, 200
