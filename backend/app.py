from flask import Flask
from flask_restful import Api
from config import Config
from models import db, User
from flask_mail import Mail

mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    api = Api(app)

    # IMPORT ROUTES
    from routes.auth import RegisterStudent, RegisterCompany, Login, AuthMe
    from routes.student_routes import StudentDashboard, ApplyJob, ViewApplications, StudentJobs, StudentJobDetail, UpdateStudentProfile
    from routes.company_routes import CompanyDashboard, CreateJob, ViewApplicants, CompanyJobs, UpdateCompanyJob, UpdateApplicationStatus
    from routes.admin_routes import AdminDashboard, ViewCompanies, ApproveCompany, ApproveJob, ViewJobs, BlacklistCompany, UpdateUserStatus

    # AUTH
    api.add_resource(RegisterStudent, "/api/auth/register/student")
    api.add_resource(RegisterCompany, "/api/auth/register/company")
    api.add_resource(Login, "/api/auth/login")
    api.add_resource(AuthMe, "/api/auth/me")

    # STUDENT
    api.add_resource(StudentDashboard, "/api/student/dashboard")
    api.add_resource(ApplyJob, "/api/student/apply")
    api.add_resource(ViewApplications, "/api/student/applications")
    api.add_resource(StudentJobs, "/api/student/jobs")
    api.add_resource(StudentJobDetail, "/api/student/jobs/<int:job_id>")
    api.add_resource(UpdateStudentProfile, "/api/student/profile")

    # COMPANY
    api.add_resource(CompanyDashboard, "/api/company/dashboard")
    api.add_resource(CreateJob, "/api/company/create-job")
    api.add_resource(ViewApplicants, "/api/company/applicants/<int:job_id>")
    api.add_resource(CompanyJobs, "/api/company/jobs")
    api.add_resource(UpdateCompanyJob, "/api/company/jobs/<int:job_id>")
    api.add_resource(UpdateApplicationStatus, "/api/company/applications/<int:application_id>/status")

    # ADMIN
    api.add_resource(AdminDashboard, "/api/admin/dashboard")
    api.add_resource(ViewCompanies, "/api/admin/companies")
    api.add_resource(ApproveCompany, "/api/admin/approve-company/<int:company_id>")
    api.add_resource(ApproveJob, "/api/admin/approve-job/<int:job_id>")
    api.add_resource(ViewJobs, "/api/admin/jobs")
    api.add_resource(BlacklistCompany, "/api/admin/companies/<int:company_id>/blacklist")
    api.add_resource(UpdateUserStatus, "/api/admin/users/<int:user_id>/status")

    with app.app_context():
        db.create_all()

        admin = User.query.filter_by(email="admin@ppa.com").first()
        if not admin:
            admin = User(email="admin@ppa.com", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
