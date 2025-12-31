<template>
  <div :class="wrapperClasses">
    <!-- Label -->
    <label v-if="label" :for="inputId" class="web3-input-label">
      {{ label }}
      <span v-if="required" class="web3-input-required">*</span>
    </label>

    <!-- Input wrapper -->
    <div class="web3-input-wrapper">
      <!-- Prefix slot -->
      <div v-if="$slots.prefix || prefix" class="web3-input-prefix">
        <slot name="prefix">
          <span class="web3-input-prefix-text">{{ prefix }}</span>
        </slot>
      </div>

      <!-- Input element -->
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
        @keydown="handleKeydown"
      />

      <!-- Suffix slot -->
      <div v-if="$slots.suffix || suffix || showClearButton" class="web3-input-suffix">
        <slot name="suffix">
          <span v-if="suffix" class="web3-input-suffix-text">{{ suffix }}</span>
          <button
            v-if="showClearButton && modelValue"
            type="button"
            class="web3-input-clear"
            @click="handleClear"
          >
            ×
          </button>
        </slot>
      </div>
    </div>

    <!-- Helper text / error message -->
    <div v-if="helperText || errorMessage" class="web3-input-helper">
      <span v-if="errorMessage" class="web3-input-error">{{ errorMessage }}</span>
      <span v-else class="web3-input-helper-text">{{ helperText }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick } from 'vue'

// ============================================
//   COMPONENT: Web3Input
//   Bitcoin DeFi Web3 Input Component
//
//   Design Philosophy:
//   - Minimalist design
//   - Bottom-border only
//   - Orange focus glow
//   - Monospace font for values
//   - Glass morphism background
// ============================================

// ============================================
//   INTERFACE - 接口定义
// ============================================

interface Props {
  modelValue?: string | number
  type?: string
  label?: string
  placeholder?: string
  prefix?: string
  suffix?: string
  helperText?: string
  errorMessage?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  maxlength?: number
  clearable?: boolean
  size?: 'sm' | 'md' | 'lg'
}

interface Emits {
  (e: 'update:modelValue', value: string | number): void
  (e: 'focus', event: FocusEvent): void
  (e: 'blur', event: FocusEvent): void
  (e: 'clear'): void
  (e: 'keydown', event: KeyboardEvent): void
}

// ============================================
//   PROPS & EMITS - 属性与事件
// ============================================

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  disabled: false,
  readonly: false,
  required: false,
  clearable: false,
  size: 'md'
})

const emit = defineEmits<Emits>()

// ============================================
//   STATE - 响应式状态
// ============================================

const inputRef = ref<HTMLInputElement>()
const isFocused = ref(false)

// ============================================
//   COMPUTED - 计算属性
// ============================================

const inputId = computed(() => {
  return `web3-input-${Math.random().toString(36).substr(2, 9)}`
})

const inputClasses = computed(() => {
  return [
    'web3-input-field',
    `web3-input-field--${props.size}`,
    {
      'web3-input-field--focused': isFocused.value,
      'web3-input-field--error': props.errorMessage,
      'web3-input-field--disabled': props.disabled
    }
  ]
})

const wrapperClasses = computed(() => {
  return [
    'web3-input-wrapper',
    `web3-input-wrapper--${props.size}`
  ]
})

const showClearButton = computed(() => {
  return props.clearable && !props.disabled && !props.readonly
})

// ============================================
//   METHODS - 方法
// ============================================

const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  emit('update:modelValue', target.value)
}

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event: FocusEvent) => {
  isFocused.value = false
  emit('blur', event)
}

const handleClear = () => {
  emit('update:modelValue', '')
  emit('clear')
  nextTick(() => {
    inputRef.value?.focus()
  })
}

const handleKeydown = (event: KeyboardEvent) => {
  emit('keydown', event)
}

// Focus method (expose to parent)
const focus = () => {
  inputRef.value?.focus()
}

// Blur method (expose to parent)
const blur = () => {
  inputRef.value?.blur()
}

// Expose methods
defineExpose({
  focus,
  blur
})
</script>

<style scoped lang="scss">
@import '@/styles/web3-tokens.scss';

// ============================================
//   WRAPPER - 包装器
// ============================================

.web3-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--web3-spacing-2);
  width: 100%;
}

// ============================================
//   LABEL - 标签
// ============================================

