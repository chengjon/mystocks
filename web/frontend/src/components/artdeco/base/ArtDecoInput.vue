<template>
    <div :class="wrapperClasses">
        <!-- Label (Optional) -->
        <label v-if="label" :for="inputId" class="artdeco-input__label">
            {{ label }}
            <span v-if="required" class="artdeco-input__required">*</span>
        </label>

        <!-- Input Wrapper -->
        <div class="artdeco-input__wrapper">
            <!-- Prefix Icon (Optional) -->
            <span v-if="$slots.prefix" class="artdeco-input__prefix">
                <slot name="prefix" />
            </span>

            <!-- Input Element -->
            <input
                :id="inputId"
                ref="inputRef"
                :type="type"
                :value="modelValue"
                :placeholder="placeholder"
                :disabled="disabled"
                :readonly="readonly"
                :maxlength="maxlength"
                :class="inputClasses"
                @input="handleInput"
                @focus="handleFocus"
                @blur="handleBlur"
                @keyup.enter="handleEnter"
            />

            <!-- Suffix Icon (Optional) -->
            <span v-if="slots.suffix || clearable" class="artdeco-input__suffix">
                <slot name="suffix" />
            </span>
        </div>

        <!-- Helper Text / Error Message -->
        <div v-if="helperText || errorMessage" class="artdeco-input__helper">
            <span v-if="errorMessage" class="artdeco-input__error">{{ errorMessage }}</span>
            <span v-else class="artdeco-input__helpertext">{{ helperText }}</span>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, useSlots } from 'vue'

    const slots = useSlots()

    // ============================================
    //   COMPONENT: ArtDecoInput
    //   Art Deco风格输入框组件
    //
    //   Design Philosophy:
    //   - Transparent background
    //   - Bottom border only (2px gold)
    //   - No side/top borders
    //   - Focus: brighter gold + glow shadow
    //   - Minimalist within maximalism
    //
    //   Usage:
    //   <ArtDecoInput v-model="text" label="Username" placeholder="Enter username" />
    // ============================================

    // ============================================
    //   PROPS - 组件属性
    // ============================================

    interface Props {
        /// Input value (v-model)
        modelValue: string | number

        /// Input label (uppercase, small font size)
        label?: string

        /// Placeholder text (muted gray)
        placeholder?: string

        /// Input type (text, password, email, number, etc.)
        type?: string

        /// Disabled state
        disabled?: boolean

        /// Readonly state
        readonly?: boolean

        /// Required field (shows asterisk)
        required?: boolean

        /// Max length
        maxlength?: number

        /// Helper text (displayed below input)
        helperText?: string

        /// Error message (overrides helper text, shown in red)
        errorMessage?: string

        /// Additional CSS classes
        class?: string

        /// Show clear button
        clearable?: boolean

        /// Input style variant
        /// - default: Bottom border only (underlined)
        /// - bordered: Full border (box)
        variant?: 'default' | 'bordered'
    }

    const props = withDefaults(defineProps<Props>(), {
        modelValue: '',
        label: '',
        placeholder: '',
        type: 'text',
        disabled: false,
        readonly: false,
        required: false,
        maxlength: undefined,
        helperText: '',
        errorMessage: '',
        class: '',
        clearable: false,
        variant: 'default'
    })

    // ============================================
    //   EMITS - 事件定义
    // ============================================

    const emit = defineEmits<{
        'update:modelValue': [value: string | number]
        focus: [event: FocusEvent]
        blur: [event: FocusEvent]
        enter: [event: KeyboardEvent]
    }>()

    // ============================================
    //   REFS - 响应式引用
    // ============================================

    const inputRef = ref<HTMLInputElement>()
    const isFocused = ref(false)

    // ============================================
    //   COMPUTED - 计算属性
    // ============================================

    /**
     * Generate unique input ID
     * 生成唯一输入框ID
     */
    const inputId = computed(() => {
        return `artdeco-input-${Math.random().toString(36).substr(2, 9)}`
    })

    /**
     * Generate wrapper CSS classes
     * 生成包装器CSS类名
     */
    const wrapperClasses = computed(() => {
        return [
            'artdeco-input',
            `artdeco-input--${props.variant}`,
            {
                'artdeco-input--disabled': props.disabled,
                'artdeco-input--error': props.errorMessage,
                'artdeco-input--focused': isFocused.value
            },
            props.class
        ]
    })

    /**
     * Generate input CSS classes
     * 生成输入框CSS类名
     */
    const inputClasses = computed(() => {
        return [
            'artdeco-input__field',
            {
                'artdeco-input__field--has-prefix': !!slots.prefix,
                'artdeco-input__field--has-suffix': !!slots.suffix
            }
        ]
    })

    // ============================================
    //   METHODS - 方法
    // ============================================

    /**
     * Handle input event
     * 处理输入事件
     */
    const handleInput = (event: Event): void => {
        const target = event.target as HTMLInputElement
        emit('update:modelValue', target.value)
    }

    /**
     * Handle focus event
     * 处理聚焦事件
     */
    const handleFocus = (event: FocusEvent): void => {
        isFocused.value = true
        emit('focus', event)
    }

    /**
     * Handle blur event
     * 处理失焦事件
     */
    const handleBlur = (event: FocusEvent): void => {
        isFocused.value = false
        emit('blur', event)
    }

    /**
     * Handle enter key press
     * 处理回车键按下
     */
    const handleEnter = (event: KeyboardEvent): void => {
        emit('enter', event)
    }

    // ============================================
    //   EXPOSE - 暴露方法
    // ============================================

    defineExpose({
        inputRef,
        focus: () => inputRef.value?.focus(),
        blur: () => inputRef.value?.blur()
    })
