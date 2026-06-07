<template>
  <main class="not-found-page" aria-labelledby="not-found-title">
    <section class="error-card">
      <div class="error-content">
        <p class="error-eyebrow">ROUTE FALLBACK</p>
        <p class="error-code">404</p>
        <h1 id="not-found-title" class="error-title">页面未找到</h1>
        <p class="error-description">
          当前地址未映射到有效页面。请返回首页，继续进入交易室或其他已审核路由。
        </p>
        <button class="button" type="button" @click="goHome">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            :stroke="'currentColor'"
            stroke-width="2"
            aria-hidden="true"
          >
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9,22 9,12 15,12 15,22"></polyline>
          </svg>
          返回首页
        </button>
      </div>

      <div class="error-illustration" aria-hidden="true">
        <svg width="200" height="200" viewBox="0 0 24 24" fill="none" :stroke="'var(--artdeco-gold-dim)'" stroke-width="1">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      </div>
    </section>
  </main>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { HOME_ROUTE_PATH } from '@/router/homeRoute'

const router = useRouter()

const goHome = () => {
  router.push(HOME_ROUTE_PATH)
}
</script>

<style scoped lang="scss">
.not-found-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: var(--artdeco-spacing-8);
  background:
    radial-gradient(circle at top, rgb(212 175 55 / 10%), transparent 30%),
    repeating-linear-gradient(
      45deg,
      transparent 0,
      transparent 14px,
      rgb(212 175 55 / 4%) 14px,
      rgb(212 175 55 / 4%) 15px
    ),
    var(--artdeco-bg-global);
}

.error-card {
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(10rem, 14rem);
  gap: var(--artdeco-spacing-8);
  align-items: center;
  width: min(100%, 54rem);
  padding: var(--artdeco-spacing-8);
  border: 1px solid var(--artdeco-border-accent);
  background:
    linear-gradient(180deg, rgb(20 20 20 / 96%), rgb(10 10 10 / 94%)),
    var(--artdeco-bg-card);
  box-shadow:
    0 0 0 1px rgb(212 175 55 / 10%) inset,
    0 28px 60px rgb(0 0 0 / 45%),
    0 0 24px rgb(212 175 55 / 10%);
}

.error-content {
  display: grid;
  gap: var(--artdeco-spacing-4);
}

.error-eyebrow {
  margin: 0;
  color: var(--artdeco-gold-light);
  font-family: var(--font-mono);
  font-size: var(--artdeco-text-xs);
  letter-spacing: var(--artdeco-tracking-widest);
  text-transform: uppercase;
}

.error-code {
  margin: 0;
  color: var(--artdeco-gold-primary);
  font-family: var(--font-display);
  font-size: clamp(4.5rem, 12vw, 7.5rem);
  line-height: 0.92;
  letter-spacing: 0.12em;
}

.error-title {
  margin: 0;
  color: var(--artdeco-fg-primary);
  font-family: var(--font-display);
  font-size: clamp(1.625rem, 3vw, 2.25rem);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
}

.error-description {
  margin: 0;
  max-width: 34rem;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-base);
  line-height: var(--artdeco-leading-relaxed);
}

.button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--artdeco-spacing-2);
  min-height: 3rem;
  width: fit-content;
  padding: 0 var(--artdeco-spacing-6);
  border: 1px solid var(--artdeco-gold-primary);
  background: linear-gradient(90deg, var(--artdeco-gold-primary), var(--artdeco-gold-light));
  color: var(--artdeco-bg-global);
  font-family: var(--font-display);
  font-size: var(--artdeco-text-sm);
  font-weight: var(--artdeco-font-semibold);
  letter-spacing: var(--artdeco-tracking-wider);
  text-transform: uppercase;
  cursor: pointer;
  transition:
    transform var(--artdeco-transition-quick) ease,
    box-shadow var(--artdeco-transition-quick) ease,
    filter var(--artdeco-transition-quick) ease;
}

.button:hover {
  transform: translateY(-1px);
  box-shadow: 0 0 20px rgb(212 175 55 / 24%);
  filter: brightness(1.03);
}

.button:focus-visible {
  outline: none;
  box-shadow: 0 0 0 3px rgb(212 175 55 / 18%);
}

.error-illustration {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 14rem;
  border: 1px solid var(--artdeco-border-default);
  background: linear-gradient(180deg, rgb(212 175 55 / 7%), rgb(212 175 55 / 2%));
}

@media (width <= 1024px) {
  .error-card {
    grid-template-columns: 1fr;
  }

  .error-illustration {
    order: -1;
    min-height: 11rem;
  }
}

@media (width <= 768px) {
  .not-found-page {
    padding: var(--artdeco-spacing-5);
  }

  .error-card {
    gap: var(--artdeco-spacing-6);
    padding: var(--artdeco-spacing-6);
  }

  .error-content {
    text-align: center;
    justify-items: center;
  }

  .button {
    width: 100%;
  }
}

@media (width <= 390px) {
  .not-found-page {
    padding: var(--artdeco-spacing-4);
  }

  .error-card {
    padding: var(--artdeco-spacing-5);
  }
}
</style>
