"""
PostgreSQL关系数据源实现

本模块实现了IRelationalDataSource接口，使用PostgreSQL数据库作为后端存储。
负责处理用户配置、策略管理、风险预警、股票基础信息等结构化关系数据。

特性:
- 完整的ACID事务支持
- 高效的JOIN查询
- JSONB字段支持半结构化数据
- 全文搜索 (pg_trgm扩展)
- 连接池管理

作者: MyStocks Backend Team
创建日期: 2025-11-21
版本: 1.0.0
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

from src.interfaces.relational_data_source import IRelationalDataSource
from src.data_access.postgresql_access import PostgreSQLDataAccess

logger = logging.getLogger(__name__)


class PostgreSQLRelationalDataSource(IRelationalDataSource):
    """
    PostgreSQL关系数据源实现

    使用PostgreSQL数据库实现IRelationalDataSource接口的所有方法。
    提供生产级的关系数据存储和查询能力。

    核心功能:
    - 自选股管理 (4个方法)
    - 策略配置管理 (4个方法)
    - 风险管理配置 (3个方法)
    - 用户配置管理 (2个方法)
    - 股票基础信息 (2个方法)
    - 行业概念板块 (4个方法)
    - 数据库操作辅助 (4个方法)
    """

    def __init__(self, connection_pool_size: int = 20):
        """
        初始化PostgreSQL关系数据源

        Args:
            connection_pool_size: 连接池大小
        """
        self.pg_access = PostgreSQLDataAccess()
        self._connection_pool_size = connection_pool_size
        logger.info("PostgreSQL关系数据源初始化完成 (连接池大小: %s)", connection_pool_size)

    # ==================== 自选股管理 ====================

    def get_watchlist(
        self, user_id: int, list_type: str = "favorite", include_stock_info: bool = True
    ) -> List[Dict[str, Any]]:
        """
        获取自选股列表

        使用LEFT JOIN避免N+1查询问题，一次查询获取所有数据
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            if include_stock_info:
                sql = """
                    SELECT
                        w.id, w.user_id, w.symbol, w.list_type,
                        w.note, w.added_at,
                        s.name, s.industry, s.market, s.pinyin
                    FROM watchlist w
                    LEFT JOIN stock_basic_info s ON w.symbol = s.symbol
                    WHERE w.user_id = %s AND w.list_type = %s
                    ORDER BY w.added_at DESC
                """
            else:
                sql = """
                    SELECT id, user_id, symbol, list_type, note, added_at
                    FROM watchlist
                    WHERE user_id = %s AND list_type = %s
                    ORDER BY w.added_at DESC
                """

            cursor.execute(sql, (user_id, list_type))
            rows = cursor.fetchall()

            result = []
            for row in rows:
                item = {
                    "id": row[0],
                    "user_id": row[1],
                    "symbol": row[2],
                    "list_type": row[3],
                    "note": row[4],
                    "added_at": row[5].strftime("%Y-%m-%d %H:%M:%S") if row[5] else None,
                }

                if include_stock_info and len(row) > 6:
                    item["stock_info"] = {
                        "name": row[6],
                        "industry": row[7],
                        "market": row[8],
                        "pinyin": row[9],
                    }

                result.append(item)

            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("获取自选股成功: user_id=%s, list_type=%s, count=%s", user_id, list_type, len(result))
            return result

        except Exception as e:
            logger.error("获取自选股失败: %s", e)
            raise

    def add_to_watchlist(
        self,
        user_id: int,
        symbol: str,
        list_type: str = "favorite",
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        添加股票到自选列表

        使用INSERT ... ON CONFLICT处理重复插入
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            # 检查是否已存在
            check_sql = """
                SELECT id FROM watchlist
                WHERE user_id = %s AND symbol = %s AND list_type = %s
            """
            cursor.execute(check_sql, (user_id, symbol, list_type))
            if cursor.fetchone():
                raise ValueError(f"股票 {symbol} 已在 {list_type} 列表中")

            # 插入新记录
            insert_sql = """
                INSERT INTO watchlist (user_id, symbol, list_type, note, added_at)
                VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
                RETURNING id, user_id, symbol, list_type, note, added_at
            """
            cursor.execute(insert_sql, (user_id, symbol, list_type, note))
            row = cursor.fetchone()

            conn.commit()
            cursor.close()
            self.pg_access._return_connection(conn)

            result = {
                "id": row[0],
                "user_id": row[1],
                "symbol": row[2],
                "list_type": row[3],
                "note": row[4],
                "added_at": row[5].strftime("%Y-%m-%d %H:%M:%S"),
            }

            logger.info("添加自选股成功: user_id=%s, symbol=%s, list_type=%s", user_id, symbol, list_type)
            return result

        except ValueError:
            raise
        except Exception as e:
            conn.rollback()
            logger.error("添加自选股失败: %s", e)
            raise

    def remove_from_watchlist(self, user_id: int, symbol: str, list_type: Optional[str] = None) -> bool:
        """
        从自选列表移除股票

        list_type为None时删除所有类型的记录
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            if list_type:
                sql = """
                    DELETE FROM watchlist
                    WHERE user_id = %s AND symbol = %s AND list_type = %s
                """
                cursor.execute(sql, (user_id, symbol, list_type))
            else:
                sql = """
                    DELETE FROM watchlist
                    WHERE user_id = %s AND symbol = %s
                """
                cursor.execute(sql, (user_id, symbol))

            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("删除自选股成功: user_id=%s, symbol=%s, deleted=%s", user_id, symbol, deleted_count)
            return deleted_count > 0

        except Exception as e:
            conn.rollback()
            logger.error("删除自选股失败: %s", e)
            raise

    def update_watchlist_note(self, user_id: int, symbol: str, list_type: str, note: str) -> bool:
        """
        更新自选股备注
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            sql = """
                UPDATE watchlist
                SET note = %s
                WHERE user_id = %s AND symbol = %s AND list_type = %s
            """
            cursor.execute(sql, (note, user_id, symbol, list_type))

            updated_count = cursor.rowcount
            conn.commit()
            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("更新自选股备注成功: user_id=%s, symbol=%s", user_id, symbol)
            return updated_count > 0

        except Exception as e:
            conn.rollback()
            logger.error("更新自选股备注失败: %s", e)
            raise

    # ==================== 策略配置管理 ====================

    def get_strategy_configs(
        self,
        user_id: int,
        strategy_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取策略配置列表

        支持按策略类型和状态过滤
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            # 构建动态WHERE子句
            where_clauses = ["user_id = %s"]
            params = [user_id]

            if strategy_type:
                where_clauses.append("strategy_type = %s")
                params.append(strategy_type)

            if status:
                where_clauses.append("status = %s")
                params.append(status)

            where_sql = " AND ".join(where_clauses)

            sql = f"""
                SELECT id, user_id, name, strategy_type, status,
                       parameters, description, created_at, updated_at
                FROM strategy_configs
                WHERE {where_sql}
                ORDER BY updated_at DESC
            """

            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(
                    {
                        "id": row[0],
                        "user_id": row[1],
                        "name": row[2],
                        "strategy_type": row[3],
                        "status": row[4],
                        "parameters": row[5],  # JSONB字段自动转换为dict
                        "description": row[6],
                        "created_at": row[7].strftime("%Y-%m-%d %H:%M:%S") if row[7] else None,
                        "updated_at": row[8].strftime("%Y-%m-%d %H:%M:%S") if row[8] else None,
                    }
                )

            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("获取策略配置成功: user_id=%s, count=%s", user_id, len(result))
            return result

        except Exception as e:
            logger.error("获取策略配置失败: %s", e)
            raise

    def save_strategy_config(
        self,
        user_id: int,
        name: str,
        strategy_type: str,
        parameters: Dict[str, Any],
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        保存策略配置

        使用JSONB字段存储策略参数
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            # 检查策略名称是否已存在
            check_sql = """
                SELECT id FROM strategy_configs
                WHERE user_id = %s AND name = %s
            """
            cursor.execute(check_sql, (user_id, name))
            if cursor.fetchone():
                raise ValueError(f"策略名称 '{name}' 已存在")

            # 插入新策略
            import json

            insert_sql = """
                INSERT INTO strategy_configs
                (user_id, name, strategy_type, status, parameters, description,
                 created_at, updated_at)
                VALUES (%s, %s, %s, 'inactive', %s::jsonb, %s,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id, user_id, name, strategy_type, status,
                          parameters, description, created_at, updated_at
            """
            cursor.execute(
                insert_sql,
                (user_id, name, strategy_type, json.dumps(parameters), description),
            )
            row = cursor.fetchone()

            conn.commit()
            cursor.close()
            self.pg_access._return_connection(conn)

            result = {
                "id": row[0],
                "user_id": row[1],
                "name": row[2],
                "strategy_type": row[3],
                "status": row[4],
                "parameters": row[5],
                "description": row[6],
                "created_at": row[7].strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": row[8].strftime("%Y-%m-%d %H:%M:%S"),
            }

            logger.info("保存策略配置成功: user_id=%s, name=%s", user_id, name)
            return result

        except ValueError:
            raise
        except Exception as e:
            conn.rollback()
            logger.error("保存策略配置失败: %s", e)
            raise

    def update_strategy_status(self, strategy_id: int, user_id: int, status: str) -> bool:
        """
        更新策略状态

        包含权限验证（user_id）
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            # 验证权限
            check_sql = """
                SELECT id FROM strategy_configs
                WHERE id = %s AND user_id = %s
            """
            cursor.execute(check_sql, (strategy_id, user_id))
            if not cursor.fetchone():
                raise PermissionError(f"用户 {user_id} 无权限修改策略 {strategy_id}")

            # 更新状态
            update_sql = """
                UPDATE strategy_configs
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            cursor.execute(update_sql, (status, strategy_id))

            updated_count = cursor.rowcount
            conn.commit()
            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("更新策略状态成功: strategy_id=%s, status=%s", strategy_id, status)
            return updated_count > 0

        except PermissionError:
            raise
        except Exception as e:
            conn.rollback()
            logger.error("更新策略状态失败: %s", e)
            raise

    def delete_strategy_config(self, strategy_id: int, user_id: int) -> bool:
        """
        删除策略配置

        包含权限验证（user_id）
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            # 验证权限并删除
            sql = """
                DELETE FROM strategy_configs
                WHERE id = %s AND user_id = %s
            """
            cursor.execute(sql, (strategy_id, user_id))

            deleted_count = cursor.rowcount
            if deleted_count == 0:
                raise PermissionError(f"用户 {user_id} 无权限删除策略 {strategy_id}")

            conn.commit()
            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("删除策略配置成功: strategy_id=%s", strategy_id)
            return True

        except PermissionError:
            raise
        except Exception as e:
            conn.rollback()
            logger.error("删除策略配置失败: %s", e)
            raise

    # ==================== 风险管理配置 ====================

    def get_risk_alerts(
        self,
        user_id: int,
        symbol: Optional[str] = None,
        alert_type: Optional[str] = None,
        enabled_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        获取风险预警配置

        支持多条件过滤
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            # 构建动态WHERE子句
            where_clauses = ["user_id = %s"]
            params = [user_id]

            if symbol:
                where_clauses.append("symbol = %s")
                params.append(symbol)

            if alert_type:
                where_clauses.append("alert_type = %s")
                params.append(alert_type)

            if enabled_only:
                where_clauses.append("enabled = TRUE")

            where_sql = " AND ".join(where_clauses)

            sql = f"""
                SELECT id, user_id, symbol, alert_type, condition, threshold,
                       notification_methods, enabled, triggered_count,
                       last_triggered, created_at, updated_at
                FROM risk_alerts
                WHERE {where_sql}
                ORDER BY created_at DESC
            """

            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(
                    {
                        "id": row[0],
                        "user_id": row[1],
                        "symbol": row[2],
                        "alert_type": row[3],
                        "condition": row[4],
                        "threshold": float(row[5]),
                        "notification_methods": row[6],  # JSONB自动转换
                        "enabled": row[7],
                        "triggered_count": row[8],
                        "last_triggered": row[9].strftime("%Y-%m-%d %H:%M:%S") if row[9] else None,
                        "created_at": row[10].strftime("%Y-%m-%d %H:%M:%S") if row[10] else None,
                        "updated_at": row[11].strftime("%Y-%m-%d %H:%M:%S") if row[11] else None,
                    }
                )

            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("获取风险预警成功: user_id=%s, count=%s", user_id, len(result))
            return result

        except Exception as e:
            logger.error("获取风险预警失败: %s", e)
            raise

    def save_risk_alert(
        self,
        user_id: int,
        symbol: str,
        alert_type: str,
        condition: str,
        threshold: float,
        notification_methods: List[str],
        enabled: bool = True,
    ) -> Dict[str, Any]:
        """
        保存风险预警配置

        使用JSONB存储通知方式数组
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            import json

            insert_sql = """
                INSERT INTO risk_alerts
                (user_id, symbol, alert_type, condition, threshold,
                 notification_methods, enabled, triggered_count,
                 created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, 0,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                RETURNING id, user_id, symbol, alert_type, condition, threshold,
                          notification_methods, enabled, created_at
            """
            cursor.execute(
                insert_sql,
                (
                    user_id,
                    symbol,
                    alert_type,
                    condition,
                    threshold,
                    json.dumps(notification_methods),
                    enabled,
                ),
            )
            row = cursor.fetchone()

            conn.commit()
            cursor.close()
            self.pg_access._return_connection(conn)

            result = {
                "id": row[0],
                "user_id": row[1],
                "symbol": row[2],
                "alert_type": row[3],
                "condition": row[4],
                "threshold": float(row[5]),
                "notification_methods": row[6],
                "enabled": row[7],
                "created_at": row[8].strftime("%Y-%m-%d %H:%M:%S"),
            }

            logger.info("保存风险预警成功: user_id=%s, symbol=%s", user_id, symbol)
            return result

        except Exception as e:
            conn.rollback()
            logger.error("保存风险预警失败: %s", e)
            raise

    def toggle_risk_alert(self, alert_id: int, user_id: int, enabled: bool) -> bool:
        """
        启用/禁用风险预警

        包含权限验证
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            # 验证权限并更新
            sql = """
                UPDATE risk_alerts
                SET enabled = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s AND user_id = %s
            """
            cursor.execute(sql, (enabled, alert_id, user_id))

            updated_count = cursor.rowcount
            if updated_count == 0:
                raise PermissionError(f"用户 {user_id} 无权限修改预警 {alert_id}")

            conn.commit()
            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("切换风险预警成功: alert_id=%s, enabled=%s", alert_id, enabled)
            return True

        except PermissionError:
            raise
        except Exception as e:
            conn.rollback()
            logger.error("切换风险预警失败: %s", e)
            raise

    # ==================== 用户配置管理 ====================

    def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户偏好设置

        JSONB字段自动反序列化为dict
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            sql = """
                SELECT user_id, display_settings, notification_settings,
                       trading_settings, updated_at
                FROM user_preferences
                WHERE user_id = %s
            """
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()

            if not row:
                # 返回默认设置
                return {
                    "user_id": user_id,
                    "display_settings": {},
                    "notification_settings": {},
                    "trading_settings": {},
                    "updated_at": None,
                }

            result = {
                "user_id": row[0],
                "display_settings": row[1] or {},
                "notification_settings": row[2] or {},
                "trading_settings": row[3] or {},
                "updated_at": row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else None,
            }

            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("获取用户偏好成功: user_id=%s", user_id)
            return result

        except Exception as e:
            logger.error("获取用户偏好失败: %s", e)
            raise

    def update_user_preferences(self, user_id: int, preferences: Dict[str, Any]) -> bool:
        """
        更新用户偏好设置

        支持部分更新（使用JSONB的||运算符合并）
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            import json

            # 构建UPDATE SET子句（部分更新）
            set_clauses = []
            params = []

            if "display_settings" in preferences:
                set_clauses.append("display_settings = display_settings || %s::jsonb")
                params.append(json.dumps(preferences["display_settings"]))

            if "notification_settings" in preferences:
                set_clauses.append("notification_settings = notification_settings || %s::jsonb")
                params.append(json.dumps(preferences["notification_settings"]))

            if "trading_settings" in preferences:
                set_clauses.append("trading_settings = trading_settings || %s::jsonb")
                params.append(json.dumps(preferences["trading_settings"]))

            if not set_clauses:
                return False

            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            set_sql = ", ".join(set_clauses)
            params.append(user_id)

            # UPSERT操作
            sql = f"""
                INSERT INTO user_preferences (user_id, display_settings, notification_settings, trading_settings, updated_at)
                VALUES (%s, '{{}}'::jsonb, '{{}}'::jsonb, '{{}}'::jsonb, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE SET {set_sql}
            """

            # 对于INSERT，需要在params前面加上user_id
            insert_params = [user_id] + params
            cursor.execute(sql, tuple(insert_params))

            conn.commit()
            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("更新用户偏好成功: user_id=%s", user_id)
            return True

        except Exception as e:
            conn.rollback()
            logger.error("更新用户偏好失败: %s", e)
            raise

    # ==================== 股票基础信息 ====================

    def get_stock_basic_info(
        self,
        symbols: Optional[List[str]] = None,
        market: Optional[str] = None,
        industry: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        获取股票基础信息

        支持批量查询和多条件过滤
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            # 构建动态WHERE子句
            where_clauses = ["status = 'active'"]
            params = []

            if symbols:
                placeholders = ", ".join(["%s"] * len(symbols))
                where_clauses.append(f"symbol IN ({placeholders})")
                params.extend(symbols)

            if market:
                where_clauses.append("market = %s")
                params.append(market)

            if industry:
                where_clauses.append("industry = %s")
                params.append(industry)

            where_sql = " AND ".join(where_clauses)

            sql = f"""
                SELECT symbol, name, pinyin, market, industry, sector,
                       list_date, total_shares, float_shares, status, updated_at
                FROM stock_basic_info
                WHERE {where_sql}
                ORDER BY symbol
            """

            cursor.execute(sql, tuple(params))
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(
                    {
                        "symbol": row[0],
                        "name": row[1],
                        "pinyin": row[2],
                        "market": row[3],
                        "industry": row[4],
                        "sector": row[5],
                        "list_date": row[6].strftime("%Y-%m-%d") if row[6] else None,
                        "total_shares": row[7],
                        "float_shares": row[8],
                        "status": row[9],
                        "updated_at": row[10].strftime("%Y-%m-%d %H:%M:%S") if row[10] else None,
                    }
                )

            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("获取股票基础信息成功: count=%s", len(result))
            return result

        except Exception as e:
            logger.error("获取股票基础信息失败: %s", e)
            raise

    def search_stocks(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        搜索股票

        使用pg_trgm扩展支持模糊搜索和拼音搜索
        优先级: 代码匹配 > 名称匹配 > 拼音匹配
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            keyword_pattern = f"%{keyword}%"

            sql = """
                SELECT symbol, name, pinyin, market,
                       CASE
                           WHEN symbol LIKE %s THEN 'code'
                           WHEN name LIKE %s THEN 'name'
                           ELSE 'pinyin'
                       END as match_type
                FROM stock_basic_info
                WHERE (symbol LIKE %s OR name LIKE %s OR pinyin LIKE %s)
                  AND status = 'active'
                ORDER BY
                    CASE
                        WHEN symbol LIKE %s THEN 1
                        WHEN name LIKE %s THEN 2
                        ELSE 3
                    END,
                    symbol
                LIMIT %s
            """

            cursor.execute(
                sql,
                (
                    keyword_pattern,
                    keyword_pattern,  # CASE条件
                    keyword_pattern,
                    keyword_pattern,
                    keyword_pattern,  # WHERE条件
                    keyword_pattern,
                    keyword_pattern,  # ORDER BY条件
                    limit,
                ),
            )
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(
                    {
                        "symbol": row[0],
                        "name": row[1],
                        "pinyin": row[2],
                        "market": row[3],
                        "match_type": row[4],
                    }
                )

            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("搜索股票成功: keyword=%s, count=%s", keyword, len(result))
            return result

        except Exception as e:
            logger.error("搜索股票失败: %s", e)
            raise

    # ==================== 行业概念板块 ====================

    def get_industry_list(self, classification: str = "sw") -> List[Dict[str, Any]]:
        """
        获取行业分类列表

        支持申万、证监会、中金等分类标准
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            sql = """
                SELECT code, name, classification, level, parent_code, stock_count, updated_at
                FROM industry_classification
                WHERE classification = %s
                ORDER BY level, code
            """

            cursor.execute(sql, (classification,))
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(
                    {
                        "code": row[0],
                        "name": row[1],
                        "classification": row[2],
                        "level": row[3],
                        "parent_code": row[4],
                        "stock_count": row[5],
                        "updated_at": row[6].strftime("%Y-%m-%d %H:%M:%S") if row[6] else None,
                    }
                )

            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("获取行业列表成功: classification=%s, count=%s", classification, len(result))
            return result

        except Exception as e:
            logger.error("获取行业列表失败: %s", e)
            raise

    def get_concept_list(self) -> List[Dict[str, Any]]:
        """
        获取概念板块列表
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            sql = """
                SELECT code, name, stock_count, description, updated_at
                FROM concept_classification
                ORDER BY stock_count DESC, code
            """

            cursor.execute(sql)
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(
                    {
                        "code": row[0],
                        "name": row[1],
                        "stock_count": row[2],
                        "description": row[3],
                        "updated_at": row[4].strftime("%Y-%m-%d") if row[4] else None,
                    }
                )

            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("获取概念列表成功: count=%s", len(result))
            return result

        except Exception as e:
            logger.error("获取概念列表失败: %s", e)
            raise

    def get_stocks_by_industry(self, industry_code: str) -> List[str]:
        """
        获取行业成分股

        通过stock_industry_mapping关联查询
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            sql = """
                SELECT DISTINCT sim.symbol
                FROM stock_industry_mapping sim
                JOIN stock_basic_info s ON sim.symbol = s.symbol
                WHERE sim.industry_code = %s AND s.status = 'active'
                ORDER BY sim.symbol
            """

            cursor.execute(sql, (industry_code,))
            rows = cursor.fetchall()

            result = [row[0] for row in rows]

            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("获取行业成分股成功: industry_code=%s, count=%s", industry_code, len(result))
            return result

        except Exception as e:
            logger.error("获取行业成分股失败: %s", e)
            raise

    def get_stocks_by_concept(self, concept_code: str) -> List[str]:
        """
        获取概念成分股

        通过stock_concept_mapping关联查询
        """
        try:
            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            sql = """
                SELECT DISTINCT scm.symbol
                FROM stock_concept_mapping scm
                JOIN stock_basic_info s ON scm.symbol = s.symbol
                WHERE scm.concept_code = %s AND s.status = 'active'
                ORDER BY scm.symbol
            """

            cursor.execute(sql, (concept_code,))
            rows = cursor.fetchall()

            result = [row[0] for row in rows]

            cursor.close()
            self.pg_access._return_connection(conn)

            logger.info("获取概念成分股成功: concept_code=%s, count=%s", concept_code, len(result))
            return result

        except Exception as e:
            logger.error("获取概念成分股失败: %s", e)
            raise

    # ==================== 数据库操作辅助 ====================

    def begin_transaction(self) -> Any:
        """
        开始事务

        返回数据库连接对象用于事务控制
        """
        try:
            conn = self.pg_access._get_connection()
            conn.autocommit = False
            logger.info("开始事务")
            return conn
        except Exception as e:
            logger.error("开始事务失败: %s", e)
            raise

    def commit_transaction(self, transaction: Any) -> None:
        """
        提交事务
        """
        try:
            transaction.commit()
            transaction.autocommit = True
            self.pg_access._return_connection(transaction)
            logger.info("提交事务成功")
        except Exception as e:
            logger.error("提交事务失败: %s", e)
            raise

    def rollback_transaction(self, transaction: Any) -> None:
        """
        回滚事务
        """
        try:
            transaction.rollback()
            transaction.autocommit = True
            self.pg_access._return_connection(transaction)
            logger.info("回滚事务成功")
        except Exception as e:
            logger.error("回滚事务失败: %s", e)
            raise

    def health_check(self) -> Dict[str, Any]:
        """
        PostgreSQL关系数据源健康检查

        返回连接状态、连接池信息、性能指标
        """
        try:
            start_time = datetime.now()

            conn = self.pg_access._get_connection()
            cursor = conn.cursor()

            # 查询数据库版本
            cursor.execute("SELECT version()")
            version = cursor.fetchone()[0]

            # 查询连接池状态（如果可用）
            # 这里简化处理，实际应该从连接池获取
            pool_info = {
                "size": self._connection_pool_size,
                "in_use": 1,  # 当前这个连接
                "available": self._connection_pool_size - 1,
            }

            elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000

            cursor.close()
            self.pg_access._return_connection(conn)

            return {
                "status": "healthy",
                "data_source_type": "postgresql",
                "version": version.split()[1] if " " in version else version,
                "response_time_ms": round(elapsed_ms, 2),
                "connection_pool": pool_info,
                "last_query": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "metrics": {
                    "total_queries_today": 0,  # 需要从监控系统获取
                    "avg_response_time_ms": 0,
                    "slow_queries_count": 0,
                },
            }

        except Exception as e:
            logger.error("健康检查失败: %s", e)
            return {
                "status": "unhealthy",
                "data_source_type": "postgresql",
                "error": str(e),
            }
