<template>
  <section class="market-etf-legacy-shell legacy-static-shell">
    <div class="shell-hero">
      <p class="shell-eyebrow">legacy etf shell</p>
      <h1 class="shell-title">ETF 行情工作台</h1>
      <p class="shell-copy">
        当前 legacy ETF 行情页未接入可复用的一对一 canonical truth。
        这里不再展示本地 ETF 资产规模、产品数量、成交额、涨幅榜、成交榜或硬编码 ETF 样本。
      </p>
    </div>

    <div class="shell-grid">
      <article class="shell-card">
        <h2>推荐入口</h2>
        <p>若需要真实已验证的市场上下文，请回到这些 canonical 路由：</p>
        <ul>
          <li>
            <a href="/market/realtime">/market/realtime</a>
            <span>查看实时行情与已验证行情快照。</span>
          </li>
          <li>
            <a href="/data/industry">/data/industry</a>
            <span>查看已验证的行业资金和板块动向。</span>
          </li>
          <li>
            <a href="/data/fund-flow">/data/fund-flow</a>
            <span>查看已验证的资金流向和市场资金结构。</span>
          </li>
        </ul>
      </article>

      <article class="shell-card">
        <h2>边界说明</h2>
        <ul class="boundary-list">
          <li>不显示 shell 级 ETF 总资产、产品总数、日成交额、平均涨幅或榜单排名。</li>
          <li>不再保留本地自动刷新、手动刷新、分类筛选、搜索排序或硬编码 ETF 行。</li>
          <li>若后续恢复 ETF 动态页，必须先建立语义匹配的 canonical owner 或 verified contract。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<style scoped lang="scss">
.market-etf-legacy-shell {
  display: grid;
  gap: 24px;
  padding: 24px;
  color: #f4efe2;
}

.shell-hero,
.shell-card {
  border: 1px solid rgba(212, 175, 55, 0.24);
  border-radius: 20px;
  background:
    linear-gradient(160deg, rgba(18, 24, 38, 0.94), rgba(8, 12, 20, 0.96)),
    radial-gradient(circle at top right, rgba(212, 175, 55, 0.12), transparent 48%);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.22);
}

.shell-hero {
  padding: 28px;
}

.shell-eyebrow {
  margin: 0 0 10px;
  color: #d4af37;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.shell-title {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
}

.shell-copy {
  max-width: 760px;
  margin: 14px 0 0;
  color: rgba(244, 239, 226, 0.82);
  line-height: 1.7;
}

.shell-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.shell-card {
  padding: 24px;
}

.shell-card h2 {
  margin: 0 0 14px;
  font-size: 18px;
}

.shell-card p,
.shell-card li,
.shell-card span {
  color: rgba(244, 239, 226, 0.8);
  line-height: 1.7;
}

.shell-card ul {
  margin: 0;
  padding-left: 18px;
}

.shell-card li + li {
  margin-top: 10px;
}

.shell-card a {
  color: #f6d774;
  font-weight: 600;
  text-decoration: none;
}

.shell-card a:hover {
  text-decoration: underline;
}

.boundary-list {
  list-style: disc;
}
</style>
