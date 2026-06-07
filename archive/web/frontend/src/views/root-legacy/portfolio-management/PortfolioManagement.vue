<template>
  <section class="portfolio-management-legacy-shell legacy-static-shell">
    <div class="shell-hero">
      <p class="shell-eyebrow">legacy portfolio management shell</p>
      <h1 class="shell-title">投资组合管理工作台</h1>
      <p class="shell-copy">
        当前 legacy 投资组合管理页未接入可复用的 canonical truth。
        这里不再展示本地伪清单指标、伪组合分析、伪告警汇总或伪持仓编辑语义。
      </p>
    </div>

    <div class="shell-grid">
      <article class="shell-card">
        <h2>推荐入口</h2>
        <p>若需要真实已验证的组合、清单与风控真相，请回到这些 canonical 路由：</p>
        <ul>
          <li>
            <a href="/watchlist/manage">/watchlist/manage</a>
            <span>查看已验证的自选清单、清单切换、持仓列表与同步状态。</span>
          </li>
          <li>
            <a href="/trade/portfolio">/trade/portfolio</a>
            <span>查看已验证的组合总览、资产结构与组合统计快照。</span>
          </li>
          <li>
            <a href="/risk/management">/risk/management</a>
            <span>查看已验证的风险中心、告警汇总与止损监控入口。</span>
          </li>
        </ul>
      </article>

      <article class="shell-card">
        <h2>边界说明</h2>
        <ul class="boundary-list">
          <li>不再展示 shell 级评分卡、清单标签页、股票编辑表单或告警统计。</li>
          <li>不再保留本地添加、移除、计算评分、查看详情或再平衡建议等伪交互。</li>
          <li>若后续需要恢复动态组合管理，必须先建立与 canonical owner 对齐的 verified truth contract。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
</script>

<style scoped lang="scss">
.portfolio-management-legacy-shell {
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
