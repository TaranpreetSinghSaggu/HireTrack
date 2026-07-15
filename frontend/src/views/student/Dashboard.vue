<template>
  <PageHeader
    title="Student dashboard"
    description="Start with profile readiness, then move through jobs, applications, and interviews."
  />
  <LoadingState v-if="loading" />
  <section v-else class="section">
    <div class="grid grid-3">
      <StatCard
        label="Applications"
        :value="data.stats?.applications || 0"
        icon="clipboard-check"
      />
      <StatCard
        label="Interviews"
        :value="data.stats?.interviews || 0"
        icon="calendar-check"
      />
      <StatCard
        label="Offers"
        :value="data.stats?.offers || 0"
        icon="award"
      />
      <StatCard
        label="Placements"
        :value="data.stats?.placed || 0"
        icon="person-check"
      />
    </div>
    <div class="card panel">
      <h2>Next best action</h2>
      <ProfileProgress label="Profile completion" :value="completion" />
      
      <div class="actions">
        <RouterLink to="/student/profile"
          ><AppButton label="Complete profile" icon="person"
        /></RouterLink>
        <RouterLink to="/student/jobs"
          ><AppButton
            label="Browse eligible jobs"
            icon="briefcase"
            variant="secondary"
        /></RouterLink>
        <RouterLink to="/student/readiness"
          ><AppButton
            label="Check readiness"
            icon="speedometer2"
            variant="secondary"
        /></RouterLink>
      </div>
    </div>
    <div class="card panel">
      <h2>Recent open jobs</h2>
      <div v-if="!data.recent_jobs?.length" class="muted">
        No open jobs available right now.
      </div>
      <div v-for="job in data.recent_jobs" :key="job.id" class="row">
        <div>
          <strong>{{ job.title }}</strong>
          <p>
            {{ job.company_name }} ·
            {{ job.location || "Location not specified" }}
          </p>
        </div>
        <RouterLink :to="`/student/jobs/${job.id}`">View</RouterLink>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import StatCard from "@/components/StatCard.vue";
import ProfileProgress from "@/components/ProfileProgress.vue";
import LoadingState from "@/components/LoadingState.vue";
import AppButton from "@/components/AppButton.vue";
import { studentApi } from "@/services/student";

const data = ref({});
const loading = ref(true);
const completion = computed(() => {
  const fields = [
    "name",
    "cgpa",
    "branch",
    "year",
    "skills",
    "contact",
    "degree",
    "institution",
    "passout_year",
    "experience",
    "resume_filename",
  ];
  return Math.round(
    (fields.filter((field) => data.value[field]).length / fields.length) * 100,
  );
});
onMounted(async () => {
  const res = await studentApi.dashboard();
  data.value = res.data;
  loading.value = false;
});
</script>

<style scoped>
.panel {
  padding: 20px;
}
h2 {
  margin: 0 0 24px;
  color: var(--navy);
  font-size: 20px;
}

/* .profile-progress {
  margin-bottom: 24px; 
} */
.actions {
  margin-top: 24px;
}
.row {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  border-top: 1px solid var(--border);
  padding: 12px 0;
}
.row p {
  margin: 4px 0 0;
  color: var(--muted);
}
a {
  color: var(--blue);
  font-weight: 600;
}
</style>
