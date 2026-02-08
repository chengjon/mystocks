<style scoped lang="scss">
@import '@/styles/artdeco-quant-extended.scss';

.position-monitor {
    min-height: 1000px;

    .monitor-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: var(--artdeco-spacing-6);

        h3 {
            @include artdeco-gold-accent;
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-xl);
            font-weight: 700;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wider);
        }

        .header-actions {
            display: flex;
            align-items: center;
            gap: var(--artdeco-spacing-4);

            .portfolio-value {
                font-size: var(--artdeco-text-sm);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }
    }

    .portfolio-overview {
        margin-bottom: var(--artdeco-spacing-6);

        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--artdeco-spacing-4);
        }
    }

    .position-filters {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .positions-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .risk-monitoring-section {
        // 折叠面板样式已在组件内部处理
    }
}

// 单元格样式
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

.shares-cell {
    text-align: right;

    .shares-count {
        font-family: var(--artdeco-font-mono);
        font-weight: 600;
        color: var(--artdeco-fg-primary);
        font-size: var(--artdeco-text-base);
    }

    .shares-unit {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        margin-left: 2px;
    }
}

.cost-cell {
    text-align: right;

    .avg-cost {
        font-family: var(--artdeco-font-mono);
        font-weight: 600;
        color: var(--artdeco-fg-primary);
        font-size: var(--artdeco-text-sm);
        display: block;
    }

    .current-price {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        margin-top: 2px;
    }
}

.value-cell {
    text-align: right;

    .market-value {
        font-family: var(--artdeco-font-mono);
        font-weight: 700;
        color: var(--artdeco-fg-primary);
        font-size: var(--artdeco-text-sm);
        display: block;
    }

    .portfolio-percent {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-gold-primary);
        margin-top: 2px;
    }
}

.pnl-cell {
    text-align: right;

    &.positive {
        .pnl-value, .pnl-percent {
            color: var(--artdeco-up);
        }
    }

    &.negative {
        .pnl-value, .pnl-percent {
            color: var(--artdeco-down);
        }
    }

    .pnl-value {
        font-family: var(--artdeco-font-mono);
        font-weight: 700;
        font-size: var(--artdeco-text-sm);
        display: block;
    }

    .pnl-percent {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        margin-top: 2px;
    }
}

.change-cell {
    text-align: right;

    &.positive .change-value {
        color: var(--artdeco-up);
    }

    &.negative .change-value {
        color: var(--artdeco-down);
    }

    .change-value {
        font-family: var(--artdeco-font-mono);
        font-weight: 600;
        color: var(--artdeco-fg-primary);
        font-size: var(--artdeco-text-sm);
    }
}

.action-buttons {
    display: flex;
    gap: var(--artdeco-spacing-2);
    flex-wrap: wrap;
}

// 风险监控样式
.risk-content {
    .risk-indicators {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: var(--artdeco-spacing-6);
        margin-bottom: var(--artdeco-spacing-6);
    }

    .concentration-risk {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-4);

        .risk-item {
            .risk-level {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: var(--artdeco-spacing-2);

                .level-label {
                    font-family: var(--artdeco-font-body);
                    font-weight: 500;
                    color: var(--artdeco-fg-primary);
                    font-size: var(--artdeco-text-sm);
                }

                .level-value {
                    font-family: var(--artdeco-font-mono);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    font-size: var(--artdeco-text-sm);
                }
            }
        }
    }

    .sector-distribution {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-4);

        .sector-item {
            .sector-info {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: var(--artdeco-spacing-2);

                .sector-name {
                    font-family: var(--artdeco-font-body);
                    font-weight: 500;
                    color: var(--artdeco-fg-primary);
                    font-size: var(--artdeco-text-sm);
                }

                .sector-percent {
                    font-family: var(--artdeco-font-mono);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    font-size: var(--artdeco-text-sm);
                }
            }
        }
    }

    .risk-alerts {
        .alerts-list {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-4);

            .alert-item {
                display: flex;
                align-items: center;
                gap: var(--artdeco-spacing-3);
                padding: var(--artdeco-spacing-3);
                background: var(--artdeco-bg-card);
                border: 1px solid rgba(212, 175, 55, 0.1);
                border-radius: var(--artdeco-radius-none);

                .alert-content {
                    flex: 1;

                    .alert-title {
                        font-family: var(--artdeco-font-body);
                        font-weight: 600;
                        color: var(--artdeco-fg-primary);
                        font-size: var(--artdeco-text-sm);
                        display: block;
                        margin-bottom: var(--artdeco-spacing-1);
                    }

                    .alert-description {
                        font-family: var(--artdeco-font-body);
                        color: var(--artdeco-fg-muted);
                        font-size: var(--artdeco-text-xs);
                    }
                }
            }
        }
    }
}

