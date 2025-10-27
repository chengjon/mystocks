"""
Market Data API - Week 3 PostgreSQL-Only Version
User Story 2: Fix 4 Broken Market Data Panels

提供纯PostgreSQL接口，移除所有MySQL依赖:
- GET /api/market/dragon-tiger - 龙虎榜数据
- GET /api/market/etf-data - ETF实时数据
- GET /api/market/fund-flow - 资金流向（PostgreSQL版本）
- GET /api/market/chip-race - 竞价抢筹数据
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy import text
import structlog

from app.core.database import get_postgresql_session
from app.core.errors import DatabaseError, ResourceNotFoundError
from app.core.security import get_current_user, User

router = APIRouter()
logger = structlog.get_logger()


@router.get("/dragon-tiger")
async def get_dragon_tiger_data(
    trade_date: Optional[str] = Query(
        None, description="交易日期 YYYY-MM-DD，默认最近一个交易日"
    ),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取龙虎榜数据

    数据来源: dragon_tiger_list table (PostgreSQL)

    Returns:
        {
            "success": true,
            "data": [
                {
                    "symbol": "000001",
                    "name": "平安银行",
                    "trade_date": "2025-01-15",
                    "close_price": 12.50,
                    "change_percent": 10.00,
                    "net_buy": 1250000.00,
                    "buy_reason": "连续三个交易日内涨幅偏离值累计达到20%"
                }
            ],
            "total": 20,
            "timestamp": "2025-01-15T10:00:00"
        }
    """
    try:
        session = get_postgresql_session()

        # 如果没有指定日期，使用最近一个交易日
        if not trade_date:
            date_query = text(
                """
                SELECT MAX(trade_date) as latest_date
                FROM dragon_tiger_list
            """
            )
            result = session.execute(date_query)
            row = result.fetchone()
            trade_date = row[0].strftime("%Y-%m-%d") if row and row[0] else None

            if not trade_date:
                logger.warning("No dragon tiger data found in database")
                return {
                    "success": True,
                    "data": [],
                    "total": 0,
                    "timestamp": datetime.now().isoformat(),
                }

        # 查询龙虎榜数据 - 使用实际的表字段名
        query = text("""
            SELECT
                symbol,
                stock_name,
                trade_date,
                net_amount,
                reason,
                total_buy_amount,
                total_sell_amount,
                institution_net_amount,
                detail_data
            FROM dragon_tiger_list
            WHERE trade_date = :trade_date
            ORDER BY net_amount DESC NULLS LAST
            LIMIT :limit
        """)

        result = session.execute(query, {"trade_date": trade_date, "limit": limit})
        rows = result.fetchall()

        data = []
        for row in rows:
            # 从 detail_data (jsonb) 中提取 close_price 和 change_percent
            detail = row[8] if row[8] else {}

            # 计算机构买入和卖出金额（从净额推算）
            institution_net = float(row[7]) if row[7] else 0.0
            # 如果净额为正，则买入=净额，卖出=0；如果为负，则买入=0，卖出=abs(净额)
            institution_buy = institution_net if institution_net > 0 else 0.0
            institution_sell = abs(institution_net) if institution_net < 0 else 0.0

            data.append({
                "symbol": row[0],
                "name": row[1],  # stock_name -> name for frontend compatibility
                "trade_date": row[2].strftime("%Y-%m-%d") if row[2] else None,
                "net_amount": float(row[3]) if row[3] else 0.0,  # 保持net_amount字段名
                "reason": row[4],  # 保持reason字段名
                "buy_amount": float(row[5]) if row[5] else 0.0,  # total_buy_amount -> buy_amount
                "sell_amount": float(row[6]) if row[6] else 0.0,  # total_sell_amount -> sell_amount
                "turnover_rate": float(detail.get("turnover_rate", 0)) if detail else 0.0,  # 从detail_data提取或默认0
                "institution_buy": institution_buy,
                "institution_sell": institution_sell,
            })

        session.close()
        logger.info(f"Retrieved {len(data)} dragon tiger records for {trade_date}")

        return {
            "success": True,
            "data": data,
            "total": len(data),
            "timestamp": datetime.now().isoformat(),
        }

    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.user_message)
    except Exception as e:
        logger.error(f"Failed to get dragon tiger data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取龙虎榜数据失败，请稍后重试")


