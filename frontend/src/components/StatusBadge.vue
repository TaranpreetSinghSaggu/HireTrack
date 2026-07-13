<template>
  <span class="badge" :class="tone">{{ text }}</span>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  status: { type: [String, Boolean], default: "" },
});

const text = computed(() => {
  if (typeof props.status === "boolean")
    return props.status ? "Approved" : "Pending";
  return props.status || "Unknown";
});

const tone = computed(() => {
  const value = String(text.value).toLowerCase();
  if (
    ["approved", "active", "placed", "selected", "offer", "success"].includes(
      value,
    )
  )
    return "success";
  if (["shortlisted", "interview"].includes(value)) return "info";
  if (["pending", "applied", "closed"].includes(value)) return "neutral";
  if (["rejected", "blocked", "blacklisted", "danger"].includes(value))
    return "danger";
  return "neutral";
});
</script>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 600;
}
.success {
  background: #dcfce7;
  color: #166534;
}
.info {
  background: #dbeafe;
  color: #1d4ed8;
}
.neutral {
  background: #f3f4f6;
  color: #374151;
}
.danger {
  background: #fee2e2;
  color: #991b1b;
}
</style>
