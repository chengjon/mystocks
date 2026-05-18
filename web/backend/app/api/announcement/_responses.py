"""Announcement route response examples, OpenAPI specs, and analysis helpers."""

from typing import Any


ANNOUNCEMENT_ERROR_RESPONSE = {
    500: {
        "description": "公告服务处理请求失败，通常表示内部依赖、数据库会话或分析流程出现异常。",
        "content": {
            "application/json": {
                "example": {
                    "detail": "公告服务暂时不可用，请稍后重试",
                }
            }
        },
    }
}

ANNOUNCEMENT_ANALYZE_EXAMPLES = {
    "earnings_review": {
        "summary": "分析财报公告内容",
        "value": {
            "title": "2026年第一季度业绩预增公告",
            "stock_code": "600519",
            "content": "预计2026年第一季度归母净利润同比增长18%-22%。",
            "analysis_mode": "summary",
        },
    }
}

ANNOUNCEMENT_MONITOR_RULE_CREATE_EXAMPLES = {
    "dividend_watch_rule": {
        "summary": "创建分红公告监控规则",
        "value": {
            "rule_name": "分红公告提醒",
            "keywords": ["分红", "派息", "股权登记日"],
            "stock_codes": ["600519", "000858"],
            "min_importance_level": 2,
            "notify_enabled": True,
        },
    }
}

ANNOUNCEMENT_MONITOR_RULE_UPDATE_EXAMPLES = {
    "raise_importance_threshold": {
        "summary": "提高监控规则触发阈值",
        "value": {
            "keywords": ["业绩预增", "利润增长", "超预期"],
            "min_importance_level": 3,
            "notify_enabled": True,
        },
    }
}

ANNOUNCEMENT_ITEM_EXAMPLE = {
    "id": 101,
    "stock_code": "600519",
    "stock_name": "贵州茅台",
    "title": "2026年第一季度业绩预增公告",
    "type": "业绩预告",
    "publish_date": "2026-04-07",
    "publish_time": "2026-04-07T18:30:00",
    "url": "https://example.com/announcement/101",
    "importance_level": 4,
    "sentiment": "positive",
}

ANNOUNCEMENT_MONITOR_RULE_EXAMPLE = {
    "id": 7,
    "rule_name": "分红公告提醒",
    "stock_codes": ["600519", "000858"],
    "keywords": ["分红", "派息", "股权登记日"],
    "min_importance_level": 2,
    "notify_enabled": True,
    "is_active": True,
}

ANNOUNCEMENT_TRIGGERED_RECORD_EXAMPLE = {
    "id": 21,
    "rule_id": 7,
    "announcement_id": 101,
    "matched_keywords": ["分红"],
    "triggered_at": "2026-04-07T18:35:00",
    "notified": True,
    "notified_at": "2026-04-07T18:36:00",
    "notification_result": "sent",
    "rule_name": "分红公告提醒",
    "announcement_title": "2026年第一季度利润分配预案公告",
    "stock_code": "600519",
}


def _success_response_spec(description: str, example: object) -> dict[int, dict]:
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


ANNOUNCEMENT_HEALTH_RESPONSES = {
    **ANNOUNCEMENT_ERROR_RESPONSE,
    **_success_response_spec("公告服务健康状态", {"status": "ok", "service": "announcement"}),
}

ANNOUNCEMENT_STATUS_RESPONSES = {
    **ANNOUNCEMENT_ERROR_RESPONSE,
    **_success_response_spec("公告服务运行状态", {"status": "active", "endpoint": "announcement"}),
}

ANNOUNCEMENT_ANALYZE_RESPONSES = {
    **ANNOUNCEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "公告分析结果",
        {
            "success": True,
            "code": 200,
            "message": "Announcement analysis completed from provided text",
            "data": {
                "status": "available",
                "endpoint": "announcement",
                "stock_code": "600519",
                "analysis_mode": "summary",
                "summary": "公告内容偏利多，核心信号集中在业绩增长预期。",
                "signals": ["earnings_growth", "positive_guidance"],
                "sentiment": "positive",
                "importance_level": 4,
            },
        },
    ),
}

POSITIVE_ANNOUNCEMENT_KEYWORDS = (
    "预增",
    "增长",
    "回购",
    "分红",
    "中标",
    "增持",
    "扭亏",
    "超预期",
)

NEGATIVE_ANNOUNCEMENT_KEYWORDS = (
    "预减",
    "下滑",
    "亏损",
    "减持",
    "问询",
    "处罚",
    "延期",
    "风险",
)


def _extract_announcement_text(data: dict[str, Any]) -> str:
    return " ".join(
        str(value).strip()
        for value in (
            data.get("title"),
            data.get("content"),
            data.get("summary"),
        )
        if value
    )


