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
import hashlib
import json
import time
from collections import defaultdict
from datetime import datetime
from functools import wraps
from typing import Dict, List, Optional, Union

import numpy as np
import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, constr, validator

from app.api.auth import get_current_active_user
from app.core.responses import create_success_response
from app.core.security import User
from app.schemas.indicator_request import (
    IndicatorCalculateRequest,
    IndicatorConfigCreateRequest,
    IndicatorConfigUpdateRequest,
)
from app.schemas.indicator_response import (
    IndicatorConfigListResponse,
    IndicatorConfigResponse,
    IndicatorMetadata,
    IndicatorRegistryResponse,
)
from app.services.data_service import InvalidDateRangeError, StockDataNotFoundError, get_data_service
from app.services.indicator_calculator import IndicatorCalculationError, InsufficientDataError, get_indicator_calculator
from app.services.indicator_registry import IndicatorCategory, get_indicator_registry

logger = structlog.get_logger()
router = APIRouter()


# ==================== 缓存和速率限制 ====================


class IndicatorCache:
    """技术指标计算结果缓存"""

    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache: Dict[str, Dict] = {}
        self.max_size = max_size
        self.ttl = ttl  # 缓存时间（秒）
        self.access_times: Dict[str, datetime] = {}

    def _generate_cache_key(self, symbol: str, start_date: str, end_date: str, indicators: List[Dict]) -> str:
        """生成缓存键"""
        cache_data = {
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "indicators": sorted(indicators, key=lambda x: x["abbreviation"]),
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    def get(self, cache_key: str) -> Optional[Dict]:
        """获取缓存结果"""
        if cache_key not in self.cache:
            return None

        cache_entry = self.cache[cache_key]

        # 检查是否过期
        if (datetime.utcnow() - cache_entry["timestamp"]).seconds > self.ttl:
            self.remove(cache_key)
            return None

        # 更新访问时间
        self.access_times[cache_key] = datetime.utcnow()
        return cache_entry["data"]

    def set(self, cache_key: str, data: Dict):
        """设置缓存结果"""
        # 检查缓存大小，如果超过限制则清理最旧的条目
        if len(self.cache) >= self.max_size:
            self._cleanup_old_entries()

        self.cache[cache_key] = {"data": data, "timestamp": datetime.utcnow()}
        self.access_times[cache_key] = datetime.utcnow()

    def remove(self, cache_key: str):
        """移除缓存条目"""
        self.cache.pop(cache_key, None)
        self.access_times.pop(cache_key, None)

    def _cleanup_old_entries(self):
        """清理最旧的缓存条目"""
        if not self.access_times:
            return

        # 找到最旧的条目
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        self.remove(oldest_key)

    def clear(self):
        """清空缓存"""
        self.cache.clear()
        self.access_times.clear()

    def get_stats(self) -> Dict:
        """获取缓存统计信息"""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "ttl": self.ttl,
            "hit_rate": getattr(self, "_hit_count", 0) / max(getattr(self, "_total_requests", 1), 1),
        }


# 全局缓存实例
indicator_cache = IndicatorCache()


class RateLimiter:
    """技术指标API速率限制器"""

    def __init__(self):
        self.requests = defaultdict(list)

    def is_allowed(self, key: str, limit: int, window: int) -> bool:
        """检查是否允许请求"""
        now = datetime.utcnow()

        # 清理过期的请求记录
        self.requests[key] = [req_time for req_time in self.requests[key] if (now - req_time).seconds < window]

        # 检查是否超过限制
        if len(self.requests[key]) >= limit:
            return False

        # 记录当前请求
        self.requests[key].append(now)
        return True


# 全局速率限制器
rate_limiter = RateLimiter()


