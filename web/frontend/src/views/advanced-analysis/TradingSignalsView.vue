<template>
    <div class="trading-signals">
        <div class="signals-overview">
            <div class="signal-stats">
                <div class="stat-item">
                    <div class="stat-value">{{ buySignals }}</div>
                    <div class="stat-label">买入信号</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ sellSignals }}</div>
                    <div class="stat-label">卖出信号</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">{{ neutralSignals }}</div>
                    <div class="stat-label">观望信号</div>
                </div>
            </div>
        </div>

        <div class="signals-list">
            <div v-for="signal in signals" :key="signal.id" class="signal-item" :class="signal.type">
                <div class="signal-icon">
                    <svg
                        v-if="signal.type === 'buy'"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                    >
                        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                        <polyline points="17 6 23 6 23 12"></polyline>
                    </svg>
                    <svg
                        v-else-if="signal.type === 'sell'"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                    >
                        <polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline>
                        <polyline points="17 18 23 18 23 12"></polyline>
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                </div>
                <div class="signal-content">
                    <div class="signal-title">{{ signal.title }}</div>
                    <div class="signal-description">{{ signal.description }}</div>
                    <div class="signal-strength">强度: {{ signal.strength }}/10</div>
                </div>
                <div class="signal-confidence">{{ signal.confidence }}%</div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { computed } from 'vue'

    interface Props {
        data: any
    }

    const props = defineProps<Props>()

    const signals = computed(() => {
        if (!props.data?.signals) return []

        return props.data.signals.map((signal: any, index: number) => ({
            id: index,
            type: signal.type || 'neutral',
            title: signal.title || '交易信号',
            description: signal.description || '',
            strength: signal.strength || 5,
            confidence: signal.confidence || 50
        }))
    })

    const buySignals = computed(() => signals.value.filter((s: any) => s.type === 'buy').length)
    const sellSignals = computed(() => signals.value.filter((s: any) => s.type === 'sell').length)
    const neutralSignals = computed(() => signals.value.filter((s: any) => s.type === 'neutral').length)
</script>
