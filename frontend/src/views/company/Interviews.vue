<template>
  <PageHeader
    title="Interviews"
    description="Choose a job to view scheduled interviews."
  />
  
  <AlertMessage :message="message" :tone="tone" />

  <div class="card filters">
    <select v-model="jobId" class="input" @change="load">
      <option value="">Select job</option>
      <option v-for="job in jobs" :key="job.id" :value="job.id">
        {{ job.title }}
      </option>
    </select>
  </div>

  <div v-if="items.length" class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Candidate</th>
          <th>Date</th>
          <th>Mode</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.interview_id">
          <td>{{ item.student_name }}</td>
          <td>{{ formatDate(item.interview_date) }}</td>
          <td>{{ item.interview_link || item.venue || "-" }}</td>
          <td><StatusBadge :status="item.application_status" /></td>
        </tr>
      </tbody>
    </table>
  </div>
  
  <div v-else-if="jobId && !items.length" class="card empty-interviews">
    <p class="muted text-center">No interviews scheduled for this job yet.</p>
  </div>

  <!-- Interview Prep Questions -->
  <div v-if="jobId" class="card prep-card">
    <div class="prep-header">
      <h2>Interview Questions</h2>
      <AppButton
        v-if="!questions.length"
        label="Generate Questions"
        :loading="loadingQuestions"
        @click="generateQuestions"
      />
      <AppButton
        v-else
        label="Regenerate Questions"
        icon="arrow-clockwise"
        variant="secondary"
        :loading="loadingQuestions"
        @click="generateQuestions"
      />
    </div>
    
    <div v-if="loadingQuestions" class="loading-questions">
      <LoadingState />
      <p class="muted">Generating questions...</p>
    </div>
    
    <div v-else-if="questions.length" class="questions-list">
      <p class="muted prep-intro">The following questions are generated based on the job requirements:</p>
      <ol class="q-list">
        <li v-for="(q, idx) in questions" :key="idx" class="question-item">
          {{ q }}
        </li>
      </ol>
    </div>
    
    <div v-else-if="hasGenerated && !questions.length" class="questions-error">
      <p class="muted text-center">AI Interview Questions are not available because the API key is not configured.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import AppButton from "@/components/AppButton.vue";
import AlertMessage from "@/components/AlertMessage.vue";
import LoadingState from "@/components/LoadingState.vue";
import { companyApi } from "@/services/company";
import { getErrorMessage } from "@/services/http";

const jobs = ref([]);
const items = ref([]);
const jobId = ref("");
const questions = ref([]);
const loadingQuestions = ref(false);
const hasGenerated = ref(false);
const message = ref("");
const tone = ref("info");

const formatDate = (value) =>
  value ? new Date(value).toLocaleString() : "Not set";

onMounted(async () => {
  try {
    jobs.value = (await companyApi.jobs()).data;
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  }
});

async function load() {
  questions.value = [];
  hasGenerated.value = false;
  message.value = "";
  if (!jobId.value) {
    items.value = [];
    return;
  }
  try {
    items.value = (await companyApi.interviews(jobId.value)).data;
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  }
}

async function generateQuestions() {
  if (!jobId.value) return;
  loadingQuestions.value = true;
  message.value = "";
  hasGenerated.value = true;
  try {
    const res = await companyApi.questions(jobId.value);
    questions.value = res.data.questions || [];
    if (questions.value.length > 0) {
      tone.value = "success";
      message.value = "Questions generated successfully.";
    } else {
      tone.value = "warning";
      message.value = "API key is not configured. Could not generate questions.";
    }
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  } finally {
    loadingQuestions.value = false;
  }
}
</script>

<style scoped>
.filters {
  padding: 16px;
  margin-bottom: 20px;
}
.empty-interviews {
  padding: 20px;
  margin-bottom: 20px;
  text-align: center;
}
.prep-card {
  margin-top: 20px;
  padding: 20px;
}
.prep-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
.prep-header h2 {
  margin: 0;
  font-size: 18px;
  color: var(--navy);
}
.loading-questions {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20px;
  gap: 8px;
}
.questions-list {
  margin-top: 16px;
  border-top: 1px solid var(--border);
  padding-top: 16px;
}
.prep-intro {
  margin-bottom: 16px;
}
.q-list {
  padding-left: 20px;
}
.question-item {
  margin-bottom: 12px;
  line-height: 1.6;
  font-weight: 500;
}
.questions-error {
  margin-top: 16px;
  border-top: 1px solid var(--border);
  padding-top: 16px;
  text-align: center;
}
.text-center {
  text-align: center;
}
</style>
