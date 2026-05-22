"""
公告监控API路由
"""

from datetime import date, timedelta
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, Path, Query
from app.core.exceptions import BusinessException
from app.core.responses import UnifiedResponse
from app.api.announcement._responses import (
    ANNOUNCEMENT_ANALYZE_EXAMPLES,
    ANNOUNCEMENT_ANALYZE_RESPONSES,
    ANNOUNCEMENT_FETCH_RESPONSES,
    ANNOUNCEMENT_HEALTH_RESPONSES,
    ANNOUNCEMENT_IMPORTANT_RESPONSES,
    ANNOUNCEMENT_LIST_RESPONSES,
    ANNOUNCEMENT_MONITOR_EVALUATE_RESPONSES,
    ANNOUNCEMENT_MONITOR_RULE_CREATE_EXAMPLES,
    ANNOUNCEMENT_MONITOR_RULE_CREATE_RESPONSES,
    ANNOUNCEMENT_MONITOR_RULE_DELETE_RESPONSES,
    ANNOUNCEMENT_MONITOR_RULE_UPDATE_EXAMPLES,
    ANNOUNCEMENT_MONITOR_RULE_UPDATE_RESPONSES,
    ANNOUNCEMENT_MONITOR_RULE_LIST_RESPONSES,
    ANNOUNCEMENT_STATS_RESPONSES,
    ANNOUNCEMENT_STATUS_RESPONSES,
    ANNOUNCEMENT_TODAY_RESPONSES,
    ANNOUNCEMENT_TRIGGERED_RECORDS_RESPONSES,
    _build_announcement_summary,
    _detect_announcement_sentiment,
    _extract_announcement_text,
)

try:
    from app.models.announcement import (
        Announcement,
        AnnouncementMonitorRecord,
        AnnouncementMonitorRule,
    )
    from app.services.announcement_service import (
        AnnouncementService,
        get_announcement_service_dependency,
    )

    HAS_ANNOUNCEMENT_SERVICE = True
except Exception:
    HAS_ANNOUNCEMENT_SERVICE = False

router = APIRouter(prefix="/announcement")


@router.get(
    "/health",
    description="检查公告服务路由是否可用，并返回最基础的服务存活状态。",
    responses=ANNOUNCEMENT_HEALTH_RESPONSES,
)
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "announcement"}


@router.get(
    "/status",
    description="返回公告服务的当前状态标记，便于前端确认功能入口是否已启用。",
    responses=ANNOUNCEMENT_STATUS_RESPONSES,
)
async def get_status():
    """获取服务状态"""
    return {"status": "active", "endpoint": "announcement"}


@router.post(
    "/analyze",
    description="提交公告文本和辅助上下文，基于正文关键词返回规则驱动的公告分析结果。",
    response_model=UnifiedResponse[Dict[str, Any]],
    responses=ANNOUNCEMENT_ANALYZE_RESPONSES,
)
async def analyze_data(
    data: dict = Body(..., openapi_examples=ANNOUNCEMENT_ANALYZE_EXAMPLES),
) -> UnifiedResponse[Dict[str, Any]]:
    """返回基于输入公告文本的规则驱动分析结果。"""
    text = _extract_announcement_text(data)
    sentiment, signals, importance_level = _detect_announcement_sentiment(text)
    return UnifiedResponse(
        success=True,
        code=200,
        message="Announcement analysis completed from provided text",
        data={
            "status": "available",
            "endpoint": "announcement",
            "stock_code": data.get("stock_code") or data.get("symbol"),
            "analysis_mode": data.get("analysis_mode") or data.get("analysis_depth"),
            "summary": _build_announcement_summary(sentiment, signals),
            "signals": signals,
            "sentiment": sentiment,
            "importance_level": importance_level,
        },
    )


