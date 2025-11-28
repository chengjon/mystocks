"""
Announcement API
Multi-data Source Support

公告查询和监控的API端点
"""

from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Path
from pydantic import BaseModel

from app.services.announcement_service import get_announcement_service
from app.models.announcement import (
    AnnouncementResponse,
    AnnouncementMonitorRuleCreate,
    AnnouncementMonitorRuleUpdate,
    AnnouncementMonitorRuleResponse,
    AnnouncementStatsResponse,
)

router = APIRouter(prefix="/api/announcement", tags=["announcement"])


# ============================================================================
# API Endpoints
# ============================================================================


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
            raise HTTPException(
                status_code=400, detail=result.get("error", "Failed to fetch")
            )

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
    min_importance: Optional[int] = Query(
        None, ge=0, le=5, description="最小重要性级别"
    ),
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
            raise HTTPException(
                status_code=400, detail=result.get("error", "Query failed")
            )

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
            raise HTTPException(
                status_code=400, detail=result.get("error", "Query failed")
            )

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
            raise HTTPException(
                status_code=400, detail=result.get("error", "Query failed")
            )

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


@router.get("/stock/{stock_code}")
async def get_stock_announcements(
    stock_code: str = Path(..., description="股票代码"),
    days: int = Query(30, ge=1, le=365, description="查询天数"),
):
    """
    获取指定股票的公告

    Args:
        stock_code: 股票代码
        days: 查询天数

    Returns:
        Dict: 股票公告列表
    """
    try:
        service = get_announcement_service()

        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        result = service.get_announcements(
            stock_code=stock_code,
            start_date=start_date,
            end_date=end_date,
            page=1,
            page_size=100,
        )

        if not result["success"]:
            raise HTTPException(
                status_code=400, detail=result.get("error", "Query failed")
            )

        return {
            "success": True,
            "stock_code": stock_code,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "announcements": result["data"],
            "count": result["total"],
        }

    except HTTPException:
        raise
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
            raise HTTPException(
                status_code=400, detail=result.get("error", "Evaluation failed")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_announcement_stats():
    """
    获取公告统计信息

    Returns:
        AnnouncementStatsResponse: 统计信息
    """
    try:
        # 简化实现，返回基本统计
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
            "by_source": {},
            "by_type": {},
            "by_sentiment": {},
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/types")
async def get_announcement_types():
    """
    获取支持的公告类型

    Returns:
        Dict: 公告类型列表
    """
    from app.adapters.cninfo_adapter import get_cninfo_adapter

    try:
        adapter = get_cninfo_adapter()
        types = adapter.get_announcement_types()

        return {
            "success": True,
            "types": [
                {"code": code, "name": name} for code, (_, name) in types.items()
            ],
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
            rules = session.query(AnnouncementMonitorRule).filter(
                AnnouncementMonitorRule.is_active == True
            ).all()
            
            return [AnnouncementMonitorRuleResponse.from_orm(rule) for rule in rules]
        finally:
            session.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/monitor-rules")
async def create_monitor_rule(rule: AnnouncementMonitorRuleCreate):
    """
    创建监控规则

    Args:
        rule: 监控规则创建请求

    Returns:
        AnnouncementMonitorRuleResponse: 创建的规则
    """
    try:
        service = get_announcement_service()
        session = service.SessionLocal()
        
        try:
            # 检查规则名称是否已存在
            existing_rule = session.query(AnnouncementMonitorRule).filter(
                AnnouncementMonitorRule.rule_name == rule.rule_name
            ).first()
            
            if existing_rule:
                raise HTTPException(status_code=400, detail="规则名称已存在")
            
            # 创建新规则
            new_rule = AnnouncementMonitorRule(
                rule_name=rule.rule_name,
                keywords=rule.keywords,
                announcement_types=rule.announcement_types,
                stock_codes=rule.stock_codes,
                min_importance_level=rule.min_importance_level,
                notify_enabled=rule.notify_enabled,
                notify_channels=rule.notify_channels,
                is_active=True
            )
            
            session.add(new_rule)
            session.commit()
            session.refresh(new_rule)
            
            return AnnouncementMonitorRuleResponse.from_orm(new_rule)
        finally:
            session.close()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/monitor-rules/{rule_id}")
async def update_monitor_rule(rule_id: int, updates: AnnouncementMonitorRuleUpdate):
    """
    更新监控规则

    Args:
        rule_id: 规则ID
        updates: 更新内容

    Returns:
        AnnouncementMonitorRuleResponse: 更新后的规则
    """
    try:
        service = get_announcement_service()
        session = service.SessionLocal()
        
        try:
            rule = session.query(AnnouncementMonitorRule).filter(
                AnnouncementMonitorRule.id == rule_id
            ).first()
            
            if not rule:
                raise HTTPException(status_code=404, detail="规则不存在")
            
            # 更新字段
            for field, value in updates.dict(exclude_unset=True).items():
                if hasattr(rule, field):
                    setattr(rule, field, value)
            
            session.commit()
            session.refresh(rule)
            
            return AnnouncementMonitorRuleResponse.from_orm(rule)
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
            rule = session.query(AnnouncementMonitorRule).filter(
                AnnouncementMonitorRule.id == rule_id
            ).first()
            
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
            query = session.query(AnnouncementMonitorRecord).join(
                AnnouncementMonitorRule
            ).join(Announcement)
            
            # 应用过滤条件
            if rule_id:
                query = query.filter(AnnouncementMonitorRecord.rule_id == rule_id)
            if stock_code:
                query = query.filter(Announcement.stock_code == stock_code)
            
            # 获取总数
            total = query.count()
            
            # 分页查询
            records = query.order_by(AnnouncementMonitorRecord.triggered_at.desc()).offset(
                (page - 1) * page_size
            ).limit(page_size).all()
            
            # 转换为响应格式
            result = []
            for record in records:
                result.append({
                    "id": record.id,
                    "rule_id": record.rule_id,
                    "announcement_id": record.announcement_id,
                    "matched_keywords": record.matched_keywords,
                    "triggered_at": record.triggered_at.isoformat(),
                    "notified": record.notified,
                    "notified_at": record.notified_at.isoformat() if record.notified_at else None,
                    "notification_result": record.notification_result,
                    "rule_name": record.rule.rule_name,
                    "announcement_title": record.announcement.announcement_title,
                    "stock_code": record.announcement.stock_code
                })
            
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
