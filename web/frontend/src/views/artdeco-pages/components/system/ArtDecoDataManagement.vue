<style scoped lang="scss">
@import '@/styles/artdeco-quant-extended.scss';

.data-management {
    min-height: 1000px;

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

            .data-health {
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }
    }

    .data-sources-overview {
        margin-bottom: var(--artdeco-spacing-6);

        .overview-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--artdeco-spacing-4);
        }
    }

    .data-sources-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .data-quality-section {
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

        .quality-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: var(--artdeco-spacing-4);
        }
    }

    .backup-section,
    .cleanup-section {
        // 折叠面板样式已在组件内部处理
    }
}

// 健康评分单元格样式
.health-score-cell {
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

.last-sync-cell {
    .sync-time {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-primary);
        display: block;
    }

    .sync-ago {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-xs);
        color: var(--artdeco-fg-muted);
        margin-top: 2px;
    }
}

.data-size-cell {
    text-align: right;

    .size-value {
        font-family: var(--artdeco-font-mono);
        font-weight: 600;
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-primary);
        display: block;
    }

    .size-records {
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

// 数据质量卡片内容样式
.quality-content {
    .quality-metric {
        display: flex;
        align-items: baseline;
        justify-content: space-between;
        margin-bottom: var(--artdeco-spacing-3);

        .metric-value {
            font-family: var(--artdeco-font-mono);
            font-size: var(--artdeco-text-2xl);
            font-weight: 700;
            color: var(--artdeco-gold-primary);
        }

        .metric-change {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            font-weight: 600;

            &.positive {
                color: var(--artdeco-up);
            }

            &.negative {
                color: var(--artdeco-down);
            }
        }
    }

    .quality-description {
        font-family: var(--artdeco-font-body);
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-muted);
        margin-top: var(--artdeco-spacing-2);
    }
}

// 备份相关样式
.backup-content {
    .backup-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: var(--artdeco-spacing-6);
    }

    .backup-config {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-4);

        .config-item {
            display: flex;
            align-items: center;
            justify-content: space-between;

            .config-label {
                font-family: var(--artdeco-font-body);
                font-weight: 500;
                color: var(--artdeco-fg-primary);
                font-size: var(--artdeco-text-sm);
            }
        }
    }

    .manual-backup {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-4);
        align-items: flex-start;

        .last-backup {
            font-family: var(--artdeco-font-body);
            font-size: var(--artdeco-text-sm);
            color: var(--artdeco-fg-muted);
        }
    }

    .backup-history {
        display: flex;
        flex-direction: column;
        gap: var(--artdeco-spacing-3);
        max-height: 300px;
        overflow-y: auto;

        .backup-item {
            display: grid;
            grid-template-columns: 1fr auto auto;
            gap: var(--artdeco-spacing-4);
            padding: var(--artdeco-spacing-3);
            background: var(--artdeco-bg-card);
            border: 1px solid rgba(212, 175, 55, 0.1);
            border-radius: var(--artdeco-radius-none);
            align-items: center;

            .backup-info {
                display: flex;
                flex-direction: column;

                .backup-name {
                    font-family: var(--artdeco-font-body);
                    font-weight: 600;
                    color: var(--artdeco-fg-primary);
                    font-size: var(--artdeco-text-sm);
                }

                .backup-size {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-text-xs);
                    color: var(--artdeco-fg-muted);
                    margin-top: 2px;
                }
            }

            .backup-time {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
            }

            .backup-actions {
                display: flex;
                gap: var(--artdeco-spacing-2);
            }
        }
    }
}

// 数据清理样式
.cleanup-content {
    .cleanup-stats {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: var(--artdeco-spacing-4);
        margin-bottom: var(--artdeco-spacing-6);

        .stat-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: var(--artdeco-spacing-4);
            background: var(--artdeco-bg-card);
            border: 1px solid rgba(212, 175, 55, 0.1);
            border-radius: var(--artdeco-radius-none);

            .stat-label {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-text-sm);
                color: var(--artdeco-fg-muted);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
                margin-bottom: var(--artdeco-spacing-2);
            }

            .stat-value {
                font-family: var(--artdeco-font-mono);
                font-size: var(--artdeco-text-lg);
                font-weight: 600;
                color: var(--artdeco-gold-primary);
            }
        }
    }

    .cleanup-actions {
        display: flex;
        gap: var(--artdeco-spacing-3);
        justify-content: flex-end;
    }
}

// 响应式设计（桌面端优先）
@media (max-width: 1200px) {
    .data-management {
        .overview-grid {
            grid-template-columns: repeat(2, 1fr);
        }

        .quality-grid {
            grid-template-columns: 1fr;
        }

        .backup-grid {
            grid-template-columns: 1fr;
        }

        .cleanup-stats {
            grid-template-columns: repeat(2, 1fr);
        }
    }
}

@media (max-width: 768px) {
    .data-management {
        .management-header {
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

        .backup-config .config-item {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--artdeco-spacing-2);
        }

        .backup-item {
            grid-template-columns: 1fr !important;
            gap: var(--artdeco-spacing-2) !important;

            .backup-actions {
                justify-content: flex-end;
            }
        }

        .cleanup-actions {
            flex-direction: column;
            align-items: stretch;
        }
    }
}

// 动画效果
.data-management {
    .data-sources-overview,
    .data-sources-section,
    .data-quality-section,
    .backup-section,
    .cleanup-section {
        animation: fadeInUp 0.6s ease-out;
    }

    .data-sources-overview {
        animation-delay: 0.1s;
    }

    .data-sources-section {
        animation-delay: 0.2s;
    }

    .data-quality-section {
        animation-delay: 0.3s;
    }

    .backup-section {
        animation-delay: 0.4s;
    }

    .cleanup-section {
        animation-delay: 0.5s;
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
</style>