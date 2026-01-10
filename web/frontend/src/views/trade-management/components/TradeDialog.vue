<template>
  <el-dialog
    v-model="dialogVisible"
    :title="form.type === 'buy' ? 'BUY STOCK' : 'SELL STOCK'"
    width="600px"
    :close-on-click-modal="false"
    class="bloomberg-trade-dialog"
  >
    <el-form :model="form" label-width="120px" label-position="left">
      <el-form-item label="SYMBOL">
        <el-input
          v-model="form.symbol"
          placeholder="E.G: 600519"
          clearable
        />
      </el-form-item>

      <el-form-item label="STOCK NAME">
        <el-input
          v-model="form.stock_name"
          placeholder="AUTO LOADED"
          readonly
        />
      </el-form-item>

      <el-form-item label="QUANTITY">
        <el-input-number
          v-model="form.quantity"
          :min="100"
          :step="100"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="PRICE">
        <el-input-number
          v-model.number="form.price"
          :min="0"
          :step="0.01"
          :precision="2"
          placeholder="MARKET PRICE"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="TRADE AMOUNT">
        <div class="trade-amount-display">
          ¥{{ (form.quantity * form.price).toFixed(2) }}
        </div>
      </el-form-item>

      <el-form-item label="REMARK">
        <el-input
          v-model="form.remark"
          type="textarea"
          :rows="3"
          placeholder="OPTIONAL"
        />
      </el-form-item>
    </el-form>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" :disabled="submitting">
          CANCEL
        </el-button>
        <el-button
          :type="form.type === 'buy' ? 'primary' : 'danger'"
          @click="handleSubmit"
          :loading="submitting"
        >
          {{ form.type === 'buy' ? 'BUY' : 'SELL' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { reactive, ref, watch, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { tradeApi } from '@/api/trade'

interface TradeForm {
  type: 'buy' | 'sell'
  symbol: string
  stock_name: string
  quantity: number
  price: number
  remark: string
}

interface Props {
  visible: boolean
  tradeType?: 'buy' | 'sell'
}

const props = withDefaults(defineProps<Props>(), {
  visible: false,
  tradeType: 'buy'
})

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'submitted': []
}>()

const submitting = ref(false)

const form = reactive<TradeForm>({
  type: props.tradeType,
  symbol: '',
  stock_name: '',
  quantity: 100,
  price: 0,
  remark: ''
})

const dialogVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val)
})

watch(() => props.visible, (newVal) => {
  if (newVal) {
    resetForm()
  }
})

watch(() => props.tradeType, (newVal) => {
  form.type = newVal
})

const resetForm = () => {
  form.type = props.tradeType
  form.symbol = ''
  form.stock_name = ''
  form.quantity = 100
  form.price = 0
  form.remark = ''
}

const handleClose = () => {
  emit('update:visible', false)
}

const handleSubmit = async () => {
  if (!form.symbol) {
    ElMessage.warning('PLEASE ENTER SYMBOL')
    return
  }
  if (!form.quantity || form.quantity <= 0) {
    ElMessage.warning('PLEASE ENTER VALID QUANTITY')
    return
  }
  if (!form.price || form.price <= 0) {
    ElMessage.warning('PLEASE ENTER VALID PRICE')
    return
  }

  submitting.value = true
  try {
    const orderData = {
      symbol: form.symbol,
      side: form.type,
      quantity: form.quantity,
      price: form.price,
      order_type: 'limit' as const,
      time_in_force: 'gtc' as const,
      remark: form.remark
    }

    await tradeApi.createOrder(orderData)
    ElMessage.success(`${form.type === 'buy' ? 'BUY' : 'SELL'} ORDER SUBMITTED`)
    emit('update:visible', false)
    emit('submitted')
  } catch (error: any) {
    console.error('交易失败:', error)
    ElMessage.error('TRADE FAILED: ' + (error.message || 'UNKNOWN ERROR'))
  } finally {
    submitting.value = false
  }
}

