<template>
    <el-card v-show="activeTab === 'backtest'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>📈 回测分析</span>
          <el-tag type="warning">文档</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>🔍 回测流程</h3>
        <p>Freqtrade 提供强大的回测功能,可以在历史数据上测试策略表现:</p>

        <el-steps :active="3" align-center style="margin: 30px 0;">
          <el-step title="下载数据" description="freqtrade download-data" />
          <el-step title="编写策略" description="实现 IStrategy 接口" />
          <el-step title="运行回测" description="freqtrade backtesting" />
          <el-step title="分析结果" description="查看报告和图表" />
        </el-steps>

        <h3 style="margin-top: 30px;">⚙️ 回测命令示例</h3>
        <el-tabs type="border-card" style="margin-top: 20px;">
          <el-tab-pane label="基础回测">
            <pre v-pre class="code-block"># 回测单个策略
freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --timeframe 5m

# 回测多个币对
freqtrade backtesting \
  --strategy SampleStrategy \
  --pairs BTC/USDT ETH/USDT BNB/USDT \
  --timerange 20210101-20211231

# 启用详细日志
freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --verbose</pre>
          </el-tab-pane>

          <el-tab-pane label="超参数优化">
            <pre v-pre class="code-block"># Hyperopt 参数优化
freqtrade hyperopt \
  --hyperopt-loss SharpeHyperOptLoss \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --epochs 500

# 只优化买入参数
freqtrade hyperopt \
  --spaces buy \
  --strategy SampleStrategy \
  --timerange 20210101-20211231

# 并行优化 (使用多核CPU)
freqtrade hyperopt \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --jobs 4</pre>
          </el-tab-pane>

          <el-tab-pane label="生成报告">
            <pre v-pre class="code-block"># 生成 HTML 回测报告
freqtrade backtesting \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --export trades \
  --export-filename backtest_results.json

freqtrade plot-dataframe \
  --strategy SampleStrategy \
  --timerange 20210101-20211231 \
  --indicators1 sma ema \
  --indicators2 rsi

# 生成利润图表
freqtrade plot-profit \
  --strategy SampleStrategy \
  --timerange 20210101-20211231</pre>
          </el-tab-pane>
        </el-tabs>

        <h3 style="margin-top: 30px;">📊 回测性能指标</h3>
        <el-table :data="metricsData" stripe style="margin-top: 15px;">
          <el-table-column prop="metric" label="指标" width="200" />
          <el-table-column prop="description" label="说明" />
          <el-table-column prop="target" label="目标值" width="150" />
        </el-table>

        <el-alert
          type="info"
          title="💡 回测结果解读"
          :closable="false"
          style="margin-top: 20px;"
        >
          <ul style="margin-top: 10px;">
            <li><strong>总收益率</strong>: 策略在回测期间的总收益,需考虑复利效应</li>
            <li><strong>胜率</strong>: 盈利交易占总交易的比例,≥ 50% 较好</li>
            <li><strong>盈亏比</strong>: 平均盈利 / 平均亏损,≥ 1.5 较好</li>
            <li><strong>最大回撤</strong>: 从峰值到谷底的最大跌幅,越小越好</li>
            <li><strong>夏普比率</strong>: 风险调整后收益,≥ 1.0 较好</li>
          </ul>
        </el-alert>
      </div>
    </el-card>

    <!-- 4. 配置说明 -->
</template>

<script setup lang="ts">
defineProps<{ 
  activeTab: string;
  metricsData: Array<{ metric: string; description: string; target: string }>;
}>()
</script>
