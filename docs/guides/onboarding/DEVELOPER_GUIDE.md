# MyStocks 开发指南

> **使用说明**:
> 本文件是开发者 onboarding 指南，不是当前仓库共享规则、分支治理或架构口径的唯一事实来源。
> 开始任何写操作、规划、迁移或验证前，请优先阅读 `architecture/STANDARDS.md`；若涉及具体执行入口，再按职责分别参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

## 📋 概述

欢迎加入MyStocks量化交易平台开发团队！本指南将帮助你快速上手项目开发，掌握分支管理、CI/CD流程和最佳实践。

## 🧪 E2E 执行入口（2026-03 基线）

- 前端 E2E 默认入口统一为 `web/frontend/playwright.config.js`（`tests/e2e` 目录）。
- 推荐命令：`cd web/frontend && npm run test:e2e`。
- 单浏览器命令：`npm run test:e2e:chromium|firefox|webkit`。
- StrategyManagement 专项：`npm run test:e2e:strategy-chain`。
- 端口统一从 `.env` 读取：`FRONTEND_PORT=3020`、`FRONTEND_BACKUP_PORT=3021`、`BACKEND_PORT=8020`、`BACKEND_BACKUP_PORT=8021`。
- 历史 PM2/视觉专项脚本继续使用 `playwright.config.ts`（legacy），避免与主 E2E 链路混用。
- 历史文档兼容入口见：`docs/testing/TESTING_GUIDE.md` 与 `docs/testing/TESTING_EXAMPLES.md`。

## 🎯 快速开始

### 环境准备

开始之前，先完成：
1. 阅读 `architecture/STANDARDS.md`
2. 阅读根目录 `AGENTS.md`
3. 如涉及 proposal / plan / spec，再阅读 `openspec/AGENTS.md`

1. **克隆项目**
   ```bash
   git clone https://github.com/your-org/mystocks.git
   cd mystocks
   ```

2. **安装依赖**
   ```bash
   # Python环境
   pip install -r requirements.txt
   pip install -r requirements-dev.txt

   # 前端依赖
   cd web/frontend && npm install
   ```

3. **安装pre-commit hooks**
   ```bash
   pre-commit install
   pre-commit run --all-files
   ```

### 验证环境
```bash
# 运行本地CI检查
./scripts/ci/local_ci_check.sh

# 启动开发环境
docker-compose -f docker-compose.test.yml up -d
```

## 📂 分支策略

### 分支模型

我们采用 **Git Flow** 变体分支模型：

```
main (生产分支)
├── develop (开发主分支)
│   ├── feature/* (功能分支)
│   ├── release/* (发布分支)
│   └── hotfix/* (热修复分支)
└── experiment/* (实验分支)
```

### 分支命名规范

| 分支类型 | 命名格式 | 示例 | 生命周期 |
|---------|---------|------|---------|
| 功能分支 | `feature/功能描述-kebab-case` | `feature/user-authentication` | 开发完成后合并到develop |
| 发布分支 | `release/v版本号` | `release/v1.2.0` | 发布准备，测试完成后合并到main |
| 热修复分支 | `hotfix/问题描述` | `hotfix/critical-security-fix` | 紧急修复，修复后同时合并到main和develop |
| 实验分支 | `experiment/实验名称` | `experiment/new-trading-strategy` | 技术验证，不合并到主分支 |

### 开发工作流

#### 1. 开始新功能开发

```bash
# 确保本地develop分支最新
git checkout develop
git pull origin develop

# 创建功能分支
git checkout -b feature/new-quantization-strategy

# 开发代码...
# 提交时会自动触发pre-commit检查
git add .
git commit -m "feat: 实现新的量化策略算法"

# 推送到远程
git push origin feature/new-quantization-strategy
```

#### 2. 创建Pull Request

```bash
# 使用GitHub CLI创建PR
gh pr create \
  --title "feat: 新量化策略" \
  --body "实现XX量化策略，包含回测验证" \
  --base develop \
  --head feature/new-quantization-strategy
```

#### 3. 代码审查与合并

- ✅ CI流水线必须全部通过
- ✅ 至少1人审查通过（量化策略需要领域专家审查）
- ✅ 解决所有merge冲突
- ✅ 符合分支保护规则

