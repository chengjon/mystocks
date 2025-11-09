import pandas as pd
import numpy as np
import os
from typing import List, Optional, Union


class XgTdx:
    """
    通达信自选股操作模型
    用于读取、创建、修改通达信自选股板块及成分股
    """

    def __init__(self, path: str = r'/mnt/D/ProgramData/tdx_new/T0002/blocknew'):
        """
        初始化通达信自选股操作模型

        Args:
            path: 通达信板块文件存储路径，默认路径为 /mnt/D/ProgramData/tdx_new/T0002/blocknew
        """
        self.path = path
        # 确保路径存在
        if not os.path.exists(self.path):
            os.makedirs(self.path, exist_ok=True)
            print(f"路径不存在，已自动创建: {self.path}")

    def read_all_tdx_stock(self) -> List[str]:
        """
        读取全部的通达信板块文件名

        Returns:
            List[str]: 板块文件列表（包含后缀名 .blk）
        """
        try:
            all_files = os.listdir(self.path)
            # 过滤出 .blk 后缀的板块文件
            return [file for file in all_files if file.endswith('.blk')]
        except PermissionError:
            print(f"权限错误：无法访问路径 {self.path}")
            return []
        except Exception as e:
            print(f"错误：通达信板块文件路径访问失败 - {str(e)}")
            return []

    def _get_blk_file_path(self, name: str) -> str:
        """
        生成板块文件的完整路径（私有辅助方法）

        Args:
            name: 板块名称

        Returns:
            str: 板块文件完整路径
        """
        return os.path.join(self.path, f"{name}.blk")

    def _is_blk_exists(self, name: str) -> bool:
        """
        检查板块是否存在（私有辅助方法）

        Args:
            name: 板块名称

        Returns:
            bool: 存在返回 True，否则返回 False
        """
        blk_file = self._get_blk_file_path(name)
        return os.path.exists(blk_file)

    def creat_tdx_user_def_stock(self, name: str = 'QMTCG') -> None:
        """
        建立通达信自定义自选股模块

        Args:
            name: 自定义板块名称，默认名称为 'QMTCG'
        """
        if self._is_blk_exists(name):
            print(f'[{name}] 通达信自选股模块已经存在，不重复创建')
            return

        blk_file = self._get_blk_file_path(name)
        try:
            with open(blk_file, 'w', encoding='gbk') as file:
                file.writelines('')
            print(f'[{name}] 通达信自选股板块建立成功')
        except Exception as e:
            print(f'错误：建立板块 [{name}] 失败 - {str(e)}')

    def del_tdx_user_def_stock(self, name: str = 'QMTCG') -> None:
        """
        删除自定义股票池板块

        Args:
            name: 自定义板块名称，默认名称为 'QMTCG'
        """
        if not self._is_blk_exists(name):
            print(f'[{name}.blk] 板块不存在，无法删除')
            return

        blk_file = self._get_blk_file_path(name)
        try:
            os.remove(blk_file)
            print(f'自定义模块 [{name}] 删除成功')
        except Exception as e:
            print(f'错误：删除板块 [{name}] 失败 - {str(e)}')

    def adjust_stock(self, stock: str) -> str:
        """
        调整股票代码格式（通达信内部格式）
        沪市股票前缀加 '1'，深市股票前缀加 '0'

        Args:
            stock: 原始股票代码（可带后缀 .SH/.SZ 或不带）

        Returns:
            str: 调整后的通达信格式股票代码
        """
        # 去除后缀（如果有）
        stock_clean = stock.replace('.SH', '').replace('.SZ', '').strip()
        
        # 沪市股票判断
        sh_prefixes = ['600', '601', '603', '605', '688', '689']
        sh_index_prefixes = ['11', '51', '58']
        
        if (stock_clean[:3] in sh_prefixes) or (stock_clean[:2] in sh_index_prefixes):
            return f"1{stock_clean}"
        # 深市股票
        else:
            return f"0{stock_clean}"

    def adjust_stock_1(self, stock: str) -> str:
        """
        调整股票代码格式（外部标准格式）
        为股票代码添加 .SH/.SZ 后缀

        Args:
            stock: 原始股票代码（可带后缀或不带）

        Returns:
            str: 标准格式股票代码（如 600031.SH, 000001.SZ）
        """
        stock_upper = stock.upper().strip()
        
        # 如果已带后缀，直接返回
        if stock_upper.endswith(('.SH', '.SZ')):
            return stock_upper
        
        # 沪市股票判断
        sh_prefixes = ['600', '601', '603', '605', '688', '689']
        sh_index_prefixes = ['11', '51', '58']
        
        if (stock_upper[:3] in sh_prefixes) or (stock_upper[:2] in sh_index_prefixes):
            return f"{stock_upper}.SH"
        # 深市股票
        else:
            return f"{stock_upper}.SZ"

    def read_tdx_stock(self, name: str = 'QMTCG') -> pd.DataFrame:
        """
        读取通达信板块成分股（通达信内部格式）

        Args:
            name: 板块名称，默认名称为 'QMTCG'

        Returns:
            pd.DataFrame: 包含证券代码的 DataFrame，列名为 '证券代码'
        """
        blk_file = self._get_blk_file_path(name)
        stock_list = []

        try:
            with open(blk_file, 'r', encoding='gbk') as file:
                lines = file.readlines()
                for line in lines:
                    stock_code = line.strip()
                    # 过滤有效股票代码（长度至少6位）
                    if len(stock_code) >= 6:
                        stock_list.append(stock_code)
            
            df = pd.DataFrame({'证券代码': stock_list})
            return df
        except FileNotFoundError:
            print(f'错误：板块 [{name}] 不存在 - 路径: {blk_file}')
        except PermissionError:
            print(f'错误：无权限访问板块 [{name}] - 路径: {blk_file}')
        except Exception as e:
            print(f'错误：读取板块 [{name}] 失败 - {str(e)}')
        
        return pd.DataFrame()

    def read_tdx_stock_1(self, name: str = 'QMTCG') -> pd.DataFrame:
        """
        读取通达信板块成分股（外部标准格式）
        将通达信内部格式转换为带 .SH/.SZ 后缀的标准格式

        Args:
            name: 板块名称，默认名称为 'QMTCG'

        Returns:
            pd.DataFrame: 包含标准格式证券代码的 DataFrame，列名为 '证券代码'
        """
        df = self.read_tdx_stock(name)
        if df.empty:
            return df
        
        try:
            # 去除通达信前缀（1或0），并转换为标准格式
            df['证券代码'] = df['证券代码'].apply(
                lambda x: self.adjust_stock_1(str(x)[1:])
            )
            return df
        except Exception as e:
            print(f'错误：转换板块 [{name}] 股票代码格式失败 - {str(e)}')
            return pd.DataFrame()

    def add_tdx_stock(self, name: str = 'QMTCG', stock: str = '000001') -> None:
        """
        单个添加股票到通达信自选股

        Args:
            name: 板块名称，默认名称为 'QMTCG'
            stock: 股票代码（可带后缀或不带），默认代码为 '000001'
        """
        # 确保板块存在
        if not self._is_blk_exists(name):
            self.creat_tdx_user_def_stock(name)
            print(f'[{name}] 自选股不存在，已自动建立')

        # 读取现有股票列表
        df = self.read_tdx_stock(name)
        stock_list = df['证券代码'].tolist() if not df.empty else []

        # 调整股票代码格式
        adjusted_stock = self.adjust_stock(stock)

        # 检查是否已存在
        if adjusted_stock in stock_list:
            print(f'[{adjusted_stock}] 已在自选股 [{name}] 中，不重复添加')
            return

        # 添加并保存
        stock_list.append(adjusted_stock)
        blk_file = self._get_blk_file_path(name)
        
        try:
            with open(blk_file, 'w', encoding='gbk') as file:
                for code in stock_list:
                    file.writelines(f"{code}\n")
            print(f'[{adjusted_stock}] 添加到自选股 [{name}] 成功')
        except Exception as e:
            print(f'错误：添加股票 [{adjusted_stock}] 到板块 [{name}] 失败 - {str(e)}')

    def add_tdx_stock_list(self, name: str = 'QMTCG', user_stock_list: List[str] = ['000001']) -> None:
        """
        批量添加股票到通达信自选股

        Args:
            name: 板块名称，默认名称为 'QMTCG'
            user_stock_list: 股票代码列表，默认列表为 ['000001']
        """
        # 确保板块存在
        if not self._is_blk_exists(name):
            self.creat_tdx_user_def_stock(name)
            print(f'[{name}] 自选股不存在，已自动建立')

        # 读取现有股票列表
        df = self.read_tdx_stock(name)
        stock_list = df['证券代码'].tolist() if not df.empty else []

        # 批量处理股票
        added_stocks = []
        existing_stocks = []
        
        for stock in user_stock_list:
            adjusted_stock = self.adjust_stock(stock)
            if adjusted_stock in stock_list:
                existing_stocks.append(adjusted_stock)
            else:
                stock_list.append(adjusted_stock)
                added_stocks.append(adjusted_stock)

        # 保存更新后的股票列表
        blk_file = self._get_blk_file_path(name)
        try:
            with open(blk_file, 'w', encoding='gbk') as file:
                for code in stock_list:
                    file.writelines(f"{code}\n")
            
            # 输出统计信息
            if existing_stocks:
                print(f'以下股票已存在于 [{name}]，未重复添加: {", ".join(existing_stocks)}')
            if added_stocks:
                print(f'以下股票添加到 [{name}] 成功: {", ".join(added_stocks)}')
        except Exception as e:
            print(f'错误：批量添加股票到板块 [{name}] 失败 - {str(e)}')

    def del_tdx_stock(self, name: str = 'QMTCG', stock: str = '000001') -> None:
        """
        单个删除通达信自选股成分股

        Args:
            name: 板块名称，默认名称为 'QMTCG'
            stock: 股票代码（可带后缀或不带），默认代码为 '000001'
        """
        # 检查板块是否存在
        if not self._is_blk_exists(name):
            print(f'[{name}] 自选股不存在，无法删除股票')
            return

        # 读取现有股票列表
        df = self.read_tdx_stock(name)
        if df.empty:
            print(f'[{name}] 自选股无数据，无需删除')
            return
        
        stock_list = df['证券代码'].tolist()
        adjusted_stock = self.adjust_stock(stock)

        # 检查股票是否存在
        if adjusted_stock not in stock_list:
            print(f'[{adjusted_stock}] 不在自选股 [{name}] 中，无法删除')
            return

        # 删除并保存
        stock_list.remove(adjusted_stock)
        blk_file = self._get_blk_file_path(name)
        
        try:
            with open(blk_file, 'w', encoding='gbk') as file:
                for code in stock_list:
                    file.writelines(f"{code}\n")
            print(f'[{adjusted_stock}] 从自选股 [{name}] 中删除成功')
        except Exception as e:
            print(f'错误：删除股票 [{adjusted_stock}] 失败 - {str(e)}')

    def del_tdx_stock_list(self, name: str = 'QMTCG', user_stock_list: List[str] = ['000001']) -> None:
        """
        批量删除通达信自选股成分股

        Args:
            name: 板块名称，默认名称为 'QMTCG'
            user_stock_list: 股票代码列表，默认列表为 ['000001']
        """
        # 检查板块是否存在
        if not self._is_blk_exists(name):
            print(f'[{name}] 自选股不存在，无法删除股票')
            return

        # 读取现有股票列表
        df = self.read_tdx_stock(name)
        if df.empty:
            print(f'[{name}] 自选股无数据，无需删除')
            return
        
        stock_list = df['证券代码'].tolist()
        deleted_stocks = []
        non_existent_stocks = []

        # 批量处理删除
        for stock in user_stock_list:
            adjusted_stock = self.adjust_stock(stock)
            if adjusted_stock in stock_list:
                stock_list.remove(adjusted_stock)
                deleted_stocks.append(adjusted_stock)
            else:
                non_existent_stocks.append(adjusted_stock)

        # 保存更新后的股票列表
        blk_file = self._get_blk_file_path(name)
        try:
            with open(blk_file, 'w', encoding='gbk') as file:
                for code in stock_list:
                    file.writelines(f"{code}\n")
            
            # 输出统计信息
            if non_existent_stocks:
                print(f'以下股票不在 [{name}] 中，无法删除: {", ".join(non_existent_stocks)}')
            if deleted_stocks:
                print(f'以下股票从 [{name}] 中删除成功: {", ".join(deleted_stocks)}')
        except Exception as e:
            print(f'错误：批量删除股票失败 - {str(e)}')

    def del_all_tdx_stock(self, name: str = 'QMTCG') -> None:
        """
        清空通达信自选股所有股票

        Args:
            name: 板块名称，默认名称为 'QMTCG'
        """
        # 检查板块是否存在
        if not self._is_blk_exists(name):
            print(f'[{name}] 自选股不存在，无法清空')
            return

        # 清空文件
        blk_file = self._get_blk_file_path(name)
        try:
            with open(blk_file, 'w', encoding='gbk') as file:
                file.writelines('')
            print(f'[{name}] 板块内容清空成功')
        except Exception as e:
            print(f'错误：清空板块 [{name}] 失败 - {str(e)}')


if __name__ == '__main__':
    # 初始化实例（修改为你的通达信板块路径）
    tdx_api = XgTdx(path=r'/mnt/D/ProgramData/tdx_new/T0002/blocknew')
    
    # 读取 BUY1 板块的股票（标准格式）
    stock_df = tdx_api.read_tdx_stock_1(name='BUY1')
    print("BUY1 板块成分股：")
    print(stock_df)