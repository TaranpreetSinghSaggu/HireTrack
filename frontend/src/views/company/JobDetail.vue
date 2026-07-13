<template>
  <PageHeader
    :title="job.title || 'Job detail'"
    description="Approval status, talent-market insight, and job actions."
  />
  <AlertMessage :message="message" :tone="tone" />
  <LoadingState v-if="loading" />
  
  <section v-else class="grid grid-2">
    <!-- Inline Edit Form (Only visible when isEditing is true) -->
    <div v-if="isEditing" class="card panel">
      <h2>Edit Job Details</h2>
      <form @submit.prevent="saveJob" class="form-grid">
        <div class="field">
          <label>Title *</label>
          <input v-model="editForm.title" class="input" required />
        </div>
        <div class="field">
          <label>Description *</label>
          <textarea v-model="editForm.description" class="input" required />
        </div>
        <div class="text-fields-grid">
          <div class="field">
            <label>Salary</label>
            <input v-model="editForm.salary" class="input" />
          </div>
          <div class="field">
            <label>Location</label>
            <input v-model="editForm.location" class="input" />
          </div>
        </div>
        <div class="field">
          <label>Benefits</label>
          <textarea v-model="editForm.benefits" class="input" />
        </div>
        <div class="text-fields-grid">
          <div class="field">
            <label>Skills Required</label>
            <input v-model="editForm.skills_required" class="input" />
          </div>
          <div class="field">
            <label>Experience Required</label>
            <input v-model="editForm.experience_required" class="input" />
          </div>
        </div>
        <div class="text-fields-grid">
          <div class="field">
            <label>Minimum CGPA</label>
            <input v-model="editForm.min_cgpa" class="input" type="number" step="0.01" />
          </div>
          <div class="field">
            <label>Eligible Year</label>
            <input v-model="editForm.eligible_year" class="input" type="number" />
          </div>
        </div>
        <div class="field">
          <label>Eligible Branches</label>
          <input v-model="editForm.eligible_branches" class="input" />
        </div>
        <div class="field">
          <label>Application Deadline *</label>
          <input v-model="editForm.application_deadline" class="input" type="datetime-local" required />
        </div>
        <div class="actions mt-3">
          <AppButton label="Save Changes" type="submit" :loading="saving" />
          <AppButton label="Cancel" variant="secondary" @click="isEditing = false" />
        </div>
      </form>
    </div>

    <!-- Job Info Card (Visible by default) -->
    <div v-else class="card panel">
      <StatusBadge :status="job.status" />
      <p class="description">{{ job.description }}</p>
      <dl>
        <dt>Package</dt>
        <dd>{{ job.salary || "-" }}</dd>
        <dt>Deadline</dt>
        <dd>{{ formatDate(job.application_deadline) }}</dd>
        <dt>Skills</dt>
        <dd>{{ job.skills_required || "-" }}</dd>
      </dl>
      <div class="actions">
        <RouterLink :to="`/company/jobs/${job.id}/applicants`"
          ><AppButton label="Review applicants" icon="people" /></RouterLink
        >
        <AppButton
          v-if="job.status === 'Pending'"
          label="Edit job"
          icon="pencil"
          variant="secondary"
          @click="startEdit"
        />
        <AppButton
          label="Close job"
          icon="x-circle"
          variant="danger"
          :disabled="job.status !== 'Approved'"
          @click="closeJob"
        />
      </div>
    </div>

    <!-- Talent Market Card -->
    <div class="card panel">
      <h2>Talent market</h2>
      <p class="insight">{{ market.insight || "No insight available yet." }}</p>
      <ProfileProgress
        :value="market.match_percentage || 0"
        label="Matching students"
      />
    </div>
  </section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import PageHeader from "@/components/PageHeader.vue";
import LoadingState from "@/components/LoadingState.vue";
import StatusBadge from "@/components/StatusBadge.vue";
import AppButton from "@/components/AppButton.vue";
import AlertMessage from "@/components/AlertMessage.vue";
import ProfileProgress from "@/components/ProfileProgress.vue";
import { companyApi } from "@/services/company";
import { getErrorMessage } from "@/services/http";

const route = useRoute();
const job = ref({});
const market = ref({});
const loading = ref(true);
const isEditing = ref(false);
const saving = ref(false);
const editForm = ref({});
const message = ref("");
const tone = ref("info");

const formatDate = (value) =>
  value ? new Date(value).toLocaleString() : "Not set";

onMounted(async () => {
  const id = route.params.id;
  try {
    const jobs = (await companyApi.jobs()).data;
    job.value = jobs.find((item) => String(item.id) === String(id)) || {};
    market.value = (await companyApi.marketInsight(id)).data;
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  } finally {
    loading.value = false;
  }
});

function startEdit() {
  editForm.value = {
    title: job.value.title || "",
    description: job.value.description || "",
    salary: job.value.salary || "",
    benefits: job.value.benefits || "",
    location: job.value.location || "",
    skills_required: job.value.skills_required || "",
    experience_required: job.value.experience_required || "",
    min_cgpa: job.value.min_cgpa !== null && job.value.min_cgpa !== undefined ? job.value.min_cgpa : "",
    eligible_year: job.value.eligible_year !== null && job.value.eligible_year !== undefined ? job.value.eligible_year : "",
    eligible_branches: job.value.eligible_branches || "",
    application_deadline: job.value.application_deadline
      ? new Date(job.value.application_deadline).toISOString().substring(0, 16)
      : ""
  };
  isEditing.value = true;
}

async function saveJob() {
  saving.value = true;
  message.value = "";
  try {
    const payload = {
      title: editForm.value.title,
      description: editForm.value.description,
      salary: editForm.value.salary || null,
      benefits: editForm.value.benefits || null,
      location: editForm.value.location || null,
      skills_required: editForm.value.skills_required || null,
      experience_required: editForm.value.experience_required || null,
      min_cgpa: editForm.value.min_cgpa !== "" ? parseFloat(editForm.value.min_cgpa) : null,
      eligible_year: editForm.value.eligible_year !== "" ? parseInt(editForm.value.eligible_year) : null,
      eligible_branches: editForm.value.eligible_branches || null,
      application_deadline: new Date(editForm.value.application_deadline).toISOString(),
    };
    await companyApi.updateJob(job.value.id, payload);
    tone.value = "success";
    message.value = "Job updated successfully.";
    isEditing.value = false;
    
    // Reload job details
    const id = route.params.id;
    const jobs = (await companyApi.jobs()).data;
    job.value = jobs.find((item) => String(item.id) === String(id)) || {};
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  } finally {
    saving.value = false;
  }
}

async function closeJob() {
  try {
    await companyApi.closeJob(job.value.id);
    job.value.status = "Closed";
    tone.value = "success";
    message.value = "Job closed.";
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  }
}
</script>

<style scoped>
.panel {
  padding: 20px;
}
.description {
  margin: 16px 0;
  line-height: 1.6;
}
h2 {
  margin: 0 0 12px;
  color: var(--navy);
}
dl {
  display: grid;
  grid-template-columns: 100px 1fr;
  gap: 8px 12px;
  margin-bottom: 20px;
}
dt {
  color: var(--muted);
  font-weight: 600;
}
dd {
  margin: 0;
}
.insight {
  margin-bottom: 20px;
  line-height: 1.6;
}
.text-fields-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
@media (max-width: 600px) {
  .text-fields-grid {
    grid-template-columns: 1fr;
  }
}
.mt-3 {
  margin-top: 16px;
}
</style>
