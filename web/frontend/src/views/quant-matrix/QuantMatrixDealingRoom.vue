<template>
  <div class="qm-dashboard">
    <div class="qm-dashboard__kpi-grid">
      <QuantMatrixKpiCard label="总资产" value="¥1,025,000" delta="+1.84%" trend="up" />
      <QuantMatrixKpiCard label="实时风险" value="LOW" delta="稳定" trend="neutral" />
      <QuantMatrixKpiCard label="可用现金" value="¥152,300" delta="-0.62%" trend="down" />
      <QuantMatrixKpiCard label="活跃策略" value="12" delta="+2" trend="up" />
    </div>

    <QuantMatrixShellCard title="执行健康状态">
      <table class="qm-dashboard__table">
        <thead>
          <tr>
            <th>模块</th>
            <th>状态</th>
            <th>说明</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>交易执行链路</td>
            <td class="is-ok">在线</td>
            <td>订单提交与回报正常</td>
          </tr>
          <tr>
            <td>行情采集链路</td>
            <td class="is-ok">在线</td>
            <td>延迟维持在可控范围</td>
          </tr>
          <tr>
            <td>风控评估链路</td>
            <td class="is-warn">关注</td>
            <td>建议观察异常告警波动</td>
          </tr>
        </tbody>
      </table>
      <p class="qm-dashboard__trace">TRACE: QM-DEALING-ROOM-RECOVERY</p>
    </QuantMatrixShellCard>
  </div>
</template>

<script setup lang="ts">
import QuantMatrixKpiCard from '@/components/quant-matrix/base/QuantMatrixKpiCard.vue'
import QuantMatrixShellCard from '@/components/quant-matrix/base/QuantMatrixShellCard.vue'
</script>

<style scoped lang="scss">
@import '@/styles/quant-matrix/views/quant-matrix-dealing-room.scss';
</style>
