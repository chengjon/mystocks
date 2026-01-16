<template>
    <div class="artdeco-trading-signals">
        <!-- 交易信号概览 -->
        <div class="signals-overview">
            <ArtDecoStatCard
                label="买入信号"
                :value="getBuySignalsCount()"
                description="当前有效买入信号数量"
                variant="rise"
            />

            <ArtDecoStatCard
                label="卖出信号"
                :value="getSellSignalsCount()"
                description="当前有效卖出信号数量"
                variant="fall"
            />

            <ArtDecoStatCard
                label="信号成功率"
                :value="getSuccessRate()"
                description="近期信号准确率"
                variant="default"
            />

            <ArtDecoStatCard
                label="平均持仓期"
                :value="getAvgHoldingPeriod()"
                description="信号建议平均持仓时间"
                variant="default"
            />
        </div>

        <!-- 实时交易信号 -->
        <ArtDecoCard class="active-signals">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>实时交易信号</h4>
                        <p>REAL-TIME TRADING SIGNALS</p>
                    </div>
                    <div class="signal-controls">
                        <ArtDecoSelect v-model="signalFilter" :options="signalFilterOptions" size="sm" />
                        <ArtDecoSwitch v-model="autoRefresh" label="自动刷新" />
                    </div>
                </div>
            </template>

            <div class="signals-list">
                <div
                    v-for="signal in filteredSignals"
                    :key="signal.id"
                    class="signal-item"
                    :class="getSignalClass(signal)"
                >
                    <div class="signal-header">
                        <div class="signal-symbol">
                            <span class="symbol-code">{{ signal.symbol }}</span>
                            <span class="symbol-name">{{ signal.name }}</span>
                        </div>
                        <div class="signal-type" :class="signal.type">
                            <svg
                                v-if="signal.type === 'buy'"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                            >
                                <path d="M7 13l3 3 7-7"></path>
                                <path
                                    d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
                                ></path>
                            </svg>
                            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                            <span>{{ getSignalTypeText(signal.type) }}</span>
                        </div>
                        <div class="signal-strength">
                            <div class="strength-bar">
                                <div
                                    class="strength-fill"
                                    :style="{ width: signal.strength + '%' }"
                                    :class="getStrengthClass(signal.strength)"
                                ></div>
                            </div>
                            <span class="strength-text">{{ signal.strength }}%</span>
                        </div>
                    </div>

                    <div class="signal-details">
                        <div class="signal-reason">
                            <strong>触发原因:</strong>
                            {{ signal.reason }}
                        </div>
                        <div class="signal-indicators">
                            <div class="indicator-item">
                                <span class="label">价格:</span>
                                <span class="value">{{ signal.price }}</span>
                            </div>
                            <div class="indicator-item">
                                <span class="label">止损:</span>
                                <span class="value">{{ signal.stopLoss }}</span>
                            </div>
                            <div class="indicator-item">
                                <span class="label">目标:</span>
                                <span class="value">{{ signal.target }}</span>
                            </div>
                            <div class="indicator-item">
                                <span class="label">时间:</span>
                                <span class="value">{{ formatTime(signal.timestamp) }}</span>
                            </div>
                        </div>
                    </div>

                    <div class="signal-actions">
                        <ArtDecoButton
                            size="sm"
                            :type="signal.type === 'buy' ? 'primary' : 'danger'"
                            @click="handleSignalAction(signal, 'execute')"
                        >
                            执行交易
                        </ArtDecoButton>
                        <ArtDecoButton size="sm" variant="outline" @click="handleSignalAction(signal, 'ignore')">
                            忽略
                        </ArtDecoButton>
                        <ArtDecoButton size="sm" variant="outline" @click="handleSignalAction(signal, 'details')">
                            详情
                        </ArtDecoButton>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 信号历史记录 -->
        <ArtDecoCard class="signal-history">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>信号历史记录</h4>
                        <p>SIGNAL HISTORY LOG</p>
                    </div>
                    <div class="history-controls">
                        <ArtDecoSelect v-model="historyPeriod" :options="historyPeriodOptions" size="sm" />
                    </div>
                </div>
            </template>

            <div class="history-table">
                <div class="table-header">
                    <div class="col-symbol">股票代码</div>
                    <div class="col-type">信号类型</div>
                    <div class="col-strength">强度</div>
                    <div class="col-result">结果</div>
                    <div class="col-time">时间</div>
                </div>
                <div class="table-body">
                    <div
                        v-for="record in signalHistory"
                        :key="record.id"
                        class="table-row"
                        :class="getResultClass(record.result)"
                    >
                        <div class="col-symbol">
                            <span class="symbol-code">{{ record.symbol }}</span>
                        </div>
                        <div class="col-type">
                            <span :class="record.type">{{ getSignalTypeText(record.type) }}</span>
                        </div>
                        <div class="col-strength">
                            <div class="strength-mini-bar">
                                <div
                                    class="strength-mini-fill"
                                    :style="{ width: record.strength + '%' }"
                                    :class="getStrengthClass(record.strength)"
                                ></div>
                            </div>
                            <span class="strength-text">{{ record.strength }}%</span>
                        </div>
                        <div class="col-result">
                            <span :class="record.result">{{ getResultText(record.result) }}</span>
                        </div>
                        <div class="col-time">
                            {{ formatTime(record.timestamp) }}
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>

        <!-- 信号策略配置 -->
        <ArtDecoCard class="signal-strategy">
            <template #header>
                <div class="section-header">
                    <div class="header-icon">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <div class="header-content">
                        <h4>信号策略配置</h4>
                        <p>SIGNAL STRATEGY CONFIGURATION</p>
                    </div>
                </div>
            </template>

            <div class="strategy-config">
                <div class="config-group">
                    <h5>信号生成参数</h5>
                    <div class="config-items">
                        <div class="config-item">
                            <label>最低信号强度</label>
                            <ArtDecoSlider v-model="minSignalStrength" :min="50" :max="95" :step="5" unit="%" />
                        </div>
                        <div class="config-item">
                            <label>信号确认周期</label>
                            <ArtDecoSelect v-model="confirmationPeriod" :options="confirmationPeriodOptions" />
                        </div>
                        <div class="config-item">
                            <label>止损比例</label>
                            <ArtDecoSlider v-model="stopLossRatio" :min="1" :max="10" :step="0.5" unit="%" />
                        </div>
                        <div class="config-item">
                            <label>目标收益比例</label>
                            <ArtDecoSlider v-model="targetProfitRatio" :min="2" :max="20" :step="1" unit="%" />
                        </div>
                    </div>
                </div>

                <div class="config-group">
                    <h5>信号类型启用</h5>
                    <div class="signal-types">
                        <div v-for="signalType in availableSignalTypes" :key="signalType.key" class="signal-type-item">
                            <ArtDecoSwitch v-model="enabledSignalTypes[signalType.key]" :label="signalType.label" />
                            <p class="type-description">{{ signalType.description }}</p>
                        </div>
                    </div>
                </div>
            </div>
        </ArtDecoCard>
    </div>
