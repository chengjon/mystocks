<template>
  <section class="realtime-monitor-legacy-shell legacy-static-shell">
    <div class="shell-hero">
      <span class="shell-eyebrow">legacy realtime monitor shell</span>
      <h1 class="shell-title">实时监控旧页</h1>
      <p class="shell-copy">
        当前 legacy 实时监控页未接入可复用的一对一 canonical SSE truth。
        这里不再展示本地长连接面板、推送测试按钮、连接计数或伪运行态。
      </p>
    </div>

    <div class="shell-grid">
      <article class="shell-card">
        <h2>建议改用的 canonical 页面</h2>
        <p>如需查看真实可验证的运行状态，请进入对应业务路由。</p>
        <ul>
          <li>
            <a href="/market/realtime">/market/realtime</a>
            <span>查看已验证的行情实时视图。</span>
          </li>
          <li>
            <a href="/risk/alerts">/risk/alerts</a>
            <span>查看已验证的风险告警列表。</span>
          </li>
          <li>
            <a href="/strategy/backtest">/strategy/backtest</a>
            <span>查看已验证的回测任务与结果状态。</span>
          </li>
        </ul>
      </article>

      <article class="shell-card">
        <h2>当前边界</h2>
        <ul class="boundary-list">
          <li>不挂载本页 SSE 组件、EventSource 连接或后端状态请求。</li>
          <li>不展示训练、回测、告警、仪表盘通道的本地连接计数。</li>
          <li>若后续恢复实时推送工作台，必须先建立 verified SSE contract。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
</script>

<style scoped lang="scss">
.realtime-monitor-legacy-shell {
  display: grid;
  gap: 24px;
  padding: 28px;
}

.shell-hero,
.shell-card {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(8, 18, 32, 0.96), rgba(15, 23, 42, 0.88));
  box-shadow: 0 18px 48px rgba(15, 23, 42, 0.18);
}

.shell-hero {
  padding: 28px;
}

.shell-eyebrow {
  display: inline-flex;
  margin-bottom: 12px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #94a3b8;
  font-size: 12px;
}

.shell-title {
  margin: 0;
  font-size: 28px;
  line-height: 1.2;
  color: #f8fafc;
}

.shell-copy {
  margin: 12px 0 0;
  color: #cbd5e1;
  line-height: 1.7;
  max-width: 72ch;
}

.shell-grid {
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.shell-card {
  padding: 24px;
  color: #e2e8f0;
}

.shell-card h2 {
  margin: 0 0 12px;
  color: #f8fafc;
  font-size: 18px;
}

.shell-card ul {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 12px;
}

.shell-card li {
  display: grid;
  gap: 4px;
}

.shell-card a {
  color: #7dd3fc;
  text-decoration: none;
}

.boundary-list {
  padding-left: 18px;
}
</style>
