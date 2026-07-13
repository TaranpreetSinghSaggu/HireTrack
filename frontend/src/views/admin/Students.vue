<template>
  <PageHeader
    title="Students"
    description="Search students and manage account access where supported."
  />
  <AlertMessage :message="message" :tone="tone" />
  <div class="card filters">
    <input v-model="filters.name" class="input" placeholder="Name" /><input
      v-model="filters.contact"
      class="input"
      placeholder="Contact"
    /><AppButton label="Search" icon="search" @click="load" />
  </div>
  <LoadingState v-if="loading" />
  <div v-else class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Name</th>
          <th>Academic</th>
          <th>Skills</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="s in students" :key="s.id">
          <td>
            {{ s.name }}<br /><span class="muted">{{ s.contact }}</span>
          </td>
          <td>
            {{ s.degree || "-" }} · {{ s.branch || "-" }} · CGPA
            {{ s.cgpa || "-" }}
          </td>
          <td>{{ s.skills || "-" }}</td>
          <td>
            <div class="actions">
              <AppButton
                :label="s.status === 'blocked' ? 'Unblock' : 'Block'"
                variant="secondary"
                @click="setStatus(s, s.status === 'blocked' ? 'active' : 'blocked')"
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
import { adminApi } from "@/services/admin";
import { getErrorMessage } from "@/services/http";
const filters = reactive({ name: "", contact: "" });
const students = ref([]);
const loading = ref(true);
const message = ref("");
const tone = ref("info");
async function load() {
  loading.value = true;
  students.value = (await adminApi.students(filters)).data;
  loading.value = false;
}
async function setStatus(student, status) {
  try {
    await adminApi.setUserStatus(student.user_id, status);
    message.value = `Student ${status}.`;
    tone.value = "success";
    await load();
  } catch (e) {
    message.value = getErrorMessage(e);
    tone.value = "danger";
  }
}
onMounted(load);
</script>
<style scoped>
.filters {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
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
