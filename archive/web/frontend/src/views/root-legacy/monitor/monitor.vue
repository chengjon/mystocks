<template>
  <section class="monitor-legacy-shell legacy-static-shell">
    <div class="shell-hero">
      <span class="shell-eyebrow">legacy system monitor shell</span>
      <h1 class="shell-title">系统监控旧页</h1>
      <p class="shell-copy">
        当前 legacy 系统监控页未接入可复用的一对一 canonical truth。
        这里不再展示本地运行控制、服务聚合、历史记录或伪连接数。
      </p>
    </div>

    <div class="shell-grid">
      <article class="shell-card">
        <h2>建议改用的 canonical 页面</h2>
        <p>如需查看真实可验证的运行状态，请进入对应业务路由。</p>
        <ul>
          <li>
            <a href="/system/health">/system/health</a>
            <span>查看已验证的服务健康探针与状态矩阵。</span>
          </li>
          <li>
            <a href="/system/resources">/system/resources</a>
            <span>查看已验证的资源观测与待处理项。</span>
          </li>
          <li>
            <a href="/trade/terminal">/trade/terminal</a>
            <span>查看已验证的交易运行态与操作入口。</span>
          </li>
        </ul>
      </article>

      <article class="shell-card">
        <h2>当前边界</h2>
        <ul class="boundary-list">
          <li>不显示刷新控制、动态运行明细或本地状态卡。</li>
          <li>不伪造任何底层服务的本地检查结果。</li>
          <li>若后续恢复动态监控能力，必须先建立 verified monitoring contract。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
</script>

<style scoped lang="scss">
.monitor-legacy-shell {
  display: grid;
  gap: 24px;
  padding: 28px;
}

.shell-hero,
.shell-card {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.96), rgba(15, 23, 42, 0.88));
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
