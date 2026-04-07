# API契约管理平台 - 部署检查清单

> **使用说明**:
> 本文件用于说明当前治理入口、执行入口或操作清单的使用方式，服务于协作过程中的上下文同步。
> 其中的局部约束和步骤不能脱离 `architecture/STANDARDS.md`、当前实现与实际验证结果单独解读为最终事实。


**项目**: MyStocks API契约管理平台
**部署环境**: Production
**部署日期**: YYYY-MM-DD
**执行人**: _______________
**审核人**: _______________

---

## 📋 使用说明

本检查清单用于API契约管理平台的部署验证，确保所有组件正确安装和配置。

**检查标准**:
- ✅ 通过: 功能正常，无问题
- ⚠️ 警告: 功能可用，但有非阻塞问题
- ❌ 失败: 功能异常，需要修复

**使用流程**:
1. 按照顺序逐项检查
2. 在对应状态框打勾
3. 记录任何问题或异常
4. 完成所有检查后签字确认

---

## Phase 1: 环境准备检查

### 1.1 系统环境

- [ ] **操作系统**: Linux (Ubuntu 20.04+ 或 CentOS 7+)
  - 检查命令: `cat /etc/os-release`
  - 预期结果: Ubuntu 20.04+ 或 CentOS 7+
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **Python版本**: Python 3.12+
  - 检查命令: `python3 --version`
  - 预期结果: Python 3.12.0+
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **Node.js版本**: Node.js 20+ (TypeScript类型生成)
  - 检查命令: `node --version`
  - 预期结果: v20.0.0+
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **内存**: ≥4GB可用内存
  - 检查命令: `free -h`
  - 预期结果: avail ≥4GB
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **磁盘空间**: ≥10GB可用空间
  - 检查命令: `df -h`
  - 预期结果: avail ≥10GB
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

### 1.2 数据库环境

- [ ] **PostgreSQL安装**: PostgreSQL 17+已安装
  - 检查命令: `psql --version`
  - 预期结果: psql (PostgreSQL) 17.x
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **数据库创建**: mystocks数据库已创建
  - 检查命令: `psql -U postgres -l | grep mystocks`
  - 预期结果: mystocks数据库存在
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **数据库连接**: 可以连接到mystocks数据库
  - 检查命令: `psql -U postgres -d mystocks -c "SELECT version();"`
  - 预期结果: 成功连接并返回PostgreSQL版本
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **TimescaleDB扩展**: TimescaleDB已安装并启用
  - 检查命令: `psql -U postgres -d mystocks -c "SELECT extversion FROM pg_extension WHERE extname = 'timescaledb';"`
  - 预期结果: 返回TimescaleDB版本号
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

### 1.3 环境变量配置

- [ ] **.env文件存在**: 项目根目录存在.env文件
  - 检查命令: `ls -la .env`
  - 预期结果: .env文件存在且权限正确 (600)
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **数据库连接配置**: PostgreSQL连接参数已配置
  - 检查命令: `grep -E "POSTGRESQL_(HOST|PORT|USER|PASSWORD|DATABASE)" .env`
  - 预期结果: 所有必需变量已配置
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **JWT密钥配置**: JWT_SECRET_KEY已设置
  - 检查命令: `grep JWT_SECRET_KEY .env`
  - 预期结果: JWT_SECRET_KEY已设置 (32+字符)
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **敏感文件权限**: .env文件权限为600
  - 检查命令: `ls -la .env | awk '{print $1}'`
  - 预期结果: -rw------- (600)
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

---

## Phase 2: 代码部署检查

### 2.1 代码检出

- [ ] **代码仓库**: 代码已从Git仓库检出
  - 检查命令: `git status`
  - 预期结果: 位于phase6-api-contract-standardization分支，无未提交更改
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **分支正确**: 当前在phase6-api-contract-standardization分支
  - 检查命令: `git branch --show-current`
  - 预期结果: phase6-api-contract-standardization
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **最新代码**: 已拉取最新代码
  - 检查命令: `git log -1 --oneline`
  - 预期结果: 显示最新提交 (包含"Phase 4"或"API契约管理平台")
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

### 2.2 依赖安装

