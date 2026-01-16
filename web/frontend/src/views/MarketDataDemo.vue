<!-- MarketDataDemo.vue - 演示统一API客户端的使用 -->
<template>
    <div class="market-data-demo">
        <h2>市场数据演示</h2>

        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading">
            <el-icon class="is-loading">
                <Loading />
            </el-icon>
            <span>正在加载市场数据...</span>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-message">
            <el-alert :title="error" type="error" :closable="false" show-icon />
            <el-button @click="refreshAllData" type="primary" size="small">重试</el-button>
        </div>

        <!-- 数据展示 -->
        <div v-else class="data-content">
            <!-- 市场概览 -->
            <el-card class="overview-card" shadow="hover">
                <template #header>
                    <div class="card-header">
                        <span>市场概览</span>
                        <el-button v-if="loadingOverview" type="text" size="small" disabled>
                            <el-icon class="is-loading">
                                <Loading />
                            </el-icon>
                            刷新中...
                        </el-button>
                        <el-button v-else type="text" size="small" @click="fetchMarketOverview(true)">刷新</el-button>
                    </div>
                </template>

                <div v-if="marketOverview" class="overview-content">
                    <div class="metric">
                        <span class="label">指数:</span>
                        <span class="value">{{ marketOverview.marketIndex || 'N/A' }}</span>
                    </div>
                    <div class="metric">
                        <span class="label">换手率:</span>
                        <span class="value">{{ marketOverview.turnoverRate || 'N/A' }}%</span>
                    </div>
                    <div class="metric">
                        <span class="label">涨跌家数:</span>
                        <span class="value">{{ marketOverview.riseFallCount || 'N/A' }}</span>
                    </div>
                </div>
                <div v-else class="no-data">暂无市场概览数据</div>
            </el-card>

            <!-- 股票基础数据 -->
            <el-card class="stocks-card" shadow="hover">
                <template #header>
                    <div class="card-header">
                        <span>股票基础数据</span>
                        <el-button v-if="loadingStocks" type="text" size="small" disabled>
                            <el-icon class="is-loading">
                                <Loading />
                            </el-icon>
                            加载中...
                        </el-button>
                        <el-button v-else type="text" size="small" @click="fetchStocksBasic()">刷新</el-button>
                    </div>
                </template>

                <div v-if="stocksBasic.length > 0" class="stocks-list">
                    <div v-for="stock in stocksBasic.slice(0, 5)" :key="stock.symbol" class="stock-item">
                        <span class="symbol">{{ stock.symbol }}</span>
                        <span class="name">{{ stock.name }}</span>
                        <span class="price" :class="{ up: stock.price_change > 0, down: stock.price_change < 0 }">
                            {{ stock.price }}
                        </span>
                    </div>
                </div>
                <div v-else class="no-data">暂无股票数据</div>
            </el-card>

            <!-- 行业和概念数据 -->
            <div class="categories-section">
                <el-row :gutter="20">
                    <el-col :span="12">
                        <el-card class="category-card" shadow="hover">
                            <template #header>
                                <div class="card-header">
                                    <span>行业分类</span>
                                    <el-button v-if="loadingIndustries" type="text" size="small" disabled>
                                        <el-icon class="is-loading">
                                            <Loading />
                                        </el-icon>
                                        加载中...
                                    </el-button>
                                    <el-button v-else type="text" size="small" @click="fetchStocksIndustries()">
                                        刷新
                                    </el-button>
                                </div>
                            </template>

                            <div v-if="stocksIndustries.length > 0" class="category-list">
                                <el-tag
                                    v-for="industry in stocksIndustries.slice(0, 10)"
                                    :key="industry.code"
                                    size="small"
                                    class="category-tag"
                                >
                                    {{ industry.name }}
                                </el-tag>
                            </div>
                            <div v-else class="no-data">暂无行业数据</div>
                        </el-card>
                    </el-col>

                    <el-col :span="12">
                        <el-card class="category-card" shadow="hover">
                            <template #header>
                                <div class="card-header">
                                    <span>概念分类</span>
                                    <el-button v-if="loadingConcepts" type="text" size="small" disabled>
                                        <el-icon class="is-loading">
                                            <Loading />
                                        </el-icon>
                                        加载中...
                                    </el-button>
                                    <el-button v-else type="text" size="small" @click="fetchStocksConcepts()">
                                        刷新
                                    </el-button>
                                </div>
                            </template>

                            <div v-if="stocksConcepts.length > 0" class="category-list">
                                <el-tag
                                    v-for="concept in stocksConcepts.slice(0, 10)"
                                    :key="concept.code"
                                    size="small"
                                    class="category-tag"
                                >
                                    {{ concept.name }}
                                </el-tag>
                            </div>
                            <div v-else class="no-data">暂无概念数据</div>
                        </el-card>
                    </el-col>
                </el-row>
            </div>

            <!-- 操作按钮 -->
            <div class="actions">
                <el-button type="primary" @click="refreshAllData" :loading="isLoading">刷新所有数据</el-button>
                <el-button @click="fetchAllMarketData">重新获取数据</el-button>
            </div>
        </div>
    </div>
