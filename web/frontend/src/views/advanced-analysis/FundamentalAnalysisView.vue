<template>
    <div class="fundamental-analysis">
        <!-- 财务比率指标 -->
        <div class="metrics-section">
            <h4>财务比率</h4>
            <div class="ratios-grid">
                <div v-for="ratio in financialRatios" :key="ratio.key" class="ratio-item">
                    <div class="ratio-value" :class="getRatioClass(ratio.value)">{{ ratio.value }}</div>
                    <div class="ratio-label">{{ ratio.label }}</div>
                </div>
            </div>
        </div>

        <!-- 偿债能力分析 -->
        <div class="metrics-section">
            <h4>偿债能力</h4>
            <div class="solvency-chart">
                <div class="chart-placeholder">
                    <svg viewBox="0 0 200 100" class="solvency-bars">
                        <rect x="20" y="60" width="20" height="20" fill="#67C23A"></rect>
                        <rect x="60" y="40" width="20" height="40" fill="#E6A23C"></rect>
                        <rect x="100" y="50" width="20" height="30" fill="#F56C6C"></rect>
                        <rect x="140" y="30" width="20" height="50" fill="#409EFF"></rect>
                        <text x="30" y="85" text-anchor="middle" font-size="10">流动比率</text>
                        <text x="70" y="85" text-anchor="middle" font-size="10">速动比率</text>
                        <text x="110" y="85" text-anchor="middle" font-size="10">现金比率</text>
                        <text x="150" y="85" text-anchor="middle" font-size="10">利息保障倍数</text>
                    </svg>
                </div>
            </div>
        </div>

        <!-- 盈利能力分析 -->
        <div class="metrics-section">
            <h4>盈利能力</h4>
            <div class="profitability-table">
                <table class="analysis-table">
                    <thead>
                        <tr>
                            <th>指标</th>
                            <th>数值</th>
                            <th>行业平均</th>
                            <th>评价</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="metric in profitabilityMetrics" :key="metric.key">
                            <td>{{ metric.label }}</td>
                            <td :class="getMetricClass(metric.value, metric.benchmark)">{{ metric.value }}</td>
                            <td>{{ metric.benchmark }}</td>
                            <td>
                                <el-tag :type="getEvaluationType(metric.evaluation)" size="small">
                                    {{ metric.evaluation }}
                                </el-tag>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- 杜邦分析 -->
        <div class="metrics-section">
            <h4>杜邦分析</h4>
            <div class="dupont-analysis">
                <div class="dupont-tree">
                    <div class="dupont-node root">
                        <div class="node-value">{{ dupontData.roa }}</div>
                        <div class="node-label">总资产报酬率</div>
                    </div>
                    <div class="dupont-branches">
                        <div class="dupont-node">
                            <div class="node-value">{{ dupontData.netProfitMargin }}</div>
                            <div class="node-label">净利率</div>
                        </div>
                        <div class="dupont-node">
                            <div class="node-value">{{ dupontData.assetTurnover }}</div>
                            <div class="node-label">总资产周转率</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { computed } from 'vue'

    interface Props {
        data: any
    }

    const props = defineProps<Props>()

    const financialRatios = computed(() => {
        if (!props.data) return []

        return [
            {
                key: 'pe',
                label: '市盈率',
                value: props.data.pe_ratio || 'N/A'
            },
            {
                key: 'pb',
                label: '市净率',
                value: props.data.pb_ratio || 'N/A'
            },
            {
                key: 'roe',
                label: '净资产收益率',
                value: props.data.roe ? `${props.data.roe}%` : 'N/A'
            },
            {
                key: 'debt_ratio',
                label: '资产负债率',
                value: props.data.debt_ratio ? `${props.data.debt_ratio}%` : 'N/A'
            }
        ]
    })

    const profitabilityMetrics = computed(() => {
        if (!props.data) return []

        return [
            {
                key: 'gross_margin',
                label: '毛利率',
                value: props.data.gross_margin ? `${props.data.gross_margin}%` : 'N/A',
                benchmark: '15-25%',
                evaluation: props.data.gross_margin > 20 ? '优秀' : props.data.gross_margin > 15 ? '良好' : '一般'
            },
            {
                key: 'net_margin',
                label: '净利率',
                value: props.data.net_margin ? `${props.data.net_margin}%` : 'N/A',
                benchmark: '5-10%',
                evaluation: props.data.net_margin > 8 ? '优秀' : props.data.net_margin > 5 ? '良好' : '一般'
            },
            {
                key: 'return_on_assets',
                label: '总资产报酬率',
                value: props.data.return_on_assets ? `${props.data.return_on_assets}%` : 'N/A',
                benchmark: '8-15%',
                evaluation:
                    props.data.return_on_assets > 12 ? '优秀' : props.data.return_on_assets > 8 ? '良好' : '一般'
            }
        ]
    })

    const dupontData = computed(() => {
        return {
            roa: props.data?.return_on_assets ? `${props.data.return_on_assets}%` : 'N/A',
            netProfitMargin: props.data?.net_margin ? `${props.data.net_margin}%` : 'N/A',
            assetTurnover: props.data?.asset_turnover || 'N/A'
        }
    })

    const getRatioClass = (value: string): string => {
        if (value === 'N/A') return 'neutral'
        // 这里可以根据具体数值判断好坏
        return 'normal'
    }

    const getMetricClass = (value: string, benchmark: string): string => {
        if (value === 'N/A') return 'neutral'
        // 这里可以实现更复杂的比较逻辑
        return 'normal'
    }

    const getEvaluationType = (evaluation: string): 'success' | 'warning' | 'danger' | 'info' => {
        switch (evaluation) {
            case '优秀':
                return 'success'
            case '良好':
                return 'warning'
            case '一般':
                return 'danger'
            default:
                return 'info'
        }
    }
</script>
