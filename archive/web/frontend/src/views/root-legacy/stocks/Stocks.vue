<template>
  <section class="stocks-legacy-shell legacy-static-shell">
    <div class="shell-hero">
      <p class="shell-eyebrow">legacy stocks shell</p>
      <h1 class="shell-title">股票清单工作台</h1>
      <p class="shell-copy">
        当前 legacy 股票清单页未接入可复用的 canonical truth。
        这里不再展示本地伪筛选条、伪股票列表、伪刷新状态或伪分析动作语义。
      </p>
    </div>

    <div class="shell-grid">
      <article class="shell-card">
        <h2>推荐入口</h2>
        <p>若需要真实已验证的股票筛选、行情或详情，请回到这些 canonical 路由：</p>
        <ul>
          <li>
            <a href="/watchlist/screener">/watchlist/screener</a>
            <span>查看已验证的策略选股结果与股票基础数据筛选入口。</span>
          </li>
          <li>
            <a href="/market/realtime">/market/realtime</a>
            <span>查看已验证的实时行情快照，而不是 shell 级列表与刷新文案。</span>
          </li>
          <li>
            <a href="/detail/graphics/600519">/detail/graphics/600519</a>
            <span>查看已验证的个股图形分析与明细视图。</span>
          </li>
        </ul>
      </article>

      <article class="shell-card">
        <h2>边界说明</h2>
        <ul class="boundary-list">
          <li>不再显示 shell 级搜索栏、行业/概念/市场筛选器、分页器或刷新按钮。</li>
          <li>不再伪造股票列表、涨跌幅、成交量、查看详情或分析动作。</li>
          <li>若后续需要恢复动态股票工作台，必须先建立与 canonical owner 对齐的 verified truth contract。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
</script>

<style scoped lang="scss">
.stocks-legacy-shell {
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
