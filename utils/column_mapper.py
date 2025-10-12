"""
统一列名管理器
提供DataFrame列名的标准化映射功能

作用：
- 统一不同数据源的列名格式
- 支持中英文列名转换
- 提供标准的列名映射规则
- 简化数据源适配器的列名处理逻辑

功能：
- 标准化DataFrame列名
- 中英文列名互转
- 自动识别和映射常见列名
- 支持自定义列名映射规则
"""
import pandas as pd
from typing import Dict, Union, Optional
import warnings


class ColumnMapper:
    """统一列名管理器"""
    
    # 标准英文列名映射表
    STANDARD_EN_MAPPING = {
        # 基本OHLCV数据
        "日期": "date",
        "时间": "date",
        "trade_date": "date",
        "trading_date": "date",
        "股票代码": "symbol",
        "代码": "symbol",
        "code": "symbol",
        "ts_code": "symbol",
        "股票名称": "name",
        "名称": "name",
        "stock_name": "name",
        "开盘": "open",
        "开盘价": "open",
        "今开": "open",
        "open_price": "open",
        "收盘": "close",
        "收盘价": "close",
        "最新价": "close",  # 实时行情中的最新价对应收盘价
        "close_price": "close",
        "最高": "high",
        "最高价": "high",
        "high_price": "high",
        "最低": "low",
        "最低价": "low",
        "low_price": "low",
        "成交量": "volume",
        "vol": "volume",
        "成交额": "amount",
        "成交金额": "amount",
        "turnover": "amount",
        "amt": "amount",
        
        # 技术指标
        "涨跌幅": "pct_chg",
        "涨跌": "pct_chg",
        "pct_change": "pct_chg",
        "change_pct": "pct_chg",
        "涨跌额": "change",
        "change_amount": "change",
        "振幅": "amplitude",
        "换手率": "turnover_rate",
        "turn": "turnover_rate",
        "turnover": "turnover_rate",
        
        # 市值相关
        "总市值": "total_mv",
        "流通市值": "circ_mv", 
        "市盈率": "pe",
        "市净率": "pb",
        "市销率": "ps",
        
        # 财务数据
        "总股本": "total_share",
        "流通股": "float_share",
        "总资产": "total_assets",
        "净资产": "net_assets",
        "营业收入": "revenue",
        "净利润": "net_profit",
        
        # 指数相关
        "权重": "weight",
        "成分券代码": "component_code",
        "品种代码": "component_code",
        
        # 其他
        "行业": "industry",
        "地区": "area",
        "上市日期": "list_date",
        "退市日期": "delist_date"
    }
    
    # 标准中文列名映射表  
    STANDARD_CN_MAPPING = {
        "date": "日期",
        "symbol": "股票代码",
        "name": "股票名称",
        "open": "开盘价",
        "close": "收盘价", 
        "high": "最高价",
        "low": "最低价",
        "volume": "成交量",
        "amount": "成交额",
        "pct_chg": "涨跌幅",
        "change": "涨跌额",
        "amplitude": "振幅",
        "turnover_rate": "换手率",
        "total_mv": "总市值",
        "circ_mv": "流通市值",
        "pe": "市盈率",
        "pb": "市净率",
        "ps": "市销率",
        "total_share": "总股本",
        "float_share": "流通股",
        "total_assets": "总资产", 
        "net_assets": "净资产",
        "revenue": "营业收入",
        "net_profit": "净利润",
        "weight": "权重",
        "component_code": "成分券代码",
        "industry": "行业",
        "area": "地区",
        "list_date": "上市日期",
        "delist_date": "退市日期"
    }
    
    @classmethod
    def standardize_columns(cls, df: pd.DataFrame, 
                           target_lang: str = "en",
                           custom_mapping: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        标准化DataFrame列名
        
        Args:
            df: 输入的DataFrame
            target_lang: 目标语言，"en"(英文)或"cn"(中文)
            custom_mapping: 自定义映射规则，会覆盖默认规则
            
        Returns:
            pd.DataFrame: 列名标准化后的DataFrame
        """
        if df.empty:
            return df
        
        # 选择映射表
        if target_lang.lower() == "en":
            mapping = cls.STANDARD_EN_MAPPING.copy()
        elif target_lang.lower() == "cn":
            mapping = cls.STANDARD_CN_MAPPING.copy()
        else:
            raise ValueError(f"不支持的目标语言: {target_lang}，请使用 'en' 或 'cn'")
        
        # 应用自定义映射
        if custom_mapping:
            mapping.update(custom_mapping)
        
        # 执行列名映射
        df_copy = df.copy()
        rename_dict = {}
        
        for old_col in df_copy.columns:
            # 尝试直接匹配
            if old_col in mapping:
                rename_dict[old_col] = mapping[old_col]
            # 尝试小写匹配
            elif old_col.lower() in mapping:
                rename_dict[old_col] = mapping[old_col.lower()]
            # 尝试去除空格和特殊字符后匹配
            else:
                clean_col = old_col.replace(" ", "").replace("_", "").replace("-", "").lower()
                for key, value in mapping.items():
                    if clean_col == key.replace(" ", "").replace("_", "").replace("-", "").lower():
                        rename_dict[old_col] = value
                        break
        
        # 应用重命名
        if rename_dict:
            df_copy = df_copy.rename(columns=rename_dict)
            print(f"列名映射完成: {rename_dict}")
        
        return df_copy
    
    @classmethod
    def to_english(cls, df: pd.DataFrame, 
                   custom_mapping: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        将DataFrame列名转换为英文
        
        Args:
            df: 输入的DataFrame
            custom_mapping: 自定义映射规则
            
        Returns:
            pd.DataFrame: 英文列名的DataFrame
        """
        return cls.standardize_columns(df, target_lang="en", custom_mapping=custom_mapping)
    
    @classmethod
    def to_chinese(cls, df: pd.DataFrame,
                   custom_mapping: Optional[Dict[str, str]] = None) -> pd.DataFrame:
        """
        将DataFrame列名转换为中文
        
        Args:
            df: 输入的DataFrame  
            custom_mapping: 自定义映射规则
            
        Returns:
            pd.DataFrame: 中文列名的DataFrame
        """
        return cls.standardize_columns(df, target_lang="cn", custom_mapping=custom_mapping)
    
    @classmethod
    def get_standard_columns(cls, data_type: str = "stock_daily", lang: str = "en") -> list:
        """
        获取特定数据类型的标准列名
        
        Args:
            data_type: 数据类型，如"stock_daily", "index_daily", "stock_basic"等
            lang: 语言，"en"或"cn"
            
        Returns:
            list: 标准列名列表
        """
        standard_columns = {
            "stock_daily": {
                "en": ["date", "symbol", "open", "close", "high", "low", "volume", "amount", "pct_chg", "change"],
                "cn": ["日期", "股票代码", "开盘价", "收盘价", "最高价", "最低价", "成交量", "成交额", "涨跌幅", "涨跌额"]
            },
            "index_daily": {
                "en": ["date", "symbol", "open", "close", "high", "low", "volume", "amount"],
                "cn": ["日期", "指数代码", "开盘价", "收盘价", "最高价", "最低价", "成交量", "成交额"]
            },
            "stock_basic": {
                "en": ["symbol", "name", "industry", "area", "pe", "pb", "total_mv", "circ_mv"],
                "cn": ["股票代码", "股票名称", "行业", "地区", "市盈率", "市净率", "总市值", "流通市值"]
            }
        }
        
        return standard_columns.get(data_type, {}).get(lang, [])
    
    @classmethod
    def validate_columns(cls, df: pd.DataFrame, 
                        required_columns: list,
                        strict: bool = False) -> tuple:
        """
        验证DataFrame是否包含必需的列
        
        Args:
            df: 输入的DataFrame
            required_columns: 必需的列名列表
            strict: 是否严格模式（必须完全匹配）
            
        Returns:
            tuple: (是否通过验证, 缺失的列, 额外的列)
        """
        current_columns = set(df.columns)
        required_set = set(required_columns)
        
        missing_columns = required_set - current_columns
        extra_columns = current_columns - required_set if strict else set()
        
        is_valid = len(missing_columns) == 0 and (not strict or len(extra_columns) == 0)
        
        return is_valid, list(missing_columns), list(extra_columns)
    
    @classmethod
    def add_custom_mapping(cls, custom_mapping: Dict[str, str], target_lang: str = "en"):
        """
        添加自定义映射规则到默认映射表
        
        Args:
            custom_mapping: 自定义映射字典
            target_lang: 目标语言
        """
        if target_lang.lower() == "en":
            cls.STANDARD_EN_MAPPING.update(custom_mapping)
        elif target_lang.lower() == "cn":
            cls.STANDARD_CN_MAPPING.update(custom_mapping)
        else:
            raise ValueError(f"不支持的目标语言: {target_lang}")
        
        print(f"已添加自定义映射规则到{target_lang}映射表: {custom_mapping}")


# 便捷函数
def standardize_dataframe(df: pd.DataFrame, 
                         target_lang: str = "en",
                         custom_mapping: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    便捷函数：标准化DataFrame列名
    
    Args:
        df: 输入的DataFrame
        target_lang: 目标语言，"en"或"cn"
        custom_mapping: 自定义映射规则
        
    Returns:
        pd.DataFrame: 标准化后的DataFrame
    """
    return ColumnMapper.standardize_columns(df, target_lang, custom_mapping)


def to_english_columns(df: pd.DataFrame) -> pd.DataFrame:
    """便捷函数：转换为英文列名"""
    return ColumnMapper.to_english(df)


def to_chinese_columns(df: pd.DataFrame) -> pd.DataFrame:
    """便捷函数：转换为中文列名"""
    return ColumnMapper.to_chinese(df)


# 测试代码
if __name__ == "__main__":
    # 创建测试数据
    test_data = pd.DataFrame({
        "日期": ["2023-08-01", "2023-08-02"],
        "股票代码": ["600000", "600000"],
        "开盘": [10.0, 10.5],
        "收盘": [10.2, 10.8],
        "最高": [10.5, 11.0],
        "最低": [9.8, 10.2],
        "成交量": [1000000, 1200000],
        "涨跌幅": [1.5, 2.8]
    })
    
    print("原始数据:")
    print(test_data)
    
    print("\n转换为英文列名:")
    en_data = to_english_columns(test_data)
    print(en_data)
    
    print("\n转换为中文列名:")
    cn_data = to_chinese_columns(en_data)
    print(cn_data)
    
    print("\n标准列名验证:")
    required_cols = ColumnMapper.get_standard_columns("stock_daily", "en")
    is_valid, missing, extra = ColumnMapper.validate_columns(en_data, required_cols)
    print(f"验证结果: {is_valid}, 缺失列: {missing}, 额外列: {extra}")