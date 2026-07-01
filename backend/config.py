import os
from dotenv import load_dotenv
from celery.schedules import crontab

load_dotenv()


BASE_DIR = os.path.dirname(__file__)


def resolve_database_url():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        db_path = os.path.join(BASE_DIR, "placement.db")
        return "sqlite:///" + db_path.replace("\\", "/")

    sqlite_prefix = "sqlite:///"
    if database_url.startswith(sqlite_prefix):
        db_path = database_url[len(sqlite_prefix):]
        if db_path and not os.path.isabs(db_path):
            db_path = os.path.join(BASE_DIR, db_path)
            return sqlite_prefix + db_path.replace("\\", "/")

    return database_url


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "b44e742bea2fbe7b2dc6bcae1c410b20f13e4d5f2baae6edf61be6a30f688dfa")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@ppa.com")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

    SQLALCHEMY_DATABASE_URI = resolve_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    AIPIPE_API_KEY = os.getenv("AIPIPE_API_KEY")
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@example.com")
    EXPORT_FOLDER = os.getenv(
        "EXPORT_FOLDER",
        os.path.join(BASE_DIR, "exports"),
    )

    CELERY_BEAT_SCHEDULE = {
        "daily-deadline-reminders": {
            "task": "tasks.email_tasks.send_deadline_reminders",
            "schedule": crontab(hour=9, minute=0),
        },
        "monthly-placement-report": {
            "task": "tasks.report_tasks.generate_monthly_report",
            "schedule": crontab(hour=9, minute=0, day_of_month=1),
        },
        "daily-interview-reminders": {
            "task": "tasks.email_tasks.send_interview_reminders",
            "schedule": crontab(hour=8, minute=0),
        },
    }
