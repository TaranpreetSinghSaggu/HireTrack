<template>
  <PageHeader
    title="Applications"
    description="Track status, interviews, rejection analysis, and export your application history."
  >
    <template #actions
      ><AppButton
        label="Export"
        icon="download"
        variant="secondary"
        :loading="exporting"
        @click="startExport"
    /></template>
  </PageHeader>
  <AlertMessage :message="message" :tone="tone" />
  <LoadingState v-if="loading" />
  <EmptyState
    v-else-if="!apps.length"
    title="No applications yet"
    description="Browse eligible jobs to start applying."
  />
  <div v-else class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Role</th>
          <th>Company</th>
          <th>Status</th>
          <th>Interview</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="app in apps" :key="app.application_id">
          <td>{{ app.job_title }}</td>
          <td>{{ app.company_name }}</td>
          <td><StatusBadge :status="app.status" /></td>
          <td>
            {{
              app.interview
                ? formatDate(app.interview.interview_date)
                : "Not scheduled"
            }}
          </td>
        </tr>
      </tbody>
    </table>
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

const apps = ref([]);
const loading = ref(true);
const exporting = ref(false);
const message = ref("");
const tone = ref("info");
const formatDate = (value) =>
  value ? new Date(value).toLocaleString() : "Not set";
onMounted(async () => {
  apps.value = (await studentApi.applications()).data;
  loading.value = false;
});
async function startExport() {
  exporting.value = true;
  try {
    const { data } = await studentApi.exportApplications();
    message.value = `Export started. Task ${data.task_id}`;
    tone.value = "success";
  } catch (error) {
    message.value = getErrorMessage(error);
    tone.value = "danger";
  } finally {
    exporting.value = false;
  }
}
</script>

<style scoped>
</style>
