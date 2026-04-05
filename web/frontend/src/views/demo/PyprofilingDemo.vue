<template>
  <div class="pyprofiling-demo">

    <div class="page-header">
      <h1 class="page-title">PyProfiling</h1>
      <p class="page-subtitle">ML PREDICTION | PERFORMANCE ANALYSIS | FEATURE ENGINEERING</p>
      <div class="decorative-line"></div>
    </div>

    <div class="card main-card">
      <div class="tabs-container">
        <button
          v-for="(tab, _idx) in tabs"
          :key="tab.key"
          class="tab-button"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span class="tab-label">{{ tab.label }}</span>
        </button>
      </div>

      <div class="tab-content">
        <component :is="currentComponent" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, defineAsyncComponent } from 'vue'
import { TABS } from './pyprofiling/config'

const Overview = defineAsyncComponent(() => import('./pyprofiling/components/Overview.vue'))
const Prediction = defineAsyncComponent(() => import('./pyprofiling/components/Prediction.vue'))
const Features = defineAsyncComponent(() => import('./pyprofiling/components/Features.vue'))
const Profiling = defineAsyncComponent(() => import('./pyprofiling/components/Profiling.vue'))
const Data = defineAsyncComponent(() => import('./pyprofiling/components/Data.vue'))
const API = defineAsyncComponent(() => import('./pyprofiling/components/API.vue'))
const Tech = defineAsyncComponent(() => import('./pyprofiling/components/Tech.vue'))

const activeTab = ref('overview')
const tabs = TABS

const componentMap: Record<string, unknown> = {
  overview: Overview,
  prediction: Prediction,
  features: Features,
  profiling: Profiling,
  data: Data,
  api: API,
  tech: Tech
}

const currentComponent = computed(() => {
  return componentMap[activeTab.value] || Overview
})
</script>

<style scoped lang="scss">
@use '../../styles/artdeco-tokens.scss' as *;

.pyprofiling-demo {
  min-height: 100vh;
  padding: var(--artdeco-spacing-6);
  position: relative;
  background: var(--artdeco-bg-global);
  background-image:
    linear-gradient(180deg, color-mix(in srgb, var(--artdeco-gold-primary) 6%, transparent), transparent 40%),
    repeating-linear-gradient(
      45deg,
      transparent,
      transparent var(--artdeco-spacing-5),
      var(--artdeco-gold-opacity-05) var(--artdeco-spacing-5),
      var(--artdeco-gold-opacity-05) calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-px))
    );
}

.page-header,
.main-card {
  position: relative;
  z-index: 1;
}

.page-header {
  text-align: center;
  margin-bottom: var(--artdeco-spacing-8);

  .page-title {
    margin: 0 0 var(--artdeco-spacing-2) 0;
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-size: var(--artdeco-text-3xl);
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: var(--artdeco-tracking-widest);
    text-transform: uppercase;
  }

  .page-subtitle {
    margin: 0;
    color: var(--artdeco-fg-muted);
    font-family: var(--artdeco-font-body, var(--font-body));
    font-size: var(--artdeco-text-xs);
    letter-spacing: var(--artdeco-tracking-wider);
    text-transform: uppercase;
  }

  .decorative-line {
    width: calc(var(--artdeco-spacing-20) * 2);
    height: calc(var(--artdeco-spacing-px) * 2);
    margin: var(--artdeco-spacing-5) auto 0;
    position: relative;
    background: linear-gradient(90deg, transparent, var(--artdeco-gold-primary), transparent);

    &::before {
      content: '';
      position: absolute;
      bottom: calc(var(--artdeco-spacing-2) * -1);
      left: 50%;
      transform: translateX(-50%);
      width: calc(var(--artdeco-spacing-20) - var(--artdeco-spacing-5));
      height: var(--artdeco-spacing-px);
      background: linear-gradient(90deg, transparent, color-mix(in srgb, var(--artdeco-gold-primary) 50%, transparent), transparent);
    }
  }
}

.main-card {
  padding: var(--artdeco-spacing-5);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-none);
  box-shadow: var(--artdeco-shadow-md);

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: var(--artdeco-spacing-4);
    height: var(--artdeco-spacing-4);
    border: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-gold-primary);
  }

  &::before {
    top: var(--artdeco-spacing-3);
    left: var(--artdeco-spacing-3);
    border-right: none;
    border-bottom: none;
  }

  &::after {
    right: var(--artdeco-spacing-3);
    bottom: var(--artdeco-spacing-3);
    border-top: none;
    border-left: none;
  }
}

.tabs-container {
  display: flex;
  gap: var(--artdeco-spacing-1);
  margin-bottom: var(--artdeco-spacing-5);
  padding-bottom: var(--artdeco-spacing-5);
  border-bottom: 1px solid var(--artdeco-gold-dim);
  flex-wrap: wrap;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-5);
  background: transparent;
  border: 1px solid var(--artdeco-gold-dim);
  color: var(--artdeco-fg-muted);
  font-family: var(--artdeco-font-heading, var(--font-display));
  font-size: var(--artdeco-text-xs);
  text-transform: uppercase;
  letter-spacing: var(--artdeco-spacing-px);
  cursor: pointer;
  border-radius: var(--artdeco-radius-none);
  transition:
    color var(--artdeco-transition-quick) var(--artdeco-ease-out),
    border-color var(--artdeco-transition-quick) var(--artdeco-ease-out),
    background var(--artdeco-transition-quick) var(--artdeco-ease-out);

  .tab-icon {
    font-size: var(--artdeco-text-sm);
  }

  &:hover {
    color: var(--artdeco-gold-primary);
    border-color: var(--artdeco-gold-primary);
    background: color-mix(in srgb, var(--artdeco-gold-primary) 5%, transparent);
  }

  &.active {
    color: var(--artdeco-bg-global);
    background: var(--artdeco-gold-primary);
    border-color: var(--artdeco-gold-primary);
  }
}

.tab-content {
  position: relative;
  z-index: 1;
}

@media (width <= 48rem) {
  .pyprofiling-demo {
    padding: var(--artdeco-spacing-4);
  }

  .page-header {
    .page-title {
      font-size: var(--artdeco-text-2xl);
      letter-spacing: calc(var(--artdeco-spacing-px) * 2);
    }

    .page-subtitle {
      font-size: calc(var(--artdeco-text-xs) - var(--artdeco-spacing-px));
      letter-spacing: calc(var(--artdeco-spacing-px) * 2);
    }
  }

  .main-card {
    padding: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
  }

  .tabs-container {
    flex-direction: column;

    .tab-button {
      width: 100%;
      justify-content: center;
    }
  }
}
</style>
