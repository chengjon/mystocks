<template>
    <div class="artdeco-alert-rule" :class="{ compact, disabled }">
        <div class="artdeco-corner-tl" v-if="!compact"></div>
        <div class="artdeco-corner-br" v-if="!compact"></div>

        <div class="rule-header">
            <div class="header-left">
                <div class="rule-indicator" :class="{ active: rule.enabled }"></div>
                <h4 class="rule-title">{{ rule.name }}</h4>
            </div>
            <div class="header-right">
                <ArtDecoBadge :text="ruleTypeText" :variant="ruleTypeVariant" />
                <ArtDecoStatus
                    :status="rule.enabled ? 'success' : 'offline'"
                    :label="rule.enabled ? 'ACTIVE' : 'INACTIVE'"
                />
            </div>
        </div>

        <div class="rule-body">
            <div v-if="!compact" class="rule-condition">
                <span class="condition-label">CONDITION</span>
                <span class="condition-value">
                    {{ rule.symbol }} {{ rule.indicator }} {{ rule.operator }} {{ rule.threshold }}
                </span>
            </div>

            <div class="rule-meta">
                <div class="meta-item">
                    <span class="meta-label">SYMBOL</span>
                    <span class="meta-value mono">{{ rule.symbol }}</span>
                </div>
                <div class="meta-item">
                    <span class="meta-label">INDICATOR</span>
                    <span class="meta-value">{{ rule.indicator }}</span>
                </div>
                <div v-if="!compact" class="meta-item">
                    <span class="meta-label">THRESHOLD</span>
                    <span class="meta-value mono gold">{{ rule.threshold }}</span>
                </div>
            </div>

            <div v-if="!compact" class="rule-actions">
                <span class="actions-label">ACTIONS</span>
                <div class="action-tags">
                    <span v-for="action in rule.actions" :key="action" class="action-tag">
                        {{ action }}
                    </span>
                </div>
            </div>
        </div>

        <div v-if="!compact" class="rule-footer">
            <button class="artdeco-btn-mini artdeco-btn-secondary" @click="handleEdit">EDIT</button>
            <button
                class="artdeco-btn-mini"
                :class="rule.enabled ? 'artdeco-btn-fall' : 'artdeco-btn-rise'"
                @click="handleToggle"
            >
                {{ rule.enabled ? 'DISABLE' : 'ENABLE' }}
            </button>
            <button class="artdeco-btn-mini artdeco-btn-fall" @click="handleDelete">DELETE</button>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { computed } from 'vue'
    import ArtDecoBadge from '../base/ArtDecoBadge.vue'
    import ArtDecoStatus from './ArtDecoStatus.vue'

    interface AlertRule {
        id: string
        name: string
        enabled: boolean
        type: 'price' | 'volume' | 'indicator' | 'custom'
        symbol: string
        indicator: string
        operator: '>' | '<' | '>=' | '<=' | '==' | '!='
        threshold: number | string
        actions: string[]
        priority?: 'low' | 'medium' | 'high'
    }

    interface Props {
        rule: AlertRule
        compact?: boolean
        disabled?: boolean
    }

    const props = withDefaults(defineProps<Props>(), {
        compact: false,
        disabled: false
    })

    const emit = defineEmits<{
        edit: [rule: AlertRule]
        toggle: [rule: AlertRule]
        delete: [rule: AlertRule]
    }>()

    const ruleTypeText = computed(() => {
        const typeMap = {
            price: 'PRICE',
            volume: 'VOLUME',
            indicator: 'INDICATOR',
            custom: 'CUSTOM'
        }
        return typeMap[props.rule.type] || 'UNKNOWN'
    })

    const ruleTypeVariant = computed(() => {
        const variantMap: { [key: string]: 'gold' | 'rise' | 'fall' | 'info' | 'warning' | 'success' | 'danger' } = {
            price: 'gold',
            volume: 'info',
            indicator: 'warning',
            custom: 'info'
        }
        return variantMap[props.rule.type] || 'info'
    })

    const handleEdit = () => {
        emit('edit', props.rule)
    }

    const handleToggle = () => {
        emit('toggle', props.rule)
    }

    const handleDelete = () => {
        emit('delete', props.rule)
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-alert-rule {
      background: var(--artdeco-bg-card);
      border: 1px solid rgba(212, 175, 55, 0.2);
      padding: var(--artdeco-spacing-4);
      position: relative;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-3);
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-alert-rule:hover {
      border-color: var(--artdeco-accent-gold);
      box-shadow: var(--artdeco-glow-subtle);
    }

    .artdeco-alert-rule.disabled {
      opacity: 0.5;
    }

    /* Corner decorations */
    .artdeco-corner-tl,
    .artdeco-corner-br {
      position: absolute;
      width: 16px;
      height: 16px;
      pointer-events: none;
      opacity: 0.4;
    }

    .artdeco-corner-tl {
      top: 8px;
      left: 8px;
      border-top: 2px solid var(--artdeco-accent-gold);
      border-left: 2px solid var(--artdeco-accent-gold);
    }

    .artdeco-corner-br {
      bottom: 8px;
      right: 8px;
      border-bottom: 2px solid var(--artdeco-accent-gold);
      border-right: 2px solid var(--artdeco-accent-gold);
    }

    /* Rule header */
    .rule-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      gap: var(--artdeco-spacing-3);
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);
    }

    .rule-indicator {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: var(--artdeco-fg-muted);
      transition: all var(--artdeco-transition-base);
    }

    .rule-indicator.active {
      background: var(--artdeco-rise);
      box-shadow: 0 0 8px rgba(0, 230, 118, 0.6);
    }

    .rule-title {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      font-weight: 600;
      color: var(--artdeco-accent-gold);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin: 0;
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: var(--artdeco-spacing-2);
    }

    /* Rule body */
    .rule-body {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-3);
    }

    .rule-condition {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-1);
    }

    .condition-label {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      font-weight: 600;
      color: var(--artdeco-fg-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .condition-value {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      color: var(--artdeco-fg-secondary);
      padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
      background: var(--artdeco-bg-primary);
      border: 1px solid rgba(212, 175, 55, 0.2);
    }

    .rule-meta {
      display: flex;
      gap: var(--artdeco-spacing-4);
      flex-wrap: wrap;
    }

    .meta-item {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-1);
    }

    .meta-label {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      font-weight: 600;
      color: var(--artdeco-fg-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .meta-value {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      color: var(--artdeco-fg-secondary);
    }

    .meta-value.mono {
      font-family: var(--artdeco-font-mono);
    }

    .meta-value.gold {
      color: var(--artdeco-accent-gold);
    }

    .rule-actions {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-1);
    }

    .actions-label {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      font-weight: 600;
      color: var(--artdeco-fg-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .action-tags {
      display: flex;
      gap: var(--artdeco-spacing-2);
      flex-wrap: wrap;
    }

    .action-tag {
      padding: var(--artdeco-spacing-1) var(--artdeco-spacing-2);
      background: var(--artdeco-bg-primary);
      border: 1px solid rgba(212, 175, 55, 0.2);
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      color: var(--artdeco-fg-secondary);
      text-transform: uppercase;
    }

    /* Rule footer */
    .rule-footer {
      display: flex;
      gap: var(--artdeco-spacing-2);
      padding-top: var(--artdeco-spacing-3);
      border-top: 1px solid rgba(212, 175, 55, 0.1);
    }

    .artdeco-btn-mini {
      flex: 1;
      padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
      border: 1px solid rgba(212, 175, 55, 0.2);
      background: var(--artdeco-bg-card);
      color: var(--artdeco-fg-secondary);
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      cursor: pointer;
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-btn-mini:hover {
      border-color: var(--artdeco-accent-gold);
      box-shadow: var(--artdeco-glow-subtle);
      transform: translateY(-1px);
    }

    .artdeco-btn-mini.artdeco-btn-secondary:hover {
      color: var(--artdeco-accent-gold);
    }

    .artdeco-btn-mini.artdeco-btn-rise:hover {
      border-color: var(--artdeco-rise);
      color: var(--artdeco-rise);
    }

    .artdeco-btn-mini.artdeco-btn-fall:hover {
      border-color: var(--artdeco-fall);
      color: var(--artdeco-fall);
    }

    /* Compact variant */
    .artdeco-alert-rule.compact {
      padding: var(--artdeco-spacing-3);
      gap: var(--artdeco-spacing-2);
    }

    .artdeco-alert-rule.compact .rule-title {
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
    }

    .artdeco-alert-rule.compact .meta-label {
      font-size: var(--artdeco-font-size-xs) // 10px - Compact v3.1;
    }

    .artdeco-alert-rule.compact .meta-value {
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
    }
</style>
