#!/usr/bin/env python3
"""
验证双数据库集成 - PostgreSQL + TDengine

检查PostgreSQL和TDengine数据库连接、数据表和数据访问功能。
"""

import asyncio
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "web" / "backend"))


async def verify_postgresql():
    """验证PostgreSQL数据库连接和数据"""
    print("\n" + "=" * 60)
    print("🔍 验证 PostgreSQL 数据库")
    print("=" * 60)

    try:
        from src.data_access import PostgreSQLDataAccess

        pg = PostgreSQLDataAccess()
        print("✅ PostgreSQLDataAccess导入成功")

        # 测试连接
        print("\n📊 测试股票列表查询...")
        stocks = await pg.get_stock_list(limit=5)
        print(f"✅ 查询成功，返回 {len(stocks)} 只股票")
        if stocks:
            print(f"   示例: {stocks[0].get('symbol', 'N/A')} - {stocks[0].get('name', 'N/A')}")

        # 测试K线数据查询
        print("\n📈 测试K线数据查询（日线）...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        kline_data = await pg.get_kline_data(
            symbol="000001",
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
        )
        print(f"✅ 查询成功，返回 {len(kline_data)} 条K线数据")
        if kline_data:
            latest = kline_data[-1]
            print(f"   最新数据: {latest.get('trade_date', 'N/A')} - 收盘价: {latest.get('close', 'N/A')}")

        return {
            "status": "success",
            "stocks_count": len(stocks),
            "kline_count": len(kline_data),
        }

    except Exception as e:
        print(f"❌ PostgreSQL验证失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return {"status": "error", "message": str(e)}


async def verify_tdengine():
    """验证TDengine数据库连接和数据"""
    print("\n" + "=" * 60)
    print("🔍 验证 TDengine 数据库")
    print("=" * 60)

    try:
        from src.data_access import TDengineDataAccess

        td = TDengineDataAccess()
        print("✅ TDengineDataAccess导入成功")

        # 测试K线数据查询（分钟级）
        print("\n📈 测试分钟级K线数据查询...")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)

        kline_data = await td.get_kline_data(
            symbol="000001",
            start_date=start_date.strftime("%Y-%m-%d %H:%M:%S"),
            end_date=end_date.strftime("%Y-%m-%d %H:%M:%S"),
        )
        print(f"✅ 查询成功，返回 {len(kline_data)} 条K线数据")
        if kline_data:
            latest = kline_data[-1]
            print(f"   最新数据: {latest.get('ts', 'N/A')} - 收盘价: {latest.get('close', 'N/A')}")

        return {
            "status": "success",
            "kline_count": len(kline_data),
        }

    except Exception as e:
        print(f"❌ TDengine验证失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return {"status": "error", "message": str(e)}


async def verify_dual_db_architecture():
    """验证双数据库架构设计"""
    print("\n" + "=" * 60)
    print("🏗️  验证双数据库架构设计")
    print("=" * 60)

    try:
        from src.core import DataClassification, DatabaseTarget, DataStorageStrategy

        print("✅ 导入架构模块成功")

        # 测试数据分类
        print("\n📊 测试数据分类...")
        assert DataClassification.HIGH_FREQUENCY_TIMESERIES == "high_frequency_timeseries"
        assert DataClassification.DAILY_KLINE == "daily_kline"
        print("✅ 数据分类枚举正确")

        # 测试数据库目标
        print("\n🎯 测试数据库目标...")
        assert DatabaseTarget.TDENGINE == "tdengine"
        assert DatabaseTarget.POSTGRESQL == "postgresql"
        print("✅ 数据库目标枚举正确")

        # 测试存储策略
        print("\n💾 测试存储策略...")
        strategy = DataStorageStrategy()
        target = strategy.select_database("high_frequency_timeseries")
        print(f"✅ 高频时序数据 -> {target}")

        target = strategy.select_database("daily_kline")
        print(f"✅ 日K线数据 -> {target}")

        return {"status": "success"}

    except Exception as e:
        print(f"❌ 架构验证失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return {"status": "error", "message": str(e)}


async def verify_data_adapters():
    """验证数据源适配器"""
    print("\n" + "=" * 60)
    print("🔌 验证数据源适配器")
    print("=" * 60)

    try:
        from src.adapters import AkshareDataSource

        print("✅ 导入数据源适配器成功")

        # 测试Akshare数据源
        print("\n📡 测试Akshare数据源...")
        adapter = AkshareDataSource()

        # 获取股票列表
        stocks = await adapter.get_stock_list()
        print(f"✅ Akshare股票列表: {len(stocks)} 只股票")

        return {
            "status": "success",
            "adapter_count": 1,
            "stocks_count": len(stocks),
        }

    except Exception as e:
        print(f"❌ 数据源适配器验证失败: {str(e)}")
        import traceback

        traceback.print_exc()
        return {"status": "error", "message": str(e)}


async def main():
    """主验证流程"""
    print("\n" + "=" * 60)
    print("🚀 MyStocks 双数据库集成验证")
    print("=" * 60)
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}

    # 1. 验证架构设计
    results["architecture"] = await verify_dual_db_architecture()

    # 2. 验证PostgreSQL
    results["postgresql"] = await verify_postgresql()

    # 3. 验证TDengine
    results["tdengine"] = await verify_tdengine()

    # 4. 验证数据源适配器
    results["adapters"] = await verify_data_adapters()

    # 生成总结报告
    print("\n" + "=" * 60)
    print("📋 验证总结")
    print("=" * 60)

    success_count = sum(1 for v in results.values() if v.get("status") == "success")
    total_count = len(results)

    print(f"\n✅ 成功: {success_count}/{total_count}")
    print(f"❌ 失败: {total_count - success_count}/{total_count}")

    for name, result in results.items():
        status_icon = "✅" if result.get("status") == "success" else "❌"
        print(f"{status_icon} {name}: {result.get('status', 'unknown')}")

        if result.get("status") == "success":
            # 显示关键指标
            for key, value in result.items():
                if key != "status" and isinstance(value, (int, float)):
                    print(f"   - {key}: {value}")

    # 最终结论
    print("\n" + "=" * 60)
    if success_count == total_count:
        print("🎉 所有验证通过！双数据库集成正常工作。")
    else:
        print("⚠️  部分验证失败，请检查错误日志。")
    print("=" * 60)

    return results


if __name__ == "__main__":
    results = asyncio.run(main())
