"""
WebSocket实时行情客户端测试
连接到WebSocket服务器并接收实时数据
"""
import asyncio
import json
import websockets
from datetime import datetime


async def test_market_websocket():
    """测试市场数据WebSocket连接"""
    uri = "ws://localhost:8001/ws/market"

    print("=" * 60)
    print("🔌 连接到MyStocks实时行情服务器...")
    print(f"📡 服务器地址: {uri}")
    print("=" * 60)

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ 连接成功！")

            # 发送开始命令
            await websocket.send(json.dumps({"action": "start"}))
            print("📤 发送: 开始接收数据")

            # 接收数据
            message_count = 0
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    message_count += 1

                    timestamp = datetime.now().strftime("%H:%M:%S")

                    if data.get("type") == "init":
                        print(f"\n[{timestamp}] 📦 收到初始快照")
                        snapshot = data["data"]
                        print(f"  - 指数: {len(snapshot['indices'])}个")
                        print(f"  - 股票: {len(snapshot['stocks'])}个")
                        print(f"  - 市场统计: 涨停{snapshot['marketStats']['limitUp']} 跌停{snapshot['marketStats']['limitDown']}")

                    elif data.get("type") == "incremental":
                        if message_count % 10 == 0:  # 每10条打印一次摘要
                            print(f"\n[{timestamp}] 📊 收到增量更新 #{message_count}")
                            print(f"  - 更新数: {len(data['updates'])}条")
                            for update in data['updates'][:2]:  # 只显示前2条
                                obj_type = update['type']
                                obj_data = update['data']
                                code = obj_data['code']
                                if obj_type == 'index':
                                    value = obj_data['value']
                                    change = obj_data['change']
                                    print(f"    • 指数 {code}: {value:.2f} ({change:+.2f}%)")
                                else:
                                    price = obj_data['price']
                                    change = obj_data['change']
                                    print(f"    • 股票 {code}: {price:.2f} ({change:+.2f}%)")

                    elif data.get("type") == "info":
                        print(f"\n[{timestamp}] ℹ️  {data['message']}")

                except asyncio.TimeoutError:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ⏱️  等待数据超时，重新连接...")
                    continue

    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket错误: {e}")
    except KeyboardInterrupt:
        print("\n\n👋 测试结束")


async def test_api_endpoints():
    """测试HTTP API端点"""
    import aiohttp

    print("\n" + "=" * 60)
    print("🧪 测试HTTP API端点")
    print("=" * 60)

    # 测试健康检查
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8001/health") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"✅ 健康检查: {data}")
            else:
                print(f"❌ 健康检查失败: {resp.status}")


async def main():
    """主函数"""
    print("\n🎯 MyStocks WebSocket客户端测试")
    print("按 Ctrl+C 停止测试\n")

    # 先测试API
    await test_api_endpoints()

    # 然后测试WebSocket
    await test_market_websocket()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n✨ 测试完成")