// 持仓详情弹窗样式
.position-detail {
    .detail-header {
        margin-bottom: var(--artdeco-spacing-6);
        padding-bottom: var(--artdeco-spacing-4);
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);

        .detail-meta {
            display: flex;
            gap: var(--artdeco-spacing-3);
            margin-bottom: var(--artdeco-spacing-3);
        }

        .detail-time {
            font-family: var(--artdeco-font-body);
            color: var(--artdeco-fg-muted);
            font-size: var(--artdeco-text-sm);
        }
    }

    .detail-content {
        .position-metrics {
            margin-bottom: var(--artdeco-spacing-6);

            .metrics-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: var(--artdeco-spacing-4);

                .metric-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: var(--artdeco-spacing-3);
                    background: var(--artdeco-bg-card);
                    border: 1px solid rgba(212, 175, 55, 0.1);
                    border-radius: var(--artdeco-radius-none);

                    .metric-label {
                        font-family: var(--artdeco-font-body);
                        font-weight: 500;
                        color: var(--artdeco-fg-primary);
                    }

                    .metric-value {
                        font-family: var(--artdeco-font-mono);
                        font-weight: 600;
                        color: var(--artdeco-gold-primary);

                        &.positive {
                            color: var(--artdeco-up);
                        }

                        &.negative {
                            color: var(--artdeco-down);
                        }
                    }
                }
            }
        }

        h4 {
            @include artdeco-gold-accent;
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-lg);
            font-weight: 600;
            margin: var(--artdeco-spacing-4) 0 var(--artdeco-spacing-3) 0;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);
        }

        .position-chart {
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
        }
    }
}

// 响应式设计（桌面端优先）
@media (max-width: 1200px) {
    .position-monitor {
        .overview-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .risk-indicators {
            grid-template-columns: 1fr !important;
        }
    }
}

@media (max-width: 768px) {
    .position-monitor {
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

        .metrics-grid {
            grid-template-columns: 1fr !important;
        }

        .action-buttons {
            flex-direction: column;
            align-items: stretch;
        }

        .alert-item {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--artdeco-spacing-2);
        }

        .detail-meta {
            flex-wrap: wrap;
        }
    }
}

// 动画效果
.position-monitor {
    .portfolio-overview,
    .positions-section,
    .risk-monitoring-section {
        animation: fadeInUp 0.6s ease-out;
    }

    .portfolio-overview {
        animation-delay: 0.1s;
    }

    .positions-section {
        animation-delay: 0.2s;
    }

    .risk-monitoring-section {
        animation-delay: 0.3s;
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

// 持仓行颜色区分
.positions-section {
    .artdeco-table__row {
        &:has(.pnl-cell.positive) {
            border-left: 3px solid var(--artdeco-up);
        }

        &:has(.pnl-cell.negative) {
            border-left: 3px solid var(--artdeco-down);
        }
    }
}

// 正负值颜色类
.positive {
    color: var(--artdeco-up) !important;
}

.negative {
    color: var(--artdeco-down) !important;
}
</style>