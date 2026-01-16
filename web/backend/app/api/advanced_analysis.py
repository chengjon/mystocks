"""
FastAPI Integration for Advanced Quantitative Analysis
A股量化分析平台高级分析功能API接口

This module provides RESTful API endpoints for accessing the advanced
quantitative analysis features integrated with the existing MyStocks platform.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from src.advanced_analysis import AdvancedAnalysisEngine, AnalysisType
from src.core import MyStocksUnifiedManager
from src.monitoring import AlertManager

# Initialize components
data_manager = MyStocksUnifiedManager()
analysis_engine = AdvancedAnalysisEngine(data_manager)
alert_manager = AlertManager()

router = APIRouter(prefix="/api/v1/advanced-analysis", tags=["advanced-analysis"])


# Request/Response Models
class AnalysisRequest(BaseModel):
    """分析请求基础模型"""

    stock_code: str = Field(..., description="股票代码", example="600000")
    analysis_types: Optional[List[str]] = Field(
        None, description="分析类型列表，不指定则执行所有分析", example=["fundamental", "technical", "trading_signals"]
    )
    include_raw_data: bool = Field(False, description="是否包含原始数据", example=False)


class FundamentalAnalysisRequest(AnalysisRequest):
    """基本面分析请求"""

    periods: int = Field(4, description="分析周期数", ge=1, le=12, example=4)
    include_valuation: bool = Field(True, description="是否包含估值分析", example=True)
    include_comparison: bool = Field(True, description="是否包含行业比较", example=True)


class TechnicalAnalysisRequest(AnalysisRequest):
    """技术分析请求"""

    timeframes: List[str] = Field(["1d"], description="时间框架列表", example=["1d", "1w"])
    include_patterns: bool = Field(True, description="是否包含形态识别", example=True)
    include_regime: bool = Field(True, description="是否包含市场状态分析", example=True)
    signal_threshold: float = Field(0.6, description="信号阈值", ge=0, le=1, example=0.6)


class TradingSignalsRequest(AnalysisRequest):
    """交易信号分析请求"""

    signal_types: Optional[List[str]] = Field(
        None, description="信号类型过滤", example=["long_term", "short_term", "real_time"]
    )
    min_confidence: float = Field(0.5, description="最小置信度", ge=0, le=1, example=0.5)


class ComprehensiveAnalysisRequest(BaseModel):
    """综合分析请求"""

    stock_code: str = Field(..., description="股票代码", example="600000")
    analysis_types: Optional[List[str]] = Field(None, description="分析类型列表，不指定则执行所有分析")
    parameters: Optional[Dict[str, Any]] = Field(
        None,
        description="各分析类型的参数",
        example={
            "fundamental": {"periods": 4, "include_valuation": True},
            "technical": {"timeframes": ["1d"], "include_patterns": True},
            "trading_signals": {"min_confidence": 0.6},
        },
    )
    include_raw_data: bool = Field(False, description="是否包含原始数据")
    async_execution: bool = Field(False, description="是否异步执行")


class AnalysisResponse(BaseModel):
    """分析响应"""

    success: bool = Field(..., description="请求是否成功")
    code: int = Field(..., description="响应代码，0表示成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="分析结果数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    request_id: Optional[str] = Field(None, description="请求ID")
    processing_time: Optional[float] = Field(None, description="处理时间(秒)")


class BatchAnalysisRequest(BaseModel):
    """批量分析请求"""

    stock_codes: List[str] = Field(..., description="股票代码列表", max_items=50)
    analysis_types: Optional[List[str]] = Field(None, description="分析类型列表")
    parameters: Optional[Dict[str, Any]] = Field(None, description="分析参数")
    priority: str = Field("normal", description="优先级", enum=["low", "normal", "high"])


# API Endpoints


@router.post("/fundamental", response_model=AnalysisResponse)
async def analyze_fundamental(request: FundamentalAnalysisRequest):
    """
    基本面分析接口

    执行股票的基本面分析，包括财务比率计算、评分和估值分析。
    """
    start_time = datetime.now()

    try:
        # 转换分析类型
        analysis_types = [AnalysisType.FUNDAMENTAL]

        # 执行分析
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            analysis_engine.comprehensive_analysis,
            request.stock_code,
            analysis_types,
            {
                "periods": request.periods,
                "include_valuation": request.include_valuation,
                "include_comparison": request.include_comparison,
                "include_raw_data": request.include_raw_data,
            },
        )

        processing_time = (datetime.now() - start_time).total_seconds()

        return AnalysisResponse(
            success=True, code=0, message="基本面分析完成", data=result, processing_time=processing_time
        )

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return AnalysisResponse(
            success=False, code=500, message=f"基本面分析失败: {str(e)}", processing_time=processing_time
        )


@router.post("/technical", response_model=AnalysisResponse)
async def analyze_technical(request: TechnicalAnalysisRequest):
    """
    技术分析接口

    执行股票的技术分析，包括指标计算、信号生成和市场状态识别。
    """
    start_time = datetime.now()

    try:
        # 转换分析类型
        analysis_types = [AnalysisType.TECHNICAL]

        # 执行分析
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            analysis_engine.comprehensive_analysis,
            request.stock_code,
            analysis_types,
            {
                "timeframes": request.timeframes,
                "include_patterns": request.include_patterns,
                "include_regime": request.include_regime,
                "signal_threshold": request.signal_threshold,
                "include_raw_data": request.include_raw_data,
            },
        )

        processing_time = (datetime.now() - start_time).total_seconds()

        return AnalysisResponse(
            success=True, code=0, message="技术分析完成", data=result, processing_time=processing_time
        )

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return AnalysisResponse(
            success=False, code=500, message=f"技术分析失败: {str(e)}", processing_time=processing_time
        )


@router.post("/trading-signals", response_model=AnalysisResponse)
async def analyze_trading_signals(request: TradingSignalsRequest):
    """
    交易信号分析接口

    执行股票的交易信号分析，包括买卖点计算和预警。
    """
    start_time = datetime.now()

    try:
        # 转换分析类型
        analysis_types = [AnalysisType.TRADING_SIGNALS]

        # 执行分析
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            analysis_engine.comprehensive_analysis,
            request.stock_code,
            analysis_types,
            {
                "signal_types": request.signal_types,
                "min_confidence": request.min_confidence,
                "include_raw_data": request.include_raw_data,
            },
        )

        processing_time = (datetime.now() - start_time).total_seconds()

        return AnalysisResponse(
            success=True, code=0, message="交易信号分析完成", data=result, processing_time=processing_time
        )

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return AnalysisResponse(
            success=False, code=500, message=f"交易信号分析失败: {str(e)}", processing_time=processing_time
        )


@router.post("/multidimensional-radar", response_model=AnalysisResponse)
async def analyze_multidimensional_radar(request: AnalysisRequest):
    """
    多维度雷达分析接口

    执行股票的多维度雷达分析，整合所有8个核心分析维度：
    - 基本面分析
    - 技术面分析
    - 交易信号分析
    - 时序分析
    - 市场全景分析
    - 资金流向分析
    - 筹码分布分析
    - 异常追踪分析

    返回综合评分、风险评估、投资建议和雷达图数据。
    """
    start_time = datetime.now()

    try:
        # 转换分析类型
        analysis_types = [AnalysisType.MULTIDIMENSIONAL_RADAR]

        # 执行分析
        result = await asyncio.get_event_loop().run_in_executor(
            None,
            analysis_engine.comprehensive_analysis,
            request.stock_code,
            analysis_types,
            {
                "include_raw_data": request.include_raw_data,
            },
        )

        processing_time = (datetime.now() - start_time).total_seconds()

        return AnalysisResponse(
            success=True, code=0, message="多维度雷达分析完成", data=result, processing_time=processing_time
        )

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return AnalysisResponse(
            success=False, code=500, message=f"多维度雷达分析失败: {str(e)}", processing_time=processing_time
        )


@router.post("/comprehensive", response_model=AnalysisResponse)
async def comprehensive_analysis(request: ComprehensiveAnalysisRequest, background_tasks: BackgroundTasks):
    """
    综合分析接口

    执行股票的全面量化分析，包括基本面、技术面、交易信号等多维度分析。
    支持异步执行和批量处理。
    """
    start_time = datetime.now()

    try:
        # 转换分析类型
        analysis_types = None
        if request.analysis_types:
            type_mapping = {
                "fundamental": AnalysisType.FUNDAMENTAL,
                "technical": AnalysisType.TECHNICAL,
                "trading_signals": AnalysisType.TRADING_SIGNALS,
                "time_series": AnalysisType.TIME_SERIES,
                "market_panorama": AnalysisType.MARKET_PANORAMA,
                "capital_flow": AnalysisType.CAPITAL_FLOW,
                "chip_distribution": AnalysisType.CHIP_DISTRIBUTION,
                "anomaly_tracking": AnalysisType.ANOMALY_TRACKING,
                "financial_valuation": AnalysisType.FINANCIAL_VALUATION,
                "sentiment_analysis": AnalysisType.SENTIMENT_ANALYSIS,
                "decision_models": AnalysisType.DECISION_MODELS,
                "multidimensional_radar": AnalysisType.MULTIDIMENSIONAL_RADAR,
            }
            analysis_types = [type_mapping.get(t) for t in request.analysis_types if t in type_mapping]

        # 准备参数
        params = request.parameters or {}
        params["include_raw_data"] = request.include_raw_data

        if request.async_execution:
            # 异步执行
            background_tasks.add_task(_execute_comprehensive_analysis_async, request.stock_code, analysis_types, params)

            return AnalysisResponse(
                success=True, code=0, message="综合分析已提交异步执行", data={"status": "processing", "async": True}
            )
        else:
            # 同步执行
            result = await asyncio.get_event_loop().run_in_executor(
                None, analysis_engine.comprehensive_analysis, request.stock_code, analysis_types, params
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            return AnalysisResponse(
                success=True, code=0, message="综合分析完成", data=result, processing_time=processing_time
            )

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return AnalysisResponse(
            success=False, code=500, message=f"综合分析失败: {str(e)}", processing_time=processing_time
        )


@router.post("/batch", response_model=AnalysisResponse)
async def batch_analysis(request: BatchAnalysisRequest, background_tasks: BackgroundTasks):
    """
    批量分析接口

    对多个股票执行批量分析，支持优先级调度。
    """
    start_time = datetime.now()

    try:
        # 转换分析类型
        analysis_types = None
        if request.analysis_types:
            type_mapping = {
                "fundamental": AnalysisType.FUNDAMENTAL,
                "technical": AnalysisType.TECHNICAL,
                "trading_signals": AnalysisType.TRADING_SIGNALS,
            }
            analysis_types = [type_mapping.get(t) for t in request.analysis_types if t in type_mapping]

        # 异步批量处理
        background_tasks.add_task(
            _execute_batch_analysis_async, request.stock_codes, analysis_types, request.parameters, request.priority
        )

        return AnalysisResponse(
            success=True,
            code=0,
            message=f"批量分析已提交处理，共{len(request.stock_codes)}只股票",
            data={"status": "processing", "stock_count": len(request.stock_codes), "priority": request.priority},
        )

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return AnalysisResponse(
            success=False, code=500, message=f"批量分析提交失败: {str(e)}", processing_time=processing_time
        )


@router.get("/market-overview", response_model=AnalysisResponse)
async def get_market_overview():
    """
    市场全景分析接口

    获取当前市场的全景分析，包括资金流向、交易活跃度、趋势变化等。
    """
    start_time = datetime.now()

    try:
        result = await asyncio.get_event_loop().run_in_executor(None, analysis_engine.get_market_overview)

        processing_time = (datetime.now() - start_time).total_seconds()

        return AnalysisResponse(
            success=True, code=0, message="市场全景分析完成", data=result, processing_time=processing_time
        )

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return AnalysisResponse(
            success=False, code=500, message=f"市场全景分析失败: {str(e)}", processing_time=processing_time
        )


@router.get("/realtime-alerts/{stock_code}", response_model=AnalysisResponse)
async def get_realtime_alerts(stock_code: str):
    """
    实时预警接口

    获取指定股票的实时分析预警信息。
    """
    start_time = datetime.now()

    try:
        alerts = await asyncio.get_event_loop().run_in_executor(None, analysis_engine.get_realtime_alerts, stock_code)

        processing_time = (datetime.now() - start_time).total_seconds()

        return AnalysisResponse(
            success=True,
            code=0,
            message=f"获取{stock_code}实时预警完成",
            data={"alerts": alerts, "count": len(alerts)},
            processing_time=processing_time,
        )

    except Exception as e:
        processing_time = (datetime.now() - start_time).total_seconds()
        return AnalysisResponse(
            success=False, code=500, message=f"获取实时预警失败: {str(e)}", processing_time=processing_time
        )


@router.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "advanced-analysis",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
    }


# Background task functions
async def _execute_comprehensive_analysis_async(
    stock_code: str, analysis_types: Optional[List[AnalysisType]], params: Dict[str, Any]
):
    """异步执行综合分析"""
    try:
        result = analysis_engine.comprehensive_analysis(stock_code, analysis_types, **params)

        # 这里可以添加结果存储或通知逻辑
        print(f"Comprehensive analysis completed for {stock_code}: {len(result)} analysis types")

    except Exception as e:
        print(f"Async comprehensive analysis failed for {stock_code}: {e}")
        # 这里可以添加错误处理和告警逻辑


async def _execute_batch_analysis_async(
    stock_codes: List[str],
    analysis_types: Optional[List[AnalysisType]],
    params: Optional[Dict[str, Any]],
    priority: str,
):
    """异步执行批量分析"""
    try:
        results = {}

        # 根据优先级设置并发数
        max_concurrent = {"low": 2, "normal": 5, "high": 10}.get(priority, 5)

        # 使用信号量控制并发
        semaphore = asyncio.Semaphore(max_concurrent)

        async def analyze_single(code: str):
            async with semaphore:
                try:
                    result = analysis_engine.comprehensive_analysis(code, analysis_types, **(params or {}))
                    results[code] = result
                    print(f"Batch analysis completed for {code}")
                except Exception as e:
                    results[code] = {"error": str(e)}
                    print(f"Batch analysis failed for {code}: {e}")

        # 并发执行
        tasks = [analyze_single(code) for code in stock_codes]
        await asyncio.gather(*tasks)

        # 这里可以添加批量结果存储或通知逻辑
        print(f"Batch analysis completed for {len(stock_codes)} stocks")

    except Exception as e:
        print(f"Async batch analysis failed: {e}")
        # 这里可以添加错误处理和告警逻辑
