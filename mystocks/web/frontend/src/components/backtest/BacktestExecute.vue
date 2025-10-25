<template>
  <div class="backtest-execute">
    <el-card>
      <template #header>
        <span>回测执行</span>
      </template>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
      >
        <el-form-item label="回测名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入回测名称" />
        </el-form-item>

        <el-form-item label="选择策略" prop="strategy_id">
          <el-select v-model="form.strategy_id" placeholder="请选择策略" style="width: 100%">
            <el-option
              v-for="strategy in strategies"
              :key="strategy.id"
              :label="strategy.name"
              :value="strategy.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="回测时间">
          <el-col :span="11">
            <el-form-item prop="start_date">
              <el-date-picker
                v-model="form.start_date"
                type="date"
                placeholder="开始日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="2" class="text-center">
            <span>-</span>
          </el-col>
          <el-col :span="11">
            <el-form-item prop="end_date">
              <el-date-picker
                v-model="form.end_date"
                type="date"
                placeholder="结束日期"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-form-item>

        <el-form-item label="初始资金" prop="initial_cash">
          <el-input-number
            v-model="form.initial_cash"
            :min="10000"
            :step="100000"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="交易参数">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="佣金费率" label-width="80px">
                <el-input-number
                  v-model="form.commission_rate"
                  :min="0"
                  :max="0.01"
                  :step="0.0001"
                  :precision="4"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="印花税率" label-width="80px">
                <el-input-number
                  v-model="form.stamp_tax_rate"
                  :min="0"
                  :max="0.01"
                  :step="0.0001"
                  :precision="4"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="滑点率" label-width="60px">
                <el-input-number
                  v-model="form.slippage_rate"
                  :min="0"
                  :max="0.01"
                  :step="0.0001"
                  :precision="4"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            开始回测
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 回测进度 -->
      <el-card v-if="backtestId" class="progress-card">
        <template #header>
          <span>回测进度</span>
        </template>
        <el-progress :percentage="progress" :status="progressStatus" />
        <p class="progress-text">{{ progressText }}</p>
      </el-card>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { strategyApi } from '@/api/strategy'
import { backtestApi } from '@/api/backtest'

const router = useRouter()
const route = useRoute()

// 策略列表
const strategies = ref([])

// 表单
const formRef = ref()
const form = reactive({
  name: '',
  strategy_id: null,
  start_date: '',
  end_date: '',
  initial_cash: 1000000,
  commission_rate: 0.0003,
  stamp_tax_rate: 0.001,
  slippage_rate: 0.001
})

// 表单验证规则
const rules = {
  name: [{ required: true, message: '请输入回测名称', trigger: 'blur' }],
  strategy_id: [{ required: true, message: '请选择策略', trigger: 'change' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }],
  end_date: [{ required: true, message: '请选择结束日期', trigger: 'change' }]
}

// 回测状态
const submitting = ref(false)
const backtestId = ref<number | null>(null)
const progress = ref(0)
const progressStatus = ref('')
const progressText = ref('')

// 加载策略列表
const loadStrategies = async () => {
  try {
    const response = await strategyApi.listStrategies({ status: 'active' })
    strategies.value = response.items
  } catch (error) {
    ElMessage.error('加载策略列表失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()

    submitting.value = true
    const response = await backtestApi.runBacktest(form)
    backtestId.value = response.backtest_id

    ElMessage.success('回测已提交，正在执行...')

    // 开始轮询进度
    pollProgress()
  } catch (error) {
    ElMessage.error('提交回测失败')
  } finally {
    submitting.value = false
  }
}

// 轮询回测进度
const pollProgress = () => {
  const timer = setInterval(async () => {
    try {
      const response = await backtestApi.getBacktestResult(backtestId.value!)

      if (response.status === 'completed') {
        clearInterval(timer)
        progress.value = 100
        progressStatus.value = 'success'
        progressText.value = '回测完成'
        ElMessage.success('回测完成！')

        // 跳转到结果页面
        setTimeout(() => {
          router.push(`/backtest/detail/${backtestId.value}`)
        }, 1000)
      } else if (response.status === 'failed') {
        clearInterval(timer)
        progressStatus.value = 'exception'
        progressText.value = '回测失败'
        ElMessage.error('回测执行失败')
      } else if (response.status === 'running') {
        // 模拟进度
        progress.value = Math.min(progress.value + 10, 90)
        progressText.value = '回测执行中...'
      }
    } catch (error) {
      clearInterval(timer)
      ElMessage.error('获取回测进度失败')
    }
  }, 2000) // 每2秒轮询一次
}

// 重置表单
const handleReset = () => {
  formRef.value.resetFields()
  backtestId.value = null
  progress.value = 0
}

// 挂载时加载策略列表
onMounted(() => {
  loadStrategies()

  // 如果URL参数中有strategy_id，自动选中
  if (route.query.strategy_id) {
    form.strategy_id = Number(route.query.strategy_id)
  }
})
</script>

<style scoped lang="scss">
.backtest-execute {
  .progress-card {
    margin-top: 20px;
  }

  .progress-text {
    margin-top: 10px;
    text-align: center;
    color: #606266;
  }

  .text-center {
    text-align: center;
  }
}
</style>
