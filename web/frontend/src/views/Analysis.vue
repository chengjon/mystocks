<template>
  <div class="analysis">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span>数据分析</span>
          <el-button type="primary" size="small">新建分析</el-button>
        </div>
      </template>
      <el-empty description="功能开发中,即将支持:
      - 技术指标分析 (MA, MACD, KDJ, RSI等)
      - 量价关系分析
      - 相关性分析
      - 回测分析" />
    </el-card>
  </div>
</template>

<script setup>
</script>

<style scoped lang="scss">
.analysis {
  .flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}
</style>
