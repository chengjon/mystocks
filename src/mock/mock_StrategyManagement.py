"""
Mock数据文件: StrategyManagement
提供接口:
1. get_strategy_definitions() -> Dict - 获取策略定义列表（对应/api/strategy/definitions）
2. run_strategy_single() -> Dict - 单策略运行（对应/api/strategy/run/single）
3. run_strategy_batch() -> Dict - 批量策略运行（对应/api/strategy/run/batch）
4. get_strategy_results() -> Dict - 获取策略结果（对应/api/strategy/results）
5. get_matched_stocks() -> Dict - 获取匹配的股票（对应/api/strategy/matched-stocks）
6. get_strategy_stats() -> Dict - 获取策略统计（对应/api/strategy/stats/summary）

使用说明:
- 所有函数参数需与真实API接口完全对齐
- 返回值字段名需与前端表格列字段一致
- 股票价格保留2位小数，百分比保留4位小数
- 时间字段使用datetime类型，格式：YYYY-MM-DD HH:MM:SS

作者: Claude Code
生成时间: 2025-11-13
"""

import datetime
import random
import time
from typing import Dict, List


def get_strategy_definitions() -> Dict:
    """获取策略定义列表（对应/api/strategy/definitions）

    Returns:
        Dict: 策略定义列表数据
    """
    strategies = [
        {
            "strategy_code": "STR001",
            "strategy_name_cn": "放量突破策略",
            "strategy_name_en": "VolumeBreakthrough",
            "description": "基于成交量放大的突破信号，适合强势股票筛选",
            "is_active": True,
            "category": "趋势跟踪",
            "parameters": {
                "ma_period": "20",
                "volume_multiplier": "1.5",
                "breakthrough_threshold": "0.03",
            },
            "created_at": "2024-01-01 10:00:00",
            "last_run": "2024-12-01 15:30:00",
        },
        {
            "strategy_code": "STR002",
            "strategy_name_cn": "均线多头策略",
            "strategy_name_en": "MovingAverageBullish",
            "description": "多头排列的均线系统，适合中长线投资",
            "is_active": True,
            "category": "趋势跟踪",
            "parameters": {
                "ma5_period": "5",
                "ma10_period": "10",
                "ma20_period": "20",
                "ma60_period": "60",
            },
            "created_at": "2024-01-01 10:00:00",
            "last_run": "2024-12-01 15:30:00",
        },
        {
            "strategy_code": "STR003",
            "strategy_name_cn": "KDJ金叉策略",
            "strategy_name_en": "KDJGoldenCross",
            "description": "基于KDJ指标金叉信号，适合短线操作",
            "is_active": True,
            "category": "技术指标",
            "parameters": {"k_period": "9", "d_period": "3", "j_period": "3"},
            "created_at": "2024-01-01 10:00:00",
            "last_run": "2024-12-01 15:30:00",
        },
        {
            "strategy_code": "STR004",
            "strategy_name_cn": "MACD底背离策略",
            "strategy_name_en": "MACDBottomDivergence",
            "description": "识别MACD底背离信号，适合抄底操作",
            "is_active": True,
            "category": "技术指标",
            "parameters": {
                "fast_period": "12",
                "slow_period": "26",
                "signal_period": "9",
            },
            "created_at": "2024-01-01 10:00:00",
            "last_run": "2024-12-01 15:30:00",
        },
        {
            "strategy_code": "STR005",
            "strategy_name_cn": "RSI超卖策略",
            "strategy_name_en": "RSIOverSold",
            "description": "RSI指标超卖区域反弹机会，适合逆势操作",
            "is_active": False,
            "category": "技术指标",
            "parameters": {
                "rsi_period": "14",
                "oversold_level": "30",
                "overbought_level": "70",
            },
            "created_at": "2024-01-01 10:00:00",
            "last_run": "2024-12-01 15:30:00",
        },
        {
            "strategy_code": "STR006",
            "strategy_name_cn": "布林带突破策略",
            "strategy_name_en": "BollingerBreakthrough",
            "description": "布林带上下轨突破信号，适合波动交易",
            "is_active": True,
            "category": "技术指标",
            "parameters": {
                "bb_period": "20",
                "bb_std": "2.0",
                "breakthrough_threshold": "0.02",
            },
            "created_at": "2024-01-01 10:00:00",
            "last_run": "2024-12-01 15:30:00",
        },
        {
            "strategy_code": "STR007",
            "strategy_name_cn": "停机坪策略",
            "strategy_name_en": "ParkingLot",
            "description": "长期横盘后的突破机会，适合价值投资",
            "is_active": True,
            "category": "形态识别",
            "parameters": {
                "consolidation_days": "30",
                "breakthrough_threshold": "0.05",
                "volume_threshold": "1.2",
            },
            "created_at": "2024-01-01 10:00:00",
            "last_run": "2024-12-01 15:30:00",
        },
        {
            "strategy_code": "STR008",
            "strategy_name_cn": "筹码密集策略",
            "strategy_name_en": "ChipConcentration",
            "description": "基于筹码分布的支撑阻力分析，适合中线操作",
            "is_active": True,
            "category": "筹码分析",
            "parameters": {
                "price_range_pct": "0.1",
                "chip_density_threshold": "0.3",
                "volume_weighted": True,
            },
            "created_at": "2024-01-01 10:00:00",
            "last_run": "2024-12-01 15:30:00",
        },
        {
            "strategy_code": "STR009",
            "strategy_name_cn": "资金流向策略",
            "strategy_name_en": "CapitalFlow",
            "description": "基于大单资金流向的主力追踪，适合跟随主力操作",
            "is_active": True,
            "category": "资金分析",
            "parameters": {
                "super_large_threshold": "10000000",
                "large_threshold": "5000000",
                "net_flow_period": "5",
            },
            "created_at": "2024-01-01 10:00:00",
            "last_run": "2024-12-01 15:30:00",
        },
        {
            "strategy_code": "STR010",
            "strategy_name_cn": "业绩驱动策略",
            "strategy_name_en": "PerformanceDriven",
            "description": "基于业绩增长和估值的价值投资策略",
            "is_active": True,
            "category": "基本面",
            "parameters": {
                "pe_threshold": "30",
                "growth_threshold": "0.2",
                "roe_threshold": "0.15",
            },
            "created_at": "2024-01-01 10:00:00",
            "last_run": "2024-12-01 15:30:00",
        },
    ]

    return {
        "success": True,
        "data": strategies,
        "total": len(strategies),
        "message": f"获取策略定义成功，共{len(strategies)}个策略",
    }


