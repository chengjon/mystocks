<template>
  <section class="market-data-nested-legacy-shell legacy-static-shell">
    <div class="shell-hero">
      <p class="shell-eyebrow">nested legacy market-data shell</p>
      <h1 class="shell-title">市场数据聚合工作台</h1>
      <p class="shell-copy">
        当前 nested legacy 市场数据聚合页未接入可复用的一对一 canonical truth。
        这里不再展示本地实时徽标、秒级时间、返回动作、Tab 聚合面板或组件级直接请求结果。
      </p>
    </div>

    <div class="shell-grid">
      <article class="shell-card">
        <h2>推荐入口</h2>
        <p>若需要真实已验证的市场数据，请回到这些 canonical 路由：</p>
        <ul>
          <li>
            <a href="/market/realtime">/market/realtime</a>
            <span>查看实时行情、行情快照与请求来源。</span>
          </li>
          <li>
            <a href="/market/lhb">/market/lhb</a>
            <span>查看已验证的龙虎榜榜单和交易日期上下文。</span>
          </li>
          <li>
            <a href="/data/fund-flow">/data/fund-flow</a>
            <span>查看已验证的资金流向和市场资金结构。</span>
          </li>
          <li>
            <a href="/data/industry">/data/industry</a>
            <span>查看已验证的行业板块资金动向。</span>
          </li>
        </ul>
      </article>

      <article class="shell-card">
        <h2>边界说明</h2>
        <ul class="boundary-list">
          <li>不显示 shell 级实时徽标、秒级时间、返回动作、Tab、统计卡或旧市场数据表格。</li>
          <li>不再拉起 legacy ETF、chip-race、资金流和 LHB 组件中的直接 axios 请求。</li>
          <li>若后续恢复嵌套市场数据页，必须先建立新的 verified aggregate contract 或一对一 canonical owner。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<style scoped lang="scss">
.market-data-nested-legacy-shell {
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
