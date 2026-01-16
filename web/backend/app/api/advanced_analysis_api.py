"""
高级分析API模块
Advanced Quantitative Analysis API Endpoints

提供12个高级量化分析功能的RESTful API接口：
1. 基本面分析 (Fundamental Analysis)
2. 技术面分析 (Technical Analysis)
3. 交易信号分析 (Trading Signals Analysis)
4. 时序分析 (Time Series Analysis)
5. 市场全景分析 (Market Panorama Analysis)
6. 资金流向分析 (Capital Flow Analysis)
7. 筹码分布分析 (Chip Distribution Analysis)
8. 异常追踪分析 (Anomaly Tracking Analysis)
9. 财务估值分析 (Financial Valuation Analysis)
10. 情绪分析 (Sentiment Analysis)
11. 决策模型分析 (Decision Models Analysis)
12. 多维度雷达分析 (Multidimensional Radar Analysis)
"""

from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.core.responses import UnifiedResponse, ok, bad_request, server_error
from app.core.security import User, get_current_user
from app.core.database import get_db
from app.services.advanced_analysis_service import AdvancedAnalysisService

# 创建路由器
router = APIRouter(
    prefix="/api/v1/advanced-analysis",
    tags=["advanced-analysis"],
    responses={
        401: {"description": "未授权"},
        422: {"description": "参数验证失败"},
        500: {"description": "服务器内部错误"},
    },
)


# Pydantic请求模型
class AnalysisRequest(BaseModel):
    """通用分析请求模型"""

    symbol: str = Query(..., description="股票代码", example="000001")
    include_raw_data: bool = Query(False, description="是否包含原始数据")


class TradingSignalsRequest(BaseModel):
    """交易信号分析请求模型"""

    symbol: str = Query(..., description="股票代码", example="000001")
    signal_types: Optional[list[str]] = Query(None, description="信号类型筛选")
    min_confidence: float = Query(0.5, description="最小置信度", ge=0.0, le=1.0)
    include_raw_data: bool = Query(False, description="是否包含原始数据")


class MarketPanoramaRequest(BaseModel):
    """市场全景分析请求模型"""

    include_raw_data: bool = Query(False, description="是否包含原始数据")


