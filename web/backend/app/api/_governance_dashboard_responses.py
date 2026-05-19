"""Response examples and OpenAPI response specs for governance_dashboard."""

GOVERNANCE_INTERNAL_ERROR_RESPONSE = {
    500: {
        "description": "Governance dashboard request failed because the backing service or database is unavailable.",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "code": "INTERNAL_ERROR",
                    "message": "database connection timeout",
                    "error_code": "GOVERNANCE_API_ERROR",
                    "request_id": "req-governance-error",
                }
            }
        },
    }
}


def _success_response_spec(description: str, example: dict[str, Any]) -> dict[int, dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


GOVERNANCE_QUALITY_OVERVIEW_RESPONSES = {
    **GOVERNANCE_INTERNAL_ERROR_RESPONSE,
    **_success_response_spec(
        "治理质量总览聚合数据",
        {
            "success": True,
            "code": 200,
            "message": "成功获取数据质量总览: 128个资产",
            "request_id": "req-governance-quality",
            "data": {
                "total_assets": 128,
                "avg_quality_score": 87.4,
                "quality_distribution": {
                    "优秀": 74,
                    "良好": 38,
                    "差": 16,
                },
                "top_assets": [
                    {
                        "asset_id": "asset-stock-daily",
                        "name": "A股日线行情",
                        "asset_type": "daily_kline",
                        "source": "tdx",
                        "quality_score": 98.5,
                        "access_count": 8642,
                        "created_at": "2026-04-01T09:30:00+00:00",
                        "updated_at": "2026-04-08T01:30:00+00:00",
                    }
                ],
            },
        },
    ),
}

GOVERNANCE_LINEAGE_STATS_RESPONSES = {
    **GOVERNANCE_INTERNAL_ERROR_RESPONSE,
    **_success_response_spec(
        "治理血缘统计数据",
        {
            "success": True,
            "code": 200,
            "message": "成功获取血缘统计: 452个节点, 914条边",
            "request_id": "req-governance-lineage",
            "data": {
                "total_nodes": 452,
                "total_edges": 914,
                "node_type_distribution": {"table": 128, "view": 34, "task": 19},
                "operation_type_distribution": {"extract": 124, "transform": 86, "load": 74},
                "recent_trends": {
                    "nodes": [{"date": "2026-04-07T00:00:00+00:00", "count": 6}],
                    "edges": [{"date": "2026-04-07T00:00:00+00:00", "count": 12}],
                },
            },
        },
    ),
}

GOVERNANCE_ASSETS_CATALOG_RESPONSES = {
    **GOVERNANCE_INTERNAL_ERROR_RESPONSE,
    **_success_response_spec(
        "治理资产目录分页数据",
        {
            "success": True,
            "code": 200,
            "message": "成功获取资产目录: 1个资产",
            "request_id": "req-governance-assets",
            "data": {
                "total_assets": 128,
                "assets": [
                    {
                        "asset_id": "asset-futures-index-main",
                        "name": "股指期货主连数据集",
                        "asset_type": "futures_index",
                        "source": "cffex",
                        "quality_score": 91.2,
                        "access_count": 426,
                        "created_at": "2026-03-20T08:00:00+00:00",
                        "updated_at": "2026-04-08T01:20:00+00:00",
                    }
                ],
                "page": 1,
                "page_size": 20,
                "total_pages": 7,
            },
        },
    ),
}

GOVERNANCE_COMPLIANCE_METRICS_RESPONSES = {
    **GOVERNANCE_INTERNAL_ERROR_RESPONSE,
    **_success_response_spec(
        "治理合规指标聚合数据",
        {
            "success": True,
            "code": 200,
            "message": "成功获取治理合规指标: 12个数据源",
            "request_id": "req-governance-compliance",
            "data": {
                "total_data_sources": 12,
                "total_config_versions": 48,
                "total_audit_logs": 1260,
                "active_users": 5,
                "recent_changes": [
                    {
                        "endpoint_name": "akshare_market",
                        "version": 7,
                        "change_type": "update",
                        "changed_by": "system_admin",
                        "changed_at": "2026-04-08T00:10:00+00:00",
                        "change_summary": "updated retry policy for market ingestion",
                    }
                ],
                "operation_stats": {"create": 14, "update": 23, "rollback": 2},
            },
        },
    ),
}

GOVERNANCE_DASHBOARD_SUMMARY_RESPONSES = {
    **GOVERNANCE_INTERNAL_ERROR_RESPONSE,
    **_success_response_spec(
        "治理仪表板汇总数据",
        {
            "success": True,
            "code": 200,
            "message": "成功获取仪表板摘要",
            "request_id": "req-governance-summary",
            "data": {
                "quality_overview": {
                    "total_assets": 128,
                    "avg_quality_score": 87.4,
                    "quality_distribution": {"优秀": 74, "良好": 38, "差": 16},
                    "top_assets": [
                        {
                            "asset_id": "asset-stock-daily",
                            "name": "A股日线行情",
                            "asset_type": "daily_kline",
                            "source": "tdx",
                            "quality_score": 98.5,
                            "access_count": 8642,
                            "created_at": "2026-04-01T09:30:00+00:00",
                            "updated_at": "2026-04-08T01:30:00+00:00",
                        }
                    ],
                },
                "lineage_stats": {
                    "total_nodes": 452,
                    "total_edges": 914,
                    "node_type_distribution": {"table": 128, "view": 34, "task": 19},
                    "operation_type_distribution": {"extract": 124, "transform": 86, "load": 74},
                    "recent_trends": {
                        "nodes": [{"date": "2026-04-07T00:00:00+00:00", "count": 6}],
                        "edges": [{"date": "2026-04-07T00:00:00+00:00", "count": 12}],
                    },
                },
                "asset_catalog_summary": {
                    "total_assets": 128,
                    "assets_by_type": {"daily_kline": 32, "watchlist": 11, "futures_index": 5},
                },
                "compliance_metrics": {
                    "total_data_sources": 12,
                    "total_config_versions": 48,
                    "total_audit_logs": 1260,
                    "active_users": 5,
                    "recent_changes": [
                        {
                            "endpoint_name": "akshare_market",
                            "version": 7,
                            "change_type": "update",
                            "changed_by": "system_admin",
                            "changed_at": "2026-04-08T00:10:00+00:00",
                            "change_summary": "updated retry policy for market ingestion",
                        }
                    ],
                    "operation_stats": {"create": 14, "update": 23, "rollback": 2},
                },
                "last_updated": "2026-04-08T01:35:00+00:00",
            },
        },
    ),
}
