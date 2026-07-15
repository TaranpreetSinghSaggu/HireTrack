<template>
  <PageHeader
    title="Drives review"
    description="Approve pending jobs or reject unsupported drives."
  />
  <AlertMessage :message="message" :tone="tone" />
  <div class="card filters">
    <select v-model="filters.status" class="input">
      <option value="">All statuses</option>
      <option>Pending</option>
      <option>Approved</option>
      <option>Closed</option>
    </select>
    <AppButton label="Filter" icon="search" @click="load" />
  </div>
  <LoadingState v-if="loading" />
  <div v-else class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Drive</th>
          <th>Company</th>
          <th>Eligibility</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="job in jobs" :key="job.id">
          <td>
            {{ job.title }}<br /><span class="muted"
              >{{ job.location || "-" }} · {{ job.salary || "-" }}</span
            >
          </td>
          <td>{{ job.company_name || "-" }}</td>
          <td>
            CGPA {{ job.min_cgpa || "-" }} · Year {{ job.eligible_year || "-"
            }}<br />{{ job.skills_required || "" }}
          </td>
          <td><StatusBadge :status="job.status" /></td>
          <td>
            <div class="actions">
              <AppButton
                label="Approve"
                variant="secondary"
                :disabled="job.status !== 'Pending'"
                @click="act(() => adminApi.approveJob(job.id))"
              /><AppButton
                label="Reject"
                variant="danger"
                @click="act(() => adminApi.rejectJob(job.id))"
              />
            </div>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import LoadingState from "@/components/LoadingState.vue";
import AppButton from "@/components/AppButton.vue";
import AlertMessage from "@/components/AlertMessage.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import { adminApi } from "@/services/admin";
import { getErrorMessage } from "@/services/http";
const filters = reactive({ status: "" });
const jobs = ref([]);
const loading = ref(true);
const message = ref("");
const tone = ref("info");
async function load() {
  loading.value = true;
  jobs.value = (await adminApi.jobs(filters)).data;
  loading.value = false;
}
async function act(fn) {
  try {
    await fn();
    tone.value = "success";
    message.value = "Drive updated.";
    await load();
  } catch (e) {
    tone.value = "danger";
    message.value = getErrorMessage(e);
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
