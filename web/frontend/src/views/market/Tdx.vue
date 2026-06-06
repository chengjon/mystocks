<template>
  <section class="tdx-interface-legacy-shell legacy-static-shell">
    <div class="shell-hero">
      <span class="shell-eyebrow">legacy tdx interface shell</span>
      <h1 class="shell-title">TDX 数据接口页</h1>
      <p class="shell-copy">
        当前 legacy TDX 数据接口页未接入可复用的一对一 canonical truth。
        这里不再展示本地模拟连接、随机响应时间、随机会话数、模拟报价或伪 K 线加载状态。
      </p>
    </div>

    <div class="shell-grid">
      <article class="shell-card">
        <h2>建议改用的 canonical 页面</h2>
        <p>如需查看当前项目里真实可验证的市场数据，请从对应业务路由进入。</p>
        <ul>
          <li>
            <a href="/market/realtime">/market/realtime</a>
            <span>查看已验证的实时行情快照。</span>
          </li>
          <li>
            <a href="/market/technical">/market/technical</a>
            <span>查看已验证的 K 线与技术分析页面。</span>
          </li>
          <li>
            <a href="/system/data">/system/data</a>
            <span>查看已验证的数据源配置与数据管理状态。</span>
          </li>
        </ul>
      </article>

      <article class="shell-card">
        <h2>当前边界</h2>
        <ul class="boundary-list">
          <li>不显示 shell 级连接状态、响应时间、活跃会话数、服务器 IP 或刷新成功提示。</li>
          <li>不伪造实时报价、买卖盘、成交量、成交额、K 线图表或时间范围选择器。</li>
          <li>若后续恢复动态 TDX 内容，必须先建立真实 API contract 与 verified market snapshot。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
</script>

<style scoped lang="scss">
.tdx-interface-legacy-shell {
  min-height: 100%;
  padding: 32px;
  color: #f4efe2;
}

.shell-hero,
.shell-card {
  border: 1px solid rgba(212, 175, 55, 0.24);
  border-radius: 20px;
  background:
    linear-gradient(155deg, rgba(18, 24, 38, 0.94), rgba(8, 12, 20, 0.98)),
    radial-gradient(circle at top right, rgba(55, 170, 212, 0.12), transparent 46%);
  box-shadow: 0 16px 42px rgba(0, 0, 0, 0.24);
}

.shell-hero {
  margin-bottom: 22px;
  padding: 28px;
}

.shell-eyebrow {
  display: inline-block;
  margin-bottom: 10px;
  color: #d4af37;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.shell-title {
  margin: 0;
  font-size: 34px;
}

.shell-copy {
  max-width: 800px;
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
  font-weight: 700;
  text-decoration: none;
}

.shell-card a:hover {
  text-decoration: underline;
}

.boundary-list {
  list-style: disc;
}
</style>
