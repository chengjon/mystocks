"""
Mock数据文件: RealTimeMonitor
提供接口:
1. get_realtime_alerts() -> List[Dict] - 获取实时告警
2. get_monitoring_summary() -> Dict - 获取监控摘要  
3. get_monitoring_status() -> Dict - 获取监控状态

使用说明:
- 所有函数参数需与真实API接口完全对齐
- 返回值字段名需与前端表格列字段一致
- 股票价格保留2位小数，百分比保留4位小数
- 时间字段使用datetime类型，格式：YYYY-MM-DD HH:MM:SS

作者: Claude Code
生成时间: 2025-11-15
"""

from typing import List, Dict, Optional
import pandas as pd
import datetime
import random
from decimal import Decimal


def get_realtime_alerts(params: Optional[Dict] = None) -> List[Dict]:
    """获取实时告警
    
    Args:
        params: Dict - 查询参数：
                limit: int - 返回记录数，默认50
                offset: int - 偏移量，默认0
                is_read: bool - 是否已读，None表示全部
        
    Returns:
        List[Dict]: 实时告警数据列表，包含：
                   - id: 告警ID
                   - symbol: 股票代码
                   - stock_name: 股票名称
                   - alert_type: 告警类型
                   - level: 告警级别
                   - message: 告警消息
                   - timestamp: 时间戳
                   - is_read: 是否已读
    """
    # 默认参数
    params = params or {}
    limit = params.get('limit', 50)
    offset = params.get('offset', 0)
    is_read = params.get('is_read')
    
    # 告警类型和级别
    alert_types = ['价格突破', '成交量激增', '技术指标', '资金流向', '龙虎榜']
    alert_levels = ['high', 'medium', 'low']
    stock_symbols = ['600519', '000858', '600036', '000001', '300750', '688981', '600276']
    stock_names = ['贵州茅台', '五粮液', '招商银行', '平安银行', '宁德时代', '中芯国际', '恒瑞医药']
    
    # 生成告警数据
    alerts = []
    for i in range(100):  # 生成100条告警数据
        symbol_idx = i % len(stock_symbols)
        alert_type = random.choice(alert_types)
        alert_level = random.choice(alert_levels)
        
        # 生成告警消息
        if alert_type == '价格突破':
            message = f"{stock_names[symbol_idx]}股价突破{random.randint(100, 2000)}元"
        elif alert_type == '成交量激增':
            message = f"{stock_names[symbol_idx]}成交量激增{random.randint(2, 10)}倍"
        elif alert_type == '技术指标':
            indicators = ['RSI', 'MACD', 'KDJ']
            message = f"{stock_names[symbol_idx]}{random.choice(indicators)}指标出现信号"
        elif alert_type == '资金流向':
            direction = '流入' if random.choice([True, False]) else '流出'
            amount = random.randint(1000, 10000)
            message = f"{stock_names[symbol_idx]}主力资金{direction}{amount}万元"
        else:  # 龙虎榜
            message = f"{stock_names[symbol_idx]}登上龙虎榜"
        
        # 生成时间戳（最近24小时内）
        timestamp = datetime.datetime.now() - datetime.timedelta(
            minutes=random.randint(0, 1440)
        )
        
        alerts.append({
            "id": i + 1,
            "symbol": stock_symbols[symbol_idx],
            "stock_name": stock_names[symbol_idx],
            "alert_type": alert_type,
            "level": alert_level,
            "message": message,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "is_read": random.choice([True, False]) if is_read is None else is_read
        })
    
    # 根据参数筛选和分页
    if is_read is not None:
        alerts = [alert for alert in alerts if alert['is_read'] == is_read]
    
    # 分页
    total_alerts = len(alerts)
    paginated_alerts = alerts[offset:offset + limit]
    
    # 添加总数信息
    for alert in paginated_alerts:
        alert['total'] = total_alerts
    
    return paginated_alerts


def get_monitoring_summary() -> Dict:
    """获取监控摘要
    
    Returns:
        Dict: 监控摘要数据，包含：
             - total_stocks: 总股票数
             - limit_up_count: 涨停数
             - limit_down_count: 跌停数
             - strong_up_count: 强势上涨数
             - strong_down_count: 强势下跌数
             - avg_change_percent: 平均涨跌幅
             - total_amount: 总成交额
             - active_alerts: 活跃告警数
             - unread_alerts: 未读告警数
    """
    return {
        "total_stocks": 4000,
        "limit_up_count": random.randint(30, 60),
        "limit_down_count": random.randint(5, 15),
        "strong_up_count": random.randint(80, 150),
        "strong_down_count": random.randint(40, 100),
        "avg_change_percent": round(random.uniform(-2.0, 2.0), 2),
        "total_amount": round(random.uniform(800, 1200), 2) * 100000000,  # 800-1200亿
        "active_alerts": random.randint(15, 35),
        "unread_alerts": random.randint(8, 20)
    }


def get_monitoring_status() -> Dict:
    """获取监控状态
    
    Returns:
        Dict: 监控状态信息，包含：
             - is_running: 是否运行中
             - start_time: 启动时间
             - last_update: 最后更新时间
             - monitored_symbols: 监控股票数
             - active_alerts: 活跃告警数
             - status: 状态
    """
    return {
        "is_running": True,
        "start_time": (datetime.datetime.now() - datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
        "last_update": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "monitored_symbols": 100,
        "active_alerts": random.randint(10, 25),
        "status": "healthy"
    }


def generate_realistic_price(base_price: float = 100.0, volatility: float = 0.02) -> float:
    """生成真实感的价格数据
    
    Args:
        base_price: 基准价格
        volatility: 波动率
        
    Returns:
        float: 生成的价格（保留2位小数）
    """
    change_rate = random.uniform(-volatility, volatility)
    price = base_price * (1 + change_rate)
    return round(price, 2)


def generate_realistic_volume() -> int:
    """生成真实感的成交量数据
    
    Returns:
        int: 成交量（股）
    """
    return random.randint(1000000, 100000000)


if __name__ == "__main__":
    # 测试函数
    print("Mock文件模板测试")
    print("=" * 50)
    print(f"get_realtime_alerts() 调用测试:")
    result1 = get_realtime_alerts()
    print(f"返回数据: {result1[:2]}")  # 只显示前2条
    
    print(f"\nget_monitoring_summary() 调用测试:")
    result2 = get_monitoring_summary()
    print(f"返回数据: {result2}")
    
    print(f"\nget_monitoring_status() 调用测试:")
    result3 = get_monitoring_status()
    print(f"返回数据: {result3}")