def run_strategy_single(request: Dict) -> Dict:
    """单策略运行（对应/api/strategy/run/single）

    Args:
        request: Dict - 请求参数：
                strategy_code: str - 策略代码
                parameters: Dict - 策略参数
                date_range: Dict - 日期范围

    Returns:
        Dict: 策略运行结果
    """
    strategy_code = request.get("strategy_code", "STR001")
    parameters = request.get("parameters", {})

    # 模拟策略运行时间
    execution_time = random.uniform(2, 8)
    time.sleep(execution_time)

    # 根据策略类型生成结果
    stock_count = random.randint(5, 50)

    # 生成匹配股票
    matched_stocks = generate_matched_stocks(stock_count)

    return {
        "success": True,
        "strategy_code": strategy_code,
        "execution_time": round(execution_time, 2),
        "total_stocks": stock_count,
        "matched_stocks": matched_stocks,
        "parameters": parameters,
        "message": f"策略运行成功，匹配{stock_count}只股票",
    }


def run_strategy_batch(request: Dict) -> Dict:
    """批量策略运行（对应/api/strategy/run/batch）

    Args:
        request: Dict - 请求参数：
                strategy_codes: List[str] - 策略代码列表
                parameters: Dict - 策略参数
                date_range: Dict - 日期范围

    Returns:
        Dict: 批量策略运行结果
    """
    strategy_codes = request.get("strategy_codes", ["STR001", "STR002"])
    request.get("parameters", {})

    # 模拟批量运行时间
    execution_time = random.uniform(5, 20)
    time.sleep(execution_time)

    # 为每个策略生成结果
    results = []
    total_stocks = 0

    for strategy_code in strategy_codes:
        stock_count = random.randint(3, 30)
        total_stocks += stock_count

        results.append(
            {
                "strategy_code": strategy_code,
                "stock_count": stock_count,
                "matched_stocks": generate_matched_stocks(stock_count),
            }
        )

    return {
        "success": True,
        "execution_time": round(execution_time, 2),
        "total_strategies": len(strategy_codes),
        "total_stocks": total_stocks,
        "results": results,
        "message": f"批量运行成功，处理{len(strategy_codes)}个策略，共匹配{total_stocks}只股票",
    }


