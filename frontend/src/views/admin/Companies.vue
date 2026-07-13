<template>
  <PageHeader
    title="Companies"
    description="Approve, blacklist, unblock, or remove company accounts."
  />
  <AlertMessage :message="message" :tone="tone" />
  <div class="card filters">
    <input v-model="filters.name" class="input" placeholder="Name" /><input
      v-model="filters.industry"
      class="input"
      placeholder="Industry"
    /><select v-model="filters.status" class="input">
      <option value="">All</option>
      <option value="pending">Pending</option>
      <option value="approved">Approved</option>
      <option value="blacklisted">Blacklisted</option></select
    ><AppButton label="Search" icon="search" @click="load" />
  </div>
  <LoadingState v-if="loading" />
  <div v-else class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Company</th>
          <th>Industry</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="c in companies" :key="c.id">
          <td>
            {{ c.name }}<br /><span class="muted">{{ c.location || "-" }}</span>
          </td>
          <td>{{ c.industry || "-" }}</td>
          <td>
            <StatusBadge
              :status="
                c.is_blacklisted
                  ? 'Blacklisted'
                  : c.is_approved
                    ? 'Approved'
                    : 'Pending'
              "
            />
          </td>
          <td>
            <div class="actions">
              <AppButton
                label="Approve"
                variant="secondary"
                :disabled="c.is_approved"
                @click="act(() => adminApi.approveCompany(c.id))"
              /><AppButton
                label="Blacklist"
                variant="secondary"
                @click="act(() => adminApi.blacklistCompany(c.id, true))"
              /><AppButton
                label="Unblock"
                variant="secondary"
                @click="act(() => adminApi.blacklistCompany(c.id, false))"
              /><AppButton
                label="Remove"
                variant="danger"
                @click="act(() => adminApi.removeCompany(c.id))"
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
const filters = reactive({ name: "", industry: "", status: "" });
const companies = ref([]);
const loading = ref(true);
const message = ref("");
const tone = ref("info");
async function load() {
  loading.value = true;
  companies.value = (await adminApi.companies(filters)).data;
  loading.value = false;
}
async function act(fn) {
  try {
    await fn();
    tone.value = "success";
    message.value = "Company record updated.";
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
  grid-template-columns: repeat(4, minmax(0, 1fr));
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
