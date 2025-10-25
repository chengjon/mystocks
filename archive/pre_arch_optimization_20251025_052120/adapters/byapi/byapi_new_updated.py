#!/usr/bin/env python
# -*- coding: utf-8 -*-
# BYAPI接口管理类 - 专业股票数据获取工具
# 功能介绍：
# 1. 提供统一的接口管理，支持49个股票市场API调用
# 2. 支持中文接口名称调用，自动映射到英文方法名
# 3. 智能数据格式转换，自动返回中文列名的DataFrame
# 4. 内置请求频率控制和异常处理机制，确保数据获取稳定可靠
# 5. 完整的日志记录系统，便于调试和问题追踪

# 调用示例：
# 1. 实例化并获取股票列表
#    >>> byapi = ByapiInfo('your_licence')
#    >>> stock_data = byapi.stock_list()  # 直接通过方法调用
#    >>> stock_data = byapi("股票列表")   # 通过中文名称调用

# 2. 获取财务数据
#    >>> balance_sheet = byapi.balance_sheet(stock_code='000001')  # 资产负债表
#    >>> income_data = byapi("利润表", stock_code='000001')         # 通过中文名称调用

# 3. 获取行情数据
#    >>> realtime_data = byapi.realtime_quotes(stock_code='000001')  # 实时行情
#    >>> fund_flow = byapi("资金流向数据", stock_code='000001')      # 资金流向
#api.get_supported_apis()
#api.stock_list(col_name=True)
#api.get_api_documentation("股票列表")
#api.get_api_links()
#api.get_tables("股票列表")
#api.get_tables("股票列表", export='df')
#api.get_tables("股票列表", export='dict')


import requests
import time
import re
import pandas as pd
import json
from typing import Dict, Any, Optional, List
import os
from loguru import logger

# 配置loguru日志记录器
logger.remove()  # 移除默认的控制台输出
# 添加文件日志
logger.add("byapi_info.log", 
           level="DEBUG",
           format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {message}",
           rotation="10 MB",  # 文件达到10MB时旋转
           retention="7 days",  # 保留7天的日志
           encoding="utf-8")
# 添加控制台日志（只显示INFO及以上级别）
logger.add(lambda msg: print(msg, end=""), 
            level="INFO",
            format="{time:HH:mm:ss} | {level} | {message}")

def json_to_dict(json_data):
    """
    将JSON格式的headers数据转换为字段信息字典
    
    Args:
        json_data: JSON格式的headers数据，可能是一个列表的字典，也可能是扁平的列表
    
    Returns:
        dict: 转换后的字段信息字典，key为字段名，value为包含字段描述、数据类型等信息的字典
    
    Raises:
        TypeError: 当json_data不是列表时抛出
        Exception: 其他转换错误
    """
    logger.debug(f"开始将JSON数据转换为字典，数据类型: {type(json_data)}, 长度: {len(json_data) if isinstance(json_data, list) else '非列表'}")
    
    try:
        if not isinstance(json_data, list):
            logger.error(f"JSON数据不是列表类型，而是: {type(json_data)}")
            raise TypeError(f"JSON数据必须是列表类型，而不是: {type(json_data)}")
        
        field_dict = {}
        
        # 检查是否是扁平列表格式（如[字段名称, 数据类型, 字段说明, dm, string, 股票代码...]）
        # 识别特征：第一个元素是'字段名称'且长度大于3
        if len(json_data) > 3 and json_data[0] == '字段名称' and json_data[1] == '数据类型' and json_data[2] == '字段说明':
            logger.debug("识别到扁平列表格式的headers数据，进行特殊处理")
            # 跳过前3个标题元素
            for i in range(3, len(json_data), 3):
                # 确保有足够的元素
                if i + 2 < len(json_data):
                    field_name = json_data[i]
                    data_type = json_data[i + 1]
                    description = json_data[i + 2]
                    
                    field_info = {
                        'description': description,
                        'data_type': data_type,
                        'required': False
                    }
                    
                    field_dict[field_name] = field_info
                    logger.debug(f"成功解析字段: {field_name}, 数据类型: {data_type}")
        else:
            # 处理标准的字典列表格式
            for item in json_data:
                if not isinstance(item, dict):
                    logger.warning(f"跳过非字典项: {item}")
                    continue
                
                # 获取字段名（从'key'或'column'字段）
                field_name = item.get('key') or item.get('column')
                if not field_name:
                    logger.warning(f"跳过没有key或column字段的项: {item}")
                    continue
                
                # 构建字段信息字典
                field_info = {
                    'description': item.get('title', ''),
                    'data_type': item.get('type', 'string'),
                    'required': item.get('required', False)
                }
                
                # 添加其他可能的字段属性
                if 'example' in item:
                    field_info['example'] = item.get('example')
                if 'format' in item:
                    field_info['format'] = item.get('format')
                if 'enum' in item:
                    field_info['enum'] = item.get('enum')
                
                field_dict[field_name] = field_info
        
        logger.debug(f"成功将JSON数据转换为字典，字段数量: {len(field_dict)}")
        return field_dict
    except Exception as e:
        logger.error(f"JSON数据转换为字典时出错: {str(e)}")
        raise Exception(f"JSON数据转换为字典时出错: {str(e)}")


