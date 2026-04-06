<template>
  <SystemDataSourceCanonicalPage v-bind="attrs" />
</template>

<script setup lang="ts">
import { useAttrs } from 'vue'
import SystemDataSourceCanonicalPage from '@/views/system/DataSource.vue'

const attrs = useAttrs()
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.data-management {
  padding: var(--artdeco-spacing-6);
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-6);
}

.data-management.is-embedded {
  padding: 0;
}

.hero-shell,
.stats-strip,
.content-shell,
.embedded-shell {
  width: 100%;
}

.hero-shell,
.content-shell {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-5);
}

.hero-rail,
.content-shell-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--artdeco-spacing-4);
  flex-wrap: wrap;
}

.hero-copy,
.content-shell-copy {
  display: flex;
  flex-direction: column;
  gap: var(--artdeco-spacing-2);
}

.hero-eyebrow,
.content-shell-kicker {
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-gold-dim);
  letter-spacing: var(--artdeco-tracking-wide);
  text-transform: uppercase;
}

.hero-meta,
.content-shell-meta {
  display: flex;
  gap: var(--artdeco-spacing-3);
  flex-wrap: wrap;
  font-family: var(--artdeco-font-mono);
  font-size: var(--artdeco-text-xs);
  color: var(--artdeco-fg-muted);
}

.content-shell-title {
  margin: 0;
  font-family: var(--artdeco-font-display);
  font-size: var(--artdeco-text-xl);
  color: var(--artdeco-fg-primary);
}

.content-shell-subtitle {
  margin: 0;
  color: var(--artdeco-fg-muted);
  font-size: var(--artdeco-text-sm);
  line-height: var(--artdeco-leading-relaxed);
}

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--artdeco-spacing-4);
}

  .config-section {
    margin-bottom: var(--artdeco-spacing-8);

    .config-table {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-2);

      .config-row {
        display: grid;
        grid-template-columns: 2fr 1fr 2fr 1fr;
        gap: var(--artdeco-spacing-4);
        padding: var(--artdeco-spacing-3);
        border: 1px solid var(--artdeco-border-default);
        align-items: center;

        &.header {
          background: var(--artdeco-gold-opacity-05);
          font-weight: 600;
          color: var(--artdeco-gold-primary);
          border-bottom: calc(var(--artdeco-spacing-px) + var(--artdeco-spacing-px)) solid var(--artdeco-gold-primary);
        }

        .col {
          &.name {
            font-family: var(--artdeco-font-mono);
            font-weight: 500;
          }

          &.status {
            .status-badge {
              padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
              border-radius: calc(var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
              font-size: var(--artdeco-text-xs);
              font-weight: 600;
              text-transform: uppercase;

              &.active {
                background: color-mix(in srgb, var(--artdeco-rise) 20%, transparent);
                color: var(--artdeco-rise);
              }

              &.inactive {
                background: color-mix(in srgb, var(--artdeco-down) 20%, transparent);
                color: var(--artdeco-down);
              }
            }
          }

          &.endpoint {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-xs);
            color: var(--artdeco-fg-muted);
          }

          &.actions {
            text-align: right;
          }
        }
      }
    }
  }

  .action-bar {
    display: flex;
    gap: var(--artdeco-spacing-4);
    margin-bottom: var(--artdeco-spacing-8);
  }

  .info-note {
    padding: var(--artdeco-spacing-6);
    font-style: italic;
    font-size: var(--artdeco-text-sm);
    line-height: var(--artdeco-leading-relaxed);
    color: var(--artdeco-fg-muted);

    p {
      margin: 0;
    }

    .gold-text {
      color: var(--artdeco-gold-primary);
    }
  }

@media (width <= 75rem) {
  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .data-management {
    .config-table {
      .config-row {
        grid-template-columns: 1fr 1fr;

        .col.endpoint,
        .col.actions {
          grid-column: 1 / -1;
        }
      }
    }
  }
}

@media (width <= 48rem) {
  .stats-strip {
    grid-template-columns: 1fr;
  }

  .content-shell-meta,
  .hero-meta,
  .action-bar {
    width: 100%;
  }

  .action-bar {
    flex-direction: column;
  }
}
</style>
