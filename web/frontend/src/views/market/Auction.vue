<template>
  <section class="market-auction-legacy-shell legacy-static-shell">
    <div class="shell-hero">
      <p class="shell-eyebrow">legacy auction shell</p>
      <h1 class="shell-title">竞价抢筹工作台</h1>
      <p class="shell-copy">
        当前 legacy 竞价抢筹页未接入可复用的一对一 canonical truth。
        这里不再展示本地伪竞价总量、参与股票数、撮合成功率、刷新动作或硬编码样本行。
      </p>
    </div>

    <div class="shell-grid">
      <article class="shell-card">
        <h2>推荐入口</h2>
        <p>若需要真实已验证的市场上下文，请回到这些 canonical 路由：</p>
        <ul>
          <li>
            <a href="/market/realtime">/market/realtime</a>
            <span>查看实时行情、请求来源与行情快照状态。</span>
          </li>
          <li>
            <a href="/market/lhb">/market/lhb</a>
            <span>查看已验证的龙虎榜榜单、交易日期与请求来源。</span>
          </li>
          <li>
            <a href="/data/fund-flow">/data/fund-flow</a>
            <span>查看已验证的资金流向与北向/主力资金数据。</span>
          </li>
        </ul>
      </article>

      <article class="shell-card">
        <h2>边界说明</h2>
        <ul class="boundary-list">
          <li>不显示 shell 级竞价总量、参与股票数、成功率、状态标签或撮合明细。</li>
          <li>不再保留本地刷新按钮、延迟模拟、硬编码股票行或伪实时成功提示。</li>
          <li>若后续恢复竞价抢筹动态页，必须先建立语义匹配的 canonical owner 或 verified contract。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<style scoped lang="scss">
.market-auction-legacy-shell {
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
