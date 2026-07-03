"""
公告监控服务
Multi-data Source Support

功能：
- 定期获取最新公告
- 评估监控规则
- 触发通知
- 公告分析和评分
"""

import asyncio
import logging
import os
import threading
from datetime import date, datetime, timedelta
from typing import Any, Callable, Dict, List, Mapping, Optional

import pandas as pd
from sqlalchemy import and_, create_engine, desc
from sqlalchemy.orm import Session, sessionmaker

from app.models.announcement import (
    Announcement,
    AnnouncementMonitorRecord,
    AnnouncementMonitorRule,
)
from app.services.openstock_client import (
    OpenStockClient,
    OpenStockClientConfig,
    OpenStockFetchResult,
)

logger = logging.getLogger(__name__)

DEFAULT_OPENSTOCK_BASE_URL = "http://localhost:8050"

# OpenStock native field names → DB schema field names used by
# _save_announcements_to_db. Keeps Layer 3 (DB write) unchanged when
# the upstream provider changes (Cninfo via multi_source_manager →
# OpenStock ANNOUNCEMENTS category).
_ANNOUNCEMENT_FIELD_MAP: Dict[str, str] = {
    "secCode": "stock_code",
    "secName": "stock_name",
    "announcementTitle": "title",
    "announcementType": "type",
    "announcementTime": "publish_time",
    "adjunctUrl": "pdf_url",
    "announcementId": "announcement_id",
}


