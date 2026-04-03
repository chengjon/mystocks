# OpenAPI 契约治理标准 v1

> 版本：v1.0  
> 生效日期：2026-04-03  
> 适用范围：`web/backend/app/api/**`、`web/backend/tests/**`、`scripts/generate_frontend_types.py`、`scripts/_generate_frontend_types_cli.py`、`web/frontend/src/api/**`、`.github/workflows/api-contract-validation.yml`

## 1. 定位

OpenAPI 在本项目中是 API 契约层，不是事后文档层。

- 后端实现必须服从契约。
- 前端调用与类型生成必须消费契约。
- 自动化测试、CI 校验、第三方系统集成必须以契约为准。

当前仓库采用 `code-first` 路线，唯一可信源为：

1. FastAPI 路由定义
2. Pydantic 请求/响应模型
3. 由应用实际导出的 `/openapi.json`

`docs/api/**` 下的说明文档、人工整理的接口清单、临时联调记录都属于派生文档，不得与上述契约并列为“第二真值”。

## 2. 核心原则

### 2.1 OpenAPI 是契约，不是事后说明

- 禁止先改接口实现，再把 OpenAPI 当作“以后补”的文档工作。
- 禁止把 Swagger/ReDoc 视为展示层而忽略其契约属性。
- 请求参数、响应结构、认证要求、错误响应、`requestBody` 示例都属于契约本体。

### 2.2 必须单源可信（Single Source of Truth）

- 当前项目以 `FastAPI route + Pydantic schema + /openapi.json` 为 API 单一事实来源。
- 禁止手工维护两套权威接口定义。
- 前端若需要类型、客户端或断言模型，应从 OpenAPI 或与其等价的后端模型链路生成，而不是重复手写一份并长期漂移。

### 2.3 必须版本化、可追溯

- OpenAPI 契约变更必须与代码一起提交到 Git。
- 必须能回答“谁在什么时候改了哪个接口、改了什么字段、是否属于 breaking change”。
- 任何 breaking change 都必须在 PR 中显式标注，并通过 CI 差异检测链路审查。

## 3. 变更规则

### 3.1 任何接口变更必须同步更新契约

以下任一变化都属于契约变化，必须同步反映到 OpenAPI：

- 路径、方法、状态码
- 请求参数、默认值、枚举、校验规则
- 请求体/响应体字段及其类型
- 认证要求与安全方案
- 错误响应说明
- `summary`、`description`
- `requestBody` 的 `example/examples`

### 3.2 禁止的行为

- 代码接口已改，但 `/openapi.json` 导出结果未同步更新
- 仅更新 Markdown 文档，不更新真实契约
- 前端手写一份长期维护的“权威字段清单”
- 用测试或前端兼容逻辑掩盖契约漂移
- 将 OpenAPI 视为“上线后再补”的低优先级事项

## 4. 当前仓库的执行流程

### 4.1 后端改接口时

1. 修改 FastAPI 路由与 Pydantic schema。
2. 同步补齐 OpenAPI 元数据：
   - `summary`
   - `description`
   - 参数 `description`
   - `requestBody.content.application/json.example/examples`
   - 错误响应说明
3. 运行 OpenAPI 文档回归测试与契约校验。

### 4.2 契约影响前端时

1. 重新生成前端类型。
2. 校验前端类型编译通过。
3. 若存在 breaking change，必须在 PR 中显式说明影响范围与迁移策略。

## 5. PR 与 CI 门禁

### 5.1 必须通过的门禁

涉及 API 契约范围的变更，至少必须通过：

1. OpenAPI 生成校验
2. OpenAPI 文档回归门禁
3. TypeScript 类型生成与类型检查
4. Breaking change 检测

### 5.2 文档回归门禁的判定口径

后端 OpenAPI 文档质量按基线文件 `reports/analysis/tech-debt-baseline.json` 中的 `backend_api_documentation` 执行“不得劣化”规则：

- `documented_endpoints` 不得下降
- `documented_percentage` 不得下降
- `endpoints_with_examples` 不得下降
- `example_percentage` 不得下降
- `endpoints_with_errors` 不得下降
- `error_response_percentage` 不得下降
- `total_issues` 不得上升
- `schema_issue_count` 不得上升

### 5.3 基线更新规则

- 仅允许在确认仓库当前状态真实改善后向上收紧基线。
- 禁止为了“让 CI 通过”而把更差的指标写回基线。
- 基线更新必须和对应治理提交一并入库，保证可追溯。

## 6. 标准命令

后端 OpenAPI 文档治理的最小校验命令：

```bash
pytest web/backend/tests/test_health_route_conflicts.py \
  web/backend/tests/test_api_documentation_validation.py \
  -q --no-cov -rs
```

查看当前 OpenAPI 汇总：

```bash
PYTHONPATH=web/backend:. \
POSTGRESQL_HOST=localhost \
POSTGRESQL_PORT=5432 \
POSTGRESQL_USER=testuser \
POSTGRESQL_PASSWORD=testpassword \
POSTGRESQL_DATABASE=testdb \
JWT_SECRET_KEY=test_secret_key_for_ci_only \
BACKEND_PORT=8020 \
BACKEND_BACKUP_PORT=8021 \
TESTING=true \
DEVELOPMENT_MODE=true \
MOCK_AUTH_ENABLED=true \
python - <<'PY'
from fastapi.testclient import TestClient
from app.main import app
from web.backend.tests.test_api_documentation_validation import APIDocumentationValidator

validator = APIDocumentationValidator(TestClient(app))
print(validator.run_comprehensive_validation()["summary"])
PY
```

## 7. 与其他规范的关系

- 本标准是 [architecture/STANDARDS.md](../../architecture/STANDARDS.md) 中“契约先行”的 API 契约治理细化。
- 技术债基线与豁免流程同时受 [technical-debt-governance-charter-v1.md](./technical-debt-governance-charter-v1.md) 约束。
- 若与上位架构准则冲突，以 `architecture/STANDARDS.md` 为准。
