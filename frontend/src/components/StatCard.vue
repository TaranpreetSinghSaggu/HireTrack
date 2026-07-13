<template>
  <div class="card stat-card">
    <div class="icon"><i :class="`bi bi-${icon}`"></i></div>
    <div>
      <p>{{ label }}</p>
      <strong>{{ value }}</strong>
    </div>
  </div>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: [String, Number], default: 0 },
  icon: { type: String, default: "bar-chart" },
});
</script>

<style scoped>
.stat-card {
  display: flex;
  gap: 16px;
  align-items: center;
  padding: 20px;
}
.icon {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 6px;
  background: #e0ecff;
  color: var(--blue);
  font-size: 18px;
}
p {
  margin: 0;
  color: var(--muted);
  font-size: 12px;
  font-weight: 600;
}
strong {
  color: var(--navy);
  font-size: 24px;
}
</style>