</script>

<style scoped lang="scss">
    // Import Art Deco tokens and patterns
    @import '@/styles/artdeco-tokens.scss';
    @import '@/styles/artdeco-patterns.scss';

    // ============================================
    //   BASE INPUT STYLES - 输入框基础样式
    //   Underlined elegance (minimalism within maximalism)
    // ============================================

    .artdeco-input {
        width: 100%;
        position: relative;
    }

    // ============================================
    //   LABEL STYLES - 标签样式
    //   Uppercase, small font size, gold color
    // ============================================

    .artdeco-input__label {
        // MANDATORY: Uppercase, small font size
        display: block;
        text-transform: uppercase;
        font-size: var(--artdeco-text-xs);
        letter-spacing: var(--artdeco-tracking-wide);

        // Gold color for active state
        color: var(--artdeco-accent-gold);

        // Spacing
        margin-bottom: var(--artdeco-spacing-2);

        // Transition
        transition: color var(--artdeco-duration-base);

        // Error state
        .artdeco-input--error & {
            color: var(--artdeco-color-up); // Red for error
        }
    }

    .artdeco-input__required {
        color: var(--artdeco-color-up); // Red asterisk
        margin-left: 2px;
    }

    // ============================================
    //   INPUT WRAPPER - 输入框包装器
    //   Contains input field and icons
    // ============================================

    .artdeco-input__wrapper {
        position: relative;
        display: flex;
        align-items: center;

        // MANDATORY: Bottom border only (2px gold)
        &::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 2px;
            background-color: var(--artdeco-border-gold-subtle);
            transition: all var(--artdeco-duration-base);
        }

        // Focus state: Border brightens + glow
        .artdeco-input--focused &::after {
            background-color: var(--artdeco-accent-gold);
            box-shadow: 0 4px 10px rgba(212, 175, 55, 0.2);
        }

        // Error state
        .artdeco-input--error &::after {
            background-color: var(--artdeco-color-up);
        }

        // BORDERED VARIANT OVERRIDES
        .artdeco-input--bordered & {
            border: 2px solid var(--artdeco-gold-dim);
            background-color: var(--artdeco-bg-card);
            transition: all var(--artdeco-duration-base);
        }

        .artdeco-input--bordered &::after {
            display: none; // Remove bottom border
        }

        .artdeco-input--bordered.artdeco-input--focused & {
            border-color: var(--artdeco-accent-gold);
            box-shadow: var(--artdeco-glow-subtle);
        }
    }

    // ============================================
    //   INPUT FIELD - 输入框字段
    //   Transparent bg, bottom border only, no side/top borders
    // ============================================

    .artdeco-input__field {
        // MANDATORY: Transparent background
        background-color: transparent;

        // MANDATORY: No side or top borders
        border: none;
        border-top: none;
        border-left: none;
        border-right: none;

        // Bottom border is handled by wrapper::after

        // Typography
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-base);
        color: var(--artdeco-fg-primary);

        // Height and padding
        height: var(--artdeco-input-height);
        padding: var(--artdeco-input-padding-y) var(--artdeco-input-padding-x);
        line-height: var(--artdeco-leading-normal);

        // Width
        width: 100%;

        // Focus states (remove default outline)
        outline: none;

        // Placeholder
        &::placeholder {
            color: var(--artdeco-fg-muted);
        }

        // Disabled state
        .artdeco-input--disabled & {
            color: var(--artdeco-fg-muted);
            cursor: not-allowed;
        }

        // Error state
        .artdeco-input--error & {
            color: var(--artdeco-color-up);
        }

        // With prefix/suffix padding adjustment
        &--has-prefix {
            padding-left: calc(var(--artdeco-input-padding-x) * 2 + 16px);
        }

        &--has-suffix {
            padding-right: calc(var(--artdeco-input-padding-x) * 2 + 16px);
        }
    }

    // ============================================
    //   PREFIX / SUFFIX ICONS - 前缀/后缀图标
    // ============================================

    .artdeco-input__prefix,
    .artdeco-input__suffix {
        position: absolute;
        display: flex;
        align-items: center;
        color: var(--artdeco-fg-muted);
        pointer-events: none;
    }

    .artdeco-input__prefix {
        left: var(--artdeco-input-padding-x);
    }

    .artdeco-input__suffix {
        right: var(--artdeco-input-padding-x);
    }

    // ============================================
    //   HELPER TEXT / ERROR MESSAGE - 辅助文本
    // ============================================

    .artdeco-input__helper {
        margin-top: var(--artdeco-spacing-2);
        min-height: 18px;
        font-size: var(--artdeco-text-xs);
    }

    .artdeco-input__helpertext {
        color: var(--artdeco-fg-muted);
        font-family: var(--artdeco-font-body);
    }

    .artdeco-input__error {
        color: var(--artdeco-color-up); // Red for error
        font-family: var(--artdeco-font-body);
    }

    // ============================================
    //   DESIGN NOTE - 设计说明
    //   本项目仅支持桌面端，不包含移动端响应式代码
    // ============================================
</style>