def dict_to_df(field_dict):
    """
    将字段信息字典转换为pandas DataFrame
    
    Args:
        field_dict: 字段信息字典，key为字段名，value为包含字段描述、数据类型等信息的字典
    
    Returns:
        pandas.DataFrame: 转换后的DataFrame，每行代表一个字段的信息
    
    Raises:
        TypeError: 当field_dict不是字典时抛出
        ImportError: 当pandas库不可用时抛出
        Exception: 其他转换错误
    """
    logger.debug(f"开始将字段字典转换为DataFrame，字段数量: {len(field_dict) if isinstance(field_dict, dict) else '非字典'}")
    
    try:
        if not isinstance(field_dict, dict):
            logger.error(f"字段数据不是字典类型，而是: {type(field_dict)}")
            raise TypeError(f"字段数据必须是字典类型，而不是: {type(field_dict)}")
        
        # 确保pandas库可用
        try:
            import pandas as pd
        except ImportError as e:
            logger.error(f"pandas库不可用: {str(e)}")
            raise ImportError(f"pandas库不可用: {str(e)}")
        
        # 转换字典为DataFrame
        df_data = []
        for field_name, field_info in field_dict.items():
            if not isinstance(field_info, dict):
                logger.warning(f"跳过非字典的字段信息: {field_name} - {field_info}")
                continue
            
            # 创建一行数据
            row_data = {'字段名': field_name}
            row_data.update(field_info)
            df_data.append(row_data)
        
        if not df_data:
            logger.warning("没有有效的字段信息可以转换为DataFrame")
            return pd.DataFrame(columns=['字段名', 'description', 'data_type', 'required'])
        
        # 创建DataFrame并重新排列列顺序
        df = pd.DataFrame(df_data)
        
        # 确保重要的列存在
        important_columns = ['字段名', 'description', 'data_type', 'required']
        existing_columns = df.columns.tolist()
        
        # 先添加重要的列
        columns_order = []
        for col in important_columns:
            if col in existing_columns:
                columns_order.append(col)
        
        # 然后添加其他列
        for col in existing_columns:
            if col not in columns_order:
                columns_order.append(col)
        
        # 重新排列列
        df = df[columns_order]
        
        logger.debug(f"成功将字段字典转换为DataFrame，形状: {df.shape}")
        return df
    except Exception as e:
        logger.error(f"字段字典转换为DataFrame时出错: {str(e)}")
        raise Exception(f"字段字典转换为DataFrame时出错: {str(e)}")


