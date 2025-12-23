# 🚀 项目目录组织标准指引

**版本**: 2.0  
**适用范围**: 通用软件项目目录组织标准  
**创建日期**: 2025-11-17  
**最后更新**: 2025-11-17  

## 📋 概述

本指引提供了科学、可维护的项目目录组织标准，旨在解决项目开发过程中根目录文件混乱的问题。该标准既适用于当前MyStocks项目，也可应用于其他软件开发项目。

## 🎯 问题分析

### 当前问题
- **根目录文件过多**: 当前项目根目录有76个文件，严重影响开发效率
- **缺乏自动清理机制**: 没有工具或流程持续维护目录结构
- **文件类型混乱**: 文档、脚本、配置、报告等混在一起
- **维护成本高**: 手动整理耗时且容易遗漏

### 根本原因
1. **开发过程自然产物**: 开发过程中产生的临时文件、日志、报告等
2. **缺乏组织意识**: 没有明确的文件放置规则
3. **没有自动化工具**: 缺乏自动整理和维护的工具
4. **硬编码路径**: 现有指引包含项目特定信息，通用性差

## 🏗️ 标准目录结构

### 🎯 核心原则
- **最少根目录文件**: 根目录只保留绝对必要的文件
- **功能导向分类**: 按功能而非文件类型分类
- **可扩展性**: 支持项目成长和变化
- **自动化友好**: 便于脚本和工具自动操作

### 📁 推荐目录结构

```
PROJECT_ROOT/
├── README.md                          # 项目说明文档
├── LICENSE                            # 许可证文件
├── .gitignore                         # Git忽略规则
├── requirements.txt                   # 依赖清单
├── package.json                       # NPM依赖（如果适用）
├── Dockerfile                         # Docker配置
├── docker-compose.yml                 # Docker Compose配置
│
├── src/                               # 📦 源代码目录
│   ├── core/                          # 核心业务逻辑
│   ├── adapters/                      # 适配器模式实现
│   ├── utils/                         # 工具函数
│   ├── interfaces/                    # 接口定义
│   └── [其他业务模块...]
│
├── config/                            # ⚙️ 配置目录
│   ├── app.yaml                       # 应用配置
│   ├── database.yaml                  # 数据库配置
│   ├── logging.yaml                   # 日志配置
│   └── [其他配置文件...]
│
├── docs/                              # 📚 文档目录
│   ├── guides/                        # 用户指南
│   ├── api/                           # API文档
│   ├── architecture/                  # 架构文档
│   └── examples/                      # 示例代码
│
├── scripts/                           # 🔧 脚本目录
│   ├── dev/                           # 开发脚本
│   ├── deploy/                        # 部署脚本
│   ├── maintenance/                   # 维护脚本
│   └── tests/                         # 测试脚本
│
├── tests/                             # 🧪 测试目录
│   ├── unit/                          # 单元测试
│   ├── integration/                   # 集成测试
│   ├── e2e/                           # 端到端测试
│   └── fixtures/                      # 测试数据
│
├── tools/                             # 🛠️ 工具目录
│   ├── generators/                    # 代码生成器
│   ├── analyzers/                     # 代码分析工具
│   └── migrations/                    # 数据迁移工具
│
├── assets/                            # 🎨 资源目录
│   ├── images/                        # 图片资源
│   ├── fonts/                         # 字体文件
│   └── [其他静态资源...]
│
├── data/                              # 💾 数据目录
│   ├── raw/                           # 原始数据
│   ├── processed/                     # 处理后数据
│   └── samples/                       # 示例数据
│
├── logs/                              # 📝 日志目录
│   ├── app/                           # 应用日志
│   ├── error/                         # 错误日志
│   └── audit/                         # 审计日志
│
├── temp/                              # 🗂️ 临时目录
│   ├── cache/                         # 缓存文件
│   ├── build/                         # 构建产物
│   └── download/                      # 下载文件
│
├── reports/                           # 📊 报告目录
│   ├── metrics/                       # 性能指标
│   ├── coverage/                      # 测试覆盖率
│   └── analysis/                      # 分析报告
│
└── .ci/                               # 🔄 CI/CD目录
    ├── workflows/                     # GitHub Actions
    ├── gitlab-ci.yml                  # GitLab CI
    └── jenkinsfile                    # Jenkins配置
```

