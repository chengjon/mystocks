"""
Data Format Converter Middleware
Unify Mock data and real database data format to ensure field names and data structure consistency
"""

from typing import Dict, Any, List
import pandas as pd
import structlog

logger = structlog.get_logger()


def normalize_stock_data_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    标准化股票数据格式，统一字段名称和数据结构

    Args:
        df: 原始数据DataFrame

    Returns:
        标准化后的DataFrame
    """
    if df.empty:
        return df

    # 创建副本以避免修改原始数据
    normalized_df = df.copy()

    # 定义字段映射关系 (数据库字段 -> 标准字段)
    field_mapping = {
        # 股票基本信息字段
        "symbol": "symbol",  # 股票代码
        "name": "name",  # 股票名称
        "stock_name": "name",  # 备用字段名
        "cname": "name",  # 备用字段名
        "industry": "industry",  # 所属行业
        "sector": "industry",  # 备用字段名
        "area": "area",  # 地区
        "location": "area",  # 备用字段名
        "market": "market",  # 市场
        "exchange": "market",  # 备用字段名
        "list_date": "list_date",  # 上市日期
        "listing_date": "list_date",  # 备用字段名
        "ipo_date": "list_date",  # 备用字段名
        # K线数据字段
        "date": "date",  # 日期
        "trade_date": "date",  # 备用字段名
        "open": "open",  # 开盘价
        "high": "high",  # 最高价
        "low": "low",  # 最低价
        "close": "close",  # 收盘价
        "volume": "volume",  # 成交量
        "amount": "amount",  # 成交金额
        # 价格相关字段
        "price": "price",  # 价格
        "current_price": "price",  # 备用字段名
        "last_price": "price",  # 备用字段名
        "change": "change",  # 涨跌幅
        "change_percent": "change",  # 备用字段名
        "pct_change": "change",  # 备用字段名
        # 交易相关字段
        "turnover": "turnover",  # 换手率
        "turnover_rate": "turnover",  # 备用字段名
        "pe": "pe",  # 市盈率
        "pe_ttm": "pe",  # 备用字段名
        "pb": "pb",  # 市净率
        "pb_ratio": "pb",  # 备用字段名
    }

    # 重命名字段
    rename_dict = {}
    for col in normalized_df.columns:
        # 检查字段映射
        if col in field_mapping:
            standard_name = field_mapping[col]
            if standard_name != col and standard_name not in normalized_df.columns:
                rename_dict[col] = standard_name
        else:
            # 如果字段不在映射中，保持原名
            pass

    if rename_dict:
        normalized_df = normalized_df.rename(columns=rename_dict)
        logger.info("字段重命名完成", rename_dict=rename_dict)

    # 确保关键字段存在，如果不存在则添加默认值
    required_fields = ["symbol", "name", "industry", "area", "market", "list_date"]
    for field in required_fields:
        if field not in normalized_df.columns:
            logger.warning("关键字段缺失，使用默认值", field=field)
            if field == "symbol":
                normalized_df[field] = "N/A"
            elif field == "name":
                normalized_df[field] = "未命名"
            elif field in ["industry", "area", "market"]:
                normalized_df[field] = "N/A"
            elif field == "list_date":
                normalized_df[field] = pd.NaT  # 空日期

    # 数据类型标准化
    for col in normalized_df.columns:
        # 处理日期字段
        if "date" in col.lower() or "time" in col.lower():
            if not pd.api.types.is_datetime64_any_dtype(normalized_df[col]):
                try:
                    normalized_df[col] = pd.to_datetime(normalized_df[col])
                except Exception:
                    # 如果转换失败，保持原值
                    pass

        # 处理数值字段
        elif col in [
            "open",
            "high",
            "low",
            "close",
            "price",
            "change",
            "pe",
            "pb",
            "turnover",
            "amount",
        ]:
            if not pd.api.types.is_numeric_dtype(normalized_df[col]):
                try:
                    normalized_df[col] = pd.to_numeric(normalized_df[col], errors="coerce")
                except Exception:
                    pass

        # 强制处理成交量为整数类型 (长期方案)
        elif col == "volume":
            try:
                # 先转为数值（处理字符串等），NaN转为0，最后强制转为int64
                normalized_df[col] = pd.to_numeric(normalized_df[col], errors="coerce").fillna(0).astype("int64")
            except Exception:
                logger.warning("成交量类型转换失败", field=col)

    return normalized_df


def normalize_api_response_format(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    标准化API响应格式

    Args:
        data: 原始API响应数据

    Returns:
        标准化后的API响应数据
    """
    if not isinstance(data, dict):
        return data

    normalized_data = data.copy()

    # 如果有data字段，对其中的内容进行标准化
    if "data" in normalized_data:
        if isinstance(normalized_data["data"], pd.DataFrame):
            normalized_data["data"] = normalize_stock_data_format(normalized_data["data"])
        elif isinstance(normalized_data["data"], list):
            # 长期方案：对列表使用非Pandas的标准化方法，避免类型隐式提升
            try:
                # 使用专门处理列表的方法
                normalized_data["data"] = normalize_stock_list_format(normalized_data["data"])

                # 双重保障：如果是K线数据，确保 volume 是 int
                if len(normalized_data["data"]) > 0 and "volume" in normalized_data["data"][0]:
                    for item in normalized_data["data"]:
                        if "volume" in item and item["volume"] is not None:
                            try:
                                # 处理可能的 float 或 string
                                item["volume"] = int(float(item["volume"]))
                            except (ValueError, TypeError):
                                item["volume"] = 0
            except Exception as e:
                logger.warning("列表数据标准化失败: %s", e)

    # 添加缺失的必要字段
    if "success" not in normalized_data:
        normalized_data["success"] = True

    # 确保 total 是整数
    if "total" in normalized_data:
        try:
            normalized_data["total"] = int(float(normalized_data["total"]))
        except (ValueError, TypeError):
            pass
    elif "data" in normalized_data:
        if isinstance(normalized_data["data"], list):
            normalized_data["total"] = len(normalized_data["data"])
        elif isinstance(normalized_data["data"], pd.DataFrame):
            normalized_data["total"] = len(normalized_data["data"])

    if "timestamp" not in normalized_data:
        from datetime import datetime

        normalized_data["timestamp"] = datetime.now().isoformat()

    return normalized_data


