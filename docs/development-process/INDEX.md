# 开发流程文档索引

**版本**: 1.0
**日期**: 2025-10-29
**用途**: 5 层验证流程的完整文档导航

---

## 📖 快速导航

### 🎯 核心文档(必读)

| 文档 | 说明 | 适用场景 | 阅读时间 |
|------|------|---------|---------|
| [README.md](./README.md) | 开发流程快速入门 | 新人上手 | 5 分钟 |
| [definition-of-done.md](./definition-of-done.md) | 新的"完成"标准定义 | 所有开发任务 | 10 分钟 |
| [onboarding-checklist.md](./onboarding-checklist.md) | 60分钟上手清单 | 新人第一天 | 60 分钟 |

### 🔧 工具与方法

| 文档 | 说明 | 适用场景 | 阅读时间 |
|------|------|---------|---------|
| [tool-selection-guide.md](./tool-selection-guide.md) | 工具选型完整指南 | 选择验证工具 | 15 分钟 |
| [tool-comparison.md](./tool-comparison.md) | MCP vs AGENTS vs Manual | 决策对比 | 10 分钟 |
| [manual-verification-guide.md](./manual-verification-guide.md) | Layer 4/5 手动验证步骤 | UI+数据验证 | 10 分钟 |
| [troubleshooting.md](./troubleshooting.md) | 5大常见问题诊断 | 遇到问题时 | 参考 |

### 📊 采纳与度量

| 文档 | 说明 | 适用场景 | 阅读时间 |
|------|------|---------|---------|
| [adoption-metrics.md](./adoption-metrics.md) | SC-001 功能可用率跟踪 | 度量改进 | 5 分钟 |

### 📝 示例与参考

| 文档 | 说明 | 适用场景 | 阅读时间 |
|------|------|---------|---------|
| [examples/api-fix-example.md](./examples/api-fix-example.md) | API 修复完整示例 | 修复 API Bug | 10 分钟 |
| [examples/ui-fix-example.md](./examples/ui-fix-example.md) | UI 修复完整示例 | 修复 UI Bug | 10 分钟 |
| [examples/data-integration-example.md](./examples/data-integration-example.md) | 数据集成完整示例 | 集成新数据源 | 15 分钟 |

---

## 🗂️ 按层级分类

### Layer 5: 数据层验证

