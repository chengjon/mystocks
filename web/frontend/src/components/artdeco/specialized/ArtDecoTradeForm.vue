<template>
    <div v-if="visible" class="artdeco-trade-form-overlay" @click.self="handleCancel">
        <div class="artdeco-trade-form">
            <div class="artdeco-corner-tl"></div>
            <div class="artdeco-corner-br"></div>

            <div class="form-header">
                <h3 class="form-title">
                    {{ tradeType === 'buy' ? 'BUY STOCK' : 'SELL STOCK' }}
                </h3>
                <button class="close-btn" @click="handleCancel">×</button>
            </div>

            <div class="form-body">
                <div class="form-group">
                    <label class="artdeco-label">SYMBOL</label>
                    <input
                        v-model="formData.symbol"
                        type="text"
                        class="artdeco-input"
                        placeholder="E.G: 600519"
                        :disabled="readonly"
                        @input="handleSymbolChange"
                    />
                </div>

                <div class="form-group">
                    <label class="artdeco-label">STOCK NAME</label>
                    <input
                        v-model="formData.stock_name"
                        type="text"
                        class="artdeco-input"
                        placeholder="AUTO LOADED"
                        readonly
                    />
                </div>

                <div class="form-group">
                    <label class="artdeco-label">QUANTITY</label>
                    <input
                        v-model.number="formData.quantity"
                        type="number"
                        class="artdeco-input"
                        :placeholder="minQuantity ? `MIN ${minQuantity}` : 'QUANTITY'"
                        :min="minQuantity"
                        :step="stepQuantity"
                        :disabled="readonly"
                    />
                </div>

                <div class="form-group">
                    <label class="artdeco-label">PRICE</label>
                    <input
                        v-model.number="formData.price"
                        type="number"
                        step="0.01"
                        class="artdeco-input"
                        :placeholder="pricePlaceholder"
                        :min="0"
                        :disabled="readonly"
                    />
                </div>

                <div class="form-group">
                    <label class="artdeco-label">TRADE AMOUNT</label>
                    <div class="trade-amount-display" :class="tradeTypeClass">¥{{ tradeAmount.toFixed(2) }}</div>
                </div>

                <div v-if="showRemark" class="form-group">
                    <label class="artdeco-label">REMARK</label>
                    <textarea
                        v-model="formData.remark"
                        class="artdeco-textarea"
                        rows="2"
                        placeholder="OPTIONAL"
                        :disabled="readonly"
                    />
                </div>

                <div v-if="showMaxQuantity && maxQuantity > 0" class="form-group">
                    <label class="artdeco-label">MAX AVAILABLE</label>
                    <div class="max-quantity-display">{{ maxQuantity }}</div>
                </div>
            </div>

            <div class="form-footer">
                <button class="artdeco-btn artdeco-btn-secondary" @click="handleCancel">CANCEL</button>
                <button
                    class="artdeco-btn"
                    :class="tradeTypeClass"
                    @click="handleSubmit"
                    :disabled="disabled || submitting || !isValid"
                >
                    <span v-if="submitting" class="artdeco-spinner"></span>
                    <span v-else>{{ tradeType === 'buy' ? 'BUY' : 'SELL' }}</span>
                </button>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
    import { computed, reactive } from 'vue'

    interface Props {
        visible?: boolean
        tradeType?: 'buy' | 'sell'
        symbol?: string
        stockName?: string
        quantity?: number
        price?: number
        remark?: string
        readonly?: boolean
        disabled?: boolean
        submitting?: boolean
        minQuantity?: number
        stepQuantity?: number
        maxQuantity?: number
        pricePlaceholder?: string
        showRemark?: boolean
        showMaxQuantity?: boolean
    }

    const props = withDefaults(defineProps<Props>(), {
        visible: false,
        tradeType: 'buy',
        symbol: '',
        stockName: '',
        quantity: 100,
        price: 0,
        remark: '',
        readonly: false,
        disabled: false,
        submitting: false,
        minQuantity: 100,
        stepQuantity: 100,
        maxQuantity: 0,
        pricePlaceholder: 'MARKET PRICE',
        showRemark: true,
        showMaxQuantity: false
    })

    const emit = defineEmits<{
        'update:visible': [value: boolean]
        'update:symbol': [value: string]
        'update:stockName': [value: string]
        'update:quantity': [value: number]
        'update:price': [value: number]
        'update:remark': [value: string]
        submit: [data: TradeFormData]
        cancel: []
        symbolChange: [symbol: string]
    }>()

    interface TradeFormData {
        type: 'buy' | 'sell'
        symbol: string
        stock_name: string
        quantity: number
        price: number
        remark: string
    }

    const formData = reactive<TradeFormData>({
        type: props.tradeType,
        symbol: props.symbol,
        stock_name: props.stockName,
        quantity: props.quantity,
        price: props.price,
        remark: props.remark
    })

    const tradeAmount = computed(() => {
        return formData.quantity * formData.price
    })

    const tradeTypeClass = computed(() => {
        return props.tradeType === 'buy' ? 'artdeco-btn-rise' : 'artdeco-btn-fall'
    })

    const isValid = computed(() => {
        return formData.symbol.trim() !== '' && formData.quantity >= props.minQuantity && formData.price > 0
    })

    const handleSymbolChange = () => {
        emit('update:symbol', formData.symbol)
        emit('symbolChange', formData.symbol)
    }

    const handleSubmit = () => {
        if (!isValid.value) return

        emit('submit', {
            ...formData,
            type: props.tradeType
        })
    }

    const handleCancel = () => {
        emit('cancel')
        emit('update:visible', false)
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-trade-form-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(0, 0, 0, 0.7);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 2000;
      backdrop-filter: blur(4px);
    }

    .artdeco-trade-form {
      background: var(--artdeco-bg-card);
      border: 1px solid rgba(212, 175, 55, 0.2);
      padding: var(--artdeco-spacing-5);
      min-width: 500px;
      max-width: 600px;
      position: relative;
      overflow: hidden;
      box-shadow: var(--artdeco-glow-medium);
    }

    /* Corner decorations */
    .artdeco-corner-tl,
    .artdeco-corner-br {
      position: absolute;
      width: 16px;
      height: 16px;
      pointer-events: none;
      opacity: 0.4;
    }

    .artdeco-corner-tl {
      top: 8px;
      left: 8px;
      border-top: 2px solid var(--artdeco-accent-gold);
      border-left: 2px solid var(--artdeco-accent-gold);
    }

    .artdeco-corner-br {
      bottom: 8px;
      right: 8px;
      border-bottom: 2px solid var(--artdeco-accent-gold);
      border-right: 2px solid var(--artdeco-accent-gold);
    }

    /* Form header */
    .form-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: var(--artdeco-spacing-5);
      padding-bottom: var(--artdeco-spacing-4);
      border-bottom: 1px solid rgba(212, 175, 55, 0.2);
    }

    .form-title {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-md) // 18px - Compact v3.1;
      font-weight: 600;
      color: var(--artdeco-accent-gold);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
      margin: 0;
    }

    .close-btn {
      background: transparent;
      border: none;
      color: var(--artdeco-fg-muted);
      font-size: var(--artdeco-font-size-lg) // 24px - Compact v3.1;
      cursor: pointer;
      padding: 0;
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all var(--artdeco-transition-base);
    }

    .close-btn:hover {
      color: var(--artdeco-accent-gold);
    }

    /* Form body */
    .form-body {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-4);
      margin-bottom: var(--artdeco-spacing-5);
    }

    .form-group {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-2);
    }

    .artdeco-label {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      font-weight: 600;
      color: var(--artdeco-accent-gold);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .artdeco-input,
    .artdeco-textarea {
      background: var(--artdeco-bg-primary);
      border: 1px solid rgba(212, 175, 55, 0.2);
      color: var(--artdeco-fg-secondary);
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-input:focus,
    .artdeco-textarea:focus {
      outline: none;
      border-color: var(--artdeco-accent-gold);
      box-shadow: var(--artdeco-glow-subtle);
    }

    .artdeco-input:disabled,
    .artdeco-textarea:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .artdeco-textarea {
      resize: vertical;
      min-height: 60px;
    }

    .trade-amount-display {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-lg) // 24px - Compact v3.1;
      font-weight: 700;
      padding: var(--artdeco-spacing-3);
      background: var(--artdeco-bg-primary);
      border: 1px solid rgba(212, 175, 55, 0.2);
      text-align: center;
    }

    .trade-amount-display.gold {
      color: var(--artdeco-accent-gold);
    }

    .trade-amount-display.rise {
      color: var(--artdeco-rise);
    }

    .trade-amount-display.fall {
      color: var(--artdeco-fall);
    }

    .max-quantity-display {
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      color: var(--artdeco-fg-muted);
      padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
      background: var(--artdeco-bg-primary);
      border: 1px solid rgba(212, 175, 55, 0.2);
    }

    /* Form footer */
    .form-footer {
      display: flex;
      justify-content: flex-end;
      gap: var(--artdeco-spacing-3);
      padding-top: var(--artdeco-spacing-4);
      border-top: 1px solid rgba(212, 175, 55, 0.2);
    }

    /* Button styles */
    .artdeco-btn {
      padding: var(--artdeco-spacing-2) var(--artdeco-spacing-5);
      border: 1px solid rgba(212, 175, 55, 0.2);
      background: var(--artdeco-bg-card);
      color: var(--artdeco-fg-secondary);
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-base) // 14px - Compact v3.1;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      cursor: pointer;
      transition: all var(--artdeco-transition-base);
      position: relative;
      overflow: hidden;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: var(--artdeco-spacing-2);
    }

    .artdeco-btn:not(:disabled):hover {
      border-color: var(--artdeco-accent-gold);
      box-shadow: var(--artdeco-glow-subtle);
      transform: translateY(-1px);
    }

    .artdeco-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .artdeco-btn-secondary:hover {
      color: var(--artdeco-accent-gold);
    }

    .artdeco-btn-rise:hover {
      color: var(--artdeco-rise);
      border-color: var(--artdeco-rise);
    }

    .artdeco-btn-fall:hover {
      color: var(--artdeco-fall);
      border-color: var(--artdeco-fall);
    }

    /* Spinner */
    .artdeco-spinner {
      width: 16px;
      height: 16px;
      border: 2px solid rgba(212, 175, 55, 0.2);
      border-top-color: var(--artdeco-accent-gold);
      border-radius: 50%;
      animation: spin 0.6s linear infinite;
    }

    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }
</style>
