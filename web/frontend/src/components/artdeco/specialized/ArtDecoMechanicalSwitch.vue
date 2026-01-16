<template>
    <div class="artdeco-mechanical-switch" :class="{ 'is-disabled': disabled, 'is-active': modelValue }">
        <!-- Label -->
        <label v-if="label" class="artdeco-mechanical-switch__label">
            {{ label }}
        </label>

        <!-- Mechanical Switch Container -->
        <div class="artdeco-mechanical-switch__control">
            <!-- Decorative Lines -->
            <div class="artdeco-mechanical-switch__frame">
                <div class="artdeco-mechanical-switch__decorator artdeco-mechanical-switch__decorator--top-left"></div>
                <div class="artdeco-mechanical-switch__decorator artdeco-mechanical-switch__decorator--top-right"></div>
                <div
                    class="artdeco-mechanical-switch__decorator artdeco-mechanical-switch__decorator--bottom-left"
                ></div>
                <div
                    class="artdeco-mechanical-switch__decorator artdeco-mechanical-switch__decorator--bottom-right"
                ></div>
            </div>

            <!-- Mechanical Toggle -->
            <div
                class="artdeco-mechanical-switch__toggle"
                :class="{ 'is-active': modelValue, 'is-disabled': disabled }"
                @click="toggle"
                role="switch"
                :aria-checked="modelValue"
                :aria-label="label || 'Toggle'"
            >
                <!-- Background Glow Effect (for active state) -->
                <div v-if="modelValue" class="artdeco-mechanical-switch__glow"></div>

                <!-- Thumb / Handle -->
                <div class="artdeco-mechanical-switch__thumb-container">
                    <div class="artdeco-mechanical-switch__thumb">
                        <div class="artdeco-mechanical-switch__thumb-screw"></div>
                        <div class="artdeco-mechanical-switch__thumb-slot"></div>
                    </div>

                    <!-- Track Lines -->
                    <div class="artdeco-mechanical-switch__track-lines">
                        <div
                            class="artdeco-mechanical-switch__track-line artdeco-mechanical-switch__track-line--left"
                        ></div>
                        <div
                            class="artdeco-mechanical-switch__track-line artdeco-mechanical-switch__track-line--center"
                        ></div>
                        <div
                            class="artdeco-mechanical-switch__track-line artdeco-mechanical-switch__track-line--right"
                        ></div>
                    </div>
                </div>
            </div>

            <!-- Status Display -->
            <div v-if="showStatus" class="artdeco-mechanical-switch__status">
                <span v-if="modelValue" class="status-text status-text--active">
                    {{ onText }}
                </span>
                <span v-else class="status-text status-text--inactive">
                    {{ offText }}
                </span>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    /**
     * ArtDecoMechanicalSwitch - 交易控制类组件
     *
     * Design Philosophy:
     * - 机械质感 - 方形设计、金属质感的拨杆
     * - 视觉确认 - 开启时金色光辉、关闭时暗灰色
     * - Art Deco风格 - 锐角、几何装饰
     *
     * Usage:
     * <ArtDecoSwitch v-model="strategyEnabled" label="Strategy ON" onText="ENABLED" offText="DISABLED" />
     *
     * @see ArtDeco.md
     */

    import { computed } from 'vue'

    // ============================================
    // PROPS - 组件属性
    // ============================================

    interface Props {
        modelValue: boolean
        label?: string
        disabled?: boolean
        showStatus?: boolean
        onText?: string
        offText?: string
    }

    const props = withDefaults(defineProps<Props>(), {
        label: '',
        disabled: false,
        showStatus: true,
        onText: 'ENABLED',
        offText: 'DISABLED'
    })

    // ============================================
    // EMITS - 事件定义
    // ============================================

    const emit = defineEmits<{
        'update:modelValue': [value: boolean]
        change: [value: boolean]
    }>()

    // ============================================
    // COMPUTED - 计算属性
    // ============================================

    const switchClasses = computed(() => ({
        'artdeco-mechanical-switch': true,
        'is-active': props.modelValue && !props.disabled,
        'is-disabled': props.disabled
    }))

    const toggle = () => {
        if (!props.disabled) {
            const newValue = !props.modelValue
            emit('update:modelValue', newValue)
            emit('change', newValue)
        }
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    // ============================================
    // MECHANICAL SWITCH - 机械质感开关组件
    //   方形设计、金属拨杆、金色光辉效果
    // ============================================

    .artdeco-mechanical-switch {
        display: inline-flex;
        align-items: center;
        gap: var(--artdeco-spacing-3);
        position: relative;
        cursor: pointer;
        user-select: none;
        transition: all var(--artdeco-transition-base);

        // Disabled state
        &.is-disabled {
            cursor: not-allowed;
            opacity: 0.4;
        }
    }

    // ============================================
    // LABEL - 标签样式
    //   大写、宽字间距
    // ============================================

    .artdeco-mechanical-switch__label {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-font-size-sm); // 12px - Compact v3.1
        font-weight: 600;
        color: var(--artdeco-fg-muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-right: var(--artdeco-spacing-3);
    }

    // ============================================
    // CONTROL CONTAINER - 控制器容器
    //   包含装饰框和机械开关
    // ============================================

    .artdeco-mechanical-switch__control {
        display: flex;
        align-items: center;
        position: relative;
        padding: var(--artdeco-spacing-2);
    }

    // ============================================
    // FRAME - 装饰框
    //   四角装饰、金色边框
    // ============================================

    .artdeco-mechanical-switch__frame {
        position: relative;
        width: 100%;
        height: 64px;
        border: 2px solid rgba(212, 175, 55, 0.2);
        background: var(--artdeco-bg-card);
        box-sizing: border-box;
        transition: all var(--artdeco-transition-base);

        // Active state glow effect
        &.is-active .artdeco-mechanical-switch__control &::after {
            content: '';
            position: absolute;
            inset: 4px;
            width: calc(100% - 8px);
            height: calc(100% - 8px);
            background: radial-gradient(
                circle at center,
                rgba(212, 175, 55, 0.15) 0%,
                rgba(212, 175, 55, 0) 20%,
                rgba(212, 175, 55, 0)
            );
            border-radius: 4px;
            z-index: -1;
            filter: blur(8px);
            animation: mechanical-glow 2s ease-in-out infinite;
        }

        &.is-disabled::after {
            background: var(--artdeco-silver-dim);
        }
    }

    // ============================================
    // DECORATORS - 角落装饰
    //   Art Deco风格的几何装饰
    // ============================================

    .artdeco-mechanical-switch__decorator {
        position: absolute;
        width: 12px;
        height: 12px;
        background: var(--artdeco-bg-primary);
        border: 2px solid var(--artdeco-gold-dim);
        border-radius: var(--artdeco-radius-none);
    }

    .artdeco-mechanical-switch__decorator--top-left {
        top: 0;
        left: 0;
        border-right: 2px solid var(--artdeco-gold-dim);
        border-bottom: 2px solid var(--artde-gold-dim);
        border-bottom-right-radius: 2px;
    }

    .artdeco-mechanical-switch__decorator--top-right {
        top: 0;
        right: 0;
        border-left: 2px solid var(--artde-gold-dim);
        border-bottom: 2px solid var(--artde-gold-dim);
        border-bottom-left-radius: 2px;
    }

    .artdeco-mechanical-switch__decorator--bottom-left {
        bottom: 0;
        left: 0;
        border-right: 2px solid var(--artde-gold-dim);
        border-top: 2px solid var(--artde-gold-dim);
        border-top-right-radius: 2px;
    }

    .artdeco-mechanical-switch__decorator--bottom-right {
        bottom: 0;
        right: 0;
        border-left: 2px solid var(--artde-gold-dim);
        border-top: 2px solid var(--artde-gold-dim);
        border-top-left-radius: 2px;
    }

    .artdeco-mechanical-switch__frame:hover .artdeco-mechanical-switch__decorator {
        background: var(--artdeco-accent-gold);
        border-color: var(--artdeco-accent-gold);
    }

    // ============================================
    // TOGGLE - 机械拨杆
    //   方形滑块、带有螺丝和槽孔
    // ============================================

    .artdeco-mechanical-switch__toggle {
        width: 100%;
        height: 48px;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(to bottom, var(--artdeco-bg-primary) 0%, var(--artdeco-bg-primary) 100%);
        border: 2px solid var(--artdeco-border-gold-subtle);
        transition: all var(--artdeco-transition-base);

        // Click animation
        &:active {
            transform: translateY(-1px);
        }
    }

    // Active state - 金属质感和光辉
    .artdeco-mechanical-switch__toggle.is-active {
        background: linear-gradient(
            to bottom,
            var(--artdeco-gold-light) 0%,
            var(--artde-gold-primary) 50%,
            var(--artde-gold-light) 100%
        );

        &::before {
            content: '';
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            background: radial-gradient(
                circle at center,
                var(--artdeco-gold-light) 0%,
                rgba(212, 175, 55, 0) 30%,
                transparent
            );
            z-index: 0;
            animation: mechanical-activate 0.6s ease-out;
        }
    }

    // Disabled state
    .artdeco-mechanical-switch__toggle.is-disabled {
        background: linear-gradient(
            to bottom,
            var(--artdeco-bg-primary) 0%,
            var(--artdeco-silver-dim) 50%,
            var(--artdeco-silver-dim) 100%
        );

        &::before {
            background: transparent;
        }
    }

    // ============================================
    // THUMB CONTAINER - 拨杆容器
    //   居中对齐
    // ============================================

    .artdeco-mechanical-switch__thumb-container {
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 100%;
        padding: 0 var(--artdeco-spacing-4);
    }

    // ============================================
    // THUMB - 拨杆手柄
    //   带有螺丝、槽孔的方形设计
    // ============================================

    .artde-mechanical-switch__thumb {
        position: absolute;
        left: 50%;
        top: 0;
        transform: translateX(-50%);
        width: 20px;
        height: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(
            135deg,
            var(--artdeco-bg-primary) 0%,
            var(--artde-silver-light) 50%,
            var(--artde-silver-light) 100%
        );
        border: 2px solid var(--artdeco-border-gold-subtle);
        border-radius: 2px;
        box-shadow: var(--artde-glow-subtle);
        transition: all var(--artde-transition-base);
        cursor: pointer;
        z-index: 2;

        // Active state - 滑到右侧、金色
        .is-active & {
            left: calc(100% - 2px);
            transform: translateX(0);
            background: linear-gradient(
                135deg,
                var(--artdeco-gold-primary) 0%,
                var(--artde-silver-light) 50%,
                var(--artde-gold-light) 100%
            );
            border-color: var(--artdeco-accent-gold);
            box-shadow: var(--artdeco-glow-intense);
        }

        // Active thumb glow
        .is-active::after {
            content: '';
            position: absolute;
            inset: -4px;
            width: 28px;
            height: 28px;
            background: radial-gradient(
                circle at center,
                var(--artdeco-gold-light) 0%,
                rgba(212, 175, 55, 0) 20%,
                transparent
            );
            z-index: 3;
            filter: blur(2px);
            animation: thumb-glow 2s ease-in-out infinite;
        }
    }

    // Disabled state
    &.is-disabled {
        background: linear-gradient(
            135deg,
            var(--artdeco-bg-primary) 0%,
            var(--artdeco-silver-dim) 50%,
            var(--artde-silver-dim) 100%
        );
        border-color: var(--artdeco-silver-dim);
        box-shadow: none;
        cursor: not-allowed;
        opacity: 0.5;
    }

    // ============================================
    // SCREW - 螺丝
    //   金属质感的装饰
    // ============================================

    .artdeco-mechanical-switch__thumb-screw {
        position: absolute;
        top: 4px;
        left: 50%;
        width: 4px;
        height: 16px;
        border: 2px solid var(--artdeco-accent-gold);
        background: linear-gradient(90deg, var(--artdeco-gold-light) 30%, var(--artdeco-silver-light) 70%);
        border-radius: 50%;
        transform: translateX(-50%) rotate(0deg);

        .is-active & {
            transform: translateX(0%) rotate(0deg);
            background: linear-gradient(90deg, var(--artdeco-gold-primary) 30%, var(--artde-silver-light) 70%);
            border-color: var(--artde-co-accent-gold);
        }
    }

    // ============================================
    // SLOT - 槽孔
    //  金属质感的凹槽
    // ============================================

    .artdeco-mechanical-switch__thumb-slot {
        position: absolute;
        top: 6px;
        left: 50%;
        width: 8px;
        height: 8px;
        background: var(--artdeco-bg-primary);
        border: 2px solid var(--artdeco-gold-dim);
        border-radius: 1px;

        .is-active & {
            background: var(--artdeco-accent-gold);
            border-color: var(--artdeco-gold-dim);
        }
    }

    // ============================================
    // TRACK LINES - 轨道线条
    // 金属质感的轨道线
    // ============================================

    .artdeco-mechanical-switch__track-lines {
        position: absolute;
        top: 50%;
        left: 4px;
        right: 4px;
        height: 2px;
        width: calc(100% - 24px);
        display: flex;
        justify-content: space-between;
    }

    .artdeco-mechanical-switch__track-line {
        position: relative;
        flex: 1;
        background: var(--artdeco-silver-dim);
        height: 100%;
        width: 2px;
        transition: background var(--artde-transition-base);

        &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 50%;
            width: 1px;
            height: 100%;
            background: var(--artdeco-accent-gold);
            box-shadow: 0 0 2px rgba(212, 175, 55, 0.2);
        }

        &--left {
            width: 12px;
        }

        &--right {
            width: 12px;
        }

        &--center {
            width: 24px;
        }
    }

    // ============================================
    // GLOW EFFECT - 光辉动画
    // ============================================

    @keyframes mechanical-glow {
        0%,
        100% {
            opacity: 0;
        }

        50%,
        100% {
            opacity: 0.3;
        }
    }

    @keyframes mechanical-activate {
        0% {
            transform: scale(0);
            opacity: 0.3;
        }

        50% {
            transform: scale(1);
            opacity: 1;
        }
    }

    @keyframes thumb-glow {
        0%,
        100% {
            box-shadow: 0 0 8px rgba(202, 175, 55, 0.2);
        }

        50%,
        100% {
            box-shadow: 0 0 15px var(--artde-co-accent-gold);
        }
    }

    // ============================================
    // STATUS DISPLAY - 状态显示
    // ============================================

    .artdeco-mechanical-switch__status {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-font-size-sm);
        color: var(--artdeco-fg-muted);
        margin-left: var(--artdeco-spacing-4);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 2px 6px;
        background: var(--artdeco-bg-card);
        border: 1px solid var(--artdeco-border-gold-subtle);
    }

    .status-text {
        font-weight: 600;
        letter-spacing: 0.05em;
    }

    .status-text--active {
        color: var(--artdeco-accent-gold);
    }

    .status-text--inactive {
        color: var(--artdeco-silver-dim);
    }

    // ============================================
    // DESIGN NOTE
    // ============================================
    // 本组件专为量化交易系统设计，体现机械质感和专业性
    // - 方形拨杆设计（非圆角）
    // - 金属质感的螺丝和槽孔
    // - 滑动时的流畅过渡动画
    // - 开启时的金色光辉效果
    // ============================================
</style>
