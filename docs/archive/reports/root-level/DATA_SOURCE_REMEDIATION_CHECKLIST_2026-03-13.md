# MyStocks 数据源剩余修复清单

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、执行清单或整改建议，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值、时间线和建议动作如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


> 依据: `reports/DATA_SOURCE_INSPECTION_REPORT_FINAL_2026-03-12.md`
> 目标: 只覆盖当前仍未收口的问题，不重复已经修完的 Redis / Mongo / registry / runtime contract 工作

---

## P0

### 1. Tushare 不可用

当前状态:

- `TUSHARE_TOKEN` 未设置
- `TushareDataSource()` 初始化失败

处理动作:

1. 在目标运行环境设置 `TUSHARE_TOKEN`
2. 重新执行最小初始化探针
3. 再补一个最小业务探针

建议验证命令:

```bash
python - <<'PY'
from dotenv import load_dotenv
load_dotenv('.env')
from src.adapters.tushare_adapter import TushareDataSource
ds = TushareDataSource()
print(type(ds).__name__)
PY
```

完成标准:

- 初始化不再抛出 `ImportError`
- 至少一个 Tushare 业务接口返回非空结果

### 2. Byapi 不可用

当前状态:

- `ByapiAdapter().get_stock_list()` 返回 `403 Forbidden`

处理动作:

1. 与 Byapi 提供方确认当前 license 是否仍有效
2. 确认是否需要切换到新的 base URL、鉴权头或 license
3. 修复后重新跑 stock list 探针

建议验证命令:

```bash
python - <<'PY'
from src.adapters.byapi_adapter import ByapiAdapter
df = ByapiAdapter().get_stock_list()
print(len(df))
PY
```

完成标准:

- 不再返回 `403`
- `get_stock_list()` 返回非空 DataFrame

---

## P1

### 3. WebData 的 Sina 关键字搜索需单独确认

当前状态:

- `get_tencent_daily_kline('sz000001')` 返回 `100` rows
- `get_sina_keyword_search('000001')` 返回 `0` rows

处理动作:

1. 确认 `get_sina_keyword_search()` 的参数约束是否变化
2. 用股票名称、代码、带交易所前缀三种输入各试一次
3. 若接口已退化，标记为降级能力并调整优先级配置

建议验证命令:

```bash
python - <<'PY'
from src.adapters.webdata.webdata_adapter import WebDataAdapter
adapter = WebDataAdapter()
for q in ['000001', 'sz000001', '平安银行']:
    data = adapter.get_sina_keyword_search(q)
    print(q, len(data) if data is not None else -1)
PY
```

完成标准:

- 明确这是“参数问题”还是“接口退化”
- 若退化，文档和优先级配置同步更新

### 4. `easyquotation` fallback 缺失

当前状态:

- `FinancialDataSource` 当前主路径可用
- `easyquotation` 未安装，fallback 能力缺失

处理动作:

1. 决定本项目是否仍需要 `easyquotation` 作为 fallback
2. 若需要，补安装并验证 import
3. 若不需要，更新文档，把它从“要求可用”改成“可选 fallback”

建议验证命令:

```bash
python - <<'PY'
try:
    import easyquotation
    print('available')
except Exception as e:
    print(type(e).__name__, e)
PY
```

完成标准:

- 项目对 `easyquotation` 的定位明确
- 文档、依赖、运行时预期保持一致

---

## 已完成项

以下事项已经不应再进入本轮排障待办:

- Redis 不可连
- MongoDB 不可连
- `DataSourceManagerV2` 重复注册到 `61` 项
- `health_check()` 全量误判 unhealthy
- `TdxDataSource` 抽象类缺方法
- `FinancialDataSource` 状态位初始化后被覆盖

---

## 建议执行顺序

1. 先修 Tushare
2. 再修 Byapi
3. 然后确认 WebData Sina 路径
4. 最后决定 `easyquotation` 是否保留
