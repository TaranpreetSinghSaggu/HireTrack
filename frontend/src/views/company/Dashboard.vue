<template>
  <PageHeader
    title="Company dashboard"
    description="Keep hiring activity moving from application to placement."
  >
    <template #actions>
      <RouterLink to="/company/applicants"><AppButton label="Review applicants" icon="people" /></RouterLink>
    </template>
  </PageHeader>
  <AlertMessage :message="message" :tone="tone" />
  <LoadingState v-if="loading" />
  <section v-else class="section">
    <div class="grid grid-3">
      <StatCard label="Active jobs" :value="data.active_jobs || 0" icon="briefcase" />
      <StatCard label="Applicants" :value="data.total_applications || 0" icon="people" />
      <StatCard label="Pending actions" :value="data.pending_actions || 0" icon="inbox" />
    </div>

    <div class="card panel pipeline-card">
      <div class="section-heading">
        <div>
          <h2>Hiring pipeline</h2>
          <p class="muted">A quick view of candidates across all your jobs.</p>
        </div>
        <RouterLink to="/company/applicants">Open pipeline</RouterLink>
      </div>
      <div class="pipeline">
        <div v-for="stage in stages" :key="stage.key" class="stage">
          <span class="stage-label">{{ stage.label }}</span>
          <strong>{{ data.pipeline_counts?.[stage.key] || 0 }}</strong>
        </div>
      </div>
    </div>

    <div class="grid grid-2">
      <div class="card panel">
        <div class="section-heading"><h2>Placement drives</h2><RouterLink to="/company/jobs">All jobs</RouterLink></div>
        <div v-if="!data.placement_drives?.length" class="muted">No jobs created yet.</div>
        <div v-for="job in data.placement_drives" :key="job.job_id" class="row">
          <div><strong>{{ job.title }}</strong><p>{{ job.applicant_count }} applicants</p></div>
          <StatusBadge :status="job.status" />
          <RouterLink :to="`/company/jobs/${job.job_id}`">Open</RouterLink>
        </div>
      </div>
      <div class="card panel">
        <div class="section-heading"><h2>Upcoming interviews</h2><RouterLink to="/company/interviews">Calendar</RouterLink></div>
        <div v-if="!data.upcoming_interviews?.length" class="muted">No upcoming interviews.</div>
        <div v-for="item in data.upcoming_interviews" :key="item.application_id" class="row interview-row">
          <div><strong>{{ item.student_name }}</strong><p>{{ item.job_title }}</p></div>
          <span>{{ formatDate(item.interview_date) }}</span>
        </div>
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
import AppButton from "@/components/AppButton.vue";
import AlertMessage from "@/components/AlertMessage.vue";
import { companyApi } from "@/services/company";
import { getErrorMessage } from "@/services/http";

const stages = [
  { key: "Applied", label: "Applied" },
  { key: "Shortlisted", label: "Shortlisted" },
  { key: "Interview", label: "Interview" },
  { key: "Offer", label: "Offer" },
  { key: "Placed", label: "Placed" },
];
const data = ref({});
const loading = ref(true);
const message = ref("");
const tone = ref("info");
const formatDate = (value) => value ? new Date(value).toLocaleString() : "Not set";

onMounted(async () => {
  try {
    data.value = (await companyApi.dashboard()).data;
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.panel { padding: 20px; }
.section-heading { display: flex; justify-content: space-between; gap: 16px; align-items: center; }
.section-heading h2 { margin: 0; color: var(--navy); }
.section-heading a, .row a { color: var(--blue); font-weight: 600; }
.pipeline { display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-top: 20px; }
.stage { border: 1px solid var(--border); border-radius: 6px; padding: 14px; background: #fafafa; }
.stage-label { display: block; color: var(--muted); font-size: 13px; margin-bottom: 8px; }
.stage strong { font-size: 24px; color: var(--navy); }
.row { display: grid; grid-template-columns: 1fr auto auto; gap: 12px; align-items: center; border-top: 1px solid var(--border); padding: 12px 0; }
.row p { margin: 4px 0 0; color: var(--muted); font-size: 13px; }
.interview-row { grid-template-columns: 1fr auto; }
@media (max-width: 800px) { .pipeline { grid-template-columns: repeat(2, 1fr); } }
</style>
