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

    migrations = {
        "benefits": "ALTER TABLE job_positions ADD COLUMN benefits TEXT",
        "resume_path": "ALTER TABLE student_profiles ADD COLUMN resume_path VARCHAR(500)",
        "offer_salary": "ALTER TABLE applications ADD COLUMN offer_salary INTEGER",
        "offer_joining_date": "ALTER TABLE applications ADD COLUMN offer_joining_date DATETIME",
        "offer_remarks": "ALTER TABLE applications ADD COLUMN offer_remarks TEXT",
        "offer_letter_path": "ALTER TABLE applications ADD COLUMN offer_letter_path VARCHAR(500)",
    }

    table_columns = {}
    for table in ("job_positions", "student_profiles", "applications"):
        table_columns[table] = {
            row[1]
            for row in db.session.execute(db.text(f"PRAGMA table_info({table})"))
        }

    changes = [
        ("job_positions", "benefits"),
        ("student_profiles", "resume_path"),
        ("applications", "offer_salary"),
        ("applications", "offer_joining_date"),
        ("applications", "offer_remarks"),
        ("applications", "offer_letter_path"),
    ]
    for table, column in changes:
        if column not in table_columns[table]:
            db.session.execute(db.text(migrations[column]))

    if any(column not in table_columns[table] for table, column in changes):
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
    from routes.student_routes import StudentDashboard, ApplyJob, ViewApplications, StudentJobs, StudentJobDetail, UpdateStudentProfile, UploadResume, StudentJobReadiness, InterviewQuestions, StudentStrategy, ApplicationAnalysis, StudentInterviews, StudentPlacements, ExportApplications, StudentOfferLetter, TaskStatus
    from routes.company_routes import CompanyDashboard, CreateJob, ViewApplicants, CompanyApplicants, CompanyJobs, UpdateCompanyJob, UpdateApplicationStatus, CandidateMatchScores, MarketInsight, JobInterviewQuestions, ScheduleInterview, GetInterviewsForJob, CompanyInterviews, CreateOffer, PlaceCandidate, CompanyResume, CloseJob, ExportCompanyApplications, CompanyExportDownload
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
    api.add_resource(StudentOfferLetter, "/api/student/applications/<int:application_id>/offer-letter")

    # COMPANY
    api.add_resource(CompanyDashboard, "/api/company/dashboard")
    api.add_resource(CreateJob, "/api/company/create-job")
    api.add_resource(ViewApplicants, "/api/company/applicants/<int:job_id>")
    api.add_resource(CompanyApplicants, "/api/company/applicants")
    api.add_resource(CompanyJobs, "/api/company/jobs")
    api.add_resource(UpdateCompanyJob, "/api/company/jobs/<int:job_id>")
    api.add_resource(UpdateApplicationStatus, "/api/company/applications/<int:application_id>/status")
    api.add_resource(CandidateMatchScores, "/api/company/jobs/<int:job_id>/match-scores")
    api.add_resource(MarketInsight, "/api/company/jobs/<int:job_id>/market-insight")
    api.add_resource(JobInterviewQuestions, "/api/company/jobs/<int:job_id>/questions")
    api.add_resource(ScheduleInterview, "/api/company/applications/<int:application_id>/schedule-interview")
    api.add_resource(GetInterviewsForJob, "/api/company/jobs/<int:job_id>/interviews")
    api.add_resource(CompanyInterviews, "/api/company/interviews")
    api.add_resource(CreateOffer, "/api/company/applications/<int:application_id>/offer")
    api.add_resource(PlaceCandidate, "/api/company/applications/<int:application_id>/place")
    api.add_resource(CompanyResume, "/api/company/applications/<int:application_id>/resume")
    api.add_resource(CloseJob, "/api/company/jobs/<int:job_id>/close")
    api.add_resource(ExportCompanyApplications, "/api/company/export")
    api.add_resource(CompanyExportDownload, "/api/company/export/<string:task_id>/download")

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
