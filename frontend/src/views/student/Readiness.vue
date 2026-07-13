<template>
  <PageHeader
    title="Readiness"
    description="Use strategy recommendations, urgent deadlines, missing skills, and interview practice to prepare."
  />
  <AlertMessage :message="message" tone="danger" />
  <LoadingState v-if="loading" />
  <section v-else class="section">
    <div class="card panel">
      <ProfileProgress
        label="Overall readiness"
        :value="strategy.readiness_score || 0"
      />
    </div>
    <div class="grid grid-2">
      <div class="card panel">
        <h2>Recommended jobs</h2>
        <div
          v-for="job in strategy.recommended_jobs"
          :key="job.job_id"
          class="row"
        >
          <RouterLink :to="`/student/jobs/${job.job_id}`">{{
            job.title
          }}</RouterLink
          ><strong>{{ job.score }}%</strong>
        </div>
      </div>
      <div class="card panel">
        <h2>Urgent deadlines</h2>
        <p v-if="!strategy.urgent_actions?.length" class="muted">
          No urgent deadlines.
        </p>
        <div
          v-for="job in strategy.urgent_actions"
          :key="job.job_id"
          class="row"
        >
          <RouterLink :to="`/student/jobs/${job.job_id}`">{{
            job.title
          }}</RouterLink
          ><span>{{ formatDate(job.deadline) }}</span>
        </div>
      </div>
      <div class="card panel">
        <h2>Weekly plan</h2>
        <ul>
          <li v-for="item in strategy.weekly_plan" :key="item">{{ item }}</li>
        </ul>
      </div>
      <div class="card panel">
        <h2>Practice questions</h2>
        <div class="actions">
          <input
            v-model="skill"
            class="input"
            placeholder="Skill, e.g. Python"
          /><AppButton
            label="Generate"
            icon="question-circle"
            @click="loadQuestions"
          />
        </div>
        <ol>
          <li v-for="q in questions" :key="q">{{ q }}</li>
        </ol>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import LoadingState from "@/components/LoadingState.vue";
import ProfileProgress from "@/components/ProfileProgress.vue";
import AppButton from "@/components/AppButton.vue";
import AlertMessage from "@/components/AlertMessage.vue";
import { studentApi } from "@/services/student";
import { getErrorMessage } from "@/services/http";

const strategy = ref({});
const loading = ref(true);
const skill = ref("python");
const questions = ref([]);
const message = ref("");
const formatDate = (value) =>
  value ? new Date(value).toLocaleDateString() : "Not set";
onMounted(loadStrategy);
async function loadStrategy() {
  try {
    strategy.value = (await studentApi.strategy()).data;
  } catch (error) {
    message.value = getErrorMessage(error);
  } finally {
    loading.value = false;
  }
}
async function loadQuestions() {
  message.value = "";
  try {
    questions.value = (await studentApi.questions(skill.value)).data.questions || [];
  } catch (error) {
    questions.value = [];
    message.value = getErrorMessage(error);
  }
}
</script>

<style scoped>
.panel {
  padding: 20px;
}
.row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  border-top: 1px solid var(--border);
  padding: 10px 0;
}
h2 {
  margin: 0 0 12px;
  color: var(--navy);
  font-size: 20px;
}
a {
  color: var(--blue);
  font-weight: 600;
}
</style>
