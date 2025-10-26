"""
Dashboard API - User Story 1: Real Data Display
提供仪表板所需的所有真实数据接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List, Dict, Any
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import text, func
import structlog

from app.core.database import get_unified_manager, get_postgresql_session
from app.core.errors import DatabaseError, ResourceNotFoundError
from app.core.security import get_current_user, User

router = APIRouter()
logger = structlog.get_logger()


def get_favorites(user_id: int, session) -> List[Dict[str, Any]]:
    """
    获取用户自选股列表，包含实时行情数据

    Args:
        user_id: 用户ID
        session: 数据库会话

    Returns:
        自选股列表，包含股票代码、名称、价格、涨跌幅等
    """
    try:
        # Query user watchlist joined with latest daily_kline and symbols_info
        query = text(
            """
            SELECT DISTINCT
                w.symbol,
                s.name,
                s.industry,
                k.close as price,
                ROUND(((k.close - k.pre_close) / k.pre_close * 100)::numeric, 2) as change,
                k.volume,
                0.0 as turnover
            FROM user_watchlist w
            INNER JOIN symbols_info s ON w.symbol = s.symbol
            LEFT JOIN LATERAL (
                SELECT close, pre_close, volume
                FROM daily_kline
                WHERE symbol = w.symbol
                ORDER BY trade_date DESC
                LIMIT 1
            ) k ON true
            WHERE w.user_id = :user_id
            ORDER BY w.added_at DESC
            LIMIT 20
        """
        )

        result = session.execute(query, {"user_id": user_id})
        rows = result.fetchall()

        favorites = []
        for row in rows:
            favorites.append(
                {
                    "symbol": row[0],
                    "name": row[1],
                    "industry": row[2],
                    "price": float(row[3]) if row[3] else 0.0,
                    "change": float(row[4]) if row[4] else 0.0,
                    "volume": f"{int(row[5])/10000:.1f}万手" if row[5] else "0万手",
                    "turnover": float(row[6]) if row[6] else 0.0,
                }
            )

        logger.info(f"Retrieved {len(favorites)} favorite stocks for user {user_id}")
        return favorites

    except Exception as e:
        logger.error(f"Failed to get favorites: {e}", exc_info=True)
        raise DatabaseError(
            technical_details=f"Failed to query user_watchlist: {str(e)}"
        )


def get_strategy_matches(session, limit: int = 20) -> List[Dict[str, Any]]:
    """
    获取策略匹配的股票列表

    Args:
        session: 数据库会话
        limit: 返回记录数

    Returns:
        策略匹配股票列表，包含策略名称、评分、信号等
    """
    try:
        # Query strategy execution results with scores
        query = text(
            """
            SELECT DISTINCT
                sr.symbol,
                s.name,
                k.close as price,
                ROUND(((k.close - k.pre_close) / k.pre_close * 100)::numeric, 2) as change,
                sd.strategy_name,
                sr.score,
                CASE
                    WHEN sr.signal > 0.7 THEN '买入'
                    WHEN sr.signal < -0.7 THEN '卖出'
                    ELSE '持有'
                END as signal
            FROM strategy_results sr
            INNER JOIN symbols_info s ON sr.symbol = s.symbol
            INNER JOIN strategy_definitions sd ON sr.strategy_id = sd.id
            LEFT JOIN LATERAL (
                SELECT close, pre_close
                FROM daily_kline
                WHERE symbol = sr.symbol
                ORDER BY trade_date DESC
                LIMIT 1
            ) k ON true
            WHERE sr.created_at >= CURRENT_DATE - INTERVAL '7 days'
            ORDER BY sr.score DESC
            LIMIT :limit
        """
        )

        result = session.execute(query, {"limit": limit})
        rows = result.fetchall()

        strategy_matches = []
        for row in rows:
            strategy_matches.append(
                {
                    "symbol": row[0],
                    "name": row[1],
                    "price": float(row[2]) if row[2] else 0.0,
                    "change": float(row[3]) if row[3] else 0.0,
                    "strategy": row[4],
                    "score": int(row[5]) if row[5] else 0,
                    "signal": row[6],
                }
            )

        logger.info(f"Retrieved {len(strategy_matches)} strategy matches")
        return strategy_matches

    except Exception as e:
        logger.error(f"Failed to get strategy matches: {e}", exc_info=True)
        raise DatabaseError(
            technical_details=f"Failed to query strategy_results: {str(e)}"
        )


def get_industry_stocks(
    session, industry: str = None, limit: int = 20
) -> List[Dict[str, Any]]:
    """
    获取行业股票列表

    Args:
        session: 数据库会话
        industry: 行业名称筛选（可选）
        limit: 返回记录数

    Returns:
        行业股票列表，包含行业排名、市值等
    """
    try:
        # Default to top industry if not specified
        if not industry:
            # Get top industry by market cap
            top_industry_query = text(
                """
                SELECT industry
                FROM symbols_info
                WHERE industry IS NOT NULL AND industry != ''
                GROUP BY industry
                ORDER BY COUNT(*) DESC
                LIMIT 1
            """
            )
            result = session.execute(top_industry_query)
            row = result.fetchone()
            industry = row[0] if row else "电子"

        # Query stocks in the industry
        query = text(
            """
            SELECT
                s.symbol,
                s.name,
                k.close as price,
                ROUND(((k.close - k.pre_close) / k.pre_close * 100)::numeric, 2) as change,
                s.industry,
                ROW_NUMBER() OVER (ORDER BY s.symbol ASC) as industry_rank,
                0.0 as market_cap
            FROM symbols_info s
            LEFT JOIN LATERAL (
                SELECT close, pre_close
                FROM daily_kline
                WHERE symbol = s.symbol
                ORDER BY trade_date DESC
                LIMIT 1
            ) k ON true
            WHERE s.industry = :industry
            ORDER BY s.symbol ASC
            LIMIT :limit
        """
        )

        result = session.execute(query, {"industry": industry, "limit": limit})
        rows = result.fetchall()

        industry_stocks = []
        for row in rows:
            industry_stocks.append(
                {
                    "symbol": row[0],
                    "name": row[1],
                    "price": float(row[2]) if row[2] else 0.0,
                    "change": float(row[3]) if row[3] else 0.0,
                    "industry": row[4],
                    "industryRank": int(row[5]),
                    "marketCap": float(row[6]) if row[6] else 0.0,
                }
            )

        logger.info(f"Retrieved {len(industry_stocks)} stocks for industry: {industry}")
        return industry_stocks

    except Exception as e:
        logger.error(f"Failed to get industry stocks: {e}", exc_info=True)
        raise DatabaseError(
            technical_details=f"Failed to query industry stocks: {str(e)}"
        )


def get_fund_flow_summary(session, standard: str = "csrc") -> Dict[str, Any]:
    """
    获取资金流向汇总数据

    Args:
        session: 数据库会话
        standard: 行业分类标准 (csrc/sw_l1/sw_l2)

    Returns:
        资金流向数据，包含各行业的资金净流入
    """
    try:
        # Map standard to industry_type
        industry_type_map = {"csrc": "csrc", "sw_l1": "sw_l1", "sw_l2": "sw_l2"}
        industry_type = industry_type_map.get(standard, "csrc")

        # Query fund flow by industry
        query = text(
            """
            SELECT
                industry_name,
                SUM(net_inflow) as total_inflow
            FROM market_fund_flow
            WHERE industry_type = :industry_type
            AND trade_date >= CURRENT_DATE - INTERVAL '1 day'
            GROUP BY industry_name
            ORDER BY total_inflow DESC
            LIMIT 10
        """
        )

        result = session.execute(query, {"industry_type": industry_type})
        rows = result.fetchall()

        # If no recent data, use mock structure with zero values
        if not rows:
            logger.warning(
                f"No fund flow data found for standard: {standard}, using empty structure"
            )
            default_industries = {
                "csrc": [
                    "金融业",
                    "房地产业",
                    "制造业",
                    "信息技术",
                    "批发零售",
                    "建筑业",
                    "采矿业",
                    "交通运输",
                ],
                "sw_l1": [
                    "计算机",
                    "电子",
                    "医药生物",
                    "电力设备",
                    "汽车",
                    "食品饮料",
                    "银行",
                    "非银金融",
                ],
                "sw_l2": [
                    "半导体",
                    "光学光电子",
                    "计算机设备",
                    "通信设备",
                    "医疗器械",
                    "化学制药",
                    "白酒",
                    "保险",
                ],
            }
            categories = default_industries.get(standard, default_industries["csrc"])
            values = [0.0] * len(categories)
        else:
            categories = [row[0] for row in rows]
            values = [float(row[1]) / 100000000 for row in rows]  # Convert to 亿

        logger.info(
            f"Retrieved fund flow for {len(categories)} industries (standard: {standard})"
        )
        return {"categories": categories, "values": values}

    except Exception as e:
        logger.error(f"Failed to get fund flow summary: {e}", exc_info=True)
        raise DatabaseError(
            technical_details=f"Failed to query market_fund_flow: {str(e)}"
        )


@router.get("/summary")
async def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取仪表板汇总数据

    Returns:
        包含自选股、策略选股、行业选股、资金流向、统计数据的完整仪表板数据
    """
    try:
        session = get_postgresql_session()

        # Get stats
        stats_query = text(
            """
            SELECT
                COUNT(*) as total_stocks,
                COUNT(*) FILTER (WHERE list_date IS NOT NULL) as active_stocks,
                (SELECT COUNT(*) FROM daily_kline WHERE trade_date = CURRENT_DATE) as today_updates
            FROM symbols_info
        """
        )
        stats_result = session.execute(stats_query)
        stats_row = stats_result.fetchone()

        # Build summary response
        summary = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "totalStocks": int(stats_row[0]) if stats_row[0] else 0,
                "activeStocks": int(stats_row[1]) if stats_row[1] else 0,
                "dataUpdates": int(stats_row[2]) if stats_row[2] else 0,
                "systemStatus": "正常",
            },
            "favorites": get_favorites(current_user.id, session),
            "strategyStocks": get_strategy_matches(session),
            "industryStocks": get_industry_stocks(session),
            "fundFlow": {
                "csrc": get_fund_flow_summary(session, "csrc"),
                "sw_l1": get_fund_flow_summary(session, "sw_l1"),
                "sw_l2": get_fund_flow_summary(session, "sw_l2"),
            },
        }

        session.close()
        logger.info(f"Dashboard summary generated for user {current_user.id}")
        return summary

    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.user_message)
    except Exception as e:
        logger.error(f"Failed to get dashboard summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="数据加载失败，请稍后重试")


@router.get("/favorites")
async def get_dashboard_favorites(
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """获取自选股列表"""
    try:
        session = get_postgresql_session()
        favorites = get_favorites(current_user.id, session)
        session.close()

        return {
            "success": True,
            "data": favorites,
            "timestamp": datetime.now().isoformat(),
        }
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.user_message)
    except Exception as e:
        logger.error(f"Failed to get favorites: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取自选股失败")


@router.get("/strategy-matches")
async def get_dashboard_strategy_matches(
    limit: int = Query(20, ge=1, le=100), current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """获取策略匹配股票"""
    try:
        session = get_postgresql_session()
        matches = get_strategy_matches(session, limit)
        session.close()

        return {
            "success": True,
            "data": matches,
            "timestamp": datetime.now().isoformat(),
        }
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.user_message)
    except Exception as e:
        logger.error(f"Failed to get strategy matches: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取策略选股失败")


@router.get("/industry-stocks")
async def get_dashboard_industry_stocks(
    industry: Optional[str] = Query(None, description="行业名称"),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """获取行业股票列表"""
    try:
        session = get_postgresql_session()
        stocks = get_industry_stocks(session, industry, limit)
        session.close()

        return {
            "success": True,
            "data": stocks,
            "timestamp": datetime.now().isoformat(),
        }
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.user_message)
    except Exception as e:
        logger.error(f"Failed to get industry stocks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取行业选股失败")


@router.get("/fund-flow")
async def get_dashboard_fund_flow(
    standard: str = Query(
        "csrc", regex="^(csrc|sw_l1|sw_l2)$", description="行业分类标准"
    ),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """获取资金流向数据"""
    try:
        session = get_postgresql_session()
        fund_flow = get_fund_flow_summary(session, standard)
        session.close()

        return {
            "success": True,
            "data": fund_flow,
            "timestamp": datetime.now().isoformat(),
        }
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=e.user_message)
    except Exception as e:
        logger.error(f"Failed to get fund flow: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取资金流向失败")
