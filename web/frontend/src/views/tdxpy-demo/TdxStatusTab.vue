<template>
  <div class="tdx-status-tab">
    <el-card v-show="activeTab === 'status'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>✅ 集成状态</span>
        </div>
      </template>

      <div class="content-section">
        <h3>📦 已集成功能</h3>
        <el-descriptions :column="1" border class="status-descriptions">
          <el-descriptions-item label="pytdx 库">
            <el-tag type="success">✅ 已安装</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="API 文档">
            <el-tag type="success">✅ 已整理</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="使用示例">
            <el-tag type="success">✅ 已收集</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="后端接口">
            <el-tag type="info">⏳ 待开发</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="实时数据服务">
            <el-tag type="info">⏳ 计划中</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="数据缓存">
            <el-tag type="info">⏳ 计划中</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <h3 class="status-section-heading">🎯 后续集成计划</h3>
        <el-timeline class="status-timeline">
          <el-timeline-item timestamp="Phase 1" placement="top">
            <el-card>
              <h4>后端 API 开发</h4>
              <p>封装 pytdx 功能为 RESTful API,提供标准化数据接口</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="Phase 2" placement="top">
            <el-card>
              <h4>实时数据服务</h4>
              <p>建立 WebSocket 推送服务,实现实时行情推送</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="Phase 3" placement="top">
            <el-card>
              <h4>数据缓存层</h4>
              <p>实现 Redis 缓存,提高数据访问速度</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="Phase 4" placement="top">
            <el-card>
              <h4>数据可视化</h4>
              <p>在 Web 界面中展示实时行情和K线图表</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>

        <h3 class="status-section-heading">💡 应用场景</h3>
        <el-row :gutter="20" class="status-row">
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>🎯 实时行情监控</h4>
              <p>使用 pytdx 获取实时行情数据,结合策略进行监控和告警。适用于短线交易和日内策略。</p>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>📊 历史数据回测</h4>
              <p>获取完整的历史K线数据,用于策略回测和参数优化。支持多周期数据分析。</p>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="20" class="status-row">
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>💾 数据采集系统</h4>
              <p>定时采集和更新股票数据,建立本地数据库。支持全市场数据采集和增量更新。</p>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="hover">
              <h4>🔍 量化分析</h4>
              <p>结合技术指标和因子分析,构建量化选股系统。支持多因子模型和机器学习。</p>
            </el-card>
          </el-col>
        </el-row>

        <el-alert
          type="warning"
          title="⚠️ 使用注意事项"
          :closable="false"
          class="status-alert"
        >
          <ul class="status-alert-list">
            <li><strong>频率限制</strong>: 避免过于频繁请求,建议间隔至少1秒</li>
            <li><strong>数据延迟</strong>: 通达信免费数据有3-5秒延迟</li>
            <li><strong>服务器稳定性</strong>: 服务器可能不稳定,需要实现重连机制</li>
            <li><strong>数据准确性</strong>: 建议与官方数据源进行对比验证</li>
            <li><strong>合规使用</strong>: 仅供个人学习研究使用,商业用途需咨询通达信</li>
          </ul>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
defineProps<{ activeTab: string }>()
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.status-descriptions {
  margin-top: calc(var(--artdeco-spacing-5) - var(--artdeco-spacing-px) * 5);
}

.status-section-heading {
  margin-top: calc(var(--artdeco-spacing-6) + var(--artdeco-spacing-3) / 2);
}

.status-timeline,
.status-row,
.status-alert {
  margin-top: var(--artdeco-spacing-5);
}

.status-alert-list {
  margin-top: calc(var(--artdeco-spacing-2) + var(--artdeco-spacing-px) * 2);
}
</style>
