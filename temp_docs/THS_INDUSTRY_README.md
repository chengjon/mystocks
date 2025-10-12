# 同花顺行业数据获取功能文档

## 功能概述

基于akshare的 `stock_board_industry_summary_ths` 接口，在 `akshare_adapter.py` 中新增了三个方法来获取同花顺行业相关数据：

1. **获取同花顺行业一览表** - `get_ths_industry_summary()`
2. **获取同花顺行业名称列表** - `get_ths_industry_names()`  
3. **获取指定行业成分股数据** - `get_ths_industry_stocks(industry_name)`

## 功能详情

### 1. 获取同花顺行业一览表

**方法签名：**
```python
def get_ths_industry_summary(self) -> pd.DataFrame
```

**功能描述：**
- 获取同花顺网站的行业板块数据
- 包含行业名称、最新价、涨跌幅、涨跌额、成交量、成交额、领涨股等信息

**返回数据列:**
- 序号: 排序号
- 板块: 行业名称
- 涨跌幅: 行业涨跌幅百分比
- 总成交量: 该行业总成交量
- 总成交额: 该行业总成交金额
- 净流入: 资金净流入情况
- 上涨家数/下跌家数: 行业内上涨和下跌股票数量
- 均价: 行业平均价格
- 领涨股: 该行业领涨股票
- 领涨股-最新价: 领涨股最新价格
- 领涨股-涨跌幅: 领涨股涨跌幅
- 数据获取时间: 数据获取的时间戳

**使用示例：**
```python
from adapters.akshare_adapter import AkshareDataSource

adapter = AkshareDataSource()
industry_data = adapter.get_ths_industry_summary()
print(industry_data.head())
```

### 2. 获取同花顺行业名称列表

**方法签名：**
```python
def get_ths_industry_names(self) -> pd.DataFrame
```

**功能描述：**
- 获取同花顺的所有行业名称和代码列表
- 可用于查看所有可用的行业分类

**返回数据列:**
- name: 行业名称
- code: 行业代码
- 数据获取时间: 数据获取的时间戳

**使用示例：**
```python
adapter = AkshareDataSource()
industry_names = adapter.get_ths_industry_names()
print(f"共有 {len(industry_names)} 个行业分类")
print(industry_names[['name', 'code']].head(10))
```

### 3. 获取指定行业成分股数据

**方法签名：**
```python
def get_ths_industry_stocks(self, industry_name: str) -> pd.DataFrame
```

**功能描述：**
- 获取指定行业下的所有成分股信息
- 注意：由于akshare的接口限制，此方法使用东方财富的行业成分股接口

**参数：**
- `industry_name` (str): 行业名称，例如："银行", "白酒", "风电设备" 等

**返回数据列:**
- 序号: 排序号
- 代码: 股票代码
- 名称: 股票名称
- 最新价: 最新价格
- 涨跌幅: 涨跌幅百分比
- 涨跌额: 涨跌绝对值
- 成交量: 成交量
- 成交额: 成交金额
- 振幅: 股价振幅
- 最高/最低: 当日最高价/最低价
- 今开/昨收: 今日开盘价/昨日收盘价
- 换手率: 换手率
- 市盈率-动态: 动态市盈率
- 市净率: 市净率
- 所属行业: 行业名称
- 数据获取时间: 数据获取的时间戳

**使用示例：**
```python
adapter = AkshareDataSource()

# 获取银行行业成分股
bank_stocks = adapter.get_ths_industry_stocks("银行")
print(f"银行行业共有 {len(bank_stocks)} 只股票")

# 获取白酒行业成分股
baijiu_stocks = adapter.get_ths_industry_stocks("白酒")
print(f"白酒行业共有 {len(baijiu_stocks)} 只股票")
```

## 完整使用示例

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from adapters.akshare_adapter import AkshareDataSource

def demo_ths_industry_data():
    """演示同花顺行业数据获取功能"""
    
    # 初始化数据源
    adapter = AkshareDataSource()
    
    # 1. 获取行业一览表
    print("=== 获取同花顺行业一览表 ===")
    industry_summary = adapter.get_ths_industry_summary()
    print(f"共获取到 {len(industry_summary)} 个行业的数据")
    print("涨幅前5的行业:")
    top5_industries = industry_summary.head()
    for _, row in top5_industries.iterrows():
        print(f"  {row['板块']}: {row['涨跌幅']}%")
    
    # 2. 获取行业名称列表  
    print("\\n=== 获取行业名称列表 ===")
    industry_names = adapter.get_ths_industry_names()
    print(f"共有 {len(industry_names)} 个行业分类")
    print("前10个行业:")
    for _, row in industry_names.head(10).iterrows():
        print(f"  {row['name']} (代码: {row['code']})")
    
    # 3. 获取特定行业的成分股
    print("\\n=== 获取银行行业成分股 ===")
    bank_stocks = adapter.get_ths_industry_stocks("银行")
    if not bank_stocks.empty:
        print(f"银行行业共有 {len(bank_stocks)} 只股票")
        print("市值前5的银行股:")
        for _, row in bank_stocks.head().iterrows():
            print(f"  {row['代码']} {row['名称']}: {row['最新价']}元 ({row['涨跌幅']}%)")
    
    # 4. 保存数据到文件
    industry_summary.to_csv("同花顺行业一览表.csv", index=False, encoding='utf-8-sig')
    industry_names.to_csv("同花顺行业名称列表.csv", index=False, encoding='utf-8-sig')
    if not bank_stocks.empty:
        bank_stocks.to_csv("银行行业成分股.csv", index=False, encoding='utf-8-sig')
    
    print("\\n✅ 数据已保存到CSV文件")

if __name__ == "__main__":
    demo_ths_industry_data()
```

## 注意事项

1. **数据来源差异**: 
   - `get_ths_industry_summary()` 使用同花顺数据源
   - `get_ths_industry_stocks()` 使用东方财富数据源（因为akshare的限制）

2. **重试机制**: 所有方法都内置了重试机制，API调用失败时会自动重试3次

3. **错误处理**: 当网络异常或数据不可用时，方法会返回空的DataFrame并输出错误信息

4. **数据时效性**: 数据为实时或近实时数据，每次调用都会获取最新信息

5. **性能考虑**: 建议合理控制调用频率，避免对数据源造成过大压力

## 测试脚本

已提供完整的测试脚本 `test_ths_industry.py`，可直接运行测试所有功能：

```bash
python test_ths_industry.py
```

测试脚本会自动：
- 测试所有三个功能
- 输出详细的执行日志
- 保存数据到CSV文件
- 显示数据预览和统计信息