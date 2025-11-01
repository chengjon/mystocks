#"D:\ProgramData\tdx_new\vipdoc\sh\lday\sh000001.day"

# -*- coding: utf-8 -*-
"""
Created on Wed Mar  5 13:28:29 2025
@author: CHENGJUN
"""

import struct
from datetime import datetime
import pandas as pd


def read_day_file(file_path):
    """
    读取日线文件并解析数据。

    参数：
    file_path (str): 日线文件的路径。

    返回值：
    list: 解析后的数据列表，每个元素是一个字典，包含日期、开盘价、最高价、最低价、收盘价、成交额和成交量。
    """
    # 列名列表
    cols = ["date", "open", "high", "low", "close", "amount", "vol"]

    # 使用with语句打开文件，确保文件在读取后正确关闭
    with open(file_path, "rb") as ofile:
        # 读取文件内容
        buf = ofile.read()

    # 使用struct.iter_unpack直接迭代解析二进制数据
    items = [
        {
            cols[0]: datetime.strptime(str(record[0]), "%Y%m%d").strftime("%Y-%m-%d"),  # 日期
            cols[1]: str(record[1] / 100.0),  # 开盘价（保留原始精度）
            cols[2]: str(record[2] / 100.0),  # 最高价（保留原始精度）
            cols[3]: str(record[3] / 100.0),  # 最低价（保留原始精度）
            cols[4]: str(record[4] / 100.0),  # 收盘价（保留原始精度）
            cols[5]: str(record[5]),  # 成交额
            cols[6]: str(record[6] / 100.0),  # 成交量
        }
        for record in struct.iter_unpack("IIIIIfII", buf)
    ]

    # 返回解析后的数据列表
    return items


if __name__ == "__main__":
    file_path = r"D:\ProgramData\tdx_new\vipdoc\sh\lday\sh000001.day"
    content = read_day_file(file_path)
    df = pd.DataFrame(content)
    print(df)