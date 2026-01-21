<template>
    <ArtDecoCard class="artdeco-backtest-config" :hoverable="false">
        <template #header>
            <div class="config-header">
                <h3 class="config-title">BACKTEST CONFIGURATION</h3>
                <ArtDecoButton variant="solid" @click="handleSubmit" :loading="loading">RUN BACKTEST</ArtDecoButton>
            </div>
        </template>

        <div class="config-body">
            <div class="config-grid">
                <div class="config-group">
                    <label class="artdeco-label">STRATEGY</label>
                    <ArtDecoSelect
                        v-model="formData.strategy_code"
                        placeholder="SELECT STRATEGY"
                        :options="strategyOptions"
                        :disabled="disabled"
                    />
                </div>

                <div class="config-group">
                    <label class="artdeco-label">SYMBOL</label>
                    <ArtDecoInput v-model="formData.symbol" type="text" placeholder="600519" :disabled="disabled" />
                </div>

                <div class="config-group">
                    <label class="artdeco-label">DATE RANGE</label>
                    <el-date-picker
                        v-model="formData.dateRange"
                        type="daterange"
                        range-separator="TO"
                        start-placeholder="START"
                        end-placeholder="END"
                        format="YYYY-MM-DD"
                        value-format="YYYY-MM-DD"
                        class="artdeco-date-picker"
                        :disabled="disabled"
                    />
                </div>

                <div class="config-group">
                    <label class="artdeco-label">CAPITAL (¥)</label>
                    <input
                        v-model.number="formData.initial_capital"
                        type="number"
                        :min="10000"
                        :max="100000000"
                        :step="10000"
                        class="artdeco-input"
                        :placeholder="String(defaultCapital)"
                        :disabled="disabled"
                    />
                </div>

                <div class="config-group">
                    <label class="artdeco-label">COMMISSION (%)</label>
                    <input
                        v-model.number="formData.commission_rate"
                        type="number"
                        :min="0"
                        :max="0.01"
                        :step="0.0001"
                        class="artdeco-input"
                        placeholder="0.0003"
                        :disabled="disabled"
                    />
                </div>

                <div class="config-group">
                    <label class="artdeco-label">SLIPPAGE (%)</label>
                    <input
                        v-model.number="formData.slippage_rate"
                        type="number"
                        :min="0"
                        :max="0.01"
                        :step="0.0001"
                        class="artdeco-input"
                        placeholder="0.0001"
                        :disabled="disabled"
                    />
                </div>
            </div>

            <div v-if="showAdvanced" class="advanced-options">
                <button class="toggle-advanced" @click="showAdvancedOptions = !showAdvancedOptions">
                    {{ showAdvancedOptions ? 'ADVANCED OPTIONS ▼' : 'ADVANCED OPTIONS ▶' }}
                </button>

                <div v-if="showAdvancedOptions" class="advanced-grid">
                    <div class="config-group">
                        <label class="artdeco-label">POSITION SIZE</label>
                        <input
                            v-model.number="formData.position_size"
                            type="number"
                            :min="0"
                            :max="1"
                            :step="0.1"
                            class="artdeco-input"
                            placeholder="1.0"
                            :disabled="disabled"
                        />
                    </div>

                    <div class="config-group">
                        <label class="artdeco-label">STOP LOSS (%)</label>
                        <input
                            v-model.number="formData.stop_loss_rate"
                            type="number"
                            :min="0"
                            :max="0.5"
                            :step="0.01"
                            class="artdeco-input"
                            placeholder="0.05"
                            :disabled="disabled"
                        />
                    </div>

                    <div class="config-group">
                        <label class="artdeco-label">TAKE PROFIT (%)</label>
                        <input
                            v-model.number="formData.take_profit_rate"
                            type="number"
                            :min="0"
                            :max="1.0"
                            :step="0.01"
                            class="artdeco-input"
                            placeholder="0.10"
                            :disabled="disabled"
                        />
                    </div>

                    <div class="config-group">
                        <label class="artdeco-label">MAX POSITION</label>
                        <input
                            v-model.number="formData.max_position"
                            type="number"
                            :min="1"
                            :step="1"
                            class="artdeco-input"
                            placeholder="5"
                            :disabled="disabled"
                        />
                    </div>
                </div>
            </div>

            <div v-if="presets.length > 0" class="presets-section">
                <label class="artdeco-label">QUICK PRESETS</label>
                <div class="presets-list">
                    <button
                        v-for="preset in presets"
                        :key="preset.name"
                        class="preset-btn"
                        :class="{ active: activePreset === preset.name }"
                        @click="applyPreset(preset)"
                    >
                        {{ preset.name }}
                    </button>
                </div>
            </div>
        </div>
    </ArtDecoCard>
</template>

