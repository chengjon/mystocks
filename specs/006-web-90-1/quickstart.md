# Web 应用开发流程快速上手指南

**版本**: 1.0
**日期**: 2025-10-29
**目标**: 30 分钟快速掌握新的开发验证流程

---

## 🎯 概述 (5 分钟阅读)

### 什么改变了？

**之前**:
- ✅ 代码通过测试 → 功能完成
- ❌ 结果: 90% 功能用户无法使用

**现在**:
- ✅ 代码通过测试
- ✅ API 返回正确数据
- ✅ 前端正确调用 API
- ✅ 用户可以看到数据
- ✅ **完成**: 用户可以实际使用功能

### 核心变化

**新增 4 个验证步骤**:

```
1. 代码层 → 2. API 层 → 3. 集成层 → 4. UI 层 → 5. 数据层
   (已有)      (新增)       (新增)       (新增)      (新增)
```

### 额外时间投入

- 简单 Bug: +35 分钟
- 中等功能: +50 分钟
- 复杂功能: +90 分钟

**收益**:
- 90% 功能用户可用 (原来只有 10%)
- 减少 75% 返工时间
- 提升产品质量和用户信任

---

## ⚙️ 环境设置 (10 分钟)

### 步骤 1: 安装工具

```bash
# 1. Playwright (浏览器自动化)
pip install playwright pytest-playwright
playwright install chromium

# 2. HTTP 工具
pip install httpie

# 3. JSON 处理工具
# Ubuntu/Debian
sudo apt install jq

# macOS
brew install jq

# 4. 数据库客户端
pip install pgcli
```

### 步骤 2: 配置快捷命令

```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
cat >> ~/.bashrc << 'EOF'

# MyStocks 验证快捷命令
export MYSTOCKS_URL="http://localhost:8000"
export MYSTOCKS_USER="admin"
export MYSTOCKS_PASS="admin123"

# 快速获取 token
alias mt-token='http POST $MYSTOCKS_URL/api/auth/login username=$MYSTOCKS_USER password=$MYSTOCKS_PASS | jq -r ".access_token"'

# 快速验证 API
function mt-api() {
  local endpoint=$1
  local token=$(mt-token)
  http GET "$MYSTOCKS_URL$endpoint" Authorization:"Bearer $token"
}

# 快速进入 PostgreSQL
alias mt-db='PGPASSWORD=mystocks2025 pgcli -h localhost -U mystocks_user -d mystocks'

EOF

# 生效配置
source ~/.bashrc
```

### 步骤 3: 验证设置

```bash
# 测试 API 工具
mt-token  # 应该返回一个 JWT token

# 测试数据库连接
mt-db
# 在 pgcli 中执行: SELECT 1;
# 应该返回: 1

# 退出 pgcli: \q
```

---

## 🧪 你的第一次验证 (15 分钟实战)

假设你刚修复了一个 Bug: "Dashboard API 返回空数据"

### Layer 1: 代码层 (2 分钟)

```bash
# 1. 运行单元测试
cd /opt/claude/mystocks_spec
pytest tests/unit/ -v

# 2. 代码格式检查
black . && flake8 .

# ✅ 通过 → 进入 Layer 2
```

### Layer 2: API 层 (3 分钟)

```bash
# 1. 确保后端运行
# 在另一个终端: cd web/backend && python -m uvicorn app.main:app --reload

# 2. 使用快捷命令验证 API
mt-api /api/data/dashboard/summary

# 期望输出:
# {
#   "data": [...]  # 有数据
# }

# 3. 验证数据不为空
mt-api /api/data/dashboard/summary | jq -e '.data != null'

# 期望输出: true

# ✅ 通过 → 进入 Layer 3
```

### Layer 3: 集成层 (2 分钟)

```bash
# 运行集成测试
pytest tests/integration/test_dashboard_data_display.py -v

# 期望输出:
# test_dashboard_data_display PASSED

# ✅ 通过 → 进入 Layer 4
```

### Layer 4: UI 层 (5 分钟)

