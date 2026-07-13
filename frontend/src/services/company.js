import { api } from "./http";

export const companyApi = {
  dashboard: () => api.get("/company/dashboard"),
  jobs: () => api.get("/company/jobs"),
  createJob: (payload) => api.post("/company/create-job", payload),
  updateJob: (id, payload) => api.patch(`/company/jobs/${id}`, payload),
  closeJob: (id) => api.patch(`/company/jobs/${id}/close`),
  applicants: (jobId) => api.get(`/company/applicants/${jobId}`),
  updateApplication: (applicationId, payload) =>
    api.patch(`/company/applications/${applicationId}/status`, payload),
  scheduleInterview: (applicationId, payload) =>
    api.post(
      `/company/applications/${applicationId}/schedule-interview`,
      payload,
    ),
  matchScores: (jobId) => api.get(`/company/jobs/${jobId}/match-scores`),
  marketInsight: (jobId) => api.get(`/company/jobs/${jobId}/market-insight`),
  questions: (jobId) => api.get(`/company/jobs/${jobId}/questions`),
  interviews: (jobId) => api.get(`/company/jobs/${jobId}/interviews`),
  exportApplications: () => api.post("/company/export"),
  taskStatus: (id) => api.get(`/task/${id}`),
};
