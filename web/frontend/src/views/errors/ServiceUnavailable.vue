<template>
    <div class="service-unavailable-page">
        <div class="error-card">
            <div class="error-content">
                <div class="error-icon">⚠️</div>
                <div class="error-code">503</div>
                <div class="error-title">服务暂时不可用</div>
                <div class="error-description">服务器正在维护或遇到临时问题，请稍后再试</div>

                <div class="maintenance-info">
                    <div class="status-indicator">
                        <span class="dot"></span>
                        系统状态: 维护中
                    </div>

                    <div class="estimated-recovery" v-if="estimatedRecovery">
                        <strong>预计恢复时间:</strong>
                        {{ estimatedRecovery }}
                    </div>

                    <div class="maintenance-message">我们正在努力解决问题，为您带来的不便深表歉意</div>
                </div>

                <div class="error-actions">
                    <button class="button primary" @click="checkStatus" :disabled="checking">
                        <span v-if="checking" class="loading-spinner"></span>
                        {{ checking ? '检查中...' : '检查状态' }}
                    </button>
                    <button class="button secondary" @click="goHome">返回首页</button>
                    <button class="button tertiary" @click="refreshPage">刷新页面</button>
                </div>

                <div class="contact-info">
                    <h4>如有紧急问题，请联系</h4>
                    <div class="contact-methods">
                        <a href="mailto:support@mystocks.com" class="contact-link">📧 support@mystocks.com</a>
                        <a href="tel:+86-400-123-4567" class="contact-link">📞 400-123-4567</a>
                    </div>
                </div>

                <div class="system-status">
                    <details>
                        <summary>查看系统状态详情</summary>
                        <div class="status-details">
                            <div class="status-item">
                                <span class="label">Web服务器:</span>
                                <span class="value" :class="{ error: !serverStatus.web, success: serverStatus.web }">
                                    {{ serverStatus.web ? '正常' : '异常' }}
                                </span>
                            </div>
                            <div class="status-item">
                                <span class="label">API服务:</span>
                                <span class="value" :class="{ error: !serverStatus.api, success: serverStatus.api }">
                                    {{ serverStatus.api ? '正常' : '异常' }}
                                </span>
                            </div>
                            <div class="status-item">
                                <span class="label">数据库:</span>
                                <span
                                    class="value"
                                    :class="{ error: !serverStatus.database, success: serverStatus.database }"
                                >
                                    {{ serverStatus.database ? '正常' : '异常' }}
                                </span>
                            </div>
                            <div class="status-item">
                                <span class="label">缓存服务:</span>
                                <span
                                    class="value"
                                    :class="{ error: !serverStatus.cache, success: serverStatus.cache }"
                                >
                                    {{ serverStatus.cache ? '正常' : '异常' }}
                                </span>
                            </div>
                        </div>
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
                    <path d="M12 6v6l4 2" />
                    <path d="M12 2v2" />
                    <path d="M2 12h2" />
                    <path d="M12 22v-2" />
                    <path d="M22 12h-2" />
                </svg>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { ref, onMounted } from 'vue'
    import { useRouter } from 'vue-router'

    const router = useRouter()

    // 模拟的恢复时间（实际应该从API获取）
    const estimatedRecovery = ref('2026-01-12 18:00 (约2小时后)')

    const checking = ref(false)

    const serverStatus = ref({
        web: false,
        api: false,
        database: false,
        cache: false
    })

    const checkStatus = async () => {
        checking.value = true

        try {
            // 并行检查各个服务的状态
            const checks = await Promise.allSettled([checkWebServer(), checkApiServer(), checkDatabase(), checkCache()])

            serverStatus.value = {
                web: checks[0].status === 'fulfilled' ? checks[0].value : false,
                api: checks[1].status === 'fulfilled' ? checks[1].value : false,
                database: checks[2].status === 'fulfilled' ? checks[2].value : false,
                cache: checks[3].status === 'fulfilled' ? checks[3].value : false
            }

            // 如果所有服务都正常，自动跳转回首页
            const allHealthy = Object.values(serverStatus.value).every(status => status)
            if (allHealthy) {
                setTimeout(() => {
                    router.push('/')
                }, 2000) // 2秒后自动跳转
            }
        } catch (error) {
            console.error('状态检查失败:', error)
        } finally {
            checking.value = false
        }
    }

    const checkWebServer = async () => {
        try {
            const response = await fetch('/', { method: 'HEAD' })
            return response.ok
        } catch {
            return false
        }
    }

    const checkApiServer = async () => {
        try {
            const response = await fetch('/health', { method: 'GET' })
            return response.ok
        } catch {
            return false
        }
    }

    const checkDatabase = async () => {
        try {
            const response = await fetch('/health/database', { method: 'GET' })
            return response.ok
        } catch {
            return false
        }
    }

    const checkCache = async () => {
        try {
            const response = await fetch('/health/cache', { method: 'GET' })
            return response.ok
        } catch {
            return false
        }
    }

    const goHome = () => {
        router.push('/')
    }

    const refreshPage = () => {
        window.location.reload()
    }

    onMounted(() => {
        // 页面加载时自动检查一次状态
        checkStatus()

        // 每30秒自动检查一次
        const interval = setInterval(checkStatus, 30000)

        return () => clearInterval(interval)
    })
