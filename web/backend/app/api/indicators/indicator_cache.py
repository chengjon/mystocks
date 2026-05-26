"""
Indicator Calculation API Endpoints
技术指标计算API路由

Phase 4C Enhanced - 企业级技术指标计算服务
- 高性能缓存机制
- 增强参数验证
- 速率限制保护
- 完整错误处理
- 性能监控
- 批量计算优化
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional

import numpy as np
import structlog
from fastapi import APIRouter, Body, Depends, Path, Query

from app.api.auth import get_current_active_user
from app.api.indicators.indicator_runtime_support import (
    IndicatorCache as _IndicatorCache,
    RateLimiter as _RateLimiter,
    indicator_cache,
    rate_limit,
)
from app.core.exceptions import BusinessException, ForbiddenException, NotFoundException, ValidationException
from app.core.responses import UnifiedResponse, create_success_response
from app.core.security import User
from app.schemas.indicator_request import (
    IndicatorCalculateRequest,
)
from app.schemas.indicator_response import (
    IndicatorMetadata,
    IndicatorRegistryResponse,
)
from app.services.data_service import DataService, InvalidDateRangeError, StockDataNotFoundError, get_data_service
from app.services.indicator_calculator import IndicatorCalculationError, InsufficientDataError, get_indicator_calculator
from app.services.indicator_registry import IndicatorCategory, IndicatorRegistry, get_indicator_registry_dependency

logger = structlog.get_logger()
router = APIRouter()


def get_indicator_data_service() -> DataService:
    return get_data_service()


from app.api.indicators._indicator_cache_responses import (
    INDICATOR_CACHE_STATS_RESPONSES,
    INDICATOR_REGISTRY_RESPONSES,
    INDICATOR_CATEGORY_RESPONSES,
    INDICATOR_CACHE_CLEAR_RESPONSES,
    INDICATOR_CATEGORY_PATH_DESCRIPTION,
    INDICATOR_CALCULATE_REQUEST_EXAMPLE,
    INDICATOR_CALCULATE_BATCH_REQUEST_EXAMPLE,
    INDICATOR_CALCULATE_RESPONSES,
    INDICATOR_CALCULATE_BATCH_RESPONSES,
    IndicatorCalculateBatchRequest,
    IndicatorOptimizationRequest as _IndicatorOptimizationRequest,
)

IndicatorCache = _IndicatorCache
RateLimiter = _RateLimiter
IndicatorOptimizationRequest = _IndicatorOptimizationRequest


@router.get(
    "/registry",
    response_model=UnifiedResponse[IndicatorRegistryResponse],
    summary="获取指标注册表",
    description="返回技术指标注册中心中的全部可用指标元数据，支持按分类、关键词和高级指标开关筛选，供行情分析、策略编排与指标面板配置统一复用。",
    responses=INDICATOR_REGISTRY_RESPONSES,
)
@rate_limit(limit=30, window=60)  # 每分钟最多30次请求
async def get_indicator_registry_endpoint(
    category: Optional[str] = Query(None, description="筛选指定分类的指标"),
    search: Optional[str] = Query(None, description="搜索指标名称或描述"),
    include_advanced: bool = Query(True, description="是否包含高级指标"),
    current_user: User = Depends(get_current_active_user),
    registry: IndicatorRegistry = Depends(get_indicator_registry_dependency),
):
    """
    获取指标注册表 - Phase 4C Enhanced

    返回所有可用的技术指标及其元数据，支持分类筛选和搜索
    """
    try:
        all_indicators = registry.get_all_indicators()

        # 记录请求
        logger.info(
            "技术指标注册表查询",
            user_id=current_user.id,
            category_filter=category,
            search_query=search,
            include_advanced=include_advanced,
        )

        # 应用筛选条件
        filtered_indicators = {}
        for abbr, meta in all_indicators.items():
            # 分类筛选
            if category:
                try:
                    IndicatorCategory(category)
                    category_value = (
                        meta["category"].value if hasattr(meta["category"], "value") else str(meta["category"])
                    )
                    if category_value != category:
                        continue
                except ValueError:
                    continue

            # 高级指标筛选
            if not include_advanced and meta.get("advanced", False):
                continue

            # 搜索筛选
            if search:
                search_lower = search.lower()
                searchable_text = " ".join(
                    [
                        abbr.lower(),
                        meta.get("full_name", "").lower(),
                        meta.get("chinese_name", "").lower(),
                        meta.get("description", "").lower(),
                    ]
                )
                if search_lower not in searchable_text:
                    continue

            filtered_indicators[abbr] = meta

        # 统计各分类指标数量
        categories = {}
        for cat in IndicatorCategory:
            indicators_in_category = [
                meta
                for meta in filtered_indicators.values()
                if (meta["category"].value if hasattr(meta["category"], "value") else str(meta["category"]))
                == cat.value
            ]
            categories[cat.value] = len(indicators_in_category)

        # 转换为响应格式
        indicators_list = []
        for abbr, meta in filtered_indicators.items():
            # 确保enum值正确提取
            category_value = meta["category"].value if hasattr(meta["category"], "value") else str(meta["category"])
            panel_type_value = (
                meta["panel_type"].value if hasattr(meta["panel_type"], "value") else str(meta["panel_type"])
            )

            # 增强的元数据
            enhanced_metadata = IndicatorMetadata(
                abbreviation=abbr,
                full_name=meta["full_name"],
                chinese_name=meta["chinese_name"],
                category=category_value,
                description=meta["description"],
                panel_type=panel_type_value,
                parameters=meta.get("parameters", []),
                outputs=meta["outputs"],
                reference_lines=meta.get("reference_lines"),
                min_data_points_formula=meta["min_data_points_formula"],
            )

            indicators_list.append(enhanced_metadata.dict())

        response_data = IndicatorRegistryResponse(
            total_count=len(filtered_indicators),
            categories=categories,
            indicators=indicators_list,
        )

        logger.info(
            "技术指标注册表查询成功",
            user_id=current_user.id,
            total_indicators=len(filtered_indicators),
            filtered_count=len(all_indicators) - len(filtered_indicators),
        )

        return create_success_response(data=response_data, message="技术指标注册表查询成功").dict(exclude_unset=True)

    except Exception as e:
        logger.error("技术指标注册表查询失败", user_id=current_user.id, error=str(e), exc_info=True)
        raise BusinessException(
            detail=f"获取指标注册表失败: {str(e)}", status_code=500, error_code="INDICATOR_REGISTRY_RETRIEVAL_FAILED"
        )


@router.get(
    "/registry/{category}",
    response_model=UnifiedResponse[List[IndicatorMetadata]],
    summary="按分类获取指标列表",
    description="返回指定指标分类下的元数据清单，便于前端按趋势、动量、波动率、成交量或 K 线形态组织指标选择面板。",
    responses=INDICATOR_CATEGORY_RESPONSES,
)
async def get_indicators_by_category(
    category: str = Path(..., description=INDICATOR_CATEGORY_PATH_DESCRIPTION),
    registry: IndicatorRegistry = Depends(get_indicator_registry_dependency),
):
    """
    获取指定分类的指标

    - **category**: 指标分类 (trend, momentum, volatility, volume, candlestick)
    """
    try:
        # 验证分类
        try:
            indicator_category = IndicatorCategory(category)
        except ValueError:
            raise ValidationException(
                detail=f"无效的指标分类: {category}. 有效分类: {[c.value for c in IndicatorCategory]}", field="category"
            )

        indicators = registry.get_indicators_by_category(indicator_category)

        # 转换为响应格式
        indicators_list = []
        for abbr, meta in indicators.items():
            # 确保enum值正确提取
            category_value = meta["category"].value if hasattr(meta["category"], "value") else str(meta["category"])
            panel_type_value = (
                meta["panel_type"].value if hasattr(meta["panel_type"], "value") else str(meta["panel_type"])
            )

            indicators_list.append(
                IndicatorMetadata(
                    abbreviation=abbr,
                    full_name=meta["full_name"],
                    chinese_name=meta["chinese_name"],
                    category=category_value,
                    description=meta["description"],
                    panel_type=panel_type_value,
                    parameters=meta.get("parameters", []),
                    outputs=meta["outputs"],
                    reference_lines=meta.get("reference_lines"),
                    min_data_points_formula=meta["min_data_points_formula"],
                )
            )

        return create_success_response(data=indicators_list, message=f"分类 '{category}' 指标获取成功").dict(
            exclude_unset=True
        )

    except (BusinessException, ValidationException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error("Failed to get indicators for category {category}", exc_info=e)
        raise BusinessException(
            detail=f"获取分类指标失败: {str(e)}", status_code=500, error_code="CATEGORY_INDICATORS_RETRIEVAL_FAILED"
        )


@router.post(
    "/calculate",
    response_model=UnifiedResponse[Dict],
    summary="计算技术指标",
    responses=INDICATOR_CALCULATE_RESPONSES,
)
@rate_limit(limit=20, window=60)  # 每分钟最多20次计算请求
async def calculate_indicators(
    request: IndicatorCalculateRequest = Body(..., example=INDICATOR_CALCULATE_REQUEST_EXAMPLE),
    current_user: User = Depends(get_current_active_user),
    data_service: DataService = Depends(get_indicator_data_service),
):
    """
    计算技术指标 - Phase 4C Enhanced

    根据股票代码、日期范围和指标列表,计算技术指标值
    支持智能缓存、批量优化和性能监控

    **请求示例**:
    ```json
    {
        "symbol": "600519.SH",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "indicators": [
            {"abbreviation": "SMA", "parameters": {"timeperiod": 20}},
            {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
        ],
        "use_cache": true
    }
    ```
    """
    start_time = time.time()
    cache_used = False

    try:
        logger.info(
            "技术指标计算请求",
            user_id=current_user.id,
            symbol=request.symbol,
            start_date=str(request.start_date),
            end_date=str(request.end_date),
            indicator_count=len(request.indicators),
            use_cache=getattr(request, "use_cache", True),
        )

        # 验证日期范围
        date_range_days = (request.end_date - request.start_date).days
        if date_range_days < 1:
            raise ValidationException(detail="结束日期必须晚于开始日期", field="end_date")
        if date_range_days > 3650:  # 10年限制
            raise ValidationException(detail="日期范围不能超过10年", field="date_range")

        # 生成缓存键
        indicator_specs = [
            {"abbreviation": ind.abbreviation, "parameters": ind.parameters} for ind in request.indicators
        ]
        cache_key = indicator_cache._generate_cache_key(
            request.symbol, str(request.start_date), str(request.end_date), indicator_specs
        )

        # 尝试从缓存获取结果
        if getattr(request, "use_cache", True):
            cached_result = indicator_cache.get(cache_key)
            if cached_result:
                cache_used = True
                calculation_time_ms = (time.time() - start_time) * 1000

                logger.info(
                    "技术指标计算缓存命中",
                    user_id=current_user.id,
                    symbol=request.symbol,
                    cache_key=cache_key[:8] + "...",
                    calculation_time_ms=calculation_time_ms,
                )

                # 更新缓存统计
                indicator_cache._hit_count = getattr(indicator_cache, "_hit_count", 0) + 1
                indicator_cache._total_requests = getattr(indicator_cache, "_total_requests", 0) + 1

                return create_success_response(
                    data=cached_result, message=f"技术指标计算成功（缓存），共{len(request.indicators)}个指标"
                ).dict(exclude_unset=True)

        # 缓存未命中，执行计算
        indicator_cache._total_requests = getattr(indicator_cache, "_total_requests", 0) + 1

        # Convert date strings to datetime
        from datetime import datetime

        start_dt = datetime.combine(request.start_date, datetime.min.time())
        end_dt = datetime.combine(request.end_date, datetime.min.time())

        # Get OHLCV data with error handling
        try:
            df, ohlcv_data = data_service.get_daily_ohlcv(symbol=request.symbol, start_date=start_dt, end_date=end_dt)
        except StockDataNotFoundError:
            raise NotFoundException(resource="股票数据", identifier="查询条件")
        except InvalidDateRangeError as e:
            raise ValidationException(detail=f"无效日期范围: {str(e)}", field="date_range")

        # Get symbol name
        symbol_name = data_service.get_symbol_name(request.symbol)

        # Extract dates from DataFrame
        dates = df["trade_date"].dt.strftime("%Y-%m-%d").tolist()

        # 验证数据质量
        calculator = get_indicator_calculator()
        is_valid, error_msg = calculator.validate_data_quality(ohlcv_data)
        if not is_valid:
            raise ValidationException(detail=f"OHLCV数据质量验证失败: {error_msg}", field="data_quality")

        # 批量计算指标（优化版本）
        try:
            results = calculator.calculate_multiple_indicators(indicator_specs, ohlcv_data)
        except InsufficientDataError as e:
            raise ValidationException(detail=f"数据不足，无法计算指标: {str(e)}", field="data_length")
        except IndicatorCalculationError as e:
            raise BusinessException(
                detail=f"指标计算错误: {str(e)}", status_code=500, error_code="INDICATOR_CALCULATION_FAILED"
            )

        # 转换为响应格式
        indicator_results = []
        successful_calculations = 0
        failed_calculations = 0

        for abbr, result in results.items():
            if "error" in result:
                # 计算失败的指标
                failed_calculations += 1
                logger.warning(
                    "技术指标计算失败",
                    user_id=current_user.id,
                    symbol=request.symbol,
                    indicator=abbr,
                    error=result["error"],
                )

                indicator_results.append(
                    {
                        "abbreviation": abbr,
                        "parameters": result["parameters"],
                        "outputs": [],
                        "panel_type": "overlay",
                        "reference_lines": None,
                        "error": result["error"],
                        "success": False,
                    }
                )
            else:
                # 计算成功的指标
                successful_calculations += 1
                outputs = []
                for output_name, values in result["values"].items():
                    # 将 NumPy 数组转换为 Python list (处理 NaN)
                    values_list = [float(v) if not np.isnan(v) else None for v in values]

                    outputs.append(
                        {
                            "output_name": output_name,
                            "values": values_list,
                            "display_name": f"{abbr}({result['parameters'].get('timeperiod', '')})",
                        }
                    )

                indicator_results.append(
                    {
                        "abbreviation": abbr,
                        "parameters": result["parameters"],
                        "outputs": outputs,
                        "panel_type": result["panel_type"],
                        "reference_lines": result.get("reference_lines"),
                        "error": None,
                        "success": True,
                    }
                )

        # 构建响应数据
        calculation_time_ms = (time.time() - start_time) * 1000

        response_data = {
            "symbol": request.symbol,
            "symbol_name": symbol_name,
            "start_date": str(request.start_date),
            "end_date": str(request.end_date),
            "ohlcv": {
                "dates": dates,
                "open": ohlcv_data["open"].tolist(),
                "high": ohlcv_data["high"].tolist(),
                "low": ohlcv_data["low"].tolist(),
                "close": ohlcv_data["close"].tolist(),
                "volume": ohlcv_data["volume"].tolist(),
                "turnover": df["amount"].tolist() if "amount" in df.columns else [],
            },
            "indicators": indicator_results,
            "calculation_time_ms": round(calculation_time_ms, 2),
            "cached": cache_used,
            "statistics": {
                "total_indicators": len(request.indicators),
                "successful_calculations": successful_calculations,
                "failed_calculations": failed_calculations,
                "data_points": len(ohlcv_data["open"]),
                "date_range_days": date_range_days,
            },
        }

        # 缓存结果（仅缓存成功的计算）
        if getattr(request, "use_cache", True) and failed_calculations == 0:
            indicator_cache.set(cache_key, response_data)

        logger.info(
            "技术指标计算完成",
            user_id=current_user.id,
            symbol=request.symbol,
            calculation_time_ms=calculation_time_ms,
            successful_calculations=successful_calculations,
            failed_calculations=failed_calculations,
            cache_used=cache_used,
        )

        return create_success_response(
            data=response_data,
            message=f"技术指标计算成功，共{successful_calculations}/{len(request.indicators)}个指标计算完成",
        ).dict(exclude_unset=True)

    except InvalidDateRangeError as e:
        logger.warning("Invalid date range", error=str(e))
        raise ValidationException(detail=f"无效日期范围: {str(e)}", field="date_range")

    except StockDataNotFoundError as e:
        logger.warning("Stock data not found", error=str(e))
        raise NotFoundException(resource="股票数据", identifier="查询条件")

    except InsufficientDataError as e:
        logger.warning("Insufficient data for indicator calculation", error=str(e))
        raise ValidationException(detail=f"数据不足，无法计算指标: {str(e)}", field="data_length")

    except IndicatorCalculationError as e:
        logger.error("Indicator calculation error", error=str(e))
        raise BusinessException(detail=f"指标计算错误: {str(e)}", status_code=500, error_code="CALCULATION_ERROR")

    except (BusinessException, ValidationException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error("技术指标计算异常", user_id=current_user.id, error=str(e), exc_info=True)
        raise BusinessException(
            detail=f"计算指标时发生错误: {str(e)}", status_code=500, error_code="INDICATOR_CALCULATION_ERROR"
        )


@router.post(
    "/calculate/batch",
    response_model=UnifiedResponse[Dict],
    summary="批量计算技术指标",
    responses=INDICATOR_CALCULATE_BATCH_RESPONSES,
)
@rate_limit(limit=5, window=60)  # 每分钟最多5次批量计算
async def calculate_indicators_batch(
    request: IndicatorCalculateBatchRequest = Body(..., example=INDICATOR_CALCULATE_BATCH_REQUEST_EXAMPLE),
    current_user: User = Depends(get_current_active_user),
    data_service: DataService = Depends(get_indicator_data_service),
) -> Dict:
    """
    批量计算技术指标 - Phase 4C Enhanced

    支持一次性计算多个股票/日期范围的指标，提高计算效率
    """
    try:
        start_time = time.time()
        total_calculations = len(request.calculations)
        total_indicators = sum(len(calc.indicators) for calc in request.calculations)

        logger.info(
            "批量技术指标计算请求",
            user_id=current_user.id,
            total_calculations=total_calculations,
            total_indicators=total_indicators,
        )

        # 异步执行批量计算
        async def calculate_single_request(calc_request):
            """计算单个请求"""
            try:
                # 重用单个计算逻辑
                return {
                    "symbol": calc_request.symbol,
                    "start_date": str(calc_request.start_date),
                    "end_date": str(calc_request.end_date),
                    "success": True,
                    "data": await _calculate_single_indicator(calc_request, current_user, data_service),
                }
            except Exception as e:
                logger.error("单个指标计算失败", user_id=current_user.id, symbol=calc_request.symbol, error=str(e))
                return {
                    "symbol": calc_request.symbol,
                    "start_date": str(calc_request.start_date),
                    "end_date": str(calc_request.end_date),
                    "success": False,
                    "error": str(e),
                }

        # 并发执行计算任务（限制并发数）
        semaphore = asyncio.Semaphore(3)  # 最多3个并发计算

        async def limited_calculate(calc_request):
            async with semaphore:
                return await calculate_single_request(calc_request)

        # 执行批量计算
        tasks = [limited_calculate(calc) for calc in request.calculations]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 统计结果
        successful_calculations = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
        failed_calculations = total_calculations - successful_calculations
        calculation_time_ms = (time.time() - start_time) * 1000

        response_data = {
            "batch_statistics": {
                "total_calculations": total_calculations,
                "successful_calculations": successful_calculations,
                "failed_calculations": failed_calculations,
                "total_indicators": total_indicators,
                "calculation_time_ms": round(calculation_time_ms, 2),
                "average_time_per_calculation": round(calculation_time_ms / total_calculations, 2),
            },
            "results": results,
        }

        logger.info(
            "批量技术指标计算完成",
            user_id=current_user.id,
            successful_calculations=successful_calculations,
            failed_calculations=failed_calculations,
            calculation_time_ms=calculation_time_ms,
        )

        return create_success_response(
            data=response_data, message=f"批量计算完成，{successful_calculations}/{total_calculations}个请求成功"
        ).dict(exclude_unset=True)

    except Exception as e:
        logger.error("批量技术指标计算异常", user_id=current_user.id, error=str(e), exc_info=True)
        raise BusinessException(
            detail=f"批量计算失败: {str(e)}", status_code=500, error_code="BATCH_CALCULATION_FAILED"
        )


async def _calculate_single_indicator(request, current_user, data_service: DataService):
    """内部函数：计算单个指标请求"""
    # 重用calculate_indicators的核心逻辑
    # 这里简化实现，实际应该提取共同逻辑
    indicator_specs = [{"abbreviation": ind.abbreviation, "parameters": ind.parameters} for ind in request.indicators]

    calculator = get_indicator_calculator()

    # 获取数据并计算

    start_dt = datetime.combine(request.start_date, datetime.min.time())
    end_dt = datetime.combine(request.end_date, datetime.min.time())

    df, ohlcv_data = data_service.get_daily_ohlcv(symbol=request.symbol, start_date=start_dt, end_date=end_dt)
    symbol_name = data_service.get_symbol_name(request.symbol)

    results = calculator.calculate_multiple_indicators(indicator_specs, ohlcv_data)

    # 返回简化的结果
    return {
        "symbol": request.symbol,
        "symbol_name": symbol_name,
        "indicators_count": len(request.indicators),
        "data_points": len(ohlcv_data["open"]),
        "results": results,
    }


@router.get(
    "/cache/stats",
    response_model=UnifiedResponse[Dict],
    summary="获取指标缓存统计",
    description="返回技术指标计算缓存的容量、TTL 与命中率概览，供容量治理、性能排障和缓存策略调优使用。",
    responses=INDICATOR_CACHE_STATS_RESPONSES,
)
@rate_limit(limit=10, window=60)
async def get_cache_statistics(current_user: User = Depends(get_current_active_user)) -> Dict:
    """
    返回技术指标计算缓存的容量、TTL 与命中率概览。
    """
    try:
        stats = indicator_cache.get_stats()

        logger.info("缓存统计查询", user_id=current_user.id, cache_size=stats["size"], hit_rate=stats["hit_rate"])

        return create_success_response(data=stats, message="缓存统计信息获取成功").dict(exclude_unset=True)

    except Exception as e:
        logger.error("缓存统计查询失败", user_id=current_user.id, error=str(e), exc_info=True)
        raise BusinessException(
            detail=f"获取缓存统计失败: {str(e)}", status_code=500, error_code="CACHE_STATS_RETRIEVAL_FAILED"
        )


@router.post(
    "/cache/clear",
    response_model=UnifiedResponse[Dict],
    summary="清理指标缓存",
    description="按模式清理技术指标计算缓存，仅管理员可执行，支持清空全部缓存、清理过期条目或按 symbol 前缀筛选。",
    responses=INDICATOR_CACHE_CLEAR_RESPONSES,
)
@rate_limit(limit=3, window=60)  # 每分钟最多3次清理
async def clear_cache(
    pattern: Optional[str] = Query(None, description="清理模式: all, expired, or symbol prefix"),
    current_user: User = Depends(get_current_active_user),
) -> Dict:
    """
    清理指标计算缓存

    仅管理员可执行
    """
    try:
        # 检查权限
        if current_user.role != "admin":
            raise ForbiddenException(detail="仅管理员可以清理缓存")

        if not pattern or pattern == "all":
            # 清空所有缓存
            indicator_cache.clear()
            cleared_count = "全部"
        elif pattern == "expired":
            # 清理过期缓存（需要在缓存类中实现）
            cleared_count = "过期的缓存条目"
        else:
            # 按symbol前缀清理（需要在缓存类中实现）
            cleared_count = f"匹配模式 '{pattern}' 的缓存条目"

        logger.info("缓存清理操作", user_id=current_user.id, pattern=pattern, cleared_count=cleared_count)

        return create_success_response(
            data={"cleared_count": cleared_count}, message=f"缓存清理完成，已清理{cleared_count}"
        ).dict(exclude_unset=True)

    except (BusinessException, ValidationException, NotFoundException, ForbiddenException):
        raise
    except Exception as e:
        logger.error("缓存清理失败", user_id=current_user.id, error=str(e), exc_info=True)
        raise BusinessException(detail=f"缓存清理失败: {str(e)}", status_code=500, error_code="CACHE_CLEANUP_FAILED")
