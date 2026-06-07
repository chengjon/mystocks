<template>
  <section class="task-management-legacy-shell legacy-static-shell">
    <div class="shell-hero">
      <p class="shell-eyebrow">legacy task management shell</p>
      <h1 class="shell-title">任务管理工作台</h1>
      <p class="shell-copy">
        当前 legacy 任务管理页未接入可复用的 canonical truth。
        这里不再展示本地伪任务统计、伪任务列表或伪导入导出语义。
      </p>
    </div>

    <div class="shell-grid">
      <article class="shell-card">
        <h2>推荐入口</h2>
        <p>若需要真实已验证的交易、策略与系统运行真相，请回到这些 canonical 路由：</p>
        <ul>
          <li>
            <a href="/strategy/backtest">/strategy/backtest</a>
            <span>查看已验证的回测任务、执行状态与结果报告。</span>
          </li>
          <li>
            <a href="/trade/terminal">/trade/terminal</a>
            <span>查看已验证的交易运行态、风控反馈与终端工作台。</span>
          </li>
          <li>
            <a href="/system/health">/system/health</a>
            <span>查看已验证的系统健康、版本、中间件与探针状态。</span>
          </li>
        </ul>
      </article>

      <article class="shell-card">
        <h2>边界说明</h2>
        <ul class="boundary-list">
          <li>不显示 shell 级任务总数、运行中数量、今日执行或成功率统计。</li>
          <li>不再保留本地任务表格、导入导出按钮、历史弹窗或任务编辑表单。</li>
          <li>若后续需要恢复动态任务管理，必须先建立对应 canonical owner 的 verified truth contract。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
</script>

<style scoped lang="scss">
.task-management-legacy-shell {
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
