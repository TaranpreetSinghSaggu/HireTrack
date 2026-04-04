from flask_restful import Resource
from flask import request
from models import db, CompanyProfile, JobPosition, User, StudentProfile, Application, Placement
from utils.jwt_utils import extract_token, decode_token
import json
from utils.cache import cache


class AdminDashboard(Resource):
    def get(self):
        token = extract_token(request)
        data = decode_token(token)

        if data["role"] != "admin":
            return {"error": "Access denied"}, 403

        try:
            cached_dashboard = cache.get("admin_dashboard")
            if cached_dashboard:
                return json.loads(cached_dashboard), 200
        except Exception:
            pass

        result = {
            "users": User.query.count(),
            "companies": CompanyProfile.query.count(),
            "jobs": JobPosition.query.count()
        }

        try:
            cache.setex("admin_dashboard", 300, json.dumps(result))
        except Exception:
            pass

        return result


class ViewCompanies(Resource):
    def get(self):
        token = extract_token(request)
        data = decode_token(token)

        if data["role"] != "admin":
            return {"error": "Access denied"}, 403

        companies = CompanyProfile.query.all()

        return [
            {
                "id": c.id,
                "name": c.name,
                "approved": c.is_approved
            } for c in companies
        ]


class ApproveCompany(Resource):
    def post(self, company_id):
        token = extract_token(request)
        data = decode_token(token)

        if data["role"] != "admin":
            return {"error": "Access denied"}, 403

        company = CompanyProfile.query.get(company_id)
        company.is_approved = True

        db.session.commit()

        try:
            cache.delete("admin_dashboard")
        except Exception:
            pass

        return {"message": "Company approved"}


class ApproveJob(Resource):
    def post(self, job_id):
        token = extract_token(request)
        data = decode_token(token)

        if data["role"] != "admin":
            return {"error": "Access denied"}, 403

        job = JobPosition.query.get(job_id)
        job.status = "Approved"

        db.session.commit()

        try:
            cache.delete("student_jobs")
            cache.delete("admin_dashboard")
            cache.delete(f"company_jobs_{job.company_id}")
        except Exception:
            pass

        return {"message": "Job approved"}


class ViewJobs(Resource):
    def get(self):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data = decode_token(token)

        if "error" in data:
            return data, 401

        if data["role"] != "admin":
            return {"error": "Access denied"}, 403

        jobs = JobPosition.query.all()

        return [
            {
                "id": job.id,
                "company_id": job.company_id,
                "title": job.title,
                "status": job.status,
                "application_deadline": job.application_deadline.isoformat() if job.application_deadline else None
            } for job in jobs
        ], 200


class BlacklistCompany(Resource):
    def patch(self, company_id):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data = decode_token(token)

        if "error" in data:
            return data, 401

        if data["role"] != "admin":
            return {"error": "Access denied"}, 403

        company = CompanyProfile.query.get(company_id)
        if not company:
            return {"error": "Company not found"}, 404

        body = request.get_json() or {}
        is_blacklisted = body.get("is_blacklisted")

        if type(is_blacklisted) is not bool:
            return {"error": "is_blacklisted must be true or false"}, 400

        company.is_blacklisted = is_blacklisted
        db.session.commit()

        try:
            cache.delete("admin_dashboard")
        except Exception:
            pass

        return {"message": "Company blacklist updated"}, 200


class UpdateUserStatus(Resource):
    def patch(self, user_id):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data = decode_token(token)

        if "error" in data:
            return data, 401

        if data["role"] != "admin":
            return {"error": "Access denied"}, 403

        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        body = request.get_json() or {}
        status = body.get("status")

        if status not in ["active", "blocked"]:
            return {"error": "Invalid status"}, 400

        user.status = status
        db.session.commit()

        try:
            cache.delete("admin_dashboard")
        except Exception:
            pass

        return {"message": "User status updated"}, 200


class PlacementAnalytics(Resource):
    def get(self):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data = decode_token(token)

        if "error" in data:
            return data, 401

        if data["role"] != "admin":
            return {"error": "Access denied"}, 403

        total_students = StudentProfile.query.count()
        total_companies = CompanyProfile.query.count()
        total_jobs = JobPosition.query.count()
        total_applications = Application.query.count()

        placement_count = Placement.query.count()
        selected_count = Application.query.filter_by(status="Selected").count()
        total_selected = placement_count if placement_count > 0 else selected_count

        placement_rate = 0
        if total_students > 0:
            placement_rate = round((total_selected / total_students) * 100, 2)

        top_companies = []
        if placement_count > 0:
            company_hires = {}
            placements = Placement.query.all()
            for placement in placements:
                company = CompanyProfile.query.get(placement.company_id)
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
