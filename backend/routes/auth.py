from flask_restful import Resource
from flask import g, request
from models import db, User, StudentProfile, CompanyProfile
from utils.auth_decorators import jwt_required
from utils.jwt_utils import generate_token
from datetime import datetime, timezone


class RegisterStudent(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}

        email = data.get("email", "").lower().strip()
        password = data.get("password")
        name = data.get("name")

        if not email or not password or not name:
            return {"error": "Missing fields"}, 400

        if User.query.filter_by(email=email).first():
            return {"error": "Email exists"}, 400

        user = User(email=email, role="student")
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        student = StudentProfile(user_id=user.id, name=name)
        db.session.add(student)
        db.session.commit()

        return {"message": "Student registered"}, 201


class RegisterCompany(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}

        email = data.get("email", "").lower().strip()
        password = data.get("password")
        name = data.get("name")

        if not email or not password or not name:
            return {"error": "Missing fields"}, 400

        if User.query.filter_by(email=email).first():
            return {"error": "Email exists"}, 400

        user = User(email=email, role="company")
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        company = CompanyProfile(
            user_id=user.id,
            name=name,
            hr_contact=data.get("hr_contact"),
            website=data.get("website"),
            industry=data.get("industry"),
            location=data.get("location"),
        )
        db.session.add(company)
        db.session.commit()

        return {"message": "Company registered, waiting approval"}, 201


class Login(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}

        email = data.get("email", "").lower().strip()
        password = data.get("password")

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            return {"error": "Invalid credentials"}, 401

        if user.role == "company":
            company = user.company_profile
            if not company.is_approved:
                return {"error": "Company not approved"}, 403
            if company.is_blacklisted:
                return {"error": "Company blacklisted"}, 403

        if user.status == "blocked":
            return {"error": "User blocked"}, 403

        user.last_login = datetime.now(timezone.utc)
        db.session.commit()

        token = generate_token(user)

        return {
            "token": token,
            "role": user.role,
            "user_id": user.id
        }, 200


class AuthMe(Resource):
    @jwt_required()
    def get(self):
        return {
            "user_id": g.current_user.id,
            "role": g.current_user.role
        }, 200
