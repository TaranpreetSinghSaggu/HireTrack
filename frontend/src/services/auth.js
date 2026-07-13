import { api } from "./http";

export const authApi = {
  login(payload) {
    return api.post("/auth/login", payload);
  },
  me() {
    return api.get("/auth/me");
  },
  registerStudent(payload) {
    return api.post("/auth/register/student", payload);
  },
  registerCompany(payload) {
    return api.post("/auth/register/company", payload);
  },
};
