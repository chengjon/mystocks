<template>
    <div class="artdeco-header">
        <div class="header-content">
            <h1 class="header-title" v-if="title">{{ title }}</h1>
            <div class="logo" v-else></div>
            <p class="header-subtitle" v-if="subtitle">{{ subtitle }}</p>
        </div>
        
        <div class="header-right">
            <div v-if="showStatus" class="status-indicator">
                <span class="status-dot"></span>
                <span class="status-text">{{ statusText }}</span>
            </div>
            <div class="actions">
                <slot name="actions"></slot>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    defineProps<{
        title?: string
        subtitle?: string
        showStatus?: boolean
        statusText?: string
    }>()
</script>

<style scoped lang="scss">
    .artdeco-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--artdeco-spacing-4) var(--artdeco-spacing-6);
        background: var(--artdeco-bg-surface);
        border-bottom: calc(var(--artdeco-spacing-px) + var(--artdeco-spacing-px)) solid var(--artdeco-border-default);
        position: relative;

        &::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--artdeco-gold-primary), transparent);
            opacity: 30%;
        }
    }

    .header-content {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-1);
    }

    .header-title {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-text-xl);
        font-weight: 700;
        color: var(--artdeco-gold-primary);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-widest);
        margin: 0;
    }

    .logo {
        font-family: var(--artdeco-font-display);
        font-size: var(--artdeco-text-lg);
        font-weight: 700;
        color: var(--artdeco-gold-primary);
        letter-spacing: var(--artdeco-tracking-wider);
    }

    .header-subtitle {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-muted);
        margin: 0;
    }

    .header-right {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-6);
    }

    .status-indicator {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-2);
        padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
        background: var(--artdeco-gold-opacity-05);
        border: 1px solid var(--artdeco-border-default);
    }

    .status-dot {
        width: var(--artdeco-spacing-2);
        height: var(--artdeco-spacing-2);
        background: var(--artdeco-gold-primary);
        box-shadow: 0 0 var(--artdeco-spacing-2) var(--artdeco-gold-primary);
    }

    .status-text {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-gold-primary);
        text-transform: uppercase;
    }

    .actions {
        display: flex;
        gap: var(--artdeco-spacing-3);
    }
</style>
