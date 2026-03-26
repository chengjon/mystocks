<template>
  <div class="risk-monitor page-enter" :class="{ 'is-embedded': isEmbedded }">
    <section class="placeholder-shell artdeco-card-shell">
      <div class="placeholder-copy">
        <span class="placeholder-eyebrow">risk control route</span>
        <h2 class="placeholder-title">风险监控主面板整理中</h2>
        <p class="placeholder-subtitle">
          当前风险监控能力正在从历史占位实现迁移到统一的 ArtDeco 风险工作台语法，后续会补齐组合暴露、集中度和告警联动主视图。
        </p>
      </div>

      <div class="placeholder-meta">
        <span>MODE: {{ isEmbedded ? 'TRADING CENTER' : 'RISK ROUTE' }}</span>
        <span>STATUS: PLACEHOLDER</span>
      </div>

      <div class="placeholder-grid">
        <article class="placeholder-card">
          <span class="placeholder-card-label">下一步补齐</span>
          <strong class="placeholder-card-value">组合暴露矩阵</strong>
        </article>
        <article class="placeholder-card">
          <span class="placeholder-card-label">下一步补齐</span>
          <strong class="placeholder-card-value">实时风险分布</strong>
        </article>
        <article class="placeholder-card">
          <span class="placeholder-card-label">下一步补齐</span>
          <strong class="placeholder-card-value">控制动作联动</strong>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  functionKey?: string
  userPermissions?: string[]
  systemConfig?: unknown
}

const props = withDefaults(defineProps<Props>(), {
  functionKey: '',
  userPermissions: () => [],
  systemConfig: undefined
})

const isEmbedded = computed(() => Boolean(props.functionKey))
</script>

