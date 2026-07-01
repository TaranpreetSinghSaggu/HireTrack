from flask import request
from flask_restful import Resource

from models import Application, CompanyProfile, JobPosition, Placement, StudentProfile, User, db
from utils.auth_decorators import jwt_required
from utils.cache import cache_delete, cache_get_json, cache_set_json, delete_pattern


def clear_admin_cache():
    cache_delete("admin_dashboard")
    delete_pattern("admin_companies*")
    delete_pattern("admin_students*")


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
        student_id = request.args.get("id", "").strip()
        cache_key = f"admin_students:{name_query}:{contact_query}:{student_id}"

        cached_students = cache_get_json(cache_key)
        if cached_students:
            return cached_students, 200

        query = StudentProfile.query
        if student_id.isdigit():
            query = query.filter_by(id=int(student_id))
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

        return {"message": "Company approved"}, 200


class RemoveCompany(Resource):
    @jwt_required(role="admin")
    def delete(self, company_id):
        company = db.session.get(CompanyProfile, company_id)
        if not company:
            return {"error": "Company not found"}, 404

        company_cache_id = company.id
        user = db.session.get(User, company.user_id)

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
        db.session.delete(job)
        db.session.commit()

        clear_admin_cache()
        delete_pattern("student_jobs*")
        cache_delete(f"company_jobs_{company_id}")

        return {"message": "Job posting removed"}, 200


class ViewJobs(Resource):
    @jwt_required(role="admin")
    def get(self):
        status_filter = request.args.get("status", "").strip()
        company_id_filter = request.args.get("company_id", "").strip()

        query = JobPosition.query
        if status_filter:
            query = query.filter_by(status=status_filter)
        if company_id_filter.isdigit():
            query = query.filter_by(company_id=int(company_id_filter))

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
        job_id_filter = request.args.get("job_id", "").strip()

        query = Application.query
        if status_filter:
            query = query.filter_by(status=status_filter)
        if job_id_filter.isdigit():
            query = query.filter_by(job_id=int(job_id_filter))

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

        return {"message": "User status updated"}, 200


class PlacementAnalytics(Resource):
    @jwt_required(role="admin")
    def get(self):
        total_students = StudentProfile.query.count()
        total_companies = CompanyProfile.query.count()
        total_jobs = JobPosition.query.count()
        total_applications = Application.query.count()

        placement_count = Placement.query.count()
        selected_count = Application.query.filter(
            Application.status.in_(["Selected", "Placed"])
        ).count()
        total_selected = placement_count if placement_count > 0 else selected_count

        placement_rate = 0
        if total_students > 0:
            placement_rate = round((total_selected / total_students) * 100, 2)

        top_companies = []
        if placement_count > 0:
            company_hires = {}
            placements = Placement.query.all()
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
            "placement_rate": placement_rate,
            "top_companies": top_companies,
            "recent_activity": recent_activity,
        }, 200
