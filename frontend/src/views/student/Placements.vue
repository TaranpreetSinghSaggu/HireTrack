<template>
  <PageHeader
    title="Placement history"
    description="Confirmed selections and placements from your application history."
  />
  <LoadingState v-if="loading" />
  <EmptyState
    v-else-if="!items.length"
    title="No placements yet"
    description="Selected and placed outcomes will be listed here."
  />
  <div v-else class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Company</th>
          <th>Position</th>
          <th>Salary</th>
          <th>Joining</th>
          <th>Remarks</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.placement_id">
          <td>{{ item.company_name }}</td>
          <td>{{ item.position || item.job_title }}</td>
          <td>{{ item.salary || "Not specified" }}</td>
          <td>{{ formatDate(item.joining_date) }}</td>
          <td>{{ item.remarks || "-" }}</td>
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
import { studentApi } from "@/services/student";
const items = ref([]);
const loading = ref(true);
const formatDate = (value) =>
  value ? new Date(value).toLocaleDateString() : "Not set";
onMounted(async () => {
  items.value = (await studentApi.placements()).data;
  loading.value = false;
});
</script>