- [ ] **Backend依赖**: web/backend/requirements.txt依赖已安装
  - 检查命令: `pip list | grep -E "(fastapi|uvicorn|pydantic|sqlalchemy|psycopg2)"`
  - 预期结果: 所有必需包已安装
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **CLI工具依赖**: scripts/cli/requirements.txt依赖已安装
  - 检查命令: `pip list | grep -E "(click|rich|deepdiff|pyyaml|prance)"`
  - 预期结果: 所有必需包已安装
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **CLI工具安装**: CLI工具已可编辑模式安装
  - 检查命令: `pip show api-contract-sync`
  - 预期结果: 显示api-contract-sync包信息，Location指向scripts/cli
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **Pre-commit hooks**: Pre-commit hooks已安装
  - 检查命令: `pre-commit --version`
  - 预期结果: 显示pre-commit版本号
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **Pre-commit配置**: Hooks已注册到Git
  - 检查命令: `ls -la .git/hooks/pre-commit`
  - 预期结果: pre-commit hook文件存在
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

---

## Phase 3: 数据库初始化检查

### 3.1 表结构创建

- [ ] **契约版本表**: contract_versions表已创建
  - 检查命令: `psql -U postgres -d mystocks -c "\d contract_versions"`
  - 预期结果: 显示表结构 (id, name, version, spec, commit_hash, author, description, tags, is_active, created_at)
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **契约差异表**: contract_diffs表已创建
  - 检查命令: `psql -U postgres -d mystocks -c "\d contract_diffs"`
  - 预期结果: 显示表结构 (id, contract_name, from_version_id, to_version_id, total_changes, breaking_changes, non_breaking_changes, diffs, summary, created_at)
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **契约验证表**: contract_validations表已创建
  - 检查命令: `psql -U postgres -d mystocks -c "\d contract_validations"`
  - 预期结果: 显示表结构 (id, version_id, valid, error_count, warning_count, results, created_at)
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **外键约束**: 外键约束已正确创建
  - 检查命令: `psql -U postgres -d mystocks -c "SELECT conname FROM pg_constraint WHERE conrelid = 'contract_diffs'::regclass AND contype = 'f';"`
  - 预期结果: 显示2个外键约束 (from_version_id, to_version_id)
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **索引创建**: 索引已正确创建
  - 检查命令: `psql -U postgres -d mystocks -c "SELECT indexname FROM pg_indexes WHERE tablename = 'contract_versions';"`
  - 预期结果: 显示索引 (contract_versions_pkey, contract_versions_name_idx, contract_versions_is_active_idx)
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

### 3.2 数据库迁移

- [ ] **迁移脚本**: 数据库迁移脚本已执行
  - 检查命令: `检查迁移日志或时间戳`
  - 预期结果: 迁移成功，无错误
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **初始数据**: 必要的初始数据已导入
  - 检查命令: `psql -U postgres -d mystocks -c "SELECT COUNT(*) FROM contract_versions;"`
  - 预期结果: 返回0 (新部署) 或 >0 (包含测试数据)
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

---

## Phase 4: 后端服务部署检查

### 4.1 服务启动

- [ ] **后端服务启动**: 后端服务已成功启动
  - 检查命令: `ps aux | grep "python -m app.main" | grep -v grep`
  - 预期结果: 显示进程信息
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **服务端口监听**: 服务监听在8000端口
  - 检查命令: `netstat -tlnp | grep 8000` 或 `lsof -i :8020`
  - 预期结果: 8000端口被python进程监听
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **健康检查**: /health端点返回200 OK
  - 检查命令: `curl -s http://localhost:8020/health | jq .`
  - 预期结果: `{"status": "healthy"}`
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **Swagger UI**: Swagger UI可访问
  - 检查命令: `curl -s -o /dev/null -w "%{http_code}" http://localhost:8020/docs`
  - 预期结果: 200 OK
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

### 4.2 API端点验证

