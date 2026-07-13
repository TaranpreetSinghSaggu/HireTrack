<template>
  <PageHeader
    title="Profile"
    description="Keep your personal, academic, skills, resume, and career details current."
  />
  <AlertMessage :message="message" :tone="tone" />
  <LoadingState v-if="loading" />
  <form v-else class="card form-grid profile" @submit.prevent="save">
    <div class="grid grid-2">
      <div v-for="field in fields" :key="field.key" class="field">
        <label>{{ field.label }}</label>
        <textarea
          v-if="field.type === 'textarea'"
          v-model="form[field.key]"
          class="input"
        ></textarea>
        <input
          v-else
          v-model="form[field.key]"
          class="input"
          :type="field.type || 'text'"
        />
      </div>
    </div>
    <div class="card resume">
      <h2>Resume parsing</h2>
      <div class="field">
        <label>Upload PDF</label
        ><input
          class="input"
          type="file"
          accept="application/pdf"
          @change="file = $event.target.files[0]"
        />
      </div>
      <div class="field">
        <label>Or paste resume text</label
        ><textarea v-model="resumeText" class="input"></textarea>
      </div>
      <AppButton
        label="Parse resume"
        icon="file-earmark-text"
        variant="secondary"
        :loading="resumeLoading"
        @click="parseResume"
      />
    </div>
    <AppButton
      label="Save profile"
      icon="check2"
      type="submit"
      :loading="saving"
    />
  </form>
</template>

<script setup>
import { reactive, ref, onMounted } from "vue";
import PageHeader from "@/components/PageHeader.vue";
import AlertMessage from "@/components/AlertMessage.vue";
import LoadingState from "@/components/LoadingState.vue";
import AppButton from "@/components/AppButton.vue";
import { studentApi } from "@/services/student";
import { getErrorMessage } from "@/services/http";

const fields = [
  { key: "name", label: "Name" },
  { key: "contact", label: "Contact" },
  { key: "degree", label: "Degree" },
  { key: "institution", label: "Institution" },
  { key: "branch", label: "Branch" },
  { key: "year", label: "Year", type: "number" },
  { key: "passout_year", label: "Passout year", type: "number" },
  { key: "cgpa", label: "CGPA", type: "number" },
  { key: "skills", label: "Skills", type: "textarea" },
  { key: "experience", label: "Experience", type: "textarea" },
];
const form = reactive({});
const loading = ref(true);
const saving = ref(false);
const resumeLoading = ref(false);
const file = ref(null);
const resumeText = ref("");
const message = ref("");
const tone = ref("info");

onMounted(async () => {
  Object.assign(form, (await studentApi.profile()).data);
  loading.value = false;
});
async function save() {
  saving.value = true;
  try {
    await studentApi.updateProfile(form);
    tone.value = "success";
    message.value = "Profile updated.";
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  } finally {
    saving.value = false;
  }
}
async function parseResume() {
  resumeLoading.value = true;
  try {
    const payload = file.value
      ? new FormData()
      : { resume_text: resumeText.value };
    if (file.value) payload.append("resume", file.value);
    const { data } = await studentApi.uploadResume(payload);
    
    form.name = data.name || form.name;
    form.contact = data.contact || form.contact;
    form.degree = data.degree || form.degree;
    form.institution = data.institution || form.institution;
    form.branch = data.branch || form.branch;
    form.year = data.year || form.year;
    form.passout_year = data.passout_year || form.passout_year;
    form.cgpa = data.cgpa || form.cgpa;
    form.skills = data.skills?.join(", ") || form.skills;
    form.experience = data.experience || form.experience;
    form.resume_filename = data.resume_filename;
    
    tone.value = "success";
    message.value = "Resume parsed. Review extracted details before saving.";
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  } finally {
    resumeLoading.value = false;
  }
}
</script>

<style scoped>
.profile {
  padding: 20px;
}
.resume {
  padding: 16px;
}
h2 {
  margin: 0 0 16px;
  color: var(--navy);
  font-size: 16px;
}
</style>
