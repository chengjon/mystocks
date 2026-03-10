<template>
  <div class="app-container">
    <section
      v-if="isChecking"
      class="app-readiness-shell app-readiness-shell--checking"
      data-testid="app-readiness-checking"
    >
      <div class="app-readiness-card">
        <p class="app-readiness-eyebrow">System Readiness</p>
        <h1>正在检查后端就绪状态</h1>
        <p>{{ readinessMessage }}</p>
      </div>
    </section>

    <section
      v-else-if="hasBlockingReadinessError"
      class="app-readiness-shell app-readiness-shell--error"
      data-testid="app-readiness-error"
    >
      <div class="app-readiness-card">
        <p class="app-readiness-eyebrow">Backend Unavailable</p>
        <h1>后端暂未就绪</h1>
        <p>{{ readinessMessage }}</p>
        <p v-if="requestId" class="app-readiness-request-id">Request ID: {{ requestId }}</p>
        <button class="app-readiness-action" type="button" @click="checkBackendReadiness">
          重试检查
        </button>
      </div>
    </section>

    <section v-else class="app-shell" data-readiness-state="ready">
      <div v-if="usingMockFallback" class="app-readiness-banner">
        <span>{{ readinessMessage }}</span>
        <span v-if="requestId" class="app-readiness-banner__request-id">Request ID: {{ requestId }}</span>
      </div>
      <router-view />
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

import { useBackendReadiness } from '@/composables/useBackendReadiness'

const {
  readinessMessage,
  requestId,
  usingMockFallback,
  isChecking,
  hasBlockingReadinessError,
  checkBackendReadiness
} = useBackendReadiness()

onMounted(() => {
  void checkBackendReadiness()
})
</script>

<style lang="scss">
@import '@/styles/artdeco-tokens.scss';

.app-container {
  min-height: 100vh;
  background: var(--artdeco-bg-global);
  color: var(--artdeco-fg-primary);
}

.app-shell {
  min-height: 100vh;
}

.app-readiness-shell {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 32px;
}

.app-readiness-card {
  width: min(560px, 100%);
  padding: 32px;
  border: 1px solid var(--artdeco-border-primary);
  border-radius: 20px;
  background: rgba(8, 15, 28, 0.92);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.32);
}

.app-readiness-eyebrow {
  margin: 0 0 12px;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--artdeco-accent-primary);
}

.app-readiness-card h1 {
  margin: 0 0 12px;
  font-size: 28px;
  line-height: 1.2;
}

.app-readiness-card p {
  margin: 0;
  color: var(--artdeco-fg-secondary);
}

.app-readiness-request-id,
.app-readiness-banner__request-id {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  font-size: 12px;
}

.app-readiness-action {
  margin-top: 20px;
  padding: 10px 16px;
  border: 1px solid var(--artdeco-accent-primary);
  border-radius: 999px;
  background: transparent;
  color: var(--artdeco-fg-primary);
  cursor: pointer;
}

.app-readiness-action:hover {
  background: rgba(91, 143, 249, 0.12);
}

.app-readiness-banner {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--artdeco-border-primary);
  background: rgba(181, 126, 14, 0.14);
  color: var(--artdeco-fg-primary);
}
</style>
