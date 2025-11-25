#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - Akshare数据访问器

专门处理从akshare获取的股票数据和市场信息

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-11-25
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Union, Tuple, Any
import logging
import time

# 导入基础模块
from src.storage.access.base import (
    IDataAccessLayer, 
    get_database_name_from_classification,
    normalize_dataframe,
    DataClassification
)
from src.monitoring.monitoring_database import MonitoringDatabase

logger = logging.getLogger("MyStocksAkshareAccess")


class AkshareDataAccess(IDataAccessLayer):
    """Akshare数据访问器 - 从akshare获取股票数据和市场信息"""

    def __init__(self, monitoring_db: MonitoringDatabase):
        """
        初始化Akshare数据访问器
        
        Args:
            monitoring_db: 监控数据库实例
        """
        super().__init__(monitoring_db)
        self.rate_limit = 0.2  # 请求间隔（秒），防止被限流
        self.last_request_time = 0

    def save_data(
        self,
        data: pd.DataFrame,
        classification: DataClassification,
        table_name: str = None,
        **kwargs,
    ) -> bool:
        """
        保存从akshare获取的数据到数据库
        
        Args:
            data: 从akshare获取的数据DataFrame
            classification: 数据分类
            table_name: 表名（可选）
            **kwargs: 其他参数
            
        Returns:
            bool: 保存是否成功
        """
        # 记录操作开始
        actual_table_name = table_name or self._get_default_table_name(classification)
        operation_id = self.monitoring_db.log_operation_start(
            actual_table_name,
            "AKSHARE",
            get_database_name_from_classification(classification),
            "INSERT",
        )

        try:
            # 数据预处理
            processed_data = self._preprocess_akshare_data(data, classification)

            # 标准化数据格式
            normalized_data = normalize_dataframe(processed_data)

            # 根据分类确定要保存到的数据库
            target_db = self._get_target_database(classification)

            if target_db == "TDengine":
                from src.storage.access.tdengine import TDengineDataAccess
                tdengine_access = TDengineDataAccess(self.monitoring_db)
                success = tdengine_access.save_data(normalized_data, classification, actual_table_name, **kwargs)
            else:  # PostgreSQL
                from src.storage.access.postgresql import PostgreSQLDataAccess
                postgresql_access = PostgreSQLDataAccess(self.monitoring_db)
                success = postgresql_access.save_data(normalized_data, classification, actual_table_name, **kwargs)

            if success:
                self.monitoring_db.log_operation_result(operation_id, True, len(processed_data))
                logger.info(f"保存akshare数据成功: {actual_table_name}, {len(processed_data)}条记录")
            else:
                self.monitoring_db.log_operation_result(operation_id, False, 0, "保存失败")

            return success

        except Exception as e:
            error_msg = f"保存akshare数据失败: {e}"
            self.monitoring_db.log_operation_result(operation_id, False, 0, error_msg)
            logger.error(error_msg)
            return False

    def load_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        从akshare获取数据
        
        Args:
            classification: 数据分类
            table_name: 表名（可选）
            filters: 过滤条件
            **kwargs: 其他参数
            
        Returns:
            pd.DataFrame: 从akshare获取的数据
        """
        # 记录操作开始
        actual_table_name = table_name or self._get_default_table_name(classification)
        operation_id = self.monitoring_db.log_operation_start(
            actual_table_name,
            "AKSHARE",
            "NONE",  # 直接从akshare获取，没有特定的数据库
            "SELECT",
        )

        try:
            # 应用请求频率限制
            self._apply_rate_limit()

            # 根据分类获取数据
            if classification == DataClassification.STOCK_BASIC_INFO:
                data = self._fetch_stock_basic_info()
            elif classification == DataClassification.DAILY_KLINE:
                symbol = kwargs.get("symbol", "000001")
                start_date = kwargs.get("start_date", "2024-01-01")
                end_date = kwargs.get("end_date", datetime.now().strftime("%Y-%m-%d"))
                data = self._fetch_daily_kline(symbol, start_date, end_date)
            elif classification == DataClassification.REALTIME_QUOTES:
                symbols = kwargs.get("symbols", ["000001", "600000"])
                data = self._fetch_realtime_quotes(symbols)
            else:
                # 通用数据获取
                data = self._fetch_generic_data(classification, filters, **kwargs)

            # 后处理
            processed_data = self._postprocess_akshare_data(data, classification)

            self.monitoring_db.log_operation_result(operation_id, True, len(processed_data))
            logger.info(f"从akshare获取数据成功: {actual_table_name}, {len(processed_data)}条记录")

            return processed_data

        except Exception as e:
            error_msg = f"从akshare获取数据失败: {e}"
            self.monitoring_db.log_operation_result(operation_id, False, 0, error_msg)
            logger.error(error_msg)
            return pd.DataFrame()

    def update_data(
        self,
        data: pd.DataFrame,
        classification: DataClassification,
        table_name: str = None,
        key_columns: List[str] = None,
        **kwargs,
    ) -> bool:
        """
        更新数据
        
        Args:
            data: 数据DataFrame
            classification: 数据分类
            table_name: 表名（可选）
            key_columns: 主键列
            **kwargs: 其他参数
            
        Returns:
            bool: 更新是否成功
        """
        # 记录操作开始
        actual_table_name = table_name or self._get_default_table_name(classification)
        operation_id = self.monitoring_db.log_operation_start(
            actual_table_name,
            "AKSHARE",
            get_database_name_from_classification(classification),
            "UPDATE",
        )

        try:
            # 实际上akshare是数据源，我们通常不从它更新数据
            # 这里实现的是更新数据库中与akshare数据相关的记录
            
            # 确定目标数据库
            target_db = self._get_target_database(classification)
            
            # 数据预处理
            processed_data = self._preprocess_akshare_data(data, classification)
            normalized_data = normalize_dataframe(processed_data)
            
            # 根据数据库类型使用相应的访问器
            if target_db == "TDengine":
                from src.storage.access.tdengine import TDengineDataAccess
                tdengine_access = TDengineDataAccess(self.monitoring_db)
                success = tdengine_access.update_data(normalized_data, classification, actual_table_name, key_columns, **kwargs)
            else:  # PostgreSQL
                from src.storage.access.postgresql import PostgreSQLDataAccess
                postgresql_access = PostgreSQLDataAccess(self.monitoring_db)
                success = postgresql_access.update_data(normalized_data, classification, actual_table_name, key_columns, **kwargs)

            if success:
                self.monitoring_db.log_operation_result(operation_id, True, len(processed_data))
                logger.info(f"更新数据成功: {actual_table_name}, {len(processed_data)}条记录")
            else:
                self.monitoring_db.log_operation_result(operation_id, False, 0, "更新失败")

            return success

        except Exception as e:
            error_msg = f"更新数据失败: {e}"
            self.monitoring_db.log_operation_result(operation_id, False, 0, error_msg)
            logger.error(error_msg)
            return False

    def delete_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> bool:
        """
        删除数据
        
        Args:
            classification: 数据分类
            table_name: 表名（可选）
            filters: 过滤条件
            **kwargs: 其他参数
            
        Returns:
            bool: 删除是否成功
        """
        # 记录操作开始
        actual_table_name = table_name or self._get_default_table_name(classification)
        operation_id = self.monitoring_db.log_operation_start(
            actual_table_name,
            "AKSHARE",
            get_database_name_from_classification(classification),
            "DELETE",
        )

        try:
            # akshare是数据源，我们通常不从中删除数据
            # 这里实现的是删除数据库中与akshare数据相关的记录
            
            # 实际删除操作应该委托给相应的数据库访问器
            target_db = self._get_target_database(classification)
            
            if target_db == "TDengine":
                from src.storage.access.tdengine import TDengineDataAccess
                tdengine_access = TDengineDataAccess(self.monitoring_db)
                success = tdengine_access.delete_data(classification, actual_table_name, filters, **kwargs)
            else:  # PostgreSQL
                from src.storage.access.postgresql import PostgreSQLDataAccess
                postgresql_access = PostgreSQLDataAccess(self.monitoring_db)
                success = postgresql_access.delete_data(classification, actual_table_name, filters, **kwargs)

            if success:
                self.monitoring_db.log_operation_result(operation_id, True, 0)
                logger.info(f"删除数据成功: {actual_table_name}")
            else:
                self.monitoring_db.log_operation_result(operation_id, False, 0, "删除失败")

            return success

        except Exception as e:
            error_msg = f"删除数据失败: {e}"
            self.monitoring_db.log_operation_result(operation_id, False, 0, error_msg)
            logger.error(error_msg)
            return False

    def _get_default_table_name(self, classification: DataClassification) -> str:
        """根据数据分类获取默认表名"""
        table_mapping = {
            DataClassification.STOCK_BASIC_INFO: "stock_basic_info",
            DataClassification.DAILY_KLINE: "daily_kline",
            DataClassification.MINUTE_KLINE: "minute_kline",
            DataClassification.REALTIME_QUOTES: "realtime_quotes",
            DataClassification.TECHNICAL_INDICATORS: "technical_indicators",
            DataClassification.QUANTITATIVE_FACTORS: "quantitative_factors",
            DataClassification.MODEL_OUTPUTS: "model_outputs",
            DataClassification.TRADING_SIGNALS: "trading_signals",
            DataClassification.ORDER_RECORDS: "order_records",
            DataClassification.TRANSACTION_RECORDS: "transaction_records",
            DataClassification.POSITION_RECORDS: "position_records",
            DataClassification.ACCOUNT_FUNDS: "account_funds",
        }
        return table_mapping.get(classification, "unknown_table")

    def _get_target_database(self, classification: DataClassification) -> str:
        """
        根据数据分类确定目标数据库
        
        Args:
            classification: 数据分类
            
        Returns:
            数据库名称: "TDengine" 或 "PostgreSQL"
        """
        # 根据数据分类特性决定存储数据库
        if classification in [
            DataClassification.TICK_DATA,
            DataClassification.MINUTE_KLINE,
            DataClassification.REALTIME_QUOTES
        ]:
            return "TDengine"
        else:
            return "PostgreSQL"

    def _apply_rate_limit(self):
        """应用请求频率限制"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.rate_limit:
            sleep_time = self.rate_limit - time_since_last_request
            logger.info(f"应用请求频率限制，休眠 {sleep_time:.2f} 秒")
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()

    def _fetch_stock_basic_info(self) -> pd.DataFrame:
        """获取股票基本信息"""
        try:
            import akshare as ak
            
            # 获取股票基本信息
            stock_info = ak.stock_info_a_code_name()
            
            # 处理数据格式
            stock_info = self._process_stock_basic_info(stock_info)
            
            return stock_info
            
        except Exception as e:
            logger.error(f"获取股票基本信息失败: {e}")
            return pd.DataFrame()

    def _process_stock_basic_info(self, stock_info: pd.DataFrame) -> pd.DataFrame:
        """处理股票基本信息数据"""
        if stock_info.empty:
            return stock_info
        
        # 重命名列
        column_mapping = {
            "代码": "symbol",
            "名称": "name",
            "现价": "price",
            "涨跌": "change",
            "涨跌幅": "change_pct",
            "今开": "open",
            "最高": "high",
            "最低": "low",
            "昨收": "pre_close",
            "成交量": "volume",
            "成交额": "amount",
            "流通市值": "market_cap",
            "总市值": "total_cap",
            "换手率": "turnover",
            "市净率": "pb",
            "动态市盈率": "pe",
            "静态市盈率": "pe_ttm",
            "量比": "volume_ratio",
        }
        
        stock_info = stock_info.rename(columns=column_mapping)
        
        # 添加时间戳
        stock_info["fetch_timestamp"] = datetime.now()
        
        return stock_info

    def _fetch_daily_kline(self, symbol: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取日K线数据"""
        try:
            import akshare as ak
            
            # 确保symbol格式正确（如果是6位数字，不需要修改）
            if len(symbol) == 6 and symbol.isdigit():
                # 添加市场前缀
                if symbol.startswith(('6',)):
                    symbol = f"sh{symbol}"
                else:
                    symbol = f"sz{symbol}"
            
            # 获取日K线数据
            kline_data = ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                                            start_date=start_date.replace('-', ''), 
                                            end_date=end_date.replace('-', ''), 
                                            adjust="qfq")  # 前复权
            
            # 处理数据格式
            kline_data = self._process_daily_kline_data(kline_data, symbol)
            
            return kline_data
            
        except Exception as e:
            logger.error(f"获取日K线数据失败: {e}")
            return pd.DataFrame()

    def _process_daily_kline_data(self, kline_data: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """处理日K线数据"""
        if kline_data.empty:
            return kline_data
        
        # 重命名列
        column_mapping = {
            "日期": "trade_date",
            "开盘": "open",
            "收盘": "close",
            "最高": "high",
            "最低": "low",
            "成交量": "volume",
            "成交额": "amount",
            "振幅": "amplitude",
            "涨跌幅": "change_pct",
            "涨跌额": "change",
            "换手率": "turnover",
        }
        
        kline_data = kline_data.rename(columns=column_mapping)
        
        # 确保symbol列存在
        if "symbol" not in kline_data.columns:
            kline_data["symbol"] = symbol
        
        # 添加时间戳
        kline_data["fetch_timestamp"] = datetime.now()
        
        return kline_data

    def _fetch_realtime_quotes(self, symbols: List[str]) -> pd.DataFrame:
        """获取实时行情数据"""
        try:
            import akshare as ak
            
            # 获取实时行情数据
            quote_data = ak.stock_zh_a_spot_em()
            
            # 过滤出指定股票
            if symbols:
                if symbols[0].isdigit():  # 如果是数字代码
                    # 转换为akshare使用的代码格式
                    formatted_symbols = []
                    for symbol in symbols:
                        if len(symbol) == 6:
                            if symbol.startswith('6'):
                                formatted_symbols.append(f"sh{symbol}")
                            else:
                                formatted_symbols.append(f"sz{symbol}")
                        else:
                            formatted_symbols.append(symbol)
                    
                    symbols = formatted_symbols
                
                quote_data = quote_data[quote_data['代码'].isin(symbols)]
            
            # 处理数据格式
            quote_data = self._process_realtime_quote_data(quote_data)
            
            return quote_data
            
        except Exception as e:
            logger.error(f"获取实时行情数据失败: {e}")
            return pd.DataFrame()

    def _process_realtime_quote_data(self, quote_data: pd.DataFrame) -> pd.DataFrame:
        """处理实时行情数据"""
        if quote_data.empty:
            return quote_data
        
        # 重命名列
        column_mapping = {
            "代码": "symbol",
            "名称": "name",
            "最新价": "price",
            "涨跌额": "change",
            "涨跌幅": "change_pct",
            "今开": "open",
            "最高": "high",
            "最低": "low",
            "今收": "pre_close",
            "成交量": "volume",
            "成交额": "amount",
            "换手率": "turnover",
            "涨跌幅": "change_pct",  # 注意这个字段可能有重复
            "涨跌额": "change",
        }
        
        quote_data = quote_data.rename(columns=column_mapping)
        
        # 添加时间戳
        quote_data["fetch_timestamp"] = datetime.now()
        
        return quote_data

    def _fetch_generic_data(self, classification: DataClassification, filters: Dict = None, **kwargs) -> pd.DataFrame:
        """
        获取通用数据
        
        Args:
            classification: 数据分类
            filters: 过滤条件
            **kwargs: 其他参数
            
        Returns:
            pd.DataFrame: 数据
        """
        try:
            # 根据不同的分类实现不同的数据获取逻辑
            if classification == DataClassification.TECHNICAL_INDICATORS:
                # 技术指标数据
                return self._fetch_technical_indicators(kwargs.get("symbol", "000001"), kwargs.get("start_date"), kwargs.get("end_date"))
            elif classification == DataClassification.QUANTITATIVE_FACTORS:
                # 量化因子数据
                return self._fetch_quantitative_factors(kwargs.get("symbol", "000001"), kwargs.get("start_date"), kwargs.get("end_date"))
            else:
                # 默认返回空数据
                logger.warning(f"未实现的通用数据获取: {classification}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"获取通用数据失败: {e}")
            return pd.DataFrame()

    def _fetch_technical_indicators(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取技术指标数据"""
        try:
            import akshare as ak
            
            # 确保symbol格式正确
            if len(symbol) == 6 and symbol.isdigit():
                if symbol.startswith('6'):
                    symbol = f"sh{symbol}"
                else:
                    symbol = f"sz{symbol}"
            
            # 获取K线数据，然后计算技术指标
            kline_data = ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                                            start_date=(start_date or "20240101").replace('-', ''), 
                                            end_date=(end_date or datetime.now().strftime('%Y%m%d')), 
                                            adjust="qfq")
            
            # 计算技术指标
            if not kline_data.empty:
                kline_data["ma5"] = kline_data["收盘"].rolling(window=5).mean()
                kline_data["ma10"] = kline_data["收盘"].rolling(window=10).mean()
                kline_data["ma20"] = kline_data["收盘"].rolling(window=20).mean()
                
                # 计算RSI
                delta = kline_data["收盘"].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                kline_data["rsi"] = 100 - (100 / (1 + rs))
                
                # 添加symbol列
                if len(symbol) >= 3:
                    symbol_code = symbol[2:]  # 去掉市场前缀
                    kline_data["symbol"] = symbol_code
            
            return kline_data
            
        except Exception as e:
            logger.error(f"获取技术指标数据失败: {e}")
            return pd.DataFrame()

    def _fetch_quantitative_factors(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """获取量化因子数据"""
        try:
            import akshare as ak
            
            # 确保symbol格式正确
            if len(symbol) == 6 and symbol.isdigit():
                if symbol.startswith('6'):
                    symbol = f"sh{symbol}"
                else:
                    symbol = f"sz{symbol}"
            
            # 获取K线数据
            kline_data = ak.stock_zh_a_hist(symbol=symbol, period="daily", 
                                            start_date=(start_date or "20240101").replace('-', ''), 
                                            end_date=(end_date or datetime.now().strftime('%Y%m%d')), 
                                            adjust="qfq")
            
            # 计算量化因子
            if not kline_data.empty:
                # 计算价格动量因子
                kline_data["momentum_5"] = kline_data["收盘"] / kline_data["收盘"].shift(5) - 1
                kline_data["momentum_10"] = kline_data["收盘"] / kline_data["收盘"].shift(10) - 1
                
                # 计算波动率因子
                kline_data["volatility_10"] = kline_data["收盘"].pct_change().rolling(window=10).std()
                
                # 计算成交量因子
                kline_data["volume_ma5"] = kline_data["成交量"].rolling(window=5).mean()
                kline_data["volume_ratio"] = kline_data["成交量"] / kline_data["volume_ma5"]
                
                # 添加symbol列
                if len(symbol) >= 3:
                    symbol_code = symbol[2:]  # 去掉市场前缀
                    kline_data["symbol"] = symbol_code
            
            return kline_data
            
        except Exception as e:
            logger.error(f"获取量化因子数据失败: {e}")
            return pd.DataFrame()

    def _preprocess_akshare_data(self, data: pd.DataFrame, classification: DataClassification) -> pd.DataFrame:
        """预处理akshare数据"""
        processed_data = data.copy()
        
        # 根据数据分类进行特定预处理
        if classification == DataClassification.STOCK_BASIC_INFO:
            # 确保symbol列格式统一
            if "symbol" in processed_data.columns:
                # 去除市场前缀，统一格式
                processed_data["symbol"] = processed_data["symbol"].str.replace(r"^(sh|sz)", "", regex=True)
        
        return processed_data

    def _postprocess_akshare_data(self, data: pd.DataFrame, classification: DataClassification) -> pd.DataFrame:
        """后处理akshare数据"""
        if data.empty:
            return data
        
        # 确保时间戳列存在
        timestamp_columns = ["fetch_timestamp", "ts", "timestamp", "trade_date", "date"]
        has_timestamp = any(col in data.columns for col in timestamp_columns)
        
        if not has_timestamp:
            # 添加当前时间戳
            data["fetch_timestamp"] = datetime.now()
        
        # 标准化数据格式
        processed_data = normalize_dataframe(data)
        
        return processed_data

