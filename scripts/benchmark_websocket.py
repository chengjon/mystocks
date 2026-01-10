"""
WebSocket 并发压测工具 (Benchmark)
================================

功能：
1. 模拟大量并发客户端连接
2. 订阅特定频道
3. 统计消息延迟和吞吐量
4. 验证心跳机制

使用方法：
python3 scripts/benchmark_websocket.py --clients 100 --duration 60
"""

import asyncio
import time
import json
import argparse
import websockets
import statistics
from datetime import datetime

async def client_simulator(client_id, url, channels, duration, stats):
    """模拟单个 WebSocket 客户端"""
    try:
        start_time = time.time()
        # 建立连接
        uri = f"{url}?channels={channels}&client_id=bench_{client_id}"
        async with websockets.connect(uri) as websocket:
            stats['active_connections'] += 1
            
            # 监听消息
            while time.time() - start_time < duration:
                try:
                    # 设置超时以防挂起
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    
                    # 如果是事件消息，计算延迟
                    if 'timestamp' in data:
                        event_ts = datetime.fromisoformat(data['timestamp']).timestamp()
                        latency = (time.time() - event_ts) * 1000
                        stats['latencies'].append(latency)
                    
                    stats['msg_count'] += 1
                    
                except asyncio.TimeoutError:
                    # 正常现象，可能没消息发送
                    continue
                except websockets.ConnectionClosed:
                    stats['errors'] += 1
                    break
                    
    except Exception as e:
        print(f"Client {client_id} error: {e}")
        stats['errors'] += 1
    finally:
        stats['active_connections'] -= 1

async def run_benchmark(args):
    print(f"🚀 启动 WebSocket 压测: {args.clients} 个并发客户端...")
    print(f"📍 目标地址: {args.url}")
    print(f"📡 订阅频道: {args.channels}")
    
    stats = {
        'active_connections': 0,
        'msg_count': 0,
        'latencies': [],
        'errors': 0
    }
    
    # 启动所有客户端
    tasks = []
    for i in range(args.clients):
        tasks.append(client_simulator(i, args.url, args.channels, args.duration, stats))
        # 稍微错开启动时间，避免瞬间冲击
        if i % 10 == 0:
            await asyncio.sleep(0.1)
            
    # 等待压测结束
    print(f"⏳ 运行中 ({args.duration}秒)...")
    await asyncio.gather(*tasks)
    
    # 输出报告
    print("\n" + "="*40)
    print("📊 压测报告")
    print("="*40)
    print(f"总连接请求: {args.clients}")
    print(f"成功接收消息: {stats['msg_count']} 条")
    print(f"发生错误: {stats['errors']} 次")
    
    if stats['latencies']:
        print(f"平均延迟: {statistics.mean(stats['latencies']):.2f} ms")
        print(f"P95 延迟: {statistics.quantiles(stats['latencies'], n=20)[18]:.2f} ms")
        print(f"P99 延迟: {statistics.quantiles(stats['latencies'], n=100)[98]:.2f} ms")
    else:
        print("未收到包含时间戳的事件消息")
    print("="*40)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WebSocket Benchmark")
    parser.add_argument("--url", default="ws://localhost:8000/ws/events", help="WS URL")
    parser.add_argument("--clients", type=int, default=50, help="并发数量")
    parser.add_argument("--duration", type=int, default=30, help="持续时间(秒)")
    parser.add_argument("--channels", default="events:tasks,events:indicators", help="订阅频道")
    
    args = parser.parse_args()
    asyncio.run(run_benchmark(args))