```bash
# 1. 确保前端运行
# 在另一个终端: cd web/frontend && npm run dev

# 2. 打开浏览器
# 访问: http://localhost:8000/dashboard

# 3. 检查 Console (F12 → Console)
# ✅ 无红色错误

# 4. 检查 Network (F12 → Network)
# ✅ /api/data/dashboard/summary 状态 200

# 5. 截图
# Ctrl+Shift+P → "Capture screenshot"
# 保存到: docs/verification-screenshots/dashboard-fix-20251029-ui.png

# ✅ 通过 → 进入 Layer 5
```

### Layer 5: 数据层 (3 分钟)

```bash
# 1. 进入数据库
mt-db

# 2. 检查数据存在
SELECT COUNT(*) FROM cn_stock_top;

# 期望: > 0

# 3. 检查最新数据
SELECT MAX(trade_date) FROM cn_stock_top;

# 期望: 今天或最近日期

# 4. 退出
\q

# ✅ 所有层通过 → 功能完成！
```

### 完成

```bash
# 1. 填写检查清单
# 复制 contracts/definition-of-done-checklist.md
# 填写所有检查项

# 2. 提交 PR
git add .
git commit -m "fix(dashboard): Fix empty data issue"
git push origin feature/fix-dashboard-data

# 3. 创建 Pull Request
gh pr create --title "Fix dashboard empty data issue" \
  --body "All 5 verification layers passed. See screenshots in docs/verification-screenshots/"
```

---

## 📋 常用命令速查表

### API 验证

```bash
# 获取 Token
TOKEN=$(mt-token)

# 验证 API (方法 1: 使用快捷命令)
mt-api /api/data/dashboard/summary

# 验证 API (方法 2: 完整命令)
http GET http://localhost:8000/api/data/dashboard/summary \
  Authorization:"Bearer $TOKEN"

# 验证数据不为空
mt-api /api/data/dashboard/summary | jq -e '.data != null'

# 验证特定字段
mt-api /api/market/dragon-tiger?limit=5 | jq -e '.data | length == 5'
```

### 数据库查询

```bash
# PostgreSQL
mt-db

# TDengine
taos -h 192.168.123.104 -u root -p taosdata

# 常用 SQL 模板
SELECT COUNT(*) FROM table_name;  # 数据量
SELECT MAX(trade_date) FROM table_name;  # 最新数据
SELECT * FROM table_name ORDER BY created_at DESC LIMIT 10;  # 查看样本
```

### 测试命令

```bash
# 单元测试
pytest tests/unit/ -v

# 集成测试
pytest tests/integration/ -v

# 特定测试
pytest tests/integration/test_dashboard_data_display.py -v

# 冒烟测试 (快速验证)
pytest tests/smoke/ -v -x  # -x: 第一个失败立即停止
```

### 浏览器快捷键

```bash
F12               # 打开 DevTools
Ctrl+Shift+J      # 直接打开 Console
Ctrl+Shift+E      # 直接打开 Network
Ctrl+Shift+C      # 启用元素选择模式
Ctrl+Shift+P      # 命令面板 (截图)
Ctrl+L            # 清除 Console
```

---

## ❓ 常见问题 (FAQ)

### Q1: 验证时间超过预算怎么办？

**A**: 首次使用新流程可能超时 20-30%，这是正常的。

**策略**:
1. **关键路径优先**: 先验证最重要的功能
2. **跳过边缘场景**: 简单任务可以跳过部分验证
3. **标记"部分完成"**: 在下个 sprint 补充完整验证

### Q2: 集成测试失败怎么办？

**A**: 集成测试会明确告诉你哪一层失败。

**分层排查**:
```python
# 测试输出示例
AssertionError: UI Layer Failed: 数据表未渲染
  可能原因:
  1. API 未返回数据 → 检查 Layer 2
  2. 前端未调用 API → 检查 Network 标签
  3. 前端渲染逻辑错误 → 检查 Console 错误
```

**处理步骤**:
1. 查看测试报告，确定失败的层
2. 回到对应的 Layer 手动验证
3. 修复问题后重新运行测试

### Q3: 如何判断是否需要 MCP 工具？

