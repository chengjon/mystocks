<template>
  <div class="demo-card card">
    <div class="card-header">
      <div class="header-content">
        <span class="header-icon">🤖</span>
        <span class="header-title">股票价格预测模型</span>
      </div>
      <span class="status-badge warning">功能展示</span>
    </div>

    <div class="prediction-section">
      <div class="config-alert">
        <svg class="alert-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="16" x2="12" y2="12"></line>
          <line x1="12" y1="8" x2="12.01" y2="8"></line>
        </svg>
        <div class="alert-content">
          <div class="alert-title">模型配置</div>
          <div class="alert-text">
            <strong>LightGBM 超参数：</strong>
            <ul class="params-list">
              <li>num_leaves=25, learning_rate=0.2, n_estimators=70</li>
              <li>max_depth=15, bagging_fraction=0.8, feature_fraction=0.8</li>
              <li>reg_lambda=0.9（L2 正则化）</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="steps-section">
        <h3 class="section-title">
          <span class="title-icon">📊</span>
          模型训练流程
        </h3>
        <div class="steps-container">
          <div
            v-for="(step, index) in steps"
            :key="index"
            class="step-item"
            :class="{ active: modelStep === index + 1, completed: modelStep > index + 1 }"
          >
            <div class="step-indicator">
              <div class="step-number">{{ index + 1 }}</div>
              <div class="step-line" v-if="index < steps.length - 1"></div>
            </div>
            <div class="step-content">
              <div class="step-title">{{ step.title }}</div>
              <div class="step-desc">{{ step.description }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="model-actions">
        <button class="button primary" @click="runModelDemo" :disabled="modelLoading">
          <svg v-if="modelLoading" class="spinner" width="16" height="16" viewBox="0 0 50 50">
            <circle cx="25" cy="25" r="20" fill="none" :stroke="'var(--gold-primary)'" stroke-width="4"></circle>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="'currentColor'" stroke-width="2">
            <polygon points="5,3 19,12 5,21 5,3"></polygon>
          </svg>
          {{ modelLoading ? '运行中...' : '运行模型演示' }}
        </button>
        <button class="button" @click="viewModelCode">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" :stroke="'var(--gold-primary)'" stroke-width="2">
            <polyline points="16,18 22,12 16,6"></polyline>
            <polyline points="8,6 2,12 8,18"></polyline>
          </svg>
          查看代码
        </button>
      </div>

      <div v-if="modelResults" class="model-results">
        <h3 class="section-title">
          <span class="title-icon">📈</span>
          预测结果
        </h3>
        <div class="results-grid">
          <div class="result-item">
            <label>RMSE（均方根误差）</label>
            <span class="result-value">{{ modelResults.rmse }}</span>
          </div>
          <div class="result-item">
            <label>训练样本数</label>
            <span class="result-value">{{ modelResults.trainSamples }}</span>
          </div>
          <div class="result-item">
            <label>测试样本数</label>
            <span class="result-value">{{ modelResults.testSamples }}</span>
          </div>
          <div class="result-item">
            <label>特征维度</label>
            <span class="result-value">{{ modelResults.featureDim }}</span>
          </div>
        </div>

        <div class="success-alert">
          <svg class="alert-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" :stroke="'var(--fall)'" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
            <polyline points="22,4 12,14.01 9,11.01"></polyline>
          </svg>
          <div class="alert-content">
            <div class="alert-title">预测结果说明</div>
            <div class="alert-text">
              模型使用历史 OHLCV 数据的滚动窗口特征，预测下一个交易日的收盘价。
              预测结果已保存为 predict.png 和 predict2.png 图片。
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref , onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const modelStep = ref(0)
const modelLoading = ref(false)
const modelResults = ref<unknown>(null)

const steps = [
  { title: '数据加载', description: '读取通达信 .day 文件' },
  { title: '特征工程', description: '生成滚动窗口特征（10步×6列）' },
  { title: '数据分割', description: '80% 训练集 / 20% 测试集' },
  { title: '模型训练', description: 'LightGBM GBDT 回归训练' },
  { title: '预测评估', description: '计算 RMSE 并绘制预测曲线' }
]

const runModelDemo = async () => {
  modelLoading.value = true
  modelStep.value = 0

  for (let i = 0; i <= 4; i++) {
    await new Promise(resolve => setTimeout(resolve, 800))
    modelStep.value = i + 1
  }

  modelResults.value = {
    rmse: '2.35',
    trainSamples: '2400',
    testSamples: '600',
    featureDim: '60 (10步 × 6特征)'
  }

  modelLoading.value = false
  ElMessage.success('模型演示完成！预测结果已生成')
}

const viewModelCode = () => {
  ElMessageBox.alert(
    `
# 核心代码示例

class Regressor:
    def __init__(self, step=10, feature_num=6):
        self.X, self.y = gen_model_datum(step=step, feature_num=6)

    def model_train(self):
        self.model = LGBMRegressor(
            boosting_type='gbdt',
            objective='regression',
            num_leaves=25,
            learning_rate=0.2,
            n_estimators=70,
            max_depth=15
        )
        self.model.fit(self.X_train, self.y_train)

    def model_predict(self):
        self.y_pred = self.model.predict(self.X_test)

    def model_evaluate(self):
        rmse = mean_squared_error(self.y_test, self.y_pred) ** 0.5
        print(f'RMSE: {rmse}')
    `,
    '模型代码',
    {
      confirmButtonText: '关闭',
      dangerouslyUseHTMLString: false
    }
  )
}

// Auto-generated: cleanup timers to prevent memory leaks
const _timer_1: ReturnType<typeof setTimeout> | null = null
onUnmounted(() => {
  if (_timer_1) clearTimeout(_timer_1)
})
</script>

<style scoped lang="scss">
@import "./styles/Prediction.scss";
</style>
