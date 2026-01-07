<template>
  <el-row :gutter="24" class="overview-section">
    <el-col :xs="24" :sm="12" :md="6">
      <div class="stat-card">
        <div class="corner-tl"></div>
        <div class="stat-content">
          <div class="stat-info">
            <span class="stat-label">TOTAL ASSETS</span>
            <span class="stat-value gold">¥{{ formatNumber(portfolio.total_assets) }}</span>
          </div>
        </div>
      </div>
    </el-col>
    <el-col :xs="24" :sm="12" :md="6">
      <div class="stat-card">
        <div class="stat-content">
          <div class="stat-info">
            <span class="stat-label">AVAILABLE CASH</span>
            <span class="stat-value green">¥{{ formatNumber(portfolio.available_cash) }}</span>
          </div>
        </div>
      </div>
    </el-col>
    <el-col :xs="24" :sm="12" :md="6">
      <div class="stat-card">
        <div class="stat-content">
          <div class="stat-info">
            <span class="stat-label">POSITION VALUE</span>
            <span class="stat-value blue">¥{{ formatNumber(portfolio.position_value) }}</span>
          </div>
        </div>
      </div>
    </el-col>
    <el-col :xs="24" :sm="12" :md="6">
      <div class="stat-card">
        <div class="corner-br"></div>
        <div class="stat-content">
          <div class="stat-info">
            <span class="stat-label">TOTAL PROFIT</span>
            <span class="stat-value" :class="portfolio.total_profit >= 0 ? 'profit-up' : 'profit-down'">
              ¥{{ formatNumber(portfolio.total_profit) }}
              <span class="stat-percent">({{ portfolio.profit_rate }}%)</span>
            </span>
          </div>
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { reactive } from 'vue'

interface Portfolio {
  total_assets: number
  available_cash: number
  position_value: number
  total_profit: number
  profit_rate: number
}

const portfolio = reactive<Portfolio>({
  total_assets: 1000000,
  available_cash: 500000,
  position_value: 500000,
  total_profit: 50000,
  profit_rate: 5.0
})

const formatNumber = (value: number): string => {
  if (!value) return '0.00'
  return value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

defineExpose({
  setPortfolio: (data: Portfolio) => {
    Object.assign(portfolio, data)
  }
})
</script>

<style scoped lang="scss">

.overview-section {
  margin-bottom: var(--spacing-6);
  position: relative;
  z-index: 1;

  .stat-card {
    position: relative;
    background: var(--bg-card);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: var(--radius-none);
    padding: var(--spacing-5);
    transition: all var(--transition-slow);

      position: absolute;
      width: 16px;
      height: 16px;
      pointer-events: none;
      opacity: 0.6;
    }

      top: 8px;
      left: 8px;
      border-top: 2px solid var(--accent-gold);
      border-left: 2px solid var(--accent-gold);
    }

      bottom: 8px;
      right: 8px;
      border-bottom: 2px solid var(--accent-gold);
      border-right: 2px solid var(--accent-gold);
    }

    &:hover {
      border-color: var(--accent-gold);
      box-shadow: var(--glow-medium);
      transform: translateY(-2px);
    }

    .stat-content {
      .stat-info {
        text-align: center;

        .stat-label {
          display: block;
          font-family: var(--font-display);
          font-size: var(--font-size-xs);
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: var(--tracking-wider);
          color: var(--fg-muted);
          margin-bottom: var(--spacing-2);
        }

        .stat-value {
          display: block;
          font-family: var(--font-mono);
          font-size: var(--font-size-h4);
          font-weight: 700;
          color: var(--fg-primary);
          margin-bottom: 2px;

          &.gold { color: var(--accent-gold); }
          &.green { color: #27AE60; }
          &.blue { color: #4A90E2; }
          &.profit-up { color: var(--accent-gold); }
          &.profit-down { color: #27AE60; }

          .stat-percent {
            font-size: var(--font-size-small);
            margin-left: 4px;
          }
        }
      }
    }
  }
}
</style>
