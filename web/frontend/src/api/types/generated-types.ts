// Auto-generated TypeScript types from backend Pydantic models
// Generated at: 2025-12-29T18:10:31.916336

// API Response Types
export interface APIResponse {

  success?: boolean;
  data?: any | null;
  error?: ErrorDetail | null;
  timestamp?: string;
}

export interface ActiveAlert {

  id?: number;
  name?: string;
  metricType?: string;
  thresholdValue?: number;
}

export interface BacktestRequest {

  strategyName?: string;
  symbols?: string[];
  startDate?: string;
  endDate?: string;
  initialCapital?: number;
  parameters?: Record<string, any>;
}

export interface BacktestResponse {

  taskId?: string;
  status?: string;
  summary?: BacktestResultSummary | null;
  equityCurve?: Record<string, any>[];
  trades?: BacktestTrade[];
  errorMessage?: string | null;
}

export interface BacktestResultSummary {

  totalReturn?: number;
  annualizedReturn?: number;
  maxDrawdown?: number;
  sharpeRatio?: number;
  winRate?: number;
  totalTrades?: number;
}

export interface BacktestTrade {

  symbol?: string;
  entryDate?: string;
  exitDate?: string;
  entryPrice?: number;
  exitPrice?: number;
  quantity?: number;
  pnl?: number;
  returnPct?: number;
}

export interface BatchOperation {

  operation?: string;
  data?: Record<string, any>;
  id?: string | null;
}

export interface BatchOperationRequest {

  operations?: BatchOperation[];
}

export interface BatchOperationResult {

  id?: string | null;
  success?: boolean;
  data?: any | null;
  error?: string | null;
}

export interface BetaRequest {

  entityType?: string;
  entityId?: number;
  marketIndex?: string;
}

export interface BetaResult {

  beta?: number | null;
  correlation?: number | null;
  entityType?: string | null;
  entityId?: number | null;
  marketIndex?: string | null;
}

export interface ChipRaceItem {

  symbol?: string;
  name?: string;
  raceAmount?: number;
  changePercent?: number;
}

export interface ChipRaceRequest {

  raceType: string; // Default: 'open'
  tradeDate?: string | null;
  minRaceAmount?: number | null;
  limit: number; // Default: 100
}

export interface ChipRaceResponse {

  id?: number;
  symbol?: string;
  name?: string;
  tradeDate?: string;
  raceType?: string;
  latestPrice?: number;
  changePercent?: number;
  prevClose?: number;
  openPrice?: number;
  raceAmount?: number;
  raceAmplitude?: number;
  raceCommission?: number;
  raceTransaction?: number;
  raceRatio?: number;
  createdAt: string | null; // Default: None
}

export interface CurrencyField {

  amount?: string;
}

export interface DateField {

  date?: string;
}

export interface ETFDataRequest {

  symbol?: string | null;
  keyword?: string | null;
  limit: number; // Default: 50
}

export interface ETFDataResponse {

  id?: number;
  symbol?: string;
  name?: string;
  tradeDate?: string;
  latestPrice?: number;
  changePercent?: number;
  changeAmount?: number;
  volume?: number;
  amount?: number;
  openPrice?: number;
  highPrice?: number;
  lowPrice?: number;
  prevClose?: number;
  turnoverRate?: number;
  totalMarketCap?: number;
  circulatingMarketCap?: number;
  createdAt: string | null; // Default: None
}

export interface ErrorDetail {

  errorCode?: string;
  errorMessage?: string;
  details?: Record<string, any> | null;
}

export interface ErrorResponse {

  error?: string;
  message?: string;
  detail?: string | null;
}

export interface FeatureGenerationRequest {

  stockCode?: string;
  market: string; // Default: 'sh'
  step: number; // Default: 10
  includeIndicators: boolean; // Default: True
}

export interface FeatureGenerationResponse {

  success?: boolean;
  message?: string;
  totalSamples?: number;
  featureDim?: number;
  step?: number;
  featureColumns?: string[];
  metadata?: Record<string, any>;
}

export interface FilterRequest {

  filters?: Record<string, any> | null;
}

export interface FundFlowDataResponse {

  fundFlow?: FundFlowItem[];
  total?: number;
  symbol?: string | null;
  timeframe?: string | null;
}

export interface FundFlowItem {

  tradeDate?: string;
  mainNetInflow?: number;
  mainNetInflowRate: number; // Default: 0
  superLargeNetInflow?: number;
  largeNetInflow?: number;
  mediumNetInflow?: number;
  smallNetInflow?: number;
}

