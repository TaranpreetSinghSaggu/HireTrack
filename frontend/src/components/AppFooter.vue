<template>
  <footer id="contact">
    <div class="footer-inner">
      <div>
        <strong>HireTrack</strong>
        <p>Campus Placement Management System</p>
      </div>
      <div>
        <strong>Quick Links</strong><a href="#top">Home</a
        ><a href="#drives">Placement Calendar</a>
      </div>
      <div>
        <strong>Contact</strong>
        <p>Placement Cell · Campus Office</p>
        <p>© 2026 HireTrack</p>
      </div>
    </div>
  </footer>
</template>
<style scoped>
footer {
  border-top: 1px solid var(--border);
  background: #fff;
}
.footer-inner {
  width: min(1060px, calc(100% - 40px));
  margin: auto;
  padding: 28px 0;
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 24px;
  color: var(--muted);
  font-size: 13px;
}
.footer-inner strong {
  display: block;
  color: var(--navy);
  margin-bottom: 7px;
}
.footer-inner p {
  margin: 4px 0;
}
.footer-inner a {
  display: block;
  margin: 4px 0;
  color: var(--text);
}
@media (max-width: 600px) {
  .footer-inner {
    grid-template-columns: 1fr;
    width: calc(100% - 28px);
  }
}
</style>
