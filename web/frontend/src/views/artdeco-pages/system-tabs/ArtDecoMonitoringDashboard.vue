<style scoped lang="scss">
@import '@/styles/artdeco-quant-extended.scss';

.monitoring-dashboard {
    min-height: 1000px;

    .dashboard-header {
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

            .system-health {
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }
    }

    .system-overview {
        margin-bottom: var(--artdeco-spacing-6);

        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--artdeco-spacing-4);
        }
    }

    .services-section {
        margin-bottom: var(--artdeco-spacing-6);

        .section-title {
            @include artdeco-gold-accent;
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-xl);
            font-weight: 600;
            margin: 0 0 var(--artdeco-spacing-4) 0;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }

        .services-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: var(--artdeco-spacing-4);
        }
    }

    .data-quality-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .performance-charts-section {
        margin-bottom: var(--artdeco-spacing-6);

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: var(--artdeco-spacing-6);
        }
    }

    .alerts-history-section {
        // 折叠面板样式已在组件内部处理
    }
}

// 服务卡片样式
.service-card {
    background: var(--artdeco-bg-card);
    border: 1px solid rgba(212, 175, 55, 0.1);
    border-radius: var(--artdeco-radius-none);
    padding: var(--artdeco-spacing-4);
    transition: all var(--artdeco-transition-base);

    &:hover {
        border-color: var(--artdeco-gold-primary);
        box-shadow: var(--artdeco-glow-subtle);
        transform: translateY(-2px);
    }

    &--error {
        border-color: var(--artdeco-up);
        background: rgba(255, 82, 82, 0.05);
    }

    .service-header {
        display: flex;
        align-items: center;
        gap: var(--artdeco-spacing-3);
        margin-bottom: var(--artdeco-spacing-4);

        .service-info {
            flex: 1;

            .service-name {
                font-family: var(--artdeco-font-display);
                font-size: var(--artdeco-text-lg);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                margin: 0 0 var(--artdeco-spacing-1) 0;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }
    }

    .service-metrics {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: var(--artdeco-spacing-3);
        margin-bottom: var(--artdeco-spacing-4);

        .metric-item {
            text-align: center;
            padding: var(--artdeco-spacing-2);
            background: rgba(255, 255, 255, 0.02);
            border-radius: var(--artdeco-radius-none);

            .metric-label {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-xs);
                color: var(--artdeco-fg-muted);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
                display: block;
                margin-bottom: var(--artdeco-spacing-1);
            }

            .metric-value {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-sm);
                font-weight: 600;
                color: var(--artdeco-gold-primary);
            }
        }
    }

    .service-actions {
        display: flex;
        gap: var(--artdeco-spacing-2);
        justify-content: flex-end;
    }
}

// 数据质量单元格样式
.quality-score-cell {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: var(--artdeco-spacing-2);

    .score-value {
        font-family: var(--artdeco-font-mono);
        font-weight: 600;
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-primary);
    }
}

.last-check-cell {
    .check-time {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-primary);
        display: block;
    }

    .check-ago {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        margin-top: 2px;
    }
}

.issues-cell {
    text-align: center;
}

// 图表占位符样式
.chart-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: var(--artdeco-spacing-8);
    text-align: center;
    color: var(--artdeco-fg-muted);

    p {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-base);
        margin: var(--artdeco-spacing-2) 0;
    }

    small {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        opacity: 0.7;
    }
}

// 响应式设计（桌面端优先）
@media (max-width: 1200px) {
    .monitoring-dashboard {
        .overview-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .services-grid {
            grid-template-columns: 1fr;
        }

        .charts-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
}

@media (max-width: 768px) {
    .monitoring-dashboard {
        .dashboard-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--artdeco-spacing-4);

            .header-actions {
                width: 100%;
                justify-content: space-between;
            }
        }

        .overview-grid {
            grid-template-columns: 1fr;
        }

        .charts-grid {
            grid-template-columns: 1fr;
        }

        .service-metrics {
            grid-template-columns: 1fr !important;
        }

        .service-actions {
            flex-direction: column;
            align-items: stretch;
        }
    }
}

// 动画效果
.monitoring-dashboard {
    .system-overview,
    .services-section,
    .data-quality-section,
    .performance-charts-section {
        animation: fadeInUp 0.6s ease-out;
    }

    .system-overview {
        animation-delay: 0.1s;
    }

    .services-section {
        animation-delay: 0.2s;
    }

    .data-quality-section {
        animation-delay: 0.3s;
    }

    .performance-charts-section {
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

// 服务状态指示器
.service-card--error {
    animation: pulseError 2s infinite;
}

@keyframes pulseError {
    0%, 100% {
        border-color: var(--artdeco-up);
    }
    50% {
        border-color: rgba(255, 82, 82, 0.3);
    }
}

// 健康状态颜色
.system-health {
    &.success {
        background: rgba(0, 230, 118, 0.1);
        color: var(--artdeco-up);
    }

    &.warning {
        background: rgba(255, 213, 79, 0.1);
        color: var(--artdeco-gold-primary);
    }

    &.error {
        background: rgba(255, 82, 82, 0.1);
        color: var(--artdeco-down);
    }
}
</style>