def _detect_announcement_sentiment(text: str) -> tuple[str, list[str], int]:
    signals: list[str] = []
    importance_level = 2

    positive_hits = [keyword for keyword in POSITIVE_ANNOUNCEMENT_KEYWORDS if keyword in text]
    negative_hits = [keyword for keyword in NEGATIVE_ANNOUNCEMENT_KEYWORDS if keyword in text]

    if positive_hits:
        signals.extend(
            "earnings_growth" if keyword in {"预增", "增长", "扭亏", "超预期"} else
            "capital_return" if keyword in {"回购", "分红"} else
            "business_momentum"
            for keyword in positive_hits
        )
        if len(positive_hits) >= 2:
            signals.append("positive_guidance")
        importance_level = max(importance_level, 4 if len(positive_hits) >= 2 else 3)

    if negative_hits:
        signals.extend(
            "earnings_pressure" if keyword in {"预减", "下滑", "亏损"} else
            "governance_risk" if keyword in {"问询", "处罚"} else
            "execution_risk"
            for keyword in negative_hits
        )
        if len(negative_hits) >= 2:
            signals.append("risk_escalation")
        importance_level = max(importance_level, 4 if len(negative_hits) >= 2 else 3)

    if len(positive_hits) > len(negative_hits):
        return "positive", list(dict.fromkeys(signals)), importance_level
    if len(negative_hits) > len(positive_hits):
        return "negative", list(dict.fromkeys(signals)), importance_level
    if signals:
        return "neutral", list(dict.fromkeys(signals)), importance_level
    return "neutral", ["watchlist_review"], 2


def _build_announcement_summary(sentiment: str, signals: list[str]) -> str:
    if sentiment == "positive":
        return "公告内容偏利多，核心信号集中在业绩增长预期。"
    if sentiment == "negative":
        return "公告内容偏利空，需重点关注业绩或治理风险。"
    if "watchlist_review" in signals:
        return "公告文本未出现强烈方向性关键词，建议结合原文进一步研判。"
    return "公告信号多空交织，短期方向仍需更多信息确认。"


ANNOUNCEMENT_FETCH_RESPONSES = {
    **ANNOUNCEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "公告抓取和入库结果",
        {
            "success": True,
            "saved_count": 12,
            "updated_count": 4,
            "total_fetched": 16,
            "source": "cninfo",
        },
    ),
}

ANNOUNCEMENT_LIST_RESPONSES = {
    **ANNOUNCEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "公告列表查询结果",
        {
            "success": True,
            "data": [ANNOUNCEMENT_ITEM_EXAMPLE],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "total_pages": 1,
        },
    ),
}

ANNOUNCEMENT_TODAY_RESPONSES = {
    **ANNOUNCEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "今日公告列表",
        {
            "success": True,
            "date": "2026-04-07",
            "announcements": [ANNOUNCEMENT_ITEM_EXAMPLE],
            "count": 1,
        },
    ),
}

ANNOUNCEMENT_IMPORTANT_RESPONSES = {
    **ANNOUNCEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "重要公告列表",
        {
            "success": True,
            "start_date": "2026-04-01",
            "end_date": "2026-04-07",
            "min_importance": 3,
            "announcements": [ANNOUNCEMENT_ITEM_EXAMPLE],
            "count": 1,
        },
    ),
}

ANNOUNCEMENT_STATS_RESPONSES = {
    **ANNOUNCEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "公告统计概览",
        {
            "success": True,
            "total_count": 240,
            "today_count": 12,
            "important_count": 5,
            "triggered_count": 2,
            "by_source": {"cninfo": 240},
            "by_type": {"业绩预告": 48},
            "by_sentiment": {"positive": 88, "neutral": 120, "negative": 32},
        },
    ),
}

ANNOUNCEMENT_MONITOR_RULE_LIST_RESPONSES = {
    **ANNOUNCEMENT_ERROR_RESPONSE,
    **_success_response_spec("公告监控规则列表", [ANNOUNCEMENT_MONITOR_RULE_EXAMPLE]),
}

ANNOUNCEMENT_MONITOR_RULE_CREATE_RESPONSES = {
    **ANNOUNCEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "新建公告监控规则结果",
        {
            "success": True,
            "data": ANNOUNCEMENT_MONITOR_RULE_EXAMPLE,
        },
    ),
}

ANNOUNCEMENT_MONITOR_RULE_UPDATE_RESPONSES = {
    **ANNOUNCEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "更新后的公告监控规则",
        {
            "success": True,
            "data": {
                **ANNOUNCEMENT_MONITOR_RULE_EXAMPLE,
                "keywords": ["业绩预增", "利润增长", "超预期"],
                "min_importance_level": 3,
            },
        },
    ),
}

ANNOUNCEMENT_MONITOR_RULE_DELETE_RESPONSES = {
    **ANNOUNCEMENT_ERROR_RESPONSE,
    **_success_response_spec("公告监控规则删除结果", {"success": True, "message": "规则已删除"}),
}

ANNOUNCEMENT_TRIGGERED_RECORDS_RESPONSES = {
    **ANNOUNCEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "公告规则触发记录列表",
        {
            "success": True,
            "data": [ANNOUNCEMENT_TRIGGERED_RECORD_EXAMPLE],
            "total": 1,
            "page": 1,
            "page_size": 20,
            "total_pages": 1,
        },
    ),
}

ANNOUNCEMENT_MONITOR_EVALUATE_RESPONSES = {
    **ANNOUNCEMENT_ERROR_RESPONSE,
    **_success_response_spec(
        "公告监控规则评估结果",
        {
            "success": True,
            "rules_evaluated": 5,
            "triggered_count": 2,
        },
    ),
}
