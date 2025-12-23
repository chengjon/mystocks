"""
Mock数据文件: Dashboard
提供接口:
1. get_market_stats() -> Dict - 获取市场统计数据（仪表盘顶部4个统计卡片）
2. get_market_heat_data() -> List[Dict] - 获取市场热度数据（图表）
3. get_leading_sectors() -> List[Dict] - 获取领涨板块数据（图表）
4. get_price_distribution() -> List[Dict] - 获取涨跌分布数据（图表）
5. get_capital_flow_data() -> List[Dict] - 获取资金流向数据（图表）
6. get_industry_fund_flow(standard: str) -> Dict - 获取行业资金流向（图表）
7. get_favorite_stocks() -> List[Dict] - 获取自选股板块表现数据
8. get_strategy_stocks() -> List[Dict] - 获取策略选股板块表现数据
9. get_industry_stocks() -> List[Dict] - 获取行业选股板块表现数据
10. get_concept_stocks() -> List[Dict] - 获取概念选股板块表现数据

使用说明:
- 所有函数参数需与真实API接口完全对齐
- 返回值字段名需与前端表格列字段一致
- 股票价格保留2位小数，百分比保留4位小数
- 时间字段使用datetime类型，格式：YYYY-MM-DD HH:MM:SS

作者: Claude Code
生成时间: 2025-11-13
"""

from typing import List, Dict
import datetime
import random


def get_market_overview() -> Dict:
    """获取市场概览数据（仪表盘顶部4个统计卡片）

    Returns:
        Dict: 包含总股票数、活跃股票、数据更新、系统状态
    """
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "total_stocks": {
            "title": "总股票数",
            "value": "4,526",
            "trend": "较昨日 +12",
            "trend_class": "up",
            "icon": "TrendCharts",
            "color": "#409eff",
        },
        "active_stocks": {
            "title": "活跃股票",
            "value": "3,891",
            "trend": "较昨日 +8",
            "trend_class": "up",
            "icon": "DataLine",
            "color": "#67c23a",
        },
        "data_update": {
            "title": "数据更新",
            "value": "刚刚",
            "trend": "今日更新",
            "trend_class": "neutral",
            "icon": "Refresh",
            "color": "#e6a23c",
        },
        "system_status": {
            "title": "系统状态",
            "value": "正常",
            "trend": "所有服务运行中",
            "trend_class": "up",
            "icon": "CircleCheck",
            "color": "#67c23a",
        },
        "last_update": current_time,
    }


