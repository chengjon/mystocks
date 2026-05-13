<template>
    <div class="artdeco-select" :class="sizeClass">
        <select
            :value="modelValue"
            @input="handleInput"
            :disabled="disabled"
            :placeholder="placeholder"
            :aria-label="accessibleName"
            :aria-disabled="disabled ? 'true' : undefined"
        >
            <option v-if="placeholder && !modelValue" value="" disabled selected>
                {{ placeholder }}
            </option>
            <option v-for="option in options" :key="option.value" :value="option.value" :disabled="option.disabled">
                {{ option.label }}
            </option>
        </select>
        <div class="artdeco-select-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" focusable="false">
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
        label?: string
        ariaLabel?: string
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

    const accessibleName = computed(() => {
        return props.ariaLabel || props.label || props.placeholder || undefined
    })

    function handleInput(event: Event) {
        const target = event.target as HTMLSelectElement
        emit('update:modelValue', target.value)
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens';

    .artdeco-select {
      position: relative;
      display: inline-block;
      width: 100%;
    }

    .artdeco-select select {
      width: 100%;
      padding:
        calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px))
        var(--artdeco-spacing-10)
        calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px))
        var(--artdeco-spacing-3);
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-base); // Compact base size
      font-weight: 500;
      color: var(--artdeco-fg-secondary);
      background: var(--artdeco-bg-card);
      border: 1px solid var(--artdeco-gold-opacity-20);
      border-radius: var(--artdeco-radius-none);
      cursor: pointer;
      appearance: none;
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
      opacity: 50%;
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
      right: var(--artdeco-spacing-3);
      top: 50%;
      transform: translateY(-50%);
      width: var(--artdeco-spacing-4);
      height: var(--artdeco-spacing-4);
      color: var(--artdeco-accent-gold);
      pointer-events: none;
      transition: transform var(--artdeco-transition-base);
    }

    .artdeco-select:hover .artdeco-select-icon {
      transform: translateY(-50%) scale(1.1);
    }

    /* Size Variants */
    .artdeco-select-sm select {
      padding:
        calc(var(--artdeco-spacing-2) - var(--artdeco-radius-sm))
        var(--artdeco-spacing-8)
        calc(var(--artdeco-spacing-2) - var(--artdeco-radius-sm))
        calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
      font-size: var(--artdeco-font-size-sm); // Compact small size
    }

    .artdeco-select-sm .artdeco-select-icon {
      width: calc(var(--artdeco-spacing-3) + var(--artdeco-radius-sm));
      height: calc(var(--artdeco-spacing-3) + var(--artdeco-radius-sm));
      right: calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px));
    }

    .artdeco-select-lg select {
      padding:
        calc(var(--artdeco-spacing-3) + var(--artdeco-radius-sm))
        calc(var(--artdeco-spacing-12) + var(--artdeco-spacing-px) + var(--artdeco-spacing-px))
        calc(var(--artdeco-spacing-3) + var(--artdeco-radius-sm))
        var(--artdeco-spacing-4);
      font-size: var(--artdeco-font-size-base); // Compact base size
    }

    .artdeco-select-lg .artdeco-select-icon {
      width: calc(var(--artdeco-spacing-4) + var(--artdeco-radius-sm));
      height: calc(var(--artdeco-spacing-4) + var(--artdeco-radius-sm));
      right: var(--artdeco-spacing-4);
    }
</style>
