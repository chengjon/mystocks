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
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-switch-wrapper {
      display: inline-flex;
      align-items: center;
      gap: var(--artdeco-spacing-3);
      cursor: pointer;
      user-select: none;
    }

    .artdeco-switch-wrapper.is-disabled {
      cursor: not-allowed;
      opacity: 0.5;
    }

    .artdeco-switch-label {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      letter-spacing: 1px;
      color: var(--artdeco-fg-muted);
      text-transform: uppercase;
    }

    .artdeco-switch {
      display: inline-block;
      width: 48px;
      height: 24px;
      position: relative;
    }

    .artdeco-switch-track {
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: #1A2026;
      border: 1px solid rgba(212, 175, 55, 0.2);
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-switch-thumb {
      position: absolute;
      top: 2px;
      left: 2px;
      width: 18px;
      height: 18px;
      background: var(--artdeco-silver-dim);
      border: 1px solid #000;
      transition: all 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
      box-shadow: 0 0 5px rgba(0,0,0,0.5);
      z-index: 2;
    }

    /* Active State */
    .artdeco-switch.active .artdeco-switch-track {
      background: rgba(212, 175, 55, 0.15);
      border-color: var(--artdeco-accent-gold);
    }

    .artdeco-switch.active .artdeco-switch-thumb {
      left: 26px;
      background: var(--artdeco-accent-gold);
      box-shadow: 0 0 10px var(--artdeco-accent-gold);
    }

    .artdeco-switch-status {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-sm) // 12px - Compact v3.1;
      font-weight: 600;
      min-width: 25px;
    }

    .text-gold { color: var(--artdeco-accent-gold); }
    .text-dim { color: var(--artdeco-fg-muted); }
</style>