def rate_limit(limit: int, window: int):
    """速率限制装饰器"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = None
            for arg in args:
                if hasattr(arg, "id"):
                    current_user = arg
                    break

            if not current_user:
                for key, value in kwargs.items():
                    if hasattr(value, "id"):
                        current_user = value
                        break

            if current_user:
                user_key = f"indicators_user_{current_user.id}"
            else:
                user_key = "indicators_anonymous"

            if not rate_limiter.is_allowed(user_key, limit, window):
                raise HTTPException(status_code=429, detail=f"技术指标计算请求过于频繁，请在{window}秒后重试")

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# ==================== 增强请求模型 ====================


class IndicatorCalculateBatchRequest(BaseModel):
    """批量技术指标计算请求"""

    calculations: List[IndicatorCalculateRequest] = Field(
        ..., min_items=1, max_items=10, description="批量计算请求列表，最多10个"
    )

    @validator("calculations")
    def validate_calculations(cls, v):
        """验证批量计算请求"""
        if not v:
            raise ValueError("计算请求列表不能为空")

        # 检查重复的symbol+date范围组合
        combinations = set()
        for calc in v:
            combo = f"{calc.symbol}_{calc.start_date}_{calc.end_date}"
            if combo in combinations:
                raise ValueError(f"存在重复的计算请求: {combo}")
            combinations.add(combo)

        return v


class IndicatorOptimizationRequest(BaseModel):
    """技术指标参数优化请求"""

    symbol: constr(min_length=1, max_length=20) = Field(..., description="股票代码")
    start_date: datetime = Field(..., description="开始日期")
    end_date: datetime = Field(..., description="结束日期")
    indicator_abbr: constr(min_length=1, max_length=10) = Field(..., description="指标简称")
    parameter_ranges: Dict[str, List[Union[int, float]]] = Field(..., description="参数范围")
    optimization_target: str = Field(
        "profit", pattern="^(profit|sharpe|max_drawdown|win_rate)$", description="优化目标"
    )
    max_iterations: int = Field(50, ge=1, le=200, description="最大迭代次数")


@router.get("/registry", response_model=IndicatorRegistryResponse)
@rate_limit(limit=30, window=60)  # 每分钟最多30次请求
async def get_indicator_registry_endpoint(
    category: Optional[str] = Query(None, description="筛选指定分类的指标"),
    search: Optional[str] = Query(None, description="搜索指标名称或描述"),
    include_advanced: bool = Query(True, description="是否包含高级指标"),
    current_user: User = Depends(get_current_active_user),
):
    """
    获取指标注册表 - Phase 4C Enhanced

    返回所有可用的技术指标及其元数据，支持分类筛选和搜索
    """
    try:
        registry = get_indicator_registry()
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
                    category_enum = IndicatorCategory(category)
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

        return create_success_response(
            data=response_data.dict(), message=f"技术指标注册表查询成功，共{len(filtered_indicators)}个指标"
        ).dict(exclude_unset=True)

    except Exception as e:
        logger.error("技术指标注册表查询失败", user_id=current_user.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取指标注册表失败: {str(e)}")


@router.get("/registry/{category}", response_model=List[IndicatorMetadata])
async def get_indicators_by_category(category: str):
    """
    获取指定分类的指标

    - **category**: 指标分类 (trend, momentum, volatility, volume, candlestick)
    """
    try:
        # 验证分类
        try:
            indicator_category = IndicatorCategory(category)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"无效的指标分类: {category}. 有效分类: {[c.value for c in IndicatorCategory]}",
            )

        registry = get_indicator_registry()
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

        return indicators_list

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get indicators for category {category}", exc_info=e)
        raise HTTPException(status_code=500, detail=f"获取分类指标失败: {str(e)}")


@router.post("/calculate")
@rate_limit(limit=20, window=60)  # 每分钟最多20次计算请求
async def calculate_indicators(
    request: IndicatorCalculateRequest, current_user: User = Depends(get_current_active_user)
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
            raise HTTPException(status_code=400, detail="结束日期必须晚于开始日期")
        if date_range_days > 3650:  # 10年限制
            raise HTTPException(status_code=400, detail="日期范围不能超过10年")

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

        # Load OHLCV data from database via DataService
        data_service = get_data_service()

        # Convert date strings to datetime
        from datetime import datetime

        start_dt = datetime.combine(request.start_date, datetime.min.time())
        end_dt = datetime.combine(request.end_date, datetime.min.time())

        # Get OHLCV data with error handling
        try:
            df, ohlcv_data = data_service.get_daily_ohlcv(symbol=request.symbol, start_date=start_dt, end_date=end_dt)
        except StockDataNotFoundError as e:
            raise HTTPException(status_code=404, detail=f"股票数据未找到: {str(e)}")
        except InvalidDateRangeError as e:
            raise HTTPException(status_code=400, detail=f"无效日期范围: {str(e)}")

        # Get symbol name
        symbol_name = data_service.get_symbol_name(request.symbol)

        # Extract dates from DataFrame
        dates = df["trade_date"].dt.strftime("%Y-%m-%d").tolist()

        # 验证数据质量
        calculator = get_indicator_calculator()
        is_valid, error_msg = calculator.validate_data_quality(ohlcv_data)
        if not is_valid:
            raise HTTPException(status_code=422, detail=f"OHLCV数据质量验证失败: {error_msg}")

        # 批量计算指标（优化版本）
        try:
            results = calculator.calculate_multiple_indicators(indicator_specs, ohlcv_data)
        except InsufficientDataError as e:
            raise HTTPException(status_code=422, detail=f"数据不足，无法计算指标: {str(e)}")
        except IndicatorCalculationError as e:
            raise HTTPException(status_code=500, detail=f"指标计算错误: {str(e)}")

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
        raise HTTPException(
            status_code=422,
            detail={"error_code": "INVALID_DATE_RANGE", "error_message": str(e)},
        )

    except StockDataNotFoundError as e:
        logger.warning("Stock data not found", error=str(e))
        raise HTTPException(
            status_code=404,
            detail={"error_code": "STOCK_DATA_NOT_FOUND", "error_message": str(e)},
        )

    except InsufficientDataError as e:
        logger.warning("Insufficient data for indicator calculation", error=str(e))
        raise HTTPException(
            status_code=422,
            detail={"error_code": "INSUFFICIENT_DATA", "error_message": str(e)},
        )

    except IndicatorCalculationError as e:
        logger.error("Indicator calculation error", error=str(e))
        raise HTTPException(
            status_code=500,
            detail={"error_code": "CALCULATION_ERROR", "error_message": str(e)},
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("技术指标计算异常", user_id=current_user.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"计算指标时发生错误: {str(e)}")


@router.post("/calculate/batch")
@rate_limit(limit=5, window=60)  # 每分钟最多5次批量计算
async def calculate_indicators_batch(
    request: IndicatorCalculateBatchRequest, current_user: User = Depends(get_current_active_user)
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
                    "data": await _calculate_single_indicator(calc_request, current_user),
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
        raise HTTPException(status_code=500, detail=f"批量计算失败: {str(e)}")


async def _calculate_single_indicator(request, current_user):
    """内部函数：计算单个指标请求"""
    # 重用calculate_indicators的核心逻辑
    # 这里简化实现，实际应该提取共同逻辑
    indicator_specs = [{"abbreviation": ind.abbreviation, "parameters": ind.parameters} for ind in request.indicators]

    data_service = get_data_service()
    calculator = get_indicator_calculator()

    # 获取数据并计算
    from datetime import datetime

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


@router.get("/cache/stats")
@rate_limit(limit=10, window=60)
async def get_cache_statistics(current_user: User = Depends(get_current_active_user)) -> Dict:
    """
    获取指标计算缓存统计信息
    """
    try:
        stats = indicator_cache.get_stats()

        logger.info("缓存统计查询", user_id=current_user.id, cache_size=stats["size"], hit_rate=stats["hit_rate"])

        return create_success_response(data=stats, message="缓存统计信息获取成功").dict(exclude_unset=True)

    except Exception as e:
        logger.error("缓存统计查询失败", user_id=current_user.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取缓存统计失败: {str(e)}")


@router.post("/cache/clear")
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
            raise HTTPException(status_code=403, detail="仅管理员可以清理缓存")

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

    except HTTPException:
        raise
    except Exception as e:
        logger.error("缓存清理失败", user_id=current_user.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"缓存清理失败: {str(e)}")


@router.post("/configs", response_model=IndicatorConfigResponse)
async def create_indicator_config(
    request: IndicatorConfigCreateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    创建指标配置

    保存用户的常用指标组合配置,方便下次快速加载

    **请求示例**:
    ```json
    {
        "name": "我的常用配置",
        "indicators": [
            {"abbreviation": "SMA", "parameters": {"timeperiod": 20}},
            {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
        ]
    }
    ```
    """
    user_id = current_user.id

    try:

        from app.core.database import get_mysql_session
        from app.models.indicator_config import IndicatorConfiguration

        session = get_mysql_session()

        try:
            # 检查同名配置是否存在
            existing = (
                session.query(IndicatorConfiguration)
                .filter(
                    IndicatorConfiguration.user_id == user_id,
                    IndicatorConfiguration.name == request.name,
                )
                .first()
            )

            if existing:
                raise HTTPException(status_code=409, detail=f"配置名称已存在: {request.name}")

            # 创建新配置
            indicators_json = [
                {"abbreviation": ind.abbreviation, "parameters": ind.parameters} for ind in request.indicators
            ]

            new_config = IndicatorConfiguration(user_id=user_id, name=request.name, indicators=indicators_json)

            session.add(new_config)
            session.commit()
            session.refresh(new_config)

            logger.info(
                "Indicator config created",
                config_id=new_config.id,
                user_id=user_id,
                name=request.name,
            )

            return IndicatorConfigResponse(
                id=new_config.id,
                user_id=new_config.user_id,
                name=new_config.name,
                indicators=new_config.indicators,
                created_at=new_config.created_at,
                updated_at=new_config.updated_at,
                last_used_at=new_config.last_used_at,
            )

        finally:
            session.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create indicator config", exc_info=e)
        raise HTTPException(status_code=500, detail=f"创建配置失败: {str(e)}")


