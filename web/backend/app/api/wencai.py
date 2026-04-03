#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
问财API路由

提供问财股票筛选功能的RESTful API端点

作者: MyStocks Backend Team
创建日期: 2025-10-17
"""

import logging
import os
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, get_db
from app.mock.unified_mock_data import get_mock_data_manager
from app.openapi_config import COMMON_RESPONSES
from app.schemas.wencai_schemas import (
    WencaiCustomQueryRequest,
    WencaiCustomQueryResponse,
    WencaiHistoryResponse,
    WencaiQueryInfo,
    WencaiQueryListResponse,
    WencaiQueryRequest,
    WencaiQueryResponse,
    WencaiRefreshResponse,
    WencaiResultsResponse,
)
from app.services.wencai_service import WencaiService

# 配置日志
logger = logging.getLogger(__name__)

WENCAI_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
}

WENCAI_QUERY_REQUEST_EXAMPLES = {
    "execute_qs_9_query": {
        "summary": "执行预定义问财查询",
        "description": "执行预定义的强势股筛选模板，并抓取前两页结果保存到数据库。",
        "value": {
            "query_name": "qs_9",
            "pages": 2,
        },
    }
}

WENCAI_CUSTOM_QUERY_REQUEST_EXAMPLES = {
    "execute_custom_breakout_query": {
        "summary": "执行自定义自然语言查询",
        "description": "查询涨幅、换手率和成交额同时满足条件的强势股，不写入数据库。",
        "value": {
            "query_text": "请列出今天涨幅超过5%且换手率大于3%的股票",
            "pages": 1,
        },
    }
}

WENCAI_QUERY_LIST_SUCCESS_RESPONSE = {
    200: {
        "description": "问财预定义查询模板列表",
        "content": {
            "application/json": {
                "example": {
                    "queries": [
                        {
                            "id": 1,
                            "query_name": "qs_1",
                            "query_text": "请列举出20天内出现过涨停的股票",
                            "description": "涨停板复盘模板",
                            "is_active": True,
                            "created_at": "2025-10-17T09:00:00",
                            "updated_at": "2025-10-17T09:00:00",
                        }
                    ],
                    "total": 9,
                }
            }
        },
    }
}

WENCAI_QUERY_INFO_SUCCESS_RESPONSE = {
    200: {
        "description": "指定问财查询模板详情",
        "content": {
            "application/json": {
                "example": {
                    "id": 9,
                    "query_name": "qs_9",
                    "query_text": "请列出近期强势突破且量能放大的股票",
                    "description": "强势突破模板",
                    "is_active": True,
                    "created_at": "2025-10-17T09:00:00",
                    "updated_at": "2025-10-17T09:00:00",
                }
            }
        },
    }
}

WENCAI_RESULTS_SUCCESS_RESPONSE = {
    200: {
        "description": "指定问财查询的最新结果集",
        "content": {
            "application/json": {
                "example": {
                    "query_name": "qs_9",
                    "total": 45,
                    "results": [
                        {
                            "股票代码": "000001",
                            "股票简称": "平安银行",
                            "涨跌幅": "6.5%",
                            "fetch_time": "2025-10-17T09:00:00",
                        }
                    ],
                    "columns": ["股票代码", "股票简称", "涨跌幅", "fetch_time"],
                    "latest_fetch_time": "2025-10-17T09:00:00",
                }
            }
        },
    }
}

WENCAI_REFRESH_SUCCESS_RESPONSE = {
    200: {
        "description": "后台刷新任务已成功提交",
        "content": {
            "application/json": {
                "example": {
                    "status": "refreshing",
                    "message": "后台刷新任务已启动",
                    "task_id": None,
                    "query_name": "qs_9",
                }
            }
        },
    }
}

WENCAI_HISTORY_SUCCESS_RESPONSE = {
    200: {
        "description": "指定问财查询的历史统计数据",
        "content": {
            "application/json": {
                "example": {
                    "query_name": "qs_9",
                    "date_range": ["2025-10-10", "2025-10-17"],
                    "history": [
                        {
                            "date": "2025-10-17",
                            "total_records": 45,
                            "fetch_count": 3,
                        }
                    ],
                    "total_days": 7,
                }
            }
        },
    }
}

WENCAI_HEALTH_SUCCESS_RESPONSE = {
    200: {
        "description": "问财接口服务健康状态",
        "content": {
            "application/json": {
                "example": {
                    "status": "healthy",
                    "service": "wencai",
                    "version": "1.0.0",
                }
            }
        },
    }
}

# 创建路由
router = APIRouter(prefix="/api/market/wencai", tags=["wencai"], responses=WENCAI_ROUTE_RESPONSES)


# ============================================================================
# API端点
# ============================================================================


@router.get(
    "/queries",
    response_model=WencaiQueryListResponse,
    summary="获取所有查询列表",
    description="获取所有已注册的问财查询模板，返回模板名称、查询语句、启用状态和维护说明。",
    responses=WENCAI_QUERY_LIST_SUCCESS_RESPONSE,
)
async def get_all_queries(db: Session = Depends(get_db)) -> WencaiQueryListResponse:
    """
    获取所有查询列表

    返回所有预定义的问财查询配置（qs_1 ~ qs_9）
    支持Mock数据模式切换
    """
    try:
        # 检查是否使用Mock数据
        use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

        if use_mock:
            # 使用Mock数据
            mock_manager = get_mock_data_manager()
            queries_data = mock_manager.get_data("wencai", query_name="all")

            return WencaiQueryListResponse(
                queries=queries_data.get("queries", []), total=len(queries_data.get("queries", []))
            )
        else:
            # 使用真实数据库
            service = WencaiService(db=db)
            queries = service.get_all_queries()
            return WencaiQueryListResponse(queries=queries, total=len(queries))

    except Exception as e:
        logger.error("Failed to get queries: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取查询列表失败: {str(e)}")


@router.get(
    "/queries/{query_name}",
    response_model=WencaiQueryInfo,
    summary="获取指定查询信息",
    description="根据预定义查询名称获取单个问财模板详情，便于前端展示模板说明和执行入口。",
    responses=WENCAI_QUERY_INFO_SUCCESS_RESPONSE,
)
async def get_query_by_name(
    query_name: str = Path(..., description="预定义问财查询名称，如 qs_1 到 qs_9"),
    db: Session = Depends(get_db),
) -> WencaiQueryInfo:
    """
    获取指定查询信息

    Args:
        query_name: 查询名称（如qs_1）

    Returns:
        查询配置详情
    """
    try:
        service = WencaiService(db=db)
        query = service.get_query_by_name(query_name)

        if not query:
            raise HTTPException(status_code=404, detail=f"查询'{query_name}'不存在")

        return WencaiQueryInfo(**query)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get query {query_name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取查询失败: {str(e)}")


@router.post(
    "/query",
    response_model=WencaiQueryResponse,
    summary="执行问财查询",
    description="执行指定的预定义问财查询模板，抓取结果并将清洗后的数据落库，返回本次执行统计。",
)
async def execute_query(
    request: WencaiQueryRequest = Body(..., openapi_examples=WENCAI_QUERY_REQUEST_EXAMPLES),
    db: Session = Depends(get_db),
) -> WencaiQueryResponse:
    """
    执行问财查询

    从问财API获取数据，清理、去重后保存到数据库
    支持Mock数据模式切换

    Args:
        request: 查询请求（包含query_name和pages）

    Returns:
        查询执行结果统计
    """
    try:
        logger.info("Executing query: {request.query_name}, pages={request.pages}")

        # 检查是否使用Mock数据
        use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

        if use_mock:
            # 使用Mock数据
            mock_manager = get_mock_data_manager()
            result_data = mock_manager.get_data("wencai", query_name=request.query_name)

            return WencaiQueryResponse(
                query_name=request.query_name,
                success=True,
                message=f"Mock查询执行成功: {request.query_name}",
                new_records=len(result_data.get("query_result", {}).get("results", [])),
                total_records=len(result_data.get("query_result", {}).get("results", [])),
                execution_time=0.1,
                timestamp=datetime.now(),
            )
        else:
            # 使用真实数据库
            service = WencaiService(db=db)
            result = service.fetch_and_save(query_name=request.query_name, pages=request.pages)
            return WencaiQueryResponse(**result)

    except ValueError as e:
        logger.warning("Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to execute query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询执行失败: {str(e)}")


@router.get(
    "/results/{query_name}",
    response_model=WencaiResultsResponse,
    summary="获取查询结果",
    description="获取指定问财查询模板的最新结果集，支持分页读取历史落库后的筛选结果。",
    responses=WENCAI_RESULTS_SUCCESS_RESPONSE,
)
async def get_query_results(
    query_name: str = Path(..., description="预定义问财查询名称，如 qs_1 到 qs_9"),
    limit: int = Query(100, ge=1, le=1000, description="返回条数"),
    offset: int = Query(0, ge=0, description="偏移量"),
    db: Session = Depends(get_db),
) -> WencaiResultsResponse:
    """
    获取查询结果

    从数据库获取指定查询的最新结果

    Args:
        query_name: 查询名称
        limit: 返回条数（1-1000）
        offset: 偏移量（用于分页）

    Returns:
        查询结果列表
    """
    try:
        service = WencaiService(db=db)
        results = service.get_query_results(query_name=query_name, limit=limit, offset=offset)

        return WencaiResultsResponse(**results)

    except Exception as e:
        logger.error("Failed to get results for {query_name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取结果失败: {str(e)}")


@router.post(
    "/refresh/{query_name}",
    response_model=WencaiRefreshResponse,
    summary="刷新查询数据",
    description="在后台异步刷新指定问财查询模板的数据，并立即返回任务受理状态。",
    responses=WENCAI_REFRESH_SUCCESS_RESPONSE,
)
async def refresh_query(
    background_tasks: BackgroundTasks,
    query_name: str = Path(..., description="需要刷新的预定义问财查询名称，如 qs_1 到 qs_9"),
    pages: int = Query(1, ge=1, le=10, description="获取页数"),
    db: Session = Depends(get_db),
) -> WencaiRefreshResponse:
    """
    刷新查询数据（后台任务）

    在后台异步执行数据刷新，立即返回任务状态

    Args:
        query_name: 查询名称
        pages: 获取页数
        background_tasks: FastAPI后台任务管理器

    Returns:
        任务状态响应
    """
    try:
        # 验证查询是否存在
        service = WencaiService(db=db)
        query = service.get_query_by_name(query_name)

        if not query:
            raise HTTPException(status_code=404, detail=f"查询'{query_name}'不存在")

        # 添加后台任务
        background_tasks.add_task(_refresh_query_task, query_name=query_name, pages=pages)

        logger.info("Background refresh task added for %(query_name)s")

        return WencaiRefreshResponse(
            status="refreshing",
            message="后台刷新任务已启动",
            task_id=None,  # 如果使用Celery可以返回task_id
            query_name=query_name,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to start refresh task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"启动刷新任务失败: {str(e)}")


@router.get(
    "/history/{query_name}",
    response_model=WencaiHistoryResponse,
    summary="获取查询历史",
    description="获取指定问财查询模板在最近若干天内的抓取历史和记录数量变化。",
    responses=WENCAI_HISTORY_SUCCESS_RESPONSE,
)
async def get_query_history(
    query_name: str = Path(..., description="预定义问财查询名称，如 qs_1 到 qs_9"),
    days: int = Query(7, ge=1, le=30, description="查询天数"),
    db: Session = Depends(get_db),
) -> WencaiHistoryResponse:
    """
    获取查询历史

    统计指定天数内的查询数据情况

    Args:
        query_name: 查询名称
        days: 查询天数（1-30）

    Returns:
        历史统计数据
    """
    try:
        service = WencaiService(db=db)
        history = service.get_query_history(query_name=query_name, days=days)

        return WencaiHistoryResponse(**history)

    except Exception as e:
        logger.error("Failed to get history for {query_name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取历史数据失败: {str(e)}")


@router.post(
    "/custom-query",
    response_model=WencaiCustomQueryResponse,
    summary="执行自定义查询",
    description="执行用户输入的自然语言问财查询，直接返回结果预览而不写入数据库。",
)
async def execute_custom_query(
    request: WencaiCustomQueryRequest = Body(..., openapi_examples=WENCAI_CUSTOM_QUERY_REQUEST_EXAMPLES),
    db: Session = Depends(get_db),
) -> WencaiCustomQueryResponse:
    """
    执行自定义查询

    用户可以输入任意自然语言查询，直接获取结果
    支持Mock数据模式切换

    Args:
        request: 自定义查询请求（包含query_text和pages）

    Returns:
        查询结果（不保存到数据库）
    """
    try:
        logger.info("Executing custom query: {request.query_text[:50]}..., pages={request.pages}")

        # 检查是否使用Mock数据
        use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"

        if use_mock:
            # 使用Mock数据 - 模拟自定义查询
            get_mock_data_manager()

            # 生成模拟查询结果
            mock_results = [
                {
                    "stock_code": f"000{request.pages}{i:02d}",
                    "stock_name": f"测试股票{i}",
                    "current_price": round(10 + i * 0.5, 2),
                    "change_percent": round((i % 10 - 5) * 0.1, 2),
                    "volume": i * 1000,
                    "market_cap": i * 1000000,
                }
                for i in range(request.pages * 10)
            ]

            return WencaiCustomQueryResponse(
                success=True,
                message=f"Mock自定义查询成功，共获取 {len(mock_results)} 条数据",
                query_text=request.query_text,
                total_records=len(mock_results),
                results=mock_results,
                columns=["stock_code", "stock_name", "current_price", "change_percent", "volume", "market_cap"],
                fetch_time=datetime.now(),
            )
        else:
            # 使用真实数据库
            service = WencaiService(db=db)
            df = service.adapter.fetch_data(query=request.query_text, pages=request.pages)

            if df.empty:
                return WencaiCustomQueryResponse(
                    success=True,
                    message="查询成功，但没有找到匹配的数据",
                    query_text=request.query_text,
                    total_records=0,
                    results=[],
                    columns=[],
                    fetch_time=datetime.now(),
                )

            results = df.to_dict("records")
            columns = df.columns.tolist()

            return WencaiCustomQueryResponse(
                success=True,
                message=f"查询成功，共获取 {len(results)} 条数据",
                query_text=request.query_text,
                total_records=len(results),
                results=results,
                columns=columns,
                fetch_time=datetime.now(),
            )

    except ValueError as e:
        logger.warning("Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to execute custom query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"自定义查询执行失败: {str(e)}")


@router.get(
    "/health",
    summary="健康检查",
    description="检查问财 API 服务是否可用，并返回当前服务名称与版本信息。",
    responses=WENCAI_HEALTH_SUCCESS_RESPONSE,
)
async def health_check():
    """
    健康检查

    检查服务是否正常运行

    Returns:
        健康状态
    """
    return {"status": "healthy", "service": "wencai", "version": "1.0.0"}


# ============================================================================
# 辅助函数
# ============================================================================


async def _refresh_query_task(query_name: str, pages: int = 1):
    """
    后台刷新任务

    Args:
        query_name: 查询名称
        pages: 获取页数
    """
    # 创建新的数据库会话
    db = SessionLocal()
    try:
        logger.info("[Background] Starting refresh for %(query_name)s")

        service = WencaiService(db=db)

        result = service.fetch_and_save(query_name=query_name, pages=pages)

        logger.info("[Background] Refresh completed for {query_name}: " f"{result['new_records']} new records")

    except Exception:
        logger.error("[Background] Refresh failed for {query_name}: {str(e)}", exc_info=True)
    finally:
        db.close()
