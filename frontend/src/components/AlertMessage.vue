<template>
  <div v-if="message" class="alert" :class="tone">{{ message }}</div>
</template>

<script setup>
defineProps({
  message: { type: String, default: "" },
  tone: { type: String, default: "info" },
});
</script>

<style scoped>
.alert {
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 12px;
}
.info {
  background: #eff6ff;
  color: #1e3a8a;
}
.success {
  background: #f0fdf4;
  color: #166534;
}
.danger {
  background: #fef2f2;
  color: #991b1b;
}
</style>