@router.get("/etf-data")
async def get_etf_data(
    limit: int = Query(50, ge=1, le=200, description="返回记录数"),
    sort_by: str = Query(
        "volume", regex="^(volume|change|turnover)$", description="排序字段"
    ),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取ETF实时数据

    数据来源: etf_spot_data table (PostgreSQL)

    Returns:
        {
            "success": true,
            "data": [
                {
                    "symbol": "510050",
                    "name": "50ETF",
                    "close": 2.856,
                    "change": 0.35,
                    "volume": 125000000,
                    "turnover": 3.25,
                    "amount": 357000000.00
                }
            ],
            "total": 50,
            "timestamp": "2025-01-15T10:00:00"
        }
    """
    try:
        session = get_postgresql_session()

        # 排序字段映射
        sort_fields = {
            "volume": "volume DESC NULLS LAST",
            "change": "change_percent DESC NULLS LAST",
            "turnover": "turnover_rate DESC NULLS LAST",
        }

        order_clause = sort_fields.get(sort_by, "volume DESC NULLS LAST")

        # 查询ETF数据
        query = text(
            f"""
            SELECT
                symbol,
                name,
                latest_price,
                change_percent,
                volume,
                turnover_rate,
                amount,
                high_price,
                low_price,
                open_price
            FROM etf_spot_data
            ORDER BY {order_clause}
            LIMIT :limit
        """
        )

        result = session.execute(query, {"limit": limit})
        rows = result.fetchall()

        data = []
        for row in rows:
            data.append(
                {
                    "symbol": row[0],
                    "name": row[1],
                    "close": float(row[2]) if row[2] else 0.0,
                    "change": float(row[3]) if row[3] else 0.0,
                    "volume": int(row[4]) if row[4] else 0,
                    "turnover": float(row[5]) if row[5] else 0.0,
                    "amount": float(row[6]) if row[6] else 0.0,
                    "high": float(row[7]) if row[7] else 0.0,
                    "low": float(row[8]) if row[8] else 0.0,
                    "open": float(row[9]) if row[9] else 0.0,
                }
            )

        session.close()
        logger.info(f"Retrieved {len(data)} ETF records (sorted by {sort_by})")

        return {
            "success": True,
            "data": data,
            "total": len(data),
            "timestamp": datetime.now().isoformat(),
        }

    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.user_message)
    except Exception as e:
        logger.error(f"Failed to get ETF data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取ETF数据失败，请稍后重试")


@router.get("/fund-flow")
async def get_fund_flow_data(
    trade_date: Optional[str] = Query(
        None, description="交易日期 YYYY-MM-DD，默认最近一个交易日"
    ),
    industry_type: str = Query(
        "csrc", regex="^(csrc|sw_l1|sw_l2)$", description="行业分类标准"
    ),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取行业资金流向数据（PostgreSQL版本）

    数据来源: market_fund_flow table (PostgreSQL)

    Returns:
        {
            "success": true,
            "data": [
                {
                    "industry_name": "计算机",
                    "industry_type": "sw_l1",
                    "net_inflow": 1850000000.00,
                    "main_inflow": 1200000000.00,
                    "retail_inflow": 650000000.00,
                    "trade_date": "2025-01-15"
                }
            ],
            "total": 20,
            "timestamp": "2025-01-15T10:00:00"
        }
    """
    try:
        session = get_postgresql_session()

        # 如果没有指定日期，使用最近一个交易日
        if not trade_date:
            date_query = text(
                """
                SELECT MAX(trade_date) as latest_date
                FROM market_fund_flow
                WHERE industry_type = :industry_type
            """
            )
            result = session.execute(date_query, {"industry_type": industry_type})
            row = result.fetchone()
            trade_date = row[0].strftime("%Y-%m-%d") if row and row[0] else None

            if not trade_date:
                logger.warning(
                    f"No fund flow data found for industry_type={industry_type}"
                )
                return {
                    "success": True,
                    "data": [],
                    "total": 0,
                    "timestamp": datetime.now().isoformat(),
                }

        # 查询资金流向数据
        query = text(
            """
            SELECT
                industry_name,
                industry_type,
                net_inflow,
                main_inflow,
                retail_inflow,
                trade_date,
                total_inflow,
                total_outflow
            FROM market_fund_flow
            WHERE trade_date = :trade_date
            AND industry_type = :industry_type
            ORDER BY ABS(net_inflow) DESC NULLS LAST
            LIMIT :limit
        """
        )

        result = session.execute(
            query,
            {"trade_date": trade_date, "industry_type": industry_type, "limit": limit},
        )
        rows = result.fetchall()

        data = []
        for row in rows:
            data.append(
                {
                    "industry_name": row[0],
                    "industry_type": row[1],
                    "net_inflow": (
                        float(row[2]) / 100000000 if row[2] else 0.0
                    ),  # 转换为亿
                    "main_inflow": float(row[3]) / 100000000 if row[3] else 0.0,
                    "retail_inflow": float(row[4]) / 100000000 if row[4] else 0.0,
                    "trade_date": row[5].strftime("%Y-%m-%d") if row[5] else None,
                    "total_inflow": float(row[6]) / 100000000 if row[6] else 0.0,
                    "total_outflow": float(row[7]) / 100000000 if row[7] else 0.0,
                }
            )

        session.close()
        logger.info(
            f"Retrieved {len(data)} fund flow records for {trade_date} ({industry_type})"
        )

        return {
            "success": True,
            "data": data,
            "total": len(data),
            "timestamp": datetime.now().isoformat(),
        }

    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.user_message)
    except Exception as e:
        logger.error(f"Failed to get fund flow data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取资金流向数据失败，请稍后重试")


