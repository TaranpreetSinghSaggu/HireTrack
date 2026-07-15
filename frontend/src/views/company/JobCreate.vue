<template>
  <PageHeader
    title="Create job"
    description="Submit a complete role for admin approval."
  />
  <AlertMessage :message="message" :tone="tone" />
  <form class="card form-grid wizard" @submit.prevent="submit">
    <h2>{{ steps[step] }}</h2>
    <div v-if="step === 0" class="form-grid">
      <div class="field">
        <label>Role *</label
        ><input v-model="form.title" class="input" required />
      </div>
      <div class="field">
        <label>Description *</label
        ><textarea v-model="form.description" class="input" required />
      </div>
    </div>
    <div v-if="step === 1" class="form-grid">
      <div class="field">
        <label>Package</label><input v-model="form.salary" class="input" />
      </div>
      <div class="field">
        <label>Benefits</label
        ><textarea v-model="form.benefits" class="input" />
      </div>
      <div class="field">
        <label>Location</label><input v-model="form.location" class="input" />
      </div>
    </div>
    <div v-if="step === 2" class="grid grid-2">
      <div class="field">
        <label>Minimum CGPA</label
        ><input
          v-model="form.min_cgpa"
          class="input"
          type="number"
          step="0.01"
        />
      </div>
      <div class="field">
        <label>Eligible year</label
        ><input v-model="form.eligible_year" class="input" type="number" />
      </div>
      <div class="field">
        <label>Branches</label
        ><input v-model="form.eligible_branches" class="input" />
      </div>
      <div class="field">
        <label>Skills</label
        ><input v-model="form.skills_required" class="input" />
      </div>
      <div class="field">
        <label>Experience</label
        ><input v-model="form.experience_required" class="input" />
      </div>
    </div>
    <div v-if="step === 3" class="field">
      <label>Application deadline *</label
      ><input
        v-model="form.application_deadline"
        class="input"
        type="datetime-local"
        required
      />
    </div>
    <div v-if="step === 4" class="review">
      <p v-for="(value, key) in form" :key="key">
        <strong>{{ key }}:</strong> {{ value || "-" }}
      </p>
    </div>
    <div class="actions">
      <AppButton
        v-if="step"
        label="Back"
        variant="secondary"
        @click="step--"
      /><AppButton
        v-if="step < steps.length - 1"
        label="Next"
        icon="arrow-right"
        @click="step++"
      /><AppButton
        v-else
        label="Submit for approval"
        icon="send"
        type="submit"
        :loading="loading"
      />
    </div>
  </form>
</template>

<script setup>
import { reactive, ref } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import AppButton from "@/components/AppButton.vue";
import AlertMessage from "@/components/AlertMessage.vue";
import { companyApi } from "@/services/company";
import { getErrorMessage } from "@/services/http";
const steps = [
  "Role and description",
  "Package and location",
  "Eligibility and skills",
  "Deadline",
  "Review",
];
const step = ref(0);
const loading = ref(false);
const message = ref("");
const tone = ref("info");
const form = reactive({
  title: "",
  description: "",
  salary: "",
  benefits: "",
  location: "",
  min_cgpa: "",
  eligible_year: "",
  eligible_branches: "",
  skills_required: "",
  experience_required: "",
  application_deadline: "",
});
async function submit() {
  loading.value = true;
  try {
    await companyApi.createJob({
      ...form,
      application_deadline: new Date(form.application_deadline).toISOString(),
    });
    tone.value = "success";
    message.value = "Job submitted for admin approval.";
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.wizard {
  padding: 20px;
}
h2 {
  margin: 0;
  color: var(--navy);
  font-size: 20px;
}
.review p {
  margin: 0 0 8px;
}
</style>
