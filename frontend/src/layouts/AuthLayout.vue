<template>
  <main class="auth-shell">
    <section class="auth-panel">
      <div class="brand">
        <span>HT</span>
        <div>
          <strong>HireTrack</strong>
          <p>Campus placement portal</p>
        </div>
      </div>
      <RouterView />
    </section>
  </main>
</template>

<style scoped>
.auth-shell {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 24px;
  background: var(--bg);
}
.auth-panel {
  width: min(480px, 100%);
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #fff;
  padding: 24px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}
.brand {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 24px;
}
.brand span {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border-radius: 6px;
  background: var(--navy);
  color: white;
  font-weight: 700;
}
strong {
  color: var(--navy);
  font-size: 20px;
}
p {
  margin: 0;
  color: var(--muted);
}
</style>
