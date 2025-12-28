"""
真实数据库查询服务
实现与Mock数据一致的接口格式

作者: MyStocks项目组
创建日期: 2025-11-15
"""

from typing import List, Dict, Optional
import pandas as pd
from datetime import datetime
import logging

# 导入数据访问层
from src.data_access import PostgreSQLDataAccess

logger = logging.getLogger(__name__)

# 创建数据库访问实例
postgresql_access = PostgreSQLDataAccess()


def get_stock_list(params: Optional[Dict] = None) -> List[Dict]:
    """获取股票列表（支持按交易所筛选，支持分页）

    Args:
        params: Dict - 查询参数：
                exchange: Optional[str] - 交易所筛选（sh=上交所，sz=深交所）
                limit: int - 每页数量，默认20
                offset: int - 偏移量，默认0

    Returns:
        List[Dict]: 股票列表数据，与Mock数据格式一致：
                   - symbol: 股票代码
                   - name: 股票名称
                   - industry: 所属行业
                   - area: 地区
                   - market: 市场
                   - list_date: 上市日期
                   - total: 总数量（用于分页）
    """
    try:
        # 默认参数
        params = params or {}
        exchange = params.get("exchange")
        limit = params.get("limit", 20)
        offset = params.get("offset", 0)

        # 构建查询条件
        filters = {}
        if exchange:
            # 根据交易所筛选（需要与数据库中的字段对应）
            if exchange == "sh":
                filters["market"] = "上交所"
            elif exchange == "sz":
                filters["market"] = "深交所"

        # 查询股票基本信息表
        df = postgresql_access.query(table_name="symbols_info", filters=filters, limit=limit, offset=offset)

        # 获取总数量
        total_df = postgresql_access.query(table_name="symbols_info", filters=filters, columns=["COUNT(*) as total"])
        total_count = total_df.iloc[0]["total"] if not total_df.empty else 0

        # 转换为与Mock数据一致的格式
        result = []
        if not df.empty:
            for _, row in df.iterrows():
                result.append(
                    {
                        "symbol": row.get("symbol", ""),
                        "name": row.get("name", ""),
                        "industry": row.get("industry", ""),
                        "area": row.get("area", ""),
                        "market": row.get("market", ""),
                        "list_date": (
                            row.get("list_date", "").strftime("%Y-%m-%d") if pd.notna(row.get("list_date")) else ""
                        ),
                        "total": total_count,  # 用于分页的总数量
                    }
                )

        return result

    except Exception as e:
        logger.error("获取股票列表失败: %s", e)
        # 出错时返回空列表，保持接口一致性
        return []


def get_real_time_quote(code: str) -> Dict:
    """获取实时行情（必填参数：股票代码）

    Args:
        code: str - 股票代码（必填）

    Returns:
        Dict: 实时行情数据，与Mock数据格式一致
    """
    try:
        if not code:
            return {}

        # 查询实时行情表（假设表名为realtime_quotes）
        filters = {"symbol": code}
        df = postgresql_access.query(table_name="realtime_quotes", filters=filters, limit=1)

        # 转换为与Mock数据一致的格式
        if not df.empty:
            row = df.iloc[0]
            return {
                "symbol": row.get("symbol", ""),
                "name": row.get("name", ""),
                "price": float(row.get("price", 0.0)),
                "change": float(row.get("change", 0.0)),
                "change_percent": float(row.get("change_percent", 0.0)),
                "volume": int(row.get("volume", 0)),
                "amount": float(row.get("amount", 0.0)),
                "open": float(row.get("open", 0.0)),
                "high": float(row.get("high", 0.0)),
                "low": float(row.get("low", 0.0)),
                "pre_close": float(row.get("pre_close", 0.0)),
                "timestamp": (
                    row.get("timestamp", "").strftime("%Y-%m-%d %H:%M:%S") if pd.notna(row.get("timestamp")) else ""
                ),
            }

        return {}

    except Exception as e:
        logger.error("获取实时行情失败: %s", e)
        return {}


def get_history_profit(params: Optional[Dict] = None) -> pd.DataFrame:
    """获取历史收益（默认30天，返回DataFrame）

    Args:
        params: Dict - 查询参数：
                symbol: str - 股票代码（必填）
                days: int - 天数，默认30

    Returns:
        pd.DataFrame: 历史收益数据
    """
    try:
        # 默认参数
        params = params or {}
        symbol = params.get("symbol")
        days = params.get("days", 30)

        if not symbol:
            return pd.DataFrame()

        # 计算开始日期
        end_date = datetime.now()
        start_date = end_date - pd.Timedelta(days=days)

        # 查询日线数据表（假设表名为daily_kline）
        filters = {
            "symbol": symbol,
            "date >= ": start_date.strftime("%Y-%m-%d"),
            "date <= ": end_date.strftime("%Y-%m-%d"),
        }

        df = postgresql_access.query(table_name="daily_kline", filters=filters, order_by="date ASC")

        # 计算收益（假设已有收益字段或需要计算）
        if not df.empty:
            # 确保日期列是datetime类型
            df["date"] = pd.to_datetime(df["date"])
            # 按日期排序
            df = df.sort_values("date")

        return df

    except Exception as e:
        logger.error("获取历史收益失败: %s", e)
        return pd.DataFrame()
