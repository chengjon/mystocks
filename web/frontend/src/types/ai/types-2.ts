
/**
 * 模型评估结果
 */
export interface ModelEvaluationResult {
  /** 评估ID */
  id: string;

  /** 模型ID */
  modelId: string;

  /** 评估数据集 */
  dataset: EvaluationDataset;

  /** 性能指标 */
  performance: ModelPerformance;

  /** 混淆矩阵 */
  confusionMatrix?: ConfusionMatrix;

  /** 分类报告 */
  classificationReport?: ClassificationReport;

  /** 可视化数据 */
  visualizations?: EvaluationVisualization[];

  /** 评估时间 */
  evaluatedAt: string;
}

/**
 * 评估数据集
 */
export interface EvaluationDataset {
  /** 数据集名称 */
  name: string;

  /** 数据集大小 */
  size: number;

  /** 数据范围 */
  range: {
    /** 起始日期 */
    startDate: string;

    /** 结束日期 */
    endDate: string;
  };
}

/**
 * 混淆矩阵
 */
export interface ConfusionMatrix {
  /** 真阳性 */
  truePositive: number;

  /** 真阴性 */
  trueNegative: number;

  /** 假阳性 */
  falsePositive: number;

  /** 假阴性 */
  falseNegative: number;
}

/**
 * 分类报告
 */
export interface ClassificationReport {
  /** 类别 */
  class: string;

  /** 精确率 */
  precision: number;

  /** 召回率 */
  recall: number;

  /** F1分数 */
  f1Score: number;

  /** 支持度 */
  support: number;
}

/**
 * 评估可视化
 */
export interface EvaluationVisualization {
  /** 可视化类型 */
  type: 'roc_curve' | 'precision_recall_curve' | 'confusion_matrix' | 'feature_importance';

  /** 数据 */
  data: Record<string, unknown>;

  /** 标题 */
  title: string;
}

/**
 * 特征工程配置
 */
export interface FeatureEngineeringConfig {
  /** 特征选择方法 */
  selectionMethod: 'correlation' | 'mutual_info' | 'recursive' | 'none';

  /** 特征数量限制 */
  maxFeatures?: number;

  /** 特征转换 */
  transforms: FeatureTransform[];

  /** 特征组合 */
  combinations?: FeatureCombination[];
}

/**
 * 特征转换
 */
export interface FeatureTransform {
  /** 转换类型 */
  type: 'log' | 'sqrt' | 'box_cox' | 'min_max' | 'z_score' | 'pca';

  /** 应用到的特征 */
  features: string[];

  /** 转换参数 */
  params?: Record<string, unknown>;
}

/**
 * 特征组合
 */
export interface FeatureCombination {
  /** 组合ID */
  id: string;

  /** 组合名称 */
  name: string;

  /** 输入特征 */
  inputFeatures: string[];

  /** 组合方法 */
  method: 'add' | 'multiply' | 'divide' | 'custom';

  /** 自定义函数 */
  customFunction?: string;
}

/**
 * 模型预测请求
 */
export interface ModelPredictionRequest {
  /** 模型ID */
  modelId: string;

  /** 股票代码列表 */
  symbols: string[];

  /** 预测时间范围 */
  horizon: PredictionHorizon;

  /** 是否返回特征重要性 */
  returnFeatureImportance: boolean;

  /** 是否返回概率分布 */
  returnProbability: boolean;

  /** 额外参数 */
  extraParams?: Record<string, unknown>;
}

/**
 * 模型对比结果
 */
export interface ModelComparison {
  /** 对比ID */
  id: string;

  /** 对比的模型ID列表 */
  modelIds: string[];

  /** 对比指标 */
  metrics: ModelPerformance[];

  /** 排名 */
  ranking: {
    modelId: string;
    rank: number;
    score: number;
  }[];

  /** 对比时间 */
  comparedAt: string;

  /** 建议 */
  recommendation: string;
}

