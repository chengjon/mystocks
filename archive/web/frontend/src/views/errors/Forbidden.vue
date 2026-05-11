<template>
    <div class="forbidden-page">
        <div class="error-card">
            <div class="error-content">
                <div class="error-icon">🔒</div>
                <div class="error-code">403</div>
                <div class="error-title">访问被拒绝</div>
                <div class="error-description">您没有权限访问此页面，请联系管理员或返回首页</div>

                <div class="permission-info" v-if="userRole">
                    <p class="role-display">
                        当前角色:
                        <span class="role-badge">{{ userRole }}</span>
                    </p>
                    <p class="permission-hint">此页面需要更高的权限等级</p>
                </div>

                <div class="error-actions">
                    <button class="button primary" @click="goHome">返回首页</button>
                    <button class="button secondary" @click="requestAccess" v-if="canRequestAccess">申请权限</button>
                    <button class="button tertiary" @click="contactAdmin">联系管理员</button>
                </div>

                <div class="helpful-links">
                    <h4>可能有用的链接</h4>
                    <ul>
                        <li><router-link to="/dashboard">交易室</router-link></li>
                        <li><router-link to="/analysis">数据分析</router-link></li>
                        <li><router-link to="/settings">系统设置</router-link></li>
                    </ul>
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
                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                    <circle cx="12" cy="16" r="1" />
                    <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { computed } from 'vue'
    import { useRouter } from 'vue-router'
    import { useAuthStore } from '@/stores/auth'

    const router = useRouter()
    const authStore = useAuthStore()

    const userRole = computed(() => {
        const user = authStore.user
        return user?.roles?.[0] || user?.role || '普通用户'
    })

    const canRequestAccess = computed(() => {
        // 这里可以根据用户角色和页面要求来决定是否显示申请权限按钮
        return true // 暂时允许所有用户申请
    })

    const goHome = () => {
        router.push('/')
    }

    const requestAccess = () => {
        // 这里可以实现权限申请逻辑
        alert('权限申请功能即将上线，请联系管理员手动申请')
        // 或者跳转到权限申请页面
        // router.push('/permissions/request')
    }

    const contactAdmin = () => {
        // 这里可以实现联系管理员的逻辑
        const adminEmail = 'admin@mystocks.com'
        const subject = encodeURIComponent('权限访问申请')
        const body = encodeURIComponent(
            `
您好，

我需要申请访问以下页面的权限：
页面: ${window.location.pathname}
我的角色: ${userRole.value}
申请时间: ${new Date().toLocaleString()}

请审核并授予相应权限。

谢谢！
  `.trim()
        )

        window.location.href = `mailto:${adminEmail}?subject=${subject}&body=${body}`
    }
</script>

<style scoped lang="scss">
@use '../../styles/artdeco-tokens.scss' as *;

.forbidden-page {
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

.permission-info {
    margin-bottom: calc(var(--artdeco-spacing-10) + var(--artdeco-spacing-px) * 2);
    padding: var(--artdeco-spacing-5);
    background: color-mix(in srgb, var(--artdeco-gold-primary) 5%, var(--artdeco-bg-card));
    border: 1px solid var(--artdeco-gold-dim);
}

.role-display {
    margin: 0 0 var(--artdeco-spacing-2) 0;
    color: var(--artdeco-fg-primary);
    font-weight: var(--artdeco-font-semibold);
}

.role-badge {
    display: inline-block;
    padding: var(--artdeco-spacing-1) var(--artdeco-spacing-3);
    background: var(--artdeco-gold-primary);
    color: var(--artdeco-bg-global);
    font-size: var(--artdeco-text-xs);
    font-weight: var(--artdeco-font-bold);
    letter-spacing: var(--artdeco-spacing-px);
    text-transform: uppercase;
}

.permission-hint {
    margin: 0;
    color: var(--artdeco-fg-muted);
    font-size: var(--artdeco-text-sm);
}

.error-actions {
    display: flex;
    flex-wrap: wrap;
    gap: var(--artdeco-spacing-3);
    margin-bottom: var(--artdeco-spacing-10);
}

.button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-height: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-2));
    padding: 0 var(--artdeco-spacing-5);
    border: 1px solid transparent;
    border-radius: var(--artdeco-radius-none);
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-size: var(--artdeco-text-sm);
    font-weight: var(--artdeco-font-semibold);
    letter-spacing: var(--artdeco-spacing-px);
    text-transform: uppercase;
    cursor: pointer;
    transition:
        background var(--artdeco-transition-quick) var(--artdeco-ease-out),
        border-color var(--artdeco-transition-quick) var(--artdeco-ease-out),
        color var(--artdeco-transition-quick) var(--artdeco-ease-out),
        box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out),
        transform var(--artdeco-transition-quick) var(--artdeco-ease-out);
}

.button:hover {
    transform: translateY(calc(var(--artdeco-spacing-px) * -2));
}

.button.primary {
    background: var(--artdeco-gold-primary);
    color: var(--artdeco-bg-global);
}

.button.primary:hover {
    background: var(--artdeco-gold-light);
    box-shadow: var(--artdeco-glow-subtle);
}

.button.secondary {
    background: color-mix(in srgb, var(--artdeco-gold-primary) 8%, var(--artdeco-bg-card));
    color: var(--artdeco-gold-primary);
    border-color: var(--artdeco-gold-primary);
}

.button.secondary:hover {
    background: var(--artdeco-gold-primary);
    color: var(--artdeco-bg-global);
}

.button.tertiary {
    background: transparent;
    color: var(--artdeco-fg-muted);
    border-color: var(--artdeco-fg-muted);
}

.button.tertiary:hover {
    color: var(--artdeco-gold-primary);
    border-color: var(--artdeco-gold-primary);
}

.helpful-links {
    padding-top: var(--artdeco-spacing-5);
    border-top: 1px solid var(--artdeco-gold-dim);
}

.helpful-links h4 {
    margin: 0 0 var(--artdeco-spacing-4) 0;
    color: var(--artdeco-fg-primary);
    font-size: var(--artdeco-text-base);
    font-weight: var(--artdeco-font-semibold);
}

.helpful-links ul {
    margin: 0;
    padding: 0;
    list-style: none;
}

.helpful-links li {
    margin-bottom: var(--artdeco-spacing-2);
}

.helpful-links a {
    color: var(--artdeco-gold-primary);
    font-size: var(--artdeco-text-sm);
    text-decoration: none;
}

.helpful-links a:hover {
    text-decoration: underline;
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
        justify-content: center;
    }

    .button {
        flex: 1 1 100%;
        min-width: calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-10));
    }

    .helpful-links li {
        text-align: center;
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
