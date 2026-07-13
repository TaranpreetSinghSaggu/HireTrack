from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from config import Config
from models import db, User
from flask_mail import Mail

mail = Mail()


def add_missing_sqlite_columns():
    if not db.engine.url.drivername.startswith("sqlite"):
        return

    existing_columns = {
        row[1]
        for row in db.session.execute(db.text("PRAGMA table_info(job_positions)"))
    }

    if "benefits" not in existing_columns:
        db.session.execute(db.text("ALTER TABLE job_positions ADD COLUMN benefits TEXT"))
        db.session.commit()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)
    mail.init_app(app)

    api = Api(app)

    # IMPORT ROUTES
    from routes.auth import RegisterStudent, RegisterCompany, Login, AuthMe
    from routes.student_routes import StudentDashboard, ApplyJob, ViewApplications, StudentJobs, StudentJobDetail, UpdateStudentProfile, UploadResume, StudentJobReadiness, InterviewQuestions, StudentStrategy, ApplicationAnalysis, StudentInterviews, StudentPlacements, ExportApplications, TaskStatus
    from routes.company_routes import CompanyDashboard, CreateJob, ViewApplicants, CompanyJobs, UpdateCompanyJob, UpdateApplicationStatus, CandidateMatchScores, MarketInsight, JobInterviewQuestions, ScheduleInterview, GetInterviewsForJob, CloseJob, ExportCompanyApplications
    from routes.admin_routes import AdminDashboard, PublicDashboard, ViewCompanies, ViewStudents, ApproveCompany, RemoveCompany, ApproveJob, RejectJob, ViewJobs, ViewAllApplications, BlacklistCompany, UpdateUserStatus, ExportAdminReport, PlacementAnalytics

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
    api.add_resource(UploadResume, "/api/student/resume")
    api.add_resource(StudentJobReadiness, "/api/student/jobs/<int:job_id>/readiness")
    api.add_resource(InterviewQuestions, "/api/student/interview-questions")
    api.add_resource(StudentStrategy, "/api/student/strategy")
    api.add_resource(ApplicationAnalysis, "/api/student/applications/<int:application_id>/analysis")
    api.add_resource(StudentInterviews, "/api/student/interviews")
    api.add_resource(StudentPlacements, "/api/student/placements")
    api.add_resource(ExportApplications, "/api/student/export")

    # COMPANY
    api.add_resource(CompanyDashboard, "/api/company/dashboard")
    api.add_resource(CreateJob, "/api/company/create-job")
    api.add_resource(ViewApplicants, "/api/company/applicants/<int:job_id>")
    api.add_resource(CompanyJobs, "/api/company/jobs")
    api.add_resource(UpdateCompanyJob, "/api/company/jobs/<int:job_id>")
    api.add_resource(UpdateApplicationStatus, "/api/company/applications/<int:application_id>/status")
    api.add_resource(CandidateMatchScores, "/api/company/jobs/<int:job_id>/match-scores")
    api.add_resource(MarketInsight, "/api/company/jobs/<int:job_id>/market-insight")
    api.add_resource(JobInterviewQuestions, "/api/company/jobs/<int:job_id>/questions")
    api.add_resource(ScheduleInterview, "/api/company/applications/<int:application_id>/schedule-interview")
    api.add_resource(GetInterviewsForJob, "/api/company/jobs/<int:job_id>/interviews")
    api.add_resource(CloseJob, "/api/company/jobs/<int:job_id>/close")
    api.add_resource(ExportCompanyApplications, "/api/company/export")

    # ADMIN
    api.add_resource(PublicDashboard, "/api/dashboard")
    api.add_resource(AdminDashboard, "/api/admin/dashboard")
    api.add_resource(ViewCompanies, "/api/admin/companies")
    api.add_resource(ViewStudents, "/api/admin/students")
    api.add_resource(ApproveCompany, "/api/admin/approve-company/<int:company_id>")
    api.add_resource(RemoveCompany, "/api/admin/companies/<int:company_id>/remove")
    api.add_resource(ApproveJob, "/api/admin/approve-job/<int:job_id>")
    api.add_resource(RejectJob, "/api/admin/jobs/<int:job_id>/remove")
    api.add_resource(ViewJobs, "/api/admin/jobs")
    api.add_resource(ViewAllApplications, "/api/admin/applications")
    api.add_resource(BlacklistCompany, "/api/admin/companies/<int:company_id>/blacklist")
    api.add_resource(UpdateUserStatus, "/api/admin/users/<int:user_id>/status")
    api.add_resource(ExportAdminReport, "/api/admin/reports/export-pdf")
    api.add_resource(PlacementAnalytics, "/api/admin/analytics/placement")
    api.add_resource(TaskStatus, "/api/task/<string:task_id>")

    with app.app_context():
        db.create_all()
        add_missing_sqlite_columns()

        admin = User.query.filter_by(email=app.config["ADMIN_EMAIL"]).first()
        if not admin:
            admin = User(email=app.config["ADMIN_EMAIL"], role="admin")
            admin.set_password(app.config["ADMIN_PASSWORD"])
            db.session.add(admin)
            db.session.commit()

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
