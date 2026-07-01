from celery import Celery

from app import create_app


flask_app = create_app()


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config["CELERY_BROKER_URL"],
        backend=app.config["CELERY_RESULT_BACKEND"],
        include=[
            "tasks.export_tasks",
            "tasks.email_tasks",
            "tasks.report_tasks",
        ],
    )

    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
        beat_schedule=app.config.get("CELERY_BEAT_SCHEDULE", {}),
        timezone="UTC",
        EXPORT_FOLDER=app.config.get("EXPORT_FOLDER"),
        ADMIN_EMAIL=app.config.get("ADMIN_EMAIL"),
    )

    class FlaskTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = FlaskTask
    return celery


celery_app = make_celery(flask_app)