.web3-input-label {
  // Heading font (Space Grotesk)
  font-family: var(--web3-font-heading);
  font-size: var(--web3-text-sm);
  font-weight: var(--web3-weight-semibold);
  color: var(--web3-fg-secondary);
  text-transform: uppercase;
  letter-spacing: var(--web3-tracking-wide);
  display: flex;
  align-items: center;
  gap: var(--web3-spacing-1);
}

.web3-input-required {
  color: var(--web3-accent-primary);
  font-size: var(--web3-text-lg);
}

// ============================================
//   INPUT WRAPPER - 输入框包装器
//   Glass morphism, bottom border
// ============================================

.web3-input-wrapper {
  position: relative;
  display: flex;
  align-items: stretch;
  gap: var(--web3-spacing-2);
}

.web3-input-field {
  // MANDATORY: Glass morphism background
  background: var(--web3-bg-glass-dark);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);

  // Font
  font-family: var(--web3-font-body);
  font-size: var(--web3-text-base);
  font-weight: var(--web3-weight-normal);
  color: var(--web3-fg-primary);

  // MANDATORY: Bottom border only
  border: none;
  border-bottom: 2px solid var(--web3-border-subtle);
  border-radius: var(--web3-radius-sm);

  // Padding
  padding: var(--web3-spacing-3) var(--web3-spacing-4);

  // Width
  width: 100%;

  // Transitions
  transition: all var(--web3-duration-base) var(--web3-ease-out);

  // Placeholder
  &::placeholder {
    color: var(--web3-fg-muted);
  }

  // Hover
  &:hover:not(:disabled):not(.web3-input-field--readonly) {
    background: rgba(0, 0, 0, 0.6);
  }

  // Focus state
  &--focused {
    // MANDATORY: Orange border
    border-bottom-color: var(--web3-accent-primary);

    // MANDATORY: Orange glow
    box-shadow: var(--web3-glow-orange-sm);

    background: var(--web3-bg-glass-dark);
  }

  // Error state
  &--error {
    border-bottom-color: #EF4444;

    &:focus {
      box-shadow: 0 0 20px -5px rgba(239, 68, 68, 0.5);
    }
  }

  // Disabled state
  &:disabled,
  &--readonly {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

// ============================================
//   SIZE VARIANTS - 尺寸变体
// ============================================

.web3-input-field--sm {
  font-size: var(--web3-text-sm);
  padding: var(--web3-spacing-2) var(--web3-spacing-3);
  min-height: 32px;
}

.web3-input-field--md {
  font-size: var(--web3-text-base);
  padding: var(--web3-spacing-3) var(--web3-spacing-4);
  min-height: 40px;
}

.web3-input-field--lg {
  font-size: var(--web3-text-lg);
  padding: var(--web3-spacing-4) var(--web3-spacing-5);
  min-height: 48px;
}

// ============================================
//   PREFIX & SUFFIX - 前缀与后缀
// ============================================

.web3-input-prefix,
.web3-input-suffix {
  display: flex;
  align-items: center;
  gap: var(--web3-spacing-2);
  color: var(--web3-fg-muted);
  font-size: var(--web3-text-sm);
}

.web3-input-prefix-text,
.web3-input-suffix-text {
  font-family: var(--web3-font-mono);
}

.web3-input-clear {
  background: transparent;
  border: none;
  color: var(--web3-fg-muted);
  font-size: var(--web3-text-xl);
  cursor: pointer;
  padding: 0 var(--web3-spacing-2);
  transition: color var(--web3-duration-base);

  &:hover {
    color: var(--web3-accent-primary);
  }
}

// ============================================
//   HELPER TEXT - 辅助文本
// ============================================

.web3-input-helper {
  display: flex;
  align-items: center;
  min-height: 20px;
}

.web3-input-helper-text {
  font-size: var(--web3-text-xs);
  color: var(--web3-fg-muted);
}

.web3-input-error {
  font-size: var(--web3-text-xs);
  color: #EF4444;
}

// ============================================
//   MONOSPaced VARIANT FOR VALUES
//   For numeric/financial inputs
// ============================================

.web3-input-field[type="number"],
.web3-input-field[data-mono="true"] {
  font-family: var(--web3-font-mono);
  letter-spacing: var(--web3-tracking-tight);
}

// ============================================
//   RESPONSIVE - 响应式
// ============================================

@media (max-width: 768px) {
  .web3-input-field {
    font-size: var(--web3-text-sm);
  }
}
</style>
