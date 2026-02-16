<template>
    <el-card v-show="activeTab === 'overview'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>PROJECT OVERVIEW</span>
          <el-tag type="success">MIGRATED</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>INTRODUCTION</h3>
        <p>pytdx is a pure Python implementation of Tongdaxin network protocol interface library. It provides a complete Python API for obtaining real-time and historical market data by reverse engineering Tongdaxin's network protocol, without requiring Tongdaxin client installation.</p>

        <h3 style="margin-top: 30px;">CORE FEATURES</h3>
        <div class="features-grid">
          <el-card :hoverable="true">
            <h4>MARKET DATA API</h4>
            <ul>
              <li>Real-time Quotes (Level-1)</li>
              <li>Historical K-line Data (Daily/Weekly/Monthly/Minute)</li>
              <li>Intraday Data (Tick Level)</li>
              <li>Order Book Data (5-level Bid/Ask)</li>
              <li>Transaction History</li>
            </ul>
          </el-card>

          <el-card :hoverable="true">
            <h4>BASIC DATA API</h4>
            <ul>
              <li>Stock List Query (A-Shares/Indices/Sectors)</li>
              <li>Financial Data Query</li>
              <li>Company Information</li>
              <li>Ex-dividend Data</li>
              <li>Sector Components</li>
            </ul>
          </el-card>

          <el-card :hoverable="true">
            <h4>EXTENDED API</h4>
            <ul>
              <li>Level-2 10-level Quotes (requires permission)</li>
              <li>Tick-by-tick Order Data</li>
              <li>Main Force Capital Flow</li>
              <li>Dragon Tiger List Data</li>
              <li>Large Order Tracking</li>
            </ul>
          </el-card>

          <el-card :hoverable="true">
            <h4>TOOLS</h4>
            <ul>
              <li>Cross-platform (Windows/Mac/Linux)</li>
              <li>Auto Server Selection & Load Balancing</li>
              <li>Data Caching Mechanism</li>
              <li>Concurrent Request Support</li>
              <li>Error Retry Mechanism</li>
            </ul>
          </el-card>
        </div>

        <h3 style="margin-top: 30px;">PROJECT ADVANTAGES</h3>
        <el-descriptions :column="2" border style="margin-top: 15px;" class="descriptions">
          <el-descriptions-item label="PURE PYTHON">
            No Tongdaxin client required, cross-platform support
          </el-descriptions-item>
          <el-descriptions-item label="FREE">
            Completely free, no data interface purchase required
          </el-descriptions-item>
          <el-descriptions-item label="REAL-TIME DATA">
            Direct connection to Tongdaxin servers
          </el-descriptions-item>
          <el-descriptions-item label="HISTORICAL DATA">
            Complete historical K-line data support</el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 30px;">LIBRARY REPOSITORY</h3>
        <el-alert
          type="info"
          :closable="false"
          style="margin-top: 20px;"
        >
          <template #title>
            <div style="font-weight: bold;">📚 项目资源</div>
          </template>
          <ul style="margin-top: 10px;">
            <li>GitHub: <el-link href="https://github.com/rainx/pytdx" target="_blank" type="primary">https://github.com/rainx/pytdx</el-link></li>
            <li>PyPI: <el-link href="https://pypi.org/project/pytdx/" target="_blank" type="primary">https://pypi.org/project/pytdx/</el-link></li>
            <li>Documentation: <el-link href="https://pytdx.readthedocs.io/" target="_blank" type="primary">https://pytdx.readthedocs.io/</el-link></li>
            <li>文档: 完整的 API 文档和使用示例</li>
            <li>社区: 活跃的 Issue 讨论和问题解答</li>
            <li>更新: 持续更新以支持最新的通达信协议</li>
          </ul>
        </el-alert>
      </div>
    </el-card>

    <!-- 2. 安装和配置 -->
</template>

<script setup lang="ts">
defineProps<{ activeTab: string }>()
</script>
