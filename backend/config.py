import os
from dotenv import load_dotenv
load_dotenv()
class Config:
    SECRET_KEY = "b44e742bea2fbe7b2dc6bcae1c410b20f13e4d5f2baae6edf61be6a30f688dfa"

    SQLALCHEMY_DATABASE_URI = "sqlite:///placement.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AIPIPE_API_KEY = os.getenv("AIPIPE_API_KEY")

   
#     MAIL_SERVER = "smtp.gmail.com"
#     MAIL_PORT = 587
#     MAIL_USE_TLS = True
#     MAIL_USERNAME = "email@gmail.com"      
#     MAIL_PASSWORD = "app_password"        
#     MAIL_DEFAULT_SENDER = "email@gmail.com"

#    REDIS
#     REDIS_URL = "redis://localhost:6379/0"

#      CELERY 
#     CELERY_BROKER_URL = REDIS_URL
#     CELERY_RESULT_BACKEND = REDIS_URL