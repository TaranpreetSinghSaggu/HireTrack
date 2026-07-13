<template>
  <PageHeader
    title="Eligible jobs"
    description="Filter by company, role, skills, or only show roles you can apply for."
  />
  <div class="card filters">
    <input v-model="filters.company" class="input" placeholder="Company" />
    <input v-model="filters.position" class="input" placeholder="Role" />
    <input v-model="filters.skills" class="input" placeholder="Skill" />
    <label
      ><input v-model="filters.eligible_only" type="checkbox" /> Eligible
      only</label
    >
    <AppButton label="Search" icon="search" @click="load" />
  </div>
  <LoadingState v-if="loading" />
  <EmptyState
    v-else-if="!jobs.length"
    title="No jobs match your filters"
    description="Try widening the filters or complete your profile for more accurate eligibility."
  />
  <div v-else class="grid grid-2">
    <div v-for="job in jobs" :key="job.id" class="card job">
      <div>
        <h2>{{ job.title }}</h2>
        <p>
          {{ job.company_name }} ·
          {{ job.location || "Location not specified" }}
        </p>
      </div>
      <StatusBadge :status="job.is_eligible ? 'Eligible' : 'Pending'" />
      <p>
        {{ job.salary || "Package not specified" }} · Deadline
        {{ formatDate(job.application_deadline) }}
      </p>
      <p class="muted">Skills: {{ job.skills_required || "Not specified" }}</p>
      <div v-if="job.eligibility_reasons?.length" class="muted">
        Missing: {{ job.eligibility_reasons.join(", ") }}
      </div>
      <div class="actions">
        <RouterLink :to="`/student/jobs/${job.id}`"
          ><AppButton label="View details" icon="arrow-right"
        /></RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import LoadingState from "@/components/LoadingState.vue";
import EmptyState from "@/components/EmptyState.vue";
import AppButton from "@/components/AppButton.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { studentApi } from "@/services/student";

const filters = reactive({
  company: "",
  position: "",
  skills: "",
  eligible_only: false,
});
const jobs = ref([]);
const loading = ref(true);
const formatDate = (value) =>
  value ? new Date(value).toLocaleDateString() : "Not set";
async function load() {
  loading.value = true;
  jobs.value = (await studentApi.jobs(filters)).data;
  loading.value = false;
}
onMounted(load);
</script>

<style scoped>
.filters {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
  align-items: center;
  margin-bottom: 20px;
  padding: 16px;
}
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
@media (max-width: 991px) {
  .filters {
    grid-template-columns: 1fr;
  }
}
</style>
