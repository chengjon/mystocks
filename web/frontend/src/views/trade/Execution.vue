<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArtDecoButton, ArtDecoCard, ArtDecoIcon, ArtDecoStatCard } from '@/components/artdeco'
import ArtDecoRouteHeader from '@/components/artdeco/route-shell/ArtDecoRouteHeader.vue'
import { tradeApi } from '@/api/trade'
import type { ExecutionTrackingDetailPayload, ExecutionTrackingItem } from '@/api/tradeExecutionTracking.ts'

const router = useRouter()

const accountId = ref('backtest:7')
const orderId = ref('')
const bridgeTaskId = ref('')
const symbol = ref('600519.SH')
const direction = ref<'buy' | 'sell'>('buy')
const quantity = ref(100)
const price = ref(1750)
const loading = ref(false)
const triggering = ref(false)
const detailLoading = ref(false)
const errorMessage = ref('')
const actionMessage = ref('')
const latestBridgeTaskId = ref('')
const rows = ref<ExecutionTrackingItem[]>([])
const selectedDetail = ref<ExecutionTrackingDetailPayload | null>(null)
const summary = ref({
  totalCount: 0,
  bridgeAcceptedCount: 0,
  brokerAcknowledgedCount: 0,
  reviewRequiredCount: 0,
  reconciledCount: 0,
})

const pageStatusText = computed(() => {
  if (triggering.value) {
    return '触发中'
  }
  if (loading.value) {
    return '同步中'
  }
  if (errorMessage.value) {
    return '观测异常'
  }
  if (summary.value.reviewRequiredCount > 0) {
    return '存在复核项'
  }
  return '观测就绪'
})

const runtimeMessage = computed(() => {
  if (errorMessage.value) {
    return errorMessage.value
  }
  if (actionMessage.value) {
    return actionMessage.value
  }
  if (rows.value.length === 0 && !loading.value) {
    return '暂无执行跟踪记录，可先提交外部触发请求。'
  }
  return ''
})

const brokerStateText = (state: string) => {
  if (state === 'broker_acknowledged') {
    return '已关联券商身份'
  }
  return '需复核'
}

const submissionStatusText = (status: string) => {
  if (status === 'bridge_task_accepted') {
    return 'bridge 已接收'
  }
  if (status === 'broker_acknowledged') {
    return '券商身份已关联'
  }
  return '提交失败'
}

const loadTracking = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const payload = await tradeApi.getExecutionTracking({
      accountId: accountId.value || undefined,
      orderId: orderId.value || undefined,
      bridgeTaskId: bridgeTaskId.value || undefined,
      page: 1,
      pageSize: 20,
    })
    rows.value = payload.items
    summary.value = payload.summary
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '执行跟踪加载失败'
    rows.value = []
    summary.value = {
      totalCount: 0,
      bridgeAcceptedCount: 0,
      brokerAcknowledgedCount: 0,
      reviewRequiredCount: 0,
      reconciledCount: 0,
    }
  } finally {
    loading.value = false
  }
}

const triggerExternalExecution = async () => {
  triggering.value = true
  errorMessage.value = ''
  actionMessage.value = ''
  latestBridgeTaskId.value = ''

  try {
    const payload = await tradeApi.triggerExternalExecution({
      accountId: accountId.value,
      channel: 'miniqmt',
      symbol: symbol.value.trim(),
      direction: direction.value,
      quantity: Number(quantity.value),
      price: Number(price.value),
      requestedBy: 'mystocks-ui',
    })
    latestBridgeTaskId.value = payload.bridgeReceipt.bridgeTaskId || ''
    actionMessage.value = `外部触发已记录，bridge task: ${latestBridgeTaskId.value || payload.trackingId}`
    await loadTracking()
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '外部触发失败'
  } finally {
    triggering.value = false
  }
}

const openDetail = async (trackingId: string) => {
  detailLoading.value = true
  errorMessage.value = ''

  try {
    selectedDetail.value = await tradeApi.getExecutionTrackingDetail(trackingId)
  } catch (error) {
    errorMessage.value = error instanceof Error ? error.message : '证据详情加载失败'
  } finally {
    detailLoading.value = false
  }
}

const closeDetail = () => {
  selectedDetail.value = null
}

const jumpToReconciliation = async (item: ExecutionTrackingItem) => {
  await router.push({
    path: '/trade/reconciliation',
    query: {
      account_id: item.accountId,
      order_id: item.orderId,
      bridge_task_id: item.bridgeEvidence.bridgeTaskId || '',
    },
  })
}

onMounted(() => {
  void loadTracking()
})
</script>

