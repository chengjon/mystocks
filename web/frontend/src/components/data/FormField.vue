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
    'form-field-input--has-suffix': !!slots.suffix
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
.form-field-wrapper {
  width: 100%;
}

.form-field-label {
  display: block;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 12px;
  font-weight: 500;
  color: #E5E5E5;
  margin-bottom: 6px;
}

.form-field-required {
  color: #FF5252;
  margin-left: 2px;
}

.form-field-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;

  // 底部边框
  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 1px;
    background-color: #2A2A2A;
    transition: background-color 150ms ease;
  }

  // Focus state
  .form-field-input:focus ~ &::after {
    background-color: #3B82F6;
  }

  // Error state
  .form-field-input--error ~ &::after {
    background-color: #FF5252;
  }
}

.form-field-input {
  width: 100%;
  height: 32px; // 紧凑高度
  padding: 0 12px;
  font-family: 'Inter', system-ui, sans-serif;
  font-size: 13px;
  color: #E5E5E5;
  background: #0A0A0A;
  border: 1px solid #2A2A2A;
  border-radius: 4px;
  outline: none;
  transition: border-color 150ms ease, background 150ms ease;

  &::placeholder {
    color: #666666;
  }

  &:focus {
    border-color: #3B82F6;
    background: #0F0F0F;
  }

  &:disabled {
    color: #666666;
    cursor: not-allowed;
    background: #0A0A0A;
  }

  &:read-only {
    color: #A0A0A0;
  }

  // With prefix/suffix
  &--has-prefix {
    padding-left: 36px;
  }

  &--has-suffix {
    padding-right: 36px;
  }
}

.form-field-prefix,
.form-field-suffix {
  position: absolute;
  display: flex;
  align-items: center;
  color: #A0A0A0;
  pointer-events: none;
}

.form-field-prefix {
  left: 12px;
}

.form-field-suffix {
  right: 12px;
}

.form-field-helper {
  margin-top: 6px;
  min-height: 16px;
  font-size: 12px;
}

.form-field-helpertext {
  color: #A0A0A0;
}

.form-field-error {
  color: #FF5252;
}
</style>