</template>

<script setup>
    import { useMarketData } from '@/composables/useMarketData'
    import { Loading } from '@element-plus/icons-vue'

    // 使用市场数据 Composable
    const {
        // 数据
        marketOverview,
        stocksBasic,
        stocksIndustries,
        stocksConcepts,

        // 加载状态
        loadingOverview,
        loadingStocks,
        loadingIndustries,
        loadingConcepts,
        isLoading,

        // 错误状态
        error,

        // 方法
        fetchMarketOverview,
        fetchStocksBasic,
        fetchStocksIndustries,
        fetchStocksConcepts,
        fetchAllMarketData,
        refreshAllData
    } = useMarketData()
</script>

<style scoped lang="scss">
    .market-data-demo {
        padding: 20px;
        max-width: 1200px;
        margin: 0 auto;
    }

    .loading {
        text-align: center;
        padding: 40px;
        color: #666;

        .el-icon {
            font-size: 24px;
            margin-right: 10px;
        }
    }

    .error-message {
        margin-bottom: 20px;
    }

    .data-content {
        .overview-card,
        .stocks-card,
        .category-card {
            margin-bottom: 20px;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;

            .el-button {
                margin: 0;
            }
        }
    }

    .overview-content {
        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;

            &:last-child {
                border-bottom: none;
                margin-bottom: 0;
            }

            .label {
                font-weight: 500;
                color: #666;
            }

            .value {
                font-weight: 600;
                color: #333;

                &.up {
                    color: #f56c6c;
                }

                &.down {
                    color: #67c23a;
                }
            }
        }
    }

    .stocks-list {
        .stock-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 0;
            border-bottom: 1px solid #f5f5f5;

            &:last-child {
                border-bottom: none;
            }

            .symbol {
                font-weight: 600;
                color: #333;
                min-width: 80px;
            }

            .name {
                flex: 1;
                color: #666;
                margin: 0 15px;
            }

            .price {
                font-weight: 600;
                min-width: 80px;
                text-align: right;

                &.up {
                    color: #f56c6c;
                }

                &.down {
                    color: #67c23a;
                }
            }
        }
    }

    .categories-section {
        .category-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;

            .category-tag {
                margin: 0;
            }
        }
    }

    .no-data {
        text-align: center;
        color: #999;
        padding: 40px;
        font-style: italic;
    }

    .actions {
        text-align: center;
        margin-top: 30px;
        padding-top: 20px;
        border-top: 1px solid #f0f0f0;

        .el-button {
            margin: 0 10px;
        }
    }

    // 响应式设计
    @media (max-width: 768px) {
        .market-data-demo {
            padding: 10px;
        }

        .categories-section {
            .el-col {
                margin-bottom: 20px;

                &:last-child {
                    margin-bottom: 0;
                }
            }
        }

        .stocks-list .stock-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 4px;

            .name {
                margin: 0;
            }

            .price {
                align-self: flex-end;
            }
        }

        .actions .el-button {
            display: block;
            width: 100%;
            margin: 5px 0;
        }
    }
</style>
