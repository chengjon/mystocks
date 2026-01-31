<style scoped lang="scss">
@import '@/styles/artdeco-quant-extended.scss';

.history-view {
    min-height: 900px;

    .view-header {
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

            .trades-count {
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }
    }

    .trade-stats {
        margin-bottom: var(--artdeco-spacing-6);

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--artdeco-spacing-4);
        }
    }

    .trade-filters {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .trade-history-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .pnl-analysis-section {
        // 折叠面板样式已在组件内部处理
    }
}

// 单元格样式
.datetime-cell {
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
        margin-top: 2px;
    }
}

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

.price-cell {
    text-align: right;

    .trade-price {
        font-family: var(--artdeco-font-mono);
        font-weight: 700;
        font-size: var(--artdeco-text-base);
        color: var(--artdeco-fg-primary);
        display: block;
    }

    .quantity {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        margin-top: 2px;
    }
}

.amount-cell {
    text-align: right;

    .total-amount {
        font-family: var(--artdeco-font-mono);
        font-weight: 700;
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-primary);
        display: block;
    }

    .fee {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
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
        font-size: var(--artdeco-text-base);
        display: block;
    }

    .pnl-percent {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        margin-top: 2px;
    }
}

// 盈亏分析样式
.analysis-content {
    .analysis-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

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

// 交易详情弹窗样式
.trade-detail {
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
        .trade-info {
            margin-bottom: var(--artdeco-spacing-6);

            .info-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: var(--artdeco-spacing-4);

                .info-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    padding: var(--artdeco-spacing-3);
                    background: var(--artdeco-bg-card);
                    border: 1px solid rgba(212, 175, 55, 0.1);
                    border-radius: var(--artdeco-radius-none);

                    .info-label {
                        font-family: var(--artdeco-font-body);
                        font-weight: 500;
                        color: var(--artdeco-fg-primary);
                    }

                    .info-value {
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

        .trade-notes, .trade-strategy {
            p {
                font-family: var(--artdeco-font-body);
                color: var(--artdeco-fg-primary);
                line-height: 1.6;
                margin-bottom: var(--artdeco-spacing-4);
            }
        }

        .strategy-info {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--artdeco-spacing-4);

            .strategy-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: var(--artdeco-spacing-3);
                background: var(--artdeco-bg-card);
                border: 1px solid rgba(212, 175, 55, 0.1);
                border-radius: var(--artdeco-radius-none);

                .strategy-label {
                    font-family: var(--artdeco-font-body);
                    font-weight: 500;
                    color: var(--artdeco-fg-primary);
                }

                .strategy-value {
                    font-family: var(--artdeco-font-body);
                    color: var(--artdeco-gold-primary);
                    font-weight: 500;
                }
            }
        }
    }
}

// 响应式设计（桌面端优先）
@media (max-width: 1200px) {
    .history-view {
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .analysis-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
}

@media (max-width: 768px) {
    .history-view {
        .view-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--artdeco-spacing-4);

            .header-actions {
                width: 100%;
                justify-content: space-between;
            }
        }

        .stats-grid {
            grid-template-columns: 1fr;
        }

        .analysis-grid {
            grid-template-columns: 1fr;
        }

        .info-grid {
            grid-template-columns: 1fr !important;
        }

        .strategy-info {
            grid-template-columns: 1fr !important;
        }

        .detail-meta {
            flex-wrap: wrap;
        }
    }
}

// 动画效果
.history-view {
    .trade-stats,
    .trade-history-section,
    .pnl-analysis-section {
        animation: fadeInUp 0.6s ease-out;
    }

    .trade-stats {
        animation-delay: 0.1s;
    }

    .trade-history-section {
        animation-delay: 0.2s;
    }

    .pnl-analysis-section {
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

// 交易行颜色区分
.trade-history-section {
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