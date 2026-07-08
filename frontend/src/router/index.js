import { createRouter, createWebHistory } from "vue-router";

import Login from "../views/auth/Login.vue";
import StudentRegister from "../views/auth/StudentRegister.vue";
import CompanyRegister from "../views/auth/CompanyRegister.vue";
import StudentDashboard from "../views/student/Dashboard.vue";
import StudentJobs from "../views/student/Jobs.vue";
import StudentApplications from "../views/student/Applications.vue";
import StudentProfile from "../views/student/Profile.vue";

import CompanyDashboard from "../views/company/Dashboard.vue";
import CompanyJobs from "../views/company/Jobs.vue";
import CompanyApplicants from "../views/company/Applicants.vue";
import CompanyInterviews from "../views/company/Interviews.vue";

import AdminDashboard from "../views/admin/Dashboard.vue";
import AdminStudents from "../views/admin/Students.vue";
import AdminCompanies from "../views/admin/Companies.vue";
import AdminJobs from "../views/admin/Jobs.vue";
import AdminApplications from "../views/admin/Applications.vue";
import Home from "../views/Home.vue"

const router = createRouter({

    history: createWebHistory(),

    routes:[

        {
            path:"/",
            component:Home
        },

        {
            path:"/login",
            name: "Login",
            component:Login
        },

        {
            path:"/register/student",
            name: "RegisterStudent",
            component:StudentRegister
        },

        {
            path:"/register/company",
            name: "RegisterCompany",
            component:CompanyRegister
        }

        ,

        {
            path:"/student/dashboard",
            name: "StudentDashboard",
            component:StudentDashboard
        },

        {
            path:"/student/jobs",
            name: "StudentJobs",
            component:StudentJobs
        },

        {
            path:"/student/applications",
            name: "StudentApplications",
            component:StudentApplications
        },

        {
            path:"/student/profile",
            name: "StudentProfile",
            component:StudentProfile
        },

        {
            path:"/company/dashboard",
            name: "CompanyDashboard",
            component:CompanyDashboard
        },

        {
            path:"/company/jobs",
            name: "CompanyJobs",
            component:CompanyJobs
        },

        {
            path:"/company/applicants",
            name: "CompanyApplicants",
            component:CompanyApplicants
        },

        {
            path:"/company/interviews",
            name: "CompanyInterviews",
            component:CompanyInterviews
        },

        {
            path:"/admin/dashboard",
            name: "AdminDashboard",
            component:AdminDashboard
        },

        {
            path:"/admin/students",
            name: "AdminStudents",
            component:AdminStudents
        },

        {
            path:"/admin/companies",
            name: "AdminCompanies",
            component:AdminCompanies
        },

        {
            path:"/admin/jobs",
            name: "AdminJobs",
            component:AdminJobs
        },

        {
            path:"/admin/applications",
            name: "AdminApplications",
            component:AdminApplications
        }

    ]

})

export default router