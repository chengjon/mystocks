<template>
  <div class="market-analysis page-enter">
    <section class="placeholder-shell artdeco-card-shell">
      <div class="placeholder-copy">
        <span class="placeholder-eyebrow">market breadth route</span>
        <h2 class="placeholder-title">市场分析主面板整理中</h2>
        <p class="placeholder-subtitle">
          当前市场分析能力正在从原始占位实现迁移到统一的 ArtDeco 工作台语法，后续会补齐热度分布、广度指标和市场结构总览。
        </p>
      </div>

      <div class="placeholder-meta">
        <span>MODE: TRADING CENTER</span>
        <span>STATUS: PLACEHOLDER</span>
      </div>

      <div class="placeholder-grid">
        <article class="placeholder-card">
          <span class="placeholder-card-label">下一步补齐</span>
          <strong class="placeholder-card-value">热度分布矩阵</strong>
        </article>
        <article class="placeholder-card">
          <span class="placeholder-card-label">下一步补齐</span>
          <strong class="placeholder-card-value">市场广度指标</strong>
        </article>
        <article class="placeholder-card">
          <span class="placeholder-card-label">下一步补齐</span>
          <strong class="placeholder-card-value">结构总览面板</strong>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.market-analysis {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
}

.placeholder-shell {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.placeholder-copy {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.placeholder-eyebrow,
.placeholder-meta {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-dim);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.placeholder-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
}

.placeholder-title {
  margin: 0;
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-2xl);
  color: var(--artdeco-fg-primary);
}

.placeholder-subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.placeholder-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.placeholder-card {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-gold-opacity-10);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 5%, transparent);
}

.placeholder-card-label {
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.placeholder-card-value {
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-lg);
}

@media (width <= 75rem) {
  .placeholder-grid {
    grid-template-columns: 1fr;
  }
}
</style>
