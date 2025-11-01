"""
公告监控服务
Phase 3: ValueCell Migration - Multi-data Source Support

功能：
- 定期获取最新公告
- 评估监控规则
- 触发通知
- 公告分析和评分
"""

import re
from datetime import date, datetime, timedelta
from typing import List, Optional, Dict, Any
import pandas as pd
from sqlalchemy import create_engine, and_, or_, desc, func
from sqlalchemy.orm import sessionmaker, Session
import logging

from app.models.announcement import (
    Announcement,
    AnnouncementMonitorRule,
    AnnouncementMonitorRecord,
    AnnouncementCreate,
    AnnouncementResponse
)
from app.services.multi_source_manager import get_multi_source_manager
from app.adapters.base import DataSourceType

logger = logging.getLogger(__name__)


class AnnouncementService:
    """
    公告监控服务

    负责公告的获取、存储、分析和监控
    """

    def __init__(self, db_url: str = None):
        """
        初始化服务

        Args:
            db_url: 数据库连接URL
        """
        if db_url is None:
            db_url = "postgresql://postgres:c790414J@192.168.123.104:5438/mystocks"

        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # 获取多数据源管理器
        self.multi_source_manager = get_multi_source_manager()

        # 重要关键词字典（用于重要性评分）
        self.important_keywords = {
            "重大": 5,
            "重组": 5,
            "并购": 5,
            "收购": 5,
            "增发": 4,
            "配股": 4,
            "分红": 3,
            "业绩预增": 4,
            "业绩预降": 4,
            "退市": 5,
            "ST": 4,
            "*ST": 5,
            "风险": 3,
            "诉讼": 3,
            "仲裁": 3
        }

        logger.info("AnnouncementService initialized")

    def fetch_and_save_announcements(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取并保存公告

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            category: 公告类别

        Returns:
            Dict: 执行结果
        """
        try:
            # 从多数据源获取公告
            result = self.multi_source_manager.fetch_announcements(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                category=category,
                source=DataSourceType.CNINFO
            )

            if not result["success"]:
                return {
                    "success": False,
                    "error": result.get("error", "Failed to fetch announcements")
                }

            df = result["data"]

            if df.empty:
                return {
                    "success": True,
                    "message": "No new announcements",
                    "count": 0
                }

            # 保存到数据库
            saved_count, updated_count = self._save_announcements_to_db(df)

            logger.info(f"Saved {saved_count} new announcements, updated {updated_count}")

            return {
                "success": True,
                "saved_count": saved_count,
                "updated_count": updated_count,
                "total_fetched": len(df),
                "source": result["source"]
            }

        except Exception as e:
            logger.error(f"Failed to fetch and save announcements: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _save_announcements_to_db(self, df: pd.DataFrame) -> tuple:
        """
        保存公告到数据库

        Args:
            df: 公告DataFrame

        Returns:
            tuple: (新增数量, 更新数量)
        """
        session = self.SessionLocal()
        saved_count = 0
        updated_count = 0

        try:
            for _, row in df.iterrows():
                # 检查是否已存在
                existing = session.query(Announcement).filter(
                    and_(
                        Announcement.stock_code == row.get('stock_code'),
                        Announcement.source_id == row.get('announcement_id'),
                        Announcement.data_source == row.get('data_source', 'cninfo')
                    )
                ).first()

                if existing:
                    # 更新现有记录
                    existing.announcement_title = row.get('title', existing.announcement_title)
                    existing.announcement_type = row.get('type', existing.announcement_type)
                    existing.updated_at = datetime.now()
                    updated_count += 1
                else:
                    # 创建新记录
                    announcement = Announcement(
                        stock_code=row.get('stock_code'),
                        stock_name=row.get('stock_name'),
                        announcement_title=row.get('title', ''),
                        announcement_type=row.get('type'),
                        publish_date=row.get('publish_date', date.today()),
                        publish_time=row.get('publish_time'),
                        url=row.get('pdf_url'),
                        data_source=row.get('data_source', 'cninfo'),
                        source_id=row.get('announcement_id'),
                        importance_level=self._calculate_importance(row.get('title', '')),
                        sentiment=self._analyze_sentiment(row.get('title', ''))
                    )

                    session.add(announcement)
                    saved_count += 1

            session.commit()

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to save announcements to DB: {e}")
            raise

        finally:
            session.close()

        return saved_count, updated_count

    def _calculate_importance(self, title: str) -> int:
        """
        计算公告重要性等级

        Args:
            title: 公告标题

        Returns:
            int: 重要性等级 (0-5)
        """
        max_level = 0

        for keyword, level in self.important_keywords.items():
            if keyword in title:
                max_level = max(max_level, level)

        return max_level

    def _analyze_sentiment(self, title: str) -> str:
        """
        分析公告情感倾向

        Args:
            title: 公告标题

        Returns:
            str: positive, negative, neutral
        """
        positive_keywords = ["预增", "增长", "分红", "派息", "利好", "中标", "合作"]
        negative_keywords = ["预降", "下降", "亏损", "风险", "诉讼", "退市", "ST"]

        positive_count = sum(1 for kw in positive_keywords if kw in title)
        negative_count = sum(1 for kw in negative_keywords if kw in title)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def evaluate_monitor_rules(self) -> Dict[str, Any]:
        """
        评估所有活跃的监控规则

        Returns:
            Dict: 评估结果
        """
        session = self.SessionLocal()
        triggered_count = 0

        try:
            # 获取所有活跃规则
            rules = session.query(AnnouncementMonitorRule).filter(
                AnnouncementMonitorRule.is_active == True
            ).all()

            logger.info(f"Evaluating {len(rules)} active monitor rules")

            # 获取今天的公告
            today = date.today()
            announcements = session.query(Announcement).filter(
                Announcement.publish_date == today
            ).all()

            logger.info(f"Found {len(announcements)} announcements for today")

            # 评估每个规则
            for rule in rules:
                triggered = self._evaluate_single_rule(session, rule, announcements)
                triggered_count += triggered

            session.commit()

            return {
                "success": True,
                "rules_evaluated": len(rules),
                "triggered_count": triggered_count
            }

        except Exception as e:
            session.rollback()
            logger.error(f"Failed to evaluate monitor rules: {e}")
            return {
                "success": False,
                "error": str(e)
            }

        finally:
            session.close()

    def _evaluate_single_rule(
        self,
        session: Session,
        rule: AnnouncementMonitorRule,
        announcements: List[Announcement]
    ) -> int:
        """
        评估单个监控规则

        Args:
            session: 数据库会话
            rule: 监控规则
            announcements: 公告列表

        Returns:
            int: 触发数量
        """
        triggered_count = 0

        for announcement in announcements:
            # 检查是否已经触发过
            existing = session.query(AnnouncementMonitorRecord).filter(
                and_(
                    AnnouncementMonitorRecord.rule_id == rule.id,
                    AnnouncementMonitorRecord.announcement_id == announcement.id
                )
            ).first()

            if existing:
                continue

            # 检查规则条件
            if not self._check_rule_conditions(rule, announcement):
                continue

            # 创建监控记录
            matched_keywords = self._find_matched_keywords(
                rule.keywords,
                announcement.announcement_title
            )

            record = AnnouncementMonitorRecord(
                rule_id=rule.id,
                announcement_id=announcement.id,
                matched_keywords=matched_keywords,
                triggered_at=datetime.now()
            )

            session.add(record)
            triggered_count += 1

            logger.info(f"Rule '{rule.rule_name}' triggered for announcement {announcement.id}")

            # 发送通知（如果启用）
            if rule.notify_enabled:
                self._send_notification(rule, announcement, matched_keywords)

        return triggered_count

    def _check_rule_conditions(
        self,
        rule: AnnouncementMonitorRule,
        announcement: Announcement
    ) -> bool:
        """
        检查规则条件是否满足

        Args:
            rule: 监控规则
            announcement: 公告

        Returns:
            bool: 是否满足条件
        """
        # 检查股票代码（如果规则指定了）
        if rule.stock_codes:
            if announcement.stock_code not in rule.stock_codes:
                return False

        # 检查公告类型
        if rule.announcement_types:
            if announcement.announcement_type not in rule.announcement_types:
                return False

        # 检查重要性级别
        if announcement.importance_level < rule.min_importance_level:
            return False

        # 检查关键词
        if rule.keywords:
            matched_keywords = self._find_matched_keywords(
                rule.keywords,
                announcement.announcement_title
            )
            if not matched_keywords:
                return False

        return True

    def _find_matched_keywords(self, keywords: list, text: str) -> list:
        """
        查找匹配的关键词

        Args:
            keywords: 关键词列表
            text: 文本

        Returns:
            list: 匹配的关键词
        """
        matched = []

        for keyword in keywords:
            if keyword in text:
                matched.append(keyword)

        return matched

    def _send_notification(
        self,
        rule: AnnouncementMonitorRule,
        announcement: Announcement,
        matched_keywords: list
    ):
        """
        发送通知

        Args:
            rule: 监控规则
            announcement: 公告
            matched_keywords: 匹配的关键词
        """
        # 简化实现：仅记录日志
        # 实际应用中应该发送邮件、webhook等
        logger.info(
            f"[NOTIFICATION] Rule: {rule.rule_name}, "
            f"Stock: {announcement.stock_code} {announcement.stock_name}, "
            f"Title: {announcement.announcement_title}, "
            f"Keywords: {matched_keywords}"
        )

    def get_announcements(
        self,
        stock_code: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        announcement_type: Optional[str] = None,
        min_importance: Optional[int] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        查询公告

        Args:
            stock_code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            announcement_type: 公告类型
            min_importance: 最小重要性级别
            page: 页码
            page_size: 每页数量

        Returns:
            Dict: 查询结果
        """
        session = self.SessionLocal()

        try:
            query = session.query(Announcement)

            # 应用过滤条件
            if stock_code:
                query = query.filter(Announcement.stock_code == stock_code)

            if start_date:
                query = query.filter(Announcement.publish_date >= start_date)

            if end_date:
                query = query.filter(Announcement.publish_date <= end_date)

            if announcement_type:
                query = query.filter(Announcement.announcement_type == announcement_type)

            if min_importance is not None:
                query = query.filter(Announcement.importance_level >= min_importance)

            # 计算总数
            total = query.count()

            # 分页
            announcements = query.order_by(desc(Announcement.publish_date)) \
                .offset((page - 1) * page_size) \
                .limit(page_size) \
                .all()

            return {
                "success": True,
                "data": [self._announcement_to_dict(a) for a in announcements],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }

        except Exception as e:
            logger.error(f"Failed to query announcements: {e}")
            return {
                "success": False,
                "error": str(e)
            }

        finally:
            session.close()

    def _announcement_to_dict(self, announcement: Announcement) -> dict:
        """转换公告为字典"""
        return {
            "id": announcement.id,
            "stock_code": announcement.stock_code,
            "stock_name": announcement.stock_name,
            "title": announcement.announcement_title,
            "type": announcement.announcement_type,
            "publish_date": announcement.publish_date.isoformat() if announcement.publish_date else None,
            "publish_time": announcement.publish_time.isoformat() if announcement.publish_time else None,
            "url": announcement.url,
            "importance_level": announcement.importance_level,
            "sentiment": announcement.sentiment,
            "data_source": announcement.data_source
        }


# 全局单例
_announcement_service = None


def get_announcement_service() -> AnnouncementService:
    """获取公告服务单例"""
    global _announcement_service
    if _announcement_service is None:
        _announcement_service = AnnouncementService()
    return _announcement_service
