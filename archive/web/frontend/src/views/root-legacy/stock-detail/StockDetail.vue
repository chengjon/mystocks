<template>
  <section class="stock-detail-legacy-shell legacy-static-shell">
    <div class="shell-hero">
      <p class="shell-eyebrow">legacy stock detail shell</p>
      <h1 class="shell-title">个股详情工作台</h1>
      <p class="shell-copy">
        当前 legacy 个股详情页未接入一对一可复用的 canonical truth。
        这里不再展示本地伪价格、技术指标、交易摘要或交易操作面板。
      </p>
    </div>

    <div class="shell-grid">
      <article class="shell-card">
        <h2>推荐入口</h2>
        <p>若需要真实已验证的个股详情，请回到这些 canonical 路由：</p>
        <ul>
          <li>
            <a href="/detail/graphics/600519">/detail/graphics/600519</a>
            <span>查看已验证的 K 线趋势、技术指标和行情图形快照</span>
          </li>
          <li>
            <a href="/detail/news/600519">/detail/news/600519</a>
            <span>查看已验证的公告、统计卡和辅助规则快照</span>
          </li>
          <li>
            <a href="/trade/positions">/trade/positions</a>
            <span>查看 canonical 持仓与交易上下文，而不是 legacy 壳层操作面板</span>
          </li>
        </ul>
      </article>

      <article class="shell-card">
        <h2>边界说明</h2>
        <ul class="boundary-list">
          <li>不显示 shell 级行情价格、技术指标、交易摘要或交易执行状态。</li>
          <li>不再保留本地伪图表、胜率、Sharpe、回撤或交易下单控件。</li>
          <li>若后续要恢复动态内容，必须拆回对应 canonical detail / trade owners 的 verified truth。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
</script>

<style scoped lang="scss">
.stock-detail-legacy-shell {
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