export interface FundFlowRequest {

  symbol?: string;
  timeframe: string; // Default: '1'
  startDate?: string | null;
  endDate?: string | null;
}

export interface FundFlowResponse {

  id?: number;
  symbol?: string;
  tradeDate?: string;
  timeframe?: string;
  mainNetInflow?: number;
  mainNetInflowRate?: number;
  superLargeNetInflow?: number;
  largeNetInflow?: number;
  mediumNetInflow?: number;
  smallNetInflow?: number;
  createdAt: string | null; // Default: None
}

export interface HeatmapResponse {

  sector?: string;
  stocks?: HeatmapStock[];
  avgChange?: number;
}

export interface HeatmapStock {

  symbol?: string;
  name?: string;
  changePercent?: number;
  marketCap?: number | null;
}

export interface HyperparameterSearchRequest {

  stockCode?: string;
  market: string; // Default: 'sh'
  step: number; // Default: 10
  cv: number; // Default: 5
  paramGrid?: Record<string, any[]> | null;
}

export interface HyperparameterSearchResponse {

  success?: boolean;
  message?: string;
  bestParams?: Record<string, any>;
  bestRmse?: number;
  bestMse?: number;
  cvResults?: Record<string, any>;
}

export interface IndexQuoteResponse {

  code?: string;
  name?: string;
  price?: number;
  preClose?: number;
  open?: number;
  high?: number;
  low?: number;
  volume?: number;
  amount?: number;
  change?: number | null;
  changePct?: number | null;
  timestamp?: string;
}

export interface IndicatorCalculateRequest {

  symbol?: string;
  startDate?: string;
  endDate?: string;
  indicators?: IndicatorSpec[];
  useCache: boolean; // Default: True
}

export interface IndicatorCalculateResponse {

  symbol?: string;
  symbolName?: string;
  startDate?: string;
  endDate?: string;
  ohlcv?: OHLCVData;
  indicators?: IndicatorResult[];
  calculationTimeMs?: number;
  cached: boolean; // Default: False
}

export interface IndicatorConfigCreateRequest {

  name?: string;
  indicators?: IndicatorSpec[];
}

export interface IndicatorConfigListResponse {

  totalCount?: number;
  configs?: IndicatorConfigResponse[];
}

export interface IndicatorConfigResponse {

  id?: number;
  userId?: number;
  name?: string;
  indicators?: Record<string, any>[];
  createdAt?: string;
  updatedAt?: string;
  lastUsedAt?: string | null;
}

export interface IndicatorConfigUpdateRequest {

  name?: string | null;
  indicators?: IndicatorSpec[] | null;
}

export interface IndicatorMetadata {

  abbreviation?: string;
  fullName?: string;
  chineseName?: string;
  category?: string;
  description?: string;
  panelType?: string;
  parameters?: Record<string, any>[];
  outputs?: Record<string, string>[];
  referenceLines?: number[] | null;
  minDataPointsFormula?: string;
}

export interface IndicatorRegistryResponse {

  totalCount?: number;
  categories?: Record<string, number>;
  indicators?: IndicatorMetadata[];
}

export interface IndicatorResult {

  abbreviation?: string;
  parameters?: Record<string, any>;
  outputs?: IndicatorValueOutput[];
  panelType?: string;
  referenceLines?: number[] | null;
  error?: string | null;
}

export interface IndicatorSpec {

  abbreviation?: string;
  parameters?: Record<string, any>;
}

export interface IndicatorValueOutput {

  outputName?: string;
  values?: number | null[];
  displayName?: string;
}

export interface KlineCandle {

  datetime?: string;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  volume?: number;
  amount?: number | null;
}

export interface KlineDataPoint {

  date?: string;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  volume?: number;
  amount?: number | null;
}

export interface KlineRequest {

  symbol?: string;
  startDate?: string | null;
  endDate?: string | null;
  period: string; // Default: '1d'
}

export interface KlineResponse {

  symbol?: string;
  period?: string;
  data?: KlineCandle[];
  count?: number;
}

export interface LongHuBangItem {

  symbol?: string;
  name?: string;
  netAmount?: number;
  reason?: string | null;
}

export interface LongHuBangRequest {

  symbol?: string | null;
  startDate?: string | null;
  endDate?: string | null;
  minNetAmount?: number | null;
  limit: number; // Default: 100
}

export interface LongHuBangResponse {

