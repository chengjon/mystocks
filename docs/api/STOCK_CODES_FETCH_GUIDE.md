# 获取 A 股股票代码 - 完整指南

> **使用说明**:
> 本文件是 API 相关的参考文档或专题说明，不是当前 API 契约、当前实施基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内端点、命令、统计值和示例如未重新复核，应视为参考或历史材料，不得直接当作当前事实。


**Historical Last Updated Snapshot**: 2026-01-02
**Historical Document Version Snapshot**: v1.0

本文档介绍如何使用多种方法获取 A 股市场所有股票代码。

---

## 📊 方法对比

| 方法 | 数据源 | 优点 | 缺点 | 推荐度 |
|------|--------|------|------|--------|
| **EasyQuotation** | 腾讯/新浪 | 免费、简单、快速 | 数据较少 | ⭐⭐⭐⭐⭐ |
| **麦蕊数据 API** | 麦蕊 | 数据详细 | 需要注册 | ⭐⭐⭐ |
| **efinance** | 东方财富 | 数据丰富 | 接口较重 | ⭐⭐⭐⭐ |
| **baostock** | baostock | 历史数据完整 | 需要登录 | ⭐⭐⭐ |

---

## 🚀 方法 1: EasyQuotation (推荐)

### 接口说明

**接口**: `eq.update_stock_codes()`
**文档位置**: Line 914-932

### 代码示例

```python
import easyquotation as eq
import pandas as pd

# 选择数据源
quotation = eq.use('tencent')  # 或 'sina'（新浪）

# 更新并获取所有股票代码
codes = eq.update_stock_codes()

# 查看结果
print(f"总共获取 {len(codes)} 只股票")
print(f"示例代码: {codes[:10]}")

# 转换为 DataFrame
df_codes = pd.DataFrame({'code': codes})
print(df_codes.head(10))
```

### 返回数据格式

```
['000001', '000002', '000004', '000005', '000006', '000007', '000008', '000009', '000010', ...]
```

- **数据类型**: list
- **内容**: 所有 A 股股票代码（6位数字）
- **数量**: 约 5000+ 只股票

### 完整函数封装

```python
def fetch_stock_codes_easyquotation():
    """使用 EasyQuotation 获取所有 A 股代码"""
    try:
        import easyquotation as eq

        # 更新并获取股票代码
        codes = eq.update_stock_codes()

        if codes:
            print(f"✅ 成功获取 {len(codes)} 只股票代码")
            return codes
        else:
            print("❌ 未获取到股票代码")
            return []

    except ImportError:
        print("❌ 请先安装: pip install easyquotation")
        return []
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        return []
```

---

## 🚀 方法 2: 麦蕊数据 API

### 接口说明

**接口**: `https://api.mairui.club/hslt/list/{api_key}`
**文档位置**: Line 935-949
**需要**: API 密钥（需要注册）

### 代码示例

```python
import requests
import pandas as pd

# 替换为你的 API 密钥
api_key = "your_api_key_here"

# 请求数据
url = f"https://api.mairui.club/hslt/list/{api_key}"
response = requests.get(url, timeout=10)

# 解析 JSON
data = response.json()
df = pd.DataFrame(data)

# 查看结果
print(f"总共获取 {len(df)} 只股票")
print(df.head())
```

### 返回数据格式

```json
[
  {
    "code": "000001",
    "name": "平安银行",
    "industry": "银行",
    "market": "深证主板"
  },
  ...
]
```

### 注册获取 API 密钥

1. 访问: https://www.mairui.club/
2. 注册账号
3. 获取 API 密钥
4. 免费额度: 一定次数/天的免费调用

### 完整函数封装

```python
def fetch_stock_codes_mairui(api_key: str):
    """使用麦蕊数据 API 获取所有 A 股代码"""
    try:
        import requests

        url = f"https://api.mairui.club/hslt/list/{api_key}"
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data)

            print(f"✅ 成功获取 {len(df)} 只股票")
            return df
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return pd.DataFrame()

    except ImportError:
        print("❌ 请先安装: pip install requests")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ 获取失败: {e}")
        return pd.DataFrame()
```

---

## 🚀 方法 3: efinance

### 代码示例

```python
import efinance as ef

# 获取沪深 A 股实时行情
df = ef.stock.get_realtime_quotes()

# 提取股票代码
stock_codes = df['股票代码'].tolist()

print(f"总共获取 {len(stock_codes)} 只股票")
print(stock_codes[:10])
```

