"""Idempotently add a realistic demo dataset for local development."""
from datetime import datetime, timedelta, timezone

from app import create_app
from models import (
    Application,
    CompanyProfile,
    Interview,
    JobPosition,
    Placement,
    StudentProfile,
    User,
    db,
)


def user(email, role, password="demo123"):
    record = User.query.filter_by(email=email).first()
    if not record:
        record = User(email=email, role=role)
        record.set_password(password)
        db.session.add(record)
        db.session.flush()
    return record


def company_profile(name, email, industry, location, hr_contact, website):
    account = user(email, "company")
    profile = CompanyProfile.query.filter_by(user_id=account.id).first()
    if not profile:
        profile = CompanyProfile(user_id=account.id)
        db.session.add(profile)

    profile.name = name
    profile.industry = industry
    profile.location = location
    profile.hr_contact = hr_contact
    profile.website = website
    profile.is_approved = True
    profile.approved_by_admin = True
    profile.is_blacklisted = False
    return profile


def student_profile(name, email, branch, cgpa, year, skills, contact, degree, institution, passout_year, experience, resume_filename):
    account = user(email, "student")
    profile = StudentProfile.query.filter_by(user_id=account.id).first()
    if not profile:
        profile = StudentProfile(user_id=account.id)
        db.session.add(profile)

    profile.name = name
    profile.branch = branch
    profile.cgpa = cgpa
    profile.year = year
    profile.skills = skills
    profile.contact = contact
    profile.degree = degree
    profile.institution = institution
    profile.passout_year = passout_year
    profile.experience = experience
    profile.resume_filename = resume_filename
    return profile


def job_position(company, title, description, salary, skills_required, location, eligible_branches, min_cgpa, experience_required, deadline_days, status="Approved"):
    job = JobPosition.query.filter_by(company_id=company.id, title=title).first()
    if not job:
        job = JobPosition(company_id=company.id, title=title)
        db.session.add(job)

    job.description = description
    job.salary = salary
    job.skills_required = skills_required
    job.location = location
    job.eligible_branches = eligible_branches
    job.min_cgpa = min_cgpa
    job.experience_required = experience_required
    job.application_deadline = datetime.now(timezone.utc) + timedelta(days=deadline_days)
    job.status = status
    return job


def application(student, job, status, notes, days_ago=8):
    record = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
    if not record:
        record = Application(student_id=student.id, job_id=job.id)
        db.session.add(record)

    record.status = status
    record.notes = notes
    record.application_date = datetime.now(timezone.utc) - timedelta(days=days_ago)
    return record


def interview(application_record, days_ahead, interview_link, venue, notes):
    record = Interview.query.filter_by(application_id=application_record.id).first()
    if not record:
        record = Interview(application_id=application_record.id)
        db.session.add(record)

    record.interview_date = datetime.now(timezone.utc) + timedelta(days=days_ahead)
    record.interview_link = interview_link
    record.venue = venue
    record.notes = notes
    return record


def placement(application_record, student, company, position, salary, joining_days, remarks, offer_letter):
    record = Placement.query.filter_by(application_id=application_record.id).first()
    if not record:
        record = Placement(application_id=application_record.id)
        db.session.add(record)

    record.student_id = student.id
    record.company_id = company.id
    record.position = position
    record.salary = salary
    record.joining_date = datetime.now(timezone.utc) + timedelta(days=joining_days)
    record.remarks = remarks
    record.offer_letter = offer_letter
    return record


