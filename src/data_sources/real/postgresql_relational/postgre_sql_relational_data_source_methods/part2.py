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

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.data_access.postgresql_access import PostgreSQLDataAccess
from src.interfaces.relational_data_source import IRelationalDataSource

logger = logging.getLogger(__name__)


class PostgreSQLRelationalDataSourceGetStockBasicMixin:
    """PostgreSQLRelationalDataSource 方法集 Part 2"""

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