### 优缺点

✅ **优点**:
- 数据丰富（包含行情、行业等）
- 更新快
- 免费

❌ **缺点**:
- 接口较重，返回数据量大
- 网络不稳定时容易超时

---

## 🚀 方法 4: baostock

### 代码示例

```python
import baostock as bs
import pandas as pd

# 登陆系统
lg = bs.login()

# 获取证券信息
rs = bs.query_stock_basic()

# 打印结果
data_list = []
while (rs.error_code == '0') & rs.next():
    data_list.append(rs.get_row_data())

df = pd.DataFrame(data_list, columns=rs.fields)

# 提取股票代码
stock_codes = df['code'].tolist()

print(f"总共获取 {len(stock_codes)} 只股票")
bs.logout()
```

### 优缺点

✅ **优点**:
- 历史数据完整
- 适合回测
- 免费

❌ **缺点**:
- 需要登录
- 数据更新可能不及时
- 返回格式较复杂

---

## 📋 完整对比测试脚本

已生成完整测试脚本: `scripts/fetch_market_data_multi_source.py`

### 运行脚本

```bash
cd /opt/claude/mystocks_spec
python scripts/fetch_market_data_multi_source.py
```

### 脚本功能

脚本包含 6 个主要任务:

1. **获取股票所属板块** (efinance)
   - `ef.stock.get_belong_board('300377')`

2. **查询股票行业信息** (baostock)
   - `bao.query_stock_industry('300377')`

3. **获取全市场实时行情** (efinance)
   - `ef.stock.get_realtime_quotes()`

4. **获取全市场快照** (easyquotation)
   - `quotation.market_snapshot(prefix=True)`

5. **获取所有股票代码** (easyquotation) ⭐ 新增
   - `eq.update_stock_codes()`

6. **获取所有股票代码** (麦蕊数据) ⭐ 新增
   - `https://api.mairui.club/hslt/list/{api_key}`

### 输出文件

所有数据保存在 `/tmp` 目录，文件名包含时间戳:

```
stock_belong_board_300377_20260102_022330.csv
stock_industry_300377_20260102_022330.csv
market_realtime_cyb_20260102_022330.csv
market_snapshot_tencent_20260102_022330.csv
stock_codes_all_easyquotation_20260102_022330.csv  ⭐ 新增
```

---

## 💡 使用建议

### 场景 1: 快速获取股票代码列表

**推荐**: EasyQuotation

```python
import easyquotation as eq

codes = eq.update_stock_codes()
print(f"获取到 {len(codes)} 只股票")
```

### 场景 2: 获取详细股票信息

**推荐**: 麦蕊数据 API

```python
df = fetch_stock_codes_mairui("your_api_key")
# 包含: 代码、名称、行业、市场等详细信息
```

### 场景 3: 实时行情 + 股票代码

**推荐**: efinance

```python
import efinance as ef

# 一次性获取股票代码和行情
df = ef.stock.get_realtime_quotes()
stock_codes = df['股票代码'].tolist()
```

### 场景 4: 历史回测

**推荐**: baostock

```python
import baostock as bs

# 获取历史数据完整的股票列表
lg = bs.login()
rs = bs.query_stock_basic()
# ... 处理数据
bs.logout()
```

---

## ⚠️ 注意事项

1. **网络环境**: 所有方法都需要网络连接
2. **请求频率**: 建议控制请求频率，避免被限流
3. **API 密钥**: 麦蕊数据需要注册获取密钥
4. **数据时效**:
   - EasyQuotation: 实时更新
   - efinance: 15-30秒延迟
   - baostock: T+1 数据
5. **错误处理**: 所有函数都有 try-except 保护

---

## 🔗 相关文档

- **原始文档**: `/opt/mydoc/mymd/Astock_data_source.md`
- **完整脚本**: `scripts/fetch_market_data_multi_source.py`
- **AkShare 接口**: `docs/api/AKSHARE_INTERFACE_MAPPING.md`

---

## 📚 扩展阅读

### EasyQuotation 文档

- GitHub: https://github.com/shidenggui/easyquotation
- 支持: 新浪、腾讯、集思录

### efinance 文档

- 官方文档: https://efinance.readthedocs.io/
- 数据源: 东方财富网

### baostock 文档

- 官方文档: http://baostock.com/
- 特点: 免费、历史数据完整

---

**Historical Maintainer Snapshot**: Claude Code
**Historical Last Updated Snapshot**: 2026-01-02