- [ ] **POST /api/contracts/versions**: 创建契约版本
  - 检查命令: `curl -X POST http://localhost:8020/api/contracts/versions -H "Content-Type: application/json" -d '{"name":"test","version":"1.0.0","spec":{"openapi":"3.0.0","info":{"title":"Test","version":"1.0.0"},"paths":{},"components":{"schemas":{}}}}' | jq .`
  - 预期结果: 返回200 OK，包含契约版本ID
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **GET /api/contracts/versions**: 列出契约版本
  - 检查命令: `curl -s http://localhost:8020/api/contracts/versions | jq .`
  - 预期结果: 返回200 OK，包含契约版本列表
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **GET /api/contracts/contracts**: 列出所有契约
  - 检查命令: `curl -s http://localhost:8020/api/contracts/contracts | jq .`
  - 预期结果: 返回200 OK，包含契约元数据列表
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **POST /api/contracts/validate**: 验证OpenAPI规范
  - 检查命令: `curl -X POST http://localhost:8020/api/contracts/validate -H "Content-Type: application/json" -d '{"spec":{"openapi":"3.0.0","info":{"title":"Test","version":"1.0.0"},"paths":{},"components":{"schemas":{}}},"check_breaking_changes":false}' | jq .`
  - 预期结果: 返回200 OK，验证通过
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

---

## Phase 5: CLI工具验证检查

### 5.1 CLI命令验证

- [ ] **CLI工具可用**: api-contract-sync命令可用
  - 检查命令: `api-contract-sync --help`
  - 预期结果: 显示帮助信息，包含17个命令
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **create命令**: 创建契约版本
  - 检查命令: `api-contract-sync create test-cli 1.0.0 -s docs/api/openapi_template.yaml`
  - 预期结果: 成功创建契约版本
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **list命令**: 列出契约版本
  - 检查命令: `api-contract-sync list --name test-cli`
  - 预期结果: 显示契约版本列表
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **show命令**: 显示版本详情
  - 检查命令: `api-contract-sync show 1` (假设version_id=1)
  - 预期结果: 显示契约版本详细信息
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **diff命令**: 对比版本差异
  - 检查命令: `api-contract-sync diff 1 2` (假设有2个版本)
  - 预期结果: 显示版本差异报告
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **validate命令**: 验证OpenAPI规范
  - 检查命令: `api-contract-sync validate docs/api/openapi_template.yaml`
  - 预期结果: 验证通过或显示验证结果
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

### 5.2 CLI完整命令覆盖

- [ ] **activate命令**: 激活版本
  - 检查命令: `api-contract-sync activate 1`
  - 状态: ✅ / ⚠️ / ❌

- [ ] **update命令**: 更新版本元数据
  - 检查命令: `api-contract-sync update 1 --description "Updated"`
  - 状态: ✅ / ⚠️ / ❌

- [ ] **delete命令**: 删除版本
  - 检查命令: `api-contract-sync delete 1` (谨慎操作)
  - 状态: ✅ / ⚠️ / ❌

- [ ] **sync命令**: 同步契约
  - 检查命令: `api-contract-sync sync test-cli -s docs/api/openapi_template.yaml --version 1.0.1`
  - 状态: ✅ / ⚠️ / ❌

---

## Phase 6: TypeScript类型生成检查

### 6.1 生成工具安装

- [ ] **openapi-typescript安装**: openapi-typescript已安装
  - 检查命令: `npm list -g openapi-typescript`
  - 预期结果: 显示openapi-typescript版本号
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **替代工具检查**: dtsgenerator或openapi-generator已安装 (可选)
  - 检查命令: `npm list -g dtsgenerator openapi-generator`
  - 预期结果: 至少一个工具已安装
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

### 6.2 类型文件生成

- [ ] **运行生成脚本**: TypeScript类型生成脚本已执行
  - 检查命令: `bash scripts/generate-types/generate_ts_types.sh`
  - 预期结果: 成功生成类型定义文件
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **类型文件存在**: web/frontend/src/types/目录包含类型文件
  - 检查命令: `ls -la web/frontend/src/types/`
  - 预期结果: 显示生成的.ts或.d.ts文件
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **类型文件语法**: TypeScript类型文件语法正确
  - 检查命令: `tsc --noEmit web/frontend/src/types/*.ts`
  - 预期结果: 无语法错误
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

---

## Phase 7: 测试套件验证检查

### 7.1 测试依赖安装

- [ ] **pytest安装**: pytest已安装
  - 检查命令: `pytest --version`
  - 预期结果: 显示pytest版本号
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **pytest插件**: pytest-cov和pytest-asyncio已安装
  - 检查命令: `pip list | grep pytest`
  - 预期结果: 显示pytest, pytest-cov, pytest-asyncio
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

### 7.2 测试执行

