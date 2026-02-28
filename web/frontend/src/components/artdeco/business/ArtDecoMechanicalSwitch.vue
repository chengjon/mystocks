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

    const _switchClasses = computed(() => ({
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
@import "./styles/ArtDecoMechanicalSwitch";
</style>
