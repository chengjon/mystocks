
/**
 * AI 模型类型
 */
export enum AIModelType {
  /** 价格预测模型 */
  PRICE_PREDICTION = 'price_prediction',

  /** 趋势预测模型 */
  TREND_PREDICTION = 'trend_prediction',

  /** 分类模型 */
  CLASSIFICATION = 'classification',

  /** 回归模型 */
  REGRESSION = 'regression',

  /** 时间序列模型 */
  TIME_SERIES = 'time_series',

  /** 深度学习模型 */
  DEEP_LEARNING = 'deep_learning',

  /** 强化学习模型 */
  REINFORCEMENT_LEARNING = 'reinforcement_learning',
}

/**
 * 预测方向
 */
export enum PredictionDirection {
  /** 看涨 */
  BULLISH = 'bullish',

  /** 看跌 */
  BEARISH = 'bearish',

  /** 中性 */
  NEUTRAL = 'neutral',
}

/**
 * 预测时间范围
 */
export type PredictionHorizon = '1d' | '3d' | '1w' | '2w' | '1M' | '3M';

/**
 * 模型状态
 */
export enum ModelStatus {
  /** 训练中 */
  TRAINING = 'training',

  /** 已训练 */
  TRAINED = 'trained',

  /** 评估中 */
  EVALUATING = 'evaluating',

  /** 已部署 */
  DEPLOYED = 'deployed',

  /** 已停用 */
  DEPRECATED = 'deprecated',

  /** 失败 */
  FAILED = 'failed',
}

/**
 * 预测结果
 */
export interface PredictionResult {
  /** 预测ID */
  id: string;

  /** 模型ID */
  modelId: string;

  /** 股票代码 */
  symbol: string;

  /** 预测时间范围 */
  horizon: PredictionHorizon;

  /** 预测方向 */
  direction: PredictionDirection;

  /** 预测价格（元） */
  predictedPrice: number;

  /** 当前价格（元） */
  currentPrice: number;

  /** 预测涨跌幅（%） */
  predictedChangePercent: number;

  /** 置信度（0-1） */
  confidence: number;

  /** 预测概率分布 */
  probability?: ProbabilityDistribution;

  /** 预测依据 */
  reasoning?: string;

  /** 特征重要性 */
  featureImportance?: FeatureImportance[];

  /** 创建时间 */
  createdAt: string;

  /** 目标日期 */
  targetDate: string;

  /** 实际结果（验证后） */
  actualResult?: ActualResult;
}

/**
 * 概率分布
 */
export interface ProbabilityDistribution {
  /** 看涨概率 */
  bullish: number;

  /** 看跌概率 */
  bearish: number;

  /** 中性概率 */
  neutral: number;
}

/**
 * 特征重要性
 */
export interface FeatureImportance {
  /** 特征名称 */
  feature: string;

  /** 重要性得分（0-1） */
  importance: number;

  /** 特征值 */
  value: number;

  /** 归一化值 */
  normalizedValue?: number;
}

/**
 * 实际结果（用于验证预测）
 */
export interface ActualResult {
  /** 实际价格（元） */
  actualPrice: number;

  /** 实际涨跌幅（%） */
  actualChangePercent: number;

  /** 预测准确度（0-1） */
  accuracy: number;

  /** 预测是否正确 */
  correct: boolean;

  /** 误差（元） */
  error: number;

  /** 验证时间 */
  verifiedAt: string;
}

/**
 * 批量预测结果
 */
export interface BatchPredictions {
  /** 预测结果列表 */
  predictions: PredictionResult[];

  /** 预测统计 */
  statistics: PredictionStatistics;

  /** 生成时间 */
  generatedAt: string;
}

/**
 * 预测统计
 */
export interface PredictionStatistics {
  /** 总预测数 */
  total: number;

  /** 看涨预测数 */
  bullish: number;

  /** 看跌预测数 */
  bearish: number;

  /** 中性预测数 */
  neutral: number;

  /** 平均置信度 */
  avgConfidence: number;

  /** 高置信度预测数（>0.7） */
  highConfidence: number;
}

/**
 * 模型元数据
 */
export interface ModelMetadata {
  /** 模型ID */
  id: string;

  /** 模型名称 */
  name: string;

  /** 模型类型 */
  type: AIModelType;

  /** 模型版本 */
  version: string;

  /** 模型描述 */
  description: string;

  /** 模型状态 */
  status: ModelStatus;

  /** 训练数据信息 */
  trainingData: TrainingDataInfo;

  /** 模型性能指标 */
  performance: ModelPerformance;

  /** 模型超参数 */
  hyperparameters: ModelHyperparameters;

