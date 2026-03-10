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
    .forbidden-page {
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

        .permission-info {
            background: rgb(212 175 55 / 5%);
            border: 1px solid var(--gold-dim);
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;

            .role-display {
                margin: 0 0 10px 0;
                font-weight: 600;
                color: var(--text-primary);

                .role-badge {
                    display: inline-block;
                    padding: 4px 12px;
                    background: var(--gold-primary);
                    color: var(--bg-primary);
                    border-radius: 12px;
                    font-size: 12px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
            }

            .permission-hint {
                margin: 0;
                color: var(--text-muted);
                font-size: 14px;
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
        }

        .helpful-links {
            border-top: 1px solid var(--gold-dim);
            padding-top: 20px;

            h4 {
                margin: 0 0 15px 0;
                font-size: 16px;
                font-weight: 600;
                color: var(--text-primary);
            }

            ul {
                margin: 0;
                padding: 0;
                list-style: none;

                li {
                    margin-bottom: 8px;

                    a {
                        color: var(--gold-primary);
                        text-decoration: none;
                        font-size: 14px;

                        &:hover {
                            text-decoration: underline;
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
                    justify-content: center;

                    .button {
                        flex: 1;
                        min-width: 120px;
                        justify-content: center;
                    }
                }

                .helpful-links ul li {
                    text-align: center;
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
