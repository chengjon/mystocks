<template>
  <section class="industry-concept-legacy-shell legacy-static-shell">
    <div class="shell-hero">
      <p class="shell-eyebrow">legacy industry concept shell</p>
      <h1 class="shell-title">行业概念分析工作台</h1>
      <p class="shell-copy">
        当前 legacy 行业概念分析页未接入可复用的 canonical truth。
        这里不再展示本地伪 tab 切换、伪筛选器、伪成分股列表、伪图表或伪导出动作语义。
      </p>
    </div>

    <div class="shell-grid">
      <article class="shell-card">
        <h2>推荐入口</h2>
        <p>若需要真实已验证的行业、概念或资金流向分析，请回到这些 canonical 路由：</p>
        <ul>
          <li>
            <a href="/data/industry">/data/industry</a>
            <span>查看已验证的行业板块资金流与行业级分析快照。</span>
          </li>
          <li>
            <a href="/data/concept">/data/concept</a>
            <span>查看已验证的概念板块资金流、切换状态和概念分析真相。</span>
          </li>
          <li>
            <a href="/data/fund-flow">/data/fund-flow</a>
            <span>查看已验证的资金流向总览，而不是 shell 级图表和导出文案。</span>
          </li>
        </ul>
      </article>

      <article class="shell-card">
        <h2>边界说明</h2>
        <ul class="boundary-list">
          <li>不再显示 shell 级行业/概念 tab、下拉筛选器、统计卡、图表面板、成分股表格或导出按钮。</li>
          <li>不再伪造切换状态、成分股数量、行业图表、概念图表或导出成功语义。</li>
          <li>若后续需要恢复动态行业概念工作台，必须先建立与 canonical owner 对齐的 verified truth contract。</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
</script>

<style scoped lang="scss">
.industry-concept-legacy-shell {
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
