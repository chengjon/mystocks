<template>
    <div class="artdeco-select" :class="sizeClass">
        <select :value="modelValue" @input="handleInput" :disabled="disabled" :placeholder="placeholder">
            <option v-if="placeholder && !modelValue" value="" disabled selected>
                {{ placeholder }}
            </option>
            <option v-for="option in options" :key="option.value" :value="option.value" :disabled="option.disabled">
                {{ option.label }}
            </option>
        </select>
        <div class="artdeco-select-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { computed } from 'vue'

    interface Option {
        label: string
        value: string | number
        disabled?: boolean
    }

    interface Props {
        modelValue: string | number
        options: Option[]
        placeholder?: string
        disabled?: boolean
        size?: 'sm' | 'md' | 'lg'
    }

    const props = withDefaults(defineProps<Props>(), {
        placeholder: '',
        disabled: false,
        size: 'md'
    })

    const emit = defineEmits<{
        'update:modelValue': [value: string | number]
    }>()

    const sizeClass = computed(() => {
        return `artdeco-select-${props.size}`
    })

    function handleInput(event: Event) {
        const target = event.target as HTMLSelectElement
        emit('update:modelValue', target.value)
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-select {
      position: relative;
      display: inline-block;
      width: 100%;
    }

    .artdeco-select select {
      width: 100%;
      padding: 10px 40px 10px 12px;
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      font-weight: 500;
      color: var(--artdeco-fg-secondary);
      background: var(--artdeco-bg-card);
      border: 1px solid rgba(212, 175, 55, 0.2);
      border-radius: var(--artdeco-radius-none);
      cursor: pointer;
      appearance: none;
      -webkit-appearance: none;
      -moz-appearance: none;
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-select select:hover {
      border-color: var(--artdeco-accent-gold);
    }

    .artdeco-select select:focus {
      outline: none;
      border-color: var(--artdeco-accent-gold);
      box-shadow: var(--artdeco-glow-subtle);
    }

    .artdeco-select select:disabled {
      opacity: 0.5;
      cursor: not-allowed;
      background: var(--artdeco-bg-header);
    }

    .artdeco-select select option {
      background: var(--artdeco-bg-card);
      color: var(--artdeco-fg-secondary);
      padding: var(--artdeco-spacing-2);
    }

    .artdeco-select-icon {
      position: absolute;
      right: 12px;
      top: 50%;
      transform: translateY(-50%);
      width: 16px;
      height: 16px;
      color: var(--artdeco-accent-gold);
      pointer-events: none;
      transition: transform var(--artdeco-transition-base);
    }

    .artdeco-select:hover .artdeco-select-icon {
      transform: translateY(-50%) scale(1.1);
    }

    /* Size Variants */
    .artdeco-select-sm select {
      padding: 6px 32px 6px 10px;
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
    }

    .artdeco-select-sm .artdeco-select-icon {
      width: 14px;
      height: 14px;
      right: 10px;
    }

    .artdeco-select-lg select {
      padding: 14px 48px 14px 16px;
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
    }

    .artdeco-select-lg .artdeco-select-icon {
      width: 18px;
      height: 18px;
      right: 16px;
    }
</style>
