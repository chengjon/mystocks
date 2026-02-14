<template>
    <div class="tdx-interface-container">
        <!-- Page Header -->
        <div class="page-header">
            <div class="header-title-section">
                <h1 class="page-title">
                    <el-icon><Connection /></el-icon>
                    TDX DATA INTERFACE
                </h1>
                <p class="page-subtitle">TONGDA XIN PROFESSIONAL MARKET DATA SOURCE INTEGRATION</p>
            </div>
            <div class="header-actions">
                <el-button type="primary" @click="refreshAllData" :loading="loading">
                    <template #icon>
                        <RefreshRight />
                    </template>
                    REFRESH ALL
                </el-button>
                <el-tag :type="connectionStatus === 'connected' ? 'success' : 'warning'" size="small">
                    TDX {{ connectionStatus === 'connected' ? 'CONNECTED' : 'CONNECTING' }}
                </el-tag>
            </div>
        </div>

        <!-- Connection Status -->
        <div class="status-section">
            <el-card class="status-card" shadow="never">
                <div class="status-content">
                    <div class="status-item">
                        <div class="status-icon">
                            <el-icon :class="{ connected: connectionStatus === 'connected' }">
                                <Connection />
                            </el-icon>
                        </div>
                        <div class="status-info">
                            <span class="status-label">Connection Status</span>
                            <span class="status-value" :class="{ connected: connectionStatus === 'connected' }">
                                {{
                                    connectionStatus === 'connected'
                                        ? 'Connected to TDX Server'
                                        : 'Attempting to Connect...'
                                }}
                            </span>
                        </div>
                    </div>

                    <div class="status-item">
                        <div class="status-icon">
                            <el-icon>
                                <Timer />
                            </el-icon>
                        </div>
                        <div class="status-info">
                            <span class="status-label">Response Time</span>
                            <span class="status-value">{{ responseTime }}ms</span>
                        </div>
                    </div>

                    <div class="status-item">
                        <div class="status-icon">
                            <el-icon>
                                <DataLine />
                            </el-icon>
                        </div>
                        <div class="status-info">
                            <span class="status-label">Active Sessions</span>
                            <span class="status-value">{{ activeSessions }}</span>
                        </div>
                    </div>
                </div>
            </el-card>
        </div>

        <!-- Main Content Grid -->
        <div class="content-grid">
            <!-- Real-time Quotes Section -->
            <el-card class="quotes-card" shadow="never">
                <template #header>
                    <div class="card-header">
                        <span class="card-title">REAL-TIME QUOTES</span>
                        <div class="header-controls">
                            <el-input
                                v-model="searchSymbol"
                                placeholder="Enter symbol (e.g., 600519)"
                                size="small"
                                clearable
                                class="symbol-input"
                                @keyup.enter="fetchQuote"
                            >
                                <template #prefix>
                                    <Search />
                                </template>
                            </el-input>
                            <el-button type="primary" size="small" @click="fetchQuote" :loading="quoteLoading">
                                QUERY
                            </el-button>
                        </div>
                    </div>
                </template>

                <!-- Current Quote Display -->
                <div v-if="currentQuote" class="quote-display">
                    <div class="quote-header">
                        <div class="stock-info">
                            <span class="stock-code">{{ currentQuote.code }}</span>
                            <span class="stock-name">{{ currentQuote.name || 'Unknown' }}</span>
                            <el-tag :type="currentQuote.status === 'trading' ? 'success' : 'warning'" size="small">
                                {{ currentQuote.status === 'trading' ? 'TRADING' : 'CLOSED' }}
                            </el-tag>
                        </div>
                    </div>

                    <div class="quote-main">
                        <div class="price-section">
                            <div class="current-price" :class="getPriceClass(currentQuote.change_pct)">
                                {{ currentQuote.price?.toFixed(2) || '--' }}
                            </div>
                            <div class="price-change" :class="getPriceClass(currentQuote.change_pct)">
                                <span class="change-value">{{ formatChange(currentQuote.change) }}</span>
                                <span class="change-percent">({{ formatChangePct(currentQuote.change_pct) }})</span>
                            </div>
                        </div>
                    </div>

                    <div class="quote-details">
                        <div class="detail-grid">
                            <div class="detail-item">
                                <span class="label">Open:</span>
                                <span class="value">{{ currentQuote.open?.toFixed(2) || '--' }}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Prev Close:</span>
                                <span class="value">{{ currentQuote.pre_close?.toFixed(2) || '--' }}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">High:</span>
                                <span class="value">{{ currentQuote.high?.toFixed(2) || '--' }}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Low:</span>
                                <span class="value">{{ currentQuote.low?.toFixed(2) || '--' }}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Volume:</span>
                                <span class="value">{{ formatVolume(currentQuote.volume) }}</span>
                            </div>
                            <div class="detail-item">
                                <span class="label">Amount:</span>
                                <span class="value">{{ formatAmount(currentQuote.amount) }}</span>
                            </div>
                        </div>
                    </div>

                    <!-- Bid/Ask Spread -->
                    <div class="bid-ask-section">
                        <h4 class="section-title">Bid/Ask Spread</h4>
                        <div class="bid-ask-grid">
                            <div class="bid-ask-item ask">
                                <span class="level">Sell 1</span>
                                <span class="price">{{ currentQuote.ask1?.toFixed(2) || '--' }}</span>
                                <span class="volume">{{ formatVolume(currentQuote.ask1_volume, true) }}</span>
                            </div>
                            <div class="bid-ask-item bid">
                                <span class="level">Buy 1</span>
                                <span class="price">{{ currentQuote.bid1?.toFixed(2) || '--' }}</span>
                                <span class="volume">{{ formatVolume(currentQuote.bid1_volume, true) }}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Empty State -->
                <div v-else class="empty-state">
                    <el-empty description="Enter a stock symbol to view real-time quotes" :image-size="80">
                        <template #image>
                            <el-icon size="80" class="placeholder-icon">
                                <Connection />
                            </el-icon>
                        </template>
                    </el-empty>
                </div>
            </el-card>

            <!-- K-Line Chart Section -->
            <el-card class="kline-card" shadow="never">
                <template #header>
                    <div class="card-header">
                        <span class="card-title">K-LINE CHART</span>
                        <div class="header-controls">
                            <el-select
                                v-model="selectedPeriod"
                                placeholder="Period"
                                size="small"
                                class="period-select"
                                @change="changePeriod"
                            >
                                <el-option label="1 Minute" value="1m" />
                                <el-option label="5 Minutes" value="5m" />
                                <el-option label="15 Minutes" value="15m" />
                                <el-option label="30 Minutes" value="30m" />
                                <el-option label="1 Hour" value="1h" />
                                <el-option label="Daily" value="1d" />
                            </el-select>
                            <el-date-picker
                                v-model="chartDateRange"
                                type="daterange"
                                range-separator="to"
                                start-placeholder="Start Date"
                                end-placeholder="End Date"
                                size="small"
                                class="date-picker"
                                @change="changeDateRange"
                            />
                        </div>
                    </div>
                </template>

                <div class="chart-container" v-loading="chartLoading">
                    <div v-if="!searchSymbol" class="no-chart-placeholder">
                        <el-empty description="Select a symbol and period to view K-line chart" :image-size="60" />
                    </div>

                    <div v-else ref="chartContainer" class="kline-chart" :style="{ height: chartHeight }"></div>
                </div>
            </el-card>
        </div>

        <!-- Server Information -->
        <div class="server-info-section">
            <el-card class="server-info-card" shadow="never">
                <template #header>
                    <div class="card-header">
                        <span class="card-title">TDX SERVER INFORMATION</span>
                    </div>
                </template>

                <div class="server-grid">
                    <div class="server-item">
                        <span class="server-label">Primary Server</span>
                        <span class="server-value">{{ primaryServer }}</span>
                        <el-tag type="success" size="small">Active</el-tag>
                    </div>

                    <div class="server-item">
                        <span class="server-label">Backup Servers</span>
                        <span class="server-value">{{ backupServers.length }} configured</span>
                        <el-tag type="info" size="small">Ready</el-tag>
                    </div>

                    <div class="server-item">
                        <span class="server-label">Data Types</span>
                        <span class="server-value">Stocks, Futures, Options</span>
                        <el-tag type="warning" size="small">Multiple</el-tag>
                    </div>

                    <div class="server-item">
                        <span class="server-label">Update Frequency</span>
                        <span class="server-value">Real-time</span>
                        <el-tag type="success" size="small">High</el-tag>
                    </div>
                </div>
            </el-card>
        </div>
    </div>
</template>

<script setup lang="ts">
import { useTdx } from './composables/useTdx'

const { loading, quoteLoading, chartLoading, searchSymbol, selectedPeriod, chartHeight, lastUpdate, connectionStatus, responseTime, activeSessions, primaryServer, backupServers, currentQuote, chartDateRange, refreshAllData, checkConnectionStatus, fetchQuote, changePeriod, changeDateRange, loadChartData, updateLastUpdateTime, now, getPriceClass, formatChange, formatChangePct, formatVolume, formatAmount } = useTdx()
</script>

<style scoped lang="scss">
@import './styles/Tdx.scss';
</style>
