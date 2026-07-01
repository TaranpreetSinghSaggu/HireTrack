from functools import wraps

from flask import g, request

from models import CompanyProfile, StudentProfile, User, db
from utils.jwt_utils import decode_token, extract_token


def jwt_required(role=None):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            token = extract_token(request)
            if not token:
                return {"error": "Token missing"}, 401

            data = decode_token(token)
            if "error" in data:
                return data, 401

            user = db.session.get(User, data["user_id"])
            if not user:
                return {"error": "User not found"}, 404

            if user.status == "blocked":
                return {"error": "User blocked"}, 403

            if role and user.role != role:
                return {"error": "Access denied"}, 403

            g.current_user = user
            g.current_token = data

            if user.role == "student":
                student = StudentProfile.query.filter_by(user_id=user.id).first()
                if role == "student" and not student:
                    return {"error": "Student not found"}, 404
                g.current_student = student

            if user.role == "company":
                company = CompanyProfile.query.filter_by(user_id=user.id).first()
                if role == "company" and not company:
                    return {"error": "Company not found"}, 404
                if role == "company" and not company.is_approved:
                    return {"error": "Company not approved"}, 403
                if role == "company" and company.is_blacklisted:
                    return {"error": "Company blacklisted"}, 403
                g.current_company = company

            return function(*args, **kwargs)

        return wrapper

    return decorator