class AnnouncementService:
    """
    公告监控服务

    负责公告的获取、存储、分析和监控
    """

    def __init__(self, db_url: str = None):
        """
        初始化服务（使用环境变量配置数据库连接）

        Args:
            db_url: 数据库连接URL（如果为None，从环境变量读取）

        环境变量:
            POSTGRESQL_HOST: PostgreSQL主机地址
            POSTGRESQL_PORT: PostgreSQL端口
            POSTGRESQL_USER: PostgreSQL用户名
            POSTGRESQL_PASSWORD: PostgreSQL密码
            POSTGRESQL_DATABASE: PostgreSQL数据库名
        """
        if db_url is None:
            # 从环境变量读取数据库配置
            from app.core.config import settings

            db_url = (
                f"postgresql://{settings.postgresql_user}:"
                f"{settings.postgresql_password}@"
                f"{settings.postgresql_host}:"
                f"{settings.postgresql_port}/"
                f"{settings.postgresql_database}"
            )

        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # OpenStockClient factory — Direction 6 PoC: ANNOUNCEMENTS is
        # an OpenStock-owned category (see
        # OPENSTOCK_STATIC_CATEGORIES), so it MUST be served via
        # OpenStockClient rather than multi_source_manager.
        self._openstock_client_factory: Callable[[], OpenStockClient] = (
            self._build_openstock_client
        )

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
            "仲裁": 3,
        }

        logger.info("AnnouncementService initialized")

    def _build_openstock_client(self) -> OpenStockClient:
        base_url = (
            os.getenv("OPENSTOCK_BASE_URL")
            or os.getenv("OPENSTOCK_API_BASE_URL")
            or DEFAULT_OPENSTOCK_BASE_URL
        ).strip()
        try:
            timeout_seconds = float(os.getenv("OPENSTOCK_TIMEOUT_SECONDS", "5.0"))
        except ValueError:
            timeout_seconds = 5.0
        return OpenStockClient(
            OpenStockClientConfig(
                base_url=base_url or DEFAULT_OPENSTOCK_BASE_URL,
                timeout_seconds=timeout_seconds,
            )
        )

    def _run_async(self, async_factory: Callable[[], Any]) -> Any:
        """Bridge sync→async for OpenStockClient (async) callers.

        Mirrors ``market_data_service_v2._run_async`` so the bridging
        behavior is identical repo-wide. If no event loop is running
        in the current thread, ``asyncio.run`` is used directly;
        otherwise a daemon thread is spawned to avoid the
        "asyncio.run() cannot be called from a running event loop"
        error when this service is invoked from an ``async def`` route
        handler.
        """
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(async_factory())

        result: Any = None
        error: BaseException | None = None

        def run_in_thread() -> None:
            nonlocal result, error
            try:
                result = asyncio.run(async_factory())
            except BaseException as exc:
                error = exc

        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()
        thread.join()
        if error is not None:
            raise error
        return result

    def _fetch_announcements_sync(
        self,
        *,
        symbol: Optional[str],
        start_date: date,
        end_date: date,
        category: Optional[str],
    ) -> OpenStockFetchResult:
        """Fetch ANNOUNCEMENTS via OpenStockClient (Direction 6 PoC).

        ANNOUNCEMENTS is in :data:`OPENSTOCK_STATIC_CATEGORIES`, so
        this MUST NOT route through ExtraSourceRouter. The
        ``_run_async`` bridge handles the OpenStockClient async API.
        """
        params: Dict[str, Any] = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        }
        if symbol is not None:
            params["symbol"] = symbol
        if category is not None:
            params["category"] = category

        async def fetch_once() -> OpenStockFetchResult:
            client = self._openstock_client_factory()
            try:
                return await client.fetch("ANNOUNCEMENTS", params=params)
            finally:
                await client.aclose()

        return self._run_async(fetch_once)

    @staticmethod
    def _openstock_result_to_dataframe(result: OpenStockFetchResult) -> pd.DataFrame:
        """Normalize OpenStock ANNOUNCEMENTS raw records into the
        DataFrame schema that ``_save_announcements_to_db`` expects.

        Field rename map mirrors the legacy Cninfo adapter so DB
        schema stays unchanged across the migration.
        """
        records = result.data
        if not isinstance(records, list) or not records:
            return pd.DataFrame()

        rows: List[Dict[str, Any]] = []
        for record in records:
            if not isinstance(record, Mapping):
                continue
            row: Dict[str, Any] = {}
            for src, dst in _ANNOUNCEMENT_FIELD_MAP.items():
                if src in record:
                    row[dst] = record[src]
            rows.append(row)

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(rows)
        if "publish_time" in df.columns:
            df["publish_time"] = pd.to_datetime(
                df["publish_time"], unit="ms", errors="coerce"
            )
            df["publish_date"] = df["publish_time"].dt.date
        if "pdf_url" in df.columns:
            df["pdf_url"] = df["pdf_url"].apply(
                lambda x: f"http://static.cninfo.com.cn/{x}" if x else None
            )
        df["data_source"] = "cninfo"
        return df

    def fetch_and_save_announcements(
        self,
        symbol: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category: Optional[str] = None,
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
            # Direction 6 PoC: ANNOUNCEMENTS is OpenStock-owned (in
            # OPENSTOCK_STATIC_CATEGORIES), so dispatch via
            # OpenStockClient directly. Layer 1 guard ensures no
            # ExtraSource adapter can shadow this category.
            end_date_resolved = end_date or date.today()
            start_date_resolved = start_date or (end_date_resolved - timedelta(days=7))

            fetch_result = self._fetch_announcements_sync(
                symbol=symbol,
                start_date=start_date_resolved,
                end_date=end_date_resolved,
                category=category,
            )

            df = self._openstock_result_to_dataframe(fetch_result)

            if df.empty:
                return {"success": True, "message": "No new announcements", "count": 0}

            # 保存到数据库
            saved_count, updated_count = self._save_announcements_to_db(df)

            logger.info("Saved %(saved_count)s new announcements, updated %(updated_count)s")

            return {
                "success": True,
                "saved_count": saved_count,
                "updated_count": updated_count,
                "total_fetched": len(df),
                "source": fetch_result.source or "openstock",
            }

        except Exception as e:
            logger.error("Failed to fetch and save announcements: %(e)s")
            return {"success": False, "error": str(e)}

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
                existing = (
                    session.query(Announcement)
                    .filter(
                        and_(
                            Announcement.stock_code == row.get("stock_code"),
                            Announcement.source_id == row.get("announcement_id"),
                            Announcement.data_source == row.get("data_source", "cninfo"),
                        )
                    )
                    .first()
                )

                if existing:
                    # 更新现有记录
                    existing.announcement_title = row.get("title", existing.announcement_title)
                    existing.announcement_type = row.get("type", existing.announcement_type)
                    existing.updated_at = datetime.now()
                    updated_count += 1
                else:
                    # 创建新记录
                    announcement = Announcement(
                        stock_code=row.get("stock_code"),
                        stock_name=row.get("stock_name"),
                        announcement_title=row.get("title", ""),
                        announcement_type=row.get("type"),
                        publish_date=row.get("publish_date", date.today()),
                        publish_time=row.get("publish_time"),
                        url=row.get("pdf_url"),
                        data_source=row.get("data_source", "cninfo"),
                        source_id=row.get("announcement_id"),
                        importance_level=self._calculate_importance(row.get("title", "")),
                        sentiment=self._analyze_sentiment(row.get("title", "")),
                    )

                    session.add(announcement)
                    saved_count += 1

            session.commit()

        except Exception:
            session.rollback()
            logger.error("Failed to save announcements to DB: %(e)s")
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
            rules = session.query(AnnouncementMonitorRule).filter(AnnouncementMonitorRule.is_active is True).all()

            logger.info("Evaluating {len(rules)} active monitor rules")

            # 获取今天的公告
            today = date.today()
            announcements = session.query(Announcement).filter(Announcement.publish_date == today).all()

            logger.info("Found {len(announcements)} announcements for today")

            # 评估每个规则
            for rule in rules:
                triggered = self._evaluate_single_rule(session, rule, announcements)
                triggered_count += triggered

            session.commit()

            return {
                "success": True,
                "rules_evaluated": len(rules),
                "triggered_count": triggered_count,
            }

        except Exception as e:
            session.rollback()
            logger.error("Failed to evaluate monitor rules: %(e)s")
            return {"success": False, "error": str(e)}

        finally:
            session.close()

    def _evaluate_single_rule(
        self,
        session: Session,
        rule: AnnouncementMonitorRule,
        announcements: List[Announcement],
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
            existing = (
                session.query(AnnouncementMonitorRecord)
                .filter(
                    and_(
                        AnnouncementMonitorRecord.rule_id == rule.id,
                        AnnouncementMonitorRecord.announcement_id == announcement.id,
                    )
                )
                .first()
            )

            if existing:
                continue

            # 检查规则条件
            if not self._check_rule_conditions(rule, announcement):
                continue

            # 创建监控记录
            matched_keywords = self._find_matched_keywords(rule.keywords, announcement.announcement_title)

            record = AnnouncementMonitorRecord(
                rule_id=rule.id,
                announcement_id=announcement.id,
                matched_keywords=matched_keywords,
                triggered_at=datetime.now(),
            )

            session.add(record)
            triggered_count += 1

            logger.info("Rule '{rule.rule_name}' triggered for announcement {announcement.id}")

            # 发送通知（如果启用）
            if rule.notify_enabled:
                self._send_notification(rule, announcement, matched_keywords)

        return triggered_count

    def _check_rule_conditions(self, rule: AnnouncementMonitorRule, announcement: Announcement) -> bool:
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
            matched_keywords = self._find_matched_keywords(rule.keywords, announcement.announcement_title)
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
        matched_keywords: list,
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
        page_size: int = 20,
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
            announcements = (
                query.order_by(desc(Announcement.publish_date)).offset((page - 1) * page_size).limit(page_size).all()
            )

            return {
                "success": True,
                "data": [self._announcement_to_dict(a) for a in announcements],
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
            }

        except Exception as e:
            logger.error("Failed to query announcements: %(e)s")
            return {"success": False, "error": str(e)}

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
            "publish_date": (announcement.publish_date.isoformat() if announcement.publish_date else None),
            "publish_time": (announcement.publish_time.isoformat() if announcement.publish_time else None),
            "url": announcement.url,
            "importance_level": announcement.importance_level,
            "sentiment": announcement.sentiment,
            "data_source": announcement.data_source,
        }


# 全局单例
_announcement_service = None


def get_announcement_service() -> AnnouncementService:
    """获取公告服务单例"""
    global _announcement_service
    if _announcement_service is None:
        _announcement_service = AnnouncementService()
    return _announcement_service