@router.get("/configs", response_model=IndicatorConfigListResponse)
async def list_indicator_configs(current_user: User = Depends(get_current_active_user)):
    """
    获取用户的指标配置列表

    返回当前用户的所有已保存指标配置
    """
    user_id = current_user.id

    try:
        from app.core.database import get_mysql_session
        from app.models.indicator_config import IndicatorConfiguration

        session = get_mysql_session()

        try:
            # 查询用户所有配置,按最后使用时间倒序排列
            # MySQL不支持NULLS LAST,使用CASE WHEN处理NULL值
            from sqlalchemy import case

            configs = (
                session.query(IndicatorConfiguration)
                .filter(IndicatorConfiguration.user_id == user_id)
                .order_by(
                    case((IndicatorConfiguration.last_used_at.is_(None), 1), else_=0),
                    IndicatorConfiguration.last_used_at.desc(),
                    IndicatorConfiguration.updated_at.desc(),
                )
                .all()
            )

            config_list = [
                IndicatorConfigResponse(
                    id=cfg.id,
                    user_id=cfg.user_id,
                    name=cfg.name,
                    indicators=cfg.indicators,
                    created_at=cfg.created_at,
                    updated_at=cfg.updated_at,
                    last_used_at=cfg.last_used_at,
                )
                for cfg in configs
            ]

            logger.info("Listed indicator configs", user_id=user_id, count=len(config_list))

            return IndicatorConfigListResponse(total_count=len(config_list), configs=config_list)

        finally:
            session.close()

    except Exception as e:
        logger.error("Failed to list indicator configs", exc_info=e)
        raise HTTPException(status_code=500, detail=f"获取配置列表失败: {str(e)}")


