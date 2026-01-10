"""
Watchlist & Portfolio Demo Script
自选股与组合管理演示脚本

演示自选股监控和组合管理的核心功能。
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

sys.path.insert(0, str(Path(__file__).parent.parent))


def demo_watchlist():
    """演示自选股功能"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.domain.watchlist.model import Watchlist
    from src.domain.watchlist.value_objects import WatchlistType
    from src.infrastructure.persistence.watchlist_repository_impl import (
        WatchlistRepositoryImpl,
        WatchlistStockRepositoryImpl,
    )
    from src.application.watchlist.watchlist_app_service import WatchlistApplicationService

    print("\n" + "=" * 70)
    print("自选股功能演示")
    print("=" * 70)

    engine = create_engine("sqlite:///./watchlist_demo.db", echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    watchlist_repo = WatchlistRepositoryImpl(session)
    stock_repo = WatchlistStockRepositoryImpl(session)
    watchlist_service = WatchlistApplicationService(watchlist_repo, stock_repo)

    try:
        wl = watchlist_service.create_watchlist(
            name="技术关注组合", watchlist_type="technical", description="用于技术分析的股票观察池", color_tag="#e74c3c"
        )
        print(f"\n创建自选股: {wl['name']}")
        print(f"  ID: {wl['id']}")
        print(f"  类型: {wl['type']}")

        stocks = [
            ("600519", "贵州茅台", ["白酒", "蓝筹"]),
            ("000001", "平安银行", ["银行", "金融"]),
            ("300750", "宁德时代", ["新能源", "锂电池"]),
        ]

        for code, name, tags in stocks:
            result = watchlist_service.add_stock(
                watchlist_id=wl["id"],
                stock_code=code,
                stock_name=name,
                tags=tags,
                capture_indicators=["sma.5", "sma.20", "rsi.14"],
                reference_days=20,
            )
            print(f"\n添加股票: {code} - {name}")
            print(f"  快照ID: {result.get('snapshot_id', 'N/A')}")

        summary = watchlist_service.get_watchlist_summary(wl["id"])
        print(f"\n自选股摘要:")
        print(f"  股票数量: {summary['stock_count']}")
        print(f"  上涨: {summary['up_count']} 只")
        print(f"  下跌: {summary['down_count']} 只")

        print("\n✅ 自选股演示完成")

    except Exception as e:
        logger.error(f"自选股演示失败: {e}")
        import traceback

        traceback.print_exc()


def demo_portfolio():
    """演示组合管理功能"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from src.application.portfolio.model import Portfolio
    from src.infrastructure.persistence.portfolio_repository_impl import PortfolioRepositoryImpl
    from src.application.portfolio.portfolio_app_service import PortfolioApplicationService

    print("\n" + "=" * 70)
    print("组合管理功能演示")
    print("=" * 70)

    engine = create_engine("sqlite:///./portfolio_demo.db", echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()

    portfolio_repo = PortfolioRepositoryImpl(session)
    portfolio_service = PortfolioApplicationService(portfolio_repo)

    try:
        portfolio = portfolio_service.create_portfolio(
            name="科技成长组合",
            portfolio_type="simulation",
            initial_capital=1000000,
            description="模拟组合，用于测试策略",
        )
        print(f"\n创建组合: {portfolio['name']}")
        print(f"  ID: {portfolio['id']}")
        print(f"  初始资金: {portfolio['initial_capital']}")

        positions = [
            ("300750", 200, 180.0),
            ("002475", 500, 28.50),
            ("000333", 300, 55.80),
        ]

        for symbol, qty, price in positions:
            result = portfolio_service.add_position(
                portfolio_id=portfolio["id"], symbol=symbol, quantity=qty, price=price
            )
            print(f"\n添加持仓: {symbol}")
            print(f"  数量: {qty}")
            print(f"  成本: {price}")

        portfolio_service.update_prices(portfolio["id"], {"300750": 210.0, "002475": 31.20, "000333": 58.90})

        perf = portfolio_service.get_performance(portfolio["id"])
        print(f"\n组合绩效:")
        print(f"  当前价值: {perf['current_value']}")
        print(f"  总收益: {perf['total_return']}%")
        print(f"  持仓价值: {perf['holdings_value']}")

        allocation = portfolio_service.get_allocation(portfolio["id"])
        print(f"\n配置分析:")
        print(f"  持仓数量: {len(allocation['holdings'])}")
        print(f"  最大持仓: {allocation['position_concentration']['max_position']}%")

        print("\n✅ 组合管理演示完成")

    except Exception as e:
        logger.error(f"组合管理演示失败: {e}")
        import traceback

        traceback.print_exc()


def demo_prediction():
    """演示预测功能"""
    from src.domain.prediction.prediction_service import create_prediction_service

    print("\n" + "=" * 70)
    print("预测功能演示")
    print("=" * 70)

    prediction_service = create_prediction_service()

    try:
        result = prediction_service.predict_price_direction("600519", lookback_days=30)
        print(f"\n价格走势预测 (600519):")
        print(f"  预测趋势: {result.get('predicted_trend', 'N/A')}")
        print(f"  置信度: {result.get('confidence', 0):.2%}")

        result = prediction_service.predict_volatility("600519", period_days=10)
        print(f"\n波动率预测:")
        print(f"  历史波动率: {result.get('historical_volatility', 0):.2f}%")
        print(f"  预测波动率: {result.get('predicted_volatility', 0):.2f}%")

        print("\n✅ 预测功能演示完成")

    except Exception as e:
        logger.error(f"预测功能演示失败: {e}")


def main():
    print("\n" + "=" * 70)
    print("MyStocks 自选股与组合管理演示")
    print("=" * 70)

    demo_watchlist()
    demo_portfolio()
    demo_prediction()

    print("\n" + "=" * 70)
    print("全部演示完成！")
    print("=" * 70)
    print("\n关键功能:")
    print("  ✓ 自选股分组管理")
    print("  ✓ 技术指标快照")
    print("  ✓ 组合持仓管理")
    print("  ✓ 绩效分析")
    print("  ✓ 价格预测")
    print("\n下一步:")
    print("  1. 集成真实数据源")
    print("  2. 添加Web API接口")
    print("  3. 实现前端界面")


if __name__ == "__main__":
    main()