@router.get("/fundamental", response_model=UnifiedResponse)
async def analyze_fundamental(
    request: AnalysisRequest = Depends(),
    current_user: User = Depends(get_current_user),
    service: AdvancedAnalysisService = Depends(),
) -> Dict[str, Any]:
    """
    基本面分析API

    执行股票基本面分析，包括财务比率、偿债能力、盈利能力、成长性等指标。

    **分析内容：**
    - 财务比率分析 (ROE, ROA, 毛利率等)
    - 偿债能力评估 (流动比率、速动比率)
    - 盈利能力分析 (净利率、总资产报酬率)
    - 成长性指标 (营收增长率、净利润增长率)
    """
    try:
        result = await service.analyze_fundamental(
            symbol=request.symbol,
            include_raw_data=request.include_raw_data,
            user_id=current_user.id,
        )

        return ok(
            data=result,
            message="基本面分析完成",
            symbol=request.symbol,
            analysis_type="fundamental",
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        return server_error(message=f"基本面分析失败: {str(e)}")


@router.get("/technical", response_model=UnifiedResponse)
async def analyze_technical(
    request: AnalysisRequest = Depends(),
    current_user: User = Depends(get_current_user),
    service: AdvancedAnalysisService = Depends(),
) -> Dict[str, Any]:
    """
    技术面分析API

    执行股票技术面分析，包括26个专业技术指标和趋势分析。

    **分析内容：**
    - 趋势指标 (MA, MACD, Bollinger Bands)
    - 动量指标 (RSI, Stochastic, Williams %R)
    - 波动率指标 (ATR, Bollinger Bandwidth)
    - 成交量指标 (Volume, OBV, Chaikin Money Flow)
    - 支撑阻力分析
    - 趋势强度评估
    """
    try:
        result = await service.analyze_technical(
            symbol=request.symbol,
            include_raw_data=request.include_raw_data,
            user_id=current_user.id,
        )

        return ok(
            data=result,
            message="技术面分析完成",
            symbol=request.symbol,
            analysis_type="technical",
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        return server_error(message=f"技术面分析失败: {str(e)}")


@router.get("/trading-signals", response_model=UnifiedResponse)
async def analyze_trading_signals(
    request: TradingSignalsRequest = Depends(),
    current_user: User = Depends(get_current_user),
    service: AdvancedAnalysisService = Depends(),
) -> Dict[str, Any]:
    """
    交易信号分析API

    执行交易信号分析，识别买卖点和市场信号。

    **分析内容：**
    - 动量信号 (Momentum, Mean Reversion)
    - 突破信号 (Breakout, Breakdown)
    - 成交量信号 (Volume Confirmation)
    - 价格模式识别 (Double Top/Bottom, Head & Shoulders)
    - 信号强度评分
    - 风险评估
    """
    try:
        result = await service.analyze_trading_signals(
            symbol=request.symbol,
            signal_types=request.signal_types,
            min_confidence=request.min_confidence,
            include_raw_data=request.include_raw_data,
            user_id=current_user.id,
        )

        return ok(
            data=result,
            message="交易信号分析完成",
            symbol=request.symbol,
            analysis_type="trading_signals",
            signal_types=request.signal_types,
            min_confidence=request.min_confidence,
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        return server_error(message=f"交易信号分析失败: {str(e)}")


@router.get("/time-series", response_model=UnifiedResponse)
async def analyze_time_series(
    request: AnalysisRequest = Depends(),
    current_user: User = Depends(get_current_user),
    service: AdvancedAnalysisService = Depends(),
) -> Dict[str, Any]:
    """
    时序分析API

    执行时序分析，包括拐点检测、趋势分割和预测分析。

    **分析内容：**
    - 拐点检测算法 (Peak/Valley identification)
    - 趋势分割 (Trend segmentation)
    - 周期性分析 (Seasonal decomposition)
    - 预测模型 (ARIMA, LSTM)
    - 异常点识别
    - 模式匹配分析
    """
    try:
        result = await service.analyze_time_series(
            symbol=request.symbol,
            include_raw_data=request.include_raw_data,
            user_id=current_user.id,
        )

        return ok(
            data=result,
            message="时序分析完成",
            symbol=request.symbol,
            analysis_type="time_series",
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        return server_error(message=f"时序分析失败: {str(e)}")


@router.get("/market-panorama", response_model=UnifiedResponse)
async def analyze_market_panorama(
    request: MarketPanoramaRequest = Depends(),
    current_user: User = Depends(get_current_user),
    service: AdvancedAnalysisService = Depends(),
) -> Dict[str, Any]:
    """
    市场全景分析API

    执行市场全景分析，包括资金流向、交易活跃度、趋势变化、市值分布、动态估值等。

    **分析内容：**
    - 资金流向全景 (沪深港通、主力资金、北向南向)
    - 交易活跃度分析 (换手率、成交量分布)
    - 趋势变化监控 (板块轮动、热点转移)
    - 市值分布分析 (大中小盘结构变化)
    - 动态估值评估 (整体市场估值水平)
    """
    try:
        result = await service.analyze_market_panorama(
            include_raw_data=request.include_raw_data, user_id=current_user.id
        )

        return ok(
            data=result,
            message="市场全景分析完成",
            analysis_type="market_panorama",
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        return server_error(message=f"市场全景分析失败: {str(e)}")


@router.get("/capital-flow", response_model=UnifiedResponse)
async def analyze_capital_flow(
    request: AnalysisRequest = Depends(),
    current_user: User = Depends(get_current_user),
    service: AdvancedAnalysisService = Depends(),
) -> Dict[str, Any]:
    """
    资金流向分析API

    执行资金流向分析，包括主力控盘和资金分布。

    **分析内容：**
    - 资金流向聚类分析 (K-means, DBSCAN)
    - 主力资金动向追踪
    - 资金分布特征分析
    - 主力控盘能力评估 (筹码集中度、成本分布)
    - 资金流向异常检测
    - 机构资金行为分析
    """
    try:
        result = await service.analyze_capital_flow(
            symbol=request.symbol,
            include_raw_data=request.include_raw_data,
            user_id=current_user.id,
        )

        return ok(
            data=result,
            message="资金流向分析完成",
            symbol=request.symbol,
            analysis_type="capital_flow",
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        return server_error(message=f"资金流向分析失败: {str(e)}")


@router.get("/chip-distribution", response_model=UnifiedResponse)
async def analyze_chip_distribution(
    request: AnalysisRequest = Depends(),
    current_user: User = Depends(get_current_user),
    service: AdvancedAnalysisService = Depends(),
) -> Dict[str, Any]:
    """
    筹码分布分析API

    执行筹码分布分析，基于成本转换原理。

    **分析内容：**
    - 筹码分布特征分析 (成本分布曲线)
    - 获利盘比例计算 (Profit-taking ratio)
    - 成本转换效率评估
    - 筹码集中度分析
    - 市场结构评估 (多空力量对比)
    - 关键价位识别 (支撑阻力)
    """
    try:
        result = await service.analyze_chip_distribution(
            symbol=request.symbol,
            include_raw_data=request.include_raw_data,
            user_id=current_user.id,
        )

        return ok(
            data=result,
            message="筹码分布分析完成",
            symbol=request.symbol,
            analysis_type="chip_distribution",
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        return server_error(message=f"筹码分布分析失败: {str(e)}")


@router.get("/anomaly-tracking", response_model=UnifiedResponse)
async def analyze_anomaly_tracking(
    request: AnalysisRequest = Depends(),
    current_user: User = Depends(get_current_user),
    service: AdvancedAnalysisService = Depends(),
) -> Dict[str, Any]:
    """
    异常追踪分析API

    执行异常追踪分析，基于涨跌幅排序等指标。

    **分析内容：**
    - 价格异动检测 (Price anomaly detection)
    - 成交量异常分析 (Volume spike analysis)
    - 涨跌幅排序分析 (Price change ranking)
    - 异常模式识别 (Unusual pattern detection)
    - 市场冲击评估 (Market impact assessment)
    - 异常持续性分析 (Anomaly persistence)
    """
    try:
        result = await service.analyze_anomaly_tracking(
            symbol=request.symbol,
            include_raw_data=request.include_raw_data,
            user_id=current_user.id,
        )

        return ok(
            data=result,
            message="异常追踪分析完成",
            symbol=request.symbol,
            analysis_type="anomaly_tracking",
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        return server_error(message=f"异常追踪分析失败: {str(e)}")


@router.get("/financial-valuation", response_model=UnifiedResponse)
async def analyze_financial_valuation(
    request: AnalysisRequest = Depends(),
    current_user: User = Depends(get_current_user),
    service: AdvancedAnalysisService = Depends(),
) -> Dict[str, Any]:
    """
    财务估值分析API

    执行财务估值分析，包括财务指标、杜邦分析、定价方法等。

    **分析内容：**
    - 财务指标体系 (Financial ratios analysis)
    - 杜邦分析 (DuPont analysis)
    - 现代金融工程定价方法 (DCF, EVA)
    - 基于历史相似收益的估值 (Historical valuation)
    - 市场股价正态分布分析 (Normal distribution analysis)
    - 行业估值均值对比 (Peer comparison)
    """
    try:
        result = await service.analyze_financial_valuation(
            symbol=request.symbol,
            include_raw_data=request.include_raw_data,
            user_id=current_user.id,
        )

        return ok(
            data=result,
            message="财务估值分析完成",
            symbol=request.symbol,
            analysis_type="financial_valuation",
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        return server_error(message=f"财务估值分析失败: {str(e)}")


@router.get("/sentiment", response_model=UnifiedResponse)
async def analyze_sentiment(
    request: AnalysisRequest = Depends(),
    current_user: User = Depends(get_current_user),
    service: AdvancedAnalysisService = Depends(),
) -> Dict[str, Any]:
    """
    情绪分析API

    执行情绪分析，包括研报、新闻、人气等数据。

    **分析内容：**
    - 研报情绪分析 (Research report sentiment)
    - 新闻情感分析 (News sentiment analysis)
    - 社交媒体人气分析 (Social media popularity)
    - 投资者情绪指标 (Investor sentiment indicators)
    - 市场情绪热度分析 (Market sentiment heat map)
    - 情绪变化趋势分析 (Sentiment trend analysis)
    """
    try:
        result = await service.analyze_sentiment(
            symbol=request.symbol,
            include_raw_data=request.include_raw_data,
            user_id=current_user.id,
        )

        return ok(
            data=result,
            message="情绪分析完成",
            symbol=request.symbol,
            analysis_type="sentiment",
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        return server_error(message=f"情绪分析失败: {str(e)}")


@router.get("/decision-models", response_model=UnifiedResponse)
async def analyze_decision_models(
    request: AnalysisRequest = Depends(),
    current_user: User = Depends(get_current_user),
    service: AdvancedAnalysisService = Depends(),
) -> Dict[str, Any]:
    """
    决策模型分析API

    执行决策模型分析，包括巴菲特、欧内尔、林奇模型等。

    **分析内容：**
    - 巴菲特模型 (Buffett Model - Value investing)
    - 欧内尔模型 (O'Neil Model - CAN SLIM)
    - 林奇模型 (Lynch Model - PEG ratio)
    - 数据挖掘驱动的模型 (Machine learning models)
    - 多模型集成分析 (Ensemble analysis)
    - 模型性能评估 (Model evaluation metrics)
    """
    try:
        result = await service.analyze_decision_models(
            symbol=request.symbol,
            include_raw_data=request.include_raw_data,
            user_id=current_user.id,
        )

        return ok(
            data=result,
            message="决策模型分析完成",
            symbol=request.symbol,
            analysis_type="decision_models",
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        return server_error(message=f"决策模型分析失败: {str(e)}")


@router.get("/multidimensional-radar", response_model=UnifiedResponse)
async def analyze_multidimensional_radar(
    request: AnalysisRequest = Depends(),
    current_user: User = Depends(get_current_user),
    service: AdvancedAnalysisService = Depends(),
) -> Dict[str, Any]:
    """
    多维度雷达分析API

    执行多维度雷达综合分析，整合所有8个分析维度的结果。

    **分析内容：**
    - 技术面维度 (Technical analysis)
    - 基本面维度 (Fundamental analysis)
    - 资金面维度 (Capital flow analysis)
    - 消息面维度 (Sentiment analysis)
    - 行业面维度 (Sector analysis)
    - 估值面维度 (Valuation analysis)
    - 持仓面维度 (Position analysis)
    - 板块面维度 (Board analysis)
    - 综合评分计算 (Weighted scoring)
    - 雷达图可视化数据 (Radar chart data)
    - 投资建议生成 (Investment recommendations)
    """
    try:
        result = await service.analyze_multidimensional_radar(
            symbol=request.symbol,
            include_raw_data=request.include_raw_data,
            user_id=current_user.id,
        )

        return ok(
            data=result,
            message="多维度雷达分析完成",
            symbol=request.symbol,
            analysis_type="multidimensional_radar",
            overall_score=result.get("overall_score"),
            risk_level=result.get("risk_assessment", {}).get("overall_risk_level"),
            recommendation=result.get("investment_recommendation"),
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        return server_error(message=f"多维度雷达分析失败: {str(e)}")


# 批量分析接口
@router.post("/batch", response_model=UnifiedResponse)
async def analyze_batch(
    symbols: list[str],
    analysis_types: list[str],
    current_user: User = Depends(get_current_user),
    service: AdvancedAnalysisService = Depends(),
) -> Dict[str, Any]:
    """
    批量高级分析API

    对多个股票执行批量高级分析。

    **参数：**
    - symbols: 股票代码列表
    - analysis_types: 分析类型列表

    **支持的分析类型：**
    - fundamental, technical, trading_signals, time_series
    - market_panorama, capital_flow, chip_distribution, anomaly_tracking
    - financial_valuation, sentiment, decision_models, multidimensional_radar
    """
    try:
        result = await service.analyze_batch(
            symbols=symbols, analysis_types=analysis_types, user_id=current_user.id
        )

        return ok(
            data=result,
            message="批量高级分析完成",
            symbols_count=len(symbols),
            analysis_types=analysis_types,
            total_results=len(result),
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        return server_error(message=f"批量分析失败: {str(e)}")


# 健康检查接口
@router.get("/health", response_model=UnifiedResponse)
async def health_check(service: AdvancedAnalysisService = Depends()) -> Dict[str, Any]:
    """
    高级分析模块健康检查

    检查所有分析器的可用性和性能状态。
    """
    try:
        health_status = await service.health_check()

        return ok(
            data=health_status,
            message="高级分析模块健康检查完成",
            status="healthy"
            if health_status.get("overall_status") == "healthy"
            else "degraded",
            analyzers_count=health_status.get("analyzers_count"),
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        return server_error(message=f"健康检查失败: {str(e)}")
