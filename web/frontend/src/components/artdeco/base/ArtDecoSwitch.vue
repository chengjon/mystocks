<template>
    <div class="artdeco-switch-wrapper" :class="{ 'is-disabled': disabled }" @click="toggle">
        <label v-if="label" class="artdeco-switch-label">{{ label }}</label>
        <div class="artdeco-switch" :class="{ active: modelValue }">
            <div class="artdeco-switch-track"></div>
            <div class="artdeco-switch-thumb"></div>
        </div>
        <span v-if="showStatus" class="artdeco-switch-status" :class="modelValue ? 'text-gold' : 'text-dim'">
            {{ modelValue ? onText : offText }}
        </span>
    </div>
</template>

<script setup lang="ts">
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
        onText: 'ON',
        offText: 'OFF'
    })

    const emit = defineEmits<{
        'update:modelValue': [value: boolean]
        change: [value: boolean]
    }>()

    function toggle() {
        if (props.disabled) return
        const newValue = !props.modelValue
        emit('update:modelValue', newValue)
        emit('change', newValue)
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens';

    .artdeco-switch-wrapper {
      display: inline-flex;
      align-items: center;
      gap: var(--artdeco-spacing-3);
      cursor: pointer;
      user-select: none;
    }

    .artdeco-switch-wrapper.is-disabled {
      cursor: not-allowed;
      opacity: 50%;
    }

    .artdeco-switch-label {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-sm);
      letter-spacing: 1px;
      color: var(--artdeco-fg-muted);
      text-transform: uppercase;
    }

    .artdeco-switch {
      display: inline-block;
      width: var(--artdeco-spacing-12);
      height: var(--artdeco-spacing-6);
      position: relative;
    }

    .artdeco-switch-track {
      position: absolute;
      inset: 0 0 0 0;
      background: var(--artdeco-bg-secondary);
      border: 1px solid var(--artdeco-gold-opacity-20);
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-switch-thumb {
      position: absolute;
      top: calc(var(--artdeco-spacing-1) / 2);
      left: calc(var(--artdeco-spacing-1) / 2);
      width: calc(var(--artdeco-spacing-4) + calc(var(--artdeco-spacing-1) / 2));
      height: calc(var(--artdeco-spacing-4) + calc(var(--artdeco-spacing-1) / 2));
      background: var(--artdeco-silver-dim);
      border: 1px solid var(--artdeco-bg-global);
      transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
      box-shadow: 0 0 calc(var(--artdeco-spacing-5) / 4) color-mix(in srgb, var(--artdeco-bg-global) 50%, transparent);
      z-index: 2;
    }

    /* Active State */
    .artdeco-switch.active .artdeco-switch-track {
      background: color-mix(in srgb, var(--artdeco-accent-gold) 15%, transparent);
      border-color: var(--artdeco-accent-gold);
    }

    .artdeco-switch.active .artdeco-switch-thumb {
      left: calc(var(--artdeco-spacing-6) + calc(var(--artdeco-spacing-1) / 2));
      background: var(--artdeco-accent-gold);
      box-shadow: 0 0 calc(var(--artdeco-spacing-5) / 2) var(--artdeco-accent-gold);
    }

    .artdeco-switch-status {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-sm);
      font-weight: 600;
      min-width: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-px));
    }

    .text-gold { color: var(--artdeco-accent-gold); }
    .text-dim { color: var(--artdeco-fg-muted); }
</style>
