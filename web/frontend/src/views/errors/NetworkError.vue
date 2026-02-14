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
    .network-error-page {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg-primary);
        background-image: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 10px,
            rgb(212 175 55 / 2%) 10px,
            rgb(212 175 55 / 2%) 11px
        );
        padding: 20px;
    }

    .error-card {
        position: relative;
        z-index: 1;
        display: flex;
        gap: 60px;
        align-items: center;
        padding: 60px;
        max-width: 900px;
        width: 100%;
        background: var(--bg-secondary);
        border: 1px solid var(--gold-dim);
        box-shadow: 0 8px 32px rgb(0 0 0 / 10%);

        &::before,
        &::after {
            content: '';
            position: absolute;
            width: 20px;
            height: 20px;
            border: 3px solid var(--gold-primary);
        }

        &::before {
            top: 16px;
            left: 16px;
            border-right: none;
            border-bottom: none;
        }

        &::after {
            bottom: 16px;
            right: 16px;
            border-left: none;
            border-top: none;
        }
    }

    .error-content {
        flex: 1;

        .error-icon {
            font-size: 48px;
            margin-bottom: 20px;
            text-align: center;
        }

        .error-code {
            font-family: var(--font-display);
            font-size: 24px;
            font-weight: 700;
            color: var(--gold-primary);
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 16px;
        }

        .error-title {
            font-family: var(--font-display);
            font-size: 32px;
            color: var(--text-primary);
            text-transform: uppercase;
            letter-spacing: 3px;
            margin-bottom: 16px;
            font-weight: 600;
        }

        .error-description {
            font-family: var(--font-body);
            font-size: 16px;
            color: var(--text-muted);
            line-height: 1.6;
            margin-bottom: 30px;
        }

        .network-status {
            margin-bottom: 30px;

            .status-indicator {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 500;

                &.offline {
                    background: rgb(245 108 108 / 10%);
                    color: #f56c6c;
                    border: 1px solid rgb(245 108 108 / 20%);
                }

                .dot {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: currentColor;
                    animation: pulse 2s infinite;
                }
            }
        }

        .error-actions {
            display: flex;
            gap: 16px;
            margin-bottom: 40px;

            .button {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 14px 32px;
                border: none;
                font-family: var(--font-display);
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 2px;
                cursor: pointer;
                border-radius: 0;
                transition: all 0.3s ease;
                font-weight: 600;

                &.primary {
                    background: var(--gold-primary);
                    color: var(--bg-primary);

                    &:hover:not(:disabled) {
                        background: var(--gold-muted);
                        box-shadow: 0 0 20px rgb(212 175 55 / 40%);
                        transform: translateY(-2px);
                    }

                    &:disabled {
                        opacity: 60%;
                        cursor: not-allowed;
                    }
                }

                &.secondary {
                    background: transparent;
                    color: var(--gold-primary);
                    border: 2px solid var(--gold-primary);

                    &:hover {
                        background: var(--gold-primary);
                        color: var(--bg-primary);
                    }
                }

                .loading-spinner {
                    width: 16px;
                    height: 16px;
                    border: 2px solid transparent;
                    border-top: 2px solid currentColor;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                }
            }
        }

        .troubleshooting {
            border-top: 1px solid var(--gold-dim);
            padding-top: 20px;

            details {
                summary {
                    cursor: pointer;
                    font-weight: 600;
                    color: var(--text-primary);
                    margin-bottom: 10px;

                    &:hover {
                        color: var(--gold-primary);
                    }
                }

                ul {
                    margin: 0;
                    padding-left: 20px;

                    li {
                        margin-bottom: 8px;
                        color: var(--text-muted);
                        line-height: 1.5;
                    }
                }
            }
        }
    }

    .error-illustration {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 200px;
        height: 200px;
        background: rgb(212 175 55 / 5%);
        border: 1px solid var(--gold-dim);
        position: relative;

        &::before,
        &::after {
            content: '';
            position: absolute;
            width: 12px;
            height: 12px;
            border: 2px solid var(--gold-primary);
        }

        &::before {
            top: 10px;
            left: 10px;
            border-right: none;
            border-bottom: none;
        }

        &::after {
            bottom: 10px;
            right: 10px;
            border-left: none;
            border-top: none;
        }

        svg {
            width: 120px;
            height: 120px;
        }
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

    @media (width <= 768px) {
        .error-card {
            flex-direction: column;
            gap: 40px;
            padding: 30px;

            .error-content {
                text-align: center;

                .error-icon {
                    font-size: 36px;
                }

                .error-title {
                    font-size: 24px;
                    letter-spacing: 2px;
                }

                .error-description {
                    font-size: 14px;
                }

                .error-actions {
                    flex-direction: column;

                    .button {
                        width: 100%;
                        justify-content: center;
                    }
                }
            }
        }

        .error-illustration {
            width: 150px;
            height: 150px;

            svg {
                width: 80px;
                height: 80px;
            }
        }
    }
</style>