#### 4. 发布流程

```bash
# 从develop创建release分支
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# 最终测试和版本更新
# 测试完成后合并到main
git checkout main
git merge release/v1.2.0
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin main --tags
```

## 🔄 CI/CD 流程

### 流水线概述

我们的CI/CD采用分层验证架构：

```
Git Push/PR
    ↓
本地pre-commit检查
    ↓
GitHub Actions流水线:
├── 代码质量检查 (Black, MyPy, Ruff, Bandit)
├── 量化策略验证 (语法检查 + 功能测试)
├── 安全扫描 (数据泄露 + SQL注入检查)
├── 集成测试 (API + 前端E2E)
├── 性能测试 (Lighthouse + 响应时间)
├── 部署测试环境 (自动)
└── 生产部署 (手动审批)
```

### 本地开发检查

#### pre-commit hooks

项目配置了以下自动检查：

- **Black**: 代码格式化
- **isort**: 导入排序
- **MyPy**: 类型检查
- **本地CI**: 快速质量验证
- **量化策略**: 语法检查

#### 手动本地检查

```bash
# 运行完整本地CI
./scripts/ci/local_ci_check.sh

# 只检查Python代码质量
black --check src/ web/backend/app/
mypy src/ --ignore-missing-imports

# 检查量化策略
python -c "
import sys
sys.path.insert(0, 'src')
# 策略检查代码
"
```

### GitHub Actions 流水线

#### 触发条件

| 事件 | 分支 | 触发流水线 |
|------|------|-----------|
| Push | main, develop | code-quality, test-coverage, comprehensive-testing |
| PR | main, develop | 所有流水线 + quantum-strategy-validation |
| Schedule | daily | monitoring-validation |
| Manual | any | deploy (指定环境) |

#### 主要流水线

1. **code-quality.yml**: 代码质量检查
   - Black, MyPy, Ruff, Bandit
   - 数据安全检查
   - 量化策略验证

2. **test-coverage.yml**: 测试覆盖率
   - 单元测试 + 集成测试
   - E2E测试
   - 覆盖率报告

3. **quantum-strategy-validation.yml**: 量化策略专项验证
   - 策略语法检查
   - 回测引擎验证
   - 性能基准测试

4. **deploy.yml**: 部署流水线
   - 测试环境自动部署
   - 生产环境手动审批

5. **monitoring-validation.yml**: 监控验证
   - 生产指标收集
   - 质量门禁检查
   - 自动告警

### 质量门禁标准

| 指标 | 阈值 | 说明 |
|------|------|------|
| 代码覆盖率 | ≥80% | 核心业务代码覆盖率 |
| API响应时间 | <2秒 | 95th percentile |
| 错误率 | <5% | 5分钟内错误请求比例 |
| 安全漏洞 | 0个 | 高危安全漏洞 |
| 量化策略验证 | 100% | 策略语法和逻辑检查 |

## 🚀 部署流程

### 测试环境部署

**触发**: 推送到develop分支自动部署

```bash
# 构建测试镜像
docker build -f web/backend/Dockerfile -t mystocks-backend:test ./web/backend
docker build -f web/frontend/Dockerfile -t mystocks-frontend:test ./web/frontend

# 启动测试环境
docker-compose -f docker-compose.test.yml up -d

# 运行部署后测试
curl http://localhost:8001/health
```

### 生产环境部署

**触发**: 手动触发GitHub Actions，选择生产环境

1. **预部署检查**
   - 所有CI流水线通过
   - 性能和安全评分达标
   - 人工确认部署

2. **部署执行**
   ```bash
   # 使用部署脚本
   ./scripts/deploy/deploy.sh production

   # 或回滚
   ./scripts/deploy/deploy.sh rollback production
   ```

3. **部署验证**
   - 健康检查通过
   - 核心功能验证
   - 监控告警正常

## 📊 监控与告警

### 关键指标监控

