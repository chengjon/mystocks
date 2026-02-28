<template>
  <div class="stop-loss-monitoring-tab">

    <!-- 控制面板 -->
    <div class="control-panel">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-statistic
            title="ACTIVE POSITIONS"
            :value="stats.activePositions"
            suffix="positions"
            :value-style="{ color: '#409EFF' }"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="TOTAL P&L PROTECTED"
            :value="stats.totalPnLProtected"
            prefix="¥"
            :precision="0"
            :value-style="{ color: stats.totalPnLProtected >= 0 ? '#67C23A' : '#F56C6C' }"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="SUCCESS RATE"
            :value="stats.successRate"
            suffix="%"
            :value-style="{ color: stats.successRate >= 90 ? '#67C23A' : '#E6A23C' }"
          />
        </el-col>
        <el-col :span="6">
          <el-statistic
            title="AVG HOLDING TIME"
            :value="stats.avgHoldingTime"
            suffix="days"
            :precision="1"
            :value-style="{ color: '#409EFF' }"
          />
        </el-col>
      </el-row>
    </div>

    <!-- 持仓监控表格 -->
    <el-card title="POSITION MONITORING" class="positions-card" hoverable>
      <template #header>
        <div class="card-header">
          <span>POSITION MONITORING</span>
          <div class="header-actions">
            <el-button type="primary" size="small" @click="addPosition">
              ADD POSITION
            </el-button>
            <el-button type="info" size="small" @click="refreshData">
              REFRESH
            </el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="positions"
        style="width: 100%"
        :loading="loading"
        stripe
        max-height="400"
      >
        <el-table-column prop="symbol" label="SYMBOL" width="100" />
        <el-table-column prop="position_id" label="POSITION ID" width="120" />
        <el-table-column prop="entry_price" label="ENTRY PRICE" width="120">
          <template #default="scope">
            ¥{{ scope.row.entry_price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="current_price" label="CURRENT PRICE" width="120">
          <template #default="scope">
            <span :class="getPriceClass(scope.row)">
              ¥{{ scope.row.current_price.toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="stop_loss_price" label="STOP LOSS" width="120">
          <template #default="scope">
            ¥{{ scope.row.stop_loss_price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="quantity" label="QUANTITY" width="100" />
        <el-table-column prop="stop_loss_type" label="STRATEGY" width="140">
          <template #default="scope">
            <el-tag :type="getStrategyTagType(scope.row.stop_loss_type)">
              {{ formatStrategyName(scope.row.stop_loss_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="distance_to_stop" label="DISTANCE TO STOP" width="140">
          <template #default="scope">
            <span :class="getDistanceClass(scope.row.distance_to_stop)">
              {{ scope.row.distance_to_stop.toFixed(1) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="STATUS" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.is_active ? 'success' : 'info'">
              {{ scope.row.is_active ? 'ACTIVE' : 'INACTIVE' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="ACTIONS" width="150">
          <template #default="scope">
            <el-button
              type="warning"
              size="small"
              @click="editPosition(scope.row)"
              :disabled="!scope.row.is_active"
            >
              EDIT
            </el-button>
            <el-button
              type="danger"
              size="small"
              @click="removePosition(scope.row)"
              style="margin-left: 8px;"
            >
              REMOVE
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 止损执行历史 -->
    <el-card title="STOP LOSS EXECUTION HISTORY" class="history-card" hoverable>
      <template #header>
        <div class="card-header">
          <span>STOP LOSS EXECUTION HISTORY</span>
          <div class="header-actions">
            <el-select v-model="historyPeriod" size="small" @change="loadExecutionHistory">
              <el-option label="Last 24 Hours" value="24h" />
              <el-option label="Last 7 Days" value="7d" />
              <el-option label="Last 30 Days" value="30d" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table
        :data="executionHistory"
        style="width: 100%"
        :loading="historyLoading"
        stripe
        max-height="300"
      >
        <el-table-column prop="symbol" label="SYMBOL" width="100" />
        <el-table-column prop="position_id" label="POSITION ID" width="120" />
        <el-table-column prop="execution_time" label="EXECUTION TIME" width="160">
          <template #default="scope">
            {{ formatDateTime(scope.row.execution_time) }}
          </template>
        </el-table-column>
        <el-table-column prop="stop_loss_price" label="STOP PRICE" width="120">
          <template #default="scope">
            ¥{{ scope.row.stop_loss_price.toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="loss_amount" label="LOSS AMOUNT" width="120">
          <template #default="scope">
            <span class="loss-amount">
              ¥{{ Math.abs(scope.row.loss_amount).toFixed(2) }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="loss_percentage" label="LOSS %" width="100">
          <template #default="scope">
            <span class="loss-percentage">
              {{ Math.abs(scope.row.loss_percentage).toFixed(2) }}%
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="strategy_type" label="STRATEGY" width="140">
          <template #default="scope">
            <el-tag :type="getStrategyTagType(scope.row.strategy_type)">
              {{ formatStrategyName(scope.row.strategy_type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="trigger_reason" label="TRIGGER REASON" width="150">
          <template #default="scope">
            <el-tooltip :content="scope.row.trigger_reason" placement="top">
              <span>{{ truncateText(scope.row.trigger_reason, 20) }}</span>
            </el-tooltip>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑持仓对话框 -->
    <el-dialog
      v-model="positionDialogVisible"
      :title="isEditing ? 'EDIT POSITION' : 'ADD POSITION'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="positionFormRef"
        :model="positionForm"
        :rules="positionFormRules"
        label-width="120px"
      >
        <el-form-item label="Symbol" prop="symbol">
          <el-input v-model="positionForm.symbol" placeholder="e.g., 600519" />
        </el-form-item>

        <el-form-item label="Position ID" prop="position_id">
          <el-input v-model="positionForm.position_id" placeholder="Unique position identifier" />
        </el-form-item>

        <el-form-item label="Entry Price" prop="entry_price">
          <el-input-number
            v-model="positionForm.entry_price"
            :precision="2"
            :min="0"
            style="width: 100%;"
          />
        </el-form-item>

        <el-form-item label="Quantity" prop="quantity">
          <el-input-number
            v-model="positionForm.quantity"
            :min="1"
            style="width: 100%;"
          />
        </el-form-item>

        <el-form-item label="Stop Loss Type" prop="stop_loss_type">
          <el-select v-model="positionForm.stop_loss_type" style="width: 100%;">
            <el-option label="Volatility Adaptive" value="volatility_adaptive" />
            <el-option label="Trailing Stop" value="trailing_stop" />
          </el-select>
        </el-form-item>

        <el-form-item
          v-if="positionForm.stop_loss_type === 'volatility_adaptive'"
          label="K Factor"
          prop="k_factor"
        >
          <el-slider
            v-model="positionForm.k_factor"
            :min="0.5"
            :max="4.0"
            :step="0.1"
            show-input
            style="width: 100%;"
          />
          <div class="slider-hint">
            Conservative (2.5) ← → Aggressive (1.5)
          </div>
        </el-form-item>

        <el-form-item
          v-if="positionForm.stop_loss_type === 'trailing_stop'"
          label="Trailing %"
          prop="trailing_percentage"
        >
          <el-slider
            v-model="positionForm.trailing_percentage"
            :min="0.02"
            :max="0.15"
            :step="0.01"
            show-input
            style="width: 100%;"
          />
          <div class="slider-hint">
            Tight (2%) ← → Loose (15%)
          </div>
        </el-form-item>

        <el-form-item label="Custom Stop Price" prop="custom_stop_price">
          <el-input-number
            v-model="positionForm.custom_stop_price"
            :precision="2"
            :min="0"
            placeholder="Optional: override calculated stop price"
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="positionDialogVisible = false">CANCEL</el-button>
        <el-button type="primary" @click="savePosition" :loading="saving">
          {{ isEditing ? 'UPDATE' : 'ADD' }} POSITION
        </el-button>
      </template>
    </el-dialog>

  </div>
</template>

<script setup>
import { useStopLossMonitoringTab } from './composables/useStopLossMonitoringTab'

const { loading, historyLoading, saving, positionDialogVisible, isEditing, historyPeriod, stats, positions, executionHistory, positionForm, positionFormRules, loadData, loadExecutionHistory, addPosition, editPosition, removePosition, savePosition, resetPositionForm, refreshData, getPriceClass, change, getStrategyTagType, formatStrategyName, getDistanceClass, formatDateTime, truncateText, handleStopLossUpdate } = useStopLossMonitoringTab()
</script>

<style scoped>
@import "./styles/StopLossMonitoringTab.css";
</style>