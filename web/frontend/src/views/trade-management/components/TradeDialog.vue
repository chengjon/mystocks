<template>
  <el-dialog
    v-model="dialogVisible"
    :title="form.type === 'buy' ? 'BUY STOCK' : 'SELL STOCK'"
    :width="dialogWidth"
    :close-on-click-modal="false"
    class="bloomberg-trade-dialog"
  >
    <el-form :model="form" :label-width="labelWidth" label-position="left">
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
        />
      </el-form-item>

      <el-form-item label="PRICE">
        <el-input-number
          v-model.number="form.price"
          :min="0"
          :step="0.01"
          :precision="2"
          placeholder="MARKET PRICE"
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
const dialogWidth = 'calc((var(--artdeco-spacing-20) * 7) + var(--artdeco-spacing-10))'
const labelWidth = 'calc(var(--artdeco-spacing-20) + var(--artdeco-spacing-10))'

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
  } catch (error: unknown) {
    console.error('交易失败:', error)
    ElMessage.error('TRADE FAILED: ' + ((error as Error).message || 'UNKNOWN ERROR'))
  } finally {
    submitting.value = false
  }
}

defineExpose({
  resetForm
})
</script>

<style scoped lang="scss">
@use '@/styles/artdeco-tokens.scss' as *;

.bloomberg-trade-dialog {
  :deep(.el-dialog) {
    background: linear-gradient(
      135deg,
      var(--artdeco-bg-global) 0%,
      var(--artdeco-bg-card) 100%
    );
    border: 1px solid var(--artdeco-border-default);
    border-radius: var(--artdeco-radius-none);
    box-shadow: var(--artdeco-shadow-xl), var(--artdeco-glow-subtle);
  }

  :deep(.el-dialog__header) {
    background: transparent;
    border-bottom: 1px solid var(--artdeco-border-default);
    padding: var(--artdeco-spacing-5) var(--artdeco-spacing-6);

    .el-dialog__title {
      font-family: var(--artdeco-font-heading, var(--font-display));
      font-size: var(--artdeco-text-lg);
      font-weight: var(--artdeco-font-semibold);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-widest);
      color: var(--artdeco-gold-primary);
    }
  }

  :deep(.el-dialog__body) {
    padding: var(--artdeco-spacing-6);
  }

  :deep(.el-dialog__footer) {
    border-top: 1px solid var(--artdeco-border-default);
    padding: var(--artdeco-spacing-4) var(--artdeco-spacing-6);
  }

  :deep(.el-form) {
    .el-form-item {
      margin-bottom: var(--artdeco-spacing-5);

      .el-form-item__label {
        font-family: var(--artdeco-font-heading, var(--font-display));
        font-size: var(--artdeco-text-xs);
        font-weight: var(--artdeco-font-medium);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wider);
        color: var(--artdeco-fg-muted);
      }
    }
  }

  :deep(.el-input) {
    .el-input__wrapper {
      background: color-mix(in srgb, var(--artdeco-bg-elevated) 55%, var(--artdeco-bg-card));
      border: 1px solid var(--artdeco-border-default);
      border-radius: var(--artdeco-radius-none);
      box-shadow: none;
      transition:
        border-color var(--artdeco-transition-quick) var(--artdeco-ease-out),
        box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out),
        background var(--artdeco-transition-quick) var(--artdeco-ease-out);

      &:hover {
        border-color: var(--artdeco-border-hover);
      }

      &.is-focus {
        border-color: var(--artdeco-border-hover);
        box-shadow: var(--artdeco-glow-subtle);
      }

      .el-input__inner {
        color: var(--artdeco-fg-primary);
        font-family: var(--artdeco-font-accent, var(--font-mono));
        font-size: var(--artdeco-text-compact-base);

        &::placeholder {
          color: var(--artdeco-fg-subtle);
          text-transform: uppercase;
          letter-spacing: var(--artdeco-tracking-wide);
        }
      }

      &.is-disabled {
        background: color-mix(in srgb, var(--artdeco-bg-global) 75%, var(--artdeco-bg-card));
        border-color: var(--artdeco-border-default);

        .el-input__inner {
          color: var(--artdeco-fg-muted);
        }
      }
    }
  }

  :deep(.el-input-number) {
    width: 100%;

    .el-input__wrapper {
      background: color-mix(in srgb, var(--artdeco-bg-elevated) 55%, var(--artdeco-bg-card));
      border: 1px solid var(--artdeco-border-default);
      border-radius: var(--artdeco-radius-none);
      box-shadow: none;
      transition:
        border-color var(--artdeco-transition-quick) var(--artdeco-ease-out),
        box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out),
        background var(--artdeco-transition-quick) var(--artdeco-ease-out);

      &:hover {
        border-color: var(--artdeco-border-hover);
      }

      &.is-focus {
        border-color: var(--artdeco-border-hover);
        box-shadow: var(--artdeco-glow-subtle);
      }

      .el-input__inner {
        color: var(--artdeco-fg-primary);
        font-family: var(--artdeco-font-accent, var(--font-mono));
        font-size: var(--artdeco-text-compact-base);
        text-align: left;
      }
    }

    .el-input-number__decrease,
    .el-input-number__increase {
      background: transparent;
      border-left: 1px solid var(--artdeco-border-default);
      color: var(--artdeco-fg-muted);

      &:hover {
        color: var(--artdeco-gold-primary);
      }
    }
  }

  :deep(.el-textarea) {
    .el-textarea__inner {
      background: color-mix(in srgb, var(--artdeco-bg-elevated) 55%, var(--artdeco-bg-card));
      border: 1px solid var(--artdeco-border-default);
      border-radius: var(--artdeco-radius-none);
      color: var(--artdeco-fg-primary);
      font-family: var(--artdeco-font-accent, var(--font-mono));
      font-size: var(--artdeco-text-compact-base);
      resize: none;
      transition:
        border-color var(--artdeco-transition-quick) var(--artdeco-ease-out),
        box-shadow var(--artdeco-transition-quick) var(--artdeco-ease-out),
        background var(--artdeco-transition-quick) var(--artdeco-ease-out);

      &:hover {
        border-color: var(--artdeco-border-hover);
      }

      &:focus {
        border-color: var(--artdeco-border-hover);
        box-shadow: var(--artdeco-glow-subtle);
      }

      &::placeholder {
        color: var(--artdeco-fg-subtle);
        text-transform: uppercase;
        letter-spacing: var(--artdeco-tracking-wide);
      }
    }
  }
}

.trade-amount-display {
  display: block;
  font-family: var(--artdeco-font-accent, var(--font-mono));
  font-size: var(--artdeco-text-xl);
  font-weight: var(--artdeco-font-bold);
  color: var(--artdeco-gold-primary);
  padding: var(--artdeco-spacing-3) var(--artdeco-spacing-4);
  background: color-mix(in srgb, var(--artdeco-gold-primary) 5%, var(--artdeco-bg-card));
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-none);
  text-align: center;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: var(--artdeco-spacing-3);

  :deep(.el-button) {
    font-family: var(--artdeco-font-heading, var(--font-display));
    font-size: var(--artdeco-text-compact-base);
    font-weight: var(--artdeco-font-semibold);
    text-transform: uppercase;
    letter-spacing: var(--artdeco-tracking-wider);
    border-radius: var(--artdeco-radius-none);
    padding: var(--artdeco-spacing-2) var(--artdeco-spacing-6);
  }
}
</style>
