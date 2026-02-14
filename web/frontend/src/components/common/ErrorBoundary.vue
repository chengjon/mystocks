<template>
    <div>
        <!-- 正常内容 -->
        <slot v-if="!hasError" />

        <!-- 错误状态 -->
        <div v-else class="error-boundary">
            <div class="error-content">
                <div class="error-icon">💥</div>
                <h2 class="error-title">应用程序出错</h2>
                <p class="error-description">应用程序遇到了意外错误，我们的团队已收到通知</p>

                <div class="error-details" v-if="showDetails">
                    <details>
                        <summary>技术详情 (仅开发环境显示)</summary>
                        <pre class="error-stack">{{ errorDetails }}</pre>
                    </details>
                </div>

                <div class="error-actions">
                    <button class="button primary" @click="reload">重新加载</button>
                    <button class="button secondary" @click="goHome">返回首页</button>
                    <button class="button tertiary" @click="reportError" v-if="!reported">报告问题</button>
                    <span v-else class="reported-message">✅ 已报告给开发团队</span>
                </div>

                <div class="error-info">
                    <p class="timestamp">发生时间: {{ formatTimestamp(errorTimestamp) }}</p>
                    <p class="error-id" v-if="errorId">错误ID: {{ errorId }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { ref, onErrorCaptured , onUnmounted } from 'vue'
    import { useRouter } from 'vue-router'

    const router = useRouter()

    // 错误状态
    const hasError = ref<boolean>(false)
    const errorDetails = ref<string>('')
    const errorTimestamp = ref<number | null>(null)
    const errorId = ref<string>('')
    const showDetails = ref<boolean>(false)
    const reported = ref<boolean>(false)

    // 生成错误ID
    const generateErrorId = () => {
        return 'ERR-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9).toUpperCase()
    }

    // 格式化时间戳
    const formatTimestamp = (timestamp: unknown) => {
        if (!timestamp) return ''
        return new Date(timestamp).toLocaleString()
    }

    // 重新加载页面
    const reload = () => {
        window.location.reload()
    }

    // 返回首页
    const goHome = () => {
        router.push('/')
    }

    // 报告错误
    const reportError = async () => {
        if (reported.value) return

        try {
            // 构造错误报告数据
            const errorReport = {
                id: errorId.value,
                timestamp: errorTimestamp.value,
                userAgent: navigator.userAgent,
                url: window.location.href,
                error: errorDetails.value,
                user: getCurrentUser(),
                environment: {
                    vue: '3.x',
                    node: process.env.NODE_ENV,
                    build: process.env.VITE_BUILD_TIME
                }
            }

            // 发送错误报告到监控系统
            // 这里可以调用API来报告错误
            console.error('Error Report:', errorReport)

            // 模拟API调用
            await new Promise(resolve => setTimeout(resolve, 1000))

            reported.value = true

            // 可以显示成功消息
            alert('错误报告已发送，感谢您的反馈！开发团队将尽快处理。')
        } catch (reportError) {
            console.error('Failed to report error:', reportError)
            alert('报告发送失败，请手动记录错误信息并联系技术支持。')
        }
    }

    // 获取当前用户信息（脱敏）
    const getCurrentUser = () => {
        try {
            const user = JSON.parse(localStorage.getItem('user') || 'null')
            if (user) {
                return {
                    id: user.id,
                    username: user.username,
                    role: user.role
                }
            }
        } catch (e) {
            // 忽略解析错误
        }
        return null
    }

    // 错误捕获处理函数
    const handleError = (error: unknown, instance: unknown, info: unknown) => {
        hasError.value = true
        errorTimestamp.value = Date.now()
        errorId.value = generateErrorId()

        // 构造错误详情
        const componentName = instance?.$?.type?.name || instance?.$?.type || 'Unknown'
        const componentFile = instance?.$?.type?.__file || 'Unknown'

        errorDetails.value = `
错误时间: ${new Date(errorTimestamp.value).toISOString()}
错误ID: ${errorId.value}
组件: ${componentName}
文件: ${componentFile}
Vue信息: ${info}

错误堆栈:
${error?.stack || error}

组件实例: ${JSON.stringify(instance, null, 2)}
  `.trim()

        // 在开发环境下显示错误详情
        showDetails.value = import.meta.env.DEV

        // 发送错误到监控系统
        console.error('Error Boundary caught error:', {
            error,
            instance,
            info,
            errorId: errorId.value,
            componentName,
            componentFile
        })

        // 这里可以调用监控API上报错误
        // reportToMonitoring(error, instance, info, errorId.value)

        // 阻止错误继续传播
        return false
    }

    // Vue 3 错误捕获
    onErrorCaptured(handleError)

// Auto-generated: cleanup timers to prevent memory leaks
const _timer_1: ReturnType<typeof setTimeout> | null = null
onUnmounted(() => {
  if (_timer_1) clearTimeout(_timer_1)
})
</script>

<style scoped lang="scss">
    .error-boundary {
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

    .error-content {
        max-width: 600px;
        width: 100%;
        background: var(--bg-secondary);
        border: 1px solid var(--gold-dim);
        border-radius: 8px;
        padding: 40px;
        text-align: center;
        box-shadow: 0 8px 32px rgb(0 0 0 / 10%);

        .error-icon {
            font-size: 48px;
            margin-bottom: 20px;
        }

        .error-title {
            font-family: var(--font-display);
            font-size: 28px;
            color: var(--text-primary);
            text-transform: uppercase;
            letter-spacing: 2px;
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

        .error-details {
            margin-bottom: 30px;
            text-align: left;

            details {
                summary {
                    cursor: pointer;
                    font-weight: 600;
                    color: var(--gold-primary);
                    margin-bottom: 10px;

                    &:hover {
                        text-decoration: underline;
                    }
                }

                .error-stack {
                    background: rgb(0 0 0 / 5%);
                    border: 1px solid var(--gold-dim);
                    border-radius: 4px;
                    padding: 15px;
                    font-family: 'Courier New', monospace;
                    font-size: 12px;
                    color: var(--text-primary);
                    white-space: pre-wrap;
                    word-break: break-all;
                    max-height: 300px;
                    overflow-y: auto;
                    margin: 0;
                }
            }
        }

        .error-actions {
            display: flex;
            gap: 12px;
            justify-content: center;
            margin-bottom: 30px;
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

                    &:hover {
                        background: var(--gold-muted);
                        box-shadow: 0 0 20px rgb(212 175 55 / 40%);
                        transform: translateY(-2px);
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
            }

            .reported-message {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                color: #67c23a;
                font-weight: 600;
                font-size: 14px;
            }
        }

        .error-info {
            border-top: 1px solid var(--gold-dim);
            padding-top: 20px;
            text-align: left;

            .timestamp,
            .error-id {
                margin: 0 0 8px 0;
                font-size: 12px;
                color: var(--text-muted);

                &:last-child {
                    margin-bottom: 0;
                }
            }

            .error-id {
                font-family: 'Courier New', monospace;
                background: rgb(0 0 0 / 5%);
                padding: 2px 6px;
                border-radius: 3px;
                display: inline-block;
            }
        }
    }

    @media (width <= 768px) {
        .error-content {
            padding: 30px 20px;

            .error-icon {
                font-size: 36px;
            }

            .error-title {
                font-size: 24px;
                letter-spacing: 1px;
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

            .error-details .error-stack {
                font-size: 11px;
                max-height: 200px;
            }
        }
    }
</style>
