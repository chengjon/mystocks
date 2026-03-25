# TQLEX服务接口使用说明

## 接口概述

TQLEX是通达信的一种数据服务协议，本项目使用的TQLEX服务接口部署在第三方服务器上，用于获取股票行情数据。

## 接口信息

### 基本信息
- **接口地址**: `http://excalc.icfqs.com:7616/TQLEX?Entry=HQServ.hq_nlp`
- **协议类型**: HTTP POST
- **数据格式**: JSON
- **认证方式**: Token认证

### 接口功能
目前项目中实现的功能：
1. 早盘抢筹数据获取（period=0）
2. 尾盘抢筹数据获取（period=1）

## 使用方法

### 请求参数说明

```json
{
  "funcId": 20,
  "offset": 0,
  "count": 100,
  "sort": 1,
  "period": 0,
  "Token": "6679f5cadca97d68245a086793fc1bfc0a50b487487c812f",
  "modname": "JJQC"
}
```

#### 参数详解：
- `funcId`: 功能ID，20表示抢筹功能
- `offset`: 数据偏移量，用于分页
- `count`: 返回数据条数
- `sort`: 排序方式（1-5分别代表不同排序字段）
- `period`: 时间段（0=早盘，1=尾盘）
- `Token`: 认证令牌
- `modname`: 模块名称（JJQC可能表示"竞价抢筹"）
- `date`: 可选参数，用于获取指定日期的数据（格式：YYYYMMDD）

### Python使用示例

```python
import pandas as pd
import requests

def get_chip_race_data(period=0, date=""):
    """
    获取抢筹数据
    :param period: 0=早盘, 1=尾盘
    :param date: 日期格式YYYYMMDD，空字符串表示当日
    :return: pandas.DataFrame
    """
    url = "http://excalc.icfqs.com:7616/TQLEX?Entry=HQServ.hq_nlp"
    
    params = [{
        "funcId": 20,
        "offset": 0,
        "count": 100,
        "sort": 1,
        "period": period,
        "Token": "6679f5cadca97d68245a086793fc1bfc0a50b487487c812f",
        "modname": "JJQC"
    }]
    
    if date:
        params[0]["date"] = date
    
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 TdxW",
    }
    
    response = requests.post(url, json=params, headers=headers)
    data_json = response.json()
    data = data_json["datas"]
    
    if not data:
        return pd.DataFrame()
    
    df = pd.DataFrame(data)
    # 数据处理...
    return df

# 使用示例
# 获取早盘抢筹数据
open_race_data = get_chip_race_data(period=0)

# 获取尾盘抢筹数据
end_race_data = get_chip_race_data(period=1)

# 获取指定日期的抢筹数据
historical_data = get_chip_race_data(period=0, date="20251010")
```

## 返回数据格式

### 早盘抢筹数据字段说明：
- 代码：股票代码
- 名称：股票名称
- 昨收：昨日收盘价
- 今开：今日开盘价
- 开盘金额：开盘成交金额
- 抢筹幅度：抢筹幅度（%）
- 抢筹委托金额：抢筹委托金额
- 抢筹成交金额：抢筹成交金额
- 最新价：最新成交价

### 尾盘抢筹数据字段说明：
与早盘抢筹数据类似，但"开盘金额"字段为"收盘金额"。

## 使用要求和注意事项

### 1. 访问限制
- 使用固定的Token进行认证
- 建议控制访问频率，避免被限制访问
- 接口可能有并发访问限制

### 2. 代理使用
建议使用代理池来避免IP被封禁：
```python
import random

# 代理列表示例
proxies_list = [
    "http://proxy1:port",
    "http://proxy2:port",
    "http://proxy3:port"
]

# 随机选择代理
proxy = random.choice(proxies_list)
proxies = {"http": proxy, "https": proxy}

response = requests.post(url, json=params, headers=headers, proxies=proxies)
```

### 3. 错误处理
```python
try:
    response = requests.post(url, json=params, headers=headers, timeout=10)
    response.raise_for_status()
    data_json = response.json()
except requests.exceptions.RequestException as e:
    print(f"请求错误: {e}")
except ValueError as e:
    print(f"JSON解析错误: {e}")
```

### 4. 数据处理
- 价格数据需要除以10000得到实际价格
- 抢筹幅度需要乘以100得到百分比
- 需要计算涨跌幅和抢筹占比等衍生数据

## 扩展功能

虽然目前只实现了抢筹数据功能，但该接口可能支持其他功能：
- 通过修改`funcId`参数可以调用不同的功能
- 通过修改`sort`参数可以按不同字段排序（1-5）
- 通过修改`period`参数可以获取不同时段的数据

## 风险提示

1. **非官方接口**：此接口不是通达信官方提供的接口，可能存在不稳定风险
2. **法律风险**：未经授权大量抓取数据可能涉及法律问题
3. **服务可用性**：第三方服务可能随时停止或变更
4. **数据准确性**：数据的准确性和实时性无法保证

建议在使用前确认接口的合法性和可用性，并做好异常处理和数据缓存。