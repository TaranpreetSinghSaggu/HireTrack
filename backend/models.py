from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)

    role = db.Column(
        db.Enum('admin', 'company', 'student', name='user_roles'),
        nullable=False
    )

    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    status = db.Column(
        db.Enum('active', 'blocked', name='user_status'),
        default='active'
    )

    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    company_profile = db.relationship(
        'CompanyProfile',
        backref='user',
        uselist=False,
        cascade='all, delete-orphan'
    )

    student_profile = db.relationship(
        'StudentProfile',
        backref='user',
        uselist=False,
        cascade='all, delete-orphan'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __str__(self):
        return f"{self.email} ({self.role})"


class CompanyProfile(db.Model):
    __tablename__ = 'company_profiles'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        unique=True
    )

    name = db.Column(db.String(200), nullable=False)
    hr_contact = db.Column(db.String(100))
    website = db.Column(db.String(200))

    industry = db.Column(db.String(100))
    location = db.Column(db.String(100))

    is_approved = db.Column(db.Boolean, default=False)
    approved_by_admin = db.Column(db.Boolean, default=False)
    is_blacklisted = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    job_positions = db.relationship(
        'JobPosition',
        backref='company',
        lazy=True,
        cascade='all, delete-orphan'
    )

    placements = db.relationship('Placement', backref='company', lazy=True)

    def __str__(self):
        return self.name


class StudentProfile(db.Model):
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        unique=True
    )

    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(15))

    skills = db.Column(db.Text)

    cgpa = db.Column(db.Float)
    branch = db.Column(db.String(100))
    year = db.Column(db.Integer)

    degree = db.Column(db.String(100))
    institution = db.Column(db.String(200))
    passout_year = db.Column(db.Integer)
    experience = db.Column(db.Text)

    resume_filename = db.Column(db.String(200))
    profile_pic = db.Column(db.String(200))
    resume_score = db.Column(db.Float)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    applications = db.relationship(
        'Application',
        backref='student',
        lazy=True,
        cascade='all, delete-orphan'
    )

    placements = db.relationship('Placement', backref='student', lazy=True)

    def __str__(self):
        return self.name


class JobPosition(db.Model):
    __tablename__ = 'job_positions'

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(
        db.Integer,
        db.ForeignKey('company_profiles.id'),
        nullable=False
    )

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)

    salary = db.Column(db.Integer)
    benefits = db.Column(db.Text)
    skills_required = db.Column(db.Text)
    experience_required = db.Column(db.String(50))
    location = db.Column(db.String(100))

    min_cgpa = db.Column(db.Float)
    eligible_branches = db.Column(db.String(200))
    eligible_year = db.Column(db.Integer)

    application_deadline = db.Column(db.DateTime, nullable=False)

    status = db.Column(
        db.Enum('Pending', 'Approved', 'Closed', name='job_status'),
        default='Pending'
    )

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    applications = db.relationship(
        'Application',
        backref='job',
        lazy=True,
        cascade='all, delete-orphan'
    )

    def __str__(self):
        return self.title


class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey('student_profiles.id'),
        nullable=False
    )

    job_id = db.Column(
        db.Integer,
        db.ForeignKey('job_positions.id'),
        nullable=False
    )

    application_date = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    status = db.Column(
        db.Enum(
            'Applied',
            'Shortlisted',
            'Interview',
            'Offer',
            'Selected',
            'Rejected',
            'Placed',
            name='application_status'
        ),
        default='Applied'
    )

    notes = db.Column(db.Text)

    placement = db.relationship(
        'Placement',
        backref='application',
        uselist=False,
        cascade='all, delete-orphan'
    )

    interview = db.relationship(
        'Interview',
        backref='application',
        uselist=False,
        cascade='all, delete-orphan'
    )

    __table_args__ = (
        db.UniqueConstraint('student_id', 'job_id', name='unique_student_job'),
    )

    def __str__(self):
        return str(self.id)


class Placement(db.Model):
    __tablename__ = 'placements'

    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey('applications.id'),
        nullable=False,
        unique=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey('student_profiles.id'),
        nullable=False
    )

    company_id = db.Column(
        db.Integer,
        db.ForeignKey('company_profiles.id'),
        nullable=False
    )

    position = db.Column(db.String(200))
    salary = db.Column(db.Integer)
    joining_date = db.Column(db.DateTime)

    placed_date = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    remarks = db.Column(db.Text)
    offer_letter = db.Column(db.String(200))

    def __str__(self):
        return str(self.id)


class Interview(db.Model):
    __tablename__ = 'interviews'

    id = db.Column(db.Integer, primary_key=True)

    application_id = db.Column(
        db.Integer,
        db.ForeignKey('applications.id'),
        nullable=False,
        unique=True
    )

    interview_date = db.Column(db.DateTime, nullable=False)
    interview_link = db.Column(db.String(500))
    venue = db.Column(db.String(300))

    notes = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    def __str__(self):
        return str(self.id)
