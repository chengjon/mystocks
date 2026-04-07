# AkShare 数据接口快速参考

> **设计方案说明**:
> 本文件是 API 相关的设计稿、映射文档或方案说明，不是当前 API 契约、当前实现基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内结构设计、端点规划、映射关系和实施建议应结合当前代码与主线文档复核；若未落地，不得直接当作当前标准。


从 `Astock_data_source.md` 提取的 akshare 数据接口映射

**更新时间**: 2026-01-02
**数据源**: 东方财富网 (通过 AkShare)

---

## 📊 1. 行业板块数据 (stock_industries / industries)

### 获取行业板块列表

**对应文档位置**: Line 97-103
**AkShare 接口**: `ak.stock_board_industry_name_em()`

```python
import akshare as ak

# 获取所有行业板块的实时行情
industry_df = ak.stock_board_industry_name_em()

# 返回字段:
# - 排名、板块名称、板块代码、最新价
# - 涨跌额、涨跌幅、总市值、换手率
# - 上涨家数、下跌家数、领涨股票、领涨股票-涨跌幅
```

### 获取行业成分股

**对应文档位置**: Line 109-116
**AkShare 接口**: `ak.stock_board_industry_cons_em(symbol="板块名称")`

```python
# 获取指定行业的成分股
industry_cons = ak.stock_board_industry_cons_em(symbol="黑色金属")
# 或使用行业代码
industry_cons = ak.stock_board_industry_cons_em(symbol="BK0423")

# 返回字段:
# - 序号、代码、名称、最新价、涨跌幅、涨跌额
# - 成交量、成交额、振幅、最高、最低
# - 今开、昨收、换手率、市盈率-动态、市净率
```

### 其他数据源对比

| 数据源 | 接口 | 缺点 |
|--------|------|------|
| **baostock** | `bs.query_stock_industry()` | 有的股票没行业，数据不全 |
| **efinance** | `ef.stock.get_belong_board(stock_code)` | 仅获取单只股票的行业归属 |

---

## 🏷️ 2. 概念板块数据 (stock_concepts / concepts)

### 获取概念板块列表

**对应文档位置**: Line 97-103
**AkShare 接口**: `ak.stock_board_concept_name_em()`

```python
# 获取所有概念板块的实时行情
concept_df = ak.stock_board_concept_name_em()

# 返回字段:
# - 排名、板块名称、板块代码、最新价
# - 涨跌额、涨跌幅、总市值、换手率
# - 上涨家数、下跌家数、领涨股票、领涨股票-涨跌幅
```

### 获取概念成分股

**对应文档位置**: Line 109-116
**AkShare 接口**: `ak.stock_board_concept_cons_em(symbol="概念名称")`

```python
# 获取指定概念的成分股
concept_cons = ak.stock_board_concept_cons_em(symbol="可燃冰")
# 或使用概念代码
concept_cons = ak.stock_board_concept_cons_em(symbol="BK1051")

# 返回字段:
# - 序号、代码、名称、最新价、涨跌幅、涨跌额
# - 成交量、成交额、振幅、最高、最低
# - 今开、昨收、换手率、市盈率-动态、市净率
```

### 获取概念板块历史走势

**对应文档位置**: Line 134-142
**AkShare 接口**: `ak.stock_board_concept_hist_em()`

```python
# 获取概念板块历史数据
concept_hist = ak.stock_board_concept_hist_em(
    symbol="绿色电力",
    period="daily",
    start_date="20240101",
    end_date="20241231",
    adjust=""  # 复权类型: ""/"qfq"/"hfq"
)

# 返回字段:
# - 日期、开盘、收盘、最高、最低
# - 涨跌幅、涨跌额、成交量、成交额
# - 振幅、换手率
```

### 获取概念板块实时行情

**对应文档位置**: Line 148-153
**AkShare 接口**: `ak.stock_board_concept_spot_em()`

```python
# 获取概念板块实时行情
concept_spot = ak.stock_board_concept_spot_em(symbol="可燃冰")

# 返回字段:
# - 最新、最高、最低、开盘
# - 成交量、成交额、换手率
# - 涨跌额、涨跌幅、振幅
```

### 获取概念板块分时数据

**对应文档位置**: Line 122-128
**AkShare 接口**: `ak.stock_board_concept_hist_min_em()`

```python
# 获取概念板块分钟级走势
concept_min = ak.stock_board_concept_hist_min_em(
    symbol="赛马概念",
    period="1"  # 1, 5, 15, 30, 60 分钟
)

# 返回字段:
# - 日期时间、开盘、收盘、最高、最低
# - 成交量、成交额、最新价
```

---

## 📈 3. 股票基本信息 (stocks_basic / symbols_info / stock_info)

### 获取所有股票代码和名称

**AkShare 接口**: `ak.stock_info_a_code_name()`

```python
# 获取 A 股所有股票代码和名称
stock_list = ak.stock_info_a_code_name()

# 返回字段:
# - code: 股票代码
# - name: 股票名称

# 或分市场获取
# 上海市场
sh_list = ak.stock_info_sh_name_code(indicator="主板A股")
# 深圳市场
sz_list = ak.stock_info_sz_name_code(indicator="A股列表")
```

### 获取单只股票详细信息

**AkShare 接口**: `ak.stock_individual_info_em(symbol="股票代码")`

```python
# 获取单只股票的详细信息
stock_info = ak.stock_individual_info_em(symbol="000001")

# 返回: DataFrame with item/value 列
# 包含: 股票代码、股票名称、总市值、流通市值、
#      行业、市盈率(动)、市净率、毛利率、净利率等
```

