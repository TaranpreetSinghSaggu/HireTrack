import { api } from "./http";

export const companyApi = {
  dashboard: () => api.get("/company/dashboard"),
  jobs: () => api.get("/company/jobs"),
  createJob: (payload) => api.post("/company/create-job", payload),
  updateJob: (id, payload) => api.patch(`/company/jobs/${id}`, payload),
  closeJob: (id) => api.patch(`/company/jobs/${id}/close`),
  allApplicants: (params) => api.get("/company/applicants", { params }),
  updateApplication: (applicationId, payload) =>
    api.patch(`/company/applications/${applicationId}/status`, payload),
  scheduleInterview: (applicationId, payload) =>
    api.post(
      `/company/applications/${applicationId}/schedule-interview`,
      payload,
    ),
  marketInsight: (jobId) => api.get(`/company/jobs/${jobId}/market-insight`),
  questions: (jobId) => api.get(`/company/jobs/${jobId}/questions`),
  allInterviews: (params) => api.get("/company/interviews", { params }),
  createOffer: (applicationId, payload) =>
    api.post(`/company/applications/${applicationId}/offer`, payload, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  placeCandidate: (applicationId, payload) =>
    api.post(`/company/applications/${applicationId}/place`, payload),
  resume: (applicationId) =>
    api.get(`/company/applications/${applicationId}/resume`, { responseType: "blob" }),
  exportApplications: () => api.post("/company/export"),
  taskStatus: (id) => api.get(`/task/${id}`),
  downloadExport: (id) =>
    api.get(`/company/export/${id}/download`, { responseType: "blob" }),
};
