<template>
  <div class="shell" :class="{ collapsed, drawer: drawerOpen }">
    <header class="topbar">
      <button
        class="icon-button menu"
        type="button"
        aria-label="Toggle navigation"
        @click="toggleNav"
      >
        <i class="bi bi-list"></i>
      </button>
      <RouterLink class="logo" :to="homeRoute">HireTrack</RouterLink>
      <button class="profile" type="button" @click="logout">
        <i class="bi bi-person-circle"></i><span>Logout</span>
      </button>
    </header>

    <aside class="sidebar">
      <nav>
        <RouterLink v-for="item in navItems" :key="item.to" :to="item.to" :class="{ 'nav-exact': item.to === '/company', 'active-link': item.to === '/company' && $route.path === '/company' }">
          <i :class="`bi bi-${item.icon}`"></i>
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>
    </aside>

    <button
      v-if="drawerOpen"
      class="scrim"
      type="button"
      aria-label="Close navigation"
      @click="drawerOpen = false"
    ></button>

    <main class="content">
      <div class="content-inner">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useAuthStore } from "@/stores/auth";

const auth = useAuthStore();
const collapsed = ref(false);
const drawerOpen = ref(false);
const homeRoute = computed(() => auth.homeRoute);

const navItems = computed(() => {
  if (auth.role === "company") {
    return [
      { label: "Dashboard", icon: "grid", to: "/company" },
      { label: "Jobs", icon: "briefcase", to: "/company/jobs" },
      { label: "Applicants", icon: "people", to: "/company/applicants" },
      {
        label: "Interviews",
        icon: "calendar-check",
        to: "/company/interviews",
      },
      {
        label: "Reports",
        icon: "file-earmark-bar-graph",
        to: "/company/reports",
      },
    ];
  }
  if (auth.role === "admin") {
    return [
      { label: "Dashboard", icon: "grid", to: "/admin" },
      { label: "Students", icon: "mortarboard", to: "/admin/students" },
      { label: "Companies", icon: "building", to: "/admin/companies" },
      { label: "Drives", icon: "briefcase", to: "/admin/jobs" },
      { label: "Placements", icon: "graph-up", to: "/admin/placements" },
      {
        label: "Reports",
        icon: "file-earmark-text",
        to: "/admin/applications",
      },
    ];
  }
  return [
    { label: "Dashboard", icon: "grid", to: "/student" },
    { label: "Jobs", icon: "briefcase", to: "/student/jobs" },
    {
      label: "Applications",
      icon: "clipboard-check",
      to: "/student/applications",
    },
    { label: "Interviews", icon: "calendar-check", to: "/student/interviews" },
    { label: "Readiness", icon: "speedometer2", to: "/student/readiness" },
    { label: "Profile", icon: "person", to: "/student/profile" },
    { label: "Placements", icon: "award", to: "/student/placements" },
  ];
});

function toggleNav() {
  if (window.matchMedia("(max-width: 991px)").matches)
    drawerOpen.value = !drawerOpen.value;
  else collapsed.value = !collapsed.value;
}

function logout() {
  auth.logout();
}
</script>

<style scoped>
.shell {
  --side: 240px;
}
.shell.collapsed {
  --side: 72px;
}
.topbar {
  position: fixed;
  inset: 0 0 auto 0;
  z-index: 20;
  display: flex;
  height: 64px;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--border);
  background: #fff;
  padding: 0 20px;
}
.logo {
  color: var(--navy);
  font-size: 20px;
  font-weight: 700;
}
.icon-button,
.profile {
  min-width: 40px;
  height: 40px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: #fff;
  color: var(--text);
}
.profile {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
}
.sidebar {
  position: fixed;
  top: 64px;
  bottom: 0;
  left: 0;
  z-index: 21;
  width: var(--side);
  border-right: 1px solid var(--border);
  background: #fff;
  padding: 16px 12px;
  transition: width 180ms ease;
}
nav {
  display: grid;
  gap: 4px;
}
nav a {
  display: flex;
  min-height: 44px;
  align-items: center;
  gap: 12px;
  border-radius: 6px;
  color: var(--text);
  padding: 0 12px;
  font-weight: 500;
}
nav a:hover {
  background: #f3f4f6;
}
nav a.router-link-active:not(.nav-exact),
nav a.active-link {
  background: #e0ecff;
  color: var(--blue);
  font-weight: 700;
}
.collapsed nav span {
  display: none;
}
.content {
  padding-top: 64px;
  padding-left: var(--side);
}
.content-inner {
  width: min(1440px, 100%);
  min-height: calc(100vh - 64px);
  padding: 24px;
}
.scrim {
  display: none;
}
@media (max-width: 991px) {
  .shell {
    --side: 0px;
  }
  .sidebar {
    transform: translateX(-100%);
    width: 240px;
  }
  .drawer .sidebar {
    transform: translateX(0);
  }
  .scrim {
    position: fixed;
    inset: 64px 0 0;
    z-index: 19;
    display: block;
    border: 0;
    background: rgba(17, 24, 39, 0.28);
  }
}
@media (max-width: 767px) {
  .profile span {
    display: none;
  }
  .content-inner {
    padding: 16px;
  }
}
</style>
