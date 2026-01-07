<template>
  <div class="not-found-page">

    <div class="card error-card">
      <div class="error-content">
        <div class="error-code">404</div>
        <div class="error-title">页面未找到</div>
        <div class="error-description">
          抱歉，您访问的页面不存在或已被移除
        </div>
        <button class="button" @click="goHome">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
            <polyline points="9,22 9,12 15,12 15,22"></polyline>
          </svg>
          返回首页
        </button>
      </div>

      <div class="error-illustration">
        <svg width="200" height="200" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-muted)'" stroke-width="1">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const goHome = () => {
  router.push('/')
}
</script>

<style scoped lang="scss">

.not-found-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  background-image: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(212, 175, 55, 0.02) 10px, rgba(212, 175, 55, 0.02) 11px);
  padding: 20px;
}

  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.04;
  background-image:
    repeating-linear-gradient(45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px),
    repeating-linear-gradient(-45deg, var(--gold-primary) 0px, var(--gold-primary) 1px, transparent 1px, transparent 10px);
}

.error-card {
  position: relative;
  z-index: 1;
  display: flex;
  gap: 60px;
  align-items: center;
  padding: 60px;
  max-width: 800px;
  width: 100%;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    border: 3px solid var(--gold-primary);
  }

  &::before {
    top: 16px;
    left: 16px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 16px;
    right: 16px;
    border-left: none;
    border-top: none;
  }
}

.error-content {
  flex: 1;

  .error-code {
    font-family: var(--font-display);
    font-size: 120px;
    font-weight: 700;
    color: var(--gold-primary);
    line-height: 1;
    margin-bottom: 20px;
    text-transform: uppercase;
    letter-spacing: 10px;
  }

  .error-title {
    font-family: var(--font-display);
    font-size: 32px;
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: 3px;
    margin-bottom: 16px;
    font-weight: 600;
  }

  .error-description {
    font-family: var(--font-body);
    font-size: 16px;
    color: var(--text-muted);
    line-height: 1.6;
    margin-bottom: 40px;
  }

  .button {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    padding: 14px 32px;
    background: var(--gold-primary);
    color: var(--bg-primary);
    border: none;
    font-family: var(--font-display);
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 2px;
    cursor: pointer;
    border-radius: 0;
    transition: all 0.3s ease;

    &:hover {
      background: var(--gold-muted);
      box-shadow: 0 0 20px rgba(212, 175, 55, 0.4);
      transform: translateY(-2px);
    }
  }
}

.error-illustration {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 200px;
  height: 200px;
  background: rgba(212, 175, 55, 0.05);
  border: 1px solid var(--gold-dim);
  position: relative;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 12px;
    height: 12px;
    border: 2px solid var(--gold-primary);
  }

  &::before {
    top: 10px;
    left: 10px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 10px;
    right: 10px;
    border-left: none;
    border-top: none;
  }
}

@media (max-width: 768px) {
  .error-card {
    flex-direction: column;
    gap: 40px;
    padding: 30px;

    .error-content {
      text-align: center;

      .error-code {
        font-size: 80px;
        letter-spacing: 5px;
      }

      .error-title {
        font-size: 24px;
        letter-spacing: 2px;
      }

      .error-description {
        font-size: 14px;
      }

      .button {
        width: 100%;
        justify-content: center;
      }
    }
  }

  .error-illustration {
    width: 150px;
    height: 150px;
  }
}
</style>