- [ ] **运行测试套件**: 所有测试用例执行
  - 检查命令: `bash scripts/tests/run_api_tests.sh`
  - 预期结果: 19个测试用例全部通过
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **测试覆盖率**: 测试覆盖率 ≥80%
  - 检查命令: `pytest --cov=web/backend --cov-report=term tests/api/`
  - 预期结果: 覆盖率 ≥80%
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **无错误报告**: 测试无ERROR或FAIL
  - 检查命令: 检查pytest输出
  - 预期结果: 0 error, 0 failed
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

---

## Phase 8: CI/CD配置验证检查

### 8.1 GitHub Actions配置

- [ ] **工作流文件存在**: .github/workflows/api-contract-validation.yml存在
  - 检查命令: `ls -la .github/workflows/api-contract-validation.yml`
  - 预期结果: 文件存在且内容完整
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **工作流语法**: YAML语法正确
  - 检查命令: `yamllint .github/workflows/api-contract-validation.yml` (可选)
  - 预期结果: 无语法错误
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **Job配置**: 4个job配置完整
  - 检查命令: `grep -E "jobs:|contract-validation:|contract-publish:|diff-check:|notify:" .github/workflows/api-contract-validation.yml`
  - 预期结果: 4个job定义完整
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

### 8.2 Pre-commit Hooks验证

- [ ] **配置文件存在**: .pre-commit-config.yaml存在
  - 检查命令: `ls -la .pre-commit-config.yaml`
  - 预期结果: 文件存在且内容完整
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **Hook配置**: 9个hook配置完整
  - 检查命令: `grep -c "repo:" .pre-commit-config.yaml`
  - 预期结果: ≥9个repo配置
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **Hook测试**: Pre-commit hooks测试通过
  - 检查命令: `pre-commit run --all-files`
  - 预期结果: 所有hook通过
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

---

## Phase 9: 监控和日志配置检查

### 9.1 日志配置

- [ ] **日志目录**: 日志目录已创建
  - 检查命令: `ls -la logs/` (或配置的日志目录)
  - 预期结果: 目录存在且权限正确
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **日志配置**: 日志级别已配置
  - 检查命令: `grep -E "LOG_LEVEL|logging" web/backend/app/core/config.py`
  - 预期结果: 日志级别已配置 (DEBUG/INFO/WARNING/ERROR)
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **日志输出**: 日志文件正确输出
  - 检查命令: `tail -f logs/api-contracts.log` (或配置的日志文件)
  - 预期结果: 显示日志内容
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

### 9.2 监控配置 (可选)

- [ ] **Prometheus集成**: Prometheus metrics端点可用 (如果配置)
  - 检查命令: `curl -s http://localhost:8020/metrics`
  - 预期结果: 返回Prometheus格式的metrics
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **健康检查**: /health端点返回详细健康状态
  - 检查命令: `curl -s http://localhost:8020/health | jq .`
  - 预期结果: 包含数据库状态、版本信息等
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

---

## Phase 10: 文档部署检查

### 10.1 文档文件

- [ ] **API文档**: docs/api/CONTRACT_MANAGEMENT_API.md存在
  - 检查命令: `wc -l docs/api/CONTRACT_MANAGEMENT_API.md`
  - 预期结果: ≥800行
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **CLI文档**: docs/api/CLI_TOOL_GUIDE.md存在
  - 检查命令: `wc -l docs/api/CLI_TOOL_GUIDE.md`
  - 预期结果: ≥700行
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **CI/CD文档**: docs/api/CI_CD_INTEGRATION_GUIDE.md存在
  - 检查命令: `wc -l docs/api/CI_CD_INTEGRATION_GUIDE.md`
  - 预期结果: ≥700行
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **其他文档**: 其他4份文档存在
  - 检查命令: `ls -la docs/api/*.md | wc -l`
  - 预期结果: ≥7份文档
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

### 10.2 Swagger UI

- [ ] **Swagger UI可访问**: Swagger UI页面可访问
  - 浏览器访问: http://localhost:8020/docs
  - 预期结果: 显示Swagger UI界面
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **API端点显示**: 所有11个API端点显示在Swagger UI
  - 检查命令: 手动检查Swagger UI
  - 预期结果: 显示所有契约管理API端点
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

---

## Phase 11: 安全配置检查

### 11.1 认证和授权 (生产环境推荐)

