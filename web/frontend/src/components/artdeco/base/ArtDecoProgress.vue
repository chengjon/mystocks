<template>
    <div class="artdeco-progress">
        <!-- Header Section -->
        <div class="artdeco-progress__header">
            <h3 class="artdeco-progress__title">{{ title }}</h3>
            <ArtDecoBadge v-if="badgeText" :text="badgeText" variant="gold" />
        </div>

        <!-- Progress Bar Container -->
        <div class="artdeco-progress__gauge-container">
            <!-- Background Scale -->
            <div class="artdeco-progress__scale">
                <div class="artdeco-progress__scale-line scale-line-1"></div>
                <div class="artdeco-progress__scale-line scale-line-2"></div>
                <div class="artdeco-progress__scale-line scale-line-3"></div>
                <div class="artdeco-progress__scale-line scale-line-4"></div>
                <div class="artdeco-progress__scale-line scale-line-5"></div>
            </div>

            <!-- Gauge -->
            <div class="artdeco-progress__gauge">
                <!-- Backlight Layer -->
                <svg class="artdeco-progress__svg" viewBox="0 0 200 120">
                    <defs>
                        <!-- Gold gradient for gauge background -->
                        <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                            <stop offset="0%" stop-color="var(--artdeco-bg-secondary)" />
                            <stop offset="50%" stop-color="var(--artdeco-down)" />
                            <stop offset="100%" stop-color="var(--artdeco-up)" />
                        </linearGradient>

                        <!-- Glow effect -->
                        <filter id="glow">
                            <feGaussianBlur in="SourceAlpha" stdDeviation="1" result="blur" />
                        </filter>
                    </defs>

                    <!-- Background Arc -->
                    <circle
                        class="artdeco-progress__bg-arc"
                        cx="100"
                        cy="60"
                        r="50"
                        fill="url(#gaugeGradient)"
                        fill-opacity="0.3"
                        stroke="var(--artdeco-gold-opacity-10)"
                        stroke-width="16"
                    />

                    <!-- Value Text -->
                    <text
                        x="100"
                        y="60"
                        dy="0.35em"
                        class="artdeco-progress__value"
                        :fill="valueColor"
                        text-anchor="middle"
                    >
                        {{ displayValue }}%
                    </text>

                    <!-- Epoch Counter -->
                    <text
                        v-if="showEpoch"
                        x="100"
                        y="45"
                        dy="-0.15em"
                        class="artdeco-progress__epoch"
                        text-anchor="middle"
                    >
                        Epoch {{ displayEpoch }}
                    </text>
                </svg>

                <!-- Progress Arc -->
                <circle
                    class="artdeco-progress__progress-arc artdeco-progress__arc--animating"
                    cx="100"
                    cy="60"
                    r="50"
                    fill="none"
                    :stroke="progressColor"
                    :stroke-dasharray="progressDashArray"
                    :stroke-dashoffset="dashOffset"
                />
            </div>
        </div>

        <!-- Details Section -->
        <div v-if="showDetails" class="artdeco-progress__details">
            <div v-for="(detail, index) in displayDetails" :key="index" class="artdeco-progress__detail">
                <span class="detail-label">{{ detail.label }}</span>
                <span class="detail-value mono" :class="detailValueClass(detail.value)">
                    {{ formatValue(detail.value) }}
                </span>
            </div>
        </div>

        <!-- Footer Section -->
        <div v-if="footer" class="artdeco-progress__footer">
            <span class="footer-text">{{ footer }}</span>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { computed } from 'vue'
    import ArtDecoBadge from './ArtDecoBadge.vue'

    interface DetailItem {
        label: string
        value: string | number
        threshold?: number
    }

    interface Props {
        title: string
        value: number
        max?: number
        showProgress?: boolean
        showDetails?: boolean
        showEpoch?: boolean
        badgeText?: string
        footer?: string
        details?: DetailItem[]
    }

    const props = withDefaults(defineProps<Props>(), {
        title: 'Training Progress',
        value: 0,
        max: 100,
        showProgress: true,
        showDetails: false,
        showEpoch: true,
        badgeText: 'TRAINING',
        footer: 'Optimizing parameters...',
        details: () => []
    })

    // ============================================
    // COMPUTED - 计算属性
    // ============================================

    const percentage = computed(() => {
        return Math.min(100, Math.max(0, props.value))
    })

    const displayValue = computed(() => {
        return percentage.value.toFixed(1)
    })

    const displayEpoch = computed(() => {
        const epoch = Math.floor(percentage.value / 10)
        return epoch.toString().padStart(2, '0')
    })

    const progressDashArray = computed(() => {
        const circumference = Math.PI * 100 // r=50, diameter=100
        return (circumference * (props.value / 100)) / 100
    })

    const dashOffset = computed(() => {
        const circumference = Math.PI * 100
        return circumference - (circumference * (percentage.value / 100)) / 100
    })

    /**
     * Determine value color based on thresholds
     */
    const valueColor = computed(() => {
        if (percentage.value >= 80) return 'var(--artdeco-down)'
        if (percentage.value >= 60) return 'var(--artdeco-accent-gold)'
        return 'var(--artdeco-up)'
    })

    const progressColor = computed(() => {
        if (percentage.value >= 80) return 'var(--artdeco-down)'
        if (percentage.value >= 60) return 'var(--artdeco-accent-gold)'
        return 'var(--artdeco-up)'
    })

    /**
     * Format value for details
     */
    const formatValue = (value: string | number): string => {
        if (typeof value === 'number') {
            return value.toLocaleString('en-US', {
                maximumFractionDigits: 2,
                minimumFractionDigits: 2
            })
        }
        return String(value)
    }

    const detailValueClass = (value: string | number): string => {
        if (props.details.length === 0) return ''

        const detail = props.details[0]
        const threshold = detail.threshold ?? 0

        if (typeof value === 'number') {
            const numValue = Number(value)
            if (threshold) {
                if (numValue >= threshold) return 'artdeco-progress__value--bad'
                if (numValue < -threshold) return 'artdeco-progress__value--good'
                return ''
            }
        }

        return ''
    }

    /**
     * Display details based on data availability
     */
    const displayDetails = computed(() => {
        return props.showDetails ? props.details : []
    })
</script>

<style scoped lang="scss">
@import "./styles/ArtDecoProgress";
</style>
