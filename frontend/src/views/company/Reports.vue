<template>
  <PageHeader
    title="Reports"
    description="Export company application reports and track task creation."
  />
  <AlertMessage :message="message" :tone="tone" />
  <div class="card panel">
    <p>Generate an application report for your company drives.</p>
    <AppButton
      label="Export applications"
      icon="download"
      :loading="loading"
      @click="exportReport"
    />
  </div>
</template>

<script setup>
import { ref } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import AppButton from "@/components/AppButton.vue";
import AlertMessage from "@/components/AlertMessage.vue";
import { companyApi } from "@/services/company";
import { getErrorMessage } from "@/services/http";
const loading = ref(false);
const message = ref("");
const tone = ref("info");
async function exportReport() {
  loading.value = true;
  try {
    const { data } = await companyApi.exportApplications();
    message.value = `Export started. Task ${data.task_id}`;
    tone.value = "success";
  } catch (error) {
    message.value = getErrorMessage(error);
    tone.value = "danger";
  } finally {
    loading.value = false;
  }
}
</script>
<style scoped>
.panel {
  padding: 20px;
}
</style>
