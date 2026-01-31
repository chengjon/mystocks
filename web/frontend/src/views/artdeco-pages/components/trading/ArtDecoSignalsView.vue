<style scoped lang="scss">
@import '@/styles/artdeco-quant-extended.scss';

.signals-view {
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

            .signals-count {
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }
    }

    .signals-stats {
        margin-bottom: var(--artdeco-spacing-6);

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--artdeco-spacing-4);
        }
    }

    .signals-filters {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .signals-list-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .execution-history-section {
        // 折叠面板样式已在组件内部处理
    }
}

// 单元格样式
.strength-cell {
    display: flex;
    align-items: center;
    justify-content: center;
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

    .current-price {
        font-family: var(--artdeco-font-mono);
        font-weight: 700;
        font-size: var(--artdeco-text-base);
        color: var(--artdeco-fg-primary);
        display: block;
    }

    .target-price {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        margin-top: 2px;
    }
}

.confidence-cell {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--artdeco-spacing-1);

    .confidence-text {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-xs);
        font-weight: 600;
        color: var(--artdeco-fg-primary);
    }
}

.time-cell {
    .signal-time {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-primary);
        display: block;
    }

    .time-ago {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        margin-top: 2px;
    }
}

.action-buttons {
    display: flex;
    gap: var(--artdeco-spacing-2);
    flex-wrap: wrap;
}

// 信号详情弹窗样式
.signal-detail {
    .detail-header {
        margin-bottom: var(--artdeco-spacing-6);
        padding-bottom: var(--artdeco-spacing-4);
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);

        .detail-meta {
            display: flex;
            gap: var(--artdeco-spacing-3);
            margin-bottom: var(--artdeco-spacing-3);
        }

        .detail-stock {
            display: flex;
            flex-direction: column;

            .stock-symbol {
                font-family: var(--artdeco-font-mono);
                font-weight: 600;
                color: var(--artdeco-gold-primary);
                font-size: var(--artdeco-text-lg);
            }

            .stock-name {
                font-family: var(--artdeco-font-body);
                color: var(--artdeco-fg-muted);
                font-size: var(--artdeco-text-sm);
                margin-top: 2px;
            }

            .stock-price {
                font-family: var(--artdeco-font-mono);
                font-weight: 700;
                color: var(--artdeco-fg-primary);
                font-size: var(--artdeco-text-base);
                margin-top: 4px;
            }
        }
    }

    .detail-content {
        h4 {
            @include artdeco-gold-accent;
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-lg);
            font-weight: 600;
            margin: var(--artdeco-spacing-4) 0 var(--artdeco-spacing-3) 0;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);

            &:first-child {
                margin-top: 0;
            }
        }

        .analysis-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: var(--artdeco-spacing-4);

            .analysis-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: var(--artdeco-spacing-3);
                background: var(--artdeco-bg-card);
                border: 1px solid rgba(212, 175, 55, 0.1);
                border-radius: var(--artdeco-radius-none);

                .analysis-label {
                    font-family: var(--artdeco-font-body);
                    font-weight: 500;
                    color: var(--artdeco-fg-primary);
                }

                .analysis-value {
                    font-family: var(--artdeco-font-body);
                    color: var(--artdeco-gold-primary);
                    font-weight: 500;
                }
            }
        }

        .signal-reasoning, .signal-recommendation {
            p {
                font-family: var(--artdeco-font-body);
                color: var(--artdeco-fg-primary);
                line-height: 1.6;
                margin-bottom: var(--artdeco-spacing-4);
            }
        }

        .recommendation-content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--artdeco-spacing-4);

            .recommendation-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: var(--artdeco-spacing-3);
                background: var(--artdeco-bg-card);
                border: 1px solid rgba(212, 175, 55, 0.1);
                border-radius: var(--artdeco-radius-none);

                .recommendation-label {
                    font-family: var(--artdeco-font-body);
                    font-weight: 500;
                    color: var(--artdeco-fg-primary);
                }

                .recommendation-value {
                    font-family: var(--artdeco-font-mono);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                }
            }
        }
    }
}

// 执行历史样式
.positive {
    color: var(--artdeco-up);
    font-weight: 600;
}

.negative {
    color: var(--artdeco-down);
    font-weight: 600;
}

// 响应式设计（桌面端优先）
@media (max-width: 1200px) {
    .signals-view {
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
}

@media (max-width: 768px) {
    .signals-view {
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
            grid-template-columns: 1fr !important;
        }

        .recommendation-content {
            grid-template-columns: 1fr !important;
        }

        .action-buttons {
            flex-direction: column;
            align-items: stretch;
        }

        .detail-meta {
            flex-wrap: wrap;
        }
    }
}

// 动画效果
.signals-view {
    .signals-stats,
    .signals-list-section,
    .execution-history-section {
        animation: fadeInUp 0.6s ease-out;
    }

    .signals-stats {
        animation-delay: 0.1s;
    }

    .signals-list-section {
        animation-delay: 0.2s;
    }

    .execution-history-section {
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

// 信号行悬停效果
.signals-list-section {
    .artdeco-table__row {
        &:has(.artdeco-badge[variant="rise"]) {
            border-left: 3px solid var(--artdeco-up);
        }

        &:has(.artdeco-badge[variant="fall"]) {
            border-left: 3px solid var(--artdeco-down);
        }
    }
}
</style>