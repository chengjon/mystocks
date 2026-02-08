<style scoped lang="scss">
@import '@/styles/artdeco-quant-extended.scss';

.system-settings {
    min-height: 1200px;

    .settings-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--artdeco-spacing-6);

        h2 {
            @include artdeco-gold-accent;
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-2xl);
            font-weight: 700;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wider);
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-4);

            .settings-status {
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }
    }

    .basic-settings-section,
    .datasource-settings-section,
    .notification-settings-section,
    .performance-settings-section,
    .security-settings-section {
        margin-bottom: var(--artdeco-spacing-4);
    }

    .save-settings-section {
        margin-top: var(--artdeco-spacing-8);
        padding-top: var(--artdeco-spacing-6);
        border-top: 1px solid rgba(212, 175, 55, 0.2);

        .save-actions {
            display: flex;
            gap: var(--artdeco-spacing-3);
            justify-content: center;
            margin-bottom: var(--artdeco-spacing-4);
        }

        .settings-status {
            display: flex;
            justify-content: center;

            .status-text {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
            }
        }
    }
}

// 设置网格布局
.settings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: var(--artdeco-spacing-6);
}

// 系统信息样式
.system-info {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--artdeco-spacing-4);

    .info-item {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-1);

        .info-label {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }

        .info-value {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-base);
            font-weight: 600;
            color: var(--artdeco-gold-primary);
        }
    }
}

// UI设置样式
.ui-settings {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--artdeco-spacing-4);
}

// 通用设置项样式
.setting-item {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-2);

    .setting-label {
        font-family: var(--artdeco-font-body);
        font-weight: 500;
        color: var(--artdeco-fg-primary);
        font-size: var(--artdeco-text-sm);
    }
}

// 设置内容样式
.settings-content {
    .setting-group {
        margin-bottom: var(--artdeco-spacing-6);

        &:last-child {
            margin-bottom: 0;
        }

        h4 {
            @include artdeco-gold-accent;
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-lg);
            font-weight: 600;
            margin: 0 0 var(--artdeco-spacing-4) 0;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }

        .setting-options {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--artdeco-spacing-4);
        }
    }
}

// 时间范围样式
.time-range {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-2);

    .time-separator {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-muted);
    }
}

// 响应式设计（桌面端优先）
@media (max-width: 1200px) {
    .system-settings {
        .settings-grid {
            grid-template-columns: 1fr;
        }

        .system-info {
            grid-template-columns: repeat(2, 1fr);
        }

        .ui-settings {
            grid-template-columns: 1fr;
        }
    }
}

@media (max-width: 768px) {
    .system-settings {
        .settings-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--artdeco-spacing-4);

            .header-actions {
                width: 100%;
                justify-content: space-between;
            }
        }

        .save-actions {
            flex-direction: column;
            align-items: stretch;
        }

        .system-info {
            grid-template-columns: 1fr;
        }

        .setting-options {
            grid-template-columns: 1fr !important;
        }

        .time-range {
            flex-direction: column;
            align-items: stretch;

            .time-separator {
                text-align: center;
            }
        }
    }
}

// 动画效果
.system-settings {
    .basic-settings-section,
    .datasource-settings-section,
    .notification-settings-section,
    .performance-settings-section,
    .security-settings-section,
    .save-settings-section {
        animation: fadeInUp 0.6s ease-out;
    }

    .basic-settings-section {
        animation-delay: 0.1s;
    }

    .datasource-settings-section {
        animation-delay: 0.2s;
    }

    .notification-settings-section {
        animation-delay: 0.3s;
    }

    .performance-settings-section {
        animation-delay: 0.4s;
    }

    .security-settings-section {
        animation-delay: 0.5s;
    }

    .save-settings-section {
        animation-delay: 0.6s;
    }
}

@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

// 设置项悬停效果
.setting-item {
    &:hover .setting-label {
        color: var(--artdeco-gold-primary);
    }
}

// 开关组件样式调整
:deep(.artdeco-switch) {
    margin-top: var(--artdeco-spacing-1);
}

// 输入组件样式调整
:deep(.artdeco-input),
:deep(.artdeco-select) {
    width: 100%;
}
</style>