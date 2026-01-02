# -*- coding: utf-8 -*-
"""
通达信板块数据读取器

基于PyTDX的block_reader模块，提供板块数据读取功能。
支持4种板块类型：指数板块、风格板块、概念板块、默认板块。

@author: MyStocks Project
@version: 1.0
@created: 2026-01-02
"""

import os
import pandas as pd
from typing import Dict, List, Optional
from pathlib import Path

# 尝试从PyTDX导入BlockReader
try:
    from pytdx.reader.block_reader import BlockReader, BlockReader_TYPE_FLAT, BlockReader_TYPE_GROUP
    PYTDX_AVAILABLE = True
except ImportError:
    PYTDX_AVAILABLE = False
    BlockReader = None


class TdxBlockReader:
    """
    通达信板块数据读取器

    从本地通达信安装目录读取板块分类数据，包括：
    - 指数板块 (block_zs.dat)
    - 风格板块 (block_fg.dat)
    - 概念板块 (block_gn.dat)
    - 默认板块 (block.dat)

    Attributes:
        tdx_path: 通达信安装路径 (如: /mnt/d/ProgramData/tdx_new)

    Example:
        >>> reader = TdxBlockReader("/mnt/d/ProgramData/tdx_new")
        >>> # 获取指数板块
        >>> df_index = reader.get_index_blocks()
        >>> print(df_index.head())
        >>> # 获取概念板块
        >>> df_concept = reader.get_concept_blocks()
        >>> # 获取所有板块
        >>> df_all = reader.get_all_blocks()
    """

    def __init__(self, tdx_path: str):
        """
        初始化板块数据读取器

        Args:
            tdx_path: 通达信安装路径
                例如: /mnt/d/ProgramData/tdx_new
                      C:/新建文件夹/TdxW_HuaTai

        Raises:
            ImportError: PyTDX未安装
            FileNotFoundError: 通达信路径不存在
        """
        if not PYTDX_AVAILABLE:
            raise ImportError(
                "PyTDX未安装，请先安装: pip install pytdx\n"
                "板块数据功能依赖PyTDX的block_reader模块"
            )

        self.tdx_path = Path(tdx_path)
        if not self.tdx_path.exists():
            raise FileNotFoundError(f"通达信路径不存在: {tdx_path}")

        self.reader = BlockReader()

        # 板块文件路径映射
        self.block_files = {
            'index': self.tdx_path / "T0002/hq_cache/block_zs.dat",   # 指数板块
            'style': self.tdx_path / "T0002/hq_cache/block_fg.dat",    # 风格板块
            'concept': self.tdx_path / "T0002/hq_cache/block_gn.dat",  # 概念板块
            'default': self.tdx_path / "T0002/hq_cache/block.dat"       # 默认板块
        }

    def get_index_blocks(self, result_type: str = 'flat') -> pd.DataFrame:
        """
        获取指数板块数据

        Args:
            result_type: 返回格式
                - 'flat': 扁平格式，每个股票一行 (默认)
                - 'group': 分组格式，每个板块一行

        Returns:
            pd.DataFrame: 指数板块数据
                - flat格式列: [blockname, block_type, code_index, code]
                - group格式列: [blockname, block_type, stock_count, code_list]

        Example:
            >>> df = reader.get_index_blocks()
            >>> print(df.head())
               blockname  block_type  code_index    code
            0      上证指数          1           0  000001
            1      上证指数          1           1  000002
        """
        file_path = self.block_files['index']
        if not file_path.exists():
            raise FileNotFoundError(f"指数板块文件不存在: {file_path}")

        result_type_code = BlockReader_TYPE_FLAT if result_type == 'flat' else BlockReader_TYPE_GROUP
        return self.reader.get_df(str(file_path), result_type_code)

    def get_style_blocks(self, result_type: str = 'flat') -> pd.DataFrame:
        """
        获取风格板块数据

        Args:
            result_type: 返回格式 ('flat' 或 'group')

        Returns:
            pd.DataFrame: 风格板块数据
        """
        file_path = self.block_files['style']
        if not file_path.exists():
            raise FileNotFoundError(f"风格板块文件不存在: {file_path}")

        result_type_code = BlockReader_TYPE_FLAT if result_type == 'flat' else BlockReader_TYPE_GROUP
        return self.reader.get_df(str(file_path), result_type_code)

    def get_concept_blocks(self, result_type: str = 'flat') -> pd.DataFrame:
        """
        获取概念板块数据

        Args:
            result_type: 返回格式 ('flat' 或 'group')

        Returns:
            pd.DataFrame: 概念板块数据

        Example:
            >>> df = reader.get_concept_blocks()
            >>> # 筛选特定概念
            >>> new_energy = df[df['blockname'].str.contains('新能源')]
            >>> print(new_energy)
        """
        file_path = self.block_files['concept']
        if not file_path.exists():
            raise FileNotFoundError(f"概念板块文件不存在: {file_path}")

        result_type_code = BlockReader_TYPE_FLAT if result_type == 'flat' else BlockReader_TYPE_GROUP
        return self.reader.get_df(str(file_path), result_type_code)

    def get_default_blocks(self, result_type: str = 'flat') -> pd.DataFrame:
        """
        获取默认板块数据

        Args:
            result_type: 返回格式 ('flat' 或 'group')

        Returns:
            pd.DataFrame: 默认板块数据
        """
        file_path = self.block_files['default']
        if not file_path.exists():
            raise FileNotFoundError(f"默认板块文件不存在: {file_path}")

        result_type_code = BlockReader_TYPE_FLAT if result_type == 'flat' else BlockReader_TYPE_GROUP
        return self.reader.get_df(str(file_path), result_type_code)

    def get_all_blocks(self, result_type: str = 'flat') -> pd.DataFrame:
        """
        获取所有板块数据 (合并4种类型)

        Args:
            result_type: 返回格式 ('flat' 或 'group')

        Returns:
            pd.DataFrame: 所有板块数据的合并结果

        Example:
            >>> df_all = reader.get_all_blocks()
            >>> print(f"总板块数: {df_all['blockname'].nunique()}")
            >>> print(f"总股票数: {df_all['code'].nunique()}")
        """
        dfs = []

        for block_type in ['index', 'style', 'concept', 'default']:
            try:
                df = self.get_blocks_by_type(block_type, result_type)
                if not df.empty:
                    dfs.append(df)
            except FileNotFoundError:
                # 某些板块文件可能不存在，跳过
                continue

        if not dfs:
            return pd.DataFrame()

        return pd.concat(dfs, ignore_index=True)

    def get_blocks_by_type(self, block_type: str, result_type: str = 'flat') -> pd.DataFrame:
        """
        根据板块类型获取数据

        Args:
            block_type: 板块类型 ('index', 'style', 'concept', 'default')
            result_type: 返回格式 ('flat' 或 'group')

        Returns:
            pd.DataFrame: 板块数据

        Raises:
            ValueError: 不支持的板块类型
        """
        type_methods = {
            'index': self.get_index_blocks,
            'style': self.get_style_blocks,
            'concept': self.get_concept_blocks,
            'default': self.get_default_blocks
        }

        if block_type not in type_methods:
            raise ValueError(
                f"不支持的板块类型: {block_type}\n"
                f"支持的类型: {list(type_methods.keys())}"
            )

        return type_methods[block_type](result_type)

    def get_stock_blocks(self, stock_code: str) -> List[Dict[str, str]]:
        """
        获取指定股票所属的所有板块

        Args:
            stock_code: 6位股票代码 (如: '600519')

        Returns:
            List[Dict]: 股票所属板块列表
                [{'blockname': '白酒', 'block_type': '概念'}, ...]

        Example:
            >>> blocks = reader.get_stock_blocks('600519')
            >>> for block in blocks:
            ...     print(f"{block['blockname']} ({block['block_type']})")
        """
        df_all = self.get_all_blocks(result_type='flat')

        if df_all.empty:
            return []

        # 筛选指定股票的板块
        df_stock = df_all[df_all['code'] == stock_code]

        # 转换为字典列表
        blocks = []
        for _, row in df_stock.iterrows():
            blocks.append({
                'blockname': row['blockname'],
                'block_type': row['block_type']
            })

        return blocks

    def get_block_stocks(self, block_name: str) -> List[str]:
        """
        获取指定板块包含的所有股票

        Args:
            block_name: 板块名称 (如: '白酒', '新能源')

        Returns:
            List[str]: 股票代码列表

        Example:
            >>> stocks = reader.get_block_stocks('白酒')
            >>> print(f"白酒板块共 {len(stocks)} 只股票")
            >>> print(stocks[:10])  # 前10只股票
        """
        df_all = self.get_all_blocks(result_type='flat')

        if df_all.empty:
            return []

        # 筛选指定板块的股票
        df_block = df_all[df_all['blockname'] == block_name]

        return df_block['code'].unique().tolist()

    def list_all_block_names(self) -> Dict[str, List[str]]:
        """
        列出所有板块名称（按类型分组）

        Returns:
            Dict: 按板块类型分组的板块名称
                {
                    'index': ['上证指数', '深证成指', ...],
                    'style': ['价值股', '成长股', ...],
                    'concept': ['新能源', '白酒', ...],
                    'default': [...]
                }

        Example:
            >>> all_blocks = reader.list_all_block_names()
            >>> for block_type, names in all_blocks.items():
            ...     print(f"{block_type}: {len(names)}个板块")
        """
        result = {
            'index': [],
            'style': [],
            'concept': [],
            'default': []
        }

        df_all = self.get_all_blocks(result_type='flat')

        if df_all.empty:
            return result

        # 按类型分组提取板块名称
        for block_type in ['index', 'style', 'concept', 'default']:
            df_type = df_all[df_all['block_type'] == block_type]
            result[block_type] = df_type['blockname'].unique().tolist()

        return result

    def get_statistics(self) -> Dict[str, int]:
        """
        获取板块数据统计信息

        Returns:
            Dict: 统计信息
                {
                    'total_blocks': 总板块数,
                    'total_stocks': 总股票数,
                    'index_blocks': 指数板块数,
                    'style_blocks': 风格板块数,
                    'concept_blocks': 概念板块数,
                    'default_blocks': 默认板块数
                }

        Example:
            >>> stats = reader.get_statistics()
            >>> print(f"总板块数: {stats['total_blocks']}")
            >>> print(f"总股票数: {stats['total_stocks']}")
        """
        df_all = self.get_all_blocks(result_type='flat')

        if df_all.empty:
            return {
                'total_blocks': 0,
                'total_stocks': 0,
                'index_blocks': 0,
                'style_blocks': 0,
                'concept_blocks': 0,
                'default_blocks': 0
            }

        return {
            'total_blocks': df_all['blockname'].nunique(),
            'total_stocks': df_all['code'].nunique(),
            'index_blocks': df_all[df_all['block_type'] == '指数板块']['blockname'].nunique(),
            'style_blocks': df_all[df_all['block_type'] == '风格板块']['blockname'].nunique(),
            'concept_blocks': df_all[df_all['block_type'] == '概念板块']['blockname'].nunique(),
            'default_blocks': df_all[df_all['block_type'] == '默认板块']['blockname'].nunique()
        }


