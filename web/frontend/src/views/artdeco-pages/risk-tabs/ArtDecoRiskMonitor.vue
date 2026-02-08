<style scoped lang="scss">
@import '@/styles/artdeco-quant-extended.scss';

.risk-monitor {
    min-height: 900px;

    .monitor-header {
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

            .risk-level {
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }
    }

    .risk-overview {
        margin-bottom: var(--artdeco-spacing-6);

        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--artdeco-spacing-4);
        }
    }

    .risk-charts-section {
        margin-bottom: var(--artdeco-spacing-6);

        .charts-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: var(--artdeco-spacing-6);
        }
    }

    .risk-alerts-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .risk-controls-section {
        .controls-content {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-6);
            padding: var(--artdeco-spacing-4);

            .control-group {
                h4 {
                    @include artdeco-gold-accent;
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-text-lg);
                    font-weight: 600;
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                }

                .control-items {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: var(--artdeco-spacing-4);
                }

                .control-item {
                    display: flex;
                    flex-direction: column;
                    gap: var(--artdeco-spacing-2);

                    .control-label {
                        font-family: var(--artdeco-font-body);
                        font-weight: 500;
                        color: var(--artdeco-fg-primary);
                        font-size: var(--artdeco-text-sm);
                    }
                }
            }

            .control-actions {
                display: flex;
                gap: var(--artdeco-spacing-3);
                justify-content: flex-end;
            }
        }
    }
}

// 风险分布样式
.risk-breakdown {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-4);

    .breakdown-item {
        .source-info {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-2);

            .source-name {
                font-family: var(--artdeco-font-body);
                font-weight: 500;
                color: var(--artdeco-fg-primary);
                font-size: var(--artdeco-text-sm);
            }

            .source-value {
                font-family: var(--artdeco-font-mono);
                font-weight: 600;
                color: var(--artdeco-gold-primary);
                font-size: var(--artdeco-text-sm);
            }
        }
    }
}

// 持仓集中度样式
.concentration-list {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-4);

    .concentration-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: var(--artdeco-spacing-3);
        background: var(--artdeco-bg-card);
        border: 1px solid rgba(212, 175, 55, 0.1);
        border-radius: var(--artdeco-radius-none);

        .position-info {
            display: flex;
            flex-direction: column;

            .position-symbol {
                font-family: var(--artdeco-font-mono);
                font-weight: 600;
                color: var(--artdeco-gold-primary);
                font-size: var(--artdeco-text-sm);
            }

            .position-name {
                font-family: var(--artdeco-font-body);
                color: var(--artdeco-fg-muted);
                font-size: var(--artdeco-text-xs);
                margin-top: 2px;
            }
        }

        .position-weight {
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            min-width: 120px;

            .weight-value {
                font-family: var(--artdeco-font-mono);
                font-weight: 600;
                color: var(--artdeco-fg-primary);
                font-size: var(--artdeco-text-sm);
                margin-bottom: var(--artdeco-spacing-1);
            }
        }
    }
}

// 告警表格样式
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

.alert-value-cell {
    .current-value {
        font-family: var(--artdeco-font-mono);
        font-weight: 600;
        color: var(--artdeco-fg-primary);
        font-size: var(--artdeco-text-sm);
        display: block;
    }

    .threshold-value {
        font-family: var(--artdeco-font-body);
        color: var(--artdeco-fg-muted);
        font-size: var(--artdeco-text-xs);
        margin-top: 2px;
    }
}

// 响应式设计（桌面端优先）
@media (max-width: 1200px) {
    .risk-monitor {
        .overview-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .charts-grid {
            grid-template-columns: 1fr;
        }
    }
}

@media (max-width: 768px) {
    .risk-monitor {
        .monitor-header {
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

        .control-items {
            grid-template-columns: 1fr !important;
        }

        .control-actions {
            flex-direction: column;
            align-items: stretch;
        }
    }
}

// 动画效果
.risk-monitor {
    .risk-overview,
    .risk-charts-section,
    .risk-alerts-section,
    .risk-controls-section {
        animation: fadeInUp 0.6s ease-out;
    }

    .risk-overview {
        animation-delay: 0.1s;
    }

    .risk-charts-section {
        animation-delay: 0.2s;
    }

    .risk-alerts-section {
        animation-delay: 0.3s;
    }

    .risk-controls-section {
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

// 风险指标卡片悬停效果
.overview-grid {
    .artdeco-stat-card {
        transition: all var(--artdeco-transition-base);

        &:hover {
            transform: translateY(-2px);
            box-shadow: var(--artdeco-glow-subtle);
        }
    }
}
</style>