import { api } from "./http";

export const studentApi = {
  dashboard: () => api.get("/student/dashboard"),
  profile: () => api.get("/student/profile"),
  updateProfile: (payload) => api.patch("/student/profile", payload),
  uploadResume: (payload) => api.post("/student/resume", payload),
  jobs: (params) => api.get("/student/jobs", { params }),
  job: (id) => api.get(`/student/jobs/${id}`),
  apply: (job_id) => api.post("/student/apply", { job_id }),
  readiness: (jobId) => api.get(`/student/jobs/${jobId}/readiness`),
  strategy: () => api.get("/student/strategy"),
  applications: () => api.get("/student/applications"),
  applicationAnalysis: (id) => api.get(`/student/applications/${id}/analysis`),
  interviews: () => api.get("/student/interviews"),
  placements: () => api.get("/student/placements"),
  offerLetter: (id) =>
    api.get(`/student/applications/${id}/offer-letter`, { responseType: "blob" }),
  questions: (skill) =>
    api.get("/student/interview-questions", { params: { skill } }),
  exportApplications: () => api.post("/student/export"),
  taskStatus: (id) => api.get(`/task/${id}`),
};
