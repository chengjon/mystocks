# 数据源管理工具 - 快速参考卡片

> **版本**: v1.0 | **日期**: 2026-01-02

---

## 🚀 快速开始 (5分钟上手)

### 1. 命令行测试

```bash
# 交互式模式
python scripts/tools/manual_data_source_tester.py --interactive

# 快速测试
python scripts/tools/manual_data_source_tester.py \
    --endpoint akshare.stock_zh_a_hist \
    --symbol 000001 \
    --start-date 20240101 \
    --end-date 20240131 \
    --verbose
```

### 2. API调用

```bash
# 搜索数据源
curl -X GET "http://localhost:8000/api/v1/data-sources/?data_category=DAILY_KLINE" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 测试数据源
curl -X POST "http://localhost:8000/api/v1/data-sources/akshare.stock_zh_a_hist/test" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"test_params": {"symbol": "000001", "start_date": "20240101", "end_date": "20240131"}}'
```

---

## 📋 常用命令

### 手动测试工具

| 场景 | 命令 |
|------|------|
| 交互式测试 | `python scripts/tools/manual_data_source_tester.py -i` |
| 测试日线数据 | `python scripts/tools/manual_data_source_tester.py -e akshare.stock_zh_a_hist -s 000001 --start-date 20240101 --end-date 20240131` |
| 生成报告 | `python scripts/tools/manual_data_source_tester.py -e akshare.stock_zh_a_hist -s 000001 --start-date 20240101 --end-date 20240131 --report` |
| 使用自定义参数 | `python scripts/tools/manual_data_source_tester.py -e akshare.stock_zh_a_hist -p '{"symbol":"000001","period":"daily"}'` |

### API端点

| 功能 | 端点 | 方法 |
|------|------|------|
| 搜索数据源 | `/api/v1/data-sources/` | GET |
| 分类统计 | `/api/v1/data-sources/categories` | GET |
| 数据源详情 | `/api/v1/data-sources/{endpoint_name}` | GET |
| 更新配置 | `/api/v1/data-sources/{endpoint_name}` | PUT |
| 测试接口 | `/api/v1/data-sources/{endpoint_name}/test` | POST |
| 健康检查 | `/api/v1/data-sources/{endpoint_name}/health-check` | POST |
| 批量健康检查 | `/api/v1/data-sources/health-check/all` | POST |

---

## 🔍 搜索参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `data_category` | 数据分类 | `DAILY_KLINE`, `MINUTE_KLINE`, `FINANCIAL_DATA` |
| `source_type` | 数据源类型 | `akshare`, `tushare`, `tdx` |
| `only_healthy` | 仅健康的 | `true`, `false` |
| `keyword` | 关键词搜索 | `日线`, `财务` |
| `status` | 状态筛选 | `active`, `maintenance`, `deprecated` |

---

## 📊 5层数据分类

```
层级1: DAILY_KLINE       → 日线K线数据
层级2: MINUTE_KLINE      → 分钟K线数据
层级3: TICK_DATA         → Tick逐笔数据
层级4: REALTIME_QUOTES   → 实时行情
层级5: REFERENCE_DATA    → 参考数据

其他:  FINANCIAL_DATA    → 财务数据
       INDEX_DATA        → 指数数据
       SECTOR_DATA       → 板块数据
```

---

## 🛠️ Vue.js集成

```javascript
import dataSourceService from '@/api/dataSourceService'

// 搜索数据源
const sources = await dataSourceService.searchDataSources({
  dataCategory: 'DAILY_KLINE',
  sourceType: 'akshare',
  onlyHealthy: true
})

// 测试数据源
const result = await dataSourceService.testDataSource(
  'akshare.stock_zh_a_hist',
  {
    symbol: '000001',
    start_date: '20240101',
    end_date: '20240131'
  }
)
```

---

## 🐍 Python集成

```python
from scripts.tools.manual_data_source_tester import DataSourceTester

tester = DataSourceTester()

# 测试数据源
result = tester.test_data_source(
    endpoint_name='akshare.stock_zh_a_hist',
    test_params={
        'symbol': '000001',
        'start_date': '20240101',
        'end_date': '20240131'
    },
    verbose=True
)

# 生成报告
tester.generate_test_report('my_test_report.json')
```

---

## 📈 数据质量指标

| 指标 | 说明 | 良好值 |
|------|------|--------|
| `has_data` | 是否有数据 | `true` |
| `is_empty` | 是否为空 | `false` |
| `column_completeness` | 列完整性 | 所有列 `present: true` |
| `null_rate` | 空值率 | `< 5%` |
| `duplicate_rate` | 重复率 | `0%` |

---

## ⚠️ 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `ModuleNotFoundError` | 导入路径错误 | 已自动修复 |
| `YAML syntax error` | 配置文件错误 | 已修复引号问题 |
| `Connection timeout` | 数据库延迟 | 自动从YAML降级 |
| `401 Unauthorized` | 缺少token | 添加认证头 |

---

## 🔗 相关链接

- **完整文档**: `docs/guides/DATA_SOURCE_MANAGEMENT_TOOLS_USAGE_GUIDE.md`
- **架构文档**: `docs/architecture/DATA_SOURCE_MANAGEMENT_V2.md`
- **验证报告**: `docs/reports/DATA_SOURCE_V2_FINAL_VERIFICATION_REPORT.md`
- **配置文件**: `config/data_sources_registry.yaml`
- **API文档**: `http://localhost:8000/api/docs`

---

**快速参考** | **完整指南**: 见详细文档 | **问题反馈**: 创建GitHub Issue
