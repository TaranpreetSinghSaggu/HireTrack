<template>
  <section class="section">
    <h2>Quick Access</h2>
    <div class="quick-grid">
      <a
        v-for="item in items"
        :key="item.label"
        :href="item.href"
        class="quick card"
        ><i :class="`bi bi-${item.icon}`" /><span>{{ item.label }}</span
        ><i class="bi bi-arrow-right"
      /></a>
    </div>
  </section>
</template>
<script setup>
const items = [
  { label: "Browse Companies", icon: "building", href: "#drives" },
  { label: "Placement Calendar", icon: "calendar3", href: "#drives" },
  { label: "Eligibility Rules", icon: "book", href: "#drives" },
  { label: "FAQs", icon: "question-circle", href: "#contact" },
];
</script>
<style scoped>
.section {
  margin: 36px 0;
}
.section h2 {
  margin: 0 0 14px;
  color: var(--navy);
  font-size: 19px;
}
.quick-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
.quick {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px;
  color: var(--text);
  font-weight: 600;
}
.quick i:first-child {
  color: var(--blue);
  font-size: 18px;
}
.quick i:last-child {
  margin-left: auto;
  color: var(--muted);
}
.quick:hover {
  border-color: #aebed1;
  background: #fbfdff;
}
@media (max-width: 760px) {
  .quick-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 440px) {
  .quick-grid {
    grid-template-columns: 1fr;
  }
}
</style>
