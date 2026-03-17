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
                    v-for="(signal, _idx) in filteredSignals"
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
                        v-for="(record, _idx) in signalHistory"
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
    import ArtDecoCard from '@/components/artdeco/base/ArtDecoCard.vue'
    import ArtDecoStatCard from '@/components/artdeco/base/ArtDecoStatCard.vue'
    import ArtDecoSelect from '@/components/artdeco/base/ArtDecoSelect.vue'
    import ArtDecoSwitch from '@/components/artdeco/base/ArtDecoSwitch.vue'
    import ArtDecoButton from '@/components/artdeco/base/ArtDecoButton.vue'
    import ArtDecoSlider from '@/components/artdeco/business/ArtDecoSlider.vue'

    import {
        useArtDecoTradingSignalsViewModel,
        type ArtDecoTradingSignalsProps
    } from './composables/useArtDecoTradingSignalsViewModel'

    const props = defineProps<ArtDecoTradingSignalsProps>()

    const {
        signalFilter,
        autoRefresh,
        historyPeriod,
        minSignalStrength,
        confirmationPeriod,
        stopLossRatio,
        targetProfitRatio,
        enabledSignalTypes,
        filteredSignals,
        signalHistory,
        signalFilterOptions,
        historyPeriodOptions,
        confirmationPeriodOptions,
        availableSignalTypes,
        getBuySignalsCount,
        getSellSignalsCount,
        getSuccessRate,
        getAvgHoldingPeriod,
        getSignalClass,
        getSignalTypeText,
        getStrengthClass,
        getResultClass,
        getResultText,
        formatTime,
        handleSignalAction
    } = useArtDecoTradingSignalsViewModel(props)
</script>

<style scoped lang="scss">
@import './styles/ArtDecoTradingSignals';
</style>