<script setup lang="ts">
    import { ref, reactive, computed } from 'vue'
    import ArtDecoCard from '../base/ArtDecoCard.vue'
    import ArtDecoButton from '../base/ArtDecoButton.vue'
    import ArtDecoInput from '../base/ArtDecoInput.vue'
    import ArtDecoSelect from '../base/ArtDecoSelect.vue'

    interface Strategy {
        strategy_code: string
        strategy_name_cn: string
        strategy_name_en?: string
    }

    interface BacktestConfig {
        strategy_code: string
        symbol: string
        dateRange: [string, string]
        initial_capital: number
        commission_rate: number
        slippage_rate: number
        position_size: number
        stop_loss_rate: number
        take_profit_rate: number
        max_position: number
    }

    interface Preset {
        name: string
        config: Partial<BacktestConfig>
    }

    interface Props {
        strategies?: Strategy[]
        defaultCapital?: number
        showAdvanced?: boolean
        presets?: Preset[]
        disabled?: boolean
        loading?: boolean
    }

    const props = withDefaults(defineProps<Props>(), {
        strategies: () => [],
        defaultCapital: 100000,
        showAdvanced: false,
        presets: () => [],
        disabled: false,
        loading: false
    })

    const emit = defineEmits<{
        submit: [config: BacktestConfig]
        presetApplied: [preset: Preset]
    }>()

    const formData = reactive<BacktestConfig>({
        strategy_code: '',
        symbol: '',
        dateRange: [] as any,
        initial_capital: props.defaultCapital,
        commission_rate: 0.0003,
        slippage_rate: 0.0001,
        position_size: 1.0,
        stop_loss_rate: 0.05,
        take_profit_rate: 0.1,
        max_position: 5
    })

    const showAdvancedOptions = ref(false)
    const activePreset = ref<string>('')

    const strategyOptions = computed(() => {
        return props.strategies.map(s => ({
            value: s.strategy_code,
            label: `${s.strategy_code} - ${s.strategy_name_cn}`
        }))
    })

    const applyPreset = (preset: Preset) => {
        Object.assign(formData, preset.config)
        activePreset.value = preset.name
        emit('presetApplied', preset)
    }

    const handleSubmit = () => {
        if (!formData.strategy_code || !formData.symbol || !formData.dateRange || formData.dateRange.length !== 2) {
            return
        }
        emit('submit', formData)
    }
</script>

<style scoped lang="scss">
    @import '@/styles/artdeco-tokens.scss';

    .artdeco-backtest-config {
      background: var(--artdeco-bg-card);
    }

    .config-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .config-title {
      font-family: var(--artdeco-font-display);
      font-size: var(--artdeco-font-size-md); // 18px - Compact v3.1
      font-weight: 600;
      color: var(--artdeco-accent-gold);
      text-transform: uppercase;
      letter-spacing: var(--artdeco-tracking-wide);
      margin: 0;
    }

    .config-body {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-4);
    }

    .config-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: var(--artdeco-spacing-3);
    }

    .config-group {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-2);
    }

    .artdeco-label {
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm); // 12px - Compact v3.1
      font-weight: 600;
      color: var(--artdeco-accent-gold);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .artdeco-input {
      background: var(--artdeco-bg-primary);
      border: 1px solid rgba(212, 175, 55, 0.2);
      color: var(--artdeco-fg-secondary);
      font-family: var(--artdeco-font-mono);
      font-size: var(--artdeco-font-size-base); // 14px - Compact v3.1
      padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
      transition: all var(--artdeco-transition-base);
    }

    .artdeco-input:focus {
      outline: none;
      border-color: var(--artdeco-accent-gold);
      box-shadow: var(--artdeco-glow-subtle);
    }

    .artdeco-input:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    .artdeco-date-picker {
      width: 100%;
    }

    .advanced-options {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-3);
    }

    .toggle-advanced {
      background: transparent;
      border: none;
      color: var(--artdeco-fg-muted);
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm); // 12px - Compact v3.1
      text-transform: uppercase;
      letter-spacing: 0.1em;
      cursor: pointer;
      padding: var(--artdeco-spacing-2) 0;
      transition: all var(--artdeco-transition-base);
    }

    .toggle-advanced:hover {
      color: var(--artdeco-accent-gold);
    }

    .advanced-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: var(--artdeco-spacing-3);
      padding: var(--artdeco-spacing-3);
      background: var(--artdeco-bg-primary);
      border: 1px solid rgba(212, 175, 55, 0.2);
    }

    .presets-section {
      display: flex;
      flex-direction: column;
      gap: var(--artdeco-spacing-3);
    }

    .presets-list {
      display: flex;
      gap: var(--artdeco-spacing-2);
      flex-wrap: wrap;
    }

    .preset-btn {
      padding: var(--artdeco-spacing-2) var(--artdeco-spacing-3);
      background: var(--artdeco-bg-primary);
      border: 1px solid rgba(212, 175, 55, 0.2);
      color: var(--artdeco-fg-secondary);
      font-family: var(--artdeco-font-body);
      font-size: var(--artdeco-font-size-sm); // 12px - Compact v3.1
      text-transform: uppercase;
      letter-spacing: 0.05em;
      cursor: pointer;
      transition: all var(--artdeco-transition-base);
    }

    .preset-btn:hover {
      border-color: var(--artdeco-accent-gold);
      color: var(--artdeco-accent-gold);
    }

    .preset-btn.active {
      background: var(--artdeco-accent-gold);
      border-color: var(--artdeco-accent-gold);
      color: var(--artdeco-bg-primary);
    }
</style>