defineExpose({
  resetForm
})
</script>

<style scoped lang="scss">
// ============================================
//   Bloomberg Terminal Style Trade Dialog
// ============================================

.bloomberg-trade-dialog {
  :deep(.el-dialog) {
    background: linear-gradient(135deg, #0F1115 0%, #141A24 100%);
    border: 1px solid #1E293B;
    border-radius: 8px;
    box-shadow:
      0 4px 20px rgba(0, 0, 0, 0.6),
      0 0 40px rgba(0, 128, 255, 0.1);
  }

  :deep(.el-dialog__header) {
    background: transparent;
    border-bottom: 1px solid #1E293B;
    padding: 20px 24px;

    .el-dialog__title {
      font-family: 'IBM Plex Sans', sans-serif;
      font-size: 18px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: #0080FF;
    }
  }

  :deep(.el-dialog__body) {
    padding: 24px;
  }

  :deep(.el-dialog__footer) {
    border-top: 1px solid #1E293B;
    padding: 16px 24px;
  }

  :deep(.el-form) {
    .el-form-item {
      margin-bottom: 20px;

      .el-form-item__label {
        font-family: 'IBM Plex Sans', sans-serif;
        font-size: 12px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #94A3B8;
      }
    }
  }

  :deep(.el-input) {
    .el-input__wrapper {
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid #1E293B;
      border-radius: 4px;
      box-shadow: none;
      transition: all 0.3s ease;

      &:hover {
        border-color: #0080FF;
      }

      &.is-focus {
        border-color: #0080FF;
        box-shadow: 0 0 0 2px rgba(0, 128, 255, 0.1);
      }

      .el-input__inner {
        color: #FFFFFF;
        font-family: 'Roboto Mono', monospace;
        font-size: 14px;

        &::placeholder {
          color: #64748B;
          text-transform: uppercase;
          letter-spacing: 0.05em;
        }
      }

      &.is-disabled {
        background: rgba(0, 0, 0, 0.5);
        border-color: #1E293B;

        .el-input__inner {
          color: #64748B;
        }
      }
    }
  }

  :deep(.el-input-number) {
    width: 100%;

    .el-input__wrapper {
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid #1E293B;
      border-radius: 4px;
      box-shadow: none;
      transition: all 0.3s ease;

      &:hover {
        border-color: #0080FF;
      }

      &.is-focus {
        border-color: #0080FF;
        box-shadow: 0 0 0 2px rgba(0, 128, 255, 0.1);
      }

      .el-input__inner {
        color: #FFFFFF;
        font-family: 'Roboto Mono', monospace;
        font-size: 14px;
        text-align: left;
      }
    }

    .el-input-number__decrease,
    .el-input-number__increase {
      background: transparent;
      border-left: 1px solid #1E293B;
      color: #94A3B8;

      &:hover {
        color: #0080FF;
      }
    }
  }

  :deep(.el-textarea) {
    .el-textarea__inner {
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid #1E293B;
      border-radius: 4px;
      color: #FFFFFF;
      font-family: 'Roboto Mono', monospace;
      font-size: 14px;
      resize: none;
      transition: all 0.3s ease;

      &:hover {
        border-color: #0080FF;
      }

      &:focus {
        border-color: #0080FF;
        box-shadow: 0 0 0 2px rgba(0, 128, 255, 0.1);
      }

      &::placeholder {
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }
    }
  }
}

// Trade Amount Display
.trade-amount-display {
  display: block;
  font-family: 'Roboto Mono', monospace;
  font-size: 24px;
  font-weight: 700;
  color: #0080FF;
  padding: 12px 16px;
  background: rgba(0, 128, 255, 0.05);
  border: 1px solid rgba(0, 128, 255, 0.2);
  border-radius: 4px;
  text-align: center;
}

// Dialog Footer
.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;

  :deep(.el-button) {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    border-radius: 4px;
    padding: 10px 24px;
  }
}
</style>