</script>

<style scoped lang="scss">
    .service-unavailable-page {
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--bg-primary);
        background-image: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 10px,
            rgba(212, 175, 55, 0.02) 10px,
            rgba(212, 175, 55, 0.02) 11px
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
        max-width: 1000px;
        width: 100%;
        background: var(--bg-secondary);
        border: 1px solid var(--gold-dim);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);

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

        .maintenance-info {
            background: rgba(255, 193, 7, 0.1);
            border: 1px solid rgba(255, 193, 7, 0.2);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;

            .status-indicator {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 8px 16px;
                background: rgba(255, 193, 7, 0.1);
                color: #856404;
                border-radius: 20px;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 15px;

                .dot {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #856404;
                    animation: pulse 2s infinite;
                }
            }

            .estimated-recovery {
                margin-bottom: 15px;
                font-size: 14px;
                color: var(--text-primary);

                strong {
                    color: #856404;
                }
            }

            .maintenance-message {
                font-size: 14px;
                color: var(--text-muted);
                font-style: italic;
            }
        }

        .error-actions {
            display: flex;
            gap: 12px;
            margin-bottom: 40px;
            flex-wrap: wrap;

            .button {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 12px 24px;
                border: none;
                font-family: var(--font-display);
                font-size: 14px;
                text-transform: uppercase;
                letter-spacing: 1px;
                cursor: pointer;
                border-radius: 0;
                transition: all 0.3s ease;
                font-weight: 600;

                &.primary {
                    background: var(--gold-primary);
                    color: var(--bg-primary);

                    &:hover:not(:disabled) {
                        background: var(--gold-muted);
                        box-shadow: 0 0 20px rgba(212, 175, 55, 0.4);
                        transform: translateY(-2px);
                    }

                    &:disabled {
                        opacity: 0.6;
                        cursor: not-allowed;
                    }
                }

                &.secondary {
                    background: var(--gold-secondary);
                    color: var(--gold-primary);
                    border: 2px solid var(--gold-primary);

                    &:hover {
                        background: var(--gold-primary);
                        color: var(--bg-primary);
                    }
                }

                &.tertiary {
                    background: transparent;
                    color: var(--text-muted);
                    border: 1px solid var(--text-muted);

                    &:hover {
                        color: var(--gold-primary);
                        border-color: var(--gold-primary);
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

        .contact-info {
            border-top: 1px solid var(--gold-dim);
            padding-top: 20px;
            margin-bottom: 30px;

            h4 {
                margin: 0 0 15px 0;
                font-size: 16px;
                font-weight: 600;
                color: var(--text-primary);
            }

            .contact-methods {
                display: flex;
                gap: 20px;
                flex-wrap: wrap;

                .contact-link {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    color: var(--gold-primary);
                    text-decoration: none;
                    font-size: 14px;
                    padding: 8px 12px;
                    border: 1px solid var(--gold-primary);
                    border-radius: 4px;
                    transition: all 0.3s ease;

                    &:hover {
                        background: var(--gold-primary);
                        color: var(--bg-primary);
                    }
                }
            }
        }

        .system-status {
            border-top: 1px solid var(--gold-dim);
            padding-top: 20px;

            details {
                summary {
                    cursor: pointer;
                    font-weight: 600;
                    color: var(--text-primary);
                    margin-bottom: 15px;

                    &:hover {
                        color: var(--gold-primary);
                    }
                }

                .status-details {
                    background: rgba(0, 0, 0, 0.02);
                    border-radius: 8px;
                    padding: 15px;

                    .status-item {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-bottom: 10px;
                        padding: 8px 0;

                        &:last-child {
                            margin-bottom: 0;
                        }

                        .label {
                            font-weight: 500;
                            color: var(--text-primary);
                        }

                        .value {
                            font-weight: 600;

                            &.success {
                                color: #67c23a;
                            }

                            &.error {
                                color: #f56c6c;
                            }
                        }
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
        background: rgba(212, 175, 55, 0.05);
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
            opacity: 1;
        }
        50% {
            opacity: 0.5;
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

    @media (max-width: 768px) {
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
                    justify-content: center;

                    .button {
                        flex: 1;
                        min-width: 120px;
                        justify-content: center;
                    }
                }

                .contact-methods {
                    justify-content: center;
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
