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
                            <stop offset="0%" stop-color="#1A2026" />
                            <stop offset="50%" stop-color="#00E676" />
                            <stop offset="100%" stop-color="#FF5252" />
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
                        stroke="rgba(212, 175, 55, 0.1)"
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
        if (percentage.value >= 80) return 'var(--artdeco-fall)'
        if (percentage.value >= 60) return 'var(--artdeco-accent-gold)'
        return 'var(--artdeco-up)'
    })

    const progressColor = computed(() => {
        if (percentage.value >= 80) return 'var(--artdeco-fall)'
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
    @import '@/styles/artdeco-tokens.scss';

    // ============================================
    // ART DECO PROGRESS - 进度仪表组件
    //   Art Deco风格：精密仪表、老式风格
    //   用于回测进度、模型训练Epoch等耗时操作
    // ============================================

    .artdeco-progress {
        padding: var(--artdeco-spacing-4);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.2);
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: var(--artdeco-spacing-6);
    }

    // ============================================
    // HEADER - 标题区域
    // ============================================

    .artdeco-progress__header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: var(--artdeco-spacing-4);
    }

    .artdeco-progress__title {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-font-size-lg); // 20px
        font-weight: 600;
        color: var(--artdeco-accent-gold);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        margin: 0;
    }

    // ============================================
    // GAUGE CONTAINER - 仪表盘区域
    // ============================================

    .artdeco-progress__gauge-container {
        position: relative;
        width: 200px;
        height: 120px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    // Background Scale - 刻度尺效果
    .artdeco-progress__scale {
        position: absolute;
        top: 10px;
        left: 10px;
        width: 180px;
        height: 100px;
    }

    .artdeco-progress__scale-line {
        position: absolute;
        background: var(--artdeco-gold-dim);
        opacity: 0.2;
        transition: opacity 0.3s ease-in-out;

        &--line1 {
            top: 0;
            left: 20%;
        }
        &--line2 {
            top: 25%;
            left: 40%;
        }
        &--line3 {
            top: 50%;
            left: 60%;
        }
        &--line4 {
            top: 75%;
            left: 80%;
        }
        &--line5 {
            top: 0;
            left: 100%;
        }
    }

    // Gauge SVG - Art Deco精密仪表
    .artdeco-progress__svg {
        width: 100%;
        height: 100%;
        position: relative;
        filter: url(#glow);
        animation: gauge-load 1.5s ease-out;
    }

    .artdeco-progress__bg-arc {
        transition: stroke-dasharray var(--artdeco-duration-base) 1s ease-out;
        fill-opacity: 0.3;
    }

    .artdeco-progress__progress-arc {
        fill: none;
        stroke-width: 16;
        stroke-linecap: round;
        transition: all var(--artdeco-transition-base) 1s ease-out;
        animation: gauge-progress 1.2s ease-out forwards;
    }

    // Value Text - 大号显示百分比
    .artdeco-progress__value {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-font-size-xl);; // 32px - Compact v3.1
        font-weight: 700;
        fill: var(--artdeco-accent-gold);
        text-anchor: middle;
        pointer-events: none;
        transition: all var(--artdeco-transition-base);
    }

    .artdeco-progress__value--up {
        fill: var(--artdeco-up);
    }

    .artdeco-progress__value--down {
        fill: var(--artdeco-down);
    }

    // Epoch Counter - 次数显示Epoch
    .artdeco-progress__epoch {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-font-size-sm);
        font-weight: 600;
        fill: var(--artdeco-accent-gold);
        text-anchor: middle;
        pointer-events: none;
        letter-spacing: 0.1em;
    }

    // ============================================
    // DETAILS - 详细信息
    // ============================================

    .artdeco-progress__details {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-3);
        width: 100%;
        justify-content: center;
    }

    .detail-item {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-1);
        align-items: center;
        text-align: center;
        background: rgba(212, 175, 55, 0.08);
        border-radius: var(--artdeco-radius-none);
        padding: var(--artdeco-spacing-2);
    }

    .detail-label {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-font-size-sm); // 12px - Compact v3.1
        font-weight: 600;
        color: var(--artdeco-fg-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .detail-value {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-font-size-base); // 14px - Compact v3.1
        font-weight: 600;
        color: var(--artdeco-fg-secondary);
    }

    .detail-value--good {
        color: var(--artdeco-up);
        border: 1px solid var(--artdeco-up);
        background: rgba(0, 230, 118, 0.1);
    }

    .detail-value--bad {
        color: var(--artdeco-down);
        border: 1px solid var(--artdeco-down);
        background: rgba(255, 82, 82, 0.1);
    }

    // Value color modifiers
    .artdeco-progress__value--up {
        fill: var(--artdeco-up);
        text-shadow: 0 0 8px rgba(0, 230, 118, 0.4);
    }

    .artdeco-progress__value--down {
        fill: var(--artdeco-down);
        text-shadow: 0 0 8px rgba(255, 82, 82, 0.4);
    }

    // ============================================
    // FOOTER - 页脚信息
    // ============================================

    .artdeco-progress__footer {
        margin-top: var(--artdeco-spacing-4);
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-font-size-sm);
        color: var(--artdeco-fg-muted);
        text-align: center;
    }

    .footer-text {
        opacity: 0.7;
    }

    // ============================================
    // ANIMATIONS - 动画定义
    // ============================================

    @keyframes gauge-load {
        0% {
            opacity: 0.3;
            fill-opacity: 0.3;
        }
        100% {
            opacity: 1;
            fill-opacity: 1;
        }
    }

    @keyframes gauge-progress {
        0% {
            stroke-dashoffset: var(--artde-circumference); // Full circle
            opacity: 1;
        }
        100% {
            stroke-dashoffset: 0;
            opacity: 1;
        }
    }

    @keyframes scale-pulse {
        0%,
        50%,
        100% {
            opacity: 0.4;
        }
        50% {
            opacity: 0.6;
        }
    }

    // Apply pulse animation to scale lines
    .artdeco-progress__scale-line {
        &--line1 {
            animation: scale-pulse 2s ease-in-out infinite;
            animation-delay: 0s;
        }
        &--line2 {
            animation: scale-pulse 2s ease-in-out infinite;
            animation-delay: 0.5s;
        }
        &--line3 {
            animation: scale-pulse 2s ease-in-out infinite;
            animation-delay: 1s;
        }
        &--line4 {
            animation: scale-pulse 2s ease-in-out infinite;
            animation-delay: 1.5s;
        }
        &--line5 {
            animation: scale-pulse 2s ease-in-out infinite;
            animation-delay: 2s;
        }
    }

    // ============================================
    // VALUE COLOR CLASSES - 数值颜色
    // ============================================

    .artde-co-progress__value--fall {
        fill: var(--artdeco-fall);
    }
    .artde-co-progress__value--rise {
        fill: var(--artdeco-up);
    }
</style>
