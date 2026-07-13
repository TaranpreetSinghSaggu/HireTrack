<template>
  <PageHeader
    title="Jobs"
    description="Create, review, edit pending roles, and open approved drives."
  >
    <template #actions
      ><RouterLink to="/company/jobs/new"
        ><AppButton label="Create job" icon="plus-lg" /></RouterLink
    ></template>
  </PageHeader>
  <LoadingState v-if="loading" />
  <EmptyState
    v-else-if="!jobs.length"
    title="No jobs created"
    description="Create your first campus role and submit it for admin approval."
  />
  <div v-else class="grid grid-2">
    <div v-for="job in jobs" :key="job.id" class="card job">
      <div>
        <h2>{{ job.title }}</h2>
        <p>
          {{ job.location || "Location not specified" }} ·
          {{ job.salary || "Package not specified" }}
        </p>
      </div>
      <StatusBadge :status="job.status" />
      <p class="muted">Deadline {{ formatDate(job.application_deadline) }}</p>
      <div class="actions">
        <RouterLink :to="`/company/jobs/${job.id}`"
          ><AppButton label="Open job" icon="arrow-right" /></RouterLink
        ><RouterLink :to="`/company/jobs/${job.id}/applicants`"
          ><AppButton label="Applicants" icon="people" variant="secondary"
        /></RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import LoadingState from "@/components/LoadingState.vue";
import EmptyState from "@/components/EmptyState.vue";
import AppButton from "@/components/AppButton.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { companyApi } from "@/services/company";
const jobs = ref([]);
const loading = ref(true);
const formatDate = (value) =>
  value ? new Date(value).toLocaleDateString() : "Not set";
onMounted(async () => {
  jobs.value = (await companyApi.jobs()).data;
  loading.value = false;
});
</script>

<style scoped>
.job {
  display: grid;
  gap: 12px;
  padding: 20px;
}
h2 {
  margin: 0;
  color: var(--navy);
  font-size: 20px;
}
p {
  margin: 0;
}
</style>
