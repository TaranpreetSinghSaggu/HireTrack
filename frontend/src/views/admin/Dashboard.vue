<template>
  <PageHeader
    title="Admin dashboard"
    description="Operations overview for students, companies, drives, and placements."
  />
  <LoadingState v-if="loading" />
  <section v-else class="section">
    <div class="grid grid-3">
      <StatCard
        label="Students"
        :value="data.total_students || 0"
        icon="mortarboard"
      />
      <StatCard
        label="Companies"
        :value="data.total_companies || 0"
        icon="building"
      />
      <StatCard
        label="Pending jobs"
        :value="data.pending_jobs || 0"
        icon="hourglass-split"
      />
    </div>
    <div class="grid grid-2">
      <div class="card panel">
        <h2>Pending operations</h2>
        <p>{{ data.pending_companies || 0 }} companies awaiting approval</p>
        <p>{{ data.pending_jobs || 0 }} drives awaiting review</p>
      </div>
      <div class="card panel">
        <h2>Placement rate</h2>
        <ProfileProgress
          :value="analytics.placement_rate || 0"
          label="Placed or selected students"
        />
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import LoadingState from "@/components/LoadingState.vue";
import StatCard from "@/components/StatCard.vue";
import ProfileProgress from "@/components/ProfileProgress.vue";
import { adminApi } from "@/services/admin";
const data = ref({});
const analytics = ref({});
const loading = ref(true);
onMounted(async () => {
  [data.value, analytics.value] = await Promise.all([
    adminApi.dashboard().then((r) => r.data),
    adminApi.analytics().then((r) => r.data),
  ]);
  loading.value = false;
});
</script>
<style scoped>
.panel {
  padding: 20px;
}
h2 {
  margin: 0 0 12px;
  color: var(--navy);
}
p {
  margin: 0 0 8px;
}
</style>