  id?: number;
  symbol?: string;
  name?: string;
  tradeDate?: string;
  reason?: string | null;
  buyAmount?: number;
  sellAmount?: number;
  netAmount?: number;
  turnoverRate?: number;
  institutionBuy?: number | null;
  institutionSell?: number | null;
  createdAt: string | null; // Default: None
}

export interface MLResponse {

  success?: boolean;
  message?: string;
  data?: any | null;
}

export interface MarketOverviewResponse {

  marketStats?: MarketOverviewStats;
  topEtfs?: TopETFItem[];
  chipRaces?: ChipRaceItem[];
  longHuBang?: LongHuBangItem[];
  timestamp?: string;
}

export interface MarketOverviewStats {

  totalStocks?: number;
  risingStocks?: number;
  fallingStocks?: number;
  avgChangePercent?: number;
}

export interface MessageResponse {

  success?: boolean;
  message?: string;
  data: dict | null; // Default: None
}

export interface MillisecondTimestampField {

  timestamp?: number;
}

export interface ModelDetailResponse {

  name?: string;
  metadata?: Record<string, any>;
  trainingHistory?: Record<string, any>[];
  featureImportance?: Record<string, any>[] | null;
}

export interface ModelEvaluationRequest {

  modelName?: string;
  stockCode?: string;
  market: string; // Default: 'sh'
}

export interface ModelEvaluationResponse {

  success?: boolean;
  message?: string;
  modelName?: string;
  metrics?: Record<string, any>;
}

export interface ModelInfo {

  name?: string;
  path?: string;
  trainedAt?: string;
  testRmse?: number;
  testR2?: number;
  trainSamples?: number | null;
  testSamples?: number | null;
  featureDim?: number | null;
}

export interface ModelListResponse {

  total?: number;
  models?: ModelInfo[];
}

export interface ModelPredictRequest {

  modelName?: string;
  stockCode?: string;
  market: string; // Default: 'sh'
  days: number; // Default: 1
}

export interface ModelPredictResponse {

  success?: boolean;
  message?: string;
  modelName?: string;
  stockCode?: string;
  predictions?: PredictionResult[];
}

export interface ModelTrainRequest {

  stockCode?: string;
  market: string; // Default: 'sh'
  step: number; // Default: 10
  testSize: number; // Default: 0.2
  modelName?: string;
  modelParams?: Record<string, any> | null;
}

export interface ModelTrainResponse {

  success?: boolean;
  message?: string;
  modelName?: string;
  metrics?: Record<string, any>;
}

export interface NotificationTestRequest {

  notificationType?: string;
  configData?: Record<string, any>;
}

export interface NotificationTestResponse {

  success?: boolean;
  message?: string;
}

export interface OHLCVData {

  dates?: string[];
  open?: number[];
  high?: number[];
  low?: number[];
  close?: number[];
  volume?: number[];
  turnover?: number[];
}

export interface PaginatedResponse {

  total?: number;
  page?: number;
  pageSize?: number;
  data?: dict[];
}

export interface PaginationInfo {

  page?: number;
  pageSize?: number;
  total?: number;
  pages?: number | null;
}

export interface PaginationRequest {

  page: number; // Default: 1
  pageSize: number; // Default: 20
}

export interface PercentageField {

  percentage?: string;
}

export interface PredictionResult {

  date?: string;
  predictedPrice?: number;
  confidence?: number | null;
}

export interface PriceField {

  price?: string;
}

export interface RealTimeQuoteResponse {

  code?: string;
  name?: string;
  price?: number;
  preClose?: number;
  open?: number;
  high?: number;
  low?: number;
  volume?: number;
  amount?: number;
  bid1?: number;
  bid1Volume?: number;
  ask1?: number;
  ask1Volume?: number;
  timestamp?: string;
  change?: number | null;
  changePct?: number | null;
}

export interface RiskAlertCreate {

  name?: string;
  metricType?: string;
  thresholdValue?: number;
  condition?: string;
  entityType?: string;
  entityId?: number | null;
  isActive?: boolean;
  notificationChannels?: string[];
}

export interface RiskAlertListResponse {

  alerts?: RiskAlertResponse[];
}

export interface RiskAlertResponse {

  id?: number;
  name?: string;
  metricType?: string;
  thresholdValue?: number;
  condition?: string;
  entityType?: string;
  entityId?: number | null;
  isActive?: boolean;
  notificationChannels?: string[];
  createdAt?: string;
  updatedAt?: string | null;
}