# 便利函数
def get_tdx_block_reader(tdx_path: str = None) -> TdxBlockReader:
    """
    获取TdxBlockReader实例的便利函数

    Args:
        tdx_path: 通达信安装路径，None表示使用环境变量TDX_DATA_PATH

    Returns:
        TdxBlockReader: 板块数据读取器实例

    Example:
        >>> from src.data_sources.tdx_block_reader import get_tdx_block_reader
        >>> reader = get_tdx_block_reader()
        >>> df = reader.get_concept_blocks()
    """
    if tdx_path is None:
        import os
        tdx_path = os.getenv('TDX_DATA_PATH')
        if tdx_path is None:
            raise ValueError(
                "未指定通达信路径，请:\n"
                "1. 设置环境变量 TDX_DATA_PATH\n"
                "2. 或直接传入 tdx_path 参数"
            )

    return TdxBlockReader(tdx_path)


if __name__ == '__main__':
    # 测试代码
    import sys

    # 尝试从环境变量获取TDX路径
    tdx_path = os.getenv('TDX_DATA_PATH', '/mnt/d/ProgramData/tdx_new')

    print(f"使用TDX路径: {tdx_path}")

    try:
        reader = TdxBlockReader(tdx_path)

        # 获取统计信息
        stats = reader.get_statistics()
        print("\n=== 板块数据统计 ===")
        for key, value in stats.items():
            print(f"{key}: {value}")

        # 获取概念板块示例
        print("\n=== 概念板块示例 ===")
        df_concept = reader.get_concept_blocks()
        if not df_concept.empty:
            print(f"概念板块数量: {df_concept['blockname'].nunique()}")
            print(df_concept.head(10))

        # 获取特定股票的板块
        print("\n=== 获取茅台所属板块 ===")
        blocks = reader.get_stock_blocks('600519')
        for block in blocks[:10]:  # 显示前10个
            print(f"  - {block['blockname']} ({block['block_type']})")

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)
