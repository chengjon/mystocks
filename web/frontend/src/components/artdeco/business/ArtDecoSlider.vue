<template>
    <div class="artdeco-slider-container" :class="{ 'is-disabled': disabled }">
        <!-- Label and Current Value -->
        <label v-if="label" class="artdeco-slider-label">
            {{ label }}
            <span class="slider-value">{{ modelValue }}{{ unit }}</span>
        </label>

        <!-- Precise Slider Control -->
        <div class="artdeco-slider" ref="sliderRef" @mousedown="handleMouseDown" @touchstart="handleTouchStart">
            <!-- Metallic Track -->
            <div class="artdeco-slider-track">
                <!-- Gradient Fill -->
                <div class="artdeco-slider-fill" :style="{ width: percent + '%' }"></div>
            </div>

            <!-- Metallic Thumb -->
            <div class="artdeco-slider-thumb" :style="{ left: percent + '%' }"></div>

            <!-- Diamond Shape Markers (Art Deco Style) -->
            <div class="artdeco-slider-marker marker-0" :style="{ left: '0%' }"></div>
            <div class="artdeco-slider-marker marker-1" :style="{ left: '20%' }"></div>
            <div class="artdeco-slider-marker marker-2" :style="{ left: '40%' }"></div>
            <div class="artdeco-slider-marker marker-3" :style="{ left: '60%' }"></div>
            <div class="artdeco-slider-marker marker-4" :style="{ left: '80%' }"></div>
            <div class="artde-slider-marker marker-5" :style="{ left: '100%' }"></div>

            <!-- Tick Marks -->
            <div v-if="showTicks" class="artdeco-slider-ticks">
                <div
                    class="artdeco-slider-tick"
                    v-for="tick in ticks"
                    :key="tick.value"
                    :style="{ left: tick.position + '%' }"
                >
                    <div class="artdeco-slider-tick-mark"></div>
                </div>
            </div>
        </div>

        <!-- Optional Marks Display -->
        <div v-if="showMarks" class="artdeco-slider-marks">
            <span class="mark-left">{{ min }}</span>
            <span class="mark-right">{{ max }}</span>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, onMounted, onUnmounted } from 'vue'

    // ============================================
    // COMPONENT: ArtDecoSlider
    //  Art Deco风格精密滑块组件
    //
    // Design Philosophy:
    // - 菱形/矩形金属块滑块（替代圆角）
    // - 金属质感的Thumb（金色+斜切）
    // - Art Deco风格的几何装饰（钻石标记）
    // - 刻度吸附支持
    // - 金色边框和辉光效果
    //
    // Usage:
    // <ArtDecoSlider v-model="stopLoss" min="5" max="20" unit="%" label="止损止盈" />
    // <ArtDecoSlider v-model="positionSize" min="0" max="100" unit="%" label="仓位比例" :step="10" :showTicks="true" />
    //
    // ============================================

    // ============================================
    // PROPS - 组件属性
    // ============================================

    interface Props {
        modelValue: number
        min?: number
        max?: number
        step?: number
        label?: string
        unit?: string
        disabled?: boolean
        showTicks?: boolean
        showMarks?: boolean
        tickStep?: number
        precision?: number
    }

    const props = withDefaults(defineProps<Props>(), {
        min: 0,
        max: 100,
        step: 1,
        label: '',
        unit: '',
        disabled: false,
        showTicks: false,
        showMarks: true,
        tickStep: 25,
        precision: 2
    })

    // ============================================
    // EMITS - 事件定义
    // ============================================

    const emit = defineEmits<{
        'update:modelValue': [value: number]
        change: [value: number]
    }>()

    // ============================================
    // REFS - 响应式引用
    // ============================================

    const sliderRef = ref<HTMLElement | null>(null)
    const isDragging = ref(false)

    // ============================================
    // COMPUTED - 计算属性
    // ============================================

    /**
     * Calculate percentage position
     * 计算百分比位置
     */
    const percent = computed(() => {
        const p = ((props.modelValue - props.min) / (props.max - props.min)) * 100
        return Math.max(0, Math.min(100, p))
    })

    /**
     * Generate tick marks
     * 生成刻度标记
     */
    const ticks = computed(() => {
        if (!props.showTicks) return []

        const marks = []
        const step = props.tickStep || 25

        for (let i = props.min; i <= props.max; i += step) {
            marks.push({
                value: i,
                label: i.toString(),
                position: ((i - props.min) / (props.max - props.min)) * 100
            })
        }

        return marks
    })

    /**
     * Update slider value from client position
     * 从客户端位置更新值
     */
    function updateValue(clientX: number) {
        if (!sliderRef.value || props.disabled) return

        const rect = sliderRef.value.getBoundingClientRect()
        const offset = clientX - rect.left
        let p = offset / rect.width
        p = Math.max(0, Math.min(1, p))

        let value = props.min + p * (props.max - props.min)

        // Apply step snapping
        const step = props.step || 1
        value = Math.round(value / step) * step

        emit('update:modelValue', value)
        emit('change', value)
    }

    // ============================================
    // METHODS - 事件处理方法
    // ============================================

    function handleMouseDown(e: MouseEvent) {
        if (props.disabled) return
        isDragging.value = true
        updateValue(e.clientX)
        window.addEventListener('mousemove', handleMouseMove)
        window.addEventListener('mouseup', handleMouseUp)
    }

    function handleMouseMove(e: MouseEvent) {
        if (isDragging.value) {
            updateValue(e.clientX)
        }
    }

    function handleMouseUp() {
        isDragging.value = false
        window.removeEventListener('mousemove', handleMouseMove)
        window.removeEventListener('mouseup', handleMouseUp)
    }

    function handleTouchStart(e: TouchEvent) {
        if (props.disabled) return
        isDragging.value = true
        updateValue(e.touches[0].clientX)
        window.addEventListener('touchmove', handleTouchMove)
        window.addEventListener('touchend', handleTouchEnd)
    }

    function handleTouchMove(e: TouchEvent) {
        if (isDragging.value) {
            updateValue(e.touches[0].clientX)
        }
    }

    function handleTouchEnd() {
        isDragging.value = false
        window.removeEventListener('touchmove', handleTouchMove)
        window.removeEventListener('touchend', handleTouchEnd)
    }

    // ============================================
    // LIFECYCLE
    // 生命周期清理
    // ============================================

    onUnmounted(() => {
        handleMouseUp()
        handleTouchEnd()
    })
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    // ============================================
    // ART DECO SLIDER - 精密滑块组件
    //   菱形金属块设计、Art Deco装饰
    // ============================================

    .artdeco-slider-container {
        width: 100%;
        padding: var(--artdeco-spacing-3) var(--artdeco-spacing-2) 0;
    }

    // Disabled state
    .artdeco-slider-container.is-disabled {
        opacity: 0.5;
        pointer-events: none;
    }

    // ============================================
    // LABEL - 标签样式
    //   大写、宽字间距
    // ============================================

    .artdeco-slider-label {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-font-size-sm); // 12px
        color: var(--artdeco-fg-muted);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
        margin-bottom: var(--artdeco-spacing-2);
    }

    .slider-value {
        color: var(--artdeco-accent-gold);
        font-family: var(--artdeco-font-mono);
        font-weight: 600;
    }

    // ============================================
    // SLIDER CONTROL - 滑块控制器
    //   100%宽度、24px高度（机械设计）
    // ============================================

    .artdeco-slider {
        width: 100%;
        height: 24px;
        display: flex;
        align-items: center;
        cursor: pointer;
        position: relative;
        padding: 0;
    }

    .artdeco-slider.is-disabled {
        cursor: not-allowed;
    }

    // ============================================
    // TRACK - 金色轨道
    //   2px高、金色渐变背景
    // ============================================

    .artdeco-slider-track {
        flex: 1;
        height: 100%;
        position: relative;
        background: linear-gradient(to bottom, var(--artdeco-bg-card), var(--artdeco-bg-card));
        padding: var(--artdeco-spacing-2);
    }

    // ============================================
    // FILL - 金色填充条
    //   渐变效果、金属质感
    // ============================================

    .artdeco-slider-fill {
        position: absolute;
        left: 0;
        top: 0;
        height: 100%;
        background: linear-gradient(
            to right,
            var(--artdeco-gold-primary) 0%,
            var(--artdeco-gold-primary) 50%,
            var(--artdeco-gold-hover) 100%
        );
        box-shadow: var(--artdeco-glow-subtle);
        transition: width var(--artdeco-transition-base);
    }

    // ============================================
    // THUMB - 金属质感滑块
    //   菱形、斜切、金色光泽
    // ============================================

    .artdeco-slider-thumb {
        position: absolute;
        top: 50%;
        transform: translate(-50%, -50%);
        width: 20px;
        height: 20px;
        background: linear-gradient(
            135deg,
            var(--artdeco-gold-primary) 0%,
            var(--artdeco-silver-light) 50%,
            var(--artdeco-silver-light) 100%
        );
        border: 2px solid var(--artdeco-gold-border);
        box-shadow: var(--artdeco-glow-subtle);
        transition: transform var(--artdeco-transition-base);
        cursor: pointer;
        z-index: 2;
    }

    // Active state glow effect
    .artdeco-slider-thumb:active {
        transform: translate(-50%, -50%) scale(1.1);
        background: linear-gradient(
            135deg,
            var(--artdeco-gold-primary) 30%,
            var(--artdeco-silver-light) 70%,
            var(--artdeco-gold-hover) 100%
        );
        box-shadow: var(--artdeco-glow-intense);
        z-index: 3;
    }

    // Disabled state
    .artdeco-slider-thumb:disabled {
        opacity: 0.4;
        cursor: not-allowed;
        background: var(--artdeco-silver-dim);
        border-color: var(--artdeco-gold-dim);
    }

    // ============================================
    // DIAMOND MARKERS - Art Deco风格装饰
    //   6个钻石形状标记（刻度指示器）
    // ============================================

    .artdeco-slider-marker {
        position: absolute;
        top: 50%;
        width: 12px;
        height: 12px;
        background: var(--artdeco-bg-primary);
        border: 1px solid var(--artdeco-gold-border);
        transform: rotate(45deg) translateX(-50%);
        z-index: 1;
    }

    .artdeco-slider-marker::before {
        content: '';
        position: absolute;
        inset: 0;
        width: 100%;
        height: 100%;
        background: radial-gradient(circle at center, var(--artdeco-gold-primary) 0%, transparent 60%);
        border: 1px solid var(--artdeco-gold-border);
        border-radius: 50%;
    }

    // Marker colors based on position
    .marker-0 {
        border-color: var(--artdeco-up);
    }
    .marker-1 {
        border-color: var(--artdeco-accent-gold);
    }
    .marker-2 {
        border-color: var(--artdeco-fg-secondary);
    }
    .marker-3 {
        border-color: var(--artdeco-silver-light);
    }
    .marker-4 {
        border-color: var(--artdeco-up);
    }
    .marker-5 {
        border-color: var(--artdeco-accent-gold);
    }

    // ============================================
    // TICKS - 刻度刻度标记
    //   精细的金线+刻度值
    // ============================================

    .artdeco-slider-ticks {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
    }

    .artdeco-slider-tick {
        position: absolute;
        top: calc(50% - 1px);
        left: 0;
        width: 2px;
        height: 100%;
        background: var(--artdeco-gold-primary);
        transform: translateX(-50%);
    }

    .artdeco-slider-tick-mark {
        width: 2px;
        height: 100%;
        background: var(--artdeco-bg-primary);
    }

    // ============================================
    // MARKS DISPLAY - 最小最大标记
    // ============================================

    .artdeco-slider-marks {
        display: flex;
        justify-content: space-between;
        margin-top: var(--artdeco-spacing-3);
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-font-size-xs);
        color: var(--artdeco-fg-secondary);
    }

    .mark-left,
    .mark-right {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-font-size-sm);
        font-weight: 600;
        color: var(--artdeco-accent-gold);
        text-transform: uppercase;
    }

    // ============================================
    // DESIGN NOTE
    // 本组件专为量化交易系统设计
    // - 机械质感：方形的Thumb和Track
    // - 金属光泽：渐变、边框、阴影
    // - Art Deco装饰：钻石标记、金色辉光
    // - 刻度吸附：支持tickStep配置
    // ============================================
</style>
