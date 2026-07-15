<template>
  <PageHeader title="Interviews" description="See upcoming and completed interviews across your jobs." />
  <AlertMessage :message="message" :tone="tone" />
  <div class="card filters">
    <select v-model="jobId" class="input" @change="load"><option value="">All jobs</option><option v-for="job in jobs" :key="job.id" :value="job.id">{{ job.title }}</option></select>
  </div>
  <LoadingState v-if="loading" />
  <EmptyState v-else-if="!items.length" title="No interviews scheduled" description="Scheduled interviews will appear here." />
  <div v-else class="table-wrap">
    <table><thead><tr><th>Candidate</th><th>Role</th><th>Date</th><th>Mode</th><th>Status</th></tr></thead><tbody>
      <tr v-for="item in items" :key="item.interview_id"><td>{{ item.student_name }}</td><td>{{ item.job_title }}</td><td>{{ formatDate(item.interview_date) }}</td><td>{{ item.interview_link || item.venue || "Not specified" }}</td><td><StatusBadge :status="item.application_status" /></td></tr>
    </tbody></table>
  </div>

  <div v-if="jobId" class="card prep-card">
    <div class="prep-header"><div><h2>Interview prep</h2><p class="muted">Optional questions based on the selected job.</p></div><AppButton label="Generate questions" icon="stars" :loading="loadingQuestions" @click="generateQuestions" /></div>
    <ol v-if="questions.length" class="q-list"><li v-for="(question, index) in questions" :key="index">{{ question }}</li></ol>
    <p v-else class="muted">No questions generated yet.</p>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import LoadingState from "@/components/LoadingState.vue";
import EmptyState from "@/components/EmptyState.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import AppButton from "@/components/AppButton.vue";
import AlertMessage from "@/components/AlertMessage.vue";
import { companyApi } from "@/services/company";
import { getErrorMessage } from "@/services/http";

const jobs = ref([]); const items = ref([]); const jobId = ref(""); const questions = ref([]); const loading = ref(true); const loadingQuestions = ref(false); const message = ref(""); const tone = ref("info");
const formatDate = (value) => value ? new Date(value).toLocaleString() : "Not set";
async function load() { loading.value = true; questions.value = []; try { items.value = (await companyApi.allInterviews(jobId.value ? { job_id: jobId.value } : {})).data; } catch (error) { tone.value = "danger"; message.value = getErrorMessage(error); } finally { loading.value = false; } }
async function generateQuestions() { if (!jobId.value) return; loadingQuestions.value = true; try { questions.value = (await companyApi.questions(jobId.value)).data.questions || []; } catch (error) { tone.value = "danger"; message.value = getErrorMessage(error); } finally { loadingQuestions.value = false; } }
onMounted(async () => { try { jobs.value = (await companyApi.jobs()).data; } catch (error) { tone.value = "danger"; message.value = getErrorMessage(error); } await load(); });
</script>

<style scoped>
.filters { padding: 16px; margin-bottom: 20px; }
.prep-card { margin-top: 20px; padding: 20px; }
.prep-header { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.prep-header h2 { margin: 0; color: var(--navy); }
.q-list { line-height: 1.7; margin: 18px 0 0; padding-left: 20px; }
@media (max-width: 600px) { .prep-header { display: grid; } }
</style>
