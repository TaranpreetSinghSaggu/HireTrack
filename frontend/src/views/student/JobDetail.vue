<template>
  <PageHeader
    :title="job.title || 'Job detail'"
    :description="job.company_name"
  >
    <template #actions
      ><RouterLink to="/student/jobs"
        ><AppButton label="Back to jobs" variant="secondary" /></RouterLink
    ></template>
  </PageHeader>
  <AlertMessage :message="message" :tone="tone" />
  <LoadingState v-if="loading" />
  <section v-else class="grid grid-2">
    <div class="card panel">
      <StatusBadge :status="job.is_eligible ? 'Eligible' : 'Not eligible'" />
      <p>{{ job.description }}</p>
      <dl>
        <dt>Package</dt>
        <dd>{{ job.salary || "Not specified" }}</dd>
        <dt>Deadline</dt>
        <dd>{{ formatDate(job.application_deadline) }}</dd>
        <dt>Skills</dt>
        <dd>{{ job.skills_required || "Not specified" }}</dd>
        <dt>Eligibility</dt>
        <dd>{{ eligibility }}</dd>
      </dl>
      <AppButton
        label="Apply"
        icon="send"
        :disabled="!job.is_eligible || job.already_applied"
        @click="apply"
      />
    </div>
    <div class="card panel">
      <h2>Readiness</h2>
      <ProfileProgress :value="readiness.score || 0" label="Job readiness" />
      <p class="muted">
        Matched: {{ readiness.matched_skills?.join(", ") || "None yet" }}
      </p>
      <p class="muted">
        Missing: {{ readiness.missing_skills?.join(", ") || "None" }}
      </p>
      <ul>
        <li v-for="item in readiness.suggestions" :key="item">{{ item }}</li>
      </ul>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import PageHeader from "@/components/PageHeader.vue";
import LoadingState from "@/components/LoadingState.vue";
import AppButton from "@/components/AppButton.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import ProfileProgress from "@/components/ProfileProgress.vue";
import AlertMessage from "@/components/AlertMessage.vue";
import { studentApi } from "@/services/student";
import { getErrorMessage } from "@/services/http";

const route = useRoute();
const job = ref({});
const readiness = ref({});
const loading = ref(true);
const message = ref("");
const tone = ref("info");
const eligibility = computed(() =>
  job.value.eligibility_reasons?.length
    ? job.value.eligibility_reasons.join(", ")
    : "Meets current criteria",
);
const formatDate = (value) =>
  value ? new Date(value).toLocaleString() : "Not set";
onMounted(async () => {
  const id = route.params.id;
  job.value = (await studentApi.job(id)).data;
  readiness.value = (await studentApi.readiness(id)).data;
  loading.value = false;
});
async function apply() {
  try {
    await studentApi.apply(job.value.id);
    tone.value = "success";
    message.value = "Application submitted.";
    job.value.already_applied = true;
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  }
}
</script>

<style scoped>
.panel {
  padding: 20px;
}
dl {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 8px 12px;
}
dt {
  color: var(--muted);
  font-weight: 600;
}
dd {
  margin: 0;
}
h2 {
  margin: 0 0 16px;
  color: var(--navy);
}
</style>
