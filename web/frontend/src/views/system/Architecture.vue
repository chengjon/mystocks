<template>
  <section class="architecture-legacy-shell legacy-static-shell">
    <div class="shell-hero">
      <p class="shell-eyebrow">legacy architecture shell</p>
      <h1 class="shell-title">系统架构工作台</h1>
      <p class="shell-copy">
        当前 legacy 架构页未接入可复用的 canonical truth。
        这里不再展示本地伪迁移进度、数据库数量、缓存退役状态或技术栈统计摘要。
      </p>
    </div>

    <div class="shell-grid">
      <article class="shell-card">
        <h2>推荐入口</h2>
        <p>若需要真实已验证的系统运行与配置真相，请回到这些 canonical 路由：</p>
        <ul>
          <li>
            <a href="/system/config">/system/config</a>
            <span>查看已验证的数据源配置、来源统计和系统配置状态。</span>
          </li>
          <li>
            <a href="/system/resources">/system/resources</a>
            <span>查看已验证的运行资源、进程、依赖与资源快照。</span>
          </li>
          <li>
            <a href="/system/health">/system/health</a>
            <span>查看已验证的服务健康、版本、中间件与健康探针状态。</span>
          </li>
        </ul>
      </article>

      <article class="shell-card">
        <h2>边界说明</h2>
        <ul class="boundary-list">
          <li>不显示 shell 级数据库数量、迁移完成度、表数量或缓存退役百分比。</li>
          <li>不再保留本地架构摘要卡、技术栈统计、双数据库拓扑或迁移周报语义。</li>
          <li>若后续要恢复动态架构视图，必须拆回对应 canonical system owners 的 verified truth。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
</script>

<style scoped lang="scss">
.architecture-legacy-shell {
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
