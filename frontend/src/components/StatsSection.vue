<template>
  <section class="section">
    <h2>Placement Statistics</h2>
    <div class="stats">
      <article class="card">
        <span>Students</span><strong>{{ data.total_students || 0 }}</strong>
      </article>
      <article class="card">
        <span>Companies</span><strong>{{ data.total_companies || 0 }}</strong>
      </article>
      <article class="card">
        <span>Offers</span><strong>{{ offers }}</strong>
      </article>
      <article class="card">
        <span>Placement Rate</span
        ><strong>{{ data.placement_rate || 0 }}%</strong>
      </article>
    </div>
  </section>
</template>
<script setup>
import { computed } from "vue";
const props = defineProps({ data: { type: Object, required: true } });
const offers = computed(
  () =>
    (props.data.application_funnel?.Offer || 0) +
    (props.data.application_funnel?.Selected || 0) +
    (props.data.application_funnel?.Placed || 0),
);
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
.stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 14px;
}
.stats article {
  padding: 18px;
}
.stats span {
  display: block;
  color: var(--muted);
  font-size: 13px;
}
.stats strong {
  display: block;
  margin-top: 5px;
  color: var(--navy);
  font-size: 27px;
}
@media (max-width: 700px) {
  .stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
