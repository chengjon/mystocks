<template>
    <div class="network-error-page">
        <div class="error-card">
            <div class="error-content">
                <div class="error-icon">📡</div>
                <div class="error-code">NETWORK</div>
                <div class="error-title">网络连接失败</div>
                <div class="error-description">无法连接到服务器，请检查网络连接或稍后再试</div>

                <div class="network-status" v-if="!isOnline">
                    <div class="status-indicator offline">
                        <span class="dot"></span>
                        当前状态: 离线
                    </div>
                </div>

                <div class="error-actions">
                    <button class="button primary" @click="retryConnection" :disabled="retrying">
                        <span v-if="retrying" class="loading-spinner"></span>
                        {{ retrying ? '重试中...' : '重试连接' }}
                    </button>
                    <button class="button secondary" @click="goHome">返回首页</button>
                </div>

                <div class="troubleshooting">
                    <details>
                        <summary>故障排除提示</summary>
                        <ul>
                            <li>检查网络连接是否正常</li>
                            <li>尝试刷新页面</li>
                            <li>清除浏览器缓存</li>
                            <li>联系技术支持</li>
                        </ul>
                    </details>
                </div>
            </div>

            <div class="error-illustration">
                <svg
                    width="200"
                    height="200"
                    viewBox="0 0 24 24"
                    fill="none"
                    :stroke="'var(--gold-muted)'"
                    stroke-width="1"
                >
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" />
                    <path d="M12 6v6m0 4h.01" />
                    <circle cx="12" cy="18" r="1" />
                </svg>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, onMounted } from 'vue'
    import { useRouter } from 'vue-router'
    import { useNetworkStatus } from '@/composables/useNetworkStatus'

    const router = useRouter()
    const { isOnline } = useNetworkStatus()

    const retrying = ref(false)

    const retryConnection = async () => {
        retrying.value = true

        try {
            // 尝试连接到健康检查端点
            const response = await fetch('/health', {
                method: 'GET',
                cache: 'no-cache'
            })

            if (response.ok) {
                // 连接成功，刷新页面
                window.location.reload()
            } else {
                throw new Error('连接失败')
            }
        } catch (error) {
            console.error('重试连接失败:', error)
            // 保持在当前页面，让用户手动操作
        } finally {
            retrying.value = false
        }
    }

    const goHome = () => {
        router.push('/')
    }

    onMounted(() => {
        // 如果网络恢复，自动重定向
        const checkOnline = () => {
            if (isOnline.value) {
                router.push('/')
            }
        }

        // 每5秒检查一次网络状态
        const interval = setInterval(checkOnline, 5000)

        // 组件卸载时清理定时器
        return () => clearInterval(interval)
    })
</script>

<style scoped lang="scss">
@use '../../styles/artdeco-tokens.scss' as *;

.network-error-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--artdeco-spacing-5);
    background: var(--artdeco-bg-global);
    background-image:
        linear-gradient(180deg, color-mix(in srgb, var(--artdeco-gold-primary) 6%, transparent), transparent 40%),
        repeating-linear-gradient(
            45deg,
            transparent,
            transparent var(--artdeco-spacing-5),
            var(--artdeco-gold-opacity-05) var(--artdeco-spacing-5),
            var(--artdeco-gold-opacity-05) calc(var(--artdeco-spacing-5) + var(--artdeco-spacing-px))
        );
}

.error-card {
    position: relative;
    z-index: 1;
    display: flex;
    gap: calc(var(--artdeco-spacing-16) - var(--artdeco-spacing-1));
    align-items: center;
    width: 100%;
    max-width: 56.25rem;
    padding: calc(var(--artdeco-spacing-12) + var(--artdeco-spacing-3));
    background: color-mix(in srgb, var(--artdeco-gold-primary) 4%, var(--artdeco-bg-card));
    border: 1px solid var(--artdeco-border-default);
    box-shadow: var(--artdeco-shadow-lg);
}

.error-card::before,
.error-card::after {
    content: '';
    position: absolute;
    width: var(--artdeco-spacing-5);
    height: var(--artdeco-spacing-5);
    border: calc(var(--artdeco-spacing-px) * 3) solid var(--artdeco-gold-primary);
}

.error-card::before {
    top: var(--artdeco-spacing-4);
    left: var(--artdeco-spacing-4);
    border-right: none;
    border-bottom: none;
}

.error-card::after {
    right: var(--artdeco-spacing-4);
    bottom: var(--artdeco-spacing-4);
    border-top: none;
    border-left: none;
}

.error-content {
    flex: 1;
}

.error-icon {
    margin-bottom: var(--artdeco-spacing-5);
    font-size: var(--artdeco-text-4xl);
    text-align: center;
}

.error-code {
    margin-bottom: var(--artdeco-spacing-4);
    color: var(--artdeco-gold-primary);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-size: var(--artdeco-text-xl);
    font-weight: var(--artdeco-font-bold);
    letter-spacing: calc(var(--artdeco-spacing-px) * 2);
    text-transform: uppercase;
}

.error-title {
    margin-bottom: var(--artdeco-spacing-4);
    color: var(--artdeco-fg-primary);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-size: var(--artdeco-text-3xl);
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: calc(var(--artdeco-spacing-px) * 3);
    text-transform: uppercase;
}

.error-description {
    margin-bottom: calc(var(--artdeco-spacing-10) + var(--artdeco-spacing-px) * 2);
    color: var(--artdeco-fg-muted);
    font-family: var(--artdeco-font-body, var(--font-body));
    font-size: var(--artdeco-text-base);
    line-height: var(--artdeco-leading-relaxed);
}

