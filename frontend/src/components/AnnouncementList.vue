<template>
  <section id="about" class="announcement card">
    <div>
      <h2>Placement Announcements</h2>
      <ul>
        <li v-for="item in announcements" :key="item.title">
          <span>{{ item.title }}</span
          ><time>{{ item.date }}</time>
        </li>
      </ul>
    </div>
    <a href="#drives">View drives <i class="bi bi-arrow-right" /></a>
  </section>
</template>
<script setup>
const announcements = [
  {
    title: "Placement registration is open for eligible students",
    date: "Current semester",
  },
  {
    title: "Resume review sessions are available through the placement cell",
    date: "This week",
  },
  {
    title: "Check upcoming campus drives before applying",
    date: "Updated regularly",
  },
];
</script>
<style scoped>
.announcement {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  margin-bottom: 24px;
  padding: 20px 22px;
}
.announcement h2 {
  margin: 0 0 10px;
  color: var(--navy);
  font-size: 17px;
}
.announcement ul {
  margin: 0;
  padding-left: 18px;
}
.announcement li {
  padding: 4px 0;
}
.announcement time {
  margin-left: 12px;
  color: var(--muted);
  font-size: 12px;
}
.announcement > a {
  align-self: center;
  white-space: nowrap;
  color: var(--blue);
  font-weight: 600;
}
@media (max-width: 600px) {
  .announcement {
    display: block;
  }
  .announcement > a {
    display: inline-block;
    margin-top: 14px;
  }
  .announcement time {
    display: block;
    margin-left: 0;
  }
}
</style>