def seed():
    company_rows = [
        ("northstar", "Northstar Analytics", "talent@northstar.demo", "Analytics", "Bengaluru", "Priya Nair", "https://northstar.example"),
        ("vertex", "Vertex Systems", "careers@vertex.demo", "Software", "Hyderabad", "Arjun Rao", "https://vertex.example"),
        ("cloudnova", "CloudNova Labs", "hr@cloudnova.demo", "Cloud Infrastructure", "Pune", "Meera Kulkarni", "https://cloudnova.example"),
        ("finedge", "FinEdge Capital", "campus@finedge.demo", "FinTech", "Mumbai", "Kabir Shah", "https://finedge.example"),
        ("medisync", "MediSync Health", "jobs@medisync.demo", "HealthTech", "Chennai", "Nisha Menon", "https://medisync.example"),
        ("greenbyte", "GreenByte Mobility", "placements@greenbyte.demo", "EV and Mobility", "Bengaluru", "Rahul Iyer", "https://greenbyte.example"),
        ("retailiq", "RetailIQ Commerce", "talent@retailiq.demo", "E-Commerce", "Gurugram", "Sana Khan", "https://retailiq.example"),
        ("securepath", "SecurePath Cyber", "careers@securepath.demo", "Cybersecurity", "Noida", "Vikram Sethi", "https://securepath.example"),
    ]
    company_rows.extend([
        ("aerolink", "AeroLink Systems", "campus@aerolink.demo", "Aerospace", "Bengaluru", "Aditya Bhat", "https://aerolink.example"),
        ("byteforge", "ByteForge Studio", "jobs@byteforge.demo", "Product Engineering", "Ahmedabad", "Neha Trivedi", "https://byteforge.example"),
        ("quantumgrid", "QuantumGrid Energy", "talent@quantumgrid.demo", "Energy Analytics", "Pune", "Ritesh Patil", "https://quantumgrid.example"),
        ("skillbridge", "SkillBridge EdTech", "hr@skillbridge.demo", "EdTech", "Mumbai", "Pooja Desai", "https://skillbridge.example"),
        ("nexapay", "NexaPay Digital", "careers@nexapay.demo", "Payments", "Bengaluru", "Farhan Ali", "https://nexapay.example"),
        ("urbanloop", "UrbanLoop Logistics", "placements@urbanloop.demo", "Logistics", "Delhi", "Shruti Jain", "https://urbanloop.example"),
        ("datamint", "DataMint Research", "campus@datamint.demo", "Market Research", "Kolkata", "Anirban Sen", "https://datamint.example"),
        ("codecraft", "CodeCraft Labs", "jobs@codecraft.demo", "Software Services", "Indore", "Mitali Sharma", "https://codecraft.example"),
        ("terrafin", "TerraFin ESG", "talent@terrafin.demo", "Sustainability Tech", "Chennai", "Rohit Menon", "https://terrafin.example"),
        ("bluepeak", "BluePeak Networks", "hr@bluepeak.demo", "Networking", "Noida", "Asha Bansal", "https://bluepeak.example"),
        ("smartpulse", "SmartPulse IoT", "careers@smartpulse.demo", "IoT", "Coimbatore", "Karthik Raman", "https://smartpulse.example"),
        ("insightworks", "InsightWorks BI", "placements@insightworks.demo", "Business Intelligence", "Jaipur", "Mansi Kapoor", "https://insightworks.example"),
        ("apporbit", "AppOrbit Mobile", "campus@apporbit.demo", "Mobile Apps", "Kochi", "Joel Mathew", "https://apporbit.example"),
        ("legalbot", "LegalBot AI", "jobs@legalbot.demo", "LegalTech", "Hyderabad", "Tanvi Rao", "https://legalbot.example"),
        ("farmwise", "FarmWise AgriTech", "talent@farmwise.demo", "AgriTech", "Nagpur", "Nikhil Kale", "https://farmwise.example"),
        ("brightpath", "BrightPath Consulting", "hr@brightpath.demo", "Consulting", "Mumbai", "Lavanya Shetty", "https://brightpath.example"),
        ("zenops", "ZenOps Automation", "careers@zenops.demo", "DevOps Automation", "Bengaluru", "Harsh Vardhan", "https://zenops.example"),
    ])

    companies = {
        key: company_profile(
            name=name,
            email=email,
            industry=industry,
            location=location,
            hr_contact=hr_contact,
            website=website,
        )
        for key, name, email, industry, location, hr_contact, website in company_rows
    }
    db.session.flush()

    student_rows = [
        ("aarav", "Aarav Sharma", "aarav@student.demo", "Computer Science", 8.6, 4, "Python, SQL, Excel, Communication, DSA", "+91 98765 43210", "Built a placement analytics dashboard and a resume parser project."),
        ("diya", "Diya Patel", "diya@student.demo", "Information Technology", 8.8, 4, "JavaScript, Vue, React, Node.js, SQL, APIs", "+91 98765 43211", "Built a full-stack internship tracker and a portfolio site."),
        ("rohan", "Rohan Mehta", "rohan@student.demo", "Computer Science", 7.9, 3, "Python, Java, Git, DSA, Communication", "+91 98765 43212", "Completed a machine learning mini-project and team coding challenge."),
        ("anaya", "Anaya Rao", "anaya@student.demo", "Electronics", 8.2, 4, "Python, C, Embedded Systems, SQL, Problem Solving", "+91 98765 43213", "Worked on IoT sensor data collection and reporting."),
        ("isha", "Isha Verma", "isha@student.demo", "Information Technology", 9.1, 4, "Vue, JavaScript, UI Design, REST APIs, Testing", "+91 98765 43214", "Created a responsive student services portal with API integration."),
        ("kabir", "Kabir Singh", "kabir@student.demo", "Computer Science", 8.3, 4, "Java, Spring Boot, SQL, Docker, Git", "+91 98765 43215", "Built a job portal backend with authentication and reporting."),
        ("meera", "Meera Joshi", "meera@student.demo", "Data Science", 8.9, 4, "Python, Pandas, Machine Learning, SQL, Tableau", "+91 98765 43216", "Analysed placement trends and built predictive dashboards."),
        ("vivaan", "Vivaan Kapoor", "vivaan@student.demo", "Electronics", 7.6, 3, "C, Python, IoT, Embedded Systems, Linux", "+91 98765 43217", "Built a smart attendance prototype using RFID and dashboards."),
        ("naina", "Naina Gupta", "naina@student.demo", "Computer Science", 8.1, 4, "Python, Django, APIs, PostgreSQL, Communication", "+91 98765 43218", "Developed a campus complaint management application."),
        ("arjun", "Arjun Reddy", "arjun@student.demo", "Mechanical", 7.4, 4, "Python, Excel, Operations, Analytics, CAD", "+91 98765 43219", "Worked on production analytics and process improvement projects."),
        ("saanvi", "Saanvi Kulkarni", "saanvi@student.demo", "Information Technology", 8.7, 3, "React, Node.js, MongoDB, Git, Problem Solving", "+91 98765 43220", "Created a collaborative study planner web app."),
        ("dev", "Dev Malhotra", "dev@student.demo", "Cybersecurity", 8.4, 4, "Networking, Linux, Python, Security, SIEM", "+91 98765 43221", "Completed vulnerability assessment labs and a secure login project."),
        ("riya", "Riya Banerjee", "riya@student.demo", "Data Science", 8.0, 4, "Python, Statistics, Power BI, SQL, Communication", "+91 98765 43222", "Built a sales forecasting model and BI dashboard."),
        ("om", "Om Prakash", "om@student.demo", "Computer Science", 7.8, 3, "JavaScript, Vue, Firebase, Git, APIs", "+91 98765 43223", "Built a club management app with real-time updates."),
        ("tara", "Tara D'Souza", "tara@student.demo", "Electronics", 8.5, 4, "Python, C++, Robotics, SQL, Problem Solving", "+91 98765 43224", "Created a line-following robot and sensor analytics dashboard."),
        ("yash", "Yash Agarwal", "yash@student.demo", "Information Technology", 7.7, 4, "Java, SQL, Selenium, Manual Testing, APIs", "+91 98765 43225", "Worked on QA automation for a mock e-commerce platform."),
    ]
    student_rows.extend([
        ("aditi", "Aditi Nambiar", "aditi@student.demo", "Computer Science", 8.9, 4, "Python, FastAPI, PostgreSQL, Docker, Git", "+91 98765 43226", "Built a backend for a campus helpdesk with role based access."),
        ("manav", "Manav Bansal", "manav@student.demo", "Information Technology", 7.9, 3, "Vue, JavaScript, Tailwind, REST APIs, Testing", "+91 98765 43227", "Created an event booking frontend with API integration."),
        ("prisha", "Prisha Sinha", "prisha@student.demo", "Data Science", 9.0, 4, "Python, NLP, Pandas, SQL, Power BI", "+91 98765 43228", "Built a sentiment analysis dashboard for student feedback."),
        ("reyansh", "Reyansh Pillai", "reyansh@student.demo", "Cybersecurity", 8.2, 4, "Linux, Networking, Python, Burp Suite, SIEM", "+91 98765 43229", "Completed web security labs and wrote incident reports."),
        ("kavya", "Kavya Murthy", "kavya@student.demo", "Electronics", 7.8, 4, "C, Python, MATLAB, IoT, Sensors", "+91 98765 43230", "Worked on remote monitoring for temperature and humidity sensors."),
        ("neel", "Neel Chatterjee", "neel@student.demo", "Computer Science", 8.4, 3, "Java, DSA, SQL, Git, Spring Boot", "+91 98765 43231", "Built a library management backend and practiced coding contests."),
        ("mahi", "Mahi Shah", "mahi@student.demo", "Information Technology", 8.6, 4, "React, Node.js, MongoDB, APIs, Communication", "+91 98765 43232", "Built a hostel maintenance app with notification workflows."),
        ("atharv", "Atharv Jain", "atharv@student.demo", "Mechanical", 7.5, 4, "Excel, Python, Operations, CAD, Analytics", "+91 98765 43233", "Analysed machine downtime and suggested process improvements."),
        ("zoya", "Zoya Khan", "zoya@student.demo", "Data Science", 8.3, 3, "Python, Statistics, SQL, Tableau, Storytelling", "+91 98765 43234", "Created dashboards for attendance and academic performance."),
        ("harini", "Harini Subramanian", "harini@student.demo", "Computer Science", 8.7, 4, "JavaScript, Vue, Python, APIs, Git", "+91 98765 43235", "Built a placement preparation tracker with progress analytics."),
        ("parth", "Parth Saxena", "parth@student.demo", "Cybersecurity", 7.9, 4, "Networking, Linux, Python, Cloud Security, Bash", "+91 98765 43236", "Documented cloud security checks and secure deployment basics."),
        ("lavanya", "Lavanya Mishra", "lavanya@student.demo", "Information Technology", 8.1, 3, "Java, SQL, Selenium, APIs, Documentation", "+91 98765 43237", "Created automated tests for registration and login flows."),
        ("rishi", "Rishi Narang", "rishi@student.demo", "Computer Science", 7.6, 4, "Python, Flask, SQLite, HTML, CSS", "+91 98765 43238", "Built a local inventory management tool for a small business."),
        ("samaira", "Samaira Bose", "samaira@student.demo", "Data Science", 8.5, 4, "Machine Learning, Python, SQL, Excel, Communication", "+91 98765 43239", "Developed a student dropout risk analysis model."),
    ])

    students = {
        key: student_profile(
            name=name,
            email=email,
            branch=branch,
            cgpa=cgpa,
            year=year,
            skills=skills,
            contact=contact,
            degree="B.Tech" if branch != "Mechanical" else "B.E.",
            institution="PPA Institute of Technology",
            passout_year=2026 if year == 4 else 2027,
            experience=experience,
            resume_filename=f"{key}_resume.pdf",
        )
        for key, name, email, branch, cgpa, year, skills, contact, experience in student_rows
    }
    db.session.flush()

    job_rows = [
        ("data_analyst", "northstar", "Junior Data Analyst", "Analyse placement and business data, build reports, and support decision making.", 650000, "SQL, Python, Excel, Communication", "Bengaluru", "Computer Science, Information Technology, Electronics, Data Science", 7.5, "0-1 years", 24),
        ("software_engineer", "vertex", "Software Engineer", "Build reliable web services, ship features, and collaborate with product teams.", 850000, "Python, JavaScript, APIs, Git", "Hyderabad", "Computer Science, Information Technology", 8.0, "0-2 years", 18),
        ("full_stack_intern", "vertex", "Full Stack Intern", "Support frontend and backend work on internal hiring tools.", 420000, "Vue, Node.js, SQL, APIs", "Remote", "Computer Science, Information Technology", 7.0, "Fresher", 12),
        ("operations_analyst", "northstar", "Business Analyst Intern", "Support reporting, process analysis, and stakeholder updates.", 360000, "Excel, SQL, Communication", "Remote", "Computer Science, Information Technology, Electronics, Mechanical, Data Science", 7.0, "Fresher", 30),
        ("cloud_engineer", "cloudnova", "Cloud Support Engineer", "Monitor cloud workloads, troubleshoot incidents, and automate support tasks.", 760000, "Linux, Python, Docker, Networking", "Pune", "Computer Science, Information Technology, Cybersecurity", 7.6, "0-1 years", 21),
        ("fintech_backend", "finedge", "Backend Developer Trainee", "Build secure payment and ledger services with strong code review practices.", 900000, "Java, Spring Boot, SQL, APIs", "Mumbai", "Computer Science, Information Technology", 8.0, "0-1 years", 16),
        ("health_data", "medisync", "Healthcare Data Associate", "Prepare clean datasets and dashboards for hospital operations teams.", 600000, "Python, SQL, Power BI, Communication", "Chennai", "Data Science, Computer Science, Information Technology", 7.3, "Fresher", 27),
        ("ev_iot", "greenbyte", "IoT Systems Intern", "Work on device telemetry, dashboards, and field data quality.", 390000, "Python, C, IoT, Embedded Systems", "Bengaluru", "Electronics, Computer Science", 7.2, "Fresher", 20),
        ("qa_engineer", "retailiq", "QA Automation Engineer", "Create reliable test plans and automation for commerce workflows.", 580000, "Selenium, Java, APIs, SQL", "Gurugram", "Computer Science, Information Technology", 7.0, "0-1 years", 32),
        ("security_analyst", "securepath", "Security Analyst Trainee", "Assist with monitoring, vulnerability reports, and incident response drills.", 700000, "Networking, Linux, Python, Security", "Noida", "Cybersecurity, Computer Science, Information Technology", 7.5, "Fresher", 22),
        ("product_engineer", "retailiq", "Frontend Product Engineer", "Ship polished customer-facing features and improve dashboard usability.", 820000, "Vue, React, JavaScript, APIs", "Gurugram", "Computer Science, Information Technology", 7.8, "0-1 years", 19),
        ("ml_intern", "northstar", "Machine Learning Intern", "Prototype scoring models and explain insights to placement teams.", 480000, "Python, Machine Learning, Pandas, SQL", "Bengaluru", "Data Science, Computer Science, Information Technology", 8.0, "Fresher", 26),
    ]
    job_rows.extend([
        ("aerospace_data", "aerolink", "Aerospace Data Trainee", "Clean flight telemetry data and prepare reliability dashboards.", 620000, "Python, SQL, Excel, Statistics", "Bengaluru", "Computer Science, Data Science, Electronics", 7.5, "Fresher", 25),
        ("ui_engineer", "byteforge", "UI Engineer Intern", "Build polished Vue interfaces for SaaS products.", 440000, "Vue, JavaScript, CSS, APIs", "Ahmedabad", "Computer Science, Information Technology", 7.0, "Fresher", 15),
        ("energy_analyst", "quantumgrid", "Energy Analytics Associate", "Analyse power usage trends and automate reports.", 610000, "Python, Excel, SQL, Power BI", "Pune", "Data Science, Computer Science, Mechanical", 7.2, "Fresher", 29),
        ("edtech_backend", "skillbridge", "EdTech Backend Intern", "Support learning APIs and assessment workflows.", 430000, "Python, Flask, SQL, APIs", "Mumbai", "Computer Science, Information Technology", 7.0, "Fresher", 18),
        ("payments_qa", "nexapay", "Payments QA Analyst", "Test payment flows, reconciliation reports, and API edge cases.", 590000, "SQL, APIs, Selenium, Documentation", "Bengaluru", "Computer Science, Information Technology", 7.4, "0-1 years", 21),
        ("logistics_ops", "urbanloop", "Logistics Operations Analyst", "Improve route reporting and delivery performance dashboards.", 520000, "Excel, SQL, Communication, Analytics", "Delhi", "Mechanical, Computer Science, Information Technology, Data Science", 7.0, "Fresher", 30),
        ("research_associate", "datamint", "Research Data Associate", "Prepare market datasets and insight summaries for clients.", 540000, "Excel, Python, SQL, Storytelling", "Kolkata", "Data Science, Computer Science, Information Technology", 7.0, "Fresher", 24),
        ("service_developer", "codecraft", "Associate Software Developer", "Build client features across backend services and dashboards.", 680000, "JavaScript, Python, SQL, Git", "Indore", "Computer Science, Information Technology", 7.6, "0-1 years", 20),
        ("esg_reporting", "terrafin", "ESG Reporting Analyst", "Create sustainability reports and automate data checks.", 570000, "Excel, SQL, Python, Communication", "Chennai", "Data Science, Mechanical, Information Technology", 7.1, "Fresher", 31),
        ("network_trainee", "bluepeak", "Network Operations Trainee", "Monitor network alerts and prepare incident summaries.", 560000, "Networking, Linux, Python, Troubleshooting", "Noida", "Cybersecurity, Electronics, Computer Science", 7.3, "Fresher", 26),
        ("iot_firmware", "smartpulse", "IoT Firmware Intern", "Support firmware testing and sensor integration workflows.", 400000, "C, Python, IoT, Embedded Systems", "Coimbatore", "Electronics, Computer Science", 7.0, "Fresher", 17),
        ("bi_consultant", "insightworks", "BI Consultant Trainee", "Build dashboards and translate business questions into metrics.", 640000, "Power BI, SQL, Excel, Communication", "Jaipur", "Data Science, Computer Science, Information Technology", 7.5, "Fresher", 23),
        ("mobile_intern", "apporbit", "Mobile App Intern", "Assist with app screens, API integration, and release testing.", 410000, "JavaScript, React Native, APIs, Git", "Kochi", "Computer Science, Information Technology", 7.0, "Fresher", 19),
        ("legal_ai_analyst", "legalbot", "AI Data Analyst", "Label legal datasets and evaluate AI answer quality.", 630000, "Python, NLP, SQL, Documentation", "Hyderabad", "Data Science, Computer Science, Information Technology", 7.8, "Fresher", 27),
        ("agri_data", "farmwise", "Agri Data Coordinator", "Analyse field data and prepare crop intelligence reports.", 500000, "Excel, Python, SQL, Communication", "Nagpur", "Data Science, Electronics, Computer Science", 7.0, "Fresher", 33),
        ("consulting_analyst", "brightpath", "Consulting Analyst Intern", "Prepare client research, process maps, and presentation-ready insights.", 450000, "Excel, Communication, Analytics, PowerPoint", "Mumbai", "Computer Science, Information Technology, Mechanical, Data Science", 7.2, "Fresher", 22),
        ("devops_trainee", "zenops", "DevOps Trainee", "Automate deployments, monitor services, and document runbooks.", 720000, "Linux, Docker, Python, Cloud", "Bengaluru", "Computer Science, Information Technology, Cybersecurity", 7.6, "Fresher", 16),
    ])

    jobs = {
        key: job_position(
            company=companies[company_key],
            title=title,
            description=description,
            salary=salary,
            skills_required=skills_required,
            location=location,
            eligible_branches=eligible_branches,
            min_cgpa=min_cgpa,
            experience_required=experience_required,
            deadline_days=deadline_days,
        )
        for key, company_key, title, description, salary, skills_required, location, eligible_branches, min_cgpa, experience_required, deadline_days in job_rows
    }
    db.session.flush()

    application_rows = [
        ("aarav_data", "aarav", "data_analyst", "Placed", "Excellent fit for analytics and reporting work.", 16),
        ("diya_full_stack", "diya", "full_stack_intern", "Interview", "Strong frontend and API portfolio.", 9),
        ("rohan_data", "rohan", "data_analyst", "Shortlisted", "Good SQL and Python foundation.", 11),
        ("anaya_ops", "anaya", "operations_analyst", "Applied", "Needs a little more spreadsheet and reporting practice.", 5),
        ("diya_engineer", "diya", "software_engineer", "Selected", "Strong fit for product engineering and UI work.", 14),
        ("rohan_engineer", "rohan", "software_engineer", "Rejected", "Good effort, but needs stronger JavaScript and API depth.", 12),
        ("isha_product", "isha", "product_engineer", "Interview", "Excellent frontend craft and communication.", 7),
        ("kabir_backend", "kabir", "fintech_backend", "Shortlisted", "Strong backend fundamentals and database work.", 10),
        ("meera_ml", "meera", "ml_intern", "Selected", "Excellent modelling and dashboard portfolio.", 13),
        ("vivaan_iot", "vivaan", "ev_iot", "Interview", "Relevant embedded systems mini-projects.", 8),
        ("naina_cloud", "naina", "cloud_engineer", "Applied", "Good Python and API experience.", 4),
        ("arjun_ops", "arjun", "operations_analyst", "Shortlisted", "Good operations mindset and spreadsheet skills.", 6),
        ("saanvi_fullstack", "saanvi", "full_stack_intern", "Applied", "Solid MERN project background.", 3),
        ("dev_security", "dev", "security_analyst", "Interview", "Strong security lab experience.", 9),
        ("riya_health", "riya", "health_data", "Placed", "Strong data visualization profile.", 18),
        ("om_product", "om", "product_engineer", "Rejected", "Needs stronger component architecture depth.", 15),
        ("tara_iot", "tara", "ev_iot", "Shortlisted", "Strong robotics and sensor background.", 7),
        ("yash_qa", "yash", "qa_engineer", "Offer", "Good testing fundamentals and automation exposure.", 12),
        ("aarav_cloud", "aarav", "cloud_engineer", "Applied", "Interested in cloud operations.", 2),
        ("diya_product", "diya", "product_engineer", "Shortlisted", "Polished UI and API experience.", 6),
        ("kabir_engineer", "kabir", "software_engineer", "Interview", "Good Java and service design experience.", 8),
        ("meera_health", "meera", "health_data", "Shortlisted", "Strong analytics fit.", 5),
        ("dev_cloud", "dev", "cloud_engineer", "Shortlisted", "Linux and networking experience is relevant.", 4),
        ("riya_data", "riya", "data_analyst", "Interview", "Good SQL and BI skills.", 9),
    ]
    application_rows.extend([
        ("aditi_devops", "aditi", "devops_trainee", "Shortlisted", "Strong backend and Docker fundamentals.", 6),
        ("manav_ui", "manav", "ui_engineer", "Applied", "Good Vue practice and frontend interest.", 3),
        ("prisha_legal_ai", "prisha", "legal_ai_analyst", "Interview", "Strong NLP and data cleaning project.", 8),
        ("reyansh_network", "reyansh", "network_trainee", "Shortlisted", "Relevant Linux and network security skills.", 5),
        ("kavya_firmware", "kavya", "iot_firmware", "Interview", "Good embedded systems and sensor exposure.", 7),
        ("neel_service", "neel", "service_developer", "Applied", "Strong Java and DSA base.", 2),
        ("mahi_mobile", "mahi", "mobile_intern", "Shortlisted", "Good app workflow and API experience.", 4),
        ("atharv_logistics", "atharv", "logistics_ops", "Interview", "Operations project fits logistics role.", 10),
        ("zoya_bi", "zoya", "bi_consultant", "Applied", "Solid dashboarding and storytelling skills.", 3),
        ("harini_ui", "harini", "ui_engineer", "Selected", "Excellent frontend project and communication.", 13),
        ("parth_devops", "parth", "devops_trainee", "Interview", "Cloud security and Linux experience is useful.", 9),
        ("lavanya_payments", "lavanya", "payments_qa", "Shortlisted", "Good QA and documentation practice.", 6),
        ("rishi_edtech", "rishi", "edtech_backend", "Applied", "Flask project maps well to backend internship.", 4),
        ("samaira_energy", "samaira", "energy_analyst", "Shortlisted", "Strong ML and reporting foundation.", 7),
        ("aarav_aerospace", "aarav", "aerospace_data", "Applied", "Analytics background fits telemetry reporting.", 2),
        ("isha_mobile", "isha", "mobile_intern", "Interview", "Good UI experience and API confidence.", 8),
        ("kabir_nexapay", "kabir", "payments_qa", "Applied", "Backend testing exposure is relevant.", 3),
        ("meera_research", "meera", "research_associate", "Selected", "Excellent data preparation and insight work.", 15),
        ("vivaan_smartpulse", "vivaan", "iot_firmware", "Shortlisted", "Hands-on IoT project experience.", 5),
        ("naina_codecraft", "naina", "service_developer", "Interview", "Django and API background is useful.", 6),
        ("arjun_consulting", "arjun", "consulting_analyst", "Applied", "Operations analytics experience fits consulting.", 2),
        ("saanvi_apporbit", "saanvi", "mobile_intern", "Shortlisted", "Full-stack project maps well to app role.", 5),
        ("dev_bluepeak", "dev", "network_trainee", "Selected", "Strong security and networking fundamentals.", 14),
        ("riya_insightworks", "riya", "bi_consultant", "Interview", "Power BI and SQL experience looks strong.", 6),
        ("tara_aerolink", "tara", "aerospace_data", "Shortlisted", "Robotics and sensor background is useful.", 8),
        ("yash_nexapay", "yash", "payments_qa", "Interview", "Testing skills fit payment QA role.", 9),
        ("aditi_codecraft", "aditi", "service_developer", "Interview", "Backend project and Git workflow are strong.", 8),
        ("prisha_datamint", "prisha", "research_associate", "Placed", "Strong analysis and storytelling profile.", 18),
        ("samaira_legalbot", "samaira", "legal_ai_analyst", "Applied", "ML project experience fits AI evaluation.", 3),
        ("zoya_terrafin", "zoya", "esg_reporting", "Shortlisted", "Dashboarding and reporting skills are relevant.", 5),
    ])

    applications = {
        key: application(
            students[student_key],
            jobs[job_key],
            status,
            notes,
            days_ago=days_ago,
        )
        for key, student_key, job_key, status, notes, days_ago in application_rows
    }
    db.session.flush()

    interview_rows = [
        ("diya_full_stack", 3, "https://meet.example.com/vertex-fullstack", "Virtual interview", "Round 1 with engineering panel."),
        ("rohan_data", 5, "", "Northstar Analytics, Bengaluru", "Aptitude and SQL screening round."),
        ("isha_product", 2, "https://meet.example.com/retailiq-product", "Virtual interview", "UI case study discussion."),
        ("vivaan_iot", 4, "", "GreenByte Mobility, Bengaluru", "Hardware and telemetry discussion."),
        ("dev_security", 6, "https://meet.example.com/securepath-trainee", "Virtual interview", "Security fundamentals and Linux round."),
        ("kabir_engineer", 7, "https://meet.example.com/vertex-engineering", "Virtual interview", "Backend design round."),
        ("riya_data", 3, "", "Northstar Analytics, Bengaluru", "Dashboard and SQL screening."),
    ]
    interview_rows.extend([
        ("prisha_legal_ai", 4, "https://meet.example.com/legalbot-ai", "Virtual interview", "NLP data quality discussion."),
        ("kavya_firmware", 6, "", "SmartPulse IoT, Coimbatore", "Firmware and sensor debugging round."),
        ("atharv_logistics", 5, "https://meet.example.com/urbanloop-ops", "Virtual interview", "Operations case discussion."),
        ("parth_devops", 7, "https://meet.example.com/zenops-devops", "Virtual interview", "Linux and deployment basics."),
        ("isha_mobile", 2, "https://meet.example.com/apporbit-mobile", "Virtual interview", "App UI review and API discussion."),
        ("naina_codecraft", 6, "", "CodeCraft Labs, Indore", "Backend and SQL technical round."),
        ("riya_insightworks", 3, "https://meet.example.com/insightworks-bi", "Virtual interview", "BI dashboard walkthrough."),
        ("yash_nexapay", 4, "https://meet.example.com/nexapay-qa", "Virtual interview", "QA scenarios for payment flows."),
        ("aditi_codecraft", 8, "", "CodeCraft Labs, Indore", "Service development and Git workflow round."),
    ])
    for app_key, days_ahead, link, venue, notes in interview_rows:
        interview(applications[app_key], days_ahead=days_ahead, interview_link=link, venue=venue, notes=notes)

    placement_rows = [
        ("aarav_data", "aarav", "northstar", "data_analyst", 42, "Placed through campus drive.", "offers/aarav_northstar_offer.pdf"),
        ("diya_engineer", "diya", "vertex", "software_engineer", 35, "Final selection complete.", "offers/diya_vertex_offer.pdf"),
        ("meera_ml", "meera", "northstar", "ml_intern", 28, "Selected for analytics research internship.", "offers/meera_northstar_offer.pdf"),
        ("riya_health", "riya", "medisync", "health_data", 38, "Placed in healthcare analytics team.", "offers/riya_medisync_offer.pdf"),
    ]
    placement_rows.extend([
        ("harini_ui", "harini", "byteforge", "ui_engineer", 31, "Selected for frontend internship.", "offers/harini_byteforge_offer.pdf"),
        ("meera_research", "meera", "datamint", "research_associate", 34, "Selected for research data team.", "offers/meera_datamint_offer.pdf"),
        ("dev_bluepeak", "dev", "bluepeak", "network_trainee", 40, "Selected for network operations team.", "offers/dev_bluepeak_offer.pdf"),
        ("prisha_datamint", "prisha", "datamint", "research_associate", 37, "Placed after strong analytics interview.", "offers/prisha_datamint_offer.pdf"),
    ])
    for app_key, student_key, company_key, job_key, joining_days, remarks, offer_letter in placement_rows:
        placement(
            applications[app_key],
            students[student_key],
            companies[company_key],
            position=jobs[job_key].title,
            salary=jobs[job_key].salary,
            joining_days=joining_days,
            remarks=remarks,
            offer_letter=offer_letter,
        )

    db.session.commit()
    return (
        f"Demo data ready: {len(companies)} companies, {len(students)} students, "
        f"{len(jobs)} jobs, {len(applications)} applications."
    )


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        print(seed())
