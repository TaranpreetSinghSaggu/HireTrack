<template>
  <form class="form-grid" @submit.prevent="submit">
    <div>
      <h1>Company registration</h1>
      <p class="muted">Your account will be available after admin approval.</p>
    </div>
    <AlertMessage :message="message" :tone="tone" />
    <div class="field">
      <label>Company name *</label
      ><input v-model="form.name" class="input" required />
    </div>
    <div class="field">
      <label>Email *</label
      ><input v-model="form.email" class="input" type="email" required />
    </div>
    <div class="field">
      <label>Password *</label
      ><input v-model="form.password" class="input" type="password" required />
    </div>
    <div class="field">
      <label>Industry</label><input v-model="form.industry" class="input" />
    </div>
    <div class="field">
      <label>Location</label><input v-model="form.location" class="input" />
    </div>
    <div class="field">
      <label>Website</label><input v-model="form.website" class="input" />
    </div>
    <div class="field">
      <label>HR contact</label><input v-model="form.hr_contact" class="input" />
    </div>
    <AppButton
      label="Submit for approval"
      icon="building-add"
      type="submit"
      :loading="loading"
    />
    <RouterLink to="/login">Back to sign in</RouterLink>
  </form>
</template>

<script setup>
import { reactive, ref } from "vue";
import AppButton from "@/components/AppButton.vue";
import AlertMessage from "@/components/AlertMessage.vue";
import { authApi } from "@/services/auth";
import { getErrorMessage } from "@/services/http";

const form = reactive({
  name: "",
  email: "",
  password: "",
  industry: "",
  location: "",
  website: "",
  hr_contact: "",
});
const loading = ref(false);
const message = ref("");
const tone = ref("info");

async function submit() {
  loading.value = true;
  try {
    await authApi.registerCompany(form);
    tone.value = "success";
    message.value =
      "Registration submitted. The company account is awaiting admin approval.";
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  } finally {
    loading.value = false;
  }
}
</script>
