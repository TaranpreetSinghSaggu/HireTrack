import jwt
from datetime import datetime, timedelta, timezone
from flask import current_app

def generate_token(user):
    """
    Generates JWT token for a user
    """

    payload = {
        "user_id": user.id,
        "email": user.email,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),  # token expiry
        "iat": datetime.now(timezone.utc)
    }

    token = jwt.encode(
        payload,
        current_app.config["SECRET_KEY"],
        algorithm="HS256"
    )

    return token


def decode_token(token):
    """
    Decodes JWT token and returns payload
    """

    try:
        payload = jwt.decode(
            token,
            current_app.config["SECRET_KEY"],
            algorithms=["HS256"]
        )
        return payload

    except jwt.ExpiredSignatureError:
        return {"error": "Token expired"}

    except jwt.InvalidTokenError:
        return {"error": "Invalid token"}


def extract_token(request):
    """
    Extracts Bearer token from Authorization header
    """

    auth_header = request.headers.get("Authorization")

    if not auth_header:
        return None

    try:
        token = auth_header.split(" ")[1]
        return token
    except IndexError:
        return None