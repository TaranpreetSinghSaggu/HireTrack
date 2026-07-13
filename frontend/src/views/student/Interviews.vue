<template>
  <PageHeader
    title="Interviews"
    description="Upcoming and past interviews scheduled by companies."
  />
  <LoadingState v-if="loading" />
  <EmptyState
    v-else-if="!items.length"
    title="No interviews scheduled"
    description="Shortlisted applications with scheduled interviews will appear here."
  />
  <div v-else class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Role</th>
          <th>Company</th>
          <th>Date</th>
          <th>Mode</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.interview_id">
          <td>{{ item.job_title }}</td>
          <td>{{ item.company_name }}</td>
          <td>{{ formatDate(item.interview_date) }}</td>
          <td>{{ item.interview_link || item.venue || "Not specified" }}</td>
          <td><StatusBadge :status="item.application_status" /></td>
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
import StatusBadge from "@/components/StatusBadge.vue";
import { studentApi } from "@/services/student";
const items = ref([]);
const loading = ref(true);
const formatDate = (value) =>
  value ? new Date(value).toLocaleString() : "Not set";
onMounted(async () => {
  items.value = (await studentApi.interviews()).data;
  loading.value = false;
});
</script>
