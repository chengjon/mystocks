#!/usr/bin/env python3
"""监控数据库连接测试脚本"""

import asyncio
import os
import sys


# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)


async def test_database_connection():
    """测试监控数据库连接"""
    try:
        from src.monitoring.infrastructure.postgresql_async_v3 import get_postgres_async, initialize_postgres_async

        print("🔌 开始初始化监控数据库连接...")
        success = await initialize_postgres_async()

        if success:
            print("✅ 监控数据库连接成功!")

            # 测试查询
            postgres_async = get_postgres_async()
            if postgres_async.is_connected():
                print("✅ 连接池状态: 已连接")

                # 测试查询清单
                watchlists = await postgres_async.get_user_watchlists(1)
                print(f"✅ 查询成功: 找到 {len(watchlists)} 个清单")

                # 显示清单详情
                for w in watchlists:
                    print(f"   - {w['name']} ({w['type']}): ID={w['id']}")

                    # 获取清单中的股票
                    stocks = await postgres_async.get_watchlist_stocks(w["id"])
                    print(f"     股票: {len(stocks)} 只")
                    for s in stocks:
                        print(f"       • {s['stock_code']} @ {s['entry_price']}")

            else:
                print("❌ 连接池状态: 未连接")

        else:
            print("❌ 监控数据库初始化失败!")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_database_connection())
