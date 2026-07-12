# 代码清单扫描报告

**生成日期**: 2026-02-23

## 摘要统计

| 指标 | 数值 |
|------|------|
| 总文件数 | 4,940 |
| 总代码行数 | 1,042,764 |
| 超过阈值文件数 | 61 |
| 使用Mock文件数 | 80 |

## 按文件类型统计

| 文件类型 | 文件数 | 代码行数 | 超过阈值 | 使用Mock |
|----------|--------|----------|----------|----------|
| .js | 2,254 | 443,190 | 48 | 0 |
| .py | 1,924 | 390,232 | 0 | 80 |
| .ts | 762 | 209,342 | 13 | 0 |

## 超过阈值文件列表 (Top 20)

以下文件代码行数超过1000行，建议进行代码拆分：

| 文件路径 | 行数 |
|----------|------|
| scripts/dev/chromium-bidi/lib/cjs/protocol-parser/generated/webdriver-bidi.d.ts | 64,724 |
| scripts/dev/chromium-bidi/lib/esm/protocol-parser/generated/webdriver-bidi.d.ts | 64,724 |
| scripts/dev/puppeteer-core/lib/es5-iife/puppeteer-core-browser.js | 24,608 |
| scripts/dev/chromium-bidi/lib/iife/mapperTab.js | 19,231 |
| scripts/dev/@babel/parser/lib/index.js | 14,660 |
| scripts/dev/puppeteer-core/lib/cjs/third_party/rxjs/rxjs.js | 9,256 |
| scripts/dev/puppeteer-core/lib/types.d.ts | 8,003 |
| scripts/dev/puppeteer-core/lib/es5-iife/puppeteer-core-browser.d.ts | 8,003 |
| scripts/dev/cssstyle/lib/generated/properties.js | 6,943 |
| scripts/dev/jsdom/lib/jsdom/living/generated/Document.js | 3,744 |
| scripts/dev/@babel/types/lib/index.d.ts | 3,454 |
| scripts/dev/jsdom/lib/jsdom/living/generated/Element.js | 3,223 |
| scripts/dev/chromium-bidi/lib/cjs/protocol-parser/generated/webdriver-bidi.js | 2,937 |
| scripts/dev/chromium-bidi/lib/esm/protocol-parser/generated/webdriver-bidi.js | 2,931 |
| scripts/dev/@babel/types/lib/builders/generated/lowercase.js | 2,893 |
| scripts/dev/playwright-core/lib/protocol/validator.js | 2,889 |
| scripts/dev/jsdom/lib/jsdom/living/generated/HTMLElement.js | 2,833 |
| scripts/dev/@babel/types/lib/validators/generated/index.js | 2,794 |
| scripts/dev/chromium-bidi/lib/cjs/protocol/generated/webdriver-bidi.d.ts | 2,710 |
| scripts/dev/chromium-bidi/lib/esm/protocol/generated/webdriver-bidi.d.ts | 2,710 |

> **注意**: 大部分超过阈值的文件位于 `scripts/dev/` 目录下，这些是第三方依赖库（Playwright、Puppeteer、jsdom等），不建议拆分。

## 使用Mock数据文件列表

以下文件使用了Mock数据，在REAL模式下需要特别注意：

### 严重性: error (需优先处理)

| 文件路径 | Mock导入 |
|----------|----------|
| src/data_sources/mock_data_source.py | import mock_, from src.mock import |
| src/data_sources/factory.py | from src.data_sources.mock.* |
| src/data_sources/mock/timeseries_mock.py | MockTimeSeriesDataSource |
| src/data_sources/mock/__init__.py | from src.data_sources.mock |
| src/data_sources/mock/relational_mock.py | MockRelationalDataSource |
| src/data_sources/mock/business_mock.py | from src.data_sources.mock |
| src/utils/data_source_validator.py | MockDataSource |
| src/factories/data_source_factory.py | from src.data_sources.mock |
| scripts/examples/mock_data_demo.py | from src.mock |
| scripts/tests/test_mock_system.py | - |
| scripts/tests/test_mock_data_validation_simple.py | from src.mock |
| scripts/tests/test_mock_data_system.py | from src.mock |
| scripts/tests/test_end_to_end_mock.py | from src.mock |
| scripts/tests/test_mock_simple.py | - |
| scripts/tests/test_mock_data_validation.py | from src.mock |
| scripts/dev/mock_data_demo.py | from src.mock |
| web/backend/app/services/data_source_factory/data_source_mode.py | - |
| web/backend/app/services/data_source_factory/data_source_factory.py | - |
| web/backend/app/mock/mock_data/factory.py | - |

### 严重性: warning (测试文件中的unittest.mock)

这些是测试文件中正常使用 `unittest.mock`，属于正常测试代码，无需处理。

## 环境配置检查

当前环境配置：

| 配置项 | 值 |
|--------|-----|
| USE_MOCK_DATA | False |
| DATA_SOURCE | real |
| 当前模式 | Real |

**REAL模式验证**: 通过 ✅

## 建议行动项

1. **代码拆分建议**: 对于业务代码中超过1000行的文件，考虑按功能模块进行拆分
2. **Mock使用规范**: 
   - Mock模块本身（src/data_sources/mock/）是正常的，用于开发和测试
   - 检查业务代码中是否有过多Mock依赖，确保REAL模式下能正常运行
3. **定期扫描**: 建议每月执行一次代码清单扫描，监控代码复杂度趋势

## 扫描配置

- 扫描目录: src, scripts, web/backend/app
- 文件类型: .py, .vue, .ts, .tsx, .js, .jsx
- 行数阈值: 1000

---

*此报告由 code_inventory 工具自动生成*
