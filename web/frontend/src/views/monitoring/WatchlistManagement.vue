<template>
  <div class="watchlist-management fintech-bg-primary">
    <!-- 顶部标题栏 -->
    <div class="fintech-card elevated header-section">
      <div class="header-content">
        <div class="title-section">
          <h1 class="fintech-text-primary page-title">MONITORING PORTFOLIOS</h1>
          <p class="fintech-text-secondary page-subtitle">智能量化监控组合管理</p>
        </div>
        <div class="actions-section">
          <button class="fintech-btn primary" @click="showCreateModal">
            <plus-outlined />
            <span>CREATE PORTFOLIO</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 统计面板 -->
    <div class="stats-grid">
      <div class="fintech-card stat-card">
        <div class="stat-content">
          <div class="stat-value fintech-text-primary">{{ watchlists.length }}</div>
          <div class="stat-label fintech-text-secondary">ACTIVE PORTFOLIOS</div>
        </div>
        <div class="stat-icon">
          <folder-open-outlined />
        </div>
      </div>

      <div class="fintech-card stat-card">
        <div class="stat-content">
          <div class="stat-value fintech-text-primary">{{ totalStocks }}</div>
          <div class="stat-label fintech-text-secondary">TOTAL STOCKS</div>
        </div>
        <div class="stat-icon">
          <stock-outlined />
        </div>
      </div>

      <div class="fintech-card stat-card">
        <div class="stat-content">
          <div class="stat-value fintech-text-primary">{{ activeAlerts }}</div>
          <div class="stat-label fintech-text-secondary">ACTIVE ALERTS</div>
        </div>
        <div class="stat-icon">
          <alert-outlined />
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="content-grid">
      <!-- 组合列表 -->
      <div class="fintech-card main-content">
        <div class="card-header">
          <h3 class="fintech-text-primary card-title">PORTFOLIO LIST</h3>
          <div class="card-actions">
            <button class="fintech-btn" @click="refreshData">
              <reload-outlined />
            </button>
          </div>
        </div>

        <div class="portfolio-list" v-if="watchlists.length > 0">
          <div
            v-for="(portfolio, _idx) in watchlists"
            :key="portfolio.id"
            class="portfolio-item fintech-card interactive"
            @click="handlePortfolioClick(portfolio)"
          >
            <div class="portfolio-header">
              <div class="portfolio-info">
                <h4 class="portfolio-name fintech-text-primary">{{ portfolio.name }}</h4>
                <div class="portfolio-meta">
                  <span class="portfolio-type" :class="getTypeClass(portfolio.watchlist_type)">
                    {{ getTypeText(portfolio.watchlist_type) }}
                  </span>
                  <span class="portfolio-count fintech-text-secondary">
                    {{ portfolio.stocks_count || 0 }} STOCKS
                  </span>
                </div>
              </div>
              <div class="portfolio-status">
                <span class="status-indicator" :class="portfolio.is_active ? 'active' : 'inactive'">
                  {{ portfolio.is_active ? 'ACTIVE' : 'INACTIVE' }}
                </span>
              </div>
            </div>

            <div class="portfolio-actions">
              <button class="fintech-btn" @click.stop="editWatchlist(portfolio)">
                <edit-outlined />
              </button>
              <button class="fintech-btn" @click.stop="manageStocks(portfolio)">
                <setting-outlined />
              </button>
              <button class="fintech-btn danger" @click.stop="confirmDelete(portfolio)">
                <delete-outlined />
              </button>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <div class="empty-content">
            <folder-open-outlined class="empty-icon" />
            <h3 class="fintech-text-secondary">NO PORTFOLIOS YET</h3>
            <p class="fintech-text-tertiary">Create your first monitoring portfolio to get started</p>
            <button class="fintech-btn primary" @click="showCreateModal">
              <plus-outlined />
              CREATE FIRST PORTFOLIO
            </button>
          </div>
        </div>
      </div>

      <!-- 快速概览面板 -->
      <div class="fintech-card sidebar">
        <div class="card-header">
          <h3 class="fintech-text-primary card-title">QUICK OVERVIEW</h3>
        </div>

        <div class="overview-content">
          <div class="overview-item">
            <div class="overview-label fintech-text-secondary">TOTAL VALUE</div>
            <div class="overview-value fintech-text-primary">{{ formatCurrency(totalValue) }}</div>
          </div>

          <div class="overview-item">
            <div class="overview-label fintech-text-secondary">DAY P&L</div>
            <div class="overview-value" :class="totalPnL >= 0 ? 'fintech-text-up' : 'fintech-text-down'">
              {{ formatCurrency(totalPnL) }}
            </div>
          </div>

          <div class="overview-item">
            <div class="overview-label fintech-text-secondary">WIN RATE</div>
            <div class="overview-value fintech-text-primary">{{ winRate }}%</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 股票管理抽屉 -->
    <div class="stock-drawer-overlay" v-if="stockDrawerVisible" @click="stockDrawerVisible = false">
      <div class="stock-drawer fintech-card elevated" @click.stop>
        <div class="drawer-header">
          <h2 class="fintech-text-primary drawer-title">
            STOCK MANAGEMENT - {{ currentWatchlist?.name }}
          </h2>
          <div class="drawer-actions">
            <button class="fintech-btn" @click="stockDrawerVisible = false">
              <close-outlined />
            </button>
            <button class="fintech-btn primary" @click="showAddStockModal">
              <plus-outlined />
              ADD STOCK
            </button>
          </div>
        </div>

        <div class="drawer-content">
          <div class="stock-table-container">
            <table class="fintech-table stock-table">
              <thead>
                <tr>
                  <th>SYMBOL</th>
                  <th>ENTRY PRICE</th>
                  <th>CURRENT PRICE</th>
                  <th>P&L</th>
                  <th>REASON</th>
                  <th>STOP LOSS</th>
                  <th>TARGET</th>
                  <th>ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="stock in watchlistStocks" :key="stock.id" class="stock-row">
                  <td class="fintech-text-data">{{ stock.stock_code }}</td>
                  <td class="fintech-text-data">{{ formatPrice(stock.entry_price) }}</td>
                  <td class="fintech-text-data">{{ formatPrice(stock.current_price || stock.entry_price) }}</td>
                  <td :class="getPnlClass(stock)">
                    {{ getPnlPercent(stock) }}
                  </td>
                  <td>
                    <span class="reason-tag" :class="getReasonClass(stock.entry_reason)">
                      {{ getReasonText(stock.entry_reason) }}
                    </span>
                  </td>
                  <td class="fintech-text-data">{{ formatPrice(stock.stop_loss_price) }}</td>
                  <td class="fintech-text-data">{{ formatPrice(stock.target_price) }}</td>
                  <td>
                    <button class="fintech-btn danger" @click="confirmRemoveStock(stock)">
                      <delete-outlined />
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建/编辑组合弹窗 -->
    <div class="modal-overlay" v-if="createModalVisible" @click="createModalVisible = false">
      <div class="modal fintech-card elevated" @click.stop>
        <div class="modal-header">
          <h2 class="fintech-text-primary modal-title">
            {{ editingWatchlist ? 'EDIT PORTFOLIO' : 'CREATE PORTFOLIO' }}
          </h2>
          <button class="modal-close" @click="createModalVisible = false">
            <close-outlined />
          </button>
        </div>

        <form class="modal-form" @submit.prevent="handleCreateOrUpdate">
          <div class="form-group">
            <label class="form-label fintech-text-primary">PORTFOLIO NAME</label>
            <input
              v-model="watchlistForm.name"
              type="text"
              class="form-input fintech-text-primary"
              placeholder="Enter portfolio name"
              required
            />
          </div>

          <div class="form-group">
            <label class="form-label fintech-text-primary">PORTFOLIO TYPE</label>
            <select v-model="watchlistForm.watchlist_type" class="form-select fintech-text-primary">
              <option value="manual">MANUAL</option>
              <option value="strategy">STRATEGY</option>
              <option value="benchmark">BENCHMARK</option>
            </select>
          </div>

          <div class="form-group">
            <label class="form-label fintech-text-primary">RISK TOLERANCE</label>
            <div class="slider-container">
              <input
                v-model="riskTolerance"
                type="range"
                min="0"
                max="100"
                step="10"
                class="form-slider"
              />
              <div class="slider-labels">
                <span class="fintech-text-tertiary">CONSERVATIVE</span>
                <span class="fintech-text-primary">{{ riskTolerance }}%</span>
                <span class="fintech-text-tertiary">AGGRESSIVE</span>
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="fintech-btn" @click="createModalVisible = false">
              CANCEL
            </button>
            <button type="submit" class="fintech-btn primary">
              {{ editingWatchlist ? 'UPDATE' : 'CREATE' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 添加股票弹窗 -->
    <div class="modal-overlay" v-if="addStockModalVisible" @click="addStockModalVisible = false">
      <div class="modal fintech-card elevated" @click.stop>
        <div class="modal-header">
          <h2 class="fintech-text-primary modal-title">ADD STOCK</h2>
          <button class="modal-close" @click="addStockModalVisible = false">
            <close-outlined />
          </button>
        </div>

        <form class="modal-form" @submit.prevent="handleAddStock">
          <div class="form-row">
            <div class="form-group">
              <label class="form-label fintech-text-primary">SYMBOL</label>
              <input
                v-model="stockForm.stock_code"
                type="text"
                class="form-input fintech-text-primary"
                placeholder="e.g. 600519.SH"
                required
              />
            </div>
            <div class="form-group">
              <label class="form-label fintech-text-primary">ENTRY PRICE</label>
              <input
                v-model="stockForm.entry_price"
                type="number"
                step="0.01"
                class="form-input fintech-text-primary"
                placeholder="0.00"
                required
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label fintech-text-primary">ENTRY REASON</label>
            <select v-model="stockForm.entry_reason" class="form-select fintech-text-primary">
              <option value="macd_gold_cross">MACD GOLD CROSS</option>
              <option value="rsi_oversold">RSI OVERSOLD</option>
              <option value="volume_breakout">VOLUME BREAKOUT</option>
              <option value="manual_pick">MANUAL PICK</option>
              <option value="value_investment">VALUE INVESTMENT</option>
            </select>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label class="form-label fintech-text-primary">STOP LOSS</label>
              <input
                v-model="stockForm.stop_loss_price"
                type="number"
                step="0.01"
                class="form-input fintech-text-primary"
                placeholder="0.00"
              />
            </div>
            <div class="form-group">
              <label class="form-label fintech-text-primary">TARGET PRICE</label>
              <input
                v-model="stockForm.target_price"
                type="number"
                step="0.01"
                class="form-input fintech-text-primary"
                placeholder="0.00"
              />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label fintech-text-primary">WEIGHT</label>
            <div class="slider-container">
              <input
                v-model="stockForm.weight"
                type="range"
                min="0"
                max="1"
                step="0.01"
                class="form-slider"
              />
              <div class="slider-value fintech-text-primary">
                {{ (stockForm.weight * 100).toFixed(1) }}%
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="fintech-btn" @click="addStockModalVisible = false">
              CANCEL
            </button>
            <button type="submit" class="fintech-btn primary">
              ADD STOCK
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div class="modal-overlay" v-if="deleteConfirmVisible" @click="deleteConfirmVisible = false">
      <div class="modal fintech-card elevated" @click.stop>
        <div class="modal-header">
          <h2 class="fintech-text-primary modal-title">CONFIRM DELETE</h2>
          <button class="modal-close" @click="deleteConfirmVisible = false">
            <close-outlined />
          </button>
        </div>

        <div class="modal-content">
          <p class="fintech-text-primary confirm-message">
            Are you sure you want to delete portfolio "{{ portfolioToDelete?.name }}"?
          </p>
          <p class="fintech-text-secondary confirm-warning">
            This action cannot be undone.
          </p>
        </div>

        <div class="modal-actions">
          <button class="fintech-btn" @click="deleteConfirmVisible = false">
            CANCEL
          </button>
          <button class="fintech-btn danger" @click="deleteWatchlist(portfolioToDelete.id)">
            DELETE
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useWatchlistManagement } from './composables/useWatchlistManagement'

const { loading, watchlists, watchlistStocks, stockDrawerVisible, createModalVisible, addStockModalVisible, deleteConfirmVisible, currentWatchlist, editingWatchlist, portfolioToDelete, watchlistForm, stockForm, riskTolerance, totalStocks, totalValue, price, totalPnL, current, entry, pnl, winRate, winners, current, entry, activeAlerts, getTypeClass, classes, getTypeText, texts, getPnlClass, current, entry, pnl, getPnlPercent, current, entry, pnl, getReasonClass, classes, getReasonText, texts, formatCurrency, formatPrice, fetchWatchlists, res, data, fetchWatchlistStocks, res, data, refreshData, handlePortfolioClick, showCreateModal, editWatchlist, handleCreateOrUpdate, url, method, res, data, confirmDelete, deleteWatchlist, res, data, manageStocks, showAddStockModal, handleAddStock, res, data, confirmRemoveStock, removeStock, res, data } = useWatchlistManagement()
</script>

<style scoped>
@import './styles/WatchlistManagement';
</style>
