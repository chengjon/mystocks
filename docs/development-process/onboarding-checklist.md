# 开发者上手清单

本清单帮助新开发者快速掌握 MyStocks 项目的 5 层验证开发流程。

**目标时间**: 60 分钟完成基础上手

---

## ✅ 第一步：环境准备 (15 分钟)

### 1.1 验证工具已安装
```bash
# Python 工具
pip list | grep playwright    # ✓ Playwright
pip list | grep httpie        # ✓ httpie
pip list | grep pgcli         # ✓ pgcli

# 系统工具
jq --version                  # ✓ jq
playwright --version          # ✓ Playwright CLI

# 浏览器
playwright install chromium   # ✓ Chromium
```

### 1.2 验证服务运行
```bash
# 后端
curl http://localhost:8000/health
# 预期: {"status":"ok"}

# 前端
curl http://localhost:5173
# 预期: HTML 响应

# 数据库
pg_isready -h localhost -p 5432
# 预期: accepting connections
```

### 1.3 配置环境变量
```bash
# 创建或编辑 .env 文件
cat > .env << 'EOF'
MYSTOCKS_URL=http://localhost:8000
MYSTOCKS_USER=admin
MYSTOCKS_PASS=admin123
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_USER=mystocks_user
POSTGRESQL_PASSWORD=mystocks2025
POSTGRESQL_DATABASE=mystocks
EOF

# 加载环境变量
export $(cat .env | xargs)
```

**检查点**: ✅ 所有工具已安装，服务正常运行

---

## ✅ 第二步：理解 5 层验证 (15 分钟)

### 2.1 阅读核心文档
```bash
# 1. Definition of Done (必读)
cat docs/development-process/definition-of-done.md

# 2. 工具选择指南
cat docs/development-process/tool-selection-guide.md

# 3. 手动验证指南
cat docs/development-process/manual-verification-guide.md
```

### 2.2 理解每一层的含义

| 层级 | 验证内容 | 工具 | 用时 |
|------|----------|------|------|
| Layer 5 | 数据库有数据且新鲜 | pgcli, SQL | 2 分钟 |
| Layer 2 | API 返回正确数据 | httpie | 2 分钟 |
| Layer 4 | UI 正确显示 | Browser F12 | 3 分钟 |
| Layer 3 | 完整流程畅通 | Playwright | 5 分钟 |
| Layer 1 | 代码质量合格 | pytest, linter | 5 分钟 |

**核心原则**: 自底向上验证（Layer 5 → Layer 1）

**检查点**: ✅ 理解 5 层验证模型和验证顺序

---

## ✅ 第三步：动手实践 (20 分钟)

### 3.1 Layer 5 验证练习
```bash
# 启动 pgcli
source scripts/bash_aliases.sh  # 加载别名
mt-db                            # 连接数据库

# 在 pgcli 中执行
SELECT COUNT(*) FROM cn_stock_top;
SELECT MAX(trade_date) FROM cn_stock_top;
\q  # 退出
```

**预期结果**: 看到记录数和最新日期

### 3.2 Layer 2 验证练习
```bash
# 获取 token
TOKEN=$(mt-token)

# 测试 API
http GET "$MYSTOCKS_URL/api/market/v3/dragon-tiger?limit=5" \
  Authorization:"Bearer $TOKEN"
```

**预期结果**: 看到 JSON 数据

### 3.3 Layer 4 验证练习
```bash
# 1. 打开浏览器访问前端
open http://localhost:5173  # macOS
# 或手动打开浏览器

# 2. 按 F12 打开开发者工具

# 3. 检查 Console 标签
#    - 应该没有红色错误

# 4. 检查 Network 标签
#    - 找到 API 请求
#    - 检查状态码 (应该是 200)
#    - 查看响应数据
```

**预期结果**: 页面正常显示，无控制台错误

### 3.4 Layer 3 验证练习
```bash
# 运行一个简单的集成测试
pytest tests/integration/test_user_login_flow.py::TestUserLoginFlowExample::test_login_page_loads -v -s
```

**预期结果**: 测试通过，生成截图

**检查点**: ✅ 成功完成所有层级的手动验证

---

## ✅ 第四步：查看示例 (10 分钟)

### 4.1 查看真实示例
```bash
# 1. API 修复示例
cat docs/development-process/examples/api-fix-example.md

# 2. UI 修复示例
cat docs/development-process/examples/ui-fix-example.md

# 3. 数据集成示例
cat docs/development-process/examples/data-integration-example.md
```

### 4.2 运行示例测试
```bash
# 运行登录流程示例
pytest specs/006-web-90-1/contracts/playwright-test-examples/example_login_flow.py -v -s

# 查看生成的截图
ls docs/verification-screenshots/example_*.png
```

**检查点**: ✅ 理解实际开发中如何应用 5 层验证

---

## ✅ 完成标志

恭喜！如果你完成了以上所有步骤，你已经掌握了：

- ✅ 5 层验证模型的概念和顺序
- ✅ 每一层使用的工具和方法
- ✅ 如何手动验证每一层
- ✅ 如何运行自动化测试
- ✅ 真实场景的应用示例

---

## 下一步学习

### 初级（已完成上面的清单）
- [ ] 修改一个简单的 bug，应用 5 层验证
- [ ] 编写一个简单的集成测试
- [ ] 使用 validate_all_layers() 进行自动验证

### 中级（1-2 周后）
- [ ] 添加一个新的 API 端点并验证
- [ ] 添加一个新的 UI 功能并验证
- [ ] 处理一个 Layer 失败的情况

### 高级（1 个月后）
- [ ] 设计一个完整的新功能并实现
- [ ] 编写复杂的集成测试场景
- [ ] 优化测试性能和覆盖率

---

## 常见问题

### Q: 每次都要手动验证 5 层吗？
A: 不需要。简单修改可以只验证相关层。但新功能建议完整验证。

### Q: 验证失败了怎么办？
A: 查看 `troubleshooting.md` 故障排查指南。

### Q: 可以跳过某些层吗？
A: 不建议。跳过可能导致问题未被发现。

### Q: 自动化测试可以替代手动验证吗？
A: 不完全能。首次开发建议手动验证，后续用自动化回归测试。

---

## 获取帮助

- 📖 查看文档: `docs/development-process/README.md`
- 🔧 故障排查: `docs/development-process/troubleshooting.md`
- 💡 查看示例: `docs/development-process/examples/`
- 🧪 运行测试: `pytest tests/integration/ -v`

**记住**: 90% 的问题都能通过 5 层验证快速定位！
