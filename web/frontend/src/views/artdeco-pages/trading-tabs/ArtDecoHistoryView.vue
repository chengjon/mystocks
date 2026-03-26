<template>
  <div class="history-view page-enter">
    <section class="placeholder-shell artdeco-card-shell">
      <div class="placeholder-copy">
        <span class="placeholder-eyebrow">history review route</span>
        <h3 class="placeholder-title">历史复盘主面板整理中</h3>
        <p class="placeholder-subtitle">
          当前历史复盘能力正在从旧占位实现迁移到统一的 ArtDeco 工作台语法，后续会补齐成交流水、盈亏分析和详情抽屉。
        </p>
      </div>

      <div class="placeholder-meta">
        <span>MODE: TRADING CENTER</span>
        <span>STATUS: PLACEHOLDER</span>
      </div>

      <div class="placeholder-grid">
        <article class="placeholder-card">
          <span class="placeholder-card-label">下一步补齐</span>
          <strong class="placeholder-card-value">成交流水表</strong>
        </article>
        <article class="placeholder-card">
          <span class="placeholder-card-label">下一步补齐</span>
          <strong class="placeholder-card-value">盈亏分析区</strong>
        </article>
        <article class="placeholder-card">
          <span class="placeholder-card-label">下一步补齐</span>
          <strong class="placeholder-card-value">详情抽屉</strong>
        </article>
      </div>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.history-view {
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
