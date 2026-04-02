from flask_restful import Resource
from flask import request
from models import db, CompanyProfile, JobPosition, User
from utils.jwt_utils import extract_token, decode_token


class AdminDashboard(Resource):
    def get(self):
        token = extract_token(request)
        data = decode_token(token)

        if data["role"] != "admin":
            return {"error": "Access denied"}, 403

        return {
            "users": User.query.count(),
            "companies": CompanyProfile.query.count(),
            "jobs": JobPosition.query.count()
        }


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

        return {"message": "User status updated"}, 200
