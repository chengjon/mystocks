#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
问财API路由

提供问财股票筛选功能的RESTful API端点

作者: MyStocks Backend Team
创建日期: 2025-10-17
"""

import logging
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session

from app.core.database import get_db, SessionLocal
from app.services.wencai_service import WencaiService, get_wencai_service
from app.schemas.wencai_schemas import (
    WencaiQueryRequest,
    WencaiQueryResponse,
    WencaiCustomQueryRequest,
    WencaiCustomQueryResponse,
    WencaiQueryInfo,
    WencaiQueryListResponse,
    WencaiResultsResponse,
    WencaiRefreshResponse,
    WencaiHistoryResponse,
    WencaiErrorResponse,
)

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由
router = APIRouter(prefix="/api/market/wencai", tags=["wencai"])


# ============================================================================
# API端点
# ============================================================================


@router.get(
    "/queries",
    response_model=WencaiQueryListResponse,
    summary="获取所有查询列表",
    description="获取所有可用的问财查询配置",
)
async def get_all_queries(db: Session = Depends(get_db)) -> WencaiQueryListResponse:
    """
    获取所有查询列表

    返回所有预定义的问财查询配置（qs_1 ~ qs_9）
    """
    try:
        service = WencaiService(db=db)
        queries = service.get_all_queries()

        return WencaiQueryListResponse(queries=queries, total=len(queries))

    except Exception as e:
        logger.error(f"Failed to get queries: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取查询列表失败: {str(e)}")


@router.get(
    "/queries/{query_name}",
    response_model=WencaiQueryInfo,
    summary="获取指定查询信息",
    description="根据查询名称获取查询配置详情",
)
async def get_query_by_name(
    query_name: str, db: Session = Depends(get_db)
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
        logger.error(f"Failed to get query {query_name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取查询失败: {str(e)}")


@router.post(
    "/query",
    response_model=WencaiQueryResponse,
    summary="执行问财查询",
    description="执行指定的问财查询并保存结果到数据库",
)
async def execute_query(
    request: WencaiQueryRequest, db: Session = Depends(get_db)
) -> WencaiQueryResponse:
    """
    执行问财查询

    从问财API获取数据，清理、去重后保存到MySQL

    Args:
        request: 查询请求（包含query_name和pages）

    Returns:
        查询执行结果统计
    """
    try:
        logger.info(f"Executing query: {request.query_name}, pages={request.pages}")

        service = WencaiService(db=db)
        result = service.fetch_and_save(
            query_name=request.query_name, pages=request.pages
        )

        return WencaiQueryResponse(**result)

    except ValueError as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to execute query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"查询执行失败: {str(e)}")


@router.get(
    "/results/{query_name}",
    response_model=WencaiResultsResponse,
    summary="获取查询结果",
    description="获取指定查询的最新结果数据",
)
async def get_query_results(
    query_name: str,
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
        results = service.get_query_results(
            query_name=query_name, limit=limit, offset=offset
        )

        return WencaiResultsResponse(**results)

    except Exception as e:
        logger.error(f"Failed to get results for {query_name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取结果失败: {str(e)}")


@router.post(
    "/refresh/{query_name}",
    response_model=WencaiRefreshResponse,
    summary="刷新查询数据",
    description="在后台异步刷新指定查询的数据",
)
async def refresh_query(
    query_name: str,
    background_tasks: BackgroundTasks,
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
        background_tasks.add_task(
            _refresh_query_task, query_name=query_name, pages=pages
        )

        logger.info(f"Background refresh task added for {query_name}")

        return WencaiRefreshResponse(
            status="refreshing",
            message="后台刷新任务已启动",
            task_id=None,  # 如果使用Celery可以返回task_id
            query_name=query_name,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start refresh task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"启动刷新任务失败: {str(e)}")


@router.get(
    "/history/{query_name}",
    response_model=WencaiHistoryResponse,
    summary="获取查询历史",
    description="获取指定查询的历史数据统计",
)
async def get_query_history(
    query_name: str,
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
        logger.error(f"Failed to get history for {query_name}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取历史数据失败: {str(e)}")


@router.post(
    "/custom-query",
    response_model=WencaiCustomQueryResponse,
    summary="执行自定义查询",
    description="执行用户自定义的问财查询（直接返回结果，不保存到数据库）",
)
async def execute_custom_query(
    request: WencaiCustomQueryRequest, db: Session = Depends(get_db)
) -> WencaiCustomQueryResponse:
    """
    执行自定义查询

    用户可以输入任意自然语言查询，直接获取结果

    Args:
        request: 自定义查询请求（包含query_text和pages）

    Returns:
        查询结果（不保存到数据库）
    """
    try:
        logger.info(
            f"Executing custom query: {request.query_text[:50]}..., pages={request.pages}"
        )

        service = WencaiService(db=db)

        # 直接调用适配器获取数据
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

        # 转换为字典列表
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
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to execute custom query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"自定义查询执行失败: {str(e)}")


@router.get("/health", summary="健康检查", description="检查问财API服务状态")
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
        logger.info(f"[Background] Starting refresh for {query_name}")

        service = WencaiService(db=db)

        result = service.fetch_and_save(query_name=query_name, pages=pages)

        logger.info(
            f"[Background] Refresh completed for {query_name}: "
            f"{result['new_records']} new records"
        )

    except Exception as e:
        logger.error(
            f"[Background] Refresh failed for {query_name}: {str(e)}", exc_info=True
        )
    finally:
        db.close()