export interface RiskAlertUpdate {

  name?: string | null;
  metricType?: string | null;
  thresholdValue?: number | null;
  condition?: string | null;
  entityType?: string | null;
  entityId?: number | null;
  isActive?: boolean | null;
  notificationChannels?: string[] | null;
}

export interface RiskDashboardResponse {

  metrics?: RiskMetricsSummary;
  activeAlerts?: ActiveAlert[];
  riskHistory?: RiskHistoryPoint[];
}

export interface RiskHistoryPoint {

  date?: date_type;
  var95Hist?: number | null;
  cvar95?: number | null;
  beta?: number | null;
}

export interface RiskMetricsHistoryResponse {

  metricsHistory?: RiskHistoryPoint[];
}

export interface RiskMetricsSummary {

  var95Hist?: number | null;
  cvar95?: number | null;
  beta?: number | null;
}

export interface SortRequest {

  sortBy?: string | null;
  sortOrder?: string | null;
}

export interface StandardResponse {

  status?: string;
  code?: number;
  message?: string;
  timestamp?: string;
}

export interface StockSymbolField {

  symbol?: string;
}

export interface TdxDataRequest {

  stockCode?: string;
  market: string; // Default: 'sh'
}

export interface TdxDataResponse {

  code?: string;
  market?: string;
  data?: Record<string, any>[];
  totalRecords?: number;
}

export interface TdxExportRequest {

  stockCode?: string;
  market: string; // Default: 'sh'
  outputFormat: string; // Default: 'csv'
}

export interface TdxHealthResponse {

  status?: string;
  tdxConnected?: boolean;
  timestamp?: string;
  serverInfo?: dict | null;
}

export interface TimestampField {

  timestamp?: string;
}

export interface TopETFItem {

  symbol?: string;
  name?: string;
  latestPrice?: number;
  changePercent?: number;
  volume?: number;
}

export interface VaRCVaRRequest {

  entityType?: string;
  entityId?: number;
  confidenceLevel?: number;
}

export interface VaRCVaRResult {

  var95Hist?: number | null;
  var95Param?: number | null;
  var99Hist?: number | null;
  cvar95?: number | null;
  cvar99?: number | null;
  entityType?: string | null;
  entityId?: number | null;
  confidenceLevel?: number | null;
}

export interface VolumeField {

  volume?: number;
}

export interface WencaiCustomQueryRequest {

  queryText?: string;
  pages: number; // Default: 1
}

export interface WencaiCustomQueryResponse {

  success?: boolean;
  message?: string;
  queryText?: string;
  totalRecords?: number;
  results?: Record<string, any>[];
  columns?: string[];
  fetchTime?: string;
}

export interface WencaiErrorResponse {

  success?: boolean;
  error?: string;
  message?: string;
  details?: Record<string, any> | null;
}

export interface WencaiHistoryItem {

  date?: string;
  totalRecords?: number;
  fetchCount?: number;
}

export interface WencaiHistoryResponse {

  queryName?: string;
  dateRange?: string[];
  history?: WencaiHistoryItem[];
  totalDays?: number;
}

export interface WencaiQueryInfo {

  id?: number;
  queryName?: string;
  queryText?: string;
  description?: string | null;
  isActive?: boolean;
  createdAt?: string | null;
  updatedAt?: string | null;
}

export interface WencaiQueryListResponse {

  queries?: WencaiQueryInfo[];
  total?: number;
}

export interface WencaiQueryRequest {

  queryName?: string;
  pages: number; // Default: 1
}

export interface WencaiQueryResponse {

  success?: boolean;
  message?: string;
  queryName?: string;
  totalRecords?: number;
  newRecords?: number;
  duplicateRecords?: number;
  tableName?: string;
  fetchTime?: string;
}

export interface WencaiRefreshRequest {

  pages: number; // Default: 1
  force: boolean; // Default: False
}

export interface WencaiRefreshResponse {

  status?: string;
  message?: string;
  taskId?: string | null;
  queryName?: string;
}

export interface WencaiResultItem {

  data?: Record<string, any>;
  fetchTime?: string;
}

export interface WencaiResultsResponse {

  queryName?: string;
  total?: number;
  results?: Record<string, any>[];
  columns?: string[];
  latestFetchTime?: string | null;
}

export interface WencaiStatsResponse {

  totalQueries?: number;
  activeQueries?: number;
  totalRecords?: number;
  lastRefreshTime?: string | null;
}
