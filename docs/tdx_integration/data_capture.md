# 数据抓取功能说明

## 功能概述

本项目的数据抓取功能主要通过读取本地通达信软件导出的数据文件来实现，避免了网络爬虫的不稳定性。数据抓取模块负责从通达信软件获取原始数据，并进行初步处理和存储。

## 核心组件

### 1. readTDX_lday.py - 日线数据读取和处理

#### 功能说明
- 从通达信本地数据文件读取日线数据
- 处理深市和沪市股票数据
- 导出指数数据（上证指数、沪深300等）
- 对数据进行前复权处理
- 支持增量更新和全量重新生成

#### 使用方法
```bash
# 正常执行，追加最新数据
python readTDX_lday.py

# 删除现有数据并重新生成完整数据
python readTDX_lday.py del

# 使用单进程执行（默认使用多进程）
python readTDX_lday.py single
```

#### 核心代码示例
```python
# 读取通达信日线数据并转换为CSV格式
def day2csv(source_dir, file_name, target_dir):
    """
    将通达信的日线文件转换成CSV格式保存函数。通达信数据文件32字节为一组
    :param source_dir: str 源文件路径
    :param file_name: str 文件名
    :param target_dir: str 要保存的路径
    :return: none
    """
    from struct import unpack
    from decimal import Decimal  # 用于浮点数四舍五入

    # 以二进制方式打开源文件
    source_path = source_dir + os.sep + file_name  # 源文件包含文件名的路径
    source_file = open(source_path, 'rb')
    buf = source_file.read()  # 读取源文件保存在变量中
    source_file.close()
    source_size = os.path.getsize(source_path)  # 获取源文件大小
    source_row_number = int(source_size / 32)

    # 转换数据并保存为CSV格式
    # ... 数据处理逻辑 ...
```

### 2. readTDX_cw.py - 财务数据读取

#### 功能说明
- 读取通达信专业财务数据
- 处理股本变迁数据
- 自动判断财务数据是否需要更新
- 将数据保存为CSV和pickle格式

#### 核心代码示例
```python
# 读取解析通达信目录的历史财务数据
def historyfinancialreader(filepath):
    """
    读取解析通达信目录的历史财务数据
    :param filepath: 字符串类型。传入文件路径
    :return: DataFrame格式。返回解析出的财务文件内容
    """
    import struct

    cw_file = open(filepath, 'rb')
    header_pack_format = '<1hI1H3L'
    header_size = struct.calcsize(header_pack_format)
    stock_item_size = struct.calcsize("<6s1c1L")
    data_header = cw_file.read(header_size)
    stock_header = struct.unpack(header_pack_format, data_header)
    max_count = stock_header[2]
    report_date = stock_header[1]
    report_size = stock_header[4]
    report_fields_count = int(report_size / 4)
    report_pack_format = '<{}f'.format(report_fields_count)
    results = []
    for stock_idx in range(0, max_count):
        cw_file.seek(header_size + stock_idx * struct.calcsize("<6s1c1L"))
        si = cw_file.read(stock_item_size)
        stock_item = struct.unpack("<6s1c1L", si)
        code = stock_item[0].decode("utf-8")
        foa = stock_item[2]
        cw_file.seek(foa)
        info_data = cw_file.read(struct.calcsize(report_pack_format))
        data_size = len(info_data)
        cw_info = list(struct.unpack(report_pack_format, info_data))
        cw_info.insert(0, code)
        results.append(cw_info)
    cw_file.close()
    df = pd.DataFrame(results)
    return df
```

## 数据处理流程

1. **数据源准备**：用户需在通达信软件中下载日线数据和专业财务数据
2. **数据读取**：通过readTDX_lday.py和readTDX_cw.py读取本地数据文件
3. **数据转换**：将二进制格式的通达信数据转换为CSV格式
4. **前复权处理**：对股票价格数据进行前复权计算，保证数据准确性
5. **数据存储**：将处理后的数据保存为CSV和pickle格式，提高读取效率

## 配置说明

在user_config.py中配置数据路径：

```python
tdx = {
    'tdx_path': 'd:/stock/通达信',      # 通达信安装目录
    'csv_lday': 'd:/TDXdata/lday_qfq', # 日线数据保存目录
    'pickle': 'd:/TDXdata/pickle',     # pickle格式数据保存目录
    'csv_index': 'd:/TDXdata/index',   # 指数数据保存目录
    'csv_cw': 'd:/TDXdata/cw',         # 财务数据保存目录
    'csv_gbbq': 'd:/TDXdata',          # 股本变迁数据保存目录
}
```

## 注意事项

1. 需要先在通达信软件中下载完整的日线数据和专业财务数据
2. 建议使用固态硬盘存储数据，提高处理性能
3. 日线数据每天16点后更新，需要手动或设置自动更新
4. 前复权处理保证了数据与通达信软件显示的一致性
