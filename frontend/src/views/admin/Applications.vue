<template>
  <PageHeader
    title="Applications report"
    description="Filter application status and review campus placement pipeline records."
  >
    <template #actions><AppButton label="Export PDF" icon="file-earmark-pdf" variant="secondary" :loading="exporting" @click="exportPdf" /></template>
  </PageHeader>
  <div class="card filters">
    <select v-model="filters.status" class="input">
      <option value="">All statuses</option>
      <option>Applied</option>
      <option>Shortlisted</option>
      <option>Interview</option>
      <option>Offer</option>
      <option>Selected</option>
      <option>Placed</option>
      <option>Rejected</option></select
    /><AppButton label="Filter" icon="search" @click="load" />
  </div>
  <LoadingState v-if="loading" />
  <div v-else class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Student</th>
          <th>Role</th>
          <th>Company</th>
          <th>Status</th>
          <th>Date</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="app in apps" :key="app.application_id">
          <td>{{ app.student_name }}</td>
          <td>{{ app.job_title }}</td>
          <td>{{ app.company_name }}</td>
          <td><StatusBadge :status="app.status" /></td>
          <td>{{ formatDate(app.application_date) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import LoadingState from "@/components/LoadingState.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import AppButton from "@/components/AppButton.vue";
import { adminApi } from "@/services/admin";
const filters = reactive({ status: "" });
const apps = ref([]);
const loading = ref(true);
const exporting = ref(false);
const formatDate = (value) =>
  value ? new Date(value).toLocaleString() : "Not set";
async function load() {
  loading.value = true;
  apps.value = (await adminApi.applications(filters)).data;
  loading.value = false;
}
async function exportPdf() {
  exporting.value = true;
  try {
    const response = await adminApi.exportPdf();
    const url = URL.createObjectURL(new Blob([response.data], { type: "application/pdf" }));
    const link = document.createElement("a");
    link.href = url;
    link.download = "hiretrack_admin_report.pdf";
    link.click();
    URL.revokeObjectURL(url);
  } finally {
    exporting.value = false;
  }
}
onMounted(load);
</script>
<style scoped>
.filters {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  margin-bottom: 20px;
  padding: 16px;
}
@media (max-width: 991px) {
  .filters {
    grid-template-columns: 1fr;
  }
}
</style>
