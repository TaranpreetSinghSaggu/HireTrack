<template>
  <form class="form-grid" @submit.prevent="submit">
    <div>
      <h1>Sign in</h1>
      <p class="muted">Use your student, company, or admin account.</p>
    </div>
    <AlertMessage :message="error" tone="danger" />
    <div class="field">
      <label>Email *</label
      ><input v-model="form.email" class="input" type="email" required />
    </div>
    <div class="field">
      <label>Password *</label
      ><input v-model="form.password" class="input" type="password" required />
    </div>
    <AppButton
      label="Sign in"
      icon="box-arrow-in-right"
      type="submit"
      :loading="auth.loading"
    />
    <div class="links">
      <RouterLink to="/register/student">Student registration</RouterLink>
      <RouterLink to="/register/company">Company registration</RouterLink>
    </div>
  </form>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRouter } from "vue-router";
import AppButton from "@/components/AppButton.vue";
import AlertMessage from "@/components/AlertMessage.vue";
import { useAuthStore } from "@/stores/auth";
import { getErrorMessage } from "@/services/http";

const router = useRouter();
const auth = useAuthStore();
const error = ref("");
const form = reactive({ email: "", password: "" });

async function submit() {
  error.value = "";
  try {
    await auth.login(form);
    router.push(auth.homeRoute);
  } catch (err) {
    error.value = getErrorMessage(err);
  }
}
</script>

<style scoped>
h1 {
  margin: 0;
  color: var(--navy);
}
.links {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
a {
  color: var(--blue);
  font-weight: 600;
}
</style>
