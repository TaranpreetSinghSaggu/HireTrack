from flask_restful import Resource
from flask import request
from models import db, StudentProfile, JobPosition, Application
from utils.jwt_utils import extract_token, decode_token
from datetime import datetime


class StudentDashboard(Resource):
    def get(self):
        token = extract_token(request)
        data = decode_token(token)

        if "error" in data:
            return data, 401

        if data["role"] != "student":
            return {"error": "Access denied"}, 403

        student = StudentProfile.query.filter_by(user_id=data["user_id"]).first()

        return {
            "name": student.name,
            "cgpa": student.cgpa
        }


class ApplyJob(Resource):
    def post(self):
        token = extract_token(request)
        data_token = decode_token(token)

        if "error" in data_token:
            return data_token, 401

        if data_token["role"] != "student":
            return {"error": "Access denied"}, 403

        data = request.get_json()
        job_id = data.get("job_id")

        student = StudentProfile.query.filter_by(user_id=data_token["user_id"]).first()
        job = JobPosition.query.get(job_id)

        if not job:
            return {"error": "Job not found"}, 404

        existing = Application.query.filter_by(student_id=student.id, job_id=job_id).first()
        if existing:
            return {"error": "Already applied"}, 400

        app = Application(student_id=student.id, job_id=job_id)
        db.session.add(app)
        db.session.commit()

        return {"message": "Applied successfully"}, 201


class ViewApplications(Resource):
    def get(self):
        token = extract_token(request)
        data = decode_token(token)

        if "error" in data:
            return data, 401

        if data["role"] != "student":
            return {"error": "Access denied"}, 403

        student = StudentProfile.query.filter_by(user_id=data["user_id"]).first()

        apps = Application.query.filter_by(student_id=student.id).all()

        return [
            {
                "id": a.id,
                "job_id": a.job_id,
                "status": a.status
            } for a in apps
        ]


class StudentJobs(Resource):
    def get(self):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data = decode_token(token)

        if "error" in data:
            return data, 401

        if data["role"] != "student":
            return {"error": "Access denied"}, 403

        now = datetime.utcnow()
        jobs = JobPosition.query.filter_by(status="Approved").all()

        result = []
        for job in jobs:
            if job.application_deadline and job.application_deadline > now:
                result.append(
                    {
                        "id": job.id,
                        "title": job.title,
                        "description": job.description,
                        "location": job.location,
                        "salary": job.salary,
                        "application_deadline": job.application_deadline.isoformat()
                    }
                )

        return result, 200


class StudentJobDetail(Resource):
    def get(self, job_id):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data = decode_token(token)

        if "error" in data:
            return data, 401

        if data["role"] != "student":
            return {"error": "Access denied"}, 403

        job = JobPosition.query.get(job_id)
        if not job:
            return {"error": "Job not found"}, 404

        now = datetime.utcnow()
        if job.status != "Approved" or not job.application_deadline or job.application_deadline <= now:
            return {"error": "Job not found"}, 404

        return {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "salary": job.salary,
            "skills_required": job.skills_required,
            "experience_required": job.experience_required,
            "location": job.location,
            "min_cgpa": job.min_cgpa,
            "eligible_branches": job.eligible_branches,
            "eligible_year": job.eligible_year,
            "application_deadline": job.application_deadline.isoformat(),
            "status": job.status
        }, 200


class UpdateStudentProfile(Resource):
    def patch(self):
        token = extract_token(request)
        if not token:
            return {"error": "Token missing"}, 401

        data_token = decode_token(token)

        if "error" in data_token:
            return data_token, 401

        if data_token["role"] != "student":
            return {"error": "Access denied"}, 403

        student = StudentProfile.query.filter_by(user_id=data_token["user_id"]).first()
        if not student:
            return {"error": "Student not found"}, 404

        data = request.get_json()
        if not data:
            return {"error": "No data provided"}, 400

        if "skills" in data:
            student.skills = data.get("skills")
        if "cgpa" in data:
            student.cgpa = data.get("cgpa")
        if "branch" in data:
            student.branch = data.get("branch")
        if "year" in data:
            student.year = data.get("year")

        db.session.commit()

        return {"message": "Profile updated"}, 200
