<template>
  <div>
    <div class="progress-label">
      <span>{{ label }}</span>
      <strong>{{ value }}%</strong>
    </div>
    <div class="track">
      <div class="bar" :style="{ width: `${value}%` }"></div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, default: "Progress" },
  value: { type: Number, default: 0 },
});
</script>

<style scoped>
.progress-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-weight: 600;
}
.track {
  height: 8px;
  overflow: hidden;
  border-radius: 4px;
  background: #e5e7eb;
}
.bar {
  height: 100%;
  background: var(--blue);
}
</style>