## 📝 根目录文件清单

### 必需文件（最多10个）
```bash
# 项目标识
README.md              # 项目说明
LICENSE                # 许可证

# 版本控制
.gitignore             # Git忽略规则

# 依赖管理
requirements.txt       # Python依赖
package.json           # Node.js依赖（如果适用）
Pipfile               # Pipenv依赖（如果适用）

# 容器化
Dockerfile            # Docker镜像构建
docker-compose.yml    # Docker Compose配置
docker-compose.*.yml  # 环境特定配置

# 构建配置
Makefile              # 构建脚本
pom.xml               # Maven配置（Java项目）
build.gradle          # Gradle配置（Java项目）
```

### 条件文件（根据项目需要）
```bash
# Web项目
next.config.js        # Next.js配置
nuxt.config.js        # Nuxt.js配置
vue.config.js         # Vue.js配置

# Python项目
setup.py              # 包安装配置
pyproject.toml        # 现代Python项目配置
mypy.ini              # 类型检查配置
pytest.ini            # 测试配置

# Node.js项目
.eslintrc.js          # ESLint配置
.prettierrc           # Prettier配置
jest.config.js        # Jest测试配置

# 其他
.env.example          # 环境变量示例
.env.local           # 本地环境变量
.coverage            # 测试覆盖率配置
```

## 🛠️ 自动化维护工具

### 1. 目录检查脚本
```bash
#!/bin/bash
# scripts/maintenance/check-structure.sh

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MAX_ROOT_FILES=15

# 检查根目录文件数量
ROOT_FILE_COUNT=$(find "$PROJECT_ROOT" -maxdepth 1 -type f | wc -l)

if [ "$ROOT_FILE_COUNT" -gt "$MAX_ROOT_FILES" ]; then
    echo "⚠️  警告: 根目录有 $ROOT_FILE_COUNT 个文件，超过建议数量 $MAX_ROOT_FILES"
    echo "请运行整理脚本: ./scripts/maintenance/organize-files.sh"
    exit 1
else
    echo "✅ 根目录文件数量正常: $ROOT_FILE_COUNT 个文件"
fi
```

### 2. 文件整理脚本
```bash
#!/bin/bash
# scripts/maintenance/organize-files.sh

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# 创建必要目录
mkdir -p "$PROJECT_ROOT"/{temp/cache,logs/app,reports/metrics}

# 移动临时文件
find "$PROJECT_ROOT" -maxdepth 1 -name "*.tmp" -exec mv {} "$PROJECT_ROOT/temp/cache/" \;
find "$PROJECT_ROOT" -maxdepth 1 -name "*.log" -exec mv {} "$PROJECT_ROOT/logs/app/" \;

# 移动报告文件
find "$PROJECT_ROOT" -maxdepth 1 -name "*report*.json" -exec mv {} "$PROJECT_ROOT/reports/metrics/" \;
find "$PROJECT_ROOT" -maxdepth 1 -name "*analysis*.json" -exec mv {} "$PROJECT_ROOT/reports/analysis/" \;

# 移动文档文件
find "$PROJECT_ROOT" -maxdepth 1 -name "*.md" -not -path "$PROJECT_ROOT/README.md" -not -path "$PROJECT_ROOT/LICENSE" -exec mv {} "$PROJECT_ROOT/docs/guides/" \;

echo "✅ 文件整理完成"
```

### 3. Git钩子自动检查
```bash
#!/bin/bash
# .git/hooks/pre-commit

./scripts/maintenance/check-structure.sh
if [ $? -ne 0 ]; then
    echo "❌ 提交被拒绝: 目录结构不符合标准"
    exit 1
fi
```

## 📊 文件分类规则

