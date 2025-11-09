# -*- coding: utf-8 -*-
"""
Created on Mon May 15 10:01:46 2023
@author: CHENGJUN
update: 2025-09-12

功能介绍：这是用来把dataframe保存到mysql的必备转化工具，可根据dataframe生成SQL建表命令
          这个版本是更新过的，它支持设置primary_key和字符集utf8mb4
          
修改日期：2025-09-12
修改内容：增加了对大整数的支持，自动选择INT或BIGINT类型
"""
import pandas as pd
from sqlalchemy import create_engine
import pymysql as py


def create_sql_cmd(df, table_name, primary_key=None):
    # 检查DataFrame是否为空
    if df.empty:
        raise ValueError("DataFrame 不能为空")

    # 获取DataFrame的列名和数据类型
    columns = df.dtypes.index.tolist()
    dtypes = df.dtypes.values.tolist()

    # 创建表的SQL语句，设置默认字符集为utf8mb4以支持中文
    create_table_query = f"CREATE TABLE {table_name} ("

    # 构建列的定义
    for col, dtype in zip(columns, dtypes):
        if pd.api.types.is_object_dtype(dtype) or pd.api.types.is_string_dtype(dtype):
            max_length = df[col].astype(str).apply(len).max()  # 获取列数据的最大长度
            varchar_length = min(max_length, 255)  # 限制VARCHAR长度最大为255
            create_table_query += f"{col} VARCHAR({varchar_length}), "
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            create_table_query += f"{col} DATETIME, "  # 使用DATETIME而不是DATE
        elif pd.api.types.is_float_dtype(dtype):
            max_decimals = df[col].apply(lambda x: len(str(x).split('.')[-1])).max()  # 获取浮点数小数点后的最大位数
            float_length = min(max_decimals + 4, 38)  # 限制FLOAT小数点后数据长度最大为38
            create_table_query += f"{col} FLOAT({float_length}), "
        elif pd.api.types.is_integer_dtype(dtype):
            # 检查整数的范围，如果超过INT范围则使用BIGINT
            max_value = df[col].max()
            min_value = df[col].min()
            if max_value > 2147483647 or min_value < -2147483648:
                create_table_query += f"{col} BIGINT, "
            else:
                create_table_query += f"{col} INT, "
        elif pd.api.types.is_bool_dtype(dtype):
            create_table_query += f"{col} TINYINT, "
        elif pd.api.types.is_decimal_dtype(dtype):
            create_table_query += f"{col} DECIMAL(10, 2), "  # 假设DECIMAL类型，精度和小数位数可根据需要调整
        elif pd.api.types.is_categorical_dtype(dtype):
            create_table_query += f"{col} VARCHAR(255), "  # 将分类数据视为VARCHAR
        else:
            create_table_query += f"{col} TEXT, "

    # 添加主键定义
    if primary_key:
        create_table_query += f"PRIMARY KEY ({primary_key}), "

    create_table_query = create_table_query.rstrip(', ') + ") CHARACTER SET utf8mb4"

    # 返回创建表的SQL语句
    return create_table_query