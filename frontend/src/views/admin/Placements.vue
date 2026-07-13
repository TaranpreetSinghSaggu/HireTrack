<template>
  <PageHeader
    title="Placements"
    description="Placement-rate summaries from the current analytics endpoint."
  />
  <LoadingState v-if="loading" />
  <section v-else class="section">
    <div class="grid grid-3">
      <StatCard
        label="Students"
        :value="data.total_students"
        icon="mortarboard"
      /><StatCard
        label="Selected or placed"
        :value="data.total_selected"
        icon="award"
      /><StatCard
        label="Applications"
        :value="data.total_applications"
        icon="clipboard-check"
      />
    </div>
    <div class="card panel">
      <ProfileProgress
        label="Placement rate"
        :value="data.placement_rate || 0"
      />
      <h2>Top companies</h2>
      <p v-if="!data.top_companies?.length" class="muted">
        No placement company ranking yet.
      </p>
      <ul>
        <li v-for="company in data.top_companies" :key="company">
          {{ company }}
        </li>
      </ul>
    </div>
    <div class="card panel">
      <h2>Recent activity</h2>
      <div
        v-for="item in data.recent_activity"
        :key="`${item.student_id}-${item.job_id}-${item.status}`"
        class="row"
      >
        Student {{ item.student_id }} · Job {{ item.job_id }}
        <StatusBadge :status="item.status" />
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
import StatusBadge from "@/components/StatusBadge.vue";
import { adminApi } from "@/services/admin";
const data = ref({});
const loading = ref(true);
onMounted(async () => {
  data.value = (await adminApi.analytics()).data;
  loading.value = false;
});
</script>
<style scoped>
.panel {
  padding: 20px;
}
h2 {
  margin: 20px 0 12px;
  color: var(--navy);
}
.row {
  display: flex;
  justify-content: space-between;
  border-top: 1px solid var(--border);
  padding: 10px 0;
}
</style>