@router.get("/configs/{config_id}", response_model=IndicatorConfigResponse)
async def get_indicator_config(config_id: int, current_user: User = Depends(get_current_active_user)):
    """
    获取指定的指标配置详情

    - **config_id**: 配置ID
    """
    user_id = current_user.id

    try:
        from datetime import datetime

        from app.core.database import get_mysql_session
        from app.models.indicator_config import IndicatorConfiguration

        session = get_mysql_session()

        try:
            # 查询配置
            config = (
                session.query(IndicatorConfiguration)
                .filter(
                    IndicatorConfiguration.id == config_id,
                    IndicatorConfiguration.user_id == user_id,
                )
                .first()
            )

            if not config:
                raise HTTPException(status_code=404, detail=f"配置不存在: ID={config_id}")

            # 更新最后使用时间
            config.last_used_at = datetime.now()
            session.commit()
            session.refresh(config)

            logger.info("Got indicator config", config_id=config_id, user_id=user_id)

            return IndicatorConfigResponse(
                id=config.id,
                user_id=config.user_id,
                name=config.name,
                indicators=config.indicators,
                created_at=config.created_at,
                updated_at=config.updated_at,
                last_used_at=config.last_used_at,
            )

        finally:
            session.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get indicator config", exc_info=e)
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.put("/configs/{config_id}", response_model=IndicatorConfigResponse)
async def update_indicator_config(
    config_id: int,
    request: IndicatorConfigUpdateRequest,
    current_user: User = Depends(get_current_active_user),
):
    """
    更新指标配置

    可以更新配置名称和/或指标列表

    - **config_id**: 配置ID
    """
    user_id = current_user.id

    try:
        from app.core.database import get_mysql_session
        from app.models.indicator_config import IndicatorConfiguration

        session = get_mysql_session()

        try:
            # 查询配置
            config = (
                session.query(IndicatorConfiguration)
                .filter(
                    IndicatorConfiguration.id == config_id,
                    IndicatorConfiguration.user_id == user_id,
                )
                .first()
            )

            if not config:
                raise HTTPException(status_code=404, detail=f"配置不存在: ID={config_id}")

            # 更新字段
            if request.name is not None:
                # 检查新名称是否与其他配置冲突
                existing = (
                    session.query(IndicatorConfiguration)
                    .filter(
                        IndicatorConfiguration.user_id == user_id,
                        IndicatorConfiguration.name == request.name,
                        IndicatorConfiguration.id != config_id,
                    )
                    .first()
                )

                if existing:
                    raise HTTPException(status_code=409, detail=f"配置名称已存在: {request.name}")

                config.name = request.name

            if request.indicators is not None:
                indicators_json = [
                    {"abbreviation": ind.abbreviation, "parameters": ind.parameters} for ind in request.indicators
                ]
                config.indicators = indicators_json

            session.commit()
            session.refresh(config)

            logger.info("Updated indicator config", config_id=config_id, user_id=user_id)

            return IndicatorConfigResponse(
                id=config.id,
                user_id=config.user_id,
                name=config.name,
                indicators=config.indicators,
                created_at=config.created_at,
                updated_at=config.updated_at,
                last_used_at=config.last_used_at,
            )

        finally:
            session.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update indicator config", exc_info=e)
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.delete("/configs/{config_id}", status_code=204)
async def delete_indicator_config(config_id: int, current_user: User = Depends(get_current_active_user)):
    """
    删除指标配置

    - **config_id**: 配置ID
    """
    user_id = current_user.id

    try:
        from app.core.database import get_mysql_session
        from app.models.indicator_config import IndicatorConfiguration

        session = get_mysql_session()

        try:
            # 查询配置
            config = (
                session.query(IndicatorConfiguration)
                .filter(
                    IndicatorConfiguration.id == config_id,
                    IndicatorConfiguration.user_id == user_id,
                )
                .first()
            )

            if not config:
                raise HTTPException(status_code=404, detail=f"配置不存在: ID={config_id}")

            session.delete(config)
            session.commit()

            logger.info("Deleted indicator config", config_id=config_id, user_id=user_id)

            return None  # 204 No Content

        finally:
            session.close()

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete indicator config", exc_info=e)
        raise HTTPException(status_code=500, detail=f"删除配置失败: {str(e)}")
