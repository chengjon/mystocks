<template>
    <el-card v-show="activeTab === 'config'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>⚙️ 配置说明</span>
          <el-tag type="warning">文档</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>📝 配置文件结构</h3>
        <p>Freqtrade 使用 JSON 格式配置文件 (config.json):</p>

        <el-tabs type="border-card" class="config-tabs-offset">
          <el-tab-pane name="base-config" label="基础配置">
            <pre v-pre class="code-block">{
  "max_open_trades": 3,
  "stake_currency": "USDT",
  "stake_amount": "unlimited",
  "tradable_balance_ratio": 0.99,

  "dry_run": true,
  "dry_run_wallet": 1000,

  "timeframe": "5m",

  "exchange": {
    "name": "binance",
    "key": "your-api-key",
    "secret": "your-api-secret",
    "ccxt_config": {},
    "ccxt_async_config": {},
    "pair_whitelist": [
      "BTC/USDT",
      "ETH/USDT",
      "BNB/USDT"
    ],
    "pair_blacklist": []
  }
}</pre>
          </el-tab-pane>

          <el-tab-pane name="strategy-config" label="策略配置">
            <pre v-pre class="code-block">{
  "strategy": "SampleStrategy",
  "strategy_path": "user_data/strategies/",

  "minimal_roi": {
    "0": 0.10,
    "30": 0.05,
    "60": 0.01
  },

  "stoploss": -0.10,
  "trailing_stop": true,
  "trailing_stop_positive": 0.01,
  "trailing_stop_positive_offset": 0.02,
  "trailing_only_offset_is_reached": true,

  "unfilledtimeout": {
    "buy": 10,
    "sell": 10,
    "unit": "minutes"
  }
}</pre>
          </el-tab-pane>

          <el-tab-pane name="telegram" label="Telegram 机器人">
            <pre v-pre class="code-block">{
  "telegram": {
    "enabled": true,
    "token": "your-telegram-bot-token",
    "chat_id": "your-telegram-chat-id",
    "notification_settings": {
      "status": "on",
      "warning": "on",
      "startup": "on",
      "buy": "on",
      "sell": "on",
      "buy_cancel": "on",
      "sell_cancel": "on"
    }
  }
}</pre>
          </el-tab-pane>

          <el-tab-pane name="api-config" label="API 配置">
            <pre v-pre class="code-block">{
  "api_server": {
    "enabled": true,
    "listen_ip_address": "127.0.0.1",
    "listen_port": 8080,
    "verbosity": "error",
    "enable_openapi": true,
    "jwt_secret_key": "your-jwt-secret-key",
    "CORS_origins": [],
    "username": "admin",
    "password": "your-password"
  }
}</pre>
          </el-tab-pane>
        </el-tabs>

        <h3 class="config-section-heading">🔑 关键配置参数说明</h3>
        <el-descriptions :column="1" border class="config-descriptions">
          <el-descriptions-item label="max_open_trades">
            最大同时持仓数量,控制风险分散
          </el-descriptions-item>
          <el-descriptions-item label="stake_amount">
            每笔交易金额 ("unlimited" 表示自动计算)
          </el-descriptions-item>
          <el-descriptions-item label="dry_run">
            模拟交易模式 (true=模拟, false=实盘)
          </el-descriptions-item>
          <el-descriptions-item label="timeframe">
            K线周期 (1m, 5m, 15m, 1h, 4h, 1d 等)
          </el-descriptions-item>
          <el-descriptions-item label="stoploss">
            止损百分比 (负值,如 -0.10 表示 -10%)
          </el-descriptions-item>
          <el-descriptions-item label="trailing_stop">
            移动止损,跟随价格上涨自动调整止损点
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>

    <!-- 5. Web UI -->
</template>

<script setup lang="ts">
defineProps<{ activeTab: string }>()
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.config-tabs-offset {
  margin-top: var(--artdeco-spacing-5);
}

.config-section-heading {
  margin-top: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-3) / 2);
}

.config-descriptions {
  margin-top: calc(var(--artdeco-spacing-5) - var(--artdeco-spacing-1) - var(--artdeco-spacing-px));
}
</style>
