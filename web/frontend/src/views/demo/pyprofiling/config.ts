/**
 * Pyprofiling Demo 配置文件
 * 包含所有静态数据和常量定义
 */

export interface TabItem {
  key: string
  label: string
  icon: string
}

export interface FeatureSelectionMethod {
  method: string
  module: string
  description: string
}

export interface ProfilingTool {
  tool: string
  level: string
  usage: string
  output: string
}

export interface ProfilingCommand {
  tool: string
  command: string
  description: string
}

export interface DataFile {
  file: string
  format: string
  description: string
  size: string
}

export interface SuggestedAPI {
  method: string
  endpoint: string
  description: string
  priority: string
}

export interface Dependency {
  package: string
  version: string
  purpose: string
}

// Tab 导航配置
export const TABS: TabItem[] = [
  { key: 'overview', label: '项目概览', icon: '📋' },
  { key: 'prediction', label: '模型预测', icon: '🤖' },
  { key: 'features', label: '特征工程', icon: '🔬' },
  { key: 'profiling', label: '性能分析', icon: '⚡' },
  { key: 'data', label: '数据文件', icon: '📂' },
  { key: 'api', label: 'API 服务', icon: '🌐' },
  { key: 'tech', label: '技术栈', icon: '🔧' }
]

// 特征选择方法
export const FEATURE_SELECTION_METHODS: FeatureSelectionMethod[] = [
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
export const PROFILING_TOOLS: ProfilingTool[] = [
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
export const PROFILING_COMMANDS: ProfilingCommand[] = [
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
export const DATA_FILES: DataFile[] = [
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
export const SUGGESTED_APIS: SuggestedAPI[] = [
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
export const DEPENDENCIES: Dependency[] = [
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