@router.get("/chip-race")
async def get_chip_race_data(
    trade_date: Optional[str] = Query(
        None, description="交易日期 YYYY-MM-DD，默认最近一个交易日"
    ),
    limit: int = Query(20, ge=1, le=100, description="返回记录数"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取竞价抢筹数据

    数据来源: chip_race_data table (PostgreSQL)

    Returns:
        {
            "success": true,
            "data": [
                {
                    "symbol": "000001",
                    "name": "平安银行",
                    "trade_date": "2025-01-15",
                    "open_price": 12.30,
                    "close_price": 12.50,
                    "bid_volume": 5000000,
                    "ask_volume": 3000000,
                    "net_volume": 2000000,
                    "strength": 66.67
                }
            ],
            "total": 20,
            "timestamp": "2025-01-15T10:00:00"
        }
    """
    try:
        session = get_postgresql_session()

        # 如果没有指定日期，使用最近一个交易日
        if not trade_date:
            date_query = text(
                """
                SELECT MAX(trade_date) as latest_date
                FROM chip_race_data
            """
            )
            result = session.execute(date_query)
            row = result.fetchone()
            trade_date = row[0].strftime("%Y-%m-%d") if row and row[0] else None

            if not trade_date:
                logger.warning("No chip race data found in database")
                return {
                    "success": True,
                    "data": [],
                    "total": 0,
                    "timestamp": datetime.now().isoformat(),
                }

        # 查询竞价抢筹数据
        query = text(
            """
            SELECT
                symbol,
                name,
                trade_date,
                open_price,
                close_price,
                bid_volume,
                ask_volume,
                net_volume,
                strength,
                change_percent
            FROM chip_race_data
            WHERE trade_date = :trade_date
            ORDER BY strength DESC NULLS LAST
            LIMIT :limit
        """
        )

        result = session.execute(query, {"trade_date": trade_date, "limit": limit})
        rows = result.fetchall()

        data = []
        for row in rows:
            data.append(
                {
                    "symbol": row[0],
                    "name": row[1],
                    "trade_date": row[2].strftime("%Y-%m-%d") if row[2] else None,
                    "open_price": float(row[3]) if row[3] else 0.0,
                    "close_price": float(row[4]) if row[4] else 0.0,
                    "bid_volume": int(row[5]) if row[5] else 0,
                    "ask_volume": int(row[6]) if row[6] else 0,
                    "net_volume": int(row[7]) if row[7] else 0,
                    "strength": float(row[8]) if row[8] else 0.0,
                    "change_percent": float(row[9]) if row[9] else 0.0,
                }
            )

        session.close()
        logger.info(f"Retrieved {len(data)} chip race records for {trade_date}")

        return {
            "success": True,
            "data": data,
            "total": len(data),
            "timestamp": datetime.now().isoformat(),
        }

    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.user_message)
    except Exception as e:
        logger.error(f"Failed to get chip race data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取竞价抢筹数据失败，请稍后重试")