### 对比: efinance 接口

**对应文档位置**: Line 726-748

```python
import efinance as ef

# 获取单只/多只股票基本信息
stock_base_info = ef.stock.get_base_info(stock_codes=['600519', '300715'])

# 返回字段:
# - 股票代码、股票名称、净利润、总市值、流通市值
# - 所处行业、市盈率(动)、市净率、ROE
# - 毛利率、净利率、板块编号
```

---

## 📊 4. 股票历史行情数据

### 获取日线数据

**对应文档位置**: Line 210-222
**AkShare 接口**: `ak.stock_zh_a_hist()`

```python
# 获取单只股票日线数据
stock_hist = ak.stock_zh_a_hist(
    symbol="000230",
    period="daily",
    start_date="20240101",
    end_date="20241231",
    adjust="hfq"  # 复权: ""/"qfq"(前)/"hfq"(后)
)

# 返回字段:
# - 日期、股票代码、开盘、收盘、最高、最低
# - 成交量、成交额、振幅、涨跌幅、涨跌额、换手率
```

### 获取分钟数据

**对应文档位置**: Line 258-264
**AkShare 接口**: `ak.stock_zh_a_hist_min_em()`

```python
# 获取分钟级数据
stock_min = ak.stock_zh_a_hist_min_em(
    symbol="002230",
    start_date="2024-05-01 09:30:00",
    end_date="2024-05-22 15:00:00",
    period="1",  # 1, 5, 15, 30, 60 分钟
    adjust=""
)

# 返回字段:
# - 时间、开盘、收盘、最高、最低
# - 成交量、成交额、均价
```

### 对比: efinance 接口

**对应文档位置**: Line 224-270

```python
import efinance as ef

# 获取多只股票历史数据
hist_data = ef.stock.get_quote_history(
    stock_codes=['600519', '300750'],
    beg='20200101',
    end='20241231',
    klt=101,  # 1/5/15/30/60/101(日)/102(周)/103(月)
    fqt=1     # 0: 不复权, 1: 前复权, 2: 后复权
)
```

---

## 🚀 完整脚本

已生成完整的数据获取脚本: `scripts/fetch_akshare_data.py`

**功能**:
1. ✅ 获取行业板块列表 (`stock_industries`)
2. ✅ 获取行业成分股 (`industries` 详细信息)
3. ✅ 获取概念板块列表 (`stock_concepts`)
4. ✅ 获取概念成分股 (`concepts` 详细信息)
5. ✅ 获取股票代码列表 (`stocks_basic` / `symbols_info`)
6. ✅ 获取股票详细信息 (`stock_info`)
7. ✅ 获取历史行情数据

**使用方法**:
```bash
cd /opt/claude/mystocks_spec
python scripts/fetch_akshare_data.py
```

**输出文件**:
- `industry_list_YYYYMMDD_HHMMSS.csv` - 行业板块列表
- `industry_cons_example_YYYYMMDD_HHMMSS.csv` - 行业成分股示例
- `concept_list_YYYYMMDD_HHMMSS.csv` - 概念板块列表
- `concept_cons_example_YYYYMMDD_HHMMSS.csv` - 概念成分股示例
- `stock_list_YYYYMMDD_HHMMSS.csv` - 股票代码列表
- `stock_info_example_YYYYMMDD_HHMMSS.csv` - 股票详细信息示例
- `stock_history_example_YYYYMMDD_HHMMSS.csv` - 股票历史行情示例

---

## 📝 数据字段对照表

### 行业/概念板块列表字段

| 文档字段 | AkShare 返回 | 说明 |
|---------|-------------|------|
| 板块名称 | 板块名称 | 行业/概念名称 |
| 板块代码 | 板块代码 | 如 BK0423, BK1051 |
| 最新价 | 最新价 | 当前价格 |
| 涨跌幅 | 涨跌幅 | 百分比 |
| 总市值 | 总市值 | 亿元 |
| 换手率 | 换手率 | 百分比 |
| 领涨股票 | 领涨股票 | 涨幅最大的股票 |

### 成分股字段

| 文档字段 | AkShare 返回 | 说明 |
|---------|-------------|------|
| 代码 | 代码 | 股票代码 |
| 名称 | 名称 | 股票名称 |
| 最新价 | 最新价 | 当前价格 |
| 涨跌幅 | 涨跌幅 | 百分比 |
| 成交量 | 成交量 | 手 |
| 成交额 | 成交额 | 元 |
| 市盈率-动态 | 市盈率-动态 | TTM 市盈率 |
| 市净率 | 市净率 | 市净率 |

---

## ⚠️ 注意事项

1. **数据源限制**: AkShare 数据来自东方财富网，受限于网站访问频率
2. **请求频率**: 建议每次请求间隔 1 秒，避免被限流
3. **数据延迟**: 实时数据可能有 15-30 秒延迟
4. **复权处理**:
   - `""`: 不复权
   - `"qfq"`: 前复权
   - `"hfq"`: 后复权
5. **错误处理**: 所有函数都有 try-except 保护，失败时返回空 DataFrame

---

## 🔗 相关文档

- **AkShare 官方文档**: https://akshare.akfamily.xyz/data/stock/stock.html
- **原始文档**: `/opt/mydoc/mymd/Astock_data_source.md`
- **生成脚本**: `scripts/fetch_akshare_data.py`

---

**维护者**: Claude Code
**最后更新**: 2026-01-02
