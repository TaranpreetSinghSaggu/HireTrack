import { defineStore } from "pinia";
import { authApi } from "@/services/auth";
import { getErrorMessage, setUnauthorizedHandler } from "@/services/http";

export const useAuthStore = defineStore("auth", {
  state: () => ({
    token: localStorage.getItem("hiretrack.token"),
    role: localStorage.getItem("hiretrack.role"),
    userId: localStorage.getItem("hiretrack.userId"),
    loading: false,
    error: "",
    restored: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    homeRoute: (state) => {
      if (state.role === "admin") return "/admin";
      if (state.role === "company") return "/company";
      return "/student";
    },
  },
  actions: {
    wireUnauthorized() {
      setUnauthorizedHandler(() => this.logout());
    },
    persist() {
      if (this.token) localStorage.setItem("hiretrack.token", this.token);
      if (this.role) localStorage.setItem("hiretrack.role", this.role);
      if (this.userId) localStorage.setItem("hiretrack.userId", this.userId);
    },
    clear() {
      this.token = null;
      this.role = null;
      this.userId = null;
      localStorage.removeItem("hiretrack.token");
      localStorage.removeItem("hiretrack.role");
      localStorage.removeItem("hiretrack.userId");
    },
    async login(payload) {
      this.loading = true;
      this.error = "";
      try {
        const { data } = await authApi.login(payload);
        this.token = data.token;
        this.role = data.role;
        this.userId = data.user_id;
        this.persist();
        return data;
      } catch (error) {
        this.error = getErrorMessage(error);
        throw error;
      } finally {
        this.loading = false;
      }
    },
    async restore() {
      this.wireUnauthorized();
      if (!this.token) {
        this.restored = true;
        return;
      }
      try {
        const { data } = await authApi.me();
        this.role = data.role;
        this.userId = data.user_id;
        this.persist();
      } catch {
        this.clear();
      } finally {
        this.restored = true;
      }
    },
    logout() {
      this.clear();
      if (window.location.pathname !== "/dashboard") {
        window.location.href = "/dashboard";
      }
    },
  },
});