def normalize_stock_list_format(
    stock_list: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    标准化股票列表格式

    Args:
        stock_list: 原始股票列表

    Returns:
        标准化后的股票列表
    """
    if not stock_list:
        return stock_list

    normalized_list = []
    field_mapping = {
        "stock_code": "symbol",
        "code": "symbol",
        "symbol": "symbol",
        "stock_name": "name",
        "name": "name",
        "cname": "name",
        "industry": "industry",
        "sector": "industry",
        "area": "area",
        "location": "area",
        "market": "market",
        "exchange": "market",
        "list_date": "list_date",
        "listing_date": "list_date",
        "ipo_date": "list_date",
    }

    for stock in stock_list:
        if not isinstance(stock, dict):
            normalized_list.append(stock)
            continue

        normalized_stock = {}
        for key, value in stock.items():
            # 应用字段映射
            standard_key = field_mapping.get(key, key)
            normalized_stock[standard_key] = value

        # 确保关键字段存在
        required_fields = ["symbol", "name", "industry", "area", "market", "list_date"]
        for field in required_fields:
            if field not in normalized_stock:
                if field == "symbol":
                    normalized_stock[field] = "N/A"
                elif field == "name":
                    normalized_stock[field] = "未命名"
                elif field in ["industry", "area", "market"]:
                    normalized_stock[field] = "N/A"
                elif field == "list_date":
                    normalized_stock[field] = None

        normalized_list.append(normalized_stock)

    return normalized_list


def normalize_indicator_data_format(indicator_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    标准化技术指标数据格式

    Args:
        indicator_data: 原始技术指标数据

    Returns:
        标准化后的技术指标数据
    """
    if not isinstance(indicator_data, dict):
        return indicator_data

    normalized_data = indicator_data.copy()

    # 标准化指标名称和数据格式
    if "indicators" in normalized_data:
        for i, indicator in enumerate(normalized_data["indicators"]):
            if isinstance(indicator, dict):
                # 标准化指标输出格式
                if "values" in indicator:
                    for j, output in enumerate(indicator["values"]):
                        if isinstance(output, dict):
                            # 确保输出名称标准化
                            if "output_name" not in output:
                                output["output_name"] = f"output_{j}"
                            if "values" not in output:
                                output["values"] = []

    return normalized_data


# 测试函数
def test_format_normalization():
    """测试数据格式标准化功能"""
    print("测试数据格式标准化...")

    # 创建测试数据
    test_data = pd.DataFrame(
        {
            "stock_code": ["000001.SZ", "600000.SH"],
            "stock_name": ["平安银行", "浦发银行"],
            "sector": ["金融", "金融"],
            "location": ["深圳", "上海"],
            "exchange": ["SZ", "SH"],
            "listing_date": ["2025-01-01", "2025-01-02"],
        }
    )

    print("原始数据:")
    print(test_data)
    print("\n原始列名:", list(test_data.columns))

    # 标准化
    normalized_data = normalize_stock_data_format(test_data)

    print("\n标准化后数据:")
    print(normalized_data)
    print("\n标准化后列名:", list(normalized_data.columns))

    print("\n数据格式标准化测试完成!")


if __name__ == "__main__":
    test_format_normalization()
