from app import app
from models import db, User
from utils.jwt_utils import generate_token, decode_token

with app.app_context():

    # 1. Get a user
    user = User.query.first()

    if not user:
        print("No user found. Create admin first.")
        exit()

    print("\n--- USER ---")
    print(user.email, user.role)

    # 2. Generate token
    token = generate_token(user)

    print("\n--- GENERATED TOKEN ---")
    print(token)

    # 3. Decode token
    decoded = decode_token(token)

    print("\n--- DECODED TOKEN ---")
    print(decoded)