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
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const modelStep = ref(0)
const modelLoading = ref(false)
const modelResults = ref<any>(null)

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
</script>

<style scoped lang="scss">

.demo-card {
  background: var(--bg-secondary);
  border: 1px solid var(--gold-dim);
  padding: 20px;
  position: relative;
  border-radius: 0;

  &::before,
  &::after {
    content: '';
    position: absolute;
    width: 16px;
    height: 16px;
    border: 2px solid var(--gold-primary);
  }

  &::before {
    top: 12px;
    left: 12px;
    border-right: none;
    border-bottom: none;
  }

  &::after {
    bottom: 12px;
    right: 12px;
    border-left: none;
    border-top: none;
  }

  &:hover {
    border-color: var(--gold-primary);
    box-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--gold-dim);

  .header-content {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .header-icon {
    font-size: 20px;
  }

  .header-title {
    font-family: var(--font-display);
    font-size: 18px;
    color: var(--gold-primary);
    text-transform: uppercase;
    letter-spacing: 2px;
  }
}

.status-badge {
  padding: 6px 14px;
  background: rgba(244, 179, 67, 0.15);
  border: 1px solid #F4A738;
  color: #F4A738;
  font-family: var(--font-display);
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 1px;

  &.warning {
    background: rgba(244, 179, 67, 0.15);
    border-color: #F4A738;
    color: #F4A738;
  }
}

.prediction-section {
  padding: 10px 0;
}

.config-alert {
  display: flex;
  gap: 16px;
  margin-bottom: 25px;
  padding: 20px;
  background: rgba(64, 158, 255, 0.08);
  border: 1px solid var(--gold-dim);

  .alert-icon {
    flex-shrink: 0;
    margin-top: 2px;
  }

  .alert-content {
    flex: 1;

    .alert-title {
      font-family: var(--font-display);
      font-size: 14px;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 8px;
    }

    .alert-text {
      font-family: var(--font-body);
      font-size: 14px;
      color: var(--text-primary);
      line-height: 1.8;

      strong {
        color: var(--text-primary);
      }
    }

    .params-list {
      margin: 10px 0 0 0;
      padding-left: 20px;
      list-style: none;

      li {
        position: relative;
        padding: 4px 0 4px 16px;
        font-family: var(--font-mono);
        font-size: 13px;

        &::before {
          content: '•';
          position: absolute;
          left: 0;
          color: var(--gold-primary);
        }
      }
    }
  }
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-display);
  font-size: 18px;
  color: var(--gold-primary);
  text-transform: uppercase;
  letter-spacing: 2px;
  margin: 0 0 20px 0;

  .title-icon {
    font-size: 20px;
  }
}

.steps-section {
  margin-bottom: 25px;
}

.steps-container {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  padding: 20px;
  background: var(--bg-primary);
  border: 1px solid var(--gold-dim);
  overflow-x: auto;
}

.step-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  min-width: 120px;
  text-align: center;

  .step-indicator {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-bottom: 12px;
  }

  .step-number {
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-secondary);
    border: 2px solid var(--gold-dim);
    color: var(--text-muted);
    font-family: var(--font-display);
    font-size: 14px;
    font-weight: 600;
    border-radius: 0;
    transition: all 0.3s ease;
  }

  .step-line {
    width: 100%;
    height: 2px;
    background: var(--gold-dim);
    margin-top: -36px;
    position: relative;
    z-index: -1;
  }

  .step-content {
    .step-title {
      font-family: var(--font-display);
      font-size: 12px;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 4px;
    }

    .step-desc {
      font-family: var(--font-body);
      font-size: 11px;
      color: var(--text-muted);
      line-height: 1.4;
    }
  }

  &.active {
    .step-number {
      background: var(--gold-primary);
      border-color: var(--gold-primary);
      color: var(--bg-primary);
    }
  }

  &.completed {
    .step-number {
      background: var(--fall);
      border-color: var(--fall);
      color: var(--bg-primary);
    }
  }
}

.model-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: transparent;
  border: 1px solid var(--gold-primary);
  color: var(--gold-primary);
  font-family: var(--font-display);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  cursor: pointer;
  border-radius: 0;
  transition: all 0.3s ease;

  &:hover:not(:disabled) {
    background: var(--gold-primary);
    color: var(--bg-primary);
    box-shadow: 0 0 12px rgba(212, 175, 55, 0.4);
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &.primary {
    background: var(--gold-primary);
    color: var(--bg-primary);

    &:hover:not(:disabled) {
      background: var(--gold-muted);
    }
  }
}

.spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.model-results {
  margin-top: 25px;
  padding-top: 25px;
  border-top: 1px solid var(--gold-dim);
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 20px;

  .result-item {
    display: flex;
    flex-direction: column;
    padding: 15px 20px;
    background: var(--bg-primary);
    border: 1px solid var(--gold-dim);

    label {
      font-family: var(--font-display);
      font-size: 11px;
      color: var(--gold-muted);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 8px;
    }

    .result-value {
      font-family: var(--font-display);
      font-size: 24px;
      color: var(--gold-primary);
      text-transform: uppercase;
      letter-spacing: 1px;
      font-weight: 600;
    }
  }
}

.success-alert {
  display: flex;
  gap: 16px;
  padding: 20px;
  background: rgba(0, 230, 118, 0.08);
  border: 1px solid var(--fall);

  .alert-icon {
    flex-shrink: 0;
    color: var(--fall);
  }

  .alert-content {
    flex: 1;

    .alert-title {
      font-family: var(--font-display);
      font-size: 14px;
      color: var(--fall);
      text-transform: uppercase;
      letter-spacing: 1px;
      margin-bottom: 8px;
    }

    .alert-text {
      font-family: var(--font-body);
      font-size: 14px;
      color: var(--text-primary);
      line-height: 1.6;
    }
  }
}

@media (max-width: 768px) {
  .demo-card {
    padding: 15px;
  }

  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }

  .config-alert {
    flex-direction: column;
    gap: 12px;
  }

  .steps-container {
    flex-direction: column;
    align-items: center;
  }

  .model-actions {
    flex-direction: column;
  }

  .results-grid {
    grid-template-columns: 1fr;
  }
}
</style>
