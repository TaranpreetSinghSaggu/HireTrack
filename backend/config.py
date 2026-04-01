import os

class Config:
    SECRET_KEY = "super-secret-key"

    SQLALCHEMY_DATABASE_URI = "sqlite:///placement.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

   
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