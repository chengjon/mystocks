<style scoped lang="scss">
@import '@/styles/artdeco-quant-extended.scss';

.realtime-monitor {
    min-height: 600px;
    position: relative;

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

            .connection-status {
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }
    }

    .ticker-section {
        margin-bottom: var(--artdeco-spacing-6);
        padding: var(--artdeco-spacing-4);
        background: rgba(255, 255, 255, 0.02);
        border-radius: var(--artdeco-radius-none);
        border: 1px solid rgba(212, 175, 55, 0.1);
    }

    .indices-section {
        margin-bottom: var(--artdeco-spacing-6);

        .indices-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: var(--artdeco-spacing-4);
        }
    }

    .table-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .summary-section {
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--artdeco-spacing-4);
        }
    }

    .error-section {
        margin-top: var(--artdeco-spacing-6);
    }
}

// 表格单元格样式
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
    }

    .price-unit {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        margin-left: 2px;
    }
}

.change-cell {
    text-align: right;

    &.positive {
        .change-value, .change-percent {
            color: var(--artdeco-up);
        }
    }

    &.negative {
        .change-value, .change-percent {
            color: var(--artdeco-down);
        }
    }

    .change-value {
        font-family: var(--artdeco-font-mono);
        font-weight: 700;
        font-size: var(--artdeco-text-sm);
        display: block;
    }

    .change-percent {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
    }
}

.volume-cell, .turnover-cell {
    text-align: right;

    .volume-value, .turnover-value {
        font-family: var(--artdeco-font-mono);
        font-weight: 600;
        color: var(--artdeco-fg-primary);
        font-size: var(--artdeco-text-sm);
    }

    .volume-unit, .turnover-unit {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        margin-left: 2px;
    }
}

// 响应式设计（桌面端优先）
@media (max-width: 1200px) {
    .realtime-monitor {
        .indices-grid {
            grid-template-columns: 1fr;
        }

        .summary-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
}

@media (max-width: 768px) {
    .realtime-monitor {
        .monitor-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--artdeco-spacing-4);

            .header-actions {
                width: 100%;
                justify-content: space-between;
            }
        }

        .indices-grid,
        .summary-grid {
            grid-template-columns: 1fr;
        }
    }
}

// 动画和过渡效果
.realtime-monitor {
    .ticker-section,
    .indices-section,
    .table-section,
    .summary-section {
        animation: fadeInUp 0.6s ease-out;
    }

    .ticker-section {
        animation-delay: 0.1s;
    }

    .indices-section {
        animation-delay: 0.2s;
    }

    .table-section {
        animation-delay: 0.3s;
    }

    .summary-section {
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

// 连接状态指示器动画
.connection-status {
    &.connected {
        animation: pulse 2s infinite;
    }

    &.disconnected {
        animation: blink 1s infinite;
    }
}

@keyframes blink {
    0%, 50% {
        opacity: 1;
    }
    51%, 100% {
        opacity: 0.5;
    }
}

// 按钮激活状态
.active {
    background: var(--artdeco-gold-primary);
    color: var(--artdeco-bg-primary);
    border-color: var(--artdeco-gold-primary);
}
</style>