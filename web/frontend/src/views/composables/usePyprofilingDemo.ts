import { ref , onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

export function usePyprofilingDemo() {

// Tab 切换
const activeTab = ref('overview')
const tabs = [
  { key: 'overview', label: 'OVERVIEW', icon: '📋' },
  { key: 'prediction', label: 'PREDICTION', icon: '🤖' },
  { key: 'features', label: 'FEATURES', icon: '🔬' },
  { key: 'profiling', label: 'PROFILING', icon: '⚡' },
  { key: 'data', label: 'DATA FILES', icon: '📂' },
  { key: 'api', label: 'API SERVICE', icon: '🌐' },
  { key: 'tech', label: 'TECH STACK', icon: '🔧' }
]

// 模型预测
const modelStep = ref(0)
const modelLoading = ref(false)
const modelResults = ref<{
  rmse: string
  trainSamples: string
  testSamples: string
  featureDim: string
} | null>(null)

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

// Auto-generated: cleanup timers to prevent memory leaks
const _timer_1 = null
onUnmounted(() => {
  if (_timer_1) clearTimeout(_timer_1)
})

  return {
    activeTab,
    tabs,
    modelStep,
    modelLoading,
    modelResults,
    runModelDemo,
    viewModelCode,
    featureSelectionMethods,
    profilingTools,
    profilingCommands,
    dataFiles,
    suggestedAPIs,
    dependencies,
    _timer_1,
  }
}
