<template>
  <div class="monitoring-dashboard legacy-static-shell">
    <section class="shell-card shell-hero">
      <span class="shell-eyebrow">legacy monitoring shell</span>
      <h1 class="shell-title">监控中心</h1>
      <p class="shell-copy">
        当前 legacy 监控大盘未接入可复用的 canonical truth。为避免继续展示伪实时行情、伪告警统计和伪龙虎榜快照，
        该页面已收口为静态说明壳。
      </p>
    </section>

    <section class="shell-card shell-guidance">
      <h2 class="shell-section-title">建议改用的 canonical 页面</h2>
      <div class="guidance-grid">
        <article class="guidance-item">
          <div class="guidance-kicker">实时行情</div>
          <div class="guidance-route">/market/realtime</div>
          <p class="guidance-copy">查看真实行情样本、请求来源和已验证 market snapshot。</p>
        </article>

        <article class="guidance-item">
          <div class="guidance-kicker">风险概览</div>
          <div class="guidance-route">/risk/overview</div>
          <p class="guidance-copy">查看规则、告警和 partial-slice truth，不再混用 legacy 汇总面板。</p>
        </article>

        <article class="guidance-item">
          <div class="guidance-kicker">龙虎榜</div>
          <div class="guidance-route">/market/lhb</div>
          <p class="guidance-copy">查看真实 trade-date selector 和已验证榜单 rows。</p>
        </article>
      </div>
    </section>

    <section class="shell-card shell-notes">
      <h2 class="shell-section-title">当前保留范围</h2>
      <ul class="shell-list">
        <li>保留 legacy 监控页位置信息，避免继续输出假 live summary。</li>
        <li>不再展示伪实时数据、伪告警级别或伪龙虎榜记录。</li>
        <li>后续若要恢复动态能力，必须先绑定明确的 canonical route truth 或新的已验证 contract。</li>
      </ul>
    </section>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.monitoring-dashboard {
  min-height: 100vh;
  padding: var(--artdeco-spacing-6);
  background:
    radial-gradient(circle at top left, color-mix(in srgb, var(--artdeco-gold-primary) 8%, transparent), transparent 36%),
    linear-gradient(180deg, var(--artdeco-bg-global), color-mix(in srgb, var(--artdeco-bg-global) 92%, black));
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.shell-card {
  border: 1px solid var(--artdeco-border-default);
  background: color-mix(in srgb, var(--artdeco-bg-elevated) 94%, transparent);
  box-shadow: 0 var(--artdeco-spacing-2) var(--artdeco-spacing-6)
    color-mix(in srgb, var(--artdeco-bg-global) 82%, transparent);
  padding: var(--artdeco-spacing-6);
}

.shell-eyebrow,
.guidance-kicker {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
  color: var(--artdeco-gold-dim);
}

.shell-title,
.shell-section-title,
.guidance-route {
  margin: 0;
  font-family: var(--artdeco-font-display);
  color: var(--artdeco-fg-primary);
}

.shell-title {
  font-size: var(--artdeco-text-3xl);
}

.shell-section-title {
  font-size: var(--artdeco-text-xl);
}

.shell-copy,
.guidance-copy,
.shell-list {
  margin: 0;
  color: var(--artdeco-fg-muted);
  line-height: var(--artdeco-leading-relaxed);
}

.shell-hero {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-3);
}

.shell-guidance,
.shell-notes {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-4);
}

.guidance-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.guidance-item {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-4);
  border: 1px solid color-mix(in srgb, var(--artdeco-border-default) 88%, transparent);
  background: color-mix(in srgb, var(--artdeco-bg-global) 88%, transparent);
}

.shell-list {
  padding-left: var(--artdeco-spacing-5);
}

@media (width <= 60rem) {
  .guidance-grid {
    grid-template-columns: 1fr;
  }
}

@media (width <= 48rem) {
  .monitoring-dashboard {
    padding: var(--artdeco-spacing-4);
  }

  .shell-card {
    padding: var(--artdeco-spacing-5);
  }
}
</style>
