<template>
  <section class="tdx-market-legacy-shell legacy-static-shell">
    <div class="shell-hero">
      <span class="shell-eyebrow">legacy tdx market shell</span>
      <h1 class="shell-title">TDX 行情工作台</h1>
      <p class="shell-copy">
        当前 legacy TDX 行情页未接入可复用的 canonical truth。
        这里不再展示本地伪指数监控、伪实时报价、伪 K 线图表或伪轮询刷新状态。
      </p>
    </div>

    <div class="shell-grid">
      <article class="shell-card">
        <h2>建议改用的 canonical 页面</h2>
        <p>如需查看当前项目里真实可验证的市场数据，请从对应业务路由进入。</p>
        <ul>
          <li>
            <a href="/market/realtime">/market/realtime</a>
            <span>查看已验证的实时行情快照，而不是 legacy TDX 壳层报价。</span>
          </li>
          <li>
            <a href="/market/technical">/market/technical</a>
            <span>查看已验证的 K 线与技术分析页面。</span>
          </li>
          <li>
            <a href="/system/data">/system/data</a>
            <span>查看当前数据源配置，而不是 shell 级连接状态文案。</span>
          </li>
        </ul>
      </article>

      <article class="shell-card">
        <h2>当前边界</h2>
        <ul class="boundary-list">
          <li>不显示 shell 级请求徽记、同步状态、连接状态、响应时间或活跃会话数。</li>
          <li>不伪造指数监控、逐笔报价、买卖盘、K 线图表或轮询刷新成功语义。</li>
          <li>若后续要恢复动态内容，必须先落到新的 verified market contract 或真正的 canonical owner。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
</script>

<style scoped lang="scss">
.tdx-market-legacy-shell {
  min-height: 100vh;
  padding: 48px 24px;
  background:
    radial-gradient(circle at top left, rgb(28 78 122 / 16%), transparent 42%),
    linear-gradient(180deg, #07111c 0%, #0c1724 100%);
  color: #ebf2f9;
}

.shell-hero {
  max-width: 900px;
  margin: 0 auto 32px;
}

.shell-eyebrow {
  display: inline-block;
  margin-bottom: 12px;
  color: #7cb8ec;
  font-size: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.shell-title {
  margin: 0 0 12px;
  font-size: 40px;
  line-height: 1.1;
}

.shell-copy {
  max-width: 760px;
  margin: 0;
  color: #bfd4e8;
  line-height: 1.7;
}

.shell-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.shell-card {
  padding: 24px;
  border: 1px solid rgb(124 184 236 / 20%);
  border-radius: 18px;
  background: rgb(10 18 28 / 78%);
  backdrop-filter: blur(10px);
}

.shell-card h2 {
  margin: 0 0 12px;
  font-size: 18px;
}

.shell-card p,
.shell-card li,
.shell-card span {
  color: #bfd4e8;
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
  color: #8bc8ff;
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
