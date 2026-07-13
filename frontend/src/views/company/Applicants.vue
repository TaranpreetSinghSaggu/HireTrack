<template>
  <PageHeader
    title="Applicants"
    description="Shortlist, reject, schedule interviews, offer, select, or place candidates for this job."
  />
  <AlertMessage :message="message" :tone="tone" />
  <LoadingState v-if="loading" />
  <EmptyState
    v-else-if="!items.length"
    title="No applicants yet"
    description="Applications for this job will appear here."
  />
  <div v-else class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>Candidate</th>
          <th>Profile</th>
          <th>Status</th>
          <th>Action</th>
          <th>Schedule</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.application_id">
          <td>{{ item.student_name }}</td>
          <td>
            <div>
              {{ item.student_branch || "-" }} · CGPA {{ item.student_cgpa || "-" }}
            </div>
            <div class="skills-text">{{ item.student_skills || "" }}</div>
          </td>
          <td><StatusBadge :status="item.status" /></td>
          <td>
            <div class="action-cell">
              <select v-model="item.next" class="input action-select">
                <option value="">Select action</option>
                <option v-for="status in allowed(item.status)" :key="status">
                  {{ status }}
                </option>
              </select>
              <AppButton
                label="Update"
                variant="secondary"
                @click="update(item)"
              />
            </div>
          </td>
          <td>
            <template v-if="item.status === 'Shortlisted'">
              <div class="schedule-form">
                <input
                  v-model="item.interview_date"
                  class="input date-input"
                  type="datetime-local"
                  required
                />
                <input
                  v-model="item.interview_link"
                  class="input link-input"
                  placeholder="Interview link"
                />
                <input
                  v-model="item.interview_venue"
                  class="input venue-input"
                  placeholder="Venue (e.g. Seminar Hall)"
                />
                <AppButton
                  label="Schedule"
                  variant="secondary"
                  @click="schedule(item)"
                />
              </div>
            </template>
            <template v-else>
              <span class="muted">-</span>
            </template>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import PageHeader from "@/components/PageHeader.vue";
import LoadingState from "@/components/LoadingState.vue";
import EmptyState from "@/components/EmptyState.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import AppButton from "@/components/AppButton.vue";
import AlertMessage from "@/components/AlertMessage.vue";
import { companyApi } from "@/services/company";
import { getErrorMessage } from "@/services/http";

const route = useRoute();
const items = ref([]);
const loading = ref(true);
const message = ref("");
const tone = ref("info");

const transitions = {
  Applied: ["Shortlisted", "Rejected"],
  Shortlisted: ["Interview", "Rejected"],
  Interview: ["Offer", "Selected", "Rejected"],
  Offer: ["Placed", "Rejected"],
  Selected: ["Placed", "Rejected"],
};

const allowed = (status) => transitions[status] || [];

onMounted(async () => {
  try {
    const jobId = route.params.id;
    const res = await companyApi.applicants(jobId);
    items.value = res.data.map((item) => ({
      ...item,
      next: "",
      interview_date: "",
      interview_link: "",
      interview_venue: "",
    }));
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  } finally {
    loading.value = false;
  }
});

async function update(item) {
  if (!item.next) return;
  try {
    await companyApi.updateApplication(item.application_id, {
      status: item.next,
    });
    item.status = item.next;
    item.next = "";
    tone.value = "success";
    message.value = `Candidate status updated to ${item.status}.`;
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  }
}

async function schedule(item) {
  if (!item.interview_date) {
    tone.value = "danger";
    message.value = "Interview date is required.";
    return;
  }
  try {
    await companyApi.scheduleInterview(item.application_id, {
      interview_date: new Date(item.interview_date).toISOString(),
      interview_link: item.interview_link || "",
      venue: item.interview_venue || "",
    });
    item.status = "Interview";
    tone.value = "success";
    message.value = "Interview scheduled successfully.";
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  }
}
</script>

<style scoped>
.skills-text {
  font-size: 12px;
  color: var(--muted);
  margin-top: 2px;
}
.action-cell {
  display: flex;
  gap: 6px;
  align-items: center;
}
.action-select {
  min-height: 32px;
  font-size: 12px;
  padding: 4px 8px;
  width: auto;
}
.schedule-form {
  display: grid;
  gap: 6px;
  width: 200px;
}
.schedule-form .input {
  min-height: 32px;
  padding: 4px 8px;
  font-size: 12px;
}
</style>