.network-status {
    margin-bottom: calc(var(--artdeco-spacing-10) + var(--artdeco-spacing-px) * 2);
}

.status-indicator {
    display: inline-flex;
    align-items: center;
    gap: var(--artdeco-spacing-2);
    padding: var(--artdeco-spacing-2) var(--artdeco-spacing-4);
    font-size: var(--artdeco-text-sm);
    font-weight: var(--artdeco-font-medium);
}

.status-indicator.offline {
    background: color-mix(in srgb, var(--artdeco-down) 10%, var(--artdeco-bg-card));
    color: var(--artdeco-down);
    border: 1px solid color-mix(in srgb, var(--artdeco-down) 20%, transparent);
}

.dot {
    width: var(--artdeco-spacing-2);
    height: var(--artdeco-spacing-2);
    border-radius: 50%;
    background: currentColor;
    animation: pulse 2s infinite;
}

.error-actions {
    display: flex;
    gap: var(--artdeco-spacing-4);
    margin-bottom: var(--artdeco-spacing-10);
}

.button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--artdeco-spacing-2);
    min-height: calc(var(--artdeco-spacing-8) - var(--artdeco-spacing-px));
    padding: 0 calc(var(--artdeco-spacing-12) - var(--artdeco-spacing-px));
    border: 1px solid transparent;
    border-radius: var(--artdeco-radius-none);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-size: var(--artdeco-text-sm);
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: calc(var(--artdeco-spacing-px) * 2);
    text-transform: uppercase;
    cursor: pointer;
    transition:
        background var(--artdeco-transition-quick) var(--artdeco-ease-out),
        border-color var(--artdeco-transition-quick) var(--artdeco-ease-out),
        color var(--artdeco-transition-quick) var(--artdeco-ease-out),
        box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out),
        transform var(--artdeco-transition-quick) var(--artdeco-ease-out);
}

.button:hover:not(:disabled) {
    transform: translateY(calc(var(--artdeco-spacing-px) * -2));
}

.button.primary {
    background: var(--artdeco-gold-primary);
    color: var(--artdeco-bg-global);
}

.button.primary:hover:not(:disabled) {
    background: var(--artdeco-gold-light);
    box-shadow: var(--artdeco-glow-subtle);
}

.button.primary:disabled {
    opacity: 60%;
    cursor: not-allowed;
}

.button.secondary {
    background: transparent;
    color: var(--artdeco-gold-primary);
    border-color: var(--artdeco-gold-primary);
}

.button.secondary:hover {
    background: var(--artdeco-gold-primary);
    color: var(--artdeco-bg-global);
}

.loading-spinner {
    width: var(--artdeco-spacing-4);
    height: var(--artdeco-spacing-4);
    border: calc(var(--artdeco-spacing-px) * 2) solid transparent;
    border-top-color: currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

.troubleshooting {
    padding-top: var(--artdeco-spacing-5);
    border-top: 1px solid var(--artdeco-gold-dim);
}

.troubleshooting summary {
    cursor: pointer;
    margin-bottom: var(--artdeco-spacing-2);
    color: var(--artdeco-fg-primary);
    font-weight: var(--artdeco-font-semibold);
}

.troubleshooting summary:hover {
    color: var(--artdeco-gold-primary);
}

.troubleshooting ul {
    margin: 0;
    padding-left: var(--artdeco-spacing-5);
}

.troubleshooting li {
    margin-bottom: var(--artdeco-spacing-2);
    color: var(--artdeco-fg-muted);
    line-height: var(--artdeco-leading-normal);
}

.error-illustration {
    position: relative;
    display: flex;
    width: 12.5rem;
    height: 12.5rem;
    align-items: center;
    justify-content: center;
    background: color-mix(in srgb, var(--artdeco-gold-primary) 5%, var(--artdeco-bg-card));
    border: 1px solid var(--artdeco-gold-dim);
}

.error-illustration::before,
.error-illustration::after {
    content: '';
    position: absolute;
    width: var(--artdeco-spacing-3);
    height: var(--artdeco-spacing-3);
    border: calc(var(--artdeco-spacing-px) * 2) solid var(--artdeco-gold-primary);
}

.error-illustration::before {
    top: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
    left: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
    border-right: none;
    border-bottom: none;
}

.error-illustration::after {
    right: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
    bottom: calc(var(--artdeco-spacing-4) - var(--artdeco-spacing-px));
    border-top: none;
    border-left: none;
}

.error-illustration svg {
    width: 7.5rem;
    height: 7.5rem;
}

@keyframes pulse {
    0%,
    100% {
        opacity: 100%;
    }
    50% {
        opacity: 50%;
    }
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}

@media (width <= 48rem) {
    .error-card {
        flex-direction: column;
        gap: var(--artdeco-spacing-10);
        padding: calc(var(--artdeco-spacing-10) - var(--artdeco-spacing-px));
    }

    .error-content {
        text-align: center;
    }

    .error-icon {
        font-size: var(--artdeco-text-3xl);
    }

    .error-title {
        font-size: var(--artdeco-text-2xl);
        letter-spacing: calc(var(--artdeco-spacing-px) * 2);
    }

    .error-description {
        font-size: var(--artdeco-text-sm);
    }

    .error-actions {
        flex-direction: column;
    }

    .button {
        width: 100%;
    }

    .error-illustration {
        width: 9.375rem;
        height: 9.375rem;
    }

    .error-illustration svg {
        width: 5rem;
        height: 5rem;
    }
}
</style>
