<template>
  <form class="form-grid" @submit.prevent="submit">
    <div>
      <h1>Student registration</h1>
      <p class="muted">
        Create your account, then complete your academic profile.
      </p>
    </div>
    <AlertMessage :message="message" :tone="tone" />
    <div class="field">
      <label>Name *</label><input v-model="form.name" class="input" required />
    </div>
    <div class="field">
      <label>Email *</label
      ><input v-model="form.email" class="input" type="email" required />
    </div>
    <div class="field">
      <label>Password *</label
      ><input v-model="form.password" class="input" type="password" required />
    </div>
    <AppButton
      label="Create student account"
      icon="person-plus"
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

const form = reactive({ name: "", email: "", password: "" });
const loading = ref(false);
const message = ref("");
const tone = ref("info");

async function submit() {
  loading.value = true;
  try {
    await authApi.registerStudent(form);
    tone.value = "success";
    message.value =
      "Registration complete. Sign in to complete your profile, upload your resume, and browse eligible jobs.";
  } catch (error) {
    tone.value = "danger";
    message.value = getErrorMessage(error);
  } finally {
    loading.value = false;
  }
}
</script>