def get_market_stats() -> Dict:
    """获取市场统计数据（监控摘要）

    Returns:
        Dict: 市场统计数据，包含涨跌分布、成交额等
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
        "unread_alerts": random.randint(8, 20),
    }


def get_market_heat() -> List[Dict]:
    """获取市场热度数据（用于市场热力图）

    Returns:
        List[Dict]: 各概念板块的热度指数数据
    """
    sectors = [
        "人工智能",
        "新能源车",
        "芯片半导体",
        "医药生物",
        "5G通信",
        "军工",
        "白酒",
        "光伏",
    ]
    return [{"name": sector, "value": random.randint(60, 95)} for sector in sectors]


def get_realtime_alerts() -> Dict:
    """获取实时告警数据（用于监控页面）

    Returns:
        Dict: 实时告警数据
    """
    # 告警类型和级别
    alert_types = ["价格突破", "成交量激增", "技术指标", "资金流向", "龙虎榜"]
    alert_levels = ["high", "medium", "low"]
    stock_symbols = [
        "600519",
        "000858",
        "600036",
        "000001",
        "300750",
        "688981",
        "600276",
    ]
    stock_names = [
        "贵州茅台",
        "五粮液",
        "招商银行",
        "平安银行",
        "宁德时代",
        "中芯国际",
        "恒瑞医药",
    ]

    # 生成告警数据
    alerts = []
    for i in range(25):  # 生成25条告警数据
        symbol_idx = i % len(stock_symbols)
        alert_type = random.choice(alert_types)
        alert_level = random.choice(alert_levels)

        # 生成告警消息
        if alert_type == "价格突破":
            message = f"{stock_names[symbol_idx]}股价突破{random.randint(100, 2000)}元"
        elif alert_type == "成交量激增":
            message = f"{stock_names[symbol_idx]}成交量激增{random.randint(2, 10)}倍"
        elif alert_type == "技术指标":
            indicators = ["RSI", "MACD", "KDJ"]
            message = (
                f"{stock_names[symbol_idx]}{random.choice(indicators)}指标出现信号"
            )
        elif alert_type == "资金流向":
            direction = "流入" if random.choice([True, False]) else "流出"
            amount = random.randint(1000, 10000)
            message = f"{stock_names[symbol_idx]}主力资金{direction}{amount}万元"
        else:  # 龙虎榜
            message = f"{stock_names[symbol_idx]}登上龙虎榜"

        # 生成时间戳（最近24小时内）
        timestamp = datetime.datetime.now() - datetime.timedelta(
            minutes=random.randint(0, 1440)
        )

        alerts.append(
            {
                "id": i + 1,
                "symbol": stock_symbols[symbol_idx],
                "stock_name": stock_names[symbol_idx],
                "alert_type": alert_type,
                "level": alert_level,
                "message": message,
                "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "is_read": random.choice([True, False]),
            }
        )

    return {
        "total": len(alerts),
        "alerts": alerts[:10],  # 只返回前10条
        "unread_count": len([a for a in alerts if not a["is_read"]]),
    }


def get_market_heat_data() -> List[Dict]:
    """获取市场热度数据（图表数据）

    Returns:
        List[Dict]: 各概念板块的热度指数数据
    """
    sectors = [
        "人工智能",
        "新能源车",
        "芯片半导体",
        "医药生物",
        "5G通信",
        "军工",
        "白酒",
        "光伏",
    ]
    return [{"name": sector, "value": random.randint(60, 95)} for sector in sectors]


def get_dragon_tiger_data() -> List[Dict]:
    """获取龙虎榜数据

    Returns:
        List[Dict]: 龙虎榜数据列表
    """
    stocks = [
        {"symbol": "600519", "name": "贵州茅台", "change": 5.2, "amount": 1500000000},
        {"symbol": "000858", "name": "五粮液", "change": 3.8, "amount": 800000000},
        {"symbol": "300750", "name": "宁德时代", "change": 4.5, "amount": 1200000000},
        {"symbol": "688981", "name": "中芯国际", "change": 6.1, "amount": 950000000},
        {"symbol": "002594", "name": "比亚迪", "change": 2.9, "amount": 750000000},
    ]

    return [
        {
            "symbol": stock["symbol"],
            "name": stock["name"],
            "change": stock["change"],
            "change_percent": round(stock["change"] * random.uniform(0.8, 1.2), 2),
            "amount": stock["amount"],
            "buy_amount": round(stock["amount"] * 0.6),
            "sell_amount": round(stock["amount"] * 0.4),
            "net_amount": round(stock["amount"] * 0.2),
            "rank": i + 1,
        }
        for i, stock in enumerate(stocks)
    ]


def get_leading_sectors() -> List[Dict]:
    """获取领涨板块数据（图表数据）

    Returns:
        List[Dict]: 各板块的涨幅数据
    """
    sectors = ["人工智能", "芯片", "新能源", "医疗", "5G", "军工", "消费", "金融"]
    return [
        {"name": sector, "change": round(random.uniform(2.0, 8.5), 2)}
        for sector in sectors
    ]


def get_price_distribution() -> List[Dict]:
    """获取涨跌分布数据（图表数据）

    Returns:
        List[Dict]: 各涨跌区间的股票数量分布
    """
    return [
        {
            "name": "涨停",
            "value": random.randint(400, 500),
            "itemStyle": {"color": "#f56c6c"},
        },
        {
            "name": "上涨",
            "value": random.randint(1200, 1300),
            "itemStyle": {"color": "#fca5a5"},
        },
        {
            "name": "平盘",
            "value": random.randint(750, 850),
            "itemStyle": {"color": "#909399"},
        },
        {
            "name": "下跌",
            "value": random.randint(1100, 1200),
            "itemStyle": {"color": "#86efac"},
        },
        {
            "name": "跌停",
            "value": random.randint(300, 400),
            "itemStyle": {"color": "#67c23a"},
        },
    ]


def get_capital_flow_data() -> List[Dict]:
    """获取资金流向数据（图表数据）

    Returns:
        List[Dict]: 各类型资金流向数据
    """
    return [
        {"name": "超大单", "value": round(random.uniform(100, 150), 1)},
        {"name": "大单", "value": round(random.uniform(80, 90), 1)},
        {"name": "中单", "value": round(random.uniform(-50, -40), 1)},
        {"name": "小单", "value": round(random.uniform(-170, -160), 1)},
    ]


def get_industry_fund_flow(standard: str = "csrc") -> Dict:
    """获取行业资金流向数据（图表数据）

    Args:
        standard: 行业分类标准（csrc=证监会，sw_l1=申万一级，sw_l2=申万二级）

    Returns:
        Dict: 行业资金流向图表配置
    """
    industry_data = {
        "csrc": {
            "categories": [
                "金融业",
                "房地产业",
                "制造业",
                "信息技术",
                "批发零售",
                "建筑业",
                "采矿业",
                "交通运输",
            ],
            "values": [185.5, 125.3, 98.7, 85.2, 52.8, 45.6, -38.5, -65.2],
        },
        "sw_l1": {
            "categories": [
                "计算机",
                "电子",
                "医药生物",
                "电力设备",
                "汽车",
                "食品饮料",
                "银行",
                "非银金融",
            ],
            "values": [165.8, 142.5, 118.9, 95.3, 78.6, 65.4, -45.8, -88.9],
        },
        "sw_l2": {
            "categories": [
                "半导体",
                "光学光电子",
                "计算机设备",
                "通信设备",
                "医疗器械",
                "化学制药",
                "白酒",
                "保险",
            ],
            "values": [195.2, 158.7, 125.6, 98.5, 85.3, 72.1, -52.3, -95.6],
        },
    }

    data = industry_data.get(standard, industry_data["csrc"])

    return {
        "categories": data["categories"],
        "values": data["values"],
        "standard": standard,
    }


def get_strategy_stocks() -> List[Dict]:
    """获取策略选股板块表现数据（表格数据）

    Returns:
        List[Dict]: 策略选股列表及评分数据
    """
    strategies = [
        {"symbol": "688981", "name": "中芯国际", "strategy": "突破策略", "score": 88},
        {"symbol": "002475", "name": "立讯精密", "strategy": "趋势跟踪", "score": 85},
        {"symbol": "300059", "name": "东方财富", "strategy": "均线策略", "score": 82},
        {"symbol": "600036", "name": "招商银行", "strategy": "价值投资", "score": 78},
        {"symbol": "000001", "name": "平安银行", "strategy": "价值投资", "score": 65},
    ]

    return [
        {
            "symbol": stock["symbol"],
            "name": stock["name"],
            "price": round(random.uniform(10, 100), 2),
            "change": round(random.uniform(-2, 6), 2),
            "strategy": stock["strategy"],
            "score": stock["score"],
            "signal": "买入"
            if stock["score"] > 80
            else ("卖出" if stock["score"] < 70 else "持有"),
        }
        for stock in strategies
    ]


def get_industry_stocks() -> List[Dict]:
    """获取行业选股板块表现数据（表格数据）

    Returns:
        List[Dict]: 行业龙头股票数据
    """
    industries = [
        {
            "symbol": "600519",
            "name": "贵州茅台",
            "industry": "白酒",
            "rank": 1,
            "market_cap": 21056,
        },
        {
            "symbol": "000858",
            "name": "五粮液",
            "industry": "白酒",
            "rank": 2,
            "market_cap": 6125,
        },
        {
            "symbol": "000568",
            "name": "泸州老窖",
            "industry": "白酒",
            "rank": 3,
            "market_cap": 2089,
        },
        {
            "symbol": "002304",
            "name": "洋河股份",
            "industry": "白酒",
            "rank": 4,
            "market_cap": 1516,
        },
        {
            "symbol": "600809",
            "name": "山西汾酒",
            "industry": "白酒",
            "rank": 5,
            "market_cap": 2268,
        },
    ]

    return [
        {
            "symbol": stock["symbol"],
            "name": stock["name"],
            "price": round(random.uniform(50, 2000), 2),
            "change": round(random.uniform(-1, 3), 2),
            "industry": stock["industry"],
            "industry_rank": stock["rank"],
            "market_cap": stock["market_cap"],
        }
        for stock in industries
    ]


def get_concept_stocks() -> List[Dict]:
    """获取概念选股板块表现数据（表格数据）

    Returns:
        List[Dict]: 热门概念股票数据
    """
    concepts = [
        {
            "symbol": "300750",
            "name": "宁德时代",
            "concepts": ["新能源", "电池", "MSCI"],
            "heat": 98,
        },
        {
            "symbol": "688981",
            "name": "中芯国际",
            "concepts": ["芯片", "半导体", "华为概念"],
            "heat": 95,
        },
        {
            "symbol": "600276",
            "name": "恒瑞医药",
            "concepts": ["医药", "创新药", "抗癌"],
            "heat": 88,
        },
        {
            "symbol": "300122",
            "name": "智飞生物",
            "concepts": ["疫苗", "医药", "生物制品"],
            "heat": 92,
        },
        {
            "symbol": "002230",
            "name": "科大讯飞",
            "concepts": ["AI", "人工智能", "语音识别"],
            "heat": 96,
        },
    ]

    return [
        {
            "symbol": stock["symbol"],
            "name": stock["name"],
            "price": round(random.uniform(20, 200), 2),
            "change": round(random.uniform(1, 7), 2),
            "concepts": stock["concepts"],
            "concept_heat": stock["heat"],
        }
        for stock in concepts
    ]


def generate_realistic_price(
    base_price: float = 100.0, volatility: float = 0.02
) -> float:
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


def get_dashboard_stats() -> List[Dict]:
    """获取Dashboard专用的统计数据数组格式

    Returns:
        List[Dict]: Dashboard.vue期望的stats数组格式
    """
    market_stats = get_market_stats()

    return [
        market_stats["total_stocks"],
        market_stats["active_stocks"],
        market_stats["data_update"],
        market_stats["system_status"],
    ]


def get_favorite_stocks() -> List[Dict]:
    """获取自选股板块表现数据（表格数据）

    Returns:
        List[Dict]: 自选股列表及其实时行情数据
    """
    stocks = [
        {"symbol": "600519", "name": "贵州茅台", "industry": "白酒"},
        {"symbol": "000858", "name": "五粮液", "industry": "白酒"},
        {"symbol": "300750", "name": "宁德时代", "industry": "电池"},
        {"symbol": "601012", "name": "隆基绿能", "industry": "光伏"},
        {"symbol": "002594", "name": "比亚迪", "industry": "新能源车"},
    ]

    return [
        {
            "symbol": stock["symbol"],
            "name": stock["name"],
            "price": round(random.uniform(20, 2000), 2),
            "change": round(random.uniform(-3, 5), 2),
            "volume": f"{random.randint(10, 50)}万手",
            "turnover": round(random.uniform(0.5, 5.0), 2),
            "industry": stock["industry"],
        }
        for stock in stocks
    ]


def get_strategy_stocks() -> List[Dict]:
    """获取策略选股板块表现数据（表格数据）

    Returns:
        List[Dict]: 策略选股列表及评分数据
    """
    strategies = [
        {"symbol": "688981", "name": "中芯国际", "strategy": "突破策略", "score": 88},
        {"symbol": "002475", "name": "立讯精密", "strategy": "趋势跟踪", "score": 85},
        {"symbol": "300059", "name": "东方财富", "strategy": "均线策略", "score": 82},
        {"symbol": "600036", "name": "招商银行", "strategy": "价值投资", "score": 78},
        {"symbol": "000001", "name": "平安银行", "strategy": "价值投资", "score": 65},
    ]

    return [
        {
            "symbol": stock["symbol"],
            "name": stock["name"],
            "price": round(random.uniform(10, 100), 2),
            "change": round(random.uniform(-2, 6), 2),
            "strategy": stock["strategy"],
            "score": stock["score"],
            "signal": "买入"
            if stock["score"] > 80
            else ("卖出" if stock["score"] < 70 else "持有"),
        }
        for stock in strategies
    ]


def get_industry_stocks() -> List[Dict]:
    """获取行业选股板块表现数据（表格数据）

    Returns:
        List[Dict]: 行业龙头股票数据
    """
    industries = [
        {
            "symbol": "600519",
            "name": "贵州茅台",
            "industry": "白酒",
            "rank": 1,
            "market_cap": 21056,
        },
        {
            "symbol": "000858",
            "name": "五粮液",
            "industry": "白酒",
            "rank": 2,
            "market_cap": 6125,
        },
        {
            "symbol": "000568",
            "name": "泸州老窖",
            "industry": "白酒",
            "rank": 3,
            "market_cap": 2089,
        },
        {
            "symbol": "002304",
            "name": "洋河股份",
            "industry": "白酒",
            "rank": 4,
            "market_cap": 1516,
        },
        {
            "symbol": "600809",
            "name": "山西汾酒",
            "industry": "白酒",
            "rank": 5,
            "market_cap": 2268,
        },
    ]

    return [
        {
            "symbol": stock["symbol"],
            "name": stock["name"],
            "price": round(random.uniform(50, 2000), 2),
            "change": round(random.uniform(-1, 3), 2),
            "industry": stock["industry"],
            "industry_rank": stock["rank"],
            "market_cap": stock["market_cap"],
        }
        for stock in industries
    ]


def get_concept_stocks() -> List[Dict]:
    """获取概念选股板块表现数据（表格数据）

    Returns:
        List[Dict]: 热门概念股票数据
    """
    concepts = [
        {
            "symbol": "300750",
            "name": "宁德时代",
            "concepts": ["新能源", "电池", "MSCI"],
            "heat": 98,
        },
        {
            "symbol": "688981",
            "name": "中芯国际",
            "concepts": ["芯片", "半导体", "华为概念"],
            "heat": 95,
        },
        {
            "symbol": "600276",
            "name": "恒瑞医药",
            "concepts": ["医药", "创新药", "抗癌"],
            "heat": 88,
        },
        {
            "symbol": "300122",
            "name": "智飞生物",
            "concepts": ["疫苗", "医药", "生物制品"],
            "heat": 92,
        },
        {
            "symbol": "002230",
            "name": "科大讯飞",
            "concepts": ["AI", "人工智能", "语音识别"],
            "heat": 96,
        },
    ]

    return [
        {
            "symbol": stock["symbol"],
            "name": stock["name"],
            "price": round(random.uniform(20, 200), 2),
            "change": round(random.uniform(1, 7), 2),
            "concepts": stock["concepts"],
            "concept_heat": stock["heat"],
        }
        for stock in concepts
    ]


def get_dashboard_industry_data() -> Dict:
    """获取Dashboard专用的行业数据

    Returns:
        Dict: Dashboard.vue期望的industryData格式
    """
    return {
        "csrc": {
            "categories": [
                "金融业",
                "房地产业",
                "制造业",
                "信息技术",
                "批发零售",
                "建筑业",
                "采矿业",
                "交通运输",
            ],
            "values": [185.5, 125.3, 98.7, 85.2, 52.8, 45.6, -38.5, -65.2],
        },
        "sw_l1": {
            "categories": [
                "计算机",
                "电子",
                "医药生物",
                "电力设备",
                "汽车",
                "食品饮料",
                "银行",
                "非银金融",
            ],
            "values": [165.8, 142.5, 118.9, 95.3, 78.6, 65.4, -45.8, -88.9],
        },
        "sw_l2": {
            "categories": [
                "半导体",
                "光学光电子",
                "计算机设备",
                "通信设备",
                "医疗器械",
                "化学制药",
                "白酒",
                "保险",
            ],
            "values": [195.2, 158.7, 125.6, 98.5, 85.3, 72.1, -52.3, -95.6],
        },
    }


if __name__ == "__main__":
    # 测试函数
    print("Mock文件模板测试")
    print("=" * 50)
    print("get_market_overview() 调用测试:")
    result1 = get_market_overview()
    print(f"返回数据: {result1}")

    print("\nget_market_stats() 调用测试:")
    result2 = get_market_stats()
    print(f"返回数据: {result2}")

    print("\nget_market_heat() 调用测试:")
    result3 = get_market_heat()
    print(f"返回数据: {result3}")
