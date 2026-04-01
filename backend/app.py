from flask import Flask
from config import Config
from models import db, User
from flask_login import LoginManager
from flask_mail import Mail


login_manager = LoginManager()
mail = Mail()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    # USER LOADER
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # REGISTER BLUEPRINTS
    from routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # CREATE TABLES + ADMIN
    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(email="admin@ppa.com").first()
        if not admin:
            admin = User(email="admin@ppa.com", role="admin")
            admin.set_password("admin123")

            db.session.add(admin)
            db.session.commit()

            print("Admin created successfully")
        else:
            print("Admin already exists")

    return app


app = create_app()

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)