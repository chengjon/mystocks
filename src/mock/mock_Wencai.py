"""
Mock数据文件: Wencai
提供接口:
1. get_wencai_queries() -> Dict - 获取预定义查询列表（对应/api/market/wencai/queries）
2. execute_query() -> Dict - 执行预定义查询（对应/api/market/wencai/query）
3. execute_custom_query() -> Dict - 执行自定义查询（对应/api/market/wencai/custom-query）
4. get_query_results() -> Dict - 获取查询结果（对应/api/market/wencai/results/{queryName}）

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
import time


def get_wencai_queries() -> Dict:
    """获取预定义查询列表（对应/api/market/wencai/queries）

    Returns:
        Dict: 包含queries字段的字典，queries是查询列表数组
    """
    # 预定义查询模板
    predefined_queries = [
        {
            "id": 1,
            "query_name": "qs_1",
            "query_text": "今天涨停的股票",
            "description": "获取今日涨停股票列表",
            "category": "市场表现",
            "created_at": "2024-01-01 00:00:00",
            "is_active": True,
        },
        {
            "id": 2,
            "query_name": "qs_2",
            "query_text": "涨幅超过5%的股票",
            "description": "获取涨幅超过5%的股票",
            "category": "市场表现",
            "created_at": "2024-01-01 00:00:00",
            "is_active": True,
        },
        {
            "id": 3,
            "query_name": "qs_3",
            "query_text": "成交量放大的股票",
            "description": "获取成交量放大的股票",
            "category": "成交量",
            "created_at": "2024-01-01 00:00:00",
            "is_active": True,
        },
        {
            "id": 4,
            "query_name": "qs_4",
            "query_text": "技术指标金叉的股票",
            "description": "获取技术指标金叉的股票",
            "category": "技术分析",
            "created_at": "2024-01-01 00:00:00",
            "is_active": True,
        },
        {
            "id": 5,
            "query_name": "qs_5",
            "query_text": "机构重仓的股票",
            "description": "获取机构重仓的股票",
            "category": "机构动向",
            "created_at": "2024-01-01 00:00:00",
            "is_active": True,
        },
        {
            "id": 6,
            "query_name": "qs_6",
            "query_text": "业绩预增的股票",
            "description": "获取业绩预增的股票",
            "category": "基本面",
            "created_at": "2024-01-01 00:00:00",
            "is_active": True,
        },
        {
            "id": 7,
            "query_name": "qs_7",
            "query_text": "概念板块龙头股票",
            "description": "获取概念板块龙头股票",
            "category": "概念题材",
            "created_at": "2024-01-01 00:00:00",
            "is_active": True,
        },
        {
            "id": 8,
            "query_name": "qs_8",
            "query_text": "低估值股票",
            "description": "获取低估值股票",
            "category": "估值分析",
            "created_at": "2024-01-01 00:00:00",
            "is_active": True,
        },
        {
            "id": 9,
            "query_name": "qs_9",
            "query_text": "创新高股票",
            "description": "获取创新高股票",
            "category": "市场表现",
            "created_at": "2024-01-01 00:00:00",
            "is_active": True,
        },
    ]

    return {
        "queries": predefined_queries,
        "total": len(predefined_queries),
        "status": "success",
    }


def execute_query(request: Dict) -> Dict:
    """执行预定义查询（对应/api/market/wencai/query）

    Args:
        request: Dict - 请求参数：
                query_name: str - 查询名称
                pages: int - 页数

    Returns:
        Dict: 执行结果，包含total_records等字段
    """
    query_name = request.get("query_name", "qs_1")
    pages = request.get("pages", 1)

    # 模拟查询处理时间
    time.sleep(random.uniform(0.5, 2.0))

    # 生成查询结果数量（基于查询类型）
    query_result_counts = {
        "qs_1": random.randint(50, 150),  # 涨停股票
        "qs_2": random.randint(100, 300),  # 涨幅超过5%
        "qs_3": random.randint(200, 500),  # 成交量放大
        "qs_4": random.randint(80, 200),  # 技术指标金叉
        "qs_5": random.randint(150, 400),  # 机构重仓
        "qs_6": random.randint(60, 180),  # 业绩预增
        "qs_7": random.randint(30, 100),  # 概念龙头
        "qs_8": random.randint(300, 800),  # 低估值
        "qs_9": random.randint(80, 250),  # 创新高
    }

    total_records = query_result_counts.get(query_name, random.randint(100, 500))

    return {
        "success": True,
        "query_name": query_name,
        "pages": pages,
        "total_records": total_records,
        "message": f"查询执行成功，共找到 {total_records} 条记录",
        "execution_time": round(random.uniform(1.0, 3.0), 2),
    }


def execute_custom_query(request: Dict) -> Dict:
    """执行自定义查询（对应/api/market/wencai/custom-query）

    Args:
        request: Dict - 请求参数：
                query_text: str - 自定义查询文本
                pages: int - 页数

    Returns:
        Dict: 自定义查询结果
    """
    query_text = request.get("query_text", "")
    pages = request.get("pages", 1)

    # 模拟查询处理时间
    time.sleep(random.uniform(1.0, 3.0))

    # 根据查询文本内容估算结果数量
    base_count = random.randint(50, 200)

    if any(keyword in query_text.lower() for keyword in ["涨停", "封板", "板"]):
        base_count = random.randint(30, 120)
    elif any(keyword in query_text.lower() for keyword in ["涨幅", "上涨", "涨"]):
        base_count = random.randint(100, 400)
    elif any(keyword in query_text.lower() for keyword in ["放量", "成交", "量"]):
        base_count = random.randint(200, 600)
    elif any(keyword in query_text.lower() for keyword in ["低估", "价值", "便宜"]):
        base_count = random.randint(300, 800)

    # 生成结果数据
    results = generate_wencai_results(base_count)

    return {
        "success": True,
        "query_text": query_text,
        "pages": pages,
        "total_records": base_count,
        "results": results,
        "message": f"自定义查询执行成功，共找到 {base_count} 条记录",
        "execution_time": round(random.uniform(1.5, 4.0), 2),
    }


def get_query_results(query_name: str, limit: int = 20, offset: int = 0) -> Dict:
    """获取查询结果（对应/api/market/wencai/results/{queryName}）

    Args:
        query_name: str - 查询名称
        limit: int - 每页数量，默认20
        offset: int - 偏移量，默认0

    Returns:
        Dict: 查询结果数据
    """
    # 根据查询名称确定结果数量
    query_result_counts = {
        "qs_1": 120,
        "qs_2": 250,
        "qs_3": 380,
        "qs_4": 160,
        "qs_5": 320,
        "qs_6": 140,
        "qs_7": 75,
        "qs_8": 650,
        "qs_9": 180,
    }

    total_records = query_result_counts.get(query_name, 200)

    # 生成分页数据
    page_data = generate_wencai_results(min(limit, total_records - offset))

    # 添加分页信息
    for i, item in enumerate(page_data):
        item["序号"] = offset + i + 1

    return {
        "query_name": query_name,
        "results": page_data,
        "total_records": total_records,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total_records,
        "current_page": (offset // limit) + 1,
        "total_pages": (total_records + limit - 1) // limit,
    }


def generate_wencai_results(count: int) -> List[Dict]:
    """生成问财筛选结果数据

    Args:
        count: int - 要生成的结果数量

    Returns:
        List[Dict]: 问财结果数据列表
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

    # 生成结果
    results = []
    query_date = datetime.datetime.now().strftime("%Y-%m-%d")

    for i in range(count):
        stock = stock_pool[i % len(stock_pool)]

        # 根据行业生成合理的价格和涨跌幅
        if stock["industry"] in ["白酒", "银行", "保险"]:
            base_price = random.uniform(20, 200)
            price_change = random.uniform(-5, 8)
        elif stock["industry"] in ["医药生物", "电子", "计算机"]:
            base_price = random.uniform(10, 150)
            price_change = random.uniform(-8, 12)
        elif stock["industry"] in ["房地产", "建筑材料"]:
            base_price = random.uniform(5, 50)
            price_change = random.uniform(-6, 10)
        else:
            base_price = random.uniform(10, 100)
            price_change = random.uniform(-7, 9)

        current_price = round(base_price, 2)
        change_pct = round(price_change, 2)

        results.append(
            {
                "股票代码": stock["code"],
                "股票简称": stock["name"],
                "最新价": current_price,
                "涨跌幅": f"{change_pct:+.2f}%",
                "涨停次数": random.randint(0, 5),
                "量比": round(random.uniform(0.5, 5.0), 2),
                "换手率": f"{random.uniform(1, 15):.2f}%",
                "振幅": f"{random.uniform(2, 12):.2f}%",
                "查询日期": query_date,
            }
        )

    return results


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


if __name__ == "__main__":
    # 测试函数
    print("Mock文件模板测试")
    print("=" * 50)
    print("get_wencai_queries() 调用测试:")
    result1 = get_wencai_queries()
    print(f"返回数据: {result1}")

    print("\nget_query_results() 调用测试:")
    result2 = get_query_results("qs_1")
    print(f"返回数据: {result2}")

    print("\nexecute_custom_query() 调用测试:")
    result3 = execute_custom_query({"query_text": "涨幅超过5%的股票", "pages": 1})
    print(f"返回数据: {result3}")
