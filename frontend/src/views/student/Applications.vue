<template>
  <PageHeader title="Applications" description="Track every application, interview, offer, and placement decision.">
    <template #actions><AppButton label="Export" icon="download" variant="secondary" :loading="exporting" @click="startExport" /></template>
  </PageHeader>
  <AlertMessage :message="message" :tone="tone" />
  <LoadingState v-if="loading" />
  <EmptyState v-else-if="!apps.length" title="No applications yet" description="Browse eligible jobs to start applying." />
  <div v-else class="application-list">
    <div v-for="app in apps" :key="app.application_id" class="card application-card">
      <div class="application-heading"><div><h2>{{ app.job_title }}</h2><p class="muted">{{ app.company_name }} · Applied {{ formatDate(app.application_date) }}</p></div><StatusBadge :status="app.status" /></div>
      <div class="timeline"><div v-for="history in app.history" :key="`${history.status}-${history.created_at}`" class="timeline-item"><StatusBadge :status="history.status" /><span>{{ formatDate(history.created_at) }}</span><p v-if="history.feedback">{{ history.feedback }}</p></div></div>
      <div v-if="app.interview" class="detail"><strong>Interview</strong><span>{{ formatDate(app.interview.interview_date) }}</span><span>{{ app.interview.interview_link || app.interview.venue || "Details in HireTrack" }}</span></div>
      <div v-if="app.offer" class="detail offer-detail"><div><strong>Offer</strong><span>Salary: {{ app.offer.salary || "Not specified" }}</span><span>Joining: {{ formatDate(app.offer.joining_date) }}</span></div><AppButton v-if="app.offer.has_letter" label="Download offer" icon="download" variant="secondary" @click="downloadOffer(app)" /></div>
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
import AlertMessage from "@/components/AlertMessage.vue";
import { studentApi } from "@/services/student";
import { getErrorMessage } from "@/services/http";
const apps = ref([]); const loading = ref(true); const exporting = ref(false); const message = ref(""); const tone = ref("info");
const formatDate = (value) => value ? new Date(value).toLocaleString() : "Not set";
onMounted(async () => { try { apps.value = (await studentApi.applications()).data; } catch (error) { tone.value = "danger"; message.value = getErrorMessage(error); } finally { loading.value = false; } });
async function startExport() { exporting.value = true; try { const { data } = await studentApi.exportApplications(); message.value = `Export started. Task ${data.task_id}`; tone.value = "success"; } catch (error) { tone.value = "danger"; message.value = getErrorMessage(error); } finally { exporting.value = false; } }
async function downloadOffer(app) { try { const response = await studentApi.offerLetter(app.application_id); const url = URL.createObjectURL(response.data); const link = document.createElement("a"); link.href = url; link.download = `offer_${app.application_id}.pdf`; link.click(); URL.revokeObjectURL(url); } catch (error) { tone.value = "danger"; message.value = getErrorMessage(error); } }
</script>

<style scoped>
.application-list { display: grid; gap: 16px; }
.application-card { padding: 20px; }
.application-heading { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
h2 { margin: 0; color: var(--navy); font-size: 19px; }
.muted { color: var(--muted); margin: 5px 0 0; }
.timeline { display: flex; gap: 10px; flex-wrap: wrap; margin: 20px 0; }
.timeline-item { display: grid; gap: 5px; min-width: 130px; border-left: 2px solid var(--border); padding-left: 10px; }
.timeline-item span, .timeline-item p, .detail span { color: var(--muted); font-size: 13px; }
.timeline-item p { margin: 0; max-width: 240px; }
.detail { display: flex; gap: 14px; flex-wrap: wrap; border-top: 1px solid var(--border); padding-top: 12px; }
.offer-detail { justify-content: space-between; align-items: center; }
.offer-detail > div { display: flex; gap: 12px; flex-wrap: wrap; }
@media (max-width: 600px) { .application-heading { display: grid; } }
</style>
