<template>
  <PageHeader
    title="Placement history"
    description="Confirmed placements only. Offers remain in your application timeline until they are placed."
  />
  <AlertMessage :message="message" tone="danger" />
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
          <th>Documents</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.placement_id">
          <td>{{ item.company_name }}</td>
          <td>{{ item.position || item.job_title }}</td>
          <td>{{ item.salary || "Not specified" }}</td>
          <td>{{ formatDate(item.joining_date) }}</td>
          <td>{{ item.remarks || "-" }}</td>
          <td><AppButton v-if="item.offer_letter" label="Offer letter" icon="download" variant="secondary" @click="downloadOffer(item)" /></td>
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
import AlertMessage from "@/components/AlertMessage.vue";
import { studentApi } from "@/services/student";
import { getErrorMessage } from "@/services/http";
const items = ref([]);
const loading = ref(true);
const message = ref("");
const formatDate = (value) =>
  value ? new Date(value).toLocaleDateString() : "Not set";
onMounted(async () => {
  items.value = (await studentApi.placements()).data;
  loading.value = false;
});
async function downloadOffer(item) {
  try {
    const response = await studentApi.offerLetter(item.application_id);
    const url = URL.createObjectURL(response.data);
    const link = document.createElement("a"); link.href = url; link.download = `offer_${item.application_id}.pdf`; link.click(); URL.revokeObjectURL(url);
  } catch (error) { message.value = getErrorMessage(error); }
}
</script>
