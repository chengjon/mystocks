<template>
  <div class="asset-allocation-container">
    <!-- 资产配置主容器 -->
    <div class="asset-allocation-header">
      <h2 class="asset-allocation-title">资产配置</h2>
      <div class="asset-allocation-actions">
        <button class="btn-primary" @click="saveAllocation">保存配置</button>
        <button class="btn-secondary" @click="resetAllocation">重置</button>
        <button class="btn-secondary" @click="exportAllocation">导出</button>
      </div>
    </div>

    <!-- 配置选择 -->
    <div class="allocation-selection-section">
      <div class="card selection-card">
        <div class="card-header">
          <h3>配置选择</h3>
        </div>
        <div class="card-body">
          <div class="allocation-options">
            <div class="allocation-option" :class="{ active: selectedAllocation === 'equity' }" @click="selectAllocation('equity')">
              <div class="option-icon">📊</div>
              <div class="option-info">
                <span class="option-name">股票配置</span>
                <span class="option-description">股票资产配置和分配</span>
              </div>
              <div class="option-arrow">→</div>
            </div>
            <div class="allocation-option" :class="{ active: selectedAllocation === 'bond' }" @click="selectAllocation('bond')">
              <div class="option-icon">📈</div>
              <div class="option-info">
                <span class="option-name">债券配置</span>
                <span class="option-description">债券资产配置和分配</span>
              </div>
              <div class="option-arrow">→</div>
            </div>
            <div class="allocation-option" :class="{ active: selectedAllocation === 'cash' }" @click="selectAllocation('cash')">
              <div class="option-icon">💰</div>
              <div class="option-info">
                <span class="option-name">现金配置</span>
                <span class="option-description">现金资产配置和分配</span>
              </div>
              <div class="option-arrow">→</div>
            </div>
            <div class="allocation-option" :class="{ active: selectedAllocation === 'mixed' }" @click="selectAllocation('mixed')">
              <div class="option-icon">🔄</div>
              <div class="option-info">
                <span class="option-name">混合配置</span>
                <span class="option-description">多资产混合配置和分配</span>
              </div>
              <div class="option-arrow">→</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 配置表单 -->
    <div class="allocation-form-section">
      <div class="card allocation-form-card">
        <div class="card-header">
          <h3>配置表单</h3>
        </div>
        <div class="card-body">
          <div class="allocation-form">
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">配置名称</label>
                <input type="text" v-model="allocationForm.name" placeholder="输入配置名称" class="form-input">
              </div>
              <div class="form-group">
                <label class="form-label">配置描述</label>
                <textarea v-model="allocationForm.description" placeholder="输入配置描述" class="form-textarea"></textarea>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">总资金</label>
                <input type="number" v-model="allocationForm.totalAmount" placeholder="输入总资金" class="form-input">
              </div>
              <div class="form-group">
                <label class="form-label">风险偏好</label>
                <select v-model="allocationForm.riskPreference" class="form-select">
                  <option value="conservative">保守</option>
                  <option value="moderate">中等</option>
                  <option value="aggressive">激进</option>
                </select>
              </div>
            </div>
            <div class="form-row">
              <div class="form-group">
                <label class="form-label">投资期限</label>
                <select v-model="allocationForm.investmentPeriod" class="form-select">
                  <option value="short">短期</option>
                  <option value="medium">中期</option>
                  <option value="long">长期</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">再平衡频率</label>
                <select v-model="allocationForm.rebalanceFrequency" class="form-select">
                  <option value="daily">每日</option>
                  <option value="weekly">每周</option>
                  <option value="monthly">每月</option>
                  <option value="quarterly">每季</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 资产分配 -->
    <div class="asset-allocation-section">
      <div class="card allocation-card">
        <div class="card-header">
          <h3>资产分配</h3>
          <div class="allocation-actions">
            <button class="btn-secondary" @click="addAssetAllocation">添加资产</button>
            <button class="btn-secondary" @click="autoAllocate">自动分配</button>
          </div>
        </div>
        <div class="card-body">
          <div class="allocation-list">
            <div class="allocation-item" v-for="(allocation, index) in allocationForm.allocations" :key="index">
              <div class="allocation-info">
                <div class="allocation-row">
                  <div class="allocation-group">
                    <label class="group-label">资产类型</label>
                    <select v-model="allocation.type" class="group-select">
                      <option value="equity">股票</option>
                      <option value="bond">债券</option>
                      <option value="fund">基金</option>
                      <option value="cash">现金</option>
                    </select>
                  </div>
                  <div class="allocation-group">
                    <label class="group-label">分配比例</label>
                    <input type="number" v-model="allocation.percentage" placeholder="输入百分比" class="group-input" min="0" max="100" step="1">
                  </div>
                </div>
                <div class="allocation-row">
                  <div class="allocation-group">
                    <label class="group-label">最小金额</label>
                    <input type="number" v-model="allocation.minAmount" placeholder="输入最小金额" class="group-input" min="0">
                  </div>
                  <div class="allocation-group">
                    <label class="group-label">最大金额</label>
                    <input type="number" v-model="allocation.maxAmount" placeholder="输入最大金额" class="group-input" min="0">
                  </div>
                </div>
                <div class="allocation-row">
                  <div class="allocation-group">
                    <label class="group-label">股票代码</label>
                    <input type="text" v-model="allocation.stockCode" placeholder="输入股票代码（可选）" class="group-input" :disabled="allocation.type !== 'equity'">
                  </div>
                  <div class="allocation-group">
                    <label class="group-label">基金代码</label>
                    <input type="text" v-model="allocation.fundCode" placeholder="输入基金代码（可选）" class="group-input" :disabled="allocation.type !== 'fund'">
                  </div>
                </div>
                <div class="allocation-actions">
                  <button class="btn-remove" @click="removeAllocation(index)" v-if="allocationForm.allocations.length > 1">删除</button>
                </div>
              </div>
            </div>
          </div>
          <div class="allocation-summary">
            <div class="summary-row">
              <span class="summary-label">总计</span>
              <span class="summary-value">{{ totalPercentage }}%</span>
            </div>
            <div class="summary-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: totalPercentage + '%' }"></div>
              </div>
              <div class="progress-text">
                {{ totalPercentage }}% 已分配
              </div>
            </div>
            <div class="summary-remaining" :class="{ complete: totalPercentage === 100 }">
              <span class="remaining-label">剩余</span>
              <span class="remaining-value">{{ 100 - totalPercentage }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 配置预览 -->
    <div class="allocation-preview-section">
      <div class="card preview-card">
        <div class="card-header">
          <h3>配置预览</h3>
        </div>
        <div class="card-body">
          <div class="preview-content">
            <div class="preview-header">
              <h4>{{ allocationForm.name || '未命名配置' }}</h4>
              <span class="preview-description">{{ allocationForm.description || '暂无描述' }}</span>
            </div>
            <div class="preview-allocation">
              <div class="preview-pie">
                <canvas id="allocationPieChart" :height="300"></canvas>
                <div class="pie-legend">
                  <div class="legend-item" v-for="allocation in allocationForm.allocations" :key="allocation.type">
                    <div class="legend-color" :style="{ backgroundColor: getAllocationColor(allocation.type) }"></div>
                    <span class="legend-label">{{ getAllocationTypeName(allocation.type) }}</span>
                    <span class="legend-value">{{ allocation.percentage }}%</span>
                  </div>
                </div>
              </div>
              <div class="preview-table">
                <table class="allocation-table">
                  <thead>
                    <tr>
                      <th>资产类型</th>
                      <th>分配比例</th>
                      <th>金额</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="allocation in allocationForm.allocations" :key="allocation.type">
                      <td class="table-type">{{ getAllocationTypeName(allocation.type) }}</td>
                      <td class="table-percentage">{{ allocation.percentage }}%</td>
                      <td class="table-amount">{{ formatMoney(allocation.percentage / 100 * allocationForm.totalAmount) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div class="preview-summary">
              <div class="summary-item">
                <span class="summary-label">总资金</span>
                <span class="summary-value">{{ formatMoney(allocationForm.totalAmount) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">风险偏好</span>
                <span class="summary-value">{{ getRiskPreferenceName(allocationForm.riskPreference) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">投资期限</span>
                <span class="summary-value">{{ getInvestmentPeriodName(allocationForm.investmentPeriod) }}</span>
              </div>
              <div class="summary-item">
                <span class="summary-label">再平衡频率</span>
                <span class="summary-value">{{ getRebalanceFrequencyName(allocationForm.rebalanceFrequency) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div class="loading-overlay" v-if="isLoading">
      <div class="loading-spinner"></div>
      <span class="loading-text">正在保存资产配置...</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { usePortfolioStore } from '@/stores/portfolio'
import { useRouter } from 'vue-router'
import type { AllocationForm, AssetAllocation, AllocationType, RiskPreference, InvestmentPeriod, RebalanceFrequency } from '@/types/portfolio'
import { saveAssetAllocation, getAssetAllocation } from '@/api/portfolio'
import { formatMoney } from '@/utils/format'

const router = useRouter()
const portfolioStore = usePortfolioStore()

const selectedAllocation = ref<AllocationType>('equity')

const allocationForm = reactive<AllocationForm>({
  name: '',
  description: '',
  totalAmount: 1000000,
  riskPreference: 'moderate',
  investmentPeriod: 'medium',
  rebalanceFrequency: 'monthly',
  allocations: [
    {
      type: 'equity',
      percentage: 50,
      minAmount: 100000,
      maxAmount: 500000,
      stockCode: '',
      fundCode: ''
    },
    {
      type: 'bond',
      percentage: 30,
      minAmount: 100000,
      maxAmount: 300000,
      stockCode: '',
      fundCode: ''
    },
    {
      type: 'cash',
      percentage: 20,
      minAmount: 100000,
      maxAmount: 200000,
      stockCode: '',
      fundCode: ''
    }
  ]
})

const isLoading = ref<boolean>(false)

const totalPercentage = computed(() => {
  return allocationForm.allocations.reduce((sum, allocation) => sum + allocation.percentage, 0)
})

const selectAllocation = (type: AllocationType) => {
  selectedAllocation.value = type
}

const addAssetAllocation = () => {
  allocationForm.allocations.push({
    type: 'equity',
    percentage: 10,
    minAmount: 0,
    maxAmount: 0,
    stockCode: '',
    fundCode: ''
  })
}

const removeAllocation = (index: number) => {
  if (allocationForm.allocations.length > 1) {
    allocationForm.allocations.splice(index, 1)
  }
}

const autoAllocate = () => {
  // 根据风险偏好自动分配
  const equityPercentage = getEquityPercentageByRisk(allocationForm.riskPreference)
  const bondPercentage = getBondPercentageByRisk(allocationForm.riskPreference)
  const cashPercentage = 100 - equityPercentage - bondPercentage
  
  allocationForm.allocations = [
    {
      type: 'equity',
      percentage: equityPercentage,
      minAmount: 0,
      maxAmount: 0,
      stockCode: '',
      fundCode: ''
    },
    {
      type: 'bond',
      percentage: bondPercentage,
      minAmount: 0,
      maxAmount: 0,
      stockCode: '',
      fundCode: ''
    },
    {
      type: 'cash',
      percentage: cashPercentage,
      minAmount: 0,
      maxAmount: 0,
      stockCode: '',
      fundCode: ''
    }
  ]
}

const saveAllocation = async () => {
  try {
    isLoading.value = true
    
    const response = await saveAssetAllocation(allocationForm)
    
    if (response.code === 200) {
      console.log('Asset allocation saved successfully')
      alert('资产配置保存成功！')
      router.push('/portfolio/allocation')
    } else {
      console.error('Failed to save allocation:', response.message)
      alert('保存失败：' + response.message)
    }
  } catch (error) {
    console.error('Error saving allocation:', error)
    alert('保存失败：' + error)
  } finally {
    isLoading.value = false
  }
}

const resetAllocation = () => {
  if (confirm('确定要重置所有资产配置吗？')) {
    allocationForm.name = ''
    allocationForm.description = ''
    allocationForm.totalAmount = 1000000
    allocationForm.riskPreference = 'moderate'
    allocationForm.investmentPeriod = 'medium'
    allocationForm.rebalanceFrequency = 'monthly'
    
    allocationForm.allocations = [
      {
        type: 'equity',
        percentage: 50,
        minAmount: 100000,
        maxAmount: 500000,
        stockCode: '',
        fundCode: ''
      },
      {
        type: 'bond',
        percentage: 30,
        minAmount: 100000,
        maxAmount: 300000,
        stockCode: '',
        fundCode: ''
      },
      {
        type: 'cash',
        percentage: 20,
        minAmount: 100000,
        maxAmount: 200000,
        stockCode: '',
        fundCode: ''
      }
    ]
    
    alert('资产配置已重置')
  }
}

const exportAllocation = () => {
  try {
    const reportData = {
      timestamp: new Date().toISOString(),
      allocation: allocationForm
    }
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], {
      type: 'application/json'
    })
    
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `asset_allocation_${new Date().toISOString().split('T')[0]}.json`
    link.click()
    
    console.log('Asset allocation exported')
  } catch (error) {
    console.error('Error exporting allocation:', error)
  }
}

const getEquityPercentageByRisk = (risk: RiskPreference) => {
  const percentages = {
    conservative: 30,
    moderate: 50,
    aggressive: 70
  }
  return percentages[risk] || 50
}

const getBondPercentageByRisk = (risk: RiskPreference) => {
  const percentages = {
    conservative: 50,
    moderate: 30,
    aggressive: 20
  }
  return percentages[risk] || 30
}

const getAllocationColor = (type: string) => {
  const colors = {
    equity: '#ef4444',
    bond: '#22c55e',
    fund: '#f59e0b',
    cash: '#3b82f6'
  }
  return colors[type] || '#999'
}

const getAllocationTypeName = (type: string) => {
  const names = {
    equity: '股票',
    bond: '债券',
    fund: '基金',
    cash: '现金'
  }
  return names[type] || type
}

const getRiskPreferenceName = (risk: string) => {
  const names = {
    conservative: '保守',
    moderate: '中等',
    aggressive: '激进'
  }
  return names[risk] || risk
}

const getInvestmentPeriodName = (period: string) => {
  const names = {
    short: '短期',
    medium: '中期',
    long: '长期'
  }
  return names[period] || period
}

const getRebalanceFrequencyName = (frequency: string) => {
  const names = {
    daily: '每日',
    weekly: '每周',
    monthly: '每月',
    quarterly: '每季'
  }
  return names[frequency] || frequency
}

const formatMoney = (value: number) => {
  if (value >= 100000000) return (value / 100000000).toFixed(2) + '亿'
  if (value >= 10000) return (value / 10000).toFixed(2) + '万'
  return value.toFixed(2)
}

onMounted(async () => {
  await renderAllocationPieChart()
  console.log('AssetAllocation component mounted')
})
</script>

<style scoped lang="scss">
.asset-allocation-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.asset-allocation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.asset-allocation-title {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.asset-allocation-actions {
  display: flex;
  gap: 10px;
}

.btn-primary,
.btn-secondary,
.btn-remove {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover {
  background: #1976d2;
}

.btn-secondary {
  background: transparent;
  color: #2196f3;
  border: 1px solid #2196f3;
}

.btn-secondary:hover {
  background: #f0f0f0;
  border-color: #2196f3;
}

.allocation-selection-section,
.allocation-form-section,
.asset-allocation-section,
.allocation-preview-section {
  margin-bottom: 20px;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 15px 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.card-body {
  padding: 20px;
}

.allocation-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.allocation-option {
  padding: 15px;
  background: #f9f9f9;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.allocation-option:hover {
  background: #f5f7fa;
  border-color: #2196f3;
}

.allocation-option.active {
  background: #e3f2fd;
  border-color: #2196f3;
}

.option-icon {
  font-size: 32px;
  width: 50px;
  text-align: center;
}

.option-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.option-name {
  font-size: 16px;
  font-weight: bold;
  color: #333;
}

.option-description {
  font-size: 14px;
  color: #666;
}

.option-arrow {
  font-size: 24px;
  color: #999;
}

.allocation-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  display: block;
  margin-bottom: 8px;
}

.form-input {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.form-input:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 3px rgba(33, 150, 243, 0.2);
}

.form-textarea {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.form-textarea:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 3px rgba(33, 150, 243, 0.2);
}

.form-select {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
}

.form-select:focus {
  outline: none;
  border-color: #2196f3;
  box-shadow: 0 0 3px rgba(33, 150, 243, 0.2);
}

.allocation-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.allocation-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.allocation-item {
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.allocation-info {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.allocation-row {
  display: flex;
  gap: 15px;
}

.allocation-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.group-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.group-select,
.group-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: all 0.3s;
}

.group-select:focus,
.group-input:focus {
  outline: none;
  border-color: #2196f3;
}

.group-input:disabled {
  background: #f0f0f0;
  cursor: not-allowed;
}

.allocation-actions {
  display: flex;
  gap: 10px;
  align-items: flex-end;
}

.btn-remove {
  padding: 8px 16px;
  border: 1px solid #e0e0e0;
  background: white;
  color: #666;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-remove:hover {
  background: #f44336;
  color: white;
  border-color: #f44336;
}

.allocation-summary {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 8px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.summary-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.summary-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.summary-progress {
  margin-bottom: 15px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #2196f3 0%, #374151 100%);
  transition: width 0.3s;
}

.progress-text {
  font-size: 14px;
  color: #666;
  font-weight: 500;
  text-align: center;
  margin-top: 8px;
}

.summary-remaining {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-remaining.complete {
  background: #d1fae5;
  border: 1px solid #0d9488;
}

.remaining-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.remaining-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.preview-header {
  padding: 20px;
  background: #f9f9f9;
  border-radius: 8px;
}

.preview-header h4 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0 0 10px 0;
}

.preview-description {
  font-size: 14px;
  color: #999;
  font-style: italic;
  margin: 0;
}

.preview-allocation {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.preview-pie {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-label {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.legend-value {
  font-size: 14px;
  color: #999;
  font-weight: 500;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
}

.preview-table th,
.preview-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.preview-table th {
  background: #f9f9f9;
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.preview-table tbody tr:hover {
  background: #f5f7fa;
}

.table-type {
  font-weight: 500;
}

.table-percentage {
  font-weight: 500;
}

.table-amount {
  font-weight: 500;
}

.preview-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.summary-item {
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
  text-align: center;
}

.summary-item .summary-label {
  font-size: 14px;
  color: #999;
  font-weight: 500;
  display: block;
  margin-bottom: 10px;
}

.summary-item .summary-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 999;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 5px solid #2196f3;
  border-top-color: transparent;
  border-right-color: #2196f3;
  border-bottom-color: #2196f3;
  border-left-color: #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-text {
  color: white;
  font-size: 16px;
  font-weight: 500;
  margin-top: 20px;
}

@media (max-width: 768px) {
  .allocation-options {
    grid-template-columns: 1fr;
  }
  
  .allocation-form,
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .preview-allocation {
    grid-template-columns: 1fr;
  }
  
  .preview-summary {
    grid-template-columns: 1fr;
  }
}
</style>