def get_strategy_results(request: Dict) -> Dict:
    """获取策略结果（对应/api/strategy/results）

    Args:
        request: Dict - 请求参数：
                strategy_code: str - 策略代码
                limit: int - 限制数量
                offset: int - 偏移量

    Returns:
        Dict: 策略结果数据
    """
    strategy_code = request.get("strategy_code", "STR001")
    limit = request.get("limit", 20)
    offset = request.get("offset", 0)

    # 生成历史结果
    stock_count = random.randint(20, 100)
    results = generate_matched_stocks(stock_count)

    # 分页
    paginated_results = results[offset : offset + limit]

    return {
        "success": True,
        "strategy_code": strategy_code,
        "results": paginated_results,
        "total": stock_count,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < stock_count,
    }


def get_matched_stocks(request: Dict) -> Dict:
    """获取匹配的股票（对应/api/strategy/matched-stocks）

    Args:
        request: Dict - 请求参数：
                strategy_code: str - 策略代码
                filters: Dict - 筛选条件

    Returns:
        Dict: 匹配股票数据
    """
    strategy_code = request.get("strategy_code", "STR001")
    filters = request.get("filters", {})

    stock_count = random.randint(10, 80)
    matched_stocks = generate_matched_stocks(stock_count)

    return {
        "success": True,
        "strategy_code": strategy_code,
        "filters": filters,
        "matched_stocks": matched_stocks,
        "total": stock_count,
        "message": f"获取匹配股票成功，共{stock_count}只",
    }


def get_strategy_stats() -> Dict:
    """获取策略统计（对应/api/strategy/stats/summary）

    Returns:
        Dict: 策略统计数据
    """
    # 生成统计数据
    stats = {
        "total_strategies": 10,
        "active_strategies": 8,
        "total_runs": random.randint(100, 500),
        "today_runs": random.randint(5, 20),
        "total_matches": random.randint(1000, 5000),
        "avg_run_time": round(random.uniform(2, 10), 2),
        "success_rate": round(random.uniform(0.85, 0.95), 2),
        "strategy_performance": [
            {
                "strategy_code": "STR001",
                "strategy_name": "放量突破策略",
                "run_count": random.randint(20, 50),
                "avg_matches": random.randint(8, 25),
                "success_rate": round(random.uniform(0.80, 0.90), 2),
            },
            {
                "strategy_code": "STR002",
                "strategy_name": "均线多头策略",
                "run_count": random.randint(15, 40),
                "avg_matches": random.randint(12, 35),
                "success_rate": round(random.uniform(0.85, 0.95), 2),
            },
            {
                "strategy_code": "STR003",
                "strategy_name": "KDJ金叉策略",
                "run_count": random.randint(25, 60),
                "avg_matches": random.randint(5, 20),
                "success_rate": round(random.uniform(0.75, 0.85), 2),
            },
        ],
    }

    return {"success": True, "data": stats, "message": "获取策略统计成功"}