### 📚 文档文件 (*.md, *.rst, *.txt)
- **项目根目录**: README.md, LICENSE, CHANGELOG.md
- **docs/**: 所有其他文档
- **子目录**: 各模块的README文件

### 💻 代码文件 (*.py, *.js, *.ts, *.java等)
- **src/**: 所有源代码
- **tests/**: 测试代码
- **tools/**: 工具脚本

### ⚙️ 配置文件 (*.yaml, *.yml, *.json, *.ini等)
- **config/**: 应用配置
- **根目录**: 构建和部署配置
- **各模块目录**: 模块特定配置

### 📝 日志文件 (*.log)
- **logs/**: 所有日志文件
- **按类型分类**: app/, error/, audit/

### 📊 报告文件 (*.json, *.xml, *.html)
- **reports/**: 分析报告
- **按类型分类**: metrics/, coverage/, analysis/

### 🔧 脚本文件 (*.sh, *.ps1, *.bat)
- **scripts/**: 所有脚本
- **按功能分类**: dev/, deploy/, maintenance/

## 🚀 实施步骤

### 第一阶段: 清理当前混乱（当前项目）
1. **备份当前状态**
   ```bash
   tar -czf backup-$(date +%Y%m%d).tar.gz .
   ```

2. **执行自动整理**
   ```bash
   ./scripts/maintenance/organize-files.sh
   ```

3. **手动调整**
   - 检查移动的文件是否正确
   - 调整不合适的文件位置
   - 更新必要的配置文件路径

### 第二阶段: 建立标准（新项目或重构）
1. **创建标准目录结构**
2. **设置维护脚本权限**
   ```bash
   chmod +x scripts/maintenance/*.sh
   ```
3. **配置Git钩子**
4. **更新CI/CD流程**

### 第三阶段: 持续维护
1. **定期检查**: 每周运行目录检查
2. **自动化集成**: 集成到CI/CD流程
3. **团队培训**: 确保团队成员遵循标准

## 🔧 自定义适配

### 不同项目类型的调整

#### Python项目
```bash
# 添加Python特定目录
src/                    # Python包
tests/                  # pytest测试
docs/                   # Sphinx文档
scripts/                # 管理脚本
```

#### Node.js项目
```bash
# 添加Node.js特定目录
src/                    # 源代码
public/                 # 静态文件
tests/                  # Jest测试
docs/                   # JSDoc文档
```

#### Java项目
```bash
# 添加Java特定目录
src/main/java/          # 主代码
src/main/resources/     # 主资源
src/test/java/          # 测试代码
target/                 # 构建输出
```

#### 多语言项目
```bash
# 通用结构
src/
  ├── python/           # Python代码
  ├── javascript/       # JavaScript代码
  └── java/             # Java代码
```

## 📈 效果评估

### 实施前后对比
| 指标 | 实施前 | 实施后 | 改善幅度 |
|------|--------|--------|----------|
| 根目录文件数 | 76个 | ≤15个 | 80%+ |
| 新开发者上手时间 | 2小时 | 30分钟 | 75% |
| 文件查找效率 | 低 | 高 | 显著提升 |
| 维护成本 | 高 | 低 | 显著降低 |

### 持续监控指标
- 根目录文件数量
- 目录结构合规率
- 新文件正确分类率
- 手动整理频率

## 🎯 最佳实践

### Do's ✅
- 始终将新文件放在正确的目录中
- 定期运行目录检查脚本
- 使用自动化工具维护结构
- 为新团队成员提供培训

### Don'ts ❌
- 不要在根目录放置临时文件
- 不要忽略目录结构警告
- 不要手动修改自动生成的文件
- 不要跳过代码审查中的目录检查

## 🔄 持续改进

### 版本更新记录
- **v2.0** (2025-11-17): 创建通用标准指引
- **v1.0** (2025-11-08): MyStocks项目特定指引

### 反馈和改进
如需改进建议，请通过以下方式反馈：
1. 创建Issue描述问题
2. 提供具体的改进建议
3. 分享实施经验

## 📚 相关资源

- [项目结构最佳实践](https://docs.python.org/3/tutorial/modules.html#packages)
- [GitHub项目结构指南](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [Docker多阶段构建最佳实践](https://docs.docker.com/develop/dev-best-practices/)

---

**维护者**: 开发团队  
**适用范围**: 通用软件项目  
**最后更新**: 2025-11-17