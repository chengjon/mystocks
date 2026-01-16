# MyStocks 分支策略与开发流程

## 🎯 概述

基于个人/小型量化投资平台的特点，我们采用 **Git Flow** 变体分支模型，兼顾开发效率和代码质量。

## 📋 分支模型

### 🏗️ 永久分支 (Protected)

#### `main` - 生产分支
- **用途**: 生产环境代码，随时可部署
- **合并来源**: 仅从 `release` 分支合并
- **保护规则**:
  - ✅ 必须通过 CI 流水线
  - ✅ 必须由至少1人代码审查
  - ✅ 禁止直接推送 (force push)
  - ✅ 必须有测试覆盖率报告

#### `develop` - 开发分支
- **用途**: 集成所有开发功能
- **合并来源**: 所有 `feature/*` 分支
- **保护规则**:
  - ✅ 必须通过基础 CI 检查
  - ✅ 可直接推送 (开发团队内部)

### 🔄 临时分支 (Disposable)

#### `feature/*` - 功能分支
- **命名规则**: `feature/功能描述-kebab-case`
- **示例**:
  - `feature/strategy-backtest-optimization`
  - `feature/realtime-market-data`
  - `feature/user-authentication`
- **生命周期**: 从开发完成到合并到 `develop`

#### `release/*` - 发布分支
- **命名规则**: `release/v版本号`
- **示例**: `release/v1.2.0`
- **用途**: 生产发布准备和最终测试

#### `hotfix/*` - 热修复分支
- **命名规则**: `hotfix/问题描述`
- **示例**: `hotfix/critical-bug-fix`
- **直接从**: `main` 分支创建

#### `experiment/*` - 实验分支
- **命名规则**: `experiment/实验名称`
- **用途**: 尝试新技术、算法优化等

## 🔄 开发工作流

### 🚀 日常开发流程

#### 1. 开始新功能开发
```bash
# 1. 确保本地develop分支最新
git checkout develop
git pull origin develop

# 2. 创建功能分支
git checkout -b feature/new-quantization-strategy

# 3. 开发并提交 (频繁提交)
git add .
git commit -m "feat: 实现新的量化策略算法"

# 4. 推送到远程
git push origin feature/new-quantization-strategy
```

#### 2. 提交代码审查
```bash
# 创建 Pull Request 到 develop 分支
# 在GitHub上操作，或使用CLI：
gh pr create --title "feat: 新量化策略" \
             --body "实现XX量化策略，包含回测验证" \
             --base develop \
             --head feature/new-quantization-strategy
```

#### 3. 代码审查与合并
- ✅ CI 流水线通过
- ✅ 至少1人审查通过
- ✅ 无冲突自动合并，或解决冲突后合并

### 📈 发布流程

#### 定期发布 (每周/双周)
```bash
# 1. 从develop创建release分支
git checkout develop
git pull origin develop
git checkout -b release/v1.2.0

# 2. 最终测试和版本号更新
# 运行完整测试套件
./scripts/cicd_pipeline.sh

# 3. 合并到main
git checkout main
git merge release/v1.2.0

# 4. 打标签
git tag -a v1.2.0 -m "Release v1.2.0"
git push origin main --tags
```

#### 紧急修复
```bash
# 1. 从main创建hotfix分支
git checkout main
git pull origin main
git checkout -b hotfix/critical-security-fix

# 2. 修复问题并测试
# 3. 同时合并到main和develop
git checkout main
git merge hotfix/critical-security-fix
git push origin main

git checkout develop
git merge hotfix/critical-security-fix
git push origin develop
```

## 🛡️ 分支保护配置

### GitHub Branch Protection Rules

#### `main` 分支保护
```yaml
# .github/settings.yml 或手动配置
branches:
  - name: main
    protection:
      required_status_checks:
        required_check: ["ci-complete", "security-scan", "performance-test"]
      restrictions:
        enforce_admins: true
        required_pull_request_reviews:
          required_approving_review_count: 1
          dismiss_stale_reviews: true
      restrictions: []  # 可选：限制谁能推送
```

#### `develop` 分支保护
```yaml
branches:
  - name: develop
    protection:
      required_status_checks:
        required_check: ["basic-ci", "type-check"]
      required_pull_request_reviews:
        required_approving_review_count: 0  # 开发分支可灵活
```

## 🔧 自动化工具

### 1. 预提交检查 (pre-commit hooks)
```bash
# 安装pre-commit
pip install pre-commit
pre-commit install

# 配置 .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: run-local-ci
        name: Run Local CI
        entry: ./scripts/cicd_pipeline.sh
        language: system
        pass_filenames: false
```

### 2. 自动分支清理
```bash
# 定期清理合并的分支
# 添加到GitHub Actions或cron任务
git branch -r --merged origin/main | grep -v main | sed 's/origin\///' | xargs -I {} git push origin :{}
```

## 📊 量化平台特殊考虑

### 策略验证要求
- **强制**: 所有 `feature/*` 分支必须包含策略正确性测试
- **自动化**: CI流水线自动验证策略回测结果准确性
- **阈值**: 策略收益率偏差不得超过±5%

### 数据安全保护
- **敏感信息**: 禁止在代码中硬编码API密钥、数据库密码
- **扫描**: 强制通过安全扫描检查
- **审计**: 所有数据库操作记录审计日志

### 性能基准
- **响应时间**: API接口响应时间 < 2秒
- **内存使用**: 应用内存使用 < 85%
- **测试覆盖**: 核心业务代码覆盖率 > 80%

## 🎯 成功指标

### 质量指标
- ✅ CI通过率 > 95%
- ✅ 平均代码审查时间 < 4小时
- ✅ 生产环境缺陷密度 < 0.1个/千行代码

### 效率指标
- ✅ 功能分支平均生命周期 < 3天
- ✅ 从开发到部署的平均时间 < 2天
- ✅ 紧急修复响应时间 < 1小时

## 📚 相关文档

- [CI/CD流水线配置](./cicd_pipeline.md)
- [代码审查规范](./code_review_guidelines.md)
- [发布检查清单](./release_checklist.md)