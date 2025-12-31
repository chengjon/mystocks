"""
公告监控API路由
"""

from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

try:
    from app.models.announcement import (
        Announcement,
        AnnouncementMonitorRecord,
        AnnouncementMonitorRule,
    )
    from app.services.announcement_service import get_announcement_service

    HAS_ANNOUNCEMENT_SERVICE = True
except Exception:
    HAS_ANNOUNCEMENT_SERVICE = False

router = APIRouter(prefix="/announcement")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "announcement"}


@router.get("/status")
async def get_status():
    """获取服务状态"""
    return {"status": "active", "endpoint": "announcement"}


@router.post("/analyze")
async def analyze_data(data: dict):
    """AI分析数据"""
    # TODO: 实现AI分析逻辑
    return {"result": "分析完成", "endpoint": "announcement"}


if HAS_ANNOUNCEMENT_SERVICE:

    @router.post("/fetch")
    async def fetch_announcements(
        symbol: Optional[str] = Query(None, description="股票代码"),
        start_date: Optional[date] = Query(None, description="开始日期"),
        end_date: Optional[date] = Query(None, description="结束日期"),
        category: Optional[str] = Query("all", description="公告类别"),
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
            service = get_announcement_service()

            # 默认获取最近7天的公告
            if end_date is None:
                end_date = date.today()
            if start_date is None:
                start_date = end_date - timedelta(days=7)

            result = service.fetch_and_save_announcements(
                symbol=symbol, start_date=start_date, end_date=end_date, category=category
            )

            if not result["success"]:
                raise HTTPException(status_code=400, detail=result.get("error", "Failed to fetch"))

            return result

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/list")
    async def get_announcements(
        stock_code: Optional[str] = Query(None, description="股票代码"),
        start_date: Optional[date] = Query(None, description="开始日期"),
        end_date: Optional[date] = Query(None, description="结束日期"),
        announcement_type: Optional[str] = Query(None, description="公告类型"),
        min_importance: Optional[int] = Query(None, ge=0, le=5, description="最小重要性级别"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
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
            service = get_announcement_service()

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
                raise HTTPException(status_code=400, detail=result.get("error", "Query failed"))

            return result

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/today")
    async def get_today_announcements(
        min_importance: Optional[int] = Query(0, ge=0, le=5, description="最小重要性级别")
    ):
        """
        获取今日公告

        Args:
            min_importance: 最小重要性级别

        Returns:
            Dict: 今日公告列表
        """
        try:
            service = get_announcement_service()

            today = date.today()

            result = service.get_announcements(
                start_date=today,
                end_date=today,
                min_importance=min_importance,
                page=1,
                page_size=100,
            )

            if not result["success"]:
                raise HTTPException(status_code=400, detail=result.get("error", "Query failed"))

            return {
                "success": True,
                "date": today.isoformat(),
                "announcements": result["data"],
                "count": result["total"],
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/important")
    async def get_important_announcements(
        days: int = Query(7, ge=1, le=30, description="查询天数"),
        min_importance: int = Query(3, ge=0, le=5, description="最小重要性级别"),
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
            service = get_announcement_service()

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
                raise HTTPException(status_code=400, detail=result.get("error", "Query failed"))

            return {
                "success": True,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "min_importance": min_importance,
                "announcements": result["data"],
                "count": result["total"],
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/stats")
    async def get_announcement_stats():
        """
        获取公告统计信息

        Returns:
            Dict: 统计信息
        """
        try:
            service = get_announcement_service()

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
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/monitor-rules")
    async def get_monitor_rules():
        """
        获取监控规则列表

        Returns:
            List: 监控规则列表
        """
        try:
            service = get_announcement_service()
            session = service.SessionLocal()

            try:
                rules = session.query(AnnouncementMonitorRule).filter(AnnouncementMonitorRule.is_active.is_(True)).all()

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
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/monitor-rules")
    async def create_monitor_rule(rule_data: dict):
        """
        创建监控规则

        Args:
            rule_data: 监控规则创建请求

        Returns:
            Dict: 创建的规则
        """
        try:
            service = get_announcement_service()
            session = service.SessionLocal()

            try:
                # 检查规则名称是否已存在
                existing_rule = (
                    session.query(AnnouncementMonitorRule)
                    .filter(AnnouncementMonitorRule.rule_name == rule_data.get("rule_name"))
                    .first()
                )

                if existing_rule:
                    raise HTTPException(status_code=400, detail="规则名称已存在")

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
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.put("/monitor-rules/{rule_id}")
    async def update_monitor_rule(rule_id: int, updates: dict):
        """
        更新监控规则

        Args:
            rule_id: 规则ID
            updates: 更新内容

        Returns:
            Dict: 更新后的规则
        """
        try:
            service = get_announcement_service()
            session = service.SessionLocal()

            try:
                rule = session.query(AnnouncementMonitorRule).filter(AnnouncementMonitorRule.id == rule_id).first()

                if not rule:
                    raise HTTPException(status_code=404, detail="规则不存在")

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
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.delete("/monitor-rules/{rule_id}")
    async def delete_monitor_rule(rule_id: int):
        """
        删除监控规则

        Args:
            rule_id: 规则ID

        Returns:
            Dict: 操作结果
        """
        try:
            service = get_announcement_service()
            session = service.SessionLocal()

            try:
                rule = session.query(AnnouncementMonitorRule).filter(AnnouncementMonitorRule.id == rule_id).first()

                if not rule:
                    raise HTTPException(status_code=404, detail="规则不存在")

                session.delete(rule)
                session.commit()

                return {"success": True, "message": "规则已删除"}
            finally:
                session.close()
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/triggered-records")
    async def get_triggered_records(
        rule_id: Optional[int] = Query(None, description="规则ID"),
        stock_code: Optional[str] = Query(None, description="股票代码"),
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(20, ge=1, le=100, description="每页数量"),
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
            service = get_announcement_service()
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
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/monitor/evaluate")
    async def evaluate_monitor_rules():
        """
        评估所有监控规则

        检查是否有新公告触发监控规则

        Returns:
            Dict: 评估结果
        """
        try:
            service = get_announcement_service()

            result = service.evaluate_monitor_rules()

            if not result["success"]:
                raise HTTPException(status_code=400, detail=result.get("error", "Evaluation failed"))

            return result

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
