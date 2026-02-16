<template>
  <div class="freq-status-tab">
    <el-card v-show="activeTab === 'status'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>✅ 集成状态</span>
        </div>
      </template>

      <div class="content-section">
        <h3>📦 已集成功能</h3>
        <el-descriptions :column="1" border style="margin-top: 15px;">
          <el-descriptions-item label="项目文档">
            <el-tag type="success">✅ 已整理</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="策略示例">
            <el-tag type="success">✅ 已收集</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="配置模板">
            <el-tag type="success">✅ 已文档化</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="后端 API">
            <el-tag type="info">⏳ 待开发</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="数据接口">
            <el-tag type="info">⏳ 待开发</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Web UI 集成">
            <el-tag type="info">⏳ 计划中</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 30px;">🎯 后续集成计划</h3>
        <el-timeline style="margin-top: 20px;">
          <el-timeline-item timestamp="Phase 1" placement="top">
            <el-card>
              <h4>数据接口集成</h4>
              <p>整合 Freqtrade 的数据下载和存储功能到 MyStocks 数据管理系统</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="Phase 2" placement="top">
            <el-card>
              <h4>策略管理</h4>
              <p>在 Web 界面中实现策略的创建、编辑和管理功能</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="Phase 3" placement="top">
            <el-card>
              <h4>回测系统</h4>
              <p>集成 Freqtrade 回测引擎,在 Web 界面中运行回测并查看结果</p>
            </el-card>
          </el-timeline-item>
          <el-timeline-item timestamp="Phase 4" placement="top">
            <el-card>
              <h4>实盘交易</h4>
              <p>支持在 Web 界面中启动和监控实盘交易机器人</p>
            </el-card>
          </el-timeline-item>
        </el-timeline>

        <el-alert
          type="warning"
          title="⚠️ 重要提醒"
          :closable="false"
          style="margin-top: 20px;"
        >
          <ul style="margin-top: 10px;">
            <li><strong>风险警示</strong>: 加密货币交易存在高风险,请务必充分了解风险后再使用</li>
            <li><strong>模拟交易</strong>: 建议先在模拟模式下充分测试策略</li>
            <li><strong>资金管理</strong>: 只投入您能承受损失的资金</li>
            <li><strong>持续监控</strong>: 实盘交易时需要持续监控机器人运行状态</li>
            <li><strong>法律合规</strong>: 确保您所在地区允许加密货币交易</li>
          </ul>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
defineProps<{ activeTab: string }>()
</script>