def generate_matched_stocks(count: int) -> List[Dict]:
    """生成匹配股票数据

    Args:
        count: int - 股票数量

    Returns:
        List[Dict]: 股票数据列表
    """
    # 股票基础数据池
    stock_pool = [
        {"code": "600519", "name": "贵州茅台", "industry": "白酒"},
        {"code": "600036", "name": "招商银行", "industry": "银行"},
        {"code": "000001", "name": "平安银行", "industry": "银行"},
        {"code": "000002", "name": "万科A", "industry": "房地产"},
        {"code": "000858", "name": "五粮液", "industry": "白酒"},
        {"code": "600276", "name": "恒瑞医药", "industry": "医药生物"},
        {"code": "600000", "name": "浦发银行", "industry": "银行"},
        {"code": "600887", "name": "伊利股份", "industry": "食品饮料"},
        {"code": "300750", "name": "宁德时代", "industry": "电池"},
        {"code": "002594", "name": "比亚迪", "industry": "新能源汽车"},
        {"code": "000776", "name": "广发证券", "industry": "非银金融"},
        {"code": "600104", "name": "上汽集团", "industry": "汽车"},
        {"code": "000568", "name": "泸州老窖", "industry": "白酒"},
        {"code": "002230", "name": "科大讯飞", "industry": "计算机"},
        {"code": "300015", "name": "爱尔眼科", "industry": "医疗服务"},
        {"code": "600585", "name": "海螺水泥", "industry": "建筑材料"},
        {"code": "002415", "name": "海康威视", "industry": "电子"},
        {"code": "000166", "name": "申万宏源", "industry": "非银金融"},
        {"code": "600009", "name": "上海机场", "industry": "交通运输"},
        {"code": "002304", "name": "洋河股份", "industry": "白酒"},
    ]

    # 如果需要更多股票，循环使用
    if count > len(stock_pool):
        stock_pool.extend(stock_pool * (count // len(stock_pool) + 1))

    # 生成股票数据
    stocks = []
    current_time = datetime.datetime.now()

    for i in range(count):
        stock = stock_pool[i % len(stock_pool)]

        # 生成合理的价格和涨跌幅
        base_price = random.uniform(10, 500)
        change_pct = random.uniform(-8, 12)

        current_price = round(base_price, 2)
        change_amount = round(current_price * change_pct / 100, 2)

        stocks.append(
            {
                "股票代码": stock["code"],
                "股票简称": stock["name"],
                "最新价": current_price,
                "涨跌幅": f"{change_pct:+.2f}%",
                "涨跌额": f"{change_amount:+.2f}",
                "成交量": f"{random.randint(100, 5000)}万手",
                "成交额": f"{random.randint(1, 50)}亿元",
                "换手率": f"{random.uniform(1, 15):.2f}%",
                "行业": stock["industry"],
                "策略得分": round(random.uniform(60, 95), 1),
                "匹配时间": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    return stocks


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
    def get_data_list():
        """获取数据列表（测试占位函数）"""
        return ["mock_data_1", "mock_data_2"]

    def get_data_detail():
        """获取数据详情（测试占位函数）"""
        return {"id": 1, "name": "测试数据", "value": 100.0}

    def get_data_table():
        """获取数据表（测试占位函数）"""
        return {"headers": ["id", "name", "value"], "rows": [[1, "测试", 100.0]]}

    print("Mock文件模板测试")
    print("=" * 50)
    print("get_data_list() 调用测试:")
    result1 = get_data_list()
    print(f"返回数据: {result1}")

    print("\nget_data_detail() 调用测试:")
    result2 = get_data_detail()
    print(f"返回数据: {result2}")

    print("\nget_data_table() 调用测试:")
    result3 = get_data_table()
    print(f"返回数据: {result3}")
