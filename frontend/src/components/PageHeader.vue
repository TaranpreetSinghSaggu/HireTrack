<template>
  <div class="page-header">
    <div>
      <p v-if="eyebrow" class="eyebrow">{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
      <p v-if="description" class="description">{{ description }}</p>
    </div>
    <div v-if="$slots.actions" class="header-actions">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: "" },
  eyebrow: { type: String, default: "" },
});
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}
.eyebrow {
  margin: 0 0 4px;
  color: var(--muted);
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}
h1 {
  margin: 0;
  color: var(--navy);
  font-size: 24px;
  font-weight: 600;
}
.description {
  max-width: 720px;
  margin: 6px 0 0;
  color: var(--muted);
}
.header-actions {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}
@media (max-width: 767px) {
  .page-header {
    display: grid;
  }
}
</style>
