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
@import "./styles/ServiceUnavailable";
</style>