class ApiInfoReader:
    """
    用于读取和解析api_info.json文件的类
    提供方法来获取api_links和tables数据，并支持通过api_mapping.json中的键进行访问
    """
    
    def __init__(self, api_info_path, api_mapping_path=None):
        """
        初始化ApiInfoReader类
        
        Args:
            api_info_path: api_info.json文件的路径
            api_mapping_path: api_mapping.json文件的路径，默认为None
        """
        self.api_info_path = api_info_path
        self.api_mapping_path = api_mapping_path or os.path.join(os.path.dirname(api_info_path), 'api_mapping.json')
        self.api_info_data = None
        self.api_mapping_data = None
        self.api_links_mapping = None
        self.tables_mapping = None
        
    def read_api_info_file(self):
        """
        读取api_info.json文件内容
        
        Returns:
            dict: 解析后的JSON数据
        
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
            Exception: 其他错误
        """
        logger.info(f"开始读取API信息文件: {self.api_info_path}")
        if not os.path.exists(self.api_info_path):
            logger.error(f"文件不存在: {self.api_info_path}")
            raise FileNotFoundError(f"文件不存在: {self.api_info_path}")
        
        try:
            with open(self.api_info_path, 'r', encoding='utf-8') as f:
                self.api_info_data = json.load(f)
            logger.info(f"成功读取API信息文件，数据长度: {len(str(self.api_info_data))}")
            return self.api_info_data
        except json.JSONDecodeError as e:
            logger.error(f"JSON格式错误: {e.msg}, 位置: {e.pos}")
            raise json.JSONDecodeError(f"JSON格式错误: {e.msg}", e.doc, e.pos)
        except Exception as e:
            logger.error(f"读取文件时出错: {str(e)}")
            raise Exception(f"读取文件时出错: {str(e)}")
    
    def read_api_mapping_file(self):
        """
        读取api_mapping.json文件内容
        
        Returns:
            dict: 解析后的JSON数据
        
        Raises:
            FileNotFoundError: 文件不存在
            json.JSONDecodeError: JSON格式错误
            Exception: 其他错误
        """
        logger.info(f"开始读取API映射文件: {self.api_mapping_path}")
        if not os.path.exists(self.api_mapping_path):
            logger.error(f"文件不存在: {self.api_mapping_path}")
            raise FileNotFoundError(f"文件不存在: {self.api_mapping_path}")
        
        try:
            with open(self.api_mapping_path, 'r', encoding='utf-8') as f:
                self.api_mapping_data = json.load(f)
            logger.info(f"成功读取API映射文件，包含 {len(self.api_mapping_data)} 个映射条目")
            return self.api_mapping_data
        except json.JSONDecodeError as e:
            logger.error(f"JSON格式错误: {e.msg}, 位置: {e.pos}")
            raise json.JSONDecodeError(f"JSON格式错误: {e.msg}", e.doc, e.pos)
        except Exception as e:
            logger.error(f"读取文件时出错: {str(e)}")
            raise Exception(f"读取文件时出错: {str(e)}")
    
    def _init_mappings(self):
        """
        初始化api_links和tables的映射关系
        """
        if self.api_info_data is None:
            self.read_api_info_file()
        
        if self.api_mapping_data is None:
            self.read_api_mapping_file()
        
        # 确保api_links和tables字段存在
        if 'api_links' not in self.api_info_data:
            logger.error("api_info.json中不包含api_links字段")
            raise ValueError("api_info.json中不包含api_links字段")
        
        if 'tables' not in self.api_info_data:
            logger.error("api_info.json中不包含tables字段")
            raise ValueError("api_info.json中不包含tables字段")
        
        # 获取api_links和tables数据
        api_links = self.api_info_data['api_links']
        tables = self.api_info_data['tables']
        
        # 检查数据数量是否匹配
        mapping_keys = list(self.api_mapping_data.keys())
        
        if len(api_links) != len(mapping_keys):
            logger.error(f"api_links数量({len(api_links)})与mapping数量({len(mapping_keys)})不匹配")
            raise ValueError(f"api_links数量({len(api_links)})与mapping数量({len(mapping_keys)})不匹配")
        
        if len(tables) != len(mapping_keys):
            logger.error(f"tables数量({len(tables)})与mapping数量({len(mapping_keys)})不匹配")
            raise ValueError(f"tables数量({len(tables)})与mapping数量({len(mapping_keys)})不匹配")
        
        # 创建映射
        self.api_links_mapping = {}
        self.tables_mapping = {}
        
        for i, key in enumerate(mapping_keys):
            self.api_links_mapping[key] = api_links[i]
            self.tables_mapping[key] = tables[i]
    
    def get_api_links(self, key=None):
        """
        获取api_links数据，支持通过key参数过滤特定的api_link
        
        Args:
            key: 可选，api_mapping中的键，如"股票列表"，不提供时返回所有api_links
        
        Returns:
            dict or dict: 当不提供key时返回所有api_links字典；提供key时返回对应的api_link数据
        
        Raises:
            KeyError: 当提供的key不存在时抛出
        """
        logger.info(f"获取API链接，key: {key}")
        if self.api_links_mapping is None:
            self._init_mappings()
        
        # 如果提供了key，则返回对应的api_link
        if key is not None:
            if key not in self.api_links_mapping:
                logger.error(f"键 '{key}' 不存在于api_links映射中")
                raise KeyError(f"键 '{key}' 不存在于api_links映射中")
            logger.debug(f"成功获取键 '{key}' 对应的API链接")
            return self.api_links_mapping[key]
        
        # 否则返回所有api_links
        logger.debug(f"成功获取所有API链接，共 {len(self.api_links_mapping)} 个")
        return self.api_links_mapping
    
    def get_tables(self, key=None, export='json'):
        """
        获取tables的headers数据，支持通过key参数过滤特定表格的headers，并支持不同的输出格式
        
        Args:
            key: 可选，api_mapping中的键，如"股票列表"，不提供时返回所有表格的headers
            export: 可选，输出格式，默认为'json'，可选值为'json'、'dict'、'df'
        
        Returns:
            根据export参数返回不同格式的数据：
            - 'json': 当不提供key时返回包含所有表格headers的字典；提供key时返回对应表格的headers列表
            - 'dict': 返回json_to_dict转换后的字段信息字典
            - 'df': 返回dict_to_df转换后的pandas DataFrame
        
        Raises:
            KeyError: 当提供的key不存在时抛出
            ValueError: 当export参数值不合法或表格数据格式错误时抛出
        """
        logger.info(f"获取表格数据，key: {key}, export: {export}")
        if self.tables_mapping is None:
            self._init_mappings()
        
        # 如果提供了key，则获取对应的表格headers
        if key is not None:
            if key not in self.tables_mapping:
                logger.error(f"键 '{key}' 不存在于tables映射中")
                raise KeyError(f"键 '{key}' 不存在于tables映射中")
            
            # 获取表格数据
            table_data = self.tables_mapping[key]
            logger.debug(f"获取表格 '{key}' 的数据，数据类型: {type(table_data)}")
            
            # 确保返回的是headers字段
            if isinstance(table_data, dict) and 'headers' in table_data:
                headers_data = table_data['headers']
                logger.debug(f"表格 '{key}' 的headers长度: {len(headers_data) if isinstance(headers_data, list) else '非列表'}")
            else:
                logger.error(f"表格数据格式错误，缺少'headers'字段，数据类型: {type(table_data)}")
                raise ValueError(f"表格数据格式错误，缺少'headers'字段")
        
        # 如果不提供key，则获取所有表格的headers
        else:
            headers_data = {}
            for k, table_data in self.tables_mapping.items():
                if isinstance(table_data, dict) and 'headers' in table_data:
                    headers_data[k] = table_data['headers']
        
        # 根据export参数确定输出格式
        if export == 'json':
            logger.debug(f"返回JSON格式数据，数据类型: {type(headers_data)}")
            return headers_data
        elif export == 'dict':
            if key is None:
                logger.error("当export='dict'时，必须提供key参数")
                raise ValueError("当export='dict'时，必须提供key参数")
            logger.debug(f"将数据转换为字典格式")
            return json_to_dict(headers_data)
        elif export == 'df':
            if key is None:
                logger.error("当export='df'时，必须提供key参数")
                raise ValueError("当export='df'时，必须提供key参数")
            logger.debug(f"将数据转换为DataFrame格式")
            dict_data = json_to_dict(headers_data)
            return dict_to_df(dict_data)
        else:
            logger.error(f"export参数值不合法: {export}")
            raise ValueError("export参数值不合法，可选值为'json'、'dict'、'df'")


