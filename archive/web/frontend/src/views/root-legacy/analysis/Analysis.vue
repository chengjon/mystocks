<template>
  <section class="analysis-legacy-shell legacy-static-shell">
    <div class="shell-hero">
      <span class="shell-eyebrow">legacy analysis shell</span>
      <h1 class="shell-title">分析工作台</h1>
      <p class="shell-copy">
        当前 legacy 分析工作台未接入可复用的 canonical truth。为避免继续展示伪实时分析参数、
        伪信号摘要和伪导出面板，该页面已收口为静态说明壳。
      </p>
    </div>

    <div class="shell-grid">
      <article class="shell-card">
        <h2>已保留的 canonical 入口</h2>
        <p>如需查看当前项目里真实可验证的分析数据，请从对应业务路由进入。</p>
        <ul>
          <li><a href="/detail/graphics/600519">/detail/graphics/600519</a></li>
          <li><a href="/data/indicator">/data/indicator</a></li>
          <li><a href="/ai/sentiment">/ai/sentiment</a></li>
        </ul>
      </article>

      <article class="shell-card">
        <h2>当前边界</h2>
        <ul>
          <li>不展示本地 request provenance、freshness、聚合指标带或导出成功语义。</li>
          <li>不伪造分析参数、技术信号、趋势表格或最近信号列表。</li>
          <li>后续若要恢复动态内容，必须先引入语义匹配的 canonical owner 或新的 verified contract。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<style scoped lang="scss">
@use '@/styles/theme-tokens.scss' as *;

.analysis-legacy-shell {
  min-height: 100vh;
  padding: 48px 24px;
  background:
    radial-gradient(circle at top left, rgb(32 84 132 / 14%), transparent 42%),
    linear-gradient(180deg, #07111d 0%, #0d1724 100%);
  color: #e8eef6;
}

.shell-hero {
  max-width: 880px;
  margin: 0 auto 32px;
}

.shell-eyebrow {
  display: inline-block;
  margin-bottom: 12px;
  color: #8bb8e8;
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
  margin: 0;
  max-width: 720px;
  color: #bed0e2;
  line-height: 1.7;
}

.shell-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  max-width: 880px;
  margin: 0 auto;
}

.shell-card {
  padding: 24px;
  border: 1px solid rgb(139 184 232 / 20%);
  border-radius: 18px;
  background: rgb(10 18 29 / 78%);
  backdrop-filter: blur(10px);
}

.shell-card h2 {
  margin: 0 0 12px;
  font-size: 18px;
}

.shell-card p,
.shell-card li {
  color: #bed0e2;
  line-height: 1.7;
}

.shell-card ul {
  margin: 0;
  padding-left: 18px;
}

.shell-card a {
  color: #8bb8e8;
}
</style>
