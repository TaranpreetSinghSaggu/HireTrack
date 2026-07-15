import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "@/stores/auth";
import AuthLayout from "@/layouts/AuthLayout.vue";
import DashboardLayout from "@/layouts/DashboardLayout.vue";

const routes = [
  {
    path: "/",
    redirect: "/dashboard",
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: () => import("@/views/Dashboard.vue"),
  },
  {
    path: "/",
    component: AuthLayout,
    children: [
      {
        path: "login",
        name: "login",
        component: () => import("@/views/auth/Login.vue"),
      },
      {
        path: "register/student",
        component: () => import("@/views/auth/StudentRegister.vue"),
      },
      {
        path: "register/company",
        component: () => import("@/views/auth/CompanyRegister.vue"),
      },
    ],
  },
  {
    path: "/student",
    component: DashboardLayout,
    meta: { requiresAuth: true, role: "student" },
    children: [
      { path: "", component: () => import("@/views/student/Dashboard.vue") },
      {
        path: "profile",
        component: () => import("@/views/student/Profile.vue"),
      },
      { path: "jobs", component: () => import("@/views/student/Jobs.vue") },
      {
        path: "jobs/:id",
        component: () => import("@/views/student/JobDetail.vue"),
      },
      {
        path: "applications",
        component: () => import("@/views/student/Applications.vue"),
      },
      {
        path: "readiness",
        component: () => import("@/views/student/Readiness.vue"),
      },
      {
        path: "interviews",
        component: () => import("@/views/student/Interviews.vue"),
      },
      {
        path: "placements",
        component: () => import("@/views/student/Placements.vue"),
      },
    ],
  },
  {
    path: "/company",
    component: DashboardLayout,
    meta: { requiresAuth: true, role: "company" },
    children: [
      { path: "", component: () => import("@/views/company/Dashboard.vue") },
      { path: "jobs", component: () => import("@/views/company/Jobs.vue") },
      {
        path: "jobs/new",
        component: () => import("@/views/company/JobCreate.vue"),
      },
      {
        path: "jobs/:id",
        component: () => import("@/views/company/JobDetail.vue"),
      },
      {
        path: "jobs/:id/applicants",
        component: () => import("@/views/company/Applicants.vue"),
      },
      {
        path: "applicants",
        component: () => import("@/views/company/Applicants.vue"),
      },
      {
        path: "interviews",
        component: () => import("@/views/company/Interviews.vue"),
      },
      {
        path: "reports",
        component: () => import("@/views/company/Reports.vue"),
      },
    ],
  },
  {
    path: "/admin",
    component: DashboardLayout,
    meta: { requiresAuth: true, role: "admin" },
    children: [
      { path: "", component: () => import("@/views/admin/Dashboard.vue") },
      {
        path: "students",
        component: () => import("@/views/admin/Students.vue"),
      },
      {
        path: "companies",
        component: () => import("@/views/admin/Companies.vue"),
      },
      { path: "jobs", component: () => import("@/views/admin/Jobs.vue") },
      {
        path: "applications",
        component: () => import("@/views/admin/Applications.vue"),
      },
      {
        path: "placements",
        component: () => import("@/views/admin/Placements.vue"),
      },
    ],
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to) => {
  const auth = useAuthStore();
  if (!auth.restored) await auth.restore();
  if (to.meta.requiresAuth && !auth.isAuthenticated) return "/login";
  if (to.meta.role && auth.role !== to.meta.role) return auth.homeRoute;
  if (to.name === "login" && auth.isAuthenticated) return auth.homeRoute;
  return true;
});

export default router;
