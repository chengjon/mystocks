"""
数据治理仪表板数据聚合 API

提供数据质量、血缘统计、资产目录和治理合规指标的聚合数据。

核心端点:
1. GET /api/v1/governance/quality/overview - 数据质量总览
2. GET /api/v1/governance/lineage/stats - 数据血缘统计
3. GET /api/v1/governance/assets/catalog - 数据资产目录
4. GET /api/v1/governance/compliance/metrics - 治理合规指标
5. GET /api/v1/governance/dashboard/summary - 仪表板摘要

Author: Claude Code (Main CLI)
Date: 2026-01-09
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.core.responses import (
    BusinessCode,
    UnifiedResponse,
    create_unified_error_response,
    create_unified_success_response,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/governance",
    tags=["Data Governance Dashboard"],
)


# =============================================================================
# Pydantic Models
# =============================================================================


class QualityOverviewResponse(BaseModel):
    """数据质量总览响应"""

    total_assets: int = Field(description="总资产数")
    avg_quality_score: float = Field(description="平均质量评分")
    quality_distribution: Dict[str, int] = Field(description="质量分布（优秀/良好/差）")
    top_assets: List[Dict[str, Any]] = Field(description="Top 10资产")


class LineageStatsResponse(BaseModel):
    """数据血缘统计响应"""

    total_nodes: int = Field(description="总节点数")
    total_edges: int = Field(description="总边数")
    node_type_distribution: Dict[str, int] = Field(description="节点类型分布")
    operation_type_distribution: Dict[str, int] = Field(description="操作类型分布")
    recent_trends: Dict[str, List[Dict[str, Any]]] = Field(description="最近趋势")


class AssetCatalogItem(BaseModel):
    """数据资产目录项"""

    asset_id: str
    name: str
    asset_type: str
    source: str
    quality_score: Optional[float]
    access_count: int
    created_at: datetime
    updated_at: datetime


class AssetCatalogResponse(BaseModel):
    """数据资产目录响应"""

    total_assets: int
    assets: List[AssetCatalogItem]
    page: int
    page_size: int
    total_pages: int


class ComplianceMetricsResponse(BaseModel):
    """治理合规指标响应"""

    total_data_sources: int = Field(description="已配置数据源数")
    total_config_versions: int = Field(description="配置版本总数")
    total_audit_logs: int = Field(description="审计日志总数")
    active_users: int = Field(description="活跃操作用户数")
    recent_changes: List[Dict[str, Any]] = Field(description="最近配置变更")
    operation_stats: Dict[str, int] = Field(description="操作类型统计")


class DashboardSummaryResponse(BaseModel):
    """仪表板摘要响应"""

    quality_overview: QualityOverviewResponse
    lineage_stats: LineageStatsResponse
    asset_catalog_summary: Dict[str, Any]
    compliance_metrics: ComplianceMetricsResponse
    last_updated: datetime


# =============================================================================
# Helper Functions
# =============================================================================


async def get_postgres_connection():
    """
    获取PostgreSQL数据库连接

    Returns:
        数据库连接
    """
    import asyncpg

    from app.core.config import settings

    return await asyncpg.connect(
        host=settings.postgresql_host,
        port=settings.postgresql_port,
        user=settings.postgresql_user,
        password=settings.postgresql_password,
        database=settings.postgresql_database,
    )


def handle_governance_error(error: str, request_id: Optional[str] = None) -> UnifiedResponse:
    """
    处理治理API错误

    Args:
        error: 错误消息
        request_id: 请求ID

    Returns:
        UnifiedResponse: 错误响应
    """
    return create_unified_error_response(
        code=BusinessCode.INTERNAL_ERROR,
        message=error,
        error_code="GOVERNANCE_API_ERROR",
        request_id=request_id,
    )


# =============================================================================
# API Endpoints
# =============================================================================


@router.get("/quality/overview", response_model=UnifiedResponse)
async def get_quality_overview(http_request: Request):
    """
    数据质量总览

    返回数据质量评分的总体统计信息，包括：
    - 总资产数
    - 平均质量评分
    - 质量分布（优秀/良好/差）
    - Top 10资产列表

    Args:
        http_request: HTTP请求对象

    Returns:
        UnifiedResponse: 数据质量总览
    """
    request_id = getattr(http_request.state, "request_id", None)
    logger.info("Fetching quality overview", extra={"request_id": request_id})

    try:
        conn = await get_postgres_connection()

        try:
            # 查询总资产数和平均质量评分
            total_assets_row = await conn.fetchrow(
                """
                SELECT
                    COUNT(*) as total,
                    COALESCE(AVG(quality_score), 0) as avg_score
                FROM data_assets
                """
            )

            total_assets = total_assets_row["total"]
            avg_quality_score = float(total_assets_row["avg_score"])

            # 查询质量分布
            quality_dist_rows = await conn.fetch(
                """
                SELECT
                    CASE
                        WHEN quality_score >= 80 THEN '优秀'
                        WHEN quality_score >= 60 THEN '良好'
                        ELSE '差'
                    END as quality_level,
                    COUNT(*) as count
                FROM data_assets
                WHERE quality_score IS NOT NULL
                GROUP BY quality_level
                """
            )

            quality_distribution = {row["quality_level"]: row["count"] for row in quality_dist_rows}

            # 查询Top 10资产
            top_assets_rows = await conn.fetch(
                """
                SELECT
                    asset_id,
                    name,
                    asset_type,
                    source,
                    quality_score,
                    access_count,
                    created_at,
                    updated_at
                FROM data_assets
                WHERE quality_score IS NOT NULL
                ORDER BY quality_score DESC
                LIMIT 10
                """
            )

            top_assets = [
                {
                    "asset_id": row["asset_id"],
                    "name": row["name"],
                    "asset_type": row["asset_type"],
                    "source": row["source"],
                    "quality_score": float(row["quality_score"]),
                    "access_count": row["access_count"],
                    "created_at": row["created_at"].isoformat() if row["created_at"] else None,
                    "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
                }
                for row in top_assets_rows
            ]

            await conn.close()

            response_data = QualityOverviewResponse(
                total_assets=total_assets,
                avg_quality_score=avg_quality_score,
                quality_distribution=quality_distribution,
                top_assets=top_assets,
            )

            return create_unified_success_response(
                data=response_data.dict(),
                message=f"成功获取数据质量总览: {total_assets}个资产",
                request_id=request_id,
            )

        except Exception as e:
            await conn.close()
            raise e

    except Exception as e:
        logger.error("Failed to fetch quality overview: {str(e)}", extra={"request_id": request_id}, exc_info=True)
        return handle_governance_error(str(e), request_id)


@router.get("/lineage/stats", response_model=UnifiedResponse)
async def get_lineage_stats(
    days: int = 7,
    http_request: Request = None,
):
    """
    数据血缘统计

    返回数据血缘的统计信息，包括：
    - 总节点数和边数
    - 节点类型分布
    - 操作类型分布
    - 最近趋势（默认7天）

    Args:
        days: 查询最近几天的趋势（默认7天）
        http_request: HTTP请求对象

    Returns:
        UnifiedResponse: 数据血缘统计
    """
    request_id = getattr(http_request.state, "request_id", None) if http_request else None
    logger.info("Fetching lineage stats for last {days} days", extra={"request_id": request_id})

    try:
        conn = await get_postgres_connection()

        try:
            # 查询总节点数和边数
            nodes_count = await conn.fetchval("SELECT COUNT(*) FROM data_lineage_nodes")
            edges_count = await conn.fetchval("SELECT COUNT(*) FROM data_lineage_edges")

            # 查询节点类型分布
            node_type_rows = await conn.fetch(
                "SELECT node_type, COUNT(*) as count FROM data_lineage_nodes GROUP BY node_type"
            )
            node_type_distribution = {row["node_type"]: row["count"] for row in node_type_rows}

            # 查询操作类型分布
            operation_type_rows = await conn.fetch(
                "SELECT operation, COUNT(*) as count FROM data_lineage_edges GROUP BY operation"
            )
            operation_type_distribution = {row["operation"]: row["count"] for row in operation_type_rows}

            # 查询最近趋势
            start_date = datetime.now() - timedelta(days=days)

            # 节点创建趋势
            node_trend_rows = await conn.fetch(
                """
                SELECT
                    DATE_TRUNC('day', created_at) as date,
                    COUNT(*) as count
                FROM data_lineage_nodes
                WHERE created_at >= $1
                GROUP BY DATE_TRUNC('day', created_at)
                ORDER BY date
                """,
                start_date,
            )

            nodes_trend = [
                {
                    "date": row["date"].isoformat() if row["date"] else None,
                    "count": row["count"],
                }
                for row in node_trend_rows
            ]

            # 边创建趋势
            edge_trend_rows = await conn.fetch(
                """
                SELECT
                    DATE_TRUNC('day', timestamp) as date,
                    COUNT(*) as count
                FROM data_lineage_edges
                WHERE timestamp >= $1
                GROUP BY DATE_TRUNC('day', timestamp)
                ORDER BY date
                """,
                start_date,
            )

            edges_trend = [
                {
                    "date": row["date"].isoformat() if row["date"] else None,
                    "count": row["count"],
                }
                for row in edge_trend_rows
            ]

            recent_trends = {
                "nodes": nodes_trend,
                "edges": edges_trend,
            }

            await conn.close()

            response_data = LineageStatsResponse(
                total_nodes=nodes_count,
                total_edges=edges_count,
                node_type_distribution=node_type_distribution,
                operation_type_distribution=operation_type_distribution,
                recent_trends=recent_trends,
            )

            return create_unified_success_response(
                data=response_data.dict(),
                message=f"成功获取血缘统计: {nodes_count}个节点, {edges_count}条边",
                request_id=request_id,
            )

        except Exception as e:
            await conn.close()
            raise e

    except Exception as e:
        logger.error("Failed to fetch lineage stats: {str(e)}", extra={"request_id": request_id}, exc_info=True)
        return handle_governance_error(str(e), request_id)


@router.get("/assets/catalog", response_model=UnifiedResponse)
async def get_assets_catalog(
    page: int = 1,
    page_size: int = 20,
    asset_type: Optional[str] = None,
    http_request: Request = None,
):
    """
    数据资产目录

    返回数据资产目录，支持分页和类型过滤。

    Args:
        page: 页码（从1开始）
        page_size: 每页数量
        asset_type: 资产类型过滤（可选）
        http_request: HTTP请求对象

    Returns:
        UnifiedResponse: 数据资产目录
    """
    request_id = getattr(http_request.state, "request_id", None) if http_request else None
    logger.info(
        f"Fetching assets catalog: page={page}, page_size={page_size}, type={asset_type}",
        extra={"request_id": request_id},
    )

    try:
        conn = await get_postgres_connection()

        try:
            # 构建查询条件
            where_clause = ""
            params = []
            param_count = 0

            if asset_type:
                param_count += 1
                # Safe: using parameterized query ($1, $2...) for user input
                where_clause = f"WHERE asset_type = ${param_count}"
                params.append(asset_type)

            # 查询总数
            count_query = f"SELECT COUNT(*) FROM data_assets {where_clause}"
            total_assets = await conn.fetchval(count_query, *params)

            # 计算偏移量和总页数
            offset = (page - 1) * page_size
            total_pages = (total_assets + page_size - 1) // page_size

            # 查询资产列表
            assets_query = f"""
                SELECT
                    asset_id,
                    name,
                    asset_type,
                    source,
                    quality_score,
                    access_count,
                    created_at,
                    updated_at
                FROM data_assets
                {where_clause}
                ORDER BY updated_at DESC
                LIMIT ${param_count + 1} OFFSET ${param_count + 2}
            """

            params.extend([page_size, offset])

            assets_rows = await conn.fetch(assets_query, *params)

            assets = [
                AssetCatalogItem(
                    asset_id=row["asset_id"],
                    name=row["name"],
                    asset_type=row["asset_type"],
                    source=row["source"],
                    quality_score=float(row["quality_score"]) if row["quality_score"] else None,
                    access_count=row["access_count"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                for row in assets_rows
            ]

            await conn.close()

            response_data = AssetCatalogResponse(
                total_assets=total_assets,
                assets=[asset.dict() for asset in assets],
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            )

            return create_unified_success_response(
                data=response_data.dict(),
                message=f"成功获取资产目录: {len(assets)}个资产",
                request_id=request_id,
            )

        except Exception as e:
            await conn.close()
            raise e

    except Exception as e:
        logger.error("Failed to fetch assets catalog: {str(e)}", extra={"request_id": request_id}, exc_info=True)
        return handle_governance_error(str(e), request_id)


@router.get("/compliance/metrics", response_model=UnifiedResponse)
async def get_compliance_metrics(
    days: int = 30,
    limit: int = 20,
    http_request: Request = None,
):
    """
    治理合规指标

    返回治理合规相关的指标，包括：
    - 已配置数据源数
    - 配置版本总数
    - 审计日志总数
    - 活跃操作用户数
    - 最近配置变更
    - 操作类型统计

    Args:
        days: 查询最近几天的数据（默认30天）
        limit: 返回最近变更记录数（默认20）
        http_request: HTTP请求对象

    Returns:
        UnifiedResponse: 治理合规指标
    """
    request_id = getattr(http_request.state, "request_id", None) if http_request else None
    logger.info("Fetching compliance metrics: {days} days, {limit} changes", extra={"request_id": request_id})

    try:
        conn = await get_postgres_connection()

        try:
            # 查询已配置数据源数
            total_data_sources = await conn.fetchval("SELECT COUNT(DISTINCT endpoint_name) FROM data_source_versions")

            # 查询配置版本总数
            total_config_versions = await conn.fetchval("SELECT COUNT(*) FROM data_source_versions")

            # 查询审计日志总数
            total_audit_logs = await conn.fetchval("SELECT COUNT(*) FROM data_source_audit_log")

            # 查询活跃操作用户数
            active_users = await conn.fetchval("SELECT COUNT(DISTINCT actor) FROM data_source_audit_log")

            # 查询最近配置变更
            recent_changes_rows = await conn.fetch(
                """
                SELECT
                    v.endpoint_name,
                    v.version,
                    v.change_type,
                    v.changed_by,
                    v.changed_at,
                    v.change_summary
                FROM data_source_versions v
                ORDER BY v.changed_at DESC
                LIMIT $1
                """,
                limit,
            )

            recent_changes = [
                {
                    "endpoint_name": row["endpoint_name"],
                    "version": row["version"],
                    "change_type": row["change_type"],
                    "changed_by": row["changed_by"],
                    "changed_at": row["changed_at"].isoformat() if row["changed_at"] else None,
                    "change_summary": row["change_summary"],
                }
                for row in recent_changes_rows
            ]

            # 查询操作类型统计
            operation_stats_rows = await conn.fetch(
                """
                SELECT
                    action,
                    COUNT(*) as count
                FROM data_source_audit_log
                WHERE timestamp >= NOW() - INTERVAL '1 day'
                GROUP BY action
                """
            )

            operation_stats = {row["action"]: row["count"] for row in operation_stats_rows}

            await conn.close()

            response_data = ComplianceMetricsResponse(
                total_data_sources=total_data_sources,
                total_config_versions=total_config_versions,
                total_audit_logs=total_audit_logs,
                active_users=active_users,
                recent_changes=recent_changes,
                operation_stats=operation_stats,
            )

            return create_unified_success_response(
                data=response_data.dict(),
                message=f"成功获取治理合规指标: {total_data_sources}个数据源",
                request_id=request_id,
            )

        except Exception as e:
            await conn.close()
            raise e

    except Exception as e:
        logger.error("Failed to fetch compliance metrics: {str(e)}", extra={"request_id": request_id}, exc_info=True)
        return handle_governance_error(str(e), request_id)


@router.get("/dashboard/summary", response_model=UnifiedResponse)
async def get_dashboard_summary(http_request: Request):
    """
    仪表板摘要

    返回完整的仪表板摘要数据，整合所有治理信息。

    Args:
        http_request: HTTP请求对象

    Returns:
        UnifiedResponse: 仪表板摘要
    """
    request_id = getattr(http_request.state, "request_id", None)
    logger.info("Fetching dashboard summary", extra={"request_id": request_id})

    try:
        # 并行获取所有数据

        async def fetch_all_data():
            # 获取数据质量总览
            quality_response = await get_quality_overview(http_request)
            quality_data = QualityOverviewResponse(**quality_response.data)

            # 获取血缘统计
            lineage_response = await get_lineage_stats(7, http_request)
            lineage_data = LineageStatsResponse(**lineage_response.data)

            # 获取资产目录摘要
            conn = await get_postgres_connection()
            try:
                total_assets = await conn.fetchval("SELECT COUNT(*) FROM data_assets")

                assets_by_type_rows = await conn.fetch(
                    "SELECT asset_type, COUNT(*) as count FROM data_assets GROUP BY asset_type"
                )
                assets_by_type = {row["asset_type"]: row["count"] for row in assets_by_type_rows}

            finally:
                await conn.close()

            asset_catalog_summary = {
                "total_assets": total_assets,
                "assets_by_type": assets_by_type,
            }

            # 获取治理合规指标
            compliance_response = await get_compliance_metrics(30, 20, http_request)
            compliance_data = ComplianceMetricsResponse(**compliance_response.data)

            return {
                "quality_overview": quality_data,
                "lineage_stats": lineage_data,
                "asset_catalog_summary": asset_catalog_summary,
                "compliance_metrics": compliance_data,
                "last_updated": datetime.now().isoformat(),
            }

        summary_data = await fetch_all_data()

        return create_unified_success_response(
            data=summary_data,
            message="成功获取仪表板摘要",
            request_id=request_id,
        )

    except Exception as e:
        logger.error("Failed to fetch dashboard summary: {str(e)}", extra={"request_id": request_id}, exc_info=True)
        return handle_governance_error(str(e), request_id)
