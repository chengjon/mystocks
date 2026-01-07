<template>
  <div class="modal-overlay" v-if="visible">
    <div class="modal">
      <div class="corner-tl"></div>
      <div class="corner-br"></div>

      <div class="modal-header">
        <h3 class="modal-title">{{ form.type === 'buy' ? 'BUY STOCK' : 'SELL STOCK' }}</h3>
        <button class="close-btn" @click="handleClose">×</button>
      </div>

      <div class="modal-body">
        <div class="form-group">
          <label class="label">SYMBOL</label>
          <input v-model="form.symbol" type="text" class="input" placeholder="E.G: 600519">
        </div>
        <div class="form-group">
          <label class="label">STOCK NAME</label>
          <input v-model="form.stock_name" type="text" class="input" placeholder="AUTO LOADED" readonly>
        </div>
        <div class="form-group">
          <label class="label">QUANTITY</label>
          <input v-model.number="form.quantity" type="number" class="input" placeholder="MIN 100">
        </div>
        <div class="form-group">
          <label class="label">PRICE</label>
          <input v-model.number="form.price" type="number" step="0.01" class="input" placeholder="MARKET PRICE">
        </div>
        <div class="form-group">
          <label class="label">TRADE AMOUNT</label>
          <div class="trade-amount-display gold">
            ¥{{ (form.quantity * form.price).toFixed(2) }}
          </div>
        </div>
        <div class="form-group">
          <label class="label">REMARK</label>
          <textarea v-model="form.remark" class="textarea" rows="2" placeholder="OPTIONAL"></textarea>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn btn-default" @click="handleClose" :disabled="submitting">
          CANCEL
        </button>
        <button class="btn" :class="form.type === 'buy' ? 'btn-primary' : 'btn-danger'" @click="handleSubmit" :disabled="submitting">
          <span v-if="submitting" class="spinner"></span>
          <span v-else>{{ form.type === 'buy' ? 'BUY' : 'SELL' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, watch } from 'vue'
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

const setFormData = (data: Partial<TradeForm>) => {
  Object.assign(form, data)
}

defineExpose({
  setFormData,
  resetForm
})
</script>

<style scoped lang="scss">

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: var(--bg-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;

  .modal {
    position: relative;
    width: 480px;
    background: var(--bg-card);
    border: 1px solid var(--accent-gold);
    border-radius: var(--radius-none);
    box-shadow: 0 0 60px rgba(212, 175, 55, 0.2);

      position: absolute;
      top: 12px;
      left: 12px;
      width: 24px;
      height: 24px;
      border-top: 3px solid var(--accent-gold);
      border-left: 3px solid var(--accent-gold);
    }

      position: absolute;
      bottom: 12px;
      right: 12px;
      width: 24px;
      height: 24px;
      border-bottom: 3px solid var(--accent-gold);
      border-right: 3px solid var(--accent-gold);
    }

    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: var(--spacing-5) var(--spacing-6);
      border-bottom: 1px solid rgba(212, 175, 55, 0.2);

      .modal-title {
        font-family: var(--font-display);
        font-size: var(--font-size-h4);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: var(--tracking-widest);
        color: var(--accent-gold);
        margin: 0;
      }

        background: transparent;
        border: none;
        color: var(--fg-muted);
        font-size: 32px;
        cursor: pointer;
        transition: color var(--transition-base);

        &:hover {
          color: var(--accent-gold);
        }
      }
    }

    .modal-body {
      padding: var(--spacing-6);

      .form-group {
        margin-bottom: var(--spacing-4);

          display: block;
          font-family: var(--font-display);
          font-size: var(--font-size-xs);
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: var(--tracking-wider);
          color: var(--accent-gold);
          margin-bottom: var(--spacing-1);
        }

        .input {
          width: 100%;
          padding: var(--spacing-2) var(--spacing-3);
          font-family: var(--font-body);
          font-size: var(--font-size-body);
          color: var(--fg-primary);
          background: transparent;
          border: none;
          border-bottom: 2px solid var(--accent-gold);
          border-radius: var(--radius-none);
          transition: all var(--transition-base);

          &::placeholder {
            color: var(--fg-muted);
            text-transform: uppercase;
            letter-spacing: var(--tracking-normal);
          }

          &:focus {
            outline: none;
            border-bottom-color: var(--accent-gold-light);
            box-shadow: 0 4px 10px rgba(212, 175, 55, 0.2);
          }

          &[readonly] {
            color: var(--fg-muted);
            background: rgba(212, 175, 55, 0.05);
            border-bottom-color: rgba(212, 175, 55, 0.2);
          }
        }

          width: 100%;
          padding: var(--spacing-2) var(--spacing-3);
          font-family: var(--font-body);
          font-size: var(--font-size-body);
          color: var(--fg-primary);
          background: transparent;
          border: 1px solid rgba(212, 175, 55, 0.3);
          border-radius: var(--radius-none);
          transition: all var(--transition-base);

          &::placeholder {
            color: var(--fg-muted);
            text-transform: uppercase;
            letter-spacing: var(--tracking-normal);
          }

          &:focus {
            outline: none;
            border-color: var(--accent-gold);
            box-shadow: var(--glow-subtle);
          }
        }

        .trade-amount-display {
          display: block;
          font-family: var(--font-mono);
          font-size: var(--font-size-h4);
          font-weight: 700;
          padding: var(--spacing-2) var(--spacing-3);
          border: 1px solid rgba(212, 175, 55, 0.2);
          border-radius: var(--radius-none);
          background: rgba(212, 175, 55, 0.05);

          &.gold {
            color: var(--accent-gold);
          }
        }
      }
    }

    .modal-footer {
      display: flex;
      justify-content: flex-end;
      gap: var(--spacing-3);
      padding: var(--spacing-5) var(--spacing-6);
      border-top: 1px solid rgba(212, 175, 55, 0.2);
    }
  }
}

  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-2);
  padding: var(--spacing-3) var(--spacing-6);
  font-family: var(--font-display);
  font-size: var(--font-size-body);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: var(--tracking-widest);
  border: 2px solid var(--accent-gold);
  border-radius: var(--radius-none);
  cursor: pointer;
  transition: all var(--transition-base);

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

    display: inline-block;
    width: 20px;
    height: 20px;
    border: 2px solid rgba(0, 0, 0, 0.1);
    border-top-color: currentColor;
    border-radius: 50%;
  }

    to { transform: rotate(360deg); }
  }
}

  background: var(--accent-gold);
  color: var(--bg-primary);

  &:hover:not(:disabled) {
    background: var(--accent-gold-light);
    box-shadow: var(--glow-medium);
  }
}

  background: transparent;
  color: var(--accent-gold);

  &:hover:not(:disabled) {
    background: var(--bg-secondary);
    box-shadow: var(--glow-subtle);
  }
}
</style>
