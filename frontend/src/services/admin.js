import { api } from "./http";

export const adminApi = {
  publicDashboard: () => api.get("/dashboard"),
  dashboard: () => api.get("/admin/dashboard"),
  companies: (params) => api.get("/admin/companies", { params }),
  students: (params) => api.get("/admin/students", { params }),
  jobs: (params) => api.get("/admin/jobs", { params }),
  applications: (params) => api.get("/admin/applications", { params }),
  exportPdf: () => api.get("/admin/reports/export-pdf", { responseType: "blob" }),
  analytics: () => api.get("/admin/analytics/placement"),
  approveCompany: (id) => api.post(`/admin/approve-company/${id}`),
  removeCompany: (id) => api.delete(`/admin/companies/${id}/remove`),
  blacklistCompany: (id, is_blacklisted) =>
    api.patch(`/admin/companies/${id}/blacklist`, { is_blacklisted }),
  setUserStatus: (id, status) =>
    api.patch(`/admin/users/${id}/status`, { status }),
  approveJob: (id) => api.post(`/admin/approve-job/${id}`),
  rejectJob: (id) => api.delete(`/admin/jobs/${id}/remove`),
};
