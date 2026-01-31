<style scoped lang="scss">
@import '@/styles/artdeco-quant-extended.scss';

.strategy-management {
    min-height: 900px;

    .management-header {
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

            .strategy-count {
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }
    }

    .strategy-stats {
        margin-bottom: var(--artdeco-spacing-6);

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--artdeco-spacing-4);
        }
    }

    .strategy-filters {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .strategy-grid-section {
        margin-bottom: var(--artdeco-spacing-6);

        .view-toggle {
            display: flex;
            gap: var(--artdeco-spacing-2);
            margin-bottom: var(--artdeco-spacing-4);

            .active {
                background: var(--artdeco-gold-primary);
                color: var(--artdeco-bg-primary);
                border-color: var(--artdeco-gold-primary);
            }
        }

        .strategy-cards-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: var(--artdeco-spacing-6);
        }

        .strategy-table-section {
            // 表格视图样式已在组件内部处理
        }
    }

    .batch-actions-section {
        .batch-actions-content {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-4);
            padding: var(--artdeco-spacing-4);

            .batch-buttons {
                display: flex;
                gap: var(--artdeco-spacing-3);
                flex-wrap: wrap;
            }

            .batch-stats {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
                text-align: center;
            }
        }
    }
}

// 表格单元格样式
.strategy-code-cell {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: var(--artdeco-spacing-1);

    .code {
        font-family: var(--artdeco-font-mono);
        font-weight: 600;
        color: var(--artdeco-gold-primary);
        font-size: var(--artdeco-text-sm);
    }
}

.strategy-name-cell {
    .name {
        font-family: var(--artdeco-font-body);
        font-weight: 600;
        color: var(--artdeco-fg-primary);
        display: block;
        margin-bottom: var(--artdeco-spacing-1);
    }

    .description {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        display: block;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
}

.return-cell {
    text-align: right;

    &.positive {
        .value {
            color: var(--artdeco-up);
        }
    }

    &.negative {
        .value {
            color: var(--artdeco-down);
        }
    }

    .value {
        font-family: var(--artdeco-font-mono);
        font-weight: 700;
        font-size: var(--artdeco-text-base);
        display: block;
    }

    .change {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
    }
}

.drawdown-cell, .sharpe-cell {
    text-align: right;

    .value {
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

// 新建策略表单样式
.create-strategy-form {
    display: flex;
    flex-direction: column;
    gap: var(--artdeco-spacing-4);

    .form-group {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-2);

        .form-label {
            font-family: var(--artdeco-font-body);
            font-weight: 500;
            color: var(--artdeco-fg-primary);
            font-size: var(--artdeco-text-sm);
        }
    }

    .strategy-description-input {
        width: 100%;
        padding: var(--artdeco-spacing-3);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: var(--artdeco-radius-none);
        background: var(--artdeco-bg-card);
        color: var(--artdeco-fg-primary);
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        resize: vertical;

        &:focus {
            outline: none;
            border-color: var(--artdeco-gold-primary);
            box-shadow: 0 0 0 2px rgba(255, 215, 0, 0.1);
        }

        &::placeholder {
            color: var(--artdeco-fg-muted);
        }
    }
}

// 响应式设计（桌面端优先）
@media (max-width: 1200px) {
    .strategy-management {
        .strategy-stats .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .strategy-cards-grid {
            grid-template-columns: 1fr;
        }
    }
}

@media (max-width: 768px) {
    .strategy-management {
        .management-header {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--artdeco-spacing-4);

            .header-actions {
                width: 100%;
                justify-content: space-between;
            }
        }

        .strategy-stats .stats-grid {
            grid-template-columns: 1fr;
        }

        .view-toggle {
            justify-content: center;
        }

        .batch-actions-content .batch-buttons {
            justify-content: center;
        }

        .action-buttons {
            flex-direction: column;
            align-items: stretch;
        }
    }
}

// 动画效果
.strategy-management {
    .strategy-stats,
    .strategy-grid-section,
    .batch-actions-section {
        animation: fadeInUp 0.6s ease-out;
    }

    .strategy-stats {
        animation-delay: 0.1s;
    }

    .strategy-grid-section {
        animation-delay: 0.2s;
    }

    .batch-actions-section {
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

// 卡片悬停效果
.strategy-cards-grid {
    .artdeco-strategy-card {
        transition: all var(--artdeco-transition-base);

        &:hover {
            transform: translateY(-4px);
            box-shadow: var(--artdeco-glow-strong);
        }
    }
}

// 视图切换动画
.view-toggle {
    .artdeco-btn {
        transition: all var(--artdeco-transition-base);
    }
}
</style>