  /** 特征列表 */
  features: ModelFeature[];

  /** 模型架构 */
  architecture?: ModelArchitecture;

  /** 创建者 */
  creator: string;

  /** 创建时间 */
  createdAt: string;

  /** 最后更新时间 */
  updatedAt: string;

  /** 最后训练时间 */
  lastTrainedAt?: string;

  /** 模型文件路径 */
  modelPath?: string;

  /** 模型大小（MB） */
  modelSize?: number;
}

/**
 * 训练数据信息
 */
export interface TrainingDataInfo {
  /** 数据起始日期 */
  startDate: string;

  /** 数据结束日期 */
  endDate: string;

  /** 训练样本数 */
  samples: number;

  /** 特征数 */
  features: number;

  /** 数据源 */
  sources: string[];

  /** 数据版本 */
  dataVersion: string;
}

/**
 * 模型性能指标
 */
export interface ModelPerformance {
  /** 准确率（0-1） */
  accuracy: number;

  /** 精确率（0-1） */
  precision: number;

  /** 召回率（0-1） */
  recall: number;

  /** F1分数（0-1） */
  f1Score: number;

  /** AUC-ROC（0-1） */
  aucRoc: number;

  /** 均方误差（MSE） */
  mse: number;

  /** 均方根误差（RMSE） */
  rmse: number;

  /** 平均绝对误差（MAE） */
  mae: number;

  /** 平均绝对百分比误差（MAPE） */
  mape: number;

  /** R²分数（0-1） */
  r2Score: number;
}

/**
 * 模型超参数
 */
export interface ModelHyperparameters {
  /** 学习率 */
  learningRate?: number;

  /** 批次大小 */
  batchSize?: number;

  /** 迭代次数 */
  epochs?: number;

  /** 优化器 */
  optimizer?: string;

  /** 损失函数 */
  lossFunction?: string;

  /** 正则化系数 */
  regularization?: number;

  /** Dropout比例 */
  dropout?: number;

  /** 其他超参数 */
  [key: string]: unknown;
}

/**
 * 模型特征
 */
export interface ModelFeature {
  /** 特征ID */
  id: string;

  /** 特征名称 */
  name: string;

  /** 特征类型 */
  type: 'numerical' | 'categorical' | 'time_series' | 'technical';

  /** 特征描述 */
  description?: string;

  /** 是否使用 */
  enabled: boolean;

  /** 归一化方法 */
  normalization?: 'min_max' | 'z_score' | 'log' | 'none';

  /** 缺失值处理 */
  missingValueHandling?: 'mean' | 'median' | 'forward_fill' | 'drop';
}

/**
 * 模型架构
 */
export interface ModelArchitecture {
  /** 架构类型 */
  type: 'lstm' | 'gru' | 'transformer' | 'cnn' | 'mlp' | 'custom';

  /** 层数 */
  layers: number;

  /** 隐藏单元数 */
  hiddenUnits: number[];

  /** 激活函数 */
  activation: string;

  /** 架构描述 */
  description: string;
}

/**
 * 模型训练任务
 */
export interface ModelTrainingJob {
  /** 任务ID */
  id: string;

  /** 模型ID */
  modelId: string;

  /** 任务名称 */
  name: string;

  /** 任务状态 */
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';

  /** 训练参数 */
  params: TrainingParams;

  /** 训练进度 */
  progress: TrainingProgress;

  /** 开始时间 */
  startedAt: string;

  /** 完成时间 */
  completedAt?: string;

  /** 错误信息（如果失败） */
  error?: string;
}

/**
 * 训练参数
 */
export interface TrainingParams {
  /** 训练数据比例 */
  trainRatio: number;

  /** 验证数据比例 */
  valRatio: number;

  /** 测试数据比例 */
  testRatio: number;

  /** 交叉验证折数 */
  cvFolds?: number;

  /** 早停耐心值 */
  earlyStoppingPatience?: number;

  /** 是否使用GPU */
  useGPU: boolean;

  /** 随机种子 */
  randomSeed: number;

  /** 其他参数 */
  [key: string]: unknown;
}

/**
 * 训练进度
 */
export interface TrainingProgress {
  /** 当前轮次 */
  currentEpoch: number;

  /** 总轮次 */
  totalEpochs: number;

  /** 进度百分比（0-100） */
  percent: number;

  /** 训练损失 */
  trainLoss: number;

  /** 验证损失 */
  valLoss: number;

  /** 训练准确率 */
  trainAccuracy: number;

  /** 验证准确率 */
  valAccuracy: number;

  /** 预计剩余时间（秒） */
  estimatedTimeRemaining?: number;
}

