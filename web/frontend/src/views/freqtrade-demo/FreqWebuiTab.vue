<template>
    <el-card v-show="activeTab === 'webui'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>🖥️ Web UI 管理界面</span>
          <el-tag type="info">计划集成</el-tag>
        </div>
      </template>

      <div class="content-section">
        <h3>🎨 FreqUI 功能</h3>
        <p>FreqUI 是 Freqtrade 的官方 Web 管理界面,提供直观的可视化管理功能:</p>

        <el-row :gutter="20" style="margin-top: 20px;">
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>📊 实时监控</h4>
              <ul>
                <li>实时查看持仓和订单</li>
                <li>查看策略运行状态</li>
                <li>监控账户余额变化</li>
                <li>查看交易历史记录</li>
                <li>实时日志输出</li>
              </ul>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>🎛️ 交易控制</h4>
              <ul>
                <li>启动/停止交易机器人</li>
                <li>强制买入/卖出</li>
                <li>修改配置参数</li>
                <li>紧急停止所有交易</li>
                <li>切换策略</li>
              </ul>
            </el-card>
          </el-col>
        </el-row>

        <h3 style="margin-top: 30px;">🚀 启动 Web UI</h3>
        <pre v-pre class="code-block"># 启动 Freqtrade 并开启 API
freqtrade trade --config config.json --strategy SampleStrategy

# 在另一个终端启动 FreqUI (需要单独安装)
# 或者访问: http://localhost:8080 (如果配置了 api_server)</pre>

        <el-alert
          type="info"
          title="💡 Web UI 访问"
          :closable="false"
          style="margin-top: 20px;"
        >
          <p style="margin-top: 10px;">默认访问地址: <code>http://127.0.0.1:8080</code></p>
          <p>默认账号: 在 config.json 的 api_server 部分配置</p>
          <p style="margin-top: 10px;">
            <el-link href="https://github.com/freqtrade/frequi" target="_blank" type="primary">
              FreqUI GitHub 仓库
            </el-link>
          </p>
        </el-alert>

        <h3 style="margin-top: 30px;">🔌 REST API 端点</h3>
        <el-table :data="apiEndpoints" stripe style="margin-top: 15px;">
          <el-table-column prop="method" label="方法" width="100" />
          <el-table-column prop="endpoint" label="端点" width="250" />
          <el-table-column prop="description" label="说明" />
        </el-table>
      </div>
    </el-card>

    <!-- 6. 集成状态 -->
</template>

<script setup lang="ts">
defineProps<{ 
  activeTab: string;
  apiEndpoints: Array<{ method: string; endpoint: string; description: string }>;
}>()
</script>
