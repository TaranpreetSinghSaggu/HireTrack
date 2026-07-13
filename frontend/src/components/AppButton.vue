<template>
  <button
    class="app-button"
    :class="variant"
    :disabled="disabled || loading"
    :type="type"
  >
    <i v-if="icon" :class="`bi bi-${icon}`" aria-hidden="true"></i>
    <span>{{ loading ? "Working..." : label }}</span>
  </button>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  variant: { type: String, default: "primary" },
  icon: { type: String, default: "" },
  type: { type: String, default: "button" },
  disabled: Boolean,
  loading: Boolean,
});
</script>

<style scoped>
.app-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: 40px;
  border: 1px solid transparent;
  border-radius: 6px;
  padding: 8px 16px;
  font-weight: 600;
  cursor: pointer;
  transition:
    background 180ms ease,
    border-color 180ms ease;
}
.primary {
  background: var(--blue);
  color: white;
}
.secondary {
  background: white;
  border-color: var(--border);
  color: var(--text);
}
.danger {
  background: var(--danger);
  color: white;
}
.ghost {
  background: transparent;
  color: var(--blue);
}
.app-button:disabled {
  background: #e5e7eb;
  border-color: #e5e7eb;
  color: #6b7280;
  cursor: not-allowed;
}
</style>
