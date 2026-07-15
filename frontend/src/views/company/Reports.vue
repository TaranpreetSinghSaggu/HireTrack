<template>
  <PageHeader title="Reports" description="Export application history for your company drives." />
  <AlertMessage :message="message" :tone="tone" />
  <div class="card panel">
    <div><h2>Application export</h2><p class="muted">The CSV is prepared in the background so you can keep working.</p></div>
    <AppButton label="Start export" icon="download" :loading="starting" @click="startExport" />
  </div>
  <div v-if="taskId" class="card task-card">
    <div><strong>Export task</strong><p class="muted">{{ taskStatus }}</p></div>
    <AppButton v-if="taskStatus === 'SUCCESS'" label="Download CSV" icon="file-earmark-arrow-down" @click="download" />
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import AppButton from "@/components/AppButton.vue";
import AlertMessage from "@/components/AlertMessage.vue";
import { companyApi } from "@/services/company";
import { getErrorMessage } from "@/services/http";

const taskId = ref(localStorage.getItem("hiretrack.companyExportTask") || "");
const taskStatus = ref(taskId.value ? "PENDING" : "Not started");
const starting = ref(false); const message = ref(""); const tone = ref("info"); let timer;
async function poll() { if (!taskId.value) return; try { const { data } = await companyApi.taskStatus(taskId.value); taskStatus.value = data.status; if (["PENDING", "STARTED", "RETRY"].includes(data.status)) timer = window.setTimeout(poll, 1800); if (data.status === "FAILURE") { tone.value = "danger"; message.value = "The export could not be completed."; } } catch (error) { tone.value = "danger"; message.value = getErrorMessage(error); } }
async function startExport() { starting.value = true; message.value = ""; try { const { data } = await companyApi.exportApplications(); taskId.value = data.task_id; taskStatus.value = "PENDING"; localStorage.setItem("hiretrack.companyExportTask", taskId.value); poll(); } catch (error) { tone.value = "danger"; message.value = getErrorMessage(error); } finally { starting.value = false; } }
async function download() { try { const response = await companyApi.downloadExport(taskId.value); const url = URL.createObjectURL(response.data); const link = document.createElement("a"); link.href = url; link.download = "hiretrack_company_applications.csv"; link.click(); URL.revokeObjectURL(url); } catch (error) { tone.value = "danger"; message.value = getErrorMessage(error); } }
onMounted(poll); onBeforeUnmount(() => { if (timer) window.clearTimeout(timer); });
</script>

<style scoped>
.panel, .task-card { padding: 20px; display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.panel { margin-bottom: 16px; }
h2 { margin: 0 0 6px; color: var(--navy); }
.muted { color: var(--muted); margin: 0; }
@media (max-width: 600px) { .panel, .task-card { display: grid; } }
</style>
