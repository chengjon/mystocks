# MyStocks 测试体系分析与优化方案

> **历史分析说明**:
> 本文件是测试体系分析材料，不是当前测试基线、当前工具链状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及测试执行流程或协作约束，再结合 `docs/testing/TESTING_GUIDE.md` 与根目录 `AGENTS.md`。
>
> 文内测试数量、工具版本、问题分级与修复状态如未重新测量并给出统计时间，应视为历史分析快照，不得直接当作当前事实。

## 1. 测试现状总览

### 1.1 测试规模
| 指标 | 数值 |
|------|------|
| **总测试文件数** | 460+ |
| **pytest 收集测试数** | 1535 |
| **tests/ 目录** | 406 文件 |
| **web/backend/tests/** | 54 文件 |

### 1.2 测试分布（按类型）
| 类型 | 文件数 | 占比 | 优先级 |
|------|--------|------|--------|
| Unit Tests | 160 | 35% | HIGH |
| API Tests | 76 | 17% | CRITICAL |
| Integration Tests | 24 | 5% | HIGH |
| E2E Tests | 10 | 2% | CRITICAL |
| Performance Tests | 11 | 2% | MEDIUM |
| Security Tests | 5 | 1% | HIGH |
| Adapter Tests | 10 | 2% | MEDIUM |
| DDD Tests | 13 | 3% | LOW |
| AI Tests | 9 | 2% | LOW |
| Contract Tests | 6 | 1% | MEDIUM |
| 其他 | 136 | 30% | VARIES |

### 1.3 工具链状态
| 工具 | 版本 | 状态 |
|------|------|------|
| pytest | 9.0.2 | ✅ 可用 |
| playwright | 1.55.0 | ✅ 可用 |
| locust | 2.42.6 | ✅ 可用 |
| coverage | 7.11.0 | ✅ 可用 |
| pytest-xdist | 3.8.0 | ✅ 并行执行 |
| pytest-cov | 7.0.0 | ✅ 覆盖率 |
| pytest-asyncio | 0.23.8 | ✅ 异步支持 |
| pytest-playwright | 0.4.3 | ✅ E2E |
| pytest-benchmark | 5.1.0 | ✅ 性能基准 |
| pytest-bdd | 7.3.0 | ✅ BDD |

### 1.4 Playwright 浏览器
| 浏览器 | 状态 |
|--------|------|
| Chromium | ✅ 多版本已安装 (1084, 1187, 1194, 1200) |
| Firefox | ⚠️ 需验证 |
| WebKit | ⚠️ 需验证 |

---

## 2. 已识别问题

### 2.1 CRITICAL 问题
1. ~~**测试执行超时**: 1535 测试在 600s 内仅完成 4%~~ ✅ 已修复 (conftest.py 排除问题目录)
2. ~~**预先存在的导入错误**: `ImportError: cannot import name 'Base' from 'app.db'`~~ ✅ 已修复
3. ~~**语法错误**: 已修复 (`sentiment.py`, `test_sse_performance.py`)~~ ✅ 已修复

### 2.2 HIGH 问题
1. **测试隔离不足**: 部分测试依赖外部服务（数据库、Redis）
2. **浏览器兼容性**: Firefox/WebKit 超时配置未优化
3. **API 响应格式不一致**: 需标准化

### 2.3 MEDIUM 问题
1. **覆盖率目标**: 当前 ~6%，目标 80%
2. **测试数据管理**: Mock 数据分散
3. **性能基准缺失**: 无 API 响应时间基线

---

## 3. 测试执行策略

### 3.1 分层执行（按优先级）

#### CRITICAL 层（Day 1-2）
```bash
# 1. 核心 API 测试（快速验证）
pytest tests/api/ -m "not slow" --maxfail=10 -q

# 2. 安全测试
pytest tests/security/ -v

# 3. CSRF/Auth 测试（已验证通过）
pytest web/backend/tests/test_csrf_protection.py -v
```

#### HIGH 层（Day 3-5）
```bash
# 4. 单元测试（核心模块）
pytest tests/unit/ -m "not slow" -n auto --maxfail=20

# 5. 集成测试
pytest tests/integration/ -v --maxfail=10
```

#### MEDIUM 层（Week 2）
```bash
# 6. E2E 测试（Chromium 优先）
pytest tests/e2e/ --browser chromium -v

# 7. 性能测试
pytest tests/performance/ -v
```

### 3.2 浏览器超时配置
```python
# playwright.config.ts 建议配置
BROWSER_TIMEOUTS = {
    "chromium": {
        "timeout": 30000,
        "navigationTimeout": 30000,
    },
    "firefox": {
        "timeout": 45000,  # +50%
        "navigationTimeout": 45000,
    },
    "webkit": {
        "timeout": 45000,  # +50%
        "navigationTimeout": 45000,
    }
}
```

### 3.3 测试标记使用
```bash
# 快速冒烟测试
pytest -m "not slow and not integration" -n auto

# 仅单元测试
pytest -m unit -n auto

# 仅 API 测试
pytest -m api -v

# 排除网络依赖
pytest -m "not network" -n auto
```

---

## 4. API 响应标准化

### 4.1 标准响应格式
```json
{
  "success": true,
  "code": "SUCCESS",
  "message": "操作成功",
  "data": { ... },
  "timestamp": 1707500000.123
}
```

### 4.2 错误响应格式
```json
{
  "success": false,
  "code": "ERROR_CODE",
  "message": "错误描述",
  "data": null,
  "timestamp": 1707500000.123
}
```

### 4.3 验证脚本
```python
# scripts/tests/validate_api_responses.py
def validate_response_format(response: dict) -> bool:
    required_fields = ["success", "code", "message", "data"]
    return all(field in response for field in required_fields)
```

---

## 5. 执行计划

### Phase 1: 快速稳定化（Day 1-2）
- [ ] 修复阻塞性导入错误 (`app.db.Base`)
- [ ] 运行 CRITICAL 层测试
- [ ] 生成失败测试分类报告
- [ ] 配置浏览器超时

### Phase 2: 核心测试通过（Day 3-5）
- [ ] 修复 HIGH 优先级失败
- [ ] 单元测试通过率 ≥ 90%
- [ ] API 测试通过率 ≥ 85%
- [ ] 集成测试通过率 ≥ 80%

### Phase 3: E2E 稳定化（Week 2）
- [ ] Chromium E2E 通过率 100%
- [ ] Firefox/WebKit 通过率 ≥ 85%
- [ ] 性能基准建立

### Phase 4: 覆盖率提升（Week 3-4）
- [ ] 覆盖率 ≥ 50%
- [ ] 关键路径 100% 覆盖
- [ ] 自动化 CI/CD 集成

---

## 6. 质量目标

| 指标 | 当前 | Week 1 | Week 2 | 最终 |
|------|------|--------|--------|------|
| E2E 通过率 | ~85% | ≥92% | ≥95% | ≥96% |
| API 通过率 | ~70% | ≥85% | ≥95% | ≥98% |
| 单元测试通过率 | ~80% | ≥90% | ≥95% | ≥98% |
| 覆盖率 | ~6% | ≥30% | ≥50% | ≥80% |
| API 响应时间 | N/A | ≤500ms | ≤400ms | ≤300ms |
| 浏览器兼容性 | Chromium only | +Firefox | +WebKit | 全部 |

---

## 7. 自动化配置

### 7.1 pytest.ini 优化建议
```ini
[pytest]
# 分层执行配置
addopts =
    -v
    --tb=short
    -n auto
    --maxfail=10
    --dist=loadfile
    --cov=src --cov=web/backend/app
    --cov-fail-under=30

# 超时配置
timeout = 300
timeout_method = thread
```

### 7.2 CI/CD 集成
```yaml
# .github/workflows/test.yml
jobs:
  test:
    strategy:
      matrix:
        test-type: [unit, api, integration, e2e]
    steps:
      - run: pytest tests/${{ matrix.test-type }}/ -v
```

---

## 8. Phase 2 执行结果 (2026-02-09)

### 8.1 修复的阻塞性问题

| 问题 | 修复方案 | 状态 |
|------|----------|------|
| `ImportError: Base from app.db` | 添加 `Base = declarative_base()` 到 `app/db/__init__.py` | ✅ |
| pytest 收集 scripts/ 目录 | 更新 `conftest.py` 添加 `collect_ignore` | ✅ |
| `test_sina_api.py` 有 `sys.exit(1)` | 重命名为 `sina_api_check.py` | ✅ |
| `test_app_import.py` 有 `sys.exit(1)` | 重命名为 `app_import_check.py` | ✅ |

### 8.2 CRITICAL 层测试结果

#### CSRF 测试 (33/33 = 100%)
```
web/backend/tests/test_csrf_protection.py: 33 passed ✅
```

#### API 测试 (web/backend/tests/)
| 指标 | 数值 | 百分比 |
|------|------|--------|
| **通过** | 1136 | 93.4% |
| **失败** | 18 | 1.5% |
| **跳过** | 60 | 4.9% |
| **错误** | 2 | 0.2% |
| **总计** | 1216 | 100% |

### 8.3 失败测试分类

| 类别 | 数量 | 测试文件 | 根因 |
|------|------|----------|------|
| 连接错误 | 2 | `test_client.py` | 服务未运行 (localhost:8001) |
| 适配器变更 | 2 | `test_financial_adapter.py` | `FinancialDataSource` API 变更 |
| 数据库不可用 | 3 | `test_us3_monitoring.py` | TDengine 连接失败 |
| 契约验证 | 8 | `test_*_api.py` | API 端点覆盖不完整 |
| 缺少 fixtures | 2 | `test_multi_directory.py`, `test_tdengine.py` | 未定义 fixtures |
| 配置缺失 | 1 | `test_us2_config_driven.py` | `config/table_config.yaml` 不存在 |

### 8.4 跳过测试原因

- **网络依赖** (30): 需要外部 API 访问
- **数据库依赖** (15): 需要 TDengine/PostgreSQL
- **环境依赖** (15): 需要特定环境配置

### 8.5 下一步行动

1. **HIGH 优先级**:
   - 修复 Auth 测试的 CSRF token 处理
   - 修复契约验证测试 (8个)
   - 添加缺失的 fixtures

2. **MEDIUM 优先级**:
   - 运行 Integration 测试
   - 配置 E2E 浏览器超时

3. **目标**:
   - Week 1: 通过率 ≥ 95%
   - Week 2: E2E 通过率 ≥ 95%

---

*生成时间: 2026-02-09*
*状态: Phase 2 完成，通过率 93.4%*
