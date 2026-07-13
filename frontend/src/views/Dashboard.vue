<template>
  <div class="portal">
    <main>
      <HeroSection />
      <div class="page-width">
        <AnnouncementList />
        <QuickAccess />
        <LoadingState v-if="loading" />
        <template v-else>
          <StatsSection :data="data" />
          <DriveTable id="drives" :drives="data.recent_jobs" />
        </template>
      </div>
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import AppFooter from "@/components/AppFooter.vue";
import AnnouncementList from "@/components/AnnouncementList.vue";
import DriveTable from "@/components/DriveTable.vue";
import HeroSection from "@/components/HeroSection.vue";
import LoadingState from "@/components/LoadingState.vue";
import QuickAccess from "@/components/QuickAccess.vue";
import StatsSection from "@/components/StatsSection.vue";
import { adminApi } from "@/services/admin";

const data = ref({ recent_jobs: [] });
const loading = ref(true);
onMounted(async () => {
  try {
    data.value = (await adminApi.publicDashboard()).data;
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.portal {
  min-height: 100vh;
  background: var(--bg);
}
.page-width {
  width: min(1060px, calc(100% - 40px));
  margin: 0 auto;
}
@media (max-width: 600px) {
  .page-width {
    width: min(100% - 28px, 1060px);
  }
}
</style>
