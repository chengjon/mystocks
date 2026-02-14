"""TDX 数据源适配器子模块"""

import logging
import os
import struct
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


class TdxBasicBlockMixin:
    """TDX 基础与板块数据"""

    def get_stock_basic(self, symbol: str) -> Dict:
        """获取股票基本信息 - Phase 6实现(有限支持)"""
        try:
            # 通过查询日线数据获取基本信息
            df = self.get_stock_daily(symbol, datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d"))

            if not df.empty:
                # 提取基本信息
                latest_record = df.iloc[-1]  # 最新记录

                # 构建股票基本信息
                basic_info = {
                    "symbol": symbol,
                    "name": latest_record.get("name", f"股票{symbol}"),  # 实际上可能需要单独的接口获取名称
                    "market": "SH" if symbol.startswith("6") else "SZ",
                    "category": "stock",  # 类别可以是stock, index, fund等
                    "status": "trading",  # 交易状态
                    "currency": "CNY",  # 货币
                    "industry": "",  # 行业信息，需要另外获取
                    "area": "",  # 地区信息
                    "list_date": latest_record.get("date", ""),  # 上市日期
                    "total_shares": None,  # 总股本
                    "float_shares": None,  # 流通股本
                }

                return basic_info
            else:
                # 如果无法从日线数据获取，返回默认值
                return {
                    "symbol": symbol,
                    "name": f"股票{symbol}",
                    "market": "SH" if symbol.startswith("6") else "SZ",
                    "category": "stock",
                    "status": "unknown",
                    "currency": "CNY",
                    "industry": "",
                    "area": "",
                    "list_date": "",
                    "total_shares": None,
                    "float_shares": None,
                }
        except Exception as e:
            self.logger.error("获取股票基本信息失败 %s: %s", symbol, str(e))
            return {}

    def get_index_components(self, symbol: str) -> List[str]:
        """获取指数成分股 - Phase 7实现(有限支持)"""
        try:
            # TDX API不直接支持获取指数成分股，返回空列表
            # 这是一个已知限制，因为TDX API功能有限
            self.logger.info("TDX不支持直接获取指数成分股: %s", symbol)

            # 如果是常见的指数，我们可以返回模拟数据
            if symbol in ["000001", "000300", "000016", "399001", "399006"]:
                # 这些是上证指数、沪深300、上证50、深证成指、创业板指
                # 实际应用中应通过其他接口获取这些指数的成分股
                self.logger.warning("%s 为常见指数,但TDX不提供成分股查询", symbol)

            return []
        except Exception as e:
            self.logger.error("获取指数成分股失败 %s: %s", symbol, str(e))
            return []

    def get_block_data(self, block_type: str = "all", result_type: str = "flat") -> pd.DataFrame:
        """
        获取板块数据

        Args:
            block_type: 板块类型
                - 'index': 指数板块
                - 'style': 风格板块
                - 'concept': 概念板块
                - 'default': 默认板块
                - 'all': 所有板块 (默认)
            result_type: 返回格式
                - 'flat': 扁平格式，每个股票一行 (默认)
                - 'group': 分组格式，每个板块一行

        Returns:
            pd.DataFrame: 板块数据
                - flat格式列: [blockname, block_type, code_index, code]
                - group格式列: [blockname, block_type, stock_count, code_list]

        Raises:
            ImportError: PyTDX未安装
            FileNotFoundError: 通达信路径或板块文件不存在

        Example:
            >>> tdx = TdxDataSource()
            >>> # 获取所有概念板块
            >>> df = tdx.get_block_data(block_type='concept')
            >>> print(f"概念板块数: {df['blockname'].nunique()}")
            >>> # 获取所有板块
            >>> df_all = tdx.get_block_data(block_type='all')
        """
        try:
            # 使用环境变量TDX_DATA_PATH
            import os

            from .tdx_block_reader import TdxBlockReader

            tdx_path = os.getenv("TDX_DATA_PATH")
            if not tdx_path:
                self.logger.error("环境变量TDX_DATA_PATH未设置")
                return pd.DataFrame()

            reader = TdxBlockReader(tdx_path)

            # 根据类型获取数据
            if block_type == "all":
                return reader.get_all_blocks(result_type=result_type)
            elif block_type == "index":
                return reader.get_index_blocks(result_type=result_type)
            elif block_type == "style":
                return reader.get_style_blocks(result_type=result_type)
            elif block_type == "concept":
                return reader.get_concept_blocks(result_type=result_type)
            elif block_type == "default":
                return reader.get_default_blocks(result_type=result_type)
            else:
                self.logger.error("不支持的板块类型: %s", block_type)
                return pd.DataFrame()

        except ImportError:
            self.logger.error("导入TdxBlockReader失败，请安装PyTDX: pip install pytdx")
            return pd.DataFrame()
        except FileNotFoundError as e:
            self.logger.error("板块文件不存在: %s", e)
            return pd.DataFrame()
        except Exception as e:
            self.logger.error("获取板块数据失败: %s", e)
            return pd.DataFrame()

    def get_stock_blocks(self, stock_code: str) -> List[Dict[str, str]]:
        """
        获取指定股票所属的所有板块

        Args:
            stock_code: 6位股票代码 (如: '600519')

        Returns:
            List[Dict]: 股票所属板块列表
                [{'blockname': '白酒', 'block_type': '概念板块'}, ...]

        Example:
            >>> tdx = TdxDataSource()
            >>> blocks = tdx.get_stock_blocks('600519')
            >>> for block in blocks:
            ...     print(f"{block['blockname']} ({block['block_type']})")
        """
        try:
            import os

            from .tdx_block_reader import TdxBlockReader

            tdx_path = os.getenv("TDX_DATA_PATH")
            if not tdx_path:
                self.logger.error("环境变量TDX_DATA_PATH未设置")
                return []

            reader = TdxBlockReader(tdx_path)
            return reader.get_stock_blocks(stock_code)

        except Exception as e:
            self.logger.error("获取股票板块失败 %s: %s", stock_code, e)
            return []

    def get_block_stocks(self, block_name: str) -> List[str]:
        """
        获取指定板块包含的所有股票

        Args:
            block_name: 板块名称 (如: '白酒', '新能源')

        Returns:
            List[str]: 股票代码列表

        Example:
            >>> tdx = TdxDataSource()
            >>> stocks = tdx.get_block_stocks('白酒')
            >>> print(f"白酒板块共 {len(stocks)} 只股票")
            >>> print(stocks[:10])  # 前10只股票
        """
        try:
            import os

            from .tdx_block_reader import TdxBlockReader

            tdx_path = os.getenv("TDX_DATA_PATH")
            if not tdx_path:
                self.logger.error("环境变量TDX_DATA_PATH未设置")
                return []

            reader = TdxBlockReader(tdx_path)
            return reader.get_block_stocks(block_name)

        except Exception as e:
            self.logger.error("获取板块股票失败 %s: %s", block_name, e)
            return []

