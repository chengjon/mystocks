<script setup lang="ts">
import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
import ArtDecoIcon from '@/components/artdeco/core/ArtDecoIcon.vue'

const emit = defineEmits<{
  openStockModal: []
}>()
</script>

<template>
  <div
    id="risk-panel-stock"
    class="tab-panel"
    role="tabpanel"
    aria-labelledby="risk-tab-stock"
  >
    <ArtDecoCard>
      <template #header>
        <div class="card-header-custom">
          <div class="card-title-custom">
            <span class="title-bar"></span>
            个股风险分析
          </div>
          <ArtDecoButton variant="solid" size="sm" @click="emit('openStockModal')">
            <template #icon>
              <ArtDecoIcon name="plus" />
            </template>
            选择股票
          </ArtDecoButton>
        </div>
      </template>
      <div class="stock-selector">
        <p class="hint-text">选择持仓股票查看详细风险分析</p>
      </div>
    </ArtDecoCard>
  </div>
</template>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.tab-panel {
  animation: fade-in 0.3s ease;
}

@keyframes fade-in {
  from {
    opacity: 0%;
    transform: translateY(calc(var(--artdeco-spacing-2) + (var(--artdeco-spacing-px) * 2)));
  }

  to {
    opacity: 100%;
    transform: translateY(0);
  }
}

.card-header-custom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--artdeco-spacing-4);
  padding-bottom: var(--artdeco-spacing-3);
  border-bottom: 1px solid var(--artdeco-gold-opacity-10);
}

.card-title-custom {
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-base);
  color: var(--artdeco-gold-light);
  display: flex;
  align-items: center;
  gap: var(--artdeco-spacing-2);

  .title-bar {
    width: calc(var(--artdeco-spacing-px) * 4);
    height: calc(var(--artdeco-spacing-4) + (var(--artdeco-spacing-px) * 2));
    background: var(--artdeco-gold-primary);
    border-radius: var(--artdeco-radius-sm);
  }
}

.hint-text {
  color: var(--artdeco-fg-muted);
  font-style: italic;
}
</style>
