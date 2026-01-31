<style scoped lang="scss">
@import '@/styles/artdeco-quant-extended.scss';

.announcement-monitor {
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

            .unread-count {
                font-size: var(--artdeco-text-xs);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }
        }
    }

    .announcement-stats {
        margin-bottom: var(--artdeco-spacing-6);

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: var(--artdeco-spacing-4);
        }
    }

    .announcement-filters {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .announcements-section {
        margin-bottom: var(--artdeco-spacing-6);
    }

    .monitor-settings-section {
        .settings-content {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-6);
            padding: var(--artdeco-spacing-4);

            .setting-group {
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

            .setting-actions {
                display: flex;
                gap: var(--artdeco-spacing-3);
                justify-content: flex-end;
            }
        }
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

.title-cell {
    .announcement-title {
        font-family: var(--artdeco-font-body);
        font-weight: 600;
        color: var(--artdeco-fg-primary);
        font-size: var(--artdeco-text-sm);
        display: block;
        margin-bottom: var(--artdeco-spacing-2);
        line-height: 1.4;
    }

    .title-meta {
        display: flex;
        gap: var(--artdeco-spacing-2);
    }
}

.impact-cell {
    text-align: center;
}

.time-cell {
    .publish-time {
        font-family: var(--artdeco-font-mono);
        font-size: var(--artdeco-text-sm);
        color: var(--artdeco-fg-primary);
        display: block;
    }

    .relative-time {
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

// 公告详情弹窗样式
.announcement-detail {
    .detail-header {
        margin-bottom: var(--artdeco-spacing-6);
        padding-bottom: var(--artdeco-spacing-4);
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);

        .detail-meta {
            display: flex;
            gap: var(--artdeco-spacing-3);
            margin-bottom: var(--artdeco-spacing-3);
        }

        .detail-company {
            display: flex;
            flex-direction: column;

            .company-symbol {
                font-family: var(--artdeco-font-mono);
                font-weight: 600;
                color: var(--artdeco-gold-primary);
                font-size: var(--artdeco-text-lg);
            }

            .company-name {
                font-family: var(--artdeco-font-body);
                color: var(--artdeco-fg-muted);
                font-size: var(--artdeco-text-sm);
                margin-top: 2px;
            }
        }

        .detail-time {
            font-family: var(--artdeco-font-body);
            color: var(--artdeco-fg-muted);
            font-size: var(--artdeco-text-sm);
        }
    }

    .detail-content {
        h3 {
            @include artdeco-gold-accent;
            font-family: var(--artdeco-font-display);
            font-size: var(--artdeco-text-lg);
            font-weight: 600;
            margin: var(--artdeco-spacing-6) 0 var(--artdeco-spacing-3) 0;
            text-transform: uppercase;
            letter-spacing: var(--artdeco-tracking-wide);

            &:first-child {
                margin-top: 0;
            }
        }

        p {
            font-family: var(--artdeco-font-body);
            color: var(--artdeco-fg-primary);
            line-height: 1.6;
            margin-bottom: var(--artdeco-spacing-4);
        }

        .announcement-content {
            font-family: var(--artdeco-font-body);
            color: var(--artdeco-fg-primary);
            line-height: 1.6;
            white-space: pre-wrap;
            background: var(--artdeco-bg-card);
            padding: var(--artdeco-spacing-4);
            border-radius: var(--artdeco-radius-none);
            border: 1px solid rgba(212, 175, 55, 0.1);
        }

        .impact-analysis {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-3);

            .impact-item {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: var(--artdeco-spacing-3);
                background: var(--artdeco-bg-card);
                border: 1px solid rgba(212, 175, 55, 0.1);
                border-radius: var(--artdeco-radius-none);

                .impact-label {
                    font-family: var(--artdeco-font-body);
                    font-weight: 500;
                    color: var(--artdeco-fg-primary);
                }

                .impact-value {
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
    .announcement-monitor {
        .stats-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }
}

@media (max-width: 768px) {
    .announcement-monitor {
        .monitor-header {
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

        .setting-options {
            grid-template-columns: 1fr !important;
        }

        .setting-actions {
            flex-direction: column;
            align-items: stretch;
        }

        .detail-meta {
            flex-wrap: wrap;
        }

        .impact-analysis .impact-item {
            flex-direction: column;
            align-items: flex-start;
            gap: var(--artdeco-spacing-2);
        }
    }
}

// 动画效果
.announcement-monitor {
    .announcement-stats,
    .announcements-section,
    .monitor-settings-section {
        animation: fadeInUp 0.6s ease-out;
    }

    .announcement-stats {
        animation-delay: 0.1s;
    }

    .announcements-section {
        animation-delay: 0.2s;
    }

    .monitor-settings-section {
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

// 未读公告高亮
.announcements-section {
    .artdeco-table__row {
        &:has(.artdeco-status[status="info"]) {
            background: rgba(255, 213, 79, 0.05);
            border-left: 3px solid var(--artdeco-gold-primary);
        }
    }
}

// 重要公告标记
.title-meta {
    .artdeco-badge {
        animation: pulse 2s infinite;
    }
}
</style>