**A**: 所有 API 验证必须使用 MCP 工具或 httpie。

**决策树**:
```
修改了 API？
  ├─ 是 → 必须使用 httpie 或 MCP 验证所有相关端点
  └─ 否 → 只修改前端？
        ├─ 是 → 验证前端是否正确调用现有 API (Network 标签)
        └─ 否 → 只修改数据库？
              └─ 是 → 验证 SQL 查询 + API 返回数据正确性
```

### Q4: 不知道如何验证某个功能怎么办？

**A**: 查阅以下文档:

1. **检查清单**: `contracts/definition-of-done-checklist.md`
2. **流程框架**: `process-framework.md`
3. **测试示例**: `contracts/playwright-test-examples/`
4. **询问团队**: 在站会上提问

### Q5: 可以跳过某些验证步骤吗？

**A**: 取决于任务复杂度。

**允许跳过的情况**:
- 简单的文档修改: 跳过 Layer 3-5
- 仅修改 CSS 样式: 跳过 Layer 2, 5
- 一行代码修复: 可以简化 Layer 2-5 验证

**绝对不能跳过**:
- 任何涉及数据流的改动必须完整验证所有层
- API 修改必须验证 Layer 2
- 前端显示逻辑修改必须验证 Layer 4

---

## 🚀 进阶技巧

### 技巧 1: 使用脚本批量验证 API

```bash
# scripts/verify_all_apis.sh
#!/bin/bash
TOKEN=$(mt-token)

ENDPOINTS=(
  "/api/data/dashboard/summary"
  "/api/market/dragon-tiger?limit=5"
  "/api/market/etf-data?limit=5"
)

for endpoint in "${ENDPOINTS[@]}"; do
  echo "Testing: $endpoint"
  http GET "$MYSTOCKS_URL$endpoint" \
    Authorization:"Bearer $TOKEN" | \
    jq -e '.data != null' && echo "✅ PASS" || echo "❌ FAIL"
done
```

### 技巧 2: 自动截图

```bash
# 使用 Playwright 自动截图
pytest tests/integration/ --screenshot=on --video=retain-on-failure
```

### 技巧 3: 并行运行测试

```bash
# 安装 pytest-xdist
pip install pytest-xdist

# 并行运行测试 (2x-3x 更快)
pytest tests/integration/ -n auto
```

---

## 📚 下一步学习

完成快速上手后，深入阅读以下文档:

1. ⭐ **[流程框架文档](process-framework.md)**
   完整的 Definition of Done 理念和 5 层验证模型

2. ⭐ **[完成检查清单](contracts/definition-of-done-checklist.md)**
   每个任务必须填写的详细检查清单

3. **[Playwright 测试示例](contracts/playwright-test-examples/)**
   学习如何编写端到端集成测试

4. **[手动验证指南](contracts/manual-verification-checklist.md)**
   详细的手动验证步骤和最佳实践

5. **[冒烟测试清单](contracts/smoke-test-checklist.md)**
   部署前 5 分钟快速验证清单

---

## ✅ 检查清单: 你准备好了吗？

完成以下检查项，确保你已经掌握新流程:

- [ ] 已安装所有必需工具 (Playwright, httpie, jq, pgcli)
- [ ] 已配置快捷命令 (mt-token, mt-api, mt-db)
- [ ] 已验证环境设置 (能成功获取 token, 连接数据库)
- [ ] 已完成第一次完整验证 (5 层全部通过)
- [ ] 已阅读流程框架文档和检查清单
- [ ] 知道如何填写 Definition of Done 检查清单
- [ ] 知道遇到问题如何排查和求助

**如果所有项都勾选，恭喜！你已经准备好使用新流程了。🎉**

---

## 🆘 需要帮助？

- **文档**: 查阅 `specs/006-web-90-1/` 目录下的所有文档
- **团队**: 在每日站会上提问
- **示例**: 参考 `contracts/playwright-test-examples/` 中的代码
- **反馈**: 新流程有问题或建议？联系 Team Lead

---

**版本历史**:
- v1.0 (2025-10-29): 初始版本，提供 30 分钟快速上手指南
