<template>
  <div class="market">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span>市场行情</span>
          <el-button type="primary" size="small">刷新</el-button>
        </div>
      </template>
      <el-empty description="功能开发中..." />
    </el-card>
  </div>
</template>

<script setup>
</script>

<style scoped lang="scss">
.market {
  .flex-between {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
}
</style>
