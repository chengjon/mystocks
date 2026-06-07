<template>
  <section class="artdeco-technical-orphan-shell legacy-static-shell">
    <p class="shell-eyebrow">legacy artdeco technical page</p>
    <h2>ArtDeco 技术分析页已收口</h2>
    <p>
      该 ArtDeco 页面未接入 canonical verified truth，
      不再展示本地 GPU 状态、计算负载、随机趋势序列、伪回测统计或延迟生成的权益曲线。
    </p>
    <ul>
      <li><a href="/market/technical">前往 /market/technical 查看已验证 K 线分析</a></li>
      <li><a href="/data/indicator">前往 /data/indicator 查看已验证指标分析</a></li>
      <li><a href="/strategy/backtest">前往 /strategy/backtest 查看已验证回测</a></li>
    </ul>
  </section>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.artdeco-technical-orphan-shell {
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
p,
ul {
  margin: 0;
}

p {
  max-width: 48rem;
  color: var(--artdeco-fg-muted);
  line-height: 1.7;
}

ul {
  display: grid;
  gap: var(--artdeco-spacing-2);
  padding-left: var(--artdeco-spacing-4);
}

a {
  color: var(--artdeco-gold-primary);
  font-weight: var(--artdeco-font-semibold);
  text-decoration: none;
}
</style>
