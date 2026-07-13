<template>
  <section class="section">
    <div class="heading">
      <div>
        <h2>Upcoming Campus Drives</h2>
        <p>
          Approved opportunities currently available through the placement
          portal.
        </p>
      </div>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Company</th>
            <th>Role</th>
            <th>Eligibility</th>
            <th>Deadline</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="!drives.length">
            <td colspan="5" class="empty">No drives match your search.</td>
          </tr>
          <tr v-for="drive in drives" :key="drive.id">
            <td>{{ drive.company }}</td>
            <td>{{ drive.title }}</td>
            <td>CGPA ≥ {{ drive.min_cgpa || "Not specified" }}</td>
            <td>{{ date(drive.application_deadline) }}</td>
            <td><RouterLink class="view" to="/login">View</RouterLink></td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
<script setup>
defineProps({ drives: { type: Array, default: () => [] } });
const date = (value) =>
  value
    ? new Intl.DateTimeFormat("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
      }).format(new Date(value))
    : "To be announced";
</script>
<style scoped>
.section {
  margin: 36px 0 48px;
}
.heading h2 {
  margin: 0;
  color: var(--navy);
  font-size: 19px;
}
.heading p {
  margin: 5px 0 14px;
  color: var(--muted);
}
.view {
  color: var(--blue);
  font-weight: 600;
}
.empty {
  text-align: center;
  color: var(--muted);
  padding: 24px;
}
</style>
