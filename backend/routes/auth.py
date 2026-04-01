from flask import Blueprint, request, jsonify
from models import db, User, StudentProfile, CompanyProfile
from utils.jwt_utils import generate_token
from datetime import datetime

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register/student", methods=["POST"])
def register_student():

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    email = data.get("email", "").lower().strip()
    password = data.get("password")
    name = data.get("name")

    if not email or not password or not name:
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    # Create user
    user = User(email=email, role="student")
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    # Create student profile
    student = StudentProfile(
        user_id=user.id,
        name=name
    )

    db.session.add(student)
    db.session.commit()

    return jsonify({"message": "Student registered successfully"}), 201


@auth_bp.route("/register/company", methods=["POST"])
def register_company():

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    email = data.get("email", "").lower().strip()
    password = data.get("password")
    name = data.get("name")

    if not email or not password or not name:
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 400

    user = User(email=email, role="company")
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    company = CompanyProfile(
        user_id=user.id,
        name=name,
        is_approved=False
    )

    db.session.add(company)
    db.session.commit()

    return jsonify({
        "message": "Company registered. Waiting for admin approval."
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()

    email = data.get("email", "").lower().strip()
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401


    if user.role == "company":
        company = user.company_profile

        if not company.is_approved:
            return jsonify({"error": "Company not approved"}), 403

        if company.is_blacklisted:
            return jsonify({"error": "Company is blacklisted"}), 403


    if user.status == "blocked":
        return jsonify({"error": "User is blocked"}), 403

    user.last_login = datetime.utcnow()
    db.session.commit()

    # Generate Token
    token = generate_token(user)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "role": user.role,
        "user_id": user.id
    }), 200