if HAS_ANNOUNCEMENT_SERVICE:

    @router.post("/fetch", responses=ANNOUNCEMENT_FETCH_RESPONSES)
    async def fetch_announcements(
        symbol: Optional[str] = Query(None, description="股票代码"),
        start_date: Optional[date] = Query(None, description="开始日期"),
        end_date: Optional[date] = Query(None, description="结束日期"),
        category: Optional[str] = Query("all", description="公告类别"),
        service: AnnouncementService = Depends(get_announcement_service_dependency),
    ):
        """
        从数据源获取并保存公告

        Args:
            symbol: 股票代码（可选）
            start_date: 开始日期
            end_date: 结束日期
            category: 公告类别

        Returns:
            Dict: 获取结果
        """
        try:
            # 默认获取最近7天的公告
            if end_date is None:
                end_date = date.today()
            if start_date is None:
                start_date = end_date - timedelta(days=7)

            result = service.fetch_and_save_announcements(
                symbol=symbol, start_date=start_date, end_date=end_date, category=category
            )

            if not result["success"]:
                raise BusinessException(status_code=400, detail=result.get("error", "Failed to fetch"))

            return result

        except BusinessException:
            raise
        except Exception as e:
            raise BusinessException(status_code=500, detail=str(e))

    @router.get("/list", responses=ANNOUNCEMENT_LIST_RESPONSES)
    async def get_announcements(
        stock_code: Optional[str] = Query(None, description="股票代码"),
        start_date: Optional[date] = Query(None, description="开始日期"),
        end_date: Optional[date] = Query(None, description="结束日期"),
        announcement_type: Optional[str] = Query(None, description="公告类型"),
        min_importance: Optional[int] = Query(None, ge=0, le=5, description="最小重要性级别"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        service: AnnouncementService = Depends(get_announcement_service_dependency),
    ):
        """
        查询公告列表

        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            announcement_type: 公告类型
            min_importance: 最小重要性级别
            page: 页码
            page_size: 每页数量

        Returns:
            Dict: 公告列表
        """
        try:
            result = service.get_announcements(
                stock_code=stock_code,
                start_date=start_date,
                end_date=end_date,
                announcement_type=announcement_type,
                min_importance=min_importance,
                page=page,
                page_size=page_size,
            )

            if not result["success"]:
                raise BusinessException(status_code=400, detail=result.get("error", "Query failed"))

            return result

        except BusinessException:
            raise
        except Exception as e:
            raise BusinessException(status_code=500, detail=str(e))

    @router.get("/today", responses=ANNOUNCEMENT_TODAY_RESPONSES)
    async def get_today_announcements(
        min_importance: Optional[int] = Query(0, ge=0, le=5, description="最小重要性级别"),
        service: AnnouncementService = Depends(get_announcement_service_dependency),
    ):
        """
        获取今日公告

        Args:
            min_importance: 最小重要性级别

        Returns:
            Dict: 今日公告列表
        """
        try:
            today = date.today()

            result = service.get_announcements(
                start_date=today,
                end_date=today,
                min_importance=min_importance,
                page=1,
                page_size=100,
            )

            if not result["success"]:
                raise BusinessException(status_code=400, detail=result.get("error", "Query failed"))

            return {
                "success": True,
                "date": today.isoformat(),
                "announcements": result["data"],
                "count": result["total"],
            }

        except BusinessException:
            raise
        except Exception as e:
            raise BusinessException(status_code=500, detail=str(e))

    @router.get("/important", responses=ANNOUNCEMENT_IMPORTANT_RESPONSES)
    async def get_important_announcements(
        days: int = Query(7, ge=1, le=30, description="查询天数"),
        min_importance: int = Query(3, ge=0, le=5, description="最小重要性级别"),
        service: AnnouncementService = Depends(get_announcement_service_dependency),
    ):
        """
        获取重要公告

        Args:
            days: 查询天数（默认7天）
            min_importance: 最小重要性级别（默认3）

        Returns:
            Dict: 重要公告列表
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=days)

            result = service.get_announcements(
                start_date=start_date,
                end_date=end_date,
                min_importance=min_importance,
                page=1,
                page_size=100,
            )

            if not result["success"]:
                raise BusinessException(status_code=400, detail=result.get("error", "Query failed"))

            return {
                "success": True,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "min_importance": min_importance,
                "announcements": result["data"],
                "count": result["total"],
            }

        except BusinessException:
            raise
        except Exception as e:
            raise BusinessException(status_code=500, detail=str(e))

    @router.get("/stats", responses=ANNOUNCEMENT_STATS_RESPONSES)
    async def get_announcement_stats(
        service: AnnouncementService = Depends(get_announcement_service_dependency),
    ):
        """
        获取公告统计信息

        Returns:
            Dict: 统计信息
        """
        try:
            # 获取今日公告
            today_result = service.get_announcements(
                start_date=date.today(), end_date=date.today(), page=1, page_size=1
            )

            # 获取重要公告
            important_result = service.get_announcements(
                start_date=date.today() - timedelta(days=7),
                end_date=date.today(),
                min_importance=3,
                page=1,
                page_size=1,
            )

            # 获取总数
            total_result = service.get_announcements(page=1, page_size=1)

            return {
                "success": True,
                "total_count": total_result.get("total", 0),
                "today_count": today_result.get("total", 0),
                "important_count": important_result.get("total", 0),
                "triggered_count": 0,
                "by_source": {},
                "by_type": {},
                "by_sentiment": {},
            }

        except Exception as e:
            raise BusinessException(status_code=500, detail=str(e))

    @router.get("/monitor-rules", responses=ANNOUNCEMENT_MONITOR_RULE_LIST_RESPONSES)
    async def get_monitor_rules(
        service: AnnouncementService = Depends(get_announcement_service_dependency),
    ):
        """
        获取监控规则列表

        Returns:
            List: 监控规则列表
        """
        try:
            session = service.SessionLocal()

            try:
                rules = session.query(AnnouncementMonitorRule).filter(AnnouncementMonitorRule.is_active is True).all()

                return [
                    {
                        "id": rule.id,
                        "rule_name": rule.rule_name,
                        "stock_codes": rule.stock_codes or [],
                        "keywords": rule.keywords or [],
                        "min_importance_level": rule.min_importance_level,
                        "notify_enabled": rule.notify_enabled,
                        "is_active": rule.is_active,
                    }
                    for rule in rules
                ]
            finally:
                session.close()
        except Exception as e:
            raise BusinessException(status_code=500, detail=str(e))

    @router.post("/monitor-rules", responses=ANNOUNCEMENT_MONITOR_RULE_CREATE_RESPONSES)
    async def create_monitor_rule(
        rule_data: dict = Body(..., openapi_examples=ANNOUNCEMENT_MONITOR_RULE_CREATE_EXAMPLES),
        service: AnnouncementService = Depends(get_announcement_service_dependency),
    ):
        """
        创建监控规则

        Args:
            rule_data: 监控规则创建请求

        Returns:
            Dict: 创建的规则
        """
        try:
            session = service.SessionLocal()

            try:
                # 检查规则名称是否已存在
                existing_rule = (
                    session.query(AnnouncementMonitorRule)
                    .filter(AnnouncementMonitorRule.rule_name == rule_data.get("rule_name"))
                    .first()
                )

                if existing_rule:
                    raise BusinessException(status_code=400, detail="规则名称已存在")

                # 创建新规则
                new_rule = AnnouncementMonitorRule(
                    rule_name=rule_data.get("rule_name"),
                    keywords=rule_data.get("keywords", []),
                    stock_codes=rule_data.get("stock_codes", []),
                    min_importance_level=rule_data.get("min_importance_level", 1),
                    notify_enabled=rule_data.get("notify_enabled", True),
                    is_active=True,
                )

                session.add(new_rule)
                session.commit()
                session.refresh(new_rule)

                return {
                    "success": True,
                    "data": {
                        "id": new_rule.id,
                        "rule_name": new_rule.rule_name,
                        "keywords": new_rule.keywords,
                        "stock_codes": new_rule.stock_codes,
                        "min_importance_level": new_rule.min_importance_level,
                        "notify_enabled": new_rule.notify_enabled,
                        "is_active": new_rule.is_active,
                    },
                }
            finally:
                session.close()
        except BusinessException:
            raise
        except Exception as e:
            raise BusinessException(status_code=500, detail=str(e))

    @router.put("/monitor-rules/{rule_id}", responses=ANNOUNCEMENT_MONITOR_RULE_UPDATE_RESPONSES)
    async def update_monitor_rule(
        rule_id: int = Path(..., description="需要更新的公告监控规则ID。"),
        updates: dict = Body(..., openapi_examples=ANNOUNCEMENT_MONITOR_RULE_UPDATE_EXAMPLES),
        service: AnnouncementService = Depends(get_announcement_service_dependency),
    ):
        """
        更新监控规则

        Args:
            rule_id: 规则ID
            updates: 更新内容

        Returns:
            Dict: 更新后的规则
        """
        try:
            session = service.SessionLocal()

            try:
                rule = session.query(AnnouncementMonitorRule).filter(AnnouncementMonitorRule.id == rule_id).first()

                if not rule:
                    raise BusinessException(status_code=404, detail="规则不存在")

                # 更新字段
                for field, value in updates.items():
                    if hasattr(rule, field) and value is not None:
                        setattr(rule, field, value)

                session.commit()
                session.refresh(rule)

                return {
                    "success": True,
                    "data": {
                        "id": rule.id,
                        "rule_name": rule.rule_name,
                        "keywords": rule.keywords,
                        "stock_codes": rule.stock_codes,
                        "min_importance_level": rule.min_importance_level,
                        "notify_enabled": rule.notify_enabled,
                        "is_active": rule.is_active,
                    },
                }
            finally:
                session.close()
        except BusinessException:
            raise
        except Exception as e:
            raise BusinessException(status_code=500, detail=str(e))

    @router.delete("/monitor-rules/{rule_id}", responses=ANNOUNCEMENT_MONITOR_RULE_DELETE_RESPONSES)
    async def delete_monitor_rule(
        rule_id: int = Path(..., description="需要删除的公告监控规则ID。"),
        service: AnnouncementService = Depends(get_announcement_service_dependency),
    ):
        """
        删除监控规则

        Args:
            rule_id: 规则ID

        Returns:
            Dict: 操作结果
        """
        try:
            session = service.SessionLocal()

            try:
                rule = session.query(AnnouncementMonitorRule).filter(AnnouncementMonitorRule.id == rule_id).first()

                if not rule:
                    raise BusinessException(status_code=404, detail="规则不存在")

                session.delete(rule)
                session.commit()

                return {"success": True, "message": "规则已删除"}
            finally:
                session.close()
        except BusinessException:
            raise
        except Exception as e:
            raise BusinessException(status_code=500, detail=str(e))

    @router.get("/triggered-records", responses=ANNOUNCEMENT_TRIGGERED_RECORDS_RESPONSES)
    async def get_triggered_records(
        rule_id: Optional[int] = Query(None, description="规则ID"),
        stock_code: Optional[str] = Query(None, description="股票代码"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
        service: AnnouncementService = Depends(get_announcement_service_dependency),
    ):
        """
        获取触发记录列表

        Args:
            rule_id: 规则ID
            stock_code: 股票代码
            page: 页码
            page_size: 每页数量

        Returns:
            Dict: 触发记录列表
        """
        try:
            session = service.SessionLocal()

            try:
                query = session.query(AnnouncementMonitorRecord).join(AnnouncementMonitorRule).join(Announcement)

                # 应用过滤条件
                if rule_id:
                    query = query.filter(AnnouncementMonitorRecord.rule_id == rule_id)
                if stock_code:
                    query = query.filter(Announcement.stock_code == stock_code)

                # 获取总数
                total = query.count()

                # 分页查询
                records = (
                    query.order_by(AnnouncementMonitorRecord.triggered_at.desc())
                    .offset((page - 1) * page_size)
                    .limit(page_size)
                    .all()
                )

                # 转换为响应格式
                result = []
                for record in records:
                    result.append(
                        {
                            "id": record.id,
                            "rule_id": record.rule_id,
                            "announcement_id": record.announcement_id,
                            "matched_keywords": record.matched_keywords or [],
                            "triggered_at": record.triggered_at.isoformat() if record.triggered_at else None,
                            "notified": record.notified,
                            "notified_at": record.notified_at.isoformat() if record.notified_at else None,
                            "notification_result": record.notification_result,
                            "rule_name": record.rule.rule_name if record.rule else "",
                            "announcement_title": record.announcement.announcement_title if record.announcement else "",
                            "stock_code": record.announcement.stock_code if record.announcement else "",
                        }
                    )

                return {
                    "success": True,
                    "data": result,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                    "total_pages": (total + page_size - 1) // page_size,
                }
            finally:
                session.close()
        except Exception as e:
            raise BusinessException(status_code=500, detail=str(e))

    @router.post("/monitor/evaluate", responses=ANNOUNCEMENT_MONITOR_EVALUATE_RESPONSES)
    async def evaluate_monitor_rules(
        service: AnnouncementService = Depends(get_announcement_service_dependency),
    ):
        """
        评估所有监控规则

        检查是否有新公告触发监控规则

        Returns:
            Dict: 评估结果
        """
        try:
            result = service.evaluate_monitor_rules()

            if not result["success"]:
                raise BusinessException(status_code=400, detail=result.get("error", "Evaluation failed"))

            return result

        except BusinessException:
            raise
        except Exception as e:
            raise BusinessException(status_code=500, detail=str(e))
