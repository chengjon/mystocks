<template>
  <div class="pyprofiling-demo">

    <div class="page-header">
      <h1 class="page-title">PYPROFILING DEMO</h1>
      <p class="page-subtitle">STOCK PREDICTION | FEATURE ENGINEERING | PERFORMANCE ANALYSIS</p>
    </div>

    <div class="function-nav">
      <el-button
        v-for="(tab, _idx) in tabs"
        :key="tab.key"
        type="activeTab === tab.key ? 'solid' : 'outline'"
        @click="activeTab = tab.key"
      >
        {{ tab.icon }} {{ tab.label }}
      </el-button>
    </div>

    <el-card v-show="activeTab === 'overview'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>PROJECT OVERVIEW</span>
          <el-tag type="success">MIGRATED</el-tag>
        </div>
      </template>

      <div class="overview-section">
        <el-descriptions :column="2" border class="descriptions">
          <el-descriptions-item label="PROJECT NAME">
            PyProfiling - Stock Prediction & Performance Analysis Toolkit
          </el-descriptions-item>
          <el-descriptions-item label="PURPOSE">
            LightGBM Stock Price Prediction + Python Performance Analysis
          </el-descriptions-item>
          <el-descriptions-item label="DATA SOURCE">
            Tongdaxin Binary .day Files
          </el-descriptions-item>
          <el-descriptions-item label="CORE MODEL">
            LightGBM Regressor (GBDT Regression)
          </el-descriptions-item>
          <el-descriptions-item label="FEATURE ENGINEERING">
            Rolling Window Features (10 steps × 6 features = 60 columns)
          </el-descriptions-item>
          <el-descriptions-item label="EVALUATION METRIC">
            RMSE (Root Mean Square Error)
          </el-descriptions-item>
        </el-descriptions>

        <div style="margin-top: 20px">
          <h3>CORE FEATURES</h3>
          <div class="features-grid">
            <el-card :hoverable="true">
              <h4>STOCK PRICE PREDICTION</h4>
              <ul>
                <li>Tongdaxin Data Parsing</li>
                <li>Rolling Window Feature Engineering</li>
                <li>LightGBM Model Training</li>
                <li>Prediction Visualization</li>
              </ul>
            </el-card>

            <el-card :hoverable="true">
              <h4>FEATURE SELECTION</h4>
              <ul>
                <li>RFE (Recursive Feature Elimination)</li>
                <li>Mutual Information</li>
                <li>LinearSVC Feature Selection</li>
                <li>ExtraTreesClassifier</li>
              </ul>
            </el-card>

            <el-card :hoverable="true">
              <h4>PERFORMANCE ANALYSIS</h4>
              <ul>
                <li>cProfile Function Analysis</li>
                <li>line_profiler Line-by-line Analysis</li>
                <li>memory_profiler Memory Analysis</li>
                <li>timeit Execution Time Measurement</li>
              </ul>
            </el-card>
          </div>
        </div>
      </div>
      </el-card>

    <!-- 2. 模型预测演示 -->
    <el-card v-show="activeTab === 'prediction'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>STOCK PRICE PREDICTION MODEL</span>
          <el-tag type="warning">FEATURE DEMO</el-tag>
        </div>
      </template>

      <div class="prediction-section">
        <h3>MODEL CONFIGURATION</h3>
        <div class="config-box" style="background: var(--bg-secondary); padding: 15px; border-radius: 4px; margin-bottom: 20px;">
          <strong>LightGBM Hyperparameters:</strong>
          <ul style="margin-top: 10px; line-height: 1.8">
            <li>num_leaves=25, learning_rate=0.2, n_estimators=70</li>
            <li>max_depth=15, bagging_fraction=0.8, feature_fraction=0.8</li>
            <li>reg_lambda=0.9 (L2 Regularization)</li>
          </ul>
        </div>

        <h3>MODEL TRAINING PIPELINE</h3>
        <el-steps :active="modelStep" finish-status="success" style="margin: 20px 0" class="steps">
          <el-step title="DATA LOADING" description="Read Tongdaxin .day files" />
          <el-step title="FEATURE ENGINEERING" description="Generate rolling window features (10 steps × 6 columns)" />
          <el-step title="DATA SPLIT" description="80% Train / 20% Test" />
          <el-step title="MODEL TRAINING" description="LightGBM GBDT Regression" />
          <el-step title="PREDICTION" description="Calculate RMSE & Plot Curves" />
        </el-steps>

        <div class="model-actions" style="margin-top: 20px">
          <el-button type="primary" @click="runModelDemo" :loading="modelLoading">
            RUN MODEL DEMO
          </el-button>
          <el-button type="info" @click="viewModelCode">
            VIEW CODE
          </el-button>
        </div>

        <!-- 模型结果展示 -->
        <div v-if="modelResults" class="model-results" style="margin-top: 20px">
          <h3>预测结果</h3>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="RMSE（均方根误差）">
              {{ modelResults.rmse }}
            </el-descriptions-item>
            <el-descriptions-item label="训练样本数">
              {{ modelResults.trainSamples }}
            </el-descriptions-item>
            <el-descriptions-item label="测试样本数">
              {{ modelResults.testSamples }}
            </el-descriptions-item>
            <el-descriptions-item label="特征维度">
              {{ modelResults.featureDim }}
            </el-descriptions-item>
          </el-descriptions>

          <el-alert
            title="预测结果说明"
            type="success"
            :closable="false"
            style="margin-top: 15px"
          >
            预测结果已保存为 predict.png 和 predict2.png 图片。
          </el-alert>
        </div>
      </div>
    </el-card>

    <!-- 3. 特征工程 -->
    <el-card v-show="activeTab === 'features'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>FEATURE ENGINEERING & SELECTION</span>
          <el-tag type="info">TECHNICAL</el-tag>
        </div>
      </template>

      <div class="features-section">
        <h3>ROLLING WINDOW FEATURE GENERATION</h3>
        <el-descriptions :column="1" border style="margin-top: 15px" class="descriptions">
          <el-descriptions-item label="WINDOW SIZE (step)">
            10 Trading Days
          </el-descriptions-item>
          <el-descriptions-item label="ORIGINAL FEATURES">
            6 Columns (code, tradeDate, open, high, low, close, amount, vol)
          </el-descriptions-item>
          <el-descriptions-item label="GENERATED FEATURES">
            10 steps × 6 features = 60 Column Feature Vector
          </el-descriptions-item>
          <el-descriptions-item label="TARGET VARIABLE">
            nextClose (Next Day Close Price, generated with shift(-1))
          </el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 30px">FEATURE SELECTION ALGORITHMS</h3>
        <el-table :data="featureSelectionMethods" style="margin-top: 15px">
          <el-table-column prop="method" label="METHOD" width="200" />
          <el-table-column prop="module" label="MODULE PATH" width="300" />
          <el-table-column prop="description" label="DESCRIPTION" />
          <el-table-column label="STATUS" width="120">
            <template #default>
              <el-tag type="warning">INDEPENDENT</el-tag>
            </template>
          </el-table-column>
        </el-table>

        <el-alert type="warning" :closable="false" style="margin-top: 15px">
          <template #title>INTEGRATION NOTE</template>
          Feature selection modules are currently standalone examples and not integrated with the main prediction pipeline. To use them, import from featselection/ directory and manually integrate into model.py.
        </el-alert>
      </div>
    </el-card>

    <!-- 4. 性能分析工具 -->
    <el-card v-show="activeTab === 'profiling'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>PYTHON PERFORMANCE ANALYSIS TOOLS</span>
          <el-tag type="info">TOOLKIT</el-tag>
        </div>
      </template>

      <div class="profiling-section">
        <h3>PERFORMANCE ANALYSIS TOOLS COMPARISON</h3>
        <el-table :data="profilingTools" style="margin-top: 15px">
          <el-table-column prop="tool" label="TOOL" width="180" />
          <el-table-column prop="level" label="GRANULARITY" width="120" />
          <el-table-column prop="usage" label="USAGE" />
          <el-table-column prop="output" label="OUTPUT" />
        </el-table>

        <h3 style="margin-top: 30px">PERFORMANCE ANALYSIS EXAMPLE COMMANDS</h3>
        <div class="command-examples">
          <el-card v-for="cmd in profilingCommands" :key="cmd.tool" :hoverable="true" class="command-card">
            <h4>{{ cmd.tool }}</h4>
            <el-input
              v-model="cmd.command"
              type="textarea"
              :rows="3"
              readonly
            >
              <template #prepend>COMMAND</template>
            </el-input>
            <p style="margin-top: 10px; color: var(--fg-muted); font-size: 13px">
              {{ cmd.description }}
            </p>
          </el-card>
        </div>

        <el-alert type="info" :closable="false" style="margin-top: 20px">
          <template #title>
            <strong>PERFORMANCE OPTIMIZATION WORKFLOW</strong>
          </template>
          <div style="line-height: 2">
            <strong>推荐工作流：</strong><br>
            1. 使用 <code>cProfile</code> 快速定位性能瓶颈函数<br>
            2. 使用 <code>line_profiler</code> 对瓶颈函数进行逐行分析<br>
            3. 使用 <code>memory_profiler</code> 检查内存占用问题<br>
            4. 使用 <code>timeit</code> 对比优化前后的执行时间
          </div>
        </el-alert>
      </div>
    </el-card>

    <!-- 5. 数据文件说明 -->
    <el-card v-show="activeTab === 'data'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>📂 数据文件说明</span>
          <el-tag>通达信格式</el-tag>
        </div>
      </template>

      <div class="data-section">
        <h3>项目数据文件</h3>
        <el-table :data="dataFiles" stripe style="margin-top: 15px">
          <el-table-column prop="file" label="文件路径" width="250" />
          <el-table-column prop="format" label="格式" width="150" />
          <el-table-column prop="description" label="说明" />
          <el-table-column prop="size" label="用途" width="200" />
        </el-table>

        <h3 style="margin-top: 30px">通达信二进制格式解析</h3>
        <el-descriptions :column="1" border style="margin-top: 15px">
          <el-descriptions-item label="文件格式">
            32字节固定结构（struct）
          </el-descriptions-item>
          <el-descriptions-item label="解析方法">
            struct.unpack('IIIIIfII', ...)
          </el-descriptions-item>
          <el-descriptions-item label="价格字段">
            open/high/low/close 存储为整数，需除以 100 转换
          </el-descriptions-item>
          <el-descriptions-item label="输出列">
            ['code', 'tradeDate', 'open', 'high', 'low', 'close', 'amount', 'vol']
          </el-descriptions-item>
        </el-descriptions>

        <el-alert
          title="数据处理流程"
          type="info"
          :closable="false"
          style="margin-top: 20px"
        >
          <div style="line-height: 2">
            <strong>数据转换步骤：</strong><br>
            1. <code>utils.read_tdx_day_file()</code> 读取 .day 二进制文件<br>
            2. 解析为 OHLCV DataFrame（sh000001.csv）<br>
            3. <code>utils.gen_model_datum(step=10)</code> 生成滚动窗口特征<br>
            4. 输出特征文件（sh000001_10.csv）用于模型训练
          </div>
        </el-alert>
      </div>
    </el-card>

    <!-- 6. API 服务 -->
    <el-card v-show="activeTab === 'api'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>FLASK API SERVICE</span>
          <el-tag type="warning">MINIMAL</el-tag>
        </div>
      </template>

      <div class="api-section">
        <h3>API STATUS</h3>
        <el-alert type="warning" :closable="false" style="margin-bottom: 20px">
          Current <code>server.py</code> only implements welcome page, no ML prediction endpoints exposed. Model prediction logic only exists in <code>model.py</code> as standalone script.
        </el-alert>

        <h3 style="margin-top: 20px">EXISTING ENDPOINTS</h3>
        <el-descriptions :column="1" border style="margin-top: 15px" class="descriptions">
          <el-descriptions-item label="SERVICE ADDRESS">
            http://localhost:5000
          </el-descriptions-item>
          <el-descriptions-item label="ENDPOINT">
            GET /
          </el-descriptions-item>
          <el-descriptions-item label="RESPONSE">
            "Welcome to Tongdaxin Data Analysis"
          </el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 30px">SUGGESTED API ENDPOINTS</h3>
        <el-table :data="suggestedAPIs" style="margin-top: 15px">
          <el-table-column prop="method" label="METHOD" width="100" />
          <el-table-column prop="endpoint" label="ENDPOINT" width="250" />
          <el-table-column prop="description" label="DESCRIPTION" />
          <el-table-column label="PRIORITY" width="100">
            <template #default="scope">
              <el-tag type="scope.row.priority === '高' ? 'danger' : 'info'">
                {{ scope.row.priority }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <h3>INTEGRATION RECOMMENDATIONS</h3>
        <el-alert type="info" :closable="false" style="margin-top: 20px">
          <div style="line-height: 2">
            <strong>Recommended PyProfiling Integration:</strong><br>
            1. Create <code>/api/ml/predict</code> endpoint in backend API<br>
            2. Integrate LightGBM model training and prediction logic<br>
            3. Support Tongdaxin data auto-parsing and feature engineering<br>
            4. Provide performance analysis API for model optimization monitoring
          </div>
        </el-alert>
      </div>
    </el-card>

    <!-- 7. 技术栈与依赖 -->
    <el-card v-show="activeTab === 'tech'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>TECH STACK & DEPENDENCIES</span>
        </div>
      </template>

      <div class="tech-section">
        <h3>CORE DEPENDENCIES</h3>
        <el-table :data="dependencies" style="margin-top: 15px">
          <el-table-column prop="package" label="PACKAGE" width="200" />
          <el-table-column prop="version" label="VERSION" width="150" />
          <el-table-column prop="purpose" label="PURPOSE" />
        </el-table>

        <h3 style="margin-top: 30px">INSTALLATION GUIDE</h3>
        <el-card :hoverable="true" class="install-card">
          <h4>ENVIRONMENT REQUIREMENTS</h4>
          <ul>
            <li>Python 3.6+</li>
            <li>pip (recommend upgrading to latest)</li>
          </ul>
          <h4 style="margin-top: 15px">INSTALL COMMAND</h4>
          <el-input
            value="pip install -r requirements.txt"
            readonly
            style="margin-top: 10px"
          >
            <template #prepend>COMMAND</template>
          </el-input>
          <p style="margin-top: 10px; color: var(--fg-muted); font-size: 13px">
            If you encounter installation issues, try:<br>
            <code style="display: block; margin-top: 10px">
              python -m pip install --force-reinstall pip setuptools
            </code>
          </p>
        </el-card>

        <h3 style="margin-top: 30px">CHINESE FONT CONFIGURATION</h3>
        <el-alert type="info" :closable="false" style="margin-top: 15px">
          <template #title>MATPLOTLIB CHINESE DISPLAY</template>
          <div>
            Project uses SimHei font for Chinese labels. If you encounter garbled text:<br>
            <code style="display: block; margin-top: 10px">
              plt.rcParams['font.sans-serif'] = ['SimHei']<br>
              plt.rcParams['axes.unicode_minus'] = False
            </code>
          </div>
        </el-alert>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { usePyprofilingDemo } from './composables/usePyprofilingDemo'

const { activeTab, tabs, modelStep, modelLoading, modelResults, runModelDemo, viewModelCode, featureSelectionMethods, profilingTools, profilingCommands, dataFiles, suggestedAPIs, dependencies, _timer_1 } = usePyprofilingDemo()
</script>

<style scoped>
@import "./styles/PyprofilingDemo.css";
</style>