class ByapiInfo:
    """BYAPI接口管理类 - 基于新的API映射关系更新"""
    
    def __init__(self, licence: str):
        """初始化API管理器
        
        Args:
            licence (str): API许可证
        """
        self.licence = licence
        self.base_url = "http://api.biyingapi.com"
        self.last_request_time = 0
        self.min_interval = 0.2  # 最小请求间隔(秒)，控制频率
        
        # 初始化API信息读取器
        self.api_info_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '1文件解析数据表', 'api_info.json')
        self.api_mapping_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '1文件解析数据表', 'api_mapping.json')
        
        try:
            self.api_reader = ApiInfoReader(self.api_info_path, self.api_mapping_path)
            # 加载API映射
            self.api_mapping = self.api_reader.read_api_mapping_file()
            logger.info(f"成功加载API映射，共{len(self.api_mapping)}个接口")
        except Exception as e:
            logger.error(f"加载API映射失败: {e}")
            # 使用备用的API映射字典
            self.api_mapping = {
                "股票列表": "stock_list",
                "新股日历": "new_stock_calendar",
                "指数、行业、概念树": "index_industry_concept_tree",
                "根据指数、行业、概念找相关股票": "stocks_by_index_industry_concept",
                "根据股票找相关指数、行业、概念": "index_industry_concept_by_stock",
                "涨停股池": "limit_up_stocks",
                "跌停股池": "limit_down_stocks",
                "强势股池": "strong_stocks",
                "次新股池": "new_stocks",
                "炸板股池": "broken_limit_stocks",
                "公司简介": "company_profile",
                "所属指数": "index_membership",
                "历届高管成员": "executive_history",
                "历届董事会成员": "board_history",
                "历届监事会成员": "supervisory_history",
                "近年分红": "recent_dividends",
                "近年增发": "recent_seo",
                "解禁限售": "lifted_shares",
                "近一年各季度利润": "quarterly_profits",
                "近一年各季度现金流": "quarterly_cashflow",
                "近年业绩预告": "earnings_forecast",
                "财务指标": "financial_indicators",
                "十大股东": "top_shareholders",
                "十大流通股东": "top_float_shareholders",
                "股东变化趋势": "shareholder_trend",
                "基金持股": "fund_ownership",
                "实时交易(公开数据)": "realtime_quotes_public",
                "当天逐笔交易": "intraday_transactions",
                "实时交易数据": "realtime_quotes",
                "买卖五档盘口": "five_level_quotes",
                "实时交易数据（多股）": "multi_stock_realtime",
                "资金流向数据": "fund_flow_data",
                "最新分时交易": "latest_minute_quotes",
                "历史分时交易": "history_minute_quotes",
                "历史涨跌停价格": "history_limit_prices",
                "行情指标": "market_indicators",
                "股票基础信息": "stock_basic_info",
                "资产负债表": "balance_sheet",
                "利润表": "income_statement",
                "现金流量表": "cash_flow_statement",
                "财务主要指标": "financial_ratios",
                "公司股本表": "capital_structure",
                "公司十大股东": "company_top_shareholders",
                "公司十大流通股东": "company_top_float_holders",
                "公司股东数": "shareholder_count",
                "历史分时MACD": "history_macd",
                "历史分时MA": "history_ma",
                "历史分时BOLL": "history_boll",
                "历史分时KDJ": "history_kdj"
            }
            
        # 初始化字段映射，用于列名转换
        self.field_mapping = {}
        
        # 尝试从api_info.json加载字段映射
        try:
            if hasattr(self.api_reader, 'get_field_mappings'):
                self.field_mapping = self.api_reader.get_field_mappings()
                logger.debug(f"成功加载字段映射，共{len(self.field_mapping)}个接口的字段映射")
            else:
                # 如果api_reader没有get_field_mappings方法，尝试直接构建股票列表的字段映射
                self.field_mapping = {
                    'stock_list': {
                        'dm': {'name': '股票代码'},
                        'mc': {'name': '股票名称'},
                        'jys': {'name': '交易所'}
                    }
                }
                logger.debug(f"使用默认字段映射")
        except Exception as e:
            logger.error(f"加载字段映射失败: {e}")

    def _get_stock_code_without_suffix(self, stock_code: str) -> str:
        """移除股票代码中的市场后缀
        
        Args:
            stock_code (str): 股票代码
        
        Returns:
            str: 移除后缀后的股票代码
        """
        if '.' in stock_code:
            return stock_code.split('.')[0]
        return stock_code

    def get_api_links(self, key=None):
        """
        获取API链接信息
        
        Args:
            key: 可选，API名称键，如"股票列表"，不提供时返回所有API链接
        
        Returns:
            dict: API链接信息
        """
        try:
            return self.api_reader.get_api_links(key)
        except Exception as e:
            logger.error(f"获取API链接失败: {e}")
            # 如果获取失败，返回空字典或错误信息
            if key:
                return {"error": str(e)}
            return {}

    def get_tables(self, key=None, export='json'):
        """
        获取表格定义信息
        
        Args:
            key: 可选，API名称键，如"股票列表"，不提供时返回所有表格定义
            export: 可选，输出格式，默认为'json'，可选值为'json'、'dict'、'df'
        
        Returns:
            表格定义信息，格式根据export参数而定
        """
        try:
            return self.api_reader.get_tables(key, export)
        except Exception as e:
            logger.error(f"获取表格定义失败: {e}")
            # 如果获取失败，返回空字典、空DataFrame或错误信息
            if export == 'df':
                return pd.DataFrame()
            elif key:
                return {"error": str(e)}
            return {}


    def _request(self, url: str) -> Dict[Any, Any]:
        """发送HTTP请求并返回JSON数据
        
        Args:
            url (str): 完整的API URL
            
        Returns:
            Dict[Any, Any]: 解析后的JSON数据
            
        Raises:
            requests.RequestException: 请求失败时抛出异常
        """
        # 控制请求频率
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_interval:
            time.sleep(self.min_interval - time_since_last_request)
        
        try:
            # 记录请求的URL（隐藏licence部分）
            masked_url = url
            if self.licence and self.licence in url:
                masked_url = url.replace(self.licence, "[LICENCE]")
            logger.debug(f"发送请求: {masked_url}")
            
            response = requests.get(url)
            response.raise_for_status()  # 检查HTTP错误
            self.last_request_time = time.time()
            
            # 解析JSON数据
            json_data = response.json()
            
            # 记录JSON数据结构，但不记录详细内容以保护隐私
            if json_data:
                logger.debug(f"响应数据结构: 类型={type(json_data)}, 包含键={list(json_data.keys()) if isinstance(json_data, dict) else None}")
            
            return json_data
        except requests.RequestException as e:
            logger.error(f"请求失败: {e}")
            raise requests.RequestException(f"请求失败: {e}")

    def _to_dataframe(self, json_data: Any, func_name: str, col_name: bool = False) -> pd.DataFrame:
        """将JSON数据转换为DataFrame
        
        Args:
            json_data (Any): JSON数据，可以是字典、列表或其他类型
            func_name (str): 函数名称，用于查找字段映射
            col_name (bool): 是否使用中文列名
            
        Returns:
            pd.DataFrame: 转换后的DataFrame
        """
        try:
            # 记录JSON数据结构的关键信息用于调试
            if json_data is None:
                logger.warning(f"{func_name}: 接收到None数据")
                return pd.DataFrame()
                
            logger.debug(f"{func_name}: JSON数据类型: {type(json_data)}")
            
            # 根据数据类型记录不同的信息
            if isinstance(json_data, dict):
                logger.debug(f"{func_name}: JSON数据包含键: {list(json_data.keys())}")
            elif isinstance(json_data, list):
                logger.debug(f"{func_name}: JSON数据是列表，长度: {len(json_data)}")
                # 如果列表非空，记录第一个元素的类型
                if json_data:
                    logger.debug(f"{func_name}: 列表第一个元素类型: {type(json_data[0])}")
            else:
                logger.debug(f"{func_name}: JSON数据既不是字典也不是列表")
            
            # 尝试不同的数据路径模式
            data = None
            
            # 模式1: data键直接包含列表数据
            if isinstance(json_data, dict) and 'data' in json_data:
                data = json_data['data']
                logger.debug(f"{func_name}: 在'data'键中找到数据，类型: {type(data)}")
            # 模式2: 直接返回的列表数据
            elif isinstance(json_data, list):
                data = json_data
                logger.debug(f"{func_name}: JSON直接是列表数据，长度: {len(data)}")
            # 模式3: 尝试其他可能的数据路径
            elif isinstance(json_data, dict) and 'items' in json_data:
                data = json_data['items']
                logger.debug(f"{func_name}: 在'items'键中找到数据")
            
            if data is None:
                logger.warning(f"{func_name}: 无法在JSON数据中找到有效的数据字段")
                # 尝试将整个JSON作为数据
                try:
                    df = pd.DataFrame([json_data])
                    logger.debug(f"{func_name}: 尝试将整个JSON作为单条记录转换，数据形状: {df.shape}")
                    return df
                except Exception as e:
                    logger.error(f"{func_name}: 转换JSON数据失败: {e}")
                    return pd.DataFrame()
            
            if not data:
                logger.warning(f"{func_name}: 数据字段为空")
                return pd.DataFrame()
                
            # 确保数据是列表格式
            if not isinstance(data, list):
                logger.debug(f"{func_name}: 数据不是列表，尝试转换，当前类型: {type(data)}")
                # 如果是字典，尝试将其作为单条记录
                if isinstance(data, dict):
                    data = [data]
                else:
                    # 其他类型，尝试直接转换
                    try:
                        df = pd.DataFrame([data])
                        logger.debug(f"{func_name}: 非列表数据转换成功，数据形状: {df.shape}")
                        return df
                    except Exception as e:
                        logger.error(f"{func_name}: 非列表数据转换失败: {e}")
                        return pd.DataFrame()
            
            # 创建DataFrame
            try:
                df = pd.DataFrame(data)
                logger.debug(f"{func_name}: 成功创建DataFrame，数据形状: {df.shape}")
            except Exception as e:
                logger.error(f"{func_name}: 创建DataFrame失败: {e}")
                return pd.DataFrame()
            
            # 查找字段映射并重命名列
            if col_name:
                # 安全检查self.field_mapping是否存在
                if hasattr(self, 'field_mapping') and isinstance(self.field_mapping, dict):
                    field_mapping = self.field_mapping.get(func_name, {})
                    if field_mapping and isinstance(field_mapping, dict):
                        # 重命名列为中文
                        rename_dict = {}
                        for col in df.columns:
                            if col in field_mapping and isinstance(field_mapping[col], dict) and 'name' in field_mapping[col]:
                                rename_dict[col] = field_mapping[col]['name']
                        
                        if rename_dict:
                            df = df.rename(columns=rename_dict)
                            logger.debug(f"{func_name}: 成功重命名{len(rename_dict)}列")
            
            return df
        except Exception as e:
            logger.error(f"{func_name}: _to_dataframe方法执行异常: {e}")
            # 打印完整的异常堆栈信息用于调试
            import traceback
            logger.error(f"{func_name}: 异常堆栈: {traceback.format_exc()}")
            return pd.DataFrame()

    def __call__(self, api_name: str, *args, col_name: bool = True, **kwargs) -> pd.DataFrame:
        """通过中文名称调用API接口
        
        Args:
            api_name (str): API中文名称
            col_name (bool): 是否使用中文列名
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            pd.DataFrame: API返回的数据
            
        Raises:
            ValueError: 如果API名称不存在
        """
        if api_name not in self.api_mapping:
            raise ValueError(f"API '{api_name}' 不存在")
        
        func_name = self.api_mapping[api_name]
        func = getattr(self, func_name, None)
        
        if func is None:
            raise ValueError(f"函数 {func_name} 未实现")
        
        return func(*args, col_name=col_name, **kwargs)

    # ==================== 股票列表接口 ====================
    
    def stock_list(self, col_name: bool = True) -> pd.DataFrame:
        """获取基础的股票代码和名称，用于后续接口的参数传入"""
        url = f"http://api.biyingapi.com/hslt/list/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "stock_list", col_name)
    
    def new_stock_calendar(self, col_name: bool = True) -> pd.DataFrame:
        """新股日历，按申购日期倒序"""
        url = f"http://api.biyingapi.com/hslt/new/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "new_stock_calendar", col_name)

    # ==================== 指数行业概念接口 ====================
    
    def index_industry_concept_tree(self, col_name: bool = True) -> pd.DataFrame:
        """获取指数、行业、概念（包括基金，债券，美股，外汇，期货，黄金等的代码）"""
        url = f"http://api.biyingapi.com/hszg/list/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "index_industry_concept_tree", col_name)
    
    def stocks_by_index_industry_concept(self, code: str, col_name: bool = True) -> pd.DataFrame:
        """根据"指数、行业、概念树"接口得到的代码作为参数，得到相关的股票"""
        url = f"http://api.biyingapi.com/hszg/gg/{code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "stocks_by_index_industry_concept", col_name)
    
    def index_industry_concept_by_stock(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据《股票列表》得到的股票代码作为参数，得到相关的指数、行业、概念"""
        # 去除股票代码中的市场后缀
        if '.' in stock_code:
            stock_code = stock_code.split('.')[0]
        
        url = f"http://api.biyingapi.com/hszg/zg/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "index_industry_concept_by_stock", col_name)

    # ==================== 涨跌股池接口 ====================
    
    def limit_up_stocks(self, date: str = "", col_name: bool = True) -> pd.DataFrame:
        """根据日期获取每天的涨停股票列表，根据封板时间升序"""
        if not date:
            date = time.strftime("%Y-%m-%d")
        
        url = f"http://api.biyingapi.com/hslt/ztgc/{date}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "limit_up_stocks", col_name)
    
    def limit_down_stocks(self, date: str = "", col_name: bool = True) -> pd.DataFrame:
        """根据日期获取每天的跌停股票列表，根据封单资金升序"""
        if not date:
            date = time.strftime("%Y-%m-%d")
        
        url = f"http://api.biyingapi.com/hslt/dtgc/{date}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "limit_down_stocks", col_name)
    
    def strong_stocks(self, date: str = "", col_name: bool = True) -> pd.DataFrame:
        """根据日期获取每天的强势股票列表，根据涨幅倒序"""
        if not date:
            date = time.strftime("%Y-%m-%d")
        
        url = f"http://api.biyingapi.com/hslt/qsgc/{date}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "strong_stocks", col_name)
    
    def new_stocks(self, date: str = "", col_name: bool = True) -> pd.DataFrame:
        """根据日期获取每天的次新股票列表，根据开板几日升序"""
        if not date:
            date = time.strftime("%Y-%m-%d")
        
        url = f"http://api.biyingapi.com/hslt/cxgc/{date}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "new_stocks", col_name)
    
    def broken_limit_stocks(self, date: str = "", col_name: bool = True) -> pd.DataFrame:
        """根据日期获取每天的炸板股票列表，根据首次封板时间升序"""
        if not date:
            date = time.strftime("%Y-%m-%d")
        
        url = f"http://api.biyingapi.com/hslt/zbgc/{date}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "broken_limit_stocks", col_name)

    # ==================== 上市公司详情接口 ====================
    
    def company_profile(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司的简介"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/gsjj/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "company_profile", col_name)
    
    def index_membership(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司所属的指数信息"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/sszs/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "index_membership", col_name)
    
    def executive_history(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司历届高管成员信息"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/ljgg/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "executive_history", col_name)
    
    def board_history(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司历届董事会成员信息"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/ljds/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "board_history", col_name)
    
    def supervisory_history(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司历届监事会成员信息"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/ljjj/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "supervisory_history", col_name)
    
    def recent_dividends(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司近年分红信息"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/jnfh/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "recent_dividends", col_name)
    
    def recent_seo(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司近年增发信息"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/jnzf/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "recent_seo", col_name)
    
    def lifted_shares(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司解禁限售信息"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/jjxs/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "lifted_shares", col_name)
    
    def quarterly_profits(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司近一年各季度利润信息"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/jdlr/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "quarterly_profits", col_name)
    
    def quarterly_cashflow(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司近一年各季度现金流信息"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/jdxj/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "quarterly_cashflow", col_name)
    
    def earnings_forecast(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司近年业绩预告信息"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/yjyg/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "earnings_forecast", col_name)
    
    def financial_indicators(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司的财务指标数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/cwzb/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "financial_indicators", col_name)
    
    def top_shareholders(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司的十大股东信息"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/sdgd/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "top_shareholders", col_name)
    
    def top_float_shareholders(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司的十大流通股东信息"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/ltgd/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "top_float_shareholders", col_name)
    
    def shareholder_trend(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司的股东变化趋势信息"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/gdbh/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "shareholder_trend", col_name)
    
    def fund_ownership(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """根据股票代码获取上市公司的基金持股信息"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hscp/jjcg/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "fund_ownership", col_name)

    # ==================== 实时交易接口 ====================
    
    def realtime_quotes_public(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的实时交易公开数据（不需要授权）"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hsrt/qt1/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "实时交易(公开数据)", col_name)
    
    def intraday_transactions(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取当天的逐笔交易数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hsrt/zbyt/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "当天逐笔交易", col_name)
    
    def realtime_quotes(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的实时交易数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"https://api.biyingapi.com/hsstock/real/time/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "实时交易数据", col_name)
    
    def five_level_quotes(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的买卖五档盘口数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        # 使用正确的API路径，根据api_info.json中的定义
        url = f"https://api.biyingapi.com/hsstock/real/five/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "买卖五档盘口", col_name)
    
    def multi_stock_realtime(self, stock_codes: str, col_name: bool = True) -> pd.DataFrame:
        """获取多个股票的实时交易数据，股票代码用逗号分隔"""
        url = f"http://api.biyingapi.com/hsrl/ssjy_more/{self.licence}?stock_codes={stock_codes}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "实时交易数据（多股）", col_name)
    
    def fund_flow_data(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的资金流向数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"https://api.biyingapi.com/hsstock/fund/flow/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "资金流向数据", col_name)

    # ==================== 行情数据接口 ====================
    
    def latest_minute_quotes(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的最新分时交易数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hshq/fxt/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "最新分时交易", col_name)
    
    def history_minute_quotes(self, stock_code: str, date: str = "", col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的历史分时交易数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        if not date:
            date = time.strftime("%Y-%m-%d")
        
        url = f"http://api.biyingapi.com/hshq/lxt/{stock_code}/{date}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "历史分时交易", col_name)
    
    def history_limit_prices(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的历史涨跌停价格数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hshq/ztj/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "历史涨跌停价格", col_name)
    
    def market_indicators(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的行情指标数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hshq/hqzb/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "行情指标", col_name)

    # ==================== 基础信息接口 ====================
    
    def stock_basic_info(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的基础信息"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hsjc/gsjj/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "股票基础信息", col_name)

    # ==================== 公司财务接口 ====================
    
    def balance_sheet(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的资产负债表数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        url = f"http://api.biyingapi.com/hsstock/financial/balance/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "资产负债表", col_name)
    
    def income_statement(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的利润表数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        url = f"http://api.biyingapi.com/hsstock/financial/income/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "利润表", col_name)
    
    def cash_flow_statement(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的现金流量表数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hsstock/financial/cashflow/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "现金流量表", col_name)
    
    def financial_ratios(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的财务主要指标数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hsstock/financial/pershareindex/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "财务主要指标", col_name)
    
    def capital_structure(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的公司股本表数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hsstock/financial/capital/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "公司股本表", col_name)
    
    def company_top_shareholders(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的公司十大股东数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hsstock/financial/topholder/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "公司十大股东", col_name)
    
    def company_top_float_holders(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的公司十大流通股东数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hsstock/financial/flowholder/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "公司十大流通股东", col_name)
    
    def shareholder_count(self, stock_code: str, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的公司股东数数据"""
        stock_code = self._get_stock_code_without_suffix(stock_code)
        
        url = f"http://api.biyingapi.com/hsstock/financial/hm/{stock_code}/{self.licence}"
        json_data = self._request(url)
        return self._to_dataframe(json_data, "公司股东数", col_name)

    # ==================== 技术指标接口 ====================
    
    def history_macd(self, stock_code: str, level: str = "d", adj_type: str = "n", start_time: str = "", end_time: str = "", limit: int = 0, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的历史分时MACD数据
        
        Args:
            stock_code (str): 股票代码，格式如000001.SZ
            level (str): 分时级别，支持5、15、30、60、d、w、m、y
            adj_type (str): 除权类型，日线以上支持n（不复权）、f（前复权）、b（后复权）、fr（等比前复权）、br（等比后复权），分钟级仅限n
            start_time (str): 开始时间，格式为YYYYMMDD或YYYYMMDDhhmmss
            end_time (str): 结束时间，格式为YYYYMMDD或YYYYMMDDhhmmss
            limit (int): 最新条数，0表示全部
            col_name (bool): 是否使用中文列名
        
        Returns:
            pd.DataFrame: MACD数据
        """
        url = f"http://api.biyingapi.com/hsstock/history/macd/{stock_code}/{level}/{adj_type}/{self.licence}"
        
        params = []
        if start_time:
            params.append(f"st={start_time}")
        if end_time:
            params.append(f"et={end_time}")
        if limit > 0:
            params.append(f"lt={limit}")
        
        if params:
            url += "?" + "&".join(params)
        
        json_data = self._request(url)
        return self._to_dataframe(json_data, "历史分时MACD", col_name)
    
    def history_ma(self, stock_code: str, level: str = "d", adj_type: str = "n", start_time: str = "", end_time: str = "", limit: int = 0, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的历史分时MA数据
        
        Args:
            stock_code (str): 股票代码，格式如000001.SZ
            level (str): 分时级别，支持5、15、30、60、d、w、m、y
            adj_type (str): 除权类型，日线以上支持n（不复权）、f（前复权）、b（后复权）、fr（等比前复权）、br（等比后复权），分钟级仅限n
            start_time (str): 开始时间，格式为YYYYMMDD或YYYYMMDDhhmmss
            end_time (str): 结束时间，格式为YYYYMMDD或YYYYMMDDhhmmss
            limit (int): 最新条数，0表示全部
            col_name (bool): 是否使用中文列名
        
        Returns:
            pd.DataFrame: MA数据
        """
        # 构建URL，保留股票代码的后缀
        url = f"http://api.biyingapi.com/hsstock/history/ma/{stock_code}/{level}/{adj_type}/{self.licence}"
        
        # 添加查询参数
        params = []
        if start_time:
            params.append(f"st={start_time}")
        if end_time:
            params.append(f"et={end_time}")
        if limit > 0:
            params.append(f"lt={limit}")
        
        if params:
            url += "?" + "&".join(params)
        
        json_data = self._request(url)
        return self._to_dataframe(json_data, "历史分时MA", col_name)
    
    def history_boll(self, stock_code: str, level: str = "d", adj_type: str = "n", start_time: str = "", end_time: str = "", limit: int = 0, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的历史分时BOLL数据
        
        Args:
            stock_code (str): 股票代码，格式如000001.SZ
            level (str): 分时级别，支持5、15、30、60、d、w、m、y
            adj_type (str): 除权类型，日线以上支持n（不复权）、f（前复权）、b（后复权）、fr（等比前复权）、br（等比后复权），分钟级仅限n
            start_time (str): 开始时间，格式为YYYYMMDD或YYYYMMDDhhmmss
            end_time (str): 结束时间，格式为YYYYMMDD或YYYYMMDDhhmmss
            limit (int): 最新条数，0表示全部
            col_name (bool): 是否使用中文列名
        
        Returns:
            pd.DataFrame: BOLL数据
        """
        # 构建URL，保留股票代码的后缀
        url = f"http://api.biyingapi.com/hsstock/history/boll/{stock_code}/{level}/{adj_type}/{self.licence}"
        
        # 添加查询参数
        params = []
        if start_time:
            params.append(f"st={start_time}")
        if end_time:
            params.append(f"et={end_time}")
        if limit > 0:
            params.append(f"lt={limit}")
        
        if params:
            url += "?" + "&".join(params)
        
        json_data = self._request(url)
        return self._to_dataframe(json_data, "历史分时BOLL", col_name)
    
    def history_kdj(self, stock_code: str, level: str = "d", adj_type: str = "n", start_time: str = "", end_time: str = "", limit: int = 0, col_name: bool = True) -> pd.DataFrame:
        """获取单个股票的历史分时KDJ数据
        
        Args:
            stock_code (str): 股票代码，格式如000001.SZ
            level (str): 分时级别，支持5、15、30、60、d、w、m、y
            adj_type (str): 除权类型，日线以上支持n（不复权）、f（前复权）、b（后复权）、fr（等比前复权）、br（等比后复权），分钟级仅限n
            start_time (str): 开始时间，格式为YYYYMMDD或YYYYMMDDhhmmss
            end_time (str): 结束时间，格式为YYYYMMDD或YYYYMMDDhhmmss
            limit (int): 最新条数，0表示全部
            col_name (bool): 是否使用中文列名
        
        Returns:
            pd.DataFrame: KDJ数据
        """
        # 构建URL，保留股票代码的后缀
        url = f"http://api.biyingapi.com/hsstock/history/kdj/{stock_code}/{level}/{adj_type}/{self.licence}"
        
        # 添加查询参数
        params = []
        if start_time:
            params.append(f"st={start_time}")
        if end_time:
            params.append(f"et={end_time}")
        if limit > 0:
            params.append(f"lt={limit}")
        
        if params:
            url += "?" + "&".join(params)
        
        json_data = self._request(url)
        return self._to_dataframe(json_data, "历史分时KDJ", col_name)

    # ==================== 辅助方法 ====================
    
    def _get_stock_code_without_suffix(self, stock_code: str) -> str:
        """去除股票代码中的市场后缀"""
        if '.' in stock_code:
            return stock_code.split('.')[0]
        return stock_code

    def get_supported_apis(self) -> List[Dict[str, str]]:
        """获取所有支持的API名称列表，格式为中文名:英文函数名的映射"""
        # 创建中文名:英文函数名的映射列表
        return [{cn_name: en_name} for cn_name, en_name in self.api_mapping.items()]

    def get_api_documentation(self, api_name: str) -> Dict[str, Any]:
        """获取API的文档信息
        
        Args:
            api_name (str): API中文名称
            
        Returns:
            Dict[str, Any]: 包含API文档信息的字典，按name, description, api_links, fields顺序排列
        """
        try:
            # 从api_info.json中获取文档信息和API链接信息
            tables = self.api_reader.get_tables(api_name)
            api_links = self.api_reader.get_api_links(api_name)
            
            # 创建结果字典，确保字段按指定顺序排列
            result = {
                'name': api_name,
                'description': f'{api_name}数据接口',
                'api_links': api_links if api_links and isinstance(api_links, dict) else {},
                'fields': tables if tables and isinstance(tables, dict) else (tables if tables else [])
            }
            
            return result
        except Exception as e:
            logger.error(f"获取API文档失败: {e}")
            return {
                'name': api_name,
                'description': '文档获取失败',
                'api_links': {},                
                'fields': []
            }

# 使用示例
if __name__ == "__main__":
    # 初始化API管理器（需要实际的licence）
    api = ByapiInfo("BAE8B7EA-739A-4536-BB87-275F3C6A4441")
    
    # 示例：获取所有支持的API
    print("支持的API列表：")
    print(api.get_supported_apis())
    
    # 示例：获取股票列表
    try:
        df = api.stock_list(col_name=True)
        print("股票列表获取成功！")
        print(f"数据形状: {df.shape}")
        if not df.empty:
            print(df.head())
    except Exception as e:
        print(f"获取股票列表失败: {e}")
    
    # 示例：通过中文名称调用API
    try:
        df = api("股票列表", col_name=True)
        print("通过中文名称调用成功！")
        print(f"数据形状: {df.shape}")
    except Exception as e:
        print(f"通过中文名称调用失败: {e}")
    
    # 示例：获取API文档
    try:
        api_doc = api.get_api_documentation("股票列表")
        print("API文档信息：")
        print(f"名称: {api_doc['name']}")
        print(f"描述: {api_doc['description']}")
        print(f"字段数: {len(api_doc['fields'])}")
    except Exception as e:
        print(f"获取API文档失败: {e}")
    
    # 示例：获取API链接信息
    try:
        api_links = api.get_api_links()
        print(f"获取到{len(api_links)}个API链接")
    except Exception as e:
        print(f"获取API链接失败: {e}")
    
    # 示例：获取特定API的表格定义
    try:
        table_def = api.get_tables("股票列表")
        print(f"股票列表表格定义: {table_def}")
    except Exception as e:
        print(f"获取表格定义失败: {e}")