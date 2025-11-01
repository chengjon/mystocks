<template>
  <div class="pyprofiling-demo">
    <div class="demo-header">
      <h1>📊 PyProfiling 迁移功能演示</h1>
      <p class="subtitle">展示从 PyProfiling 项目迁移的股票预测和性能分析功能</p>
    </div>

    <!-- 功能导航 -->
    <div class="function-nav">
      <el-button
        v-for="tab in tabs"
        :key="tab.key"
        :type="activeTab === tab.key ? 'primary' : ''"
        @click="activeTab = tab.key"
      >
        {{ tab.icon }} {{ tab.label }}
      </el-button>
    </div>

    <!-- 1. 项目概览 -->
    <el-card v-show="activeTab === 'overview'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>📋 项目概览</span>
          <el-tag type="success">已迁移</el-tag>
        </div>
      </template>

      <div class="overview-section">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="项目名称">
            PyProfiling - 股票预测与性能分析工具包
          </el-descriptions-item>
          <el-descriptions-item label="主要用途">
            使用 LightGBM 预测股票价格 + Python 性能分析
          </el-descriptions-item>
          <el-descriptions-item label="数据源">
            通达信（Tongdaxin）二进制 .day 文件
          </el-descriptions-item>
          <el-descriptions-item label="核心模型">
            LightGBM Regressor（GBDT 回归）
          </el-descriptions-item>
          <el-descriptions-item label="特征工程">
            滚动窗口特征（10步 × 6特征 = 60列）
          </el-descriptions-item>
          <el-descriptions-item label="评估指标">
            RMSE（均方根误差）
          </el-descriptions-item>
        </el-descriptions>

        <div style="margin-top: 20px">
          <h3>🔧 核心功能模块</h3>
          <el-row :gutter="20" style="margin-top: 15px">
            <el-col :span="8">
              <el-card class="feature-card">
                <h4>📈 股票价格预测</h4>
                <ul>
                  <li>通达信数据解析</li>
                  <li>滚动窗口特征工程</li>
                  <li>LightGBM 模型训练</li>
                  <li>预测结果可视化</li>
                </ul>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="feature-card">
                <h4>🎯 特征选择</h4>
                <ul>
                  <li>RFE（递归特征消除）</li>
                  <li>Mutual Information</li>
                  <li>LinearSVC 特征选择</li>
                  <li>ExtraTreesClassifier</li>
                </ul>
              </el-card>
            </el-col>
            <el-col :span="8">
              <el-card class="feature-card">
                <h4>⚡ 性能分析</h4>
                <ul>
                  <li>cProfile 函数分析</li>
                  <li>line_profiler 逐行分析</li>
                  <li>memory_profiler 内存分析</li>
                  <li>timeit 执行时间测量</li>
                </ul>
              </el-card>
            </el-col>
          </el-row>
        </div>

        <el-alert
          title="数据流程"
          type="info"
          :closable="false"
          style="margin-top: 20px"
        >
          <div style="line-height: 2">
            <strong>完整数据流程：</strong><br>
            通达信 .day 文件 → 二进制解析（32字节结构）→ OHLCV DataFrame →
            滚动窗口特征工程 → CSV 数据集 → LightGBM 训练 → 预测结果
          </div>
        </el-alert>
      </div>
    </el-card>

    <!-- 2. 模型预测演示 -->
    <el-card v-show="activeTab === 'prediction'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>🤖 股票价格预测模型</span>
          <el-tag type="warning">功能展示</el-tag>
        </div>
      </template>

      <div class="prediction-section">
        <el-alert
          title="模型配置"
          type="info"
          :closable="false"
          style="margin-bottom: 20px"
        >
          <div>
            <strong>LightGBM 超参数：</strong>
            <ul style="margin-top: 10px; line-height: 1.8">
              <li>num_leaves=25, learning_rate=0.2, n_estimators=70</li>
              <li>max_depth=15, bagging_fraction=0.8, feature_fraction=0.8</li>
              <li>reg_lambda=0.9（L2 正则化）</li>
            </ul>
          </div>
        </el-alert>

        <h3>模型训练流程</h3>
        <el-steps :active="modelStep" finish-status="success" style="margin: 20px 0">
          <el-step title="数据加载" description="读取通达信 .day 文件" />
          <el-step title="特征工程" description="生成滚动窗口特征（10步×6列）" />
          <el-step title="数据分割" description="80% 训练集 / 20% 测试集" />
          <el-step title="模型训练" description="LightGBM GBDT 回归训练" />
          <el-step title="预测评估" description="计算 RMSE 并绘制预测曲线" />
        </el-steps>

        <div class="model-actions" style="margin-top: 20px">
          <el-button type="primary" @click="runModelDemo" :loading="modelLoading">
            运行模型演示
          </el-button>
          <el-button @click="viewModelCode">
            查看代码
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
            模型使用历史 OHLCV 数据的滚动窗口特征，预测下一个交易日的收盘价。
            预测结果已保存为 predict.png 和 predict2.png 图片。
          </el-alert>
        </div>
      </div>
    </el-card>

    <!-- 3. 特征工程 -->
    <el-card v-show="activeTab === 'features'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>🔬 特征工程与特征选择</span>
          <el-tag type="info">技术说明</el-tag>
        </div>
      </template>

      <div class="features-section">
        <h3>滚动窗口特征生成</h3>
        <el-descriptions :column="1" border style="margin-top: 15px">
          <el-descriptions-item label="窗口大小（step）">
            10 个交易日
          </el-descriptions-item>
          <el-descriptions-item label="原始特征数">
            6 列（code, tradeDate, open, high, low, close, amount, vol）
          </el-descriptions-item>
          <el-descriptions-item label="生成特征数">
            10步 × 6特征 = 60 列特征向量
          </el-descriptions-item>
          <el-descriptions-item label="目标变量">
            nextClose（下一日收盘价，使用 shift(-1) 生成）
          </el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 30px">特征选择算法</h3>
        <el-table :data="featureSelectionMethods" stripe style="margin-top: 15px">
          <el-table-column prop="method" label="方法" width="200" />
          <el-table-column prop="module" label="模块路径" width="300" />
          <el-table-column prop="description" label="说明" />
          <el-table-column label="状态" width="120">
            <template #default>
              <el-tag type="warning">独立示例</el-tag>
            </template>
          </el-table-column>
        </el-table>

        <el-alert
          title="集成说明"
          type="warning"
          :closable="false"
          style="margin-top: 20px"
        >
          特征选择模块目前为独立示例，未与主预测管道集成。
          如需使用，需从 featselection/ 目录导入并手动集成到 model.py 中。
        </el-alert>
      </div>
    </el-card>

    <!-- 4. 性能分析工具 -->
    <el-card v-show="activeTab === 'profiling'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>⚡ Python 性能分析工具</span>
          <el-tag type="info">工具集</el-tag>
        </div>
      </template>

      <div class="profiling-section">
        <h3>性能分析工具对比</h3>
        <el-table :data="profilingTools" stripe style="margin-top: 15px">
          <el-table-column prop="tool" label="工具" width="180" />
          <el-table-column prop="level" label="分析粒度" width="120" />
          <el-table-column prop="usage" label="使用方法" />
          <el-table-column prop="output" label="输出内容" />
        </el-table>

        <h3 style="margin-top: 30px">性能分析示例命令</h3>
        <div class="command-examples">
          <el-card v-for="cmd in profilingCommands" :key="cmd.tool" class="command-card">
            <h4>{{ cmd.tool }}</h4>
            <el-input
              v-model="cmd.command"
              type="textarea"
              :rows="3"
              readonly
            >
              <template #prepend>命令</template>
            </el-input>
            <p style="margin-top: 10px; color: #666; font-size: 13px">
              {{ cmd.description }}
            </p>
          </el-card>
        </div>

        <el-alert
          title="性能优化流程"
          type="success"
          :closable="false"
          style="margin-top: 20px"
        >
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
          <span>🌐 Flask API 服务</span>
          <el-tag type="warning">最小实现</el-tag>
        </div>
      </template>

      <div class="api-section">
        <el-alert
          title="API 状态说明"
          type="warning"
          :closable="false"
        >
          <div>
            当前 <code>server.py</code> 仅实现了欢迎页面，未暴露 ML 预测端点。
            模型预测逻辑仅存在于 <code>model.py</code> 作为独立脚本。
          </div>
        </el-alert>

        <h3 style="margin-top: 20px">现有端点</h3>
        <el-descriptions :column="1" border style="margin-top: 15px">
          <el-descriptions-item label="服务地址">
            http://localhost:5000
          </el-descriptions-item>
          <el-descriptions-item label="端点">
            GET /
          </el-descriptions-item>
          <el-descriptions-item label="返回">
            "欢迎来到通达信数据分析的世界"
          </el-descriptions-item>
        </el-descriptions>

        <h3 style="margin-top: 30px">建议增强的 API 端点</h3>
        <el-table :data="suggestedAPIs" stripe style="margin-top: 15px">
          <el-table-column prop="method" label="方法" width="100" />
          <el-table-column prop="endpoint" label="端点" width="250" />
          <el-table-column prop="description" label="功能说明" />
          <el-table-column label="优先级" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.priority === '高' ? 'danger' : 'info'">
                {{ scope.row.priority }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <el-alert
          title="集成建议"
          type="success"
          :closable="false"
          style="margin-top: 20px"
        >
          <div style="line-height: 2">
            <strong>推荐将 PyProfiling 功能集成到本项目：</strong><br>
            1. 在后端 API 中创建 <code>/api/ml/predict</code> 端点<br>
            2. 集成 LightGBM 模型训练和预测逻辑<br>
            3. 支持通达信数据自动解析和特征工程<br>
            4. 提供性能分析 API 用于模型优化监控
          </div>
        </el-alert>
      </div>
    </el-card>

    <!-- 7. 技术栈与依赖 -->
    <el-card v-show="activeTab === 'tech'" class="demo-card">
      <template #header>
        <div class="card-header">
          <span>🔧 技术栈与依赖</span>
        </div>
      </template>

      <div class="tech-section">
        <h3>核心依赖包</h3>
        <el-table :data="dependencies" stripe style="margin-top: 15px">
          <el-table-column prop="package" label="包名" width="200" />
          <el-table-column prop="version" label="版本" width="150" />
          <el-table-column prop="purpose" label="用途" />
        </el-table>

        <h3 style="margin-top: 30px">安装说明</h3>
        <el-card class="install-card">
          <h4>环境要求</h4>
          <ul>
            <li>Python 3.6+</li>
            <li>pip（建议升级到最新版本）</li>
          </ul>
          <h4 style="margin-top: 15px">安装命令</h4>
          <el-input
            value="pip install -r requirements.txt"
            readonly
            style="margin-top: 10px"
          >
            <template #prepend>命令</template>
          </el-input>
          <p style="margin-top: 10px; color: #666; font-size: 13px">
            如遇到安装问题，可先执行：<br>
            <code>python -m pip install --force-reinstall pip setuptools</code>
          </p>
        </el-card>

        <h3 style="margin-top: 30px">中文字体配置</h3>
        <el-alert
          title="Matplotlib 中文显示"
          type="info"
          :closable="false"
        >
          <div>
            项目使用 SimHei 字体显示中文标签。如遇到乱码：<br>
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
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// Tab 切换
const activeTab = ref('overview')
const tabs = [
  { key: 'overview', label: '项目概览', icon: '📋' },
  { key: 'prediction', label: '模型预测', icon: '🤖' },
  { key: 'features', label: '特征工程', icon: '🔬' },
  { key: 'profiling', label: '性能分析', icon: '⚡' },
  { key: 'data', label: '数据文件', icon: '📂' },
  { key: 'api', label: 'API 服务', icon: '🌐' },
  { key: 'tech', label: '技术栈', icon: '🔧' }
]

// 模型预测
const modelStep = ref(0)
const modelLoading = ref(false)
const modelResults = ref(null)

const runModelDemo = async () => {
  modelLoading.value = true
  modelStep.value = 0

  // 模拟模型训练流程
  for (let i = 0; i <= 4; i++) {
    await new Promise(resolve => setTimeout(resolve, 800))
    modelStep.value = i + 1
  }

  // 模拟结果
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

// 特征选择方法
const featureSelectionMethods = [
  {
    method: 'RFE',
    module: 'featselection/rfe.py',
    description: '递归特征消除，逐步移除不重要特征'
  },
  {
    method: 'Mutual Information',
    module: 'featselection/mutualinfoclassif.py',
    description: '互信息特征选择，衡量特征与目标的相关性'
  },
  {
    method: 'LinearSVC',
    module: 'featselection/linearsvc.py',
    description: '基于线性 SVM 的特征选择'
  },
  {
    method: 'ExtraTreesClassifier',
    module: 'featselection/extratreesclassifier.py',
    description: '极端随机树特征重要性'
  },
  {
    method: 'SelectPercentile',
    module: 'featselection/selectpercentile.py',
    description: '选择得分最高的百分比特征'
  }
]

// 性能分析工具
const profilingTools = [
  {
    tool: 'time',
    level: '粗粒度',
    usage: 'time.time() 前后计时',
    output: '总执行时间'
  },
  {
    tool: 'timeit',
    level: '语句级',
    usage: 'python -m timeit -n 5 -r 5',
    output: '多次执行的最优时间'
  },
  {
    tool: 'cProfile',
    level: '函数级',
    usage: 'python -m cProfile -s cumulative',
    output: '每个函数的调用次数和累计时间'
  },
  {
    tool: 'line_profiler',
    level: '行级',
    usage: 'kernprof -l -v script.py',
    output: '每行代码的执行次数和时间'
  },
  {
    tool: 'memory_profiler',
    level: '行级',
    usage: 'python -m memory_profiler',
    output: '每行代码的内存占用和增量'
  }
]

// 性能分析命令示例
const profilingCommands = [
  {
    tool: 'cProfile 函数分析',
    command: 'python -m cProfile -s cumulative -o profile.stats model.py',
    description: '生成性能统计文件，可用 pstats 模块查看'
  },
  {
    tool: 'line_profiler 逐行分析',
    command: '# 1. 在函数上添加 @profile 装饰器\n# 2. 运行命令\nkernprof -l -v model.py',
    description: '输出每行代码的执行时间和次数'
  },
  {
    tool: 'memory_profiler 内存分析',
    command: 'python -m memory_profiler model.py\n# 可视化：\nmprof run model.py\nmprof plot',
    description: '分析内存占用情况，需要 matplotlib 用于可视化'
  }
]

// 数据文件
const dataFiles = [
  {
    file: 'data/sh000001.day',
    format: '通达信二进制',
    description: '上证指数原始数据（32字节结构）',
    size: '原始数据源'
  },
  {
    file: 'data/sh000001.csv',
    format: 'CSV',
    description: '转换后的 OHLCV 数据',
    size: '中间数据'
  },
  {
    file: 'data/sh000001_3.csv',
    format: 'CSV',
    description: '3步滚动窗口特征',
    size: '特征数据'
  },
  {
    file: 'data/sh000001_10.csv',
    format: 'CSV',
    description: '10步滚动窗口特征（默认）',
    size: '模型训练数据'
  }
]

// 建议的 API 端点
const suggestedAPIs = [
  {
    method: 'POST',
    endpoint: '/api/ml/train',
    description: '训练新的 LightGBM 模型',
    priority: '高'
  },
  {
    method: 'POST',
    endpoint: '/api/ml/predict',
    description: '使用训练好的模型进行预测',
    priority: '高'
  },
  {
    method: 'GET',
    endpoint: '/api/ml/model/info',
    description: '获取模型信息（RMSE、参数等）',
    priority: '中'
  },
  {
    method: 'POST',
    endpoint: '/api/ml/features/generate',
    description: '生成滚动窗口特征',
    priority: '中'
  },
  {
    method: 'GET',
    endpoint: '/api/profiling/report',
    description: '获取性能分析报告',
    priority: '低'
  }
]

// 核心依赖
const dependencies = [
  { package: 'LightGBM', version: '3.3.1', purpose: 'GBDT 梯度提升框架' },
  { package: 'scikit-learn', version: '0.24.2', purpose: '特征选择和模型工具' },
  { package: 'pandas', version: '1.1.5', purpose: '数据处理和分析' },
  { package: 'numpy', version: '-', purpose: '数值计算' },
  { package: 'matplotlib', version: '3.3.4', purpose: '结果可视化' },
  { package: 'seaborn', version: '0.11.2', purpose: '高级可视化' },
  { package: 'Flask', version: '2.0.2', purpose: 'Web 框架（API 服务）' },
  { package: 'line-profiler', version: '3.4.0', purpose: '逐行性能分析' },
  { package: 'memory-profiler', version: '-', purpose: '内存占用分析' }
]
</script>

<style scoped>
.pyprofiling-demo {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.demo-header {
  text-align: center;
  margin-bottom: 30px;
}

.demo-header h1 {
  font-size: 32px;
  margin-bottom: 10px;
  color: #409eff;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.function-nav {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.demo-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.overview-section,
.prediction-section,
.features-section,
.profiling-section,
.data-section,
.api-section,
.tech-section {
  padding: 10px 0;
}

.feature-card {
  height: 100%;
  background: #f8f9fa;
}

.feature-card h4 {
  margin-top: 0;
  color: #409eff;
  margin-bottom: 15px;
}

.feature-card ul {
  margin: 0;
  padding-left: 20px;
  line-height: 2;
}

.model-actions {
  display: flex;
  gap: 10px;
}

.command-examples {
  display: grid;
  grid-template-columns: 1fr;
  gap: 15px;
  margin-top: 15px;
}

.command-card {
  background: #f8f9fa;
}

.command-card h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #409eff;
}

.install-card {
  background: #f8f9fa;
  margin-top: 15px;
}

.install-card h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #409eff;
}

.install-card ul {
  margin: 0;
  padding-left: 20px;
  line-height: 1.8;
}

code {
  background: #f0f0f0;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}
</style>
