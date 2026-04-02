from flask_restful import Resource
from flask import request
from models import db, CompanyProfile, JobPosition, Application, StudentProfile
from utils.jwt_utils import extract_token, decode_token
from datetime import datetime


def parse_deadline(value):
    if value is None:
        return None

    if not isinstance(value, str):
        return None

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class CompanyDashboard(Resource):
    def get(self):
        token = extract_token(request)
        data = decode_token(token)

        if data["role"] != "company":
            return {"error": "Access denied"}, 403

        company = CompanyProfile.query.filter_by(user_id=data["user_id"]).first()
        jobs = JobPosition.query.filter_by(company_id=company.id).all()

        return {"total_jobs": len(jobs)}


class CreateJob(Resource):
    def post(self):
        token = extract_token(request)
        data_token = decode_token(token)

        if data_token["role"] != "company":
            return {"error": "Access denied"}, 403

        data = request.get_json()

        company = CompanyProfile.query.filter_by(user_id=data_token["user_id"]).first()

        job = JobPosition(
            company_id=company.id,
            title=data.get("title"),
            description=data.get("description"),
            application_deadline=data.get("application_deadline"),
            status="Pending"
        )

        db.session.add(job)
        db.session.commit()

        return {"message": "Job created"}, 201


class ViewApplicants(Resource):
    def get(self, job_id):
        token = extract_token(request)
        data = decode_token(token)

        if data["role"] != "company":
            return {"error": "Access denied"}, 403

        company = CompanyProfile.query.filter_by(user_id=data["user_id"]).first()
        job = JobPosition.query.get(job_id)

        if job.company_id != company.id:
            return {"error": "Unauthorized"}, 403

        apps = Application.query.filter_by(job_id=job_id).all()

        return [
            {
                "student_name": StudentProfile.query.get(a.student_id).name,
                "status": a.status
            } for a in apps
        ]


class CompanyJobs(Resource):
    def get(self):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data = decode_token(token)

        if "error" in data:
            return data, 401

        if data["role"] != "company":
            return {"error": "Access denied"}, 403

        company = CompanyProfile.query.filter_by(user_id=data["user_id"]).first()
        if not company:
            return {"error": "Company not found"}, 404

        jobs = JobPosition.query.filter_by(company_id=company.id).all()

        return [
            {
                "id": job.id,
                "title": job.title,
                "status": job.status,
                "application_deadline": job.application_deadline.isoformat() if job.application_deadline else None
            } for job in jobs
        ], 200


class UpdateCompanyJob(Resource):
    def patch(self, job_id):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data_token = decode_token(token)

        if "error" in data_token:
            return data_token, 401

        if data_token["role"] != "company":
            return {"error": "Access denied"}, 403

        company = CompanyProfile.query.filter_by(user_id=data_token["user_id"]).first()
        if not company:
            return {"error": "Company not found"}, 404

        job = JobPosition.query.get(job_id)
        if not job:
            return {"error": "Job not found"}, 404

        if job.company_id != company.id:
            return {"error": "Unauthorized"}, 403

        if job.status != "Pending":
            return {"error": "Only pending jobs can be updated"}, 400

        data = request.get_json()
        if not data:
            return {"error": "No data provided"}, 400

        if "title" in data:
            job.title = data.get("title")
        if "description" in data:
            job.description = data.get("description")
        if "salary" in data:
            job.salary = data.get("salary")
        if "skills_required" in data:
            job.skills_required = data.get("skills_required")
        if "experience_required" in data:
            job.experience_required = data.get("experience_required")
        if "location" in data:
            job.location = data.get("location")
        if "min_cgpa" in data:
            job.min_cgpa = data.get("min_cgpa")
        if "eligible_branches" in data:
            job.eligible_branches = data.get("eligible_branches")
        if "eligible_year" in data:
            job.eligible_year = data.get("eligible_year")
        if "application_deadline" in data:
            parsed_deadline = parse_deadline(data.get("application_deadline"))
            if not parsed_deadline:
                return {"error": "Invalid application_deadline"}, 400
            job.application_deadline = parsed_deadline

        db.session.commit()

        return {"message": "Job updated"}, 200


class UpdateApplicationStatus(Resource):
    def patch(self, application_id):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data_token = decode_token(token)

        if "error" in data_token:
            return data_token, 401

        if data_token["role"] != "company":
            return {"error": "Access denied"}, 403

        company = CompanyProfile.query.filter_by(user_id=data_token["user_id"]).first()
        if not company:
            return {"error": "Company not found"}, 404

        application = Application.query.get(application_id)
        if not application:
            return {"error": "Application not found"}, 404

        job = JobPosition.query.get(application.job_id)
        if not job or job.company_id != company.id:
            return {"error": "Unauthorized"}, 403

        data = request.get_json()
        if not data:
            return {"error": "No data provided"}, 400

        status = data.get("status")
        if status not in ["Shortlisted", "Rejected"]:
            return {"error": "Invalid status"}, 400

        application.status = status
        db.session.commit()

        return {"message": "Application status updated"}, 200