<template>
  <div class="trade-execution page-enter" data-testid="trade-execution-page">
    <ArtDecoRouteHeader
      title="执行跟踪 / 外部触发观测台"
      subtitle="实际交易由 miniQMT、TdxQuant 或其他外部程序完成；本系统只记录触发、回执、证据和对账线索"
      eyebrow="external trigger observation"
      :show-status="true"
      :status-text="pageStatusText"
      :status-type="errorMessage ? 'warning' : 'info'"
      test-id="trade-execution-header"
      shell-class="execution-hero artdeco-card-shell"
    >
      <template #actions>
        <ArtDecoButton
          variant="outline"
          size="sm"
          :loading="loading"
          data-testid="trade-execution-refresh"
          @click="loadTracking"
        >
          <template #icon>
            <ArtDecoIcon name="refresh" />
          </template>
          刷新
        </ArtDecoButton>
      </template>
    </ArtDecoRouteHeader>

    <section class="stats-strip artdeco-card-shell" data-testid="trade-execution-stats-strip">
      <ArtDecoStatCard label="跟踪链路" :value="summary.totalCount" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="Bridge 接收" :value="summary.bridgeAcceptedCount" :show-change="false" variant="gold" />
      <ArtDecoStatCard label="券商身份" :value="summary.brokerAcknowledgedCount" :show-change="false" variant="rise" />
      <ArtDecoStatCard label="需复核" :value="summary.reviewRequiredCount" :show-change="false" variant="fall" />
    </section>

    <section class="control-shell artdeco-card-shell" data-testid="trade-execution-filter-row">
      <div class="filter-grid">
        <label class="field">
          <span>账户</span>
          <input v-model="accountId" type="text" />
        </label>
        <label class="field">
          <span>订单 ID</span>
          <input v-model="orderId" type="text" placeholder="可选" />
        </label>
        <label class="field">
          <span>Bridge Task</span>
          <input v-model="bridgeTaskId" type="text" placeholder="可选" />
        </label>
        <div class="field field--actions">
          <span>筛选</span>
          <ArtDecoButton variant="outline" size="sm" :loading="loading" @click="loadTracking">查询</ArtDecoButton>
        </div>
      </div>
    </section>

    <section class="trigger-shell artdeco-card-shell" data-testid="trade-execution-trigger-row">
      <div class="filter-grid">
        <label class="field">
          <span>证券代码</span>
          <input data-testid="execution-symbol-input" v-model="symbol" type="text" />
        </label>
        <label class="field">
          <span>方向</span>
          <select v-model="direction">
            <option value="buy">买入</option>
            <option value="sell">卖出</option>
          </select>
        </label>
        <label class="field">
          <span>数量</span>
          <input data-testid="execution-quantity-input" v-model.number="quantity" type="number" min="1" />
        </label>
        <label class="field">
          <span>价格</span>
          <input data-testid="execution-price-input" v-model.number="price" type="number" min="0.01" step="0.01" />
        </label>
        <div class="field field--actions">
          <span>miniQMT</span>
          <ArtDecoButton
            data-testid="execution-trigger-button"
            variant="solid"
            size="sm"
            :loading="triggering"
            @click="triggerExternalExecution"
          >
            提交外部触发
          </ArtDecoButton>
        </div>
      </div>
    </section>

    <p v-if="runtimeMessage" class="runtime-message" aria-live="polite" data-testid="trade-execution-runtime-state">
      {{ runtimeMessage }}
    </p>

    <ArtDecoCard title="执行链路" data-testid="trade-execution-work-area">
      <div v-if="rows.length === 0" class="table-empty">暂无执行跟踪链路。</div>
      <div v-else class="table-shell">
        <table class="execution-table">
          <thead>
            <tr>
              <th>证券</th>
              <th>方向</th>
              <th>数量</th>
              <th>价格</th>
              <th>Bridge Task</th>
              <th>提交状态</th>
              <th>Broker</th>
              <th>对账</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.trackingId">
              <td>{{ row.symbol }}</td>
              <td>{{ row.direction === 'buy' ? '买入' : '卖出' }}</td>
              <td>{{ row.quantity }}</td>
              <td>{{ row.price.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</td>
              <td>{{ row.bridgeEvidence.bridgeTaskId || 'N/A' }}</td>
              <td>{{ submissionStatusText(row.submissionStatus) }}</td>
              <td>
                <span class="status-chip" :class="`status-chip--${row.brokerState}`">
                  {{ brokerStateText(row.brokerState) }}
                </span>
              </td>
              <td>{{ row.reconciliationStatus }}</td>
              <td class="row-actions">
                <button
                  type="button"
                  :data-testid="`execution-detail-${row.trackingId}`"
                  @click="openDetail(row.trackingId)"
                >
                  证据
                </button>
                <button
                  type="button"
                  :data-testid="`execution-reconcile-${row.trackingId}`"
                  @click="jumpToReconciliation(row)"
                >
                  对账
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </ArtDecoCard>

    <aside v-if="selectedDetail" class="evidence-drawer" aria-label="执行证据详情" data-testid="trade-execution-evidence-drawer">
      <div class="drawer-head">
        <div>
          <span class="hero-eyebrow">evidence timeline</span>
          <h2>证据时间线</h2>
        </div>
        <button type="button" @click="closeDetail">关闭</button>
      </div>
      <p class="drawer-context">
        {{ selectedDetail.item.symbol }} / {{ selectedDetail.item.orderId }} / {{ selectedDetail.item.bridgeEvidence.bridgeTaskId || 'N/A' }}
      </p>
      <ol class="timeline">
        <li v-for="event in selectedDetail.evidenceTimeline" :key="`${event.eventType}-${event.occurredAt}`">
          <strong>{{ event.eventType }}</strong>
          <span>{{ event.occurredAt }}</span>
          <p>{{ event.summary }}</p>
        </li>
      </ol>
      <p v-if="detailLoading" class="runtime-message">正在加载证据...</p>
    </aside>
  </div>
</template>

<style scoped src="./Execution.css"></style>