| 指标类型 | 监控内容 | 告警阈值 |
|---------|---------|----------|
| 性能指标 | API响应时间, CPU/内存使用率 | 响应时间>2秒, CPU>80% |
| 安全指标 | 错误率, 安全漏洞 | 错误率>5%, 发现高危漏洞 |
| 业务指标 | 用户体验评分, 策略成功率 | 评分<70, 成功率<90% |
| 系统指标 | 服务可用性, 数据库连接 | 服务宕机, 连接失败 |

### 监控面板

- **Grafana仪表板**: `http://localhost:3000`
  - API性能监控
  - 系统资源监控
  - 用户体验监控
  - 量化策略监控

- **Prometheus**: `http://localhost:9090`
  - 指标查询和告警规则

### 告警通知

- **即时告警**: 严重问题通过Webhook发送
- **日报报告**: 每日质量报告
- **周报分析**: 性能趋势分析

## 🛠️ 开发工具

### IDE配置

#### VS Code推荐配置
```json
{
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.mypyEnabled": true,
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

#### PyCharm配置
1. **代码格式化**: 设置Black为默认格式化工具
2. **类型检查**: 启用MyPy
3. **运行配置**: 添加pytest运行配置

### 调试技巧

#### 本地调试
```bash
# 启动调试服务器
python -m uvicorn app.main:app --reload --debug

# 启用调试日志
export LOG_LEVEL=DEBUG
python app/main.py
```

#### 数据库调试
```bash
# 连接测试数据库
psql -h localhost -p 5433 -U mystocks_test -d mystocks_test

# 查看慢查询
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

#### 前端调试
```bash
cd web/frontend
npm run serve -- --mode development
# 访问 http://localhost:8080
```

## 📚 代码规范

### Python代码规范

- **格式化**: 使用Black，行长度120字符
- **导入**: 使用isort，按类型分组
- **类型注解**: 所有函数参数和返回值必须标注类型
- **文档**: 公共函数必须有docstring
- **命名**: 蛇形命名法，私有方法以下划线开头

### 前端代码规范

- **格式化**: 使用Prettier
- **Linting**: 使用ESLint + TypeScript规则
- **组件**: 使用Vue 3 Composition API
- **状态管理**: 使用Pinia
- **样式**: 使用Tailwind CSS

### 量化策略规范

- **文件结构**: `src/strategies/strategy_name/`
- **命名规范**: 类名使用PascalCase
- **测试覆盖**: 策略核心逻辑必须有单元测试
- **文档**: 策略参数和逻辑必须有详细说明

## 🚨 故障排除

### 常见问题

#### pre-commit检查失败
```bash
# 查看失败详情
pre-commit run --verbose

# 跳过检查 (仅紧急情况)
git commit --no-verify -m "紧急修复"
```

#### CI流水线失败
1. 检查GitHub Actions日志
2. 本地重现问题
3. 查看具体错误信息
4. 修复后重新推送

#### 部署失败
1. 检查部署日志
2. 验证环境配置
3. 联系DevOps团队
4. 如需回滚，使用rollback命令

### 获取帮助

- **📖 文档**: 查看项目docs目录
- **💬 讨论**: 在GitHub Issues中提问
- **👥 团队**: 联系项目维护者
- **🔧 工具**: 使用项目提供的脚本和工具

## 🎯 最佳实践

### 代码提交

1. **小步提交**: 避免大块修改
2. **清晰描述**: 提交信息要说明做了什么和为什么
3. **关联Issue**: 提交时关联相关Issue

### 代码审查

1. **自查**: 提交前自己检查代码
2. **测试**: 确保所有测试通过
3. **文档**: 更新相关文档
4. **审查**: 耐心等待审查并及时响应

### 性能优化

1. **监控**: 关注性能指标变化
2. **基准**: 建立性能基准测试
3. **优化**: 定期review和优化代码
4. **测试**: 确保优化不影响功能

### 安全意识

1. **验证**: 所有输入都要验证
2. **加密**: 敏感数据要加密存储
3. **审计**: 定期进行安全审计
4. **更新**: 及时更新依赖包

---

## 📞 联系我们

- **项目主页**: https://github.com/your-org/mystocks
- **文档站点**: https://docs.mystocks.local
- **技术支持**: dev-support@mystocks.local

**祝你在MyStocks开发中取得成功！🚀**