- [ ] **认证配置**: JWT认证已配置 (生产环境)
  - 检查命令: `grep -E "JWT|authentication|auth" web/backend/app/core/config.py`
  - 预期结果: JWT配置存在
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌ (开发环境可跳过)

- [ ] **权限控制**: 权限分级已实现 (生产环境)
  - 检查命令: `grep -E "permission|role|access" web/backend/app/api/contract/routes.py`
  - 预期结果: 权限检查逻辑存在
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌ (开发环境可跳过)

- [ ] **CORS配置**: CORS已正确配置
  - 检查命令: `grep -E "CORS|allow_origins" web/backend/app/main.py`
  - 预期结果: CORS配置存在且限制来源
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

### 11.2 安全扫描

- [ ] **Bandit扫描**: Bandit安全扫描通过
  - 检查命令: `bandit -r web/backend/`
  - 预期结果: 0个高危问题
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **Safety扫描**: 依赖安全扫描通过
  - 检查命令: `safety check --file requirements.txt`
  - 预期结果: 0个已知漏洞
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **密钥检测**: Detect-secrets扫描通过
  - 检查命令: `detect-secrets scan > .secrets.baseline`
  - 预期结果: 无真实密钥泄露
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

---

## Phase 12: 性能验证检查

### 12.1 API响应时间

- [ ] **GET /api/contracts/versions**: 响应时间 < 1秒
  - 检查命令: `time curl -s http://localhost:8020/api/contracts/versions`
  - 预期结果: real < 1.0s
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **POST /api/contracts/validate**: 响应时间 < 2秒
  - 检查命令: `time curl -X POST http://localhost:8020/api/contracts/validate -H "Content-Type: application/json" -d '{"spec":{"openapi":"3.0.0","info":{"title":"Test","version":"1.0.0"},"paths":{},"components":{"schemas":{}}},"check_breaking_changes":false}'`
  - 预期结果: real < 2.0s
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

### 12.2 并发测试

- [ ] **并发请求测试**: 10个并发请求成功
  - 检查命令: `ab -n 100 -c 10 http://localhost:8020/health`
  - 预期结果: 100%成功，无失败请求
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

---

## Phase 13: 回滚计划检查

### 13.1 数据库备份

- [ ] **数据库备份**: 数据库已备份
  - 检查命令: `ls -lh backups/mystocks_backup_*.sql` (或配置的备份目录)
  - 预期结果: 备份文件存在且时间戳为部署前
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **备份可用性**: 备份文件可恢复
  - 检查命令: `pg_restore --list backups/mystocks_backup_*.sql` (验证备份格式)
  - 预期结果: 备份文件格式正确
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

### 13.2 代码版本回滚

- [ ] **Git标签**: 当前版本已打标签
  - 检查命令: `git tag -l "deploy-*" | tail -1`
  - 预期结果: 显示最新的部署标签
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

- [ ] **回滚脚本**: 回滚脚本已准备
  - 检查命令: `ls -la scripts/deploy/rollback.sh` (或配置的回滚脚本)
  - 预期结果: 回滚脚本存在且可执行
  - 实际结果: _______________
  - 状态: ✅ / ⚠️ / ❌

---

## 验收签字

### 检查结果统计

- **总检查项**: _______________
- **通过项**: _______________ (✅)
- **警告项**: _______________ (⚠️)
- **失败项**: _______________ (❌)
- **通过率**: _______________%

### 部署决策

- [ ] **通过部署**: 所有核心检查项通过，可以部署
- [ ] **条件部署**: 有警告项，需评估风险后决定
- [ ] **阻止部署**: 有失败项，必须修复后重新检查

### 签字确认

- **执行人**: _______________ 签字: _______________ 日期: _______________
- **审核人**: _______________ 签字: _______________ 日期: _______________
- **批准人**: _______________ 签字: _______________ 日期: _______________

---

## 附件

- [ ] 部署日志: _______________
- [ ] 测试报告: _______________
- [ ] 监控截图: _______________
- [ ] 其他文档: _______________

---

**检查清单版本**: v1.0
**最后更新**: 2025-12-29
**维护者**: Claude Code (AI Assistant)

---

*本检查清单应与部署验收报告 (DEPLOYMENT_ACCEPTANCE_REPORT.md) 配合使用*
