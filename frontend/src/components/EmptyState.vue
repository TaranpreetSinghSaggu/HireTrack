<template>
  <div class="card empty">
    <h2>{{ title }}</h2>
    <p>{{ description }}</p>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: "Nothing here yet" },
  description: {
    type: String,
    default: "Once records are available, they will appear here.",
  },
});
</script>

<style scoped>
.empty {
  padding: 32px;
  text-align: center;
}
h2 {
  margin: 0;
  color: var(--navy);
  font-size: 20px;
}
p {
  margin: 8px auto 20px;
  max-width: 420px;
  color: var(--muted);
}
</style>
