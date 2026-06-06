<template>
  <section class="risk-orphan-shell legacy-static-shell">
    <p class="shell-eyebrow">legacy risk child page</p>
    <h2>组合风险子页已收口</h2>
    <p>
      该 risk 子页未接入 canonical verified truth，
      不再展示 Phase roadmap 占位、独立组合风险分析入口或未验证风险执行态。
    </p>
    <a href="/risk/management">前往 /risk/management 查看已验证风险管理</a>
  </section>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.risk-orphan-shell {
  display: grid;
  gap: var(--artdeco-spacing-3);
  padding: var(--artdeco-spacing-5);
  border: 1px solid var(--artdeco-border-default);
  color: var(--artdeco-fg-primary);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
}

.shell-eyebrow {
  margin: 0;
  color: var(--artdeco-gold-primary);
  font-size: var(--artdeco-text-xs);
  font-weight: var(--artdeco-font-semibold);
  letter-spacing: var(--artdeco-tracking-widest);
  text-transform: uppercase;
}

h2,
p {
  margin: 0;
}

p {
  max-width: 44rem;
  color: var(--artdeco-fg-muted);
  line-height: 1.7;
}

a {
  color: var(--artdeco-gold-primary);
  font-weight: var(--artdeco-font-semibold);
  text-decoration: none;
}
</style>
