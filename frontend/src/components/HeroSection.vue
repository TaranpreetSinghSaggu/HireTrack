<template>
  <section id="top" class="hero">
    <p class="brand">HireTrack</p>
    <h1>Campus Placement Management System</h1>
    <p>
      Helping students connect with campus opportunities through a centralized
      placement portal.
    </p>
    <div class="actions">
      <RouterLink to="/login">Student Login</RouterLink
      ><RouterLink to="/login">Company Login</RouterLink
      ><RouterLink to="/login">Admin Login</RouterLink>
    </div>
  </section>
</template>
<style scoped>
.hero {
  max-width: 900px;
  margin: 0 auto;
  padding: 78px 20px 64px;
  text-align: center;
}
.brand {
  margin: 0 0 16px;
  color: var(--navy);
  font-size: 32px;
  font-weight: 750;
  letter-spacing: -0.04em;
}
.hero h1 {
  margin: 0;
  color: var(--navy);
  font-size: 34px;
  line-height: 1.2;
}
.hero p:not(.brand) {
  max-width: 600px;
  margin: 16px auto 0;
  color: var(--muted);
  font-size: 16px;
}
.actions {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 26px;
}
.actions a {
  border: 1px solid var(--navy);
  border-radius: 5px;
  padding: 9px 15px;
  color: var(--navy);
  font-weight: 600;
}
.actions a:first-child {
  background: var(--navy);
  color: #fff;
}
@media (max-width: 560px) {
  .hero {
    padding: 56px 20px;
  }
  .brand {
    font-size: 28px;
  }
  .hero h1 {
    font-size: 27px;
  }
}
</style>
