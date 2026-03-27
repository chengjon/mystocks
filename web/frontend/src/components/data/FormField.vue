<template>
  <div class="form-field-wrapper">
    <!-- Label -->
    <label v-if="label" :for="inputId" class="form-field-label">
      {{ label }}
      <span v-if="required" class="form-field-required">*</span>
    </label>

    <!-- Input Wrapper -->
    <div class="form-field-input-wrapper">
      <!-- Prefix Icon -->
      <span v-if="$slots.prefix" class="form-field-prefix">
        <slot name="prefix"></slot>
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
      >

      <!-- Suffix Icon -->
      <span v-if="slots.suffix || clearable" class="form-field-suffix">
        <slot name="suffix"></slot>
      </span>
    </div>

    <!-- Helper Text / Error Message -->
    <div v-if="helperText || errorMessage" class="form-field-helper">
      <span v-if="errorMessage" class="form-field-error">{{ errorMessage }}</span>
      <span v-else class="form-field-helpertext">{{ helperText }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, useSlots } from 'vue'

const slots = useSlots()

interface Props {
  modelValue: string | number
  label?: string
  placeholder?: string
  type?: string
  disabled?: boolean
  readonly?: boolean
  required?: boolean
  maxlength?: number
  helperText?: string
  errorMessage?: string
  class?: string
  clearable?: boolean
}

const _props = withDefaults(defineProps<Props>(), {
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
  clearable: false
})

const emit = defineEmits<{
  'update:modelValue': [value: string | number]
  focus: [event: FocusEvent]
  blur: [event: FocusEvent]
}>()

const inputRef = ref<HTMLInputElement>()
const isFocused = ref(false)

const inputId = computed(() => {
  return `form-field-${Math.random().toString(36).substr(2, 9)}`
})

const inputClasses = computed(() => [
  'form-field-input',
  {
    'form-field-input--has-prefix': !!slots.prefix,
    'form-field-input--has-suffix': !!slots.suffix,
    'form-field-input--error': !!_props.errorMessage
  }
])

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

defineExpose({
  inputRef,
  focus: () => inputRef.value?.focus(),
  blur: () => inputRef.value?.blur()
})
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.form-field-wrapper {
  width: 100%;
}

.form-field-label {
  display: block;
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-compact-sm);
  font-weight: var(--artdeco-font-medium);
  color: var(--artdeco-gold-primary);
  margin-bottom: calc(var(--artdeco-spacing-1) + (var(--artdeco-spacing-px) * 2));
  text-transform: uppercase;
  letter-spacing: var(--artdeco-tracking-wide);
}

.form-field-required {
  color: var(--artdeco-rise);
  margin-left: var(--artdeco-spacing-px);
}

.form-field-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: linear-gradient(
    180deg,
    color-mix(in srgb, var(--artdeco-bg-elevated) 55%, var(--artdeco-bg-card)) 0%,
    var(--artdeco-bg-card) 100%
  );
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-none);
  transition:
    border-color var(--artdeco-transition-quick) var(--artdeco-ease-out),
    box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out),
    background var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &:focus-within {
    border-color: var(--artdeco-border-hover);
    box-shadow: var(--artdeco-glow-subtle);
  }

  &:has(.form-field-input--error) {
    border-color: color-mix(in srgb, var(--artdeco-rise) 60%, var(--artdeco-border-default));
    box-shadow: 0 0 var(--artdeco-spacing-3) color-mix(in srgb, var(--artdeco-rise) 16%, transparent);
  }
}

.form-field-input {
  width: 100%;
  height: var(--artdeco-spacing-8);
  padding: 0 var(--artdeco-spacing-3);
  font-family: var(--artdeco-font-body, var(--font-body));
  font-size: var(--artdeco-text-compact-base);
  color: var(--artdeco-fg-primary);
  background: transparent;
  border: none;
  border-radius: var(--artdeco-radius-none);
  outline: none;
  line-height: var(--artdeco-leading-normal);
  transition: color var(--artdeco-transition-quick) var(--artdeco-ease-out);

  &::placeholder {
    color: var(--artdeco-fg-subtle);
  }

  &:focus {
    background: transparent;
  }

  &:disabled {
    color: var(--artdeco-fg-muted);
    cursor: not-allowed;
    background: transparent;
  }

  &:read-only {
    color: var(--artdeco-fg-muted);
  }

  &--has-prefix {
    padding-left: calc(var(--artdeco-spacing-8) + var(--artdeco-spacing-1));
  }

  &--has-suffix {
    padding-right: calc(var(--artdeco-spacing-8) + var(--artdeco-spacing-1));
  }
}

.form-field-prefix,
.form-field-suffix {
  position: absolute;
  display: flex;
  align-items: center;
  color: var(--artdeco-gold-dim);
  pointer-events: none;
}

.form-field-prefix {
  left: var(--artdeco-spacing-3);
}

.form-field-suffix {
  right: var(--artdeco-spacing-3);
}

.form-field-helper {
  margin-top: calc(var(--artdeco-spacing-1) + (var(--artdeco-spacing-px) * 2));
  min-height: var(--artdeco-spacing-4);
  font-size: var(--artdeco-text-compact-sm);
  letter-spacing: var(--artdeco-tracking-normal);
}

.form-field-helpertext {
  color: var(--artdeco-fg-muted);
}

.form-field-error {
  color: var(--artdeco-rise);
}
</style>
