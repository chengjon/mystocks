<style scoped lang="scss">
@import '@/styles/artdeco-quant-extended.scss';

.risk-alerts {
    min-height: 800px;

    .alerts-header {
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

            .alert-count {
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }
    }

    .alerts-stats {
        margin-bottom: var(--artdeco-spacing-6);

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--artdeco-spacing-4);
        }
    }

    .alerts-filters {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .active-alerts-section {
        margin-bottom: var(--artdeco-spacing-8);

        .section-title {
            @include artdeco-gold-accent;
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-xl);
            font-weight: 600;
            margin: 0 0 var(--artdeco-spacing-4) 0;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }

        .no-alerts {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: var(--artdeco-spacing-12);
            background: rgba(0, 230, 118, 0.05);
            border: 1px solid rgba(0, 230, 118, 0.2);
            border-radius: var(--artdeco-radius-none);
            color: var(--artdeco-up);

            p {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-base);
                margin: var(--artdeco-spacing-2) 0 0 0;
            }
        }

        .alerts-list {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-4);
        }
    }

    .alerts-history-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .risk-settings-section {
        .settings-content {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-4);
            padding: var(--artdeco-spacing-4);

            .setting-item {
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: var(--artdeco-spacing-3);
                background: var(--artdeco-bg-card);
                border: 1px solid rgba(212, 175, 55, 0.1);
                border-radius: var(--artdeco-radius-none);

                .setting-label {
                    font-family: var(--artdeco-font-body);
                    font-weight: 500;
                    color: var(--artdeco-fg-primary);
                }
            }
        }
    }
}

// 告警元数据样式
.alert-metadata {
    display: flex;
    gap: var(--artdeco-spacing-2);
    margin-top: var(--artdeco-spacing-2);
}

// 告警类型单元格样式
.alert-type-cell {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-2);

    span {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-primary);
    }
}

// 股票代码单元格样式
.symbol-cell {
    .symbol-code {
        font-family: var(--artdeco-font-mono);
        font-weight: 600;
        color: var(--artdeco-gold-primary);
        font-size: var(--artdeco-text-sm);
        display: block;
    }

    .symbol-name {
        font-family: var(--artdeco-font-body);
        color: var(--artdeco-fg-muted);
        font-size: var(--artdeco-text-xs);
        margin-top: 2px;
    }
}

// 时间戳单元格样式
.timestamp-cell {
    .date {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-primary);
        display: block;
    }

    .time {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
    }
}

// 响应式设计（桌面端优先）
@media (max-width: 1200px) {
    .risk-alerts {
        .alerts-stats .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
}

@media (max-width: 768px) {
    .risk-alerts {
        .alerts-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--artdeco-spacing-4);

            .header-actions {
                width: 100%;
                justify-content: space-between;
            }
        }

        .alerts-stats .stats-grid {
            grid-template-columns: 1fr;
        }

        .active-alerts-section .alerts-list {
            gap: var(--artdeco-spacing-3);
        }

        .risk-settings-section .settings-content .setting-item {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--artdeco-spacing-2);
        }
    }
}

// 动画效果
.risk-alerts {
    .alerts-stats,
    .active-alerts-section,
    .alerts-history-section,
    .risk-settings-section {
        animation: fadeInUp 0.6s ease-out;
    }

    .alerts-stats {
        animation-delay: 0.1s;
    }

    .active-alerts-section {
        animation-delay: 0.2s;
    }

    .alerts-history-section {
        animation-delay: 0.3s;
    }

    .risk-settings-section {
        animation-delay: 0.4s;
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

// 告警动画
.alerts-list {
    .artdeco-alert {
        animation: slideInLeft 0.5s ease-out;
    }

    .artdeco-alert:nth-child(1) { animation-delay: 0.1s; }
    .artdeco-alert:nth-child(2) { animation-delay: 0.2s; }
    .artdeco-alert:nth-child(3) { animation-delay: 0.3s; }
}

@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}
</style>