<style scoped lang="scss">
/*
@import '@/styles/artdeco-quant-extended';
@import '@/styles/data-dense/index';

.risk-monitor {
    min-height: calc(var(--artdeco-spacing-32) * 7 + var(--artdeco-spacing-1));

    .monitor-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--artdeco-spacing-6);

        h2 {
            @include artdeco-gold-accent;

            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-2xl);
            font-weight: 700;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wider);
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-4);

            .risk-level {
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }
    }

    .risk-overview {
        margin-bottom: var(--artdeco-spacing-6);

        .overview-grid {
            display: grid;
            grid-template-columns: repeat(
                auto-fit,
                minmax(calc(var(--artdeco-spacing-20) * 2 + var(--artdeco-spacing-10)), 1fr)
            );
            gap: var(--artdeco-spacing-4);
        }
    }

    .risk-charts-section {
        margin-bottom: var(--artdeco-spacing-6);

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(calc(var(--artdeco-spacing-20) * 5), 1fr));
            gap: var(--artdeco-spacing-6);
        }
    }

    .risk-alerts-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .risk-controls-section {
        .controls-content {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-6);
            padding: var(--artdeco-spacing-4);

            .control-group {
                h4 {
                    @include artdeco-gold-accent;

                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-text-lg);
                    font-weight: 600;
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                }

                .control-items {
                    display: grid;
                    grid-template-columns: repeat(
                        auto-fit,
                        minmax(calc(var(--artdeco-spacing-20) * 3 + var(--artdeco-spacing-5) / 2), 1fr)
                    );
                    gap: var(--artdeco-spacing-4);
                }

                .control-item {
                    display: flex;
                    flex-direction: column;
                    gap: var(--artdeco-spacing-2);

                    .control-label {
                        font-family: var(--artdeco-font-body);
                        font-weight: 500;
                        color: var(--artdeco-fg-primary);
                        font-size: var(--artdeco-text-sm);
                    }
                }
            }

            .control-actions {
                display: flex;
                gap: var(--artdeco-spacing-3);
                justify-content: flex-end;
            }
        }
    }
}

// 风险分布样式
.risk-breakdown {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-4);

    .breakdown-item {
        .source-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-2);

            .source-name {
                font-family: var(--artdeco-font-body);
                font-weight: 500;
                color: var(--artdeco-fg-primary);
                font-size: var(--artdeco-text-sm);
            }

            .source-value {
                font-family: var(--artdeco-font-mono);
                font-weight: 600;
                color: var(--artdeco-gold-primary);
                font-size: var(--artdeco-text-sm);
            }
        }
    }
}

// 持仓集中度样式
.concentration-list {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-4);

    .concentration-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid var(--artdeco-gold-opacity-10);
        border-radius: var(--artdeco-radius-none);

        .position-info {
            display: flex;
            flex-direction: column;

            .position-symbol {
                font-family: var(--artdeco-font-mono);
                font-weight: 600;
                color: var(--artdeco-gold-primary);
                font-size: var(--artdeco-text-sm);
            }

            .position-name {
                font-family: var(--artdeco-font-body);
                color: var(--artdeco-fg-muted);
                font-size: var(--artdeco-text-xs);
                margin-top: calc(var(--artdeco-spacing-1) / 2);
            }
        }

        .position-weight {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            min-width: calc(var(--artdeco-spacing-24) + var(--artdeco-spacing-6));

            .weight-value {
                font-family: var(--artdeco-font-mono);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                font-size: var(--artdeco-text-sm);
                margin-bottom: var(--artdeco-spacing-1);
            }
        }
    }
}

// 告警表格样式
.alert-type-cell {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-2);

    span {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-primary);
    }
}

.alert-value-cell {
    .current-value {
        font-family: var(--artdeco-font-mono);
        font-weight: 600;
        color: var(--artdeco-fg-primary);
        font-size: var(--artdeco-text-sm);
        display: block;
    }

    .threshold-value {
        font-family: var(--artdeco-font-body);
        color: var(--artdeco-fg-muted);
        font-size: var(--artdeco-text-xs);
        margin-top: calc(var(--artdeco-spacing-1) / 2);
    }
}

// 响应式设计（桌面端优先）
@media (width <= calc(var(--artdeco-spacing-32) * 9 + var(--artdeco-spacing-12))) {
    .risk-monitor {
        .overview-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .charts-grid {
            grid-template-columns: 1fr;
        }
    }
}

@media (width <= calc(var(--artdeco-spacing-32) * 6)) {
    .risk-monitor {
        .monitor-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--artdeco-spacing-4);

            .header-actions {
                width: 100%;
                justify-content: space-between;
            }
        }

        .overview-grid {
            grid-template-columns: 1fr;
        }

        .control-items {
            grid-template-columns: 1fr !important;
        }

        .control-actions {
            flex-direction: column;
            align-items: stretch;
        }
    }
}

// 动画效果
.risk-monitor {
    .risk-overview,
    .risk-charts-section,
    .risk-alerts-section,
    .risk-controls-section {
        animation: fade-in-up 0.6s ease-out;
    }

    .risk-overview {
        animation-delay: 0.1s;
    }

    .risk-charts-section {
        animation-delay: 0.2s;
    }

    .risk-alerts-section {
        animation-delay: 0.3s;
    }

    .risk-controls-section {
        animation-delay: 0.4s;
    }
}

@keyframes fade-in-up {
    from {
        opacity: 0%;
        transform: translateY(var(--artdeco-spacing-5));
    }
    to {
        opacity: 100%;
        transform: translateY(0);
    }
}

// 风险指标卡片悬停效果
.overview-grid {
    .artdeco-stat-card {
        transition: all var(--artdeco-transition-base);

        &:hover {
            transform: translateY(calc(var(--artdeco-spacing-1) / -2));
            box-shadow: var(--artdeco-glow-subtle);
        }
    }
}
*/

@use '@/styles/artdeco-tokens.scss' as *;

.risk-monitor {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
}

.placeholder-shell {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.placeholder-copy {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.placeholder-eyebrow,
.placeholder-meta {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-dim);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.placeholder-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
}

.placeholder-title {
  margin: 0;
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-2xl);
  color: var(--artdeco-fg-primary);
}

.placeholder-subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.placeholder-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

.placeholder-card {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-4);
  border: 1px solid var(--artdeco-gold-opacity-10);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 5%, transparent);
}

.placeholder-card-label {
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.placeholder-card-value {
  color: var(--artdeco-gold-primary);
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-lg);
}

@media (width <= 75rem) {
  .placeholder-grid {
    grid-template-columns: 1fr;
  }
}
</style>
