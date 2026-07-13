<template>
  <PageHeader
    title="Company dashboard"
    description="Review active drives, applicants, interviews, and selected candidates."
  />
  <LoadingState v-if="loading" />
  <section v-else class="section">
    <div class="grid grid-3">
      <StatCard
        label="Active jobs"
        :value="data.active_jobs || 0"
        icon="briefcase"
      />
      <StatCard
        label="Applicants"
        :value="data.total_applications || 0"
        icon="people"
      />
      <StatCard
        label="Selected"
        :value="data.selected_count || 0"
        icon="person-check"
      />
    </div>
    <div class="card panel">
      <h2>Placement drives</h2>
      <div v-for="job in data.placement_drives" :key="job.job_id" class="row">
        <div>
          <strong>{{ job.title }}</strong>
          <p>{{ job.applicant_count }} applicants</p>
        </div>
        <StatusBadge :status="job.status" /><RouterLink
          :to="`/company/jobs/${job.job_id}`"
          >Open</RouterLink
        >
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import LoadingState from "@/components/LoadingState.vue";
import StatCard from "@/components/StatCard.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { companyApi } from "@/services/company";
const data = ref({});
const loading = ref(true);
onMounted(async () => {
  data.value = (await companyApi.dashboard()).data;
  loading.value = false;
});
</script>

<style scoped>
.panel {
  padding: 20px;
}
.row {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 12px;
  align-items: center;
  border-top: 1px solid var(--border);
  padding: 12px 0;
}
h2 {
  margin: 0 0 12px;
  color: var(--navy);
}
p {
  margin: 0;
  color: var(--muted);
}
a {
  color: var(--blue);
  font-weight: 600;
}
</style>