**文档**:
- [manual-verification-guide.md](./manual-verification-guide.md#layer-5-数据层验证) - SQL 验证模板
- [troubleshooting.md](./troubleshooting.md#场景-3-数据库连接失败) - 数据库问题排查

**工具**:
- pgcli - PostgreSQL 交互式客户端
- SQL 查询 - 数据验证

**快速检查**:
```bash
# 连接数据库
source scripts/bash_aliases.sh
mt-db

# 验证数据
SELECT COUNT(*) FROM cn_stock_top;
SELECT MAX(trade_date) FROM cn_stock_top;
```

---

### Layer 2: API 层验证

**文档**:
- [specs/006-web-90-1/contracts/api-verification-guide.md](../../specs/006-web-90-1/contracts/api-verification-guide.md) - API 验证完整指南
- [tool-selection-guide.md](./tool-selection-guide.md#layer-2-api-层工具) - httpie 使用指南
- [troubleshooting.md](./troubleshooting.md#场景-1-api-返回-500-错误) - API 问题排查

**工具**:
- httpie - HTTP 客户端(推荐)
- curl - 备选工具
- MCP Tools - 批量验证

**快速检查**:
```bash
# 获取 token
TOKEN=$(mt-token)

# 测试 API
http GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=5" \
  Authorization:"Bearer $TOKEN"
```

---

### Layer 4: UI 层验证

**文档**:
- [manual-verification-guide.md](./manual-verification-guide.md#layer-4-ui-层验证) - 浏览器 DevTools 使用
- [tool-selection-guide.md](./tool-selection-guide.md#layer-4-ui-层工具) - Chrome DevTools 指南
- [troubleshooting.md](./troubleshooting.md#场景-4-前端控制台报-javascript-错误) - UI 问题排查

**工具**:
- 浏览器 DevTools (F12) - 手动验证
- MCP Playwright - 快速截图
- Playwright 脚本 - 自动化验证

**快速检查**:
1. 打开浏览器访问页面
2. 按 F12 打开 DevTools
3. 检查 Console - 无红色错误
4. 检查 Network - API 请求成功

---

### Layer 3: 集成层验证

**文档**:
- [definition-of-done.md](./definition-of-done.md#layer-3-集成层-integration) - 集成测试标准
- [tool-selection-guide.md](./tool-selection-guide.md#layer-3-集成层工具) - Playwright 指南
- [specs/006-web-90-1/contracts/playwright-test-examples/](../../specs/006-web-90-1/contracts/playwright-test-examples/) - 测试示例

**工具**:
- Playwright - 浏览器自动化
- pytest - 测试框架

**快速运行**:
```bash
# 运行集成测试
pytest tests/integration/test_user_login_flow.py -v

# 运行所有集成测试
pytest tests/integration/ -v
```

---

### Layer 1: 代码层验证

**文档**:
- [definition-of-done.md](./definition-of-done.md#layer-1-代码层-code) - 代码质量标准
- [tool-selection-guide.md](./tool-selection-guide.md#layer-1-代码层工具) - Linter 工具

**工具**:
- pytest - 单元测试
- black - 代码格式化
- flake8 - 代码风格检查

**快速检查**:
```bash
# 运行单元测试
pytest tests/unit/ -v

# 代码格式化
black app/

# 代码风格检查
flake8 app/
```

---

## 🎯 按场景分类

### 场景 1: 新人上手

**推荐阅读顺序**:
1. [README.md](./README.md) - 5 分钟了解流程
2. [onboarding-checklist.md](./onboarding-checklist.md) - 60 分钟完整上手
3. [tool-selection-guide.md](./tool-selection-guide.md) - 15 分钟了解工具
4. [definition-of-done.md](./definition-of-done.md) - 10 分钟理解标准

**动手实践**:
- 完成 onboarding-checklist.md 中的所有练习
- 运行一次完整的 5 层验证
- 查看示例文档学习真实场景

---

### 场景 2: 开发新功能

**验证流程**:
1. **Layer 5**: [manual-verification-guide.md](./manual-verification-guide.md#layer-5-数据层验证) - 检查数据
2. **Layer 2**: [API 验证指南](../../specs/006-web-90-1/contracts/api-verification-guide.md) - 测试 API
3. **Layer 4**: [manual-verification-guide.md](./manual-verification-guide.md#layer-4-ui-层验证) - 检查 UI
4. **Layer 3**: 编写集成测试 (参考 [examples/](./examples/))
5. **截图**: 保存到 `docs/verification-screenshots/`

**参考示例**:
- [data-integration-example.md](./examples/data-integration-example.md)

---

### 场景 3: 修复 Bug

**诊断步骤**:
1. [troubleshooting.md](./troubleshooting.md) - 快速诊断问题
2. [definition-of-done.md](./definition-of-done.md#5-层验证流程) - 使用 5 层定位
3. 修复后重新验证所有相关层

**常见问题**:
- API 500 错误 → [troubleshooting.md](./troubleshooting.md#场景-1-api-返回-500-错误)
- 前端无数据 → [troubleshooting.md](./troubleshooting.md#场景-2-前端页面显示无数据)
- 数据库连接失败 → [troubleshooting.md](./troubleshooting.md#场景-3-数据库连接失败)

**参考示例**:
- [api-fix-example.md](./examples/api-fix-example.md)
- [ui-fix-example.md](./examples/ui-fix-example.md)

---

### 场景 4: 工具选择

**决策流程**:
1. [tool-selection-decision-tree.md](../../specs/006-web-90-1/contracts/tool-selection-decision-tree.md) - 30 秒快速决策
2. [tool-comparison.md](./tool-comparison.md) - 详细对比分析

**快速参考**:
- 单个 API 测试 → httpie
- 多个 API 测试 → MCP Tools
- 简单 UI 验证 → 手动浏览器
- 复杂流程自动化 → Playwright 脚本

---

## 📁 文件结构

```
docs/development-process/
├── README.md                          # 快速入门
├── INDEX.md                           # 本文档(文档索引)
├── definition-of-done.md              # 核心:DoD 标准
├── tool-selection-guide.md            # 工具选型完整指南
├── tool-comparison.md                 # 工具对比矩阵
├── manual-verification-guide.md       # Layer 4/5 手动验证
├── troubleshooting.md                 # 故障排查指南
├── onboarding-checklist.md            # 新人上手清单
├── adoption-metrics.md                # 采纳度量指标
└── examples/                          # 真实场景示例
    ├── api-fix-example.md
    ├── ui-fix-example.md
    └── data-integration-example.md

specs/006-web-90-1/contracts/
├── tool-selection-decision-tree.md    # 工具决策树
├── api-verification-guide.md          # API 验证指南
└── playwright-test-examples/          # Playwright 示例
    ├── example_login_flow.py
    ├── example_dashboard_data.py
    └── example_layer_failure_detection.py

scripts/
├── bash_aliases.sh                    # 快捷命令
├── api_templates.sh                   # API 验证模板
└── sql_templates.sql                  # SQL 查询模板

tests/integration/
├── conftest.py                        # Playwright 配置
├── test_user_login_flow.py            # 登录流程测试
├── test_dashboard_data_display.py     # 仪表盘测试
├── test_data_table_rendering.py       # 数据表格测试
└── utils/
    ├── browser_helpers.py
    └── layer_validation.py
```

---

## 🚀 快速命令参考

### Bash 别名

加载快捷命令:
```bash
source scripts/bash_aliases.sh
```

**常用别名**:
- `mt-token` - 获取 API token
- `mt-db` - 连接数据库
- `mt-api-dragon` - 测试龙虎榜 API
- `mt-api-summary` - 测试仪表盘 API

### 测试命令

```bash
# 单元测试
pytest tests/unit/ -v

# 集成测试
pytest tests/integration/ -v

# 特定测试
pytest tests/integration/test_user_login_flow.py -v

# 带截图的测试
pytest tests/integration/ -v --headed --screenshot=on
```

### 验证命令

```bash
# Layer 5: 数据库验证
mt-db -c "SELECT COUNT(*) FROM cn_stock_top"

# Layer 2: API 验证
TOKEN=$(mt-token)
http GET "http://localhost:8000/api/market/v3/dragon-tiger?limit=5" \
  Authorization:"Bearer $TOKEN"

# Layer 1: 代码质量
pytest tests/unit/ -v && black app/ && flake8 app/
```

---

## 📈 学习路径

### 第 1 天: 基础理解
- ✅ 阅读 README.md (5 分钟)
- ✅ 完成 onboarding-checklist.md (60 分钟)
- ✅ 运行一次完整验证 (15 分钟)

### 第 1 周: 熟练应用
- ✅ 使用 5 层验证修复 1 个 Bug
- ✅ 开发 1 个新功能并完整验证
- ✅ 编写 1 个 Playwright 测试

### 第 1 月: 精通
- ✅ 独立选择合适的验证工具
- ✅ 快速诊断和定位问题
- ✅ 贡献文档和示例

---

## 🔗 相关资源

### 项目根目录
- [README.md](../../README.md) - 项目总体说明
- [CLAUDE.md](../../CLAUDE.md) - Claude Code 指导文档

### 规范文档
- [specs/006-web-90-1/](../../specs/006-web-90-1/) - Web 功能完整规范

### 测试目录
- [tests/integration/](../../tests/integration/) - 集成测试套件
- [tests/unit/](../../tests/unit/) - 单元测试套件

---

## ❓ 常见问题

### Q: 我应该从哪里开始?
**A**: 从 [onboarding-checklist.md](./onboarding-checklist.md) 开始,60 分钟完整上手。

### Q: 如何选择验证工具?
**A**: 查看 [tool-selection-decision-tree.md](../../specs/006-web-90-1/contracts/tool-selection-decision-tree.md) 30 秒快速决策。

### Q: 遇到问题如何排查?
**A**: 查看 [troubleshooting.md](./troubleshooting.md) 常见问题诊断。

### Q: 每次都要验证 5 层吗?
**A**: 简单修改可以只验证相关层,但新功能建议完整验证。详见 [definition-of-done.md](./definition-of-done.md)。

### Q: 文档是否有中文版?
**A**: 所有核心文档都是中文,部分示例代码为英文注释。

---

## 📞 获取帮助

- 📖 **查看文档**: 按照本索引查找相关文档
- 🔍 **搜索关键词**: 使用 `grep -r "关键词" docs/development-process/`
- 💡 **查看示例**: `docs/development-process/examples/` 目录
- 🧪 **运行测试**: `pytest tests/integration/ -v` 学习测试写法

---

**版本历史**:
- v1.0 (2025-10-29): 初始版本,完整文档索引