</template>

<script setup lang="ts">
    import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'
    import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
    import ArtDecoSlider from '@/components/artdeco/specialized/ArtDecoSlider.vue'

    interface Props {
        data: any
        symbol?: string
        loading?: boolean
    }

    const props = defineProps<Props>()

    // 响应式数据
    const signalFilter = ref('all')
    const autoRefresh = ref(true)
    const historyPeriod = ref('1d')
    const minSignalStrength = ref(70)
    const confirmationPeriod = ref('1h')
    const stopLossRatio = ref(3)
    const targetProfitRatio = ref(8)

    const enabledSignalTypes = ref<Record<string, boolean>>({
        ma_cross: true,
        macd_signal: true,
        rsi_divergence: true,
        bollinger_break: true,
        volume_surge: true,
        pattern_recognition: false
    })

    // 计算属性
    const tradingSignals = computed(() => props.data?.signals || [])

    const filteredSignals = computed(() => {
        if (signalFilter.value === 'all') return tradingSignals.value
        if (signalFilter.value === 'buy') return tradingSignals.value.filter((s: any) => s.type === 'buy')
        if (signalFilter.value === 'sell') return tradingSignals.value.filter((s: any) => s.type === 'sell')
        return tradingSignals.value.filter((s: any) => s.strength >= 80)
    })

    const signalHistory = computed(() => props.data?.history || [])

    // 配置选项
    const signalFilterOptions = [
        { label: '全部信号', value: 'all' },
        { label: '买入信号', value: 'buy' },
        { label: '卖出信号', value: 'sell' },
        { label: '强信号', value: 'strong' }
    ]

    const historyPeriodOptions = [
        { label: '1天', value: '1d' },
        { label: '3天', value: '3d' },
        { label: '1周', value: '1w' },
        { label: '1月', value: '1M' }
    ]

    const confirmationPeriodOptions = [
        { label: '5分钟', value: '5m' },
        { label: '15分钟', value: '15m' },
        { label: '1小时', value: '1h' },
        { label: '4小时', value: '4h' }
    ]

    const availableSignalTypes = [
        { key: 'ma_cross', label: '均线交叉', description: '移动平均线金叉/死叉信号' },
        { key: 'macd_signal', label: 'MACD信号', description: 'MACD指标买卖信号' },
        { key: 'rsi_divergence', label: 'RSI背离', description: 'RSI指标与价格背离信号' },
        { key: 'bollinger_break', label: '布林带突破', description: '价格突破布林带上下轨' },
        { key: 'volume_surge', label: '成交量激增', description: '成交量异常放大信号' },
        { key: 'pattern_recognition', label: '形态识别', description: '经典技术形态识别' }
    ]

    // 辅助函数
    const getBuySignalsCount = (): string => {
        return tradingSignals.value.filter((s: any) => s.type === 'buy').length.toString()
    }

    const getSellSignalsCount = (): string => {
        return tradingSignals.value.filter((s: any) => s.type === 'sell').length.toString()
    }

    const getSuccessRate = (): string => {
        const history = signalHistory.value
        if (history.length === 0) return 'N/A'

        const successful = history.filter((h: any) => h.result === 'profit').length
        const total = history.filter((h: any) => h.result !== 'pending').length

        if (total === 0) return 'N/A'
        return `${((successful / total) * 100).toFixed(1)}%`
    }

    const getAvgHoldingPeriod = (): string => {
        const completedTrades = signalHistory.value.filter((h: any) => h.result !== 'pending' && h.holdingPeriod)
        if (completedTrades.length === 0) return 'N/A'

        const totalPeriod = completedTrades.reduce((sum: any, trade: any) => sum + trade.holdingPeriod, 0)
        const avgPeriod = totalPeriod / completedTrades.length

        if (avgPeriod < 60) return `${avgPeriod.toFixed(0)}分钟`
        if (avgPeriod < 1440) return `${(avgPeriod / 60).toFixed(1)}小时`
        return `${(avgPeriod / 1440).toFixed(1)}天`
    }

    const getSignalClass = (signal: any): string => {
        return `${signal.type} strength-${signal.strength >= 80 ? 'high' : signal.strength >= 60 ? 'medium' : 'low'}`
    }

    const getSignalTypeText = (type: string): string => {
        return type === 'buy' ? '买入' : '卖出'
    }

    const getStrengthClass = (strength: number): string => {
        if (strength >= 80) return 'high'
        if (strength >= 60) return 'medium'
        return 'low'
    }

    const getResultClass = (result: string): string => {
        if (result === 'profit') return 'profit'
        if (result === 'loss') return 'loss'
        return 'pending'
    }

    const getResultText = (result: string): string => {
        if (result === 'profit') return '盈利'
        if (result === 'loss') return '亏损'
        return '待定'
    }

    const formatTime = (timestamp: string): string => {
        return new Date(timestamp).toLocaleString('zh-CN', {
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    const handleSignalAction = (signal: any, action: string) => {
        // 处理信号操作
        console.log(`Signal action: ${action} for ${signal.symbol}`)
        // 这里可以调用API执行相应的操作
    }

    // 自动刷新定时器
    let refreshTimer: number | null = null

    const startAutoRefresh = () => {
        if (autoRefresh.value && !refreshTimer) {
            refreshTimer = setInterval(() => {
                // 触发数据刷新
                console.log('Auto refreshing trading signals...')
            }, 5000) as unknown as number
        }
    }

    const stopAutoRefresh = () => {
        if (refreshTimer) {
            clearInterval(refreshTimer)
            refreshTimer = null
        }
    }

    // 生命周期
    onMounted(() => {
        startAutoRefresh()
    })

    onUnmounted(() => {
        stopAutoRefresh()
    })

    // 监听自动刷新变化
    watch(autoRefresh, newValue => {
        if (newValue) {
            startAutoRefresh()
        } else {
            stopAutoRefresh()
        }
    })
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-trading-signals {
        display: grid;
        gap: var(--artdeco-spacing-6);
    }

    // ============================================
    //   SIGNALS OVERVIEW - 信号概览
    // ============================================

    .signals-overview {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: var(--artdeco-spacing-4);
    }

    // ============================================
    //   ACTIVE SIGNALS - 实时信号
    // ============================================

    .active-signals {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }

            .signal-controls {
                display: flex;
                gap: var(--artdeco-spacing-3);
                align-items: center;
            }
        }

        .signals-list {
            display: flex;
            flex-direction: column;
            gap: var(--artdeco-spacing-3);
        }

        .signal-item {
            @include artdeco-stepped-corners(6px);
            background: var(--artdeco-bg-card);
            border: 1px solid var(--artdeco-border-default);
            padding: var(--artdeco-spacing-4);
            position: relative;
            overflow: hidden;
            transition: all var(--artdeco-transition-base);

            // 几何角落装饰
            @include artdeco-geometric-corners($color: var(--artdeco-gold-primary), $size: 12px, $border-width: 1px);

            // 悬停效果
            @include artdeco-hover-lift-glow;

            // 内边框装饰
            &::before {
                content: '';
                position: absolute;
                top: 4px;
                left: 4px;
                right: 4px;
                bottom: 4px;
                border: 1px solid rgba(212, 175, 55, 0.1);
                pointer-events: none;
                opacity: 0.3;
                transition: opacity var(--artdeco-transition-base);
            }

            &:hover::before {
                opacity: 0.6;
            }

            &.buy {
                border-color: var(--artdeco-up);
                background: linear-gradient(135deg, rgba(34, 197, 94, 0.05), transparent);
            }

            &.sell {
                border-color: var(--artdeco-down);
                background: linear-gradient(135deg, rgba(239, 68, 68, 0.05), transparent);
            }

            &.strength-high {
                box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);
            }

            &.strength-medium {
                box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
            }
        }

        .signal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-3);

            .signal-symbol {
                flex: 1;

                .symbol-code {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-fg-primary);
                    margin-bottom: var(--artdeco-spacing-1);
                    display: block;
                }

                .symbol-name {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-sm);
                    color: var(--artdeco-fg-muted);
                }
            }

            .signal-type {
                display: flex;
                align-items: center;
                gap: var(--artdeco-spacing-2);
                padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
                border-radius: 4px;
                font-size: var(--artdeco-font-size-sm);
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);

                svg {
                    width: 16px;
                    height: 16px;
                }

                &.buy {
                    background: var(--artdeco-up);
                    color: white;
                }

                &.sell {
                    background: var(--artdeco-down);
                    color: white;
                }
            }

            .signal-strength {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: var(--artdeco-spacing-1);

                .strength-bar {
                    width: 80px;
                    height: 6px;
                    background: var(--artdeco-bg-muted);
                    border-radius: 3px;
                    overflow: hidden;

                    .strength-fill {
                        height: 100%;
                        border-radius: 3px;
                        transition: width var(--artdeco-transition-base);

                        &.high {
                            background: linear-gradient(
                                90deg,
                                var(--artdeco-gold-primary),
                                var(--artdeco-gold-secondary)
                            );
                        }

                        &.medium {
                            background: linear-gradient(90deg, #fbbf24, #f59e0b);
                        }

                        &.low {
                            background: linear-gradient(90deg, #ef4444, #dc2626);
                        }
                    }
                }

                .strength-text {
                    font-family: var(--artdeco-font-mono);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    font-weight: 600;
                }
            }
        }

        .signal-details {
            margin-bottom: var(--artdeco-spacing-3);

            .signal-reason {
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-font-size-sm);
                color: var(--artdeco-fg-secondary);
                margin-bottom: var(--artdeco-spacing-3);
                line-height: 1.5;

                strong {
                    color: var(--artdeco-fg-primary);
                    font-weight: 600;
                }
            }

            .signal-indicators {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
                gap: var(--artdeco-spacing-3);

                .indicator-item {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;

                    .label {
                        font-family: var(--artdeco-font-body);
                        font-size: var(--artdeco-font-size-xs);
                        color: var(--artdeco-fg-muted);
                        font-weight: 600;
                    }

                    .value {
                        font-family: var(--artdeco-font-mono);
                        font-size: var(--artdeco-font-size-sm);
                        color: var(--artdeco-fg-primary);
                        font-weight: 600;
                    }
                }
            }
        }

        .signal-actions {
            display: flex;
            gap: var(--artdeco-spacing-2);
            justify-content: flex-end;
        }
    }

    // ============================================
    //   SIGNAL HISTORY - 信号历史
    // ============================================

    .signal-history {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }

            .history-controls {
                display: flex;
                align-items: center;
            }
        }

        .history-table {
            .table-header {
                display: grid;
                grid-template-columns: 120px 100px 120px 80px 1fr;
                gap: var(--artdeco-spacing-4);
                padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
                background: linear-gradient(135deg, var(--artdeco-bg-muted), rgba(212, 175, 55, 0.05));
                border-bottom: 1px solid var(--artdeco-border-default);
                font-family: var(--artdeco-font-body);
                font-size: var(--artdeco-font-size-sm);
                font-weight: 600;
                color: var(--artdeco-fg-muted);
                text-transform: uppercase;
                letter-spacing: var(--artdeco-tracking-wide);
            }

            .table-body {
                .table-row {
                    display: grid;
                    grid-template-columns: 120px 100px 120px 80px 1fr;
                    gap: var(--artdeco-spacing-4);
                    padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
                    border-bottom: 1px solid rgba(212, 175, 55, 0.1);
                    transition: all var(--artdeco-transition-base);

                    &:hover {
                        background: rgba(212, 175, 55, 0.02);
                    }

                    &.profit {
                        border-left: 3px solid var(--artdeco-up);
                        background: linear-gradient(90deg, rgba(34, 197, 94, 0.03), transparent);
                    }

                    &.loss {
                        border-left: 3px solid var(--artdeco-down);
                        background: linear-gradient(90deg, rgba(239, 68, 68, 0.03), transparent);
                    }

                    .col-symbol {
                        font-family: var(--artdeco-font-mono);
                        font-weight: 600;
                        color: var(--artdeco-fg-primary);
                    }

                    .col-type {
                        font-size: var(--artdeco-font-size-sm);
                        font-weight: 600;
                        text-transform: uppercase;
                        letter-spacing: var(--artdeco-tracking-wide);

                        &.buy {
                            color: var(--artdeco-up);
                        }

                        &.sell {
                            color: var(--artdeco-down);
                        }
                    }

                    .col-strength {
                        display: flex;
                        align-items: center;
                        gap: var(--artdeco-spacing-2);

                        .strength-mini-bar {
                            width: 60px;
                            height: 4px;
                            background: var(--artdeco-bg-muted);
                            border-radius: 2px;
                            overflow: hidden;

                            .strength-mini-fill {
                                height: 100%;
                                border-radius: 2px;

                                &.high {
                                    background: linear-gradient(
                                        90deg,
                                        var(--artdeco-gold-primary),
                                        var(--artdeco-gold-secondary)
                                    );
                                }

                                &.medium {
                                    background: linear-gradient(90deg, #fbbf24, #f59e0b);
                                }

                                &.low {
                                    background: linear-gradient(90deg, #ef4444, #dc2626);
                                }
                            }
                        }

                        .strength-text {
                            font-family: var(--artdeco-font-mono);
                            font-size: var(--artdeco-font-size-xs);
                            color: var(--artdeco-fg-muted);
                            font-weight: 600;
                        }
                    }

                    .col-result {
                        font-size: var(--artdeco-font-size-sm);
                        font-weight: 600;

                        &.profit {
                            color: var(--artdeco-up);
                        }

                        &.loss {
                            color: var(--artdeco-down);
                        }

                        &.pending {
                            color: var(--artdeco-fg-muted);
                        }
                    }

                    .col-time {
                        font-family: var(--artdeco-font-mono);
                        font-size: var(--artdeco-font-size-xs);
                        color: var(--artdeco-fg-muted);
                    }
                }
            }
        }
    }

    // ============================================
    //   SIGNAL STRATEGY - 信号策略配置
    // ============================================

    .signal-strategy {
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: var(--artdeco-spacing-4);

            .header-icon {
                width: 48px;
                height: 48px;
                background: linear-gradient(135deg, var(--artdeco-gold-primary), var(--artdeco-gold-secondary));
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--artdeco-bg-dark);

                svg {
                    width: 24px;
                    height: 24px;
                }
            }

            .header-content {
                flex: 1;
                margin-left: var(--artdeco-spacing-4);

                h4 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-lg);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-1) 0;
                }

                p {
                    font-family: var(--artdeco-font-body);
                    font-size: var(--artdeco-font-size-xs);
                    color: var(--artdeco-fg-muted);
                    margin: 0;
                    letter-spacing: var(--artdeco-tracking-normal);
                }
            }
        }

        .strategy-config {
            .config-group {
                margin-bottom: var(--artdeco-spacing-5);

                &:last-child {
                    margin-bottom: 0;
                }

                h5 {
                    font-family: var(--artdeco-font-display);
                    font-size: var(--artdeco-font-size-md);
                    font-weight: 600;
                    color: var(--artdeco-gold-primary);
                    text-transform: uppercase;
                    letter-spacing: var(--artdeco-tracking-wide);
                    margin: 0 0 var(--artdeco-spacing-4) 0;
                }

                .config-items {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: var(--artdeco-spacing-4);
                }

                .config-item {
                    display: flex;
                    flex-direction: column;
                    gap: var(--artdeco-spacing-2);

                    label {
                        font-family: var(--artdeco-font-body);
                        font-size: var(--artdeco-font-size-sm);
                        font-weight: 600;
                        color: var(--artdeco-fg-primary);
                        text-transform: uppercase;
                        letter-spacing: var(--artdeco-tracking-wide);
                    }
                }

                .signal-types {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: var(--artdeco-spacing-3);

                    .signal-type-item {
                        display: flex;
                        flex-direction: column;
                        gap: var(--artdeco-spacing-2);
                        padding: var(--artdeco-spacing-3);
                        background: var(--artdeco-bg-card);
                        border: 1px solid var(--artdeco-border-default);
                        border-radius: 6px;
                        transition: all var(--artdeco-transition-base);

                        &:hover {
                            border-color: var(--artdeco-gold-primary);
                            box-shadow: 0 0 15px rgba(212, 175, 55, 0.1);
                        }

                        .type-description {
                            font-family: var(--artdeco-font-body);
                            font-size: var(--artdeco-font-size-xs);
                            color: var(--artdeco-fg-muted);
                            line-height: 1.4;
                        }
                    }
                }
            }
        }
    }

    // ============================================
    //   RESPONSIVE DESIGN - 响应式设计
    // ============================================

    @media (max-width: 768px) {
        .artdeco-trading-signals {
            gap: var(--artdeco-spacing-4);
        }

        .signals-overview {
            grid-template-columns: 1fr;
        }

        .active-signals {
            .section-header {
                flex-direction: column;
                align-items: flex-start;
                gap: var(--artdeco-spacing-3);

                .header-content {
                    margin-left: 0;
                }

                .signal-controls {
                    width: 100%;
                    justify-content: space-between;
                }
            }

            .signal-header {
                flex-direction: column;
                align-items: flex-start;
                gap: var(--artdeco-spacing-3);

                .signal-symbol,
                .signal-type,
                .signal-strength {
                    width: 100%;
                    justify-content: center;
                }
            }

            .signal-details {
                .signal-indicators {
                    grid-template-columns: 1fr;
                }
            }

            .signal-actions {
                flex-wrap: wrap;
                justify-content: center;
            }
        }

        .signal-history {
            .history-table {
                .table-header,
                .table-row {
                    grid-template-columns: 80px 60px 80px 60px 1fr;
                    gap: var(--artdeco-spacing-2);
                    font-size: var(--artdeco-font-size-xs);
                }
            }
        }

        .signal-strategy {
            .strategy-config {
                .config-group {
                    .config-items {
                        grid-template-columns: 1fr;
                    }

                    .signal-types {
                        grid-template-columns: 1fr;
                    }
                }
            }
        }
    }
</style>
