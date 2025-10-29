# 功能完成检查清单 (Definition of Done Checklist)

**版本**: 1.0
**日期**: 2025-10-29
**适用范围**: 所有功能开发、Bug 修复、功能增强

---

## 📋 功能信息 (Feature Information)

| 项目 | 内容 |
|------|------|
| **功能名称** | _______________________________ |
| **任务编号** | _______________________________ |
| **分支名称** | _______________________________ |
| **验证人** | _______________________________ |
| **验证日期** | _______________________________ |
| **预计时间** | [ ] 简单 (35-55 min) &nbsp; [ ] 中等 (50-80 min) &nbsp; [ ] 复杂 (90-120 min) |

---

## ✅ Layer 1: 代码层验证 (Code Layer) - 预计 5-10 分钟

### 代码提交 (Code Commit)
- [ ] 代码已提交到 feature 分支
- [ ] Commit 消息清晰描述改动内容
- [ ] 无调试代码残留 (console.log, print 语句等)

### 单元测试 (Unit Tests)
- [ ] 单元测试通过
  ```bash
  pytest tests/unit/ -v
  ```
- [ ] 测试通过数 / 总测试数: ______ / ______
- [ ] 如有失败测试，已修复或记录原因: _______

### 代码质量 (Code Quality)
- [ ] 代码格式检查通过
  ```bash
  black . && flake8 .
  ```
- [ ] 类型检查通过 (如适用)
  ```bash
  mypy .
  ```

**Layer 1 完成时间**: ______ 分钟

---

## ✅ Layer 2: API 层验证 (API Layer) - 预计 10-15 分钟

### 准备工作 (Preparation)
- [ ] 后端服务已启动: `http://localhost:8000`
- [ ] 已获取访问 Token
  ```bash
  TOKEN=$(http POST http://localhost:8000/api/auth/login \
    username=admin password=admin123 | jq -r '.access_token')
  ```

### API 端点验证 (API Endpoint Verification)

**端点 1**: ______________________________

- [ ] HTTP 方法: [ ] GET [ ] POST [ ] PUT [ ] DELETE
- [ ] 端点 URL: _______________________________
- [ ] 验证命令:
  ```bash
  http GET http://localhost:8000/api/______ \
    Authorization:"Bearer $TOKEN"
  ```
- [ ] 期望状态码: ______ (实际状态码: ______)
- [ ] 响应包含必需字段: _______________________________
- [ ] 数据结构验证: `jq -e '.data != null'` [ ] 通过 [ ] 失败

**端点 2** (如有多个端点，复制此部分): ______________________________

- [ ] HTTP 方法: [ ] GET [ ] POST [ ] PUT [ ] DELETE
- [ ] 端点 URL: _______________________________
- [ ] 验证命令: _______________________________
- [ ] 期望状态码: ______ (实际状态码: ______)
- [ ] 响应包含必需字段: _______________________________
- [ ] 数据结构验证: [ ] 通过 [ ] 失败

### 错误场景验证 (Error Scenarios)

- [ ] 无效 Token 返回 401
  ```bash
  http GET http://localhost:8000/api/______ \
    Authorization:"Bearer invalid_token" | jq -e '.status_code == 401'
  ```
- [ ] 缺失参数返回 422 (如适用)
- [ ] 其他错误场景: _______________________________

**Layer 2 完成时间**: ______ 分钟

---

## ✅ Layer 3: 集成层验证 (Integration Layer) - 预计 5-10 分钟 (自动执行)

### Playwright 集成测试 (Integration Tests)
- [ ] 集成测试通过
  ```bash
  pytest tests/integration/test_*.py -v
  ```
- [ ] 测试通过数 / 总测试数: ______ / ______
- [ ] 测试报告位置: _______________________________

### 数据流验证 (Data Flow Verification)
- [ ] 数据库层检查通过: 数据存在
- [ ] 后端 API 层检查通过: API 返回数据
- [ ] 前端请求层检查通过: 前端调用 API
- [ ] UI 渲染层检查通过: 用户看到数据

### 失败分析 (Failure Analysis - 如有失败)
如果测试失败，记录失败的层:
- [ ] 数据库层失败: _______________________________
- [ ] API 层失败: _______________________________
- [ ] 前端层失败: _______________________________
- [ ] UI 层失败: _______________________________

**Layer 3 完成时间**: ______ 分钟

---

## ✅ Layer 4: 用��界面层验证 (UI Layer) - 预计 10-20 分钟

### 浏览器访问 (Browser Access)
- [ ] 浏览器: [ ] Chrome [ ] Firefox [ ] Safari
- [ ] 功能页面 URL: http://localhost:8000/_______________________________
- [ ] 页面正常加载 (无白屏、无 404)

### 数据显示验证 (Data Display)
- [ ] 数据正确显示在页面上
- [ ] 数据内容符合预期: _______________________________
- [ ] 数据格式正确 (日期、数字、文本等)
- [ ] 截图保存位置:
  ```
  docs/verification-screenshots/feature-name-YYYYMMDD-ui.png
  ```

### Console 错误检查 (Console Errors)
- [ ] 打开 DevTools (F12 → Console)
- [ ] 无红色错误 (Errors)
- [ ] 如有 Warning，已确认不影响功能: _______________________________
- [ ] 截图保存位置:
  ```
  docs/verification-screenshots/feature-name-YYYYMMDD-console.png
  ```

### Network 请求检查 (Network Requests)
- [ ] 打开 DevTools (F12 → Network)
- [ ] 所有 API 请求状态为 200/201/204
- [ ] 无 failed 请求 (红色)
- [ ] API 请求列表:
  - `______________________` 状态: ______
  - `______________________` 状态: ______
  - `______________________` 状态: ______
- [ ] 截图保存位置:
  ```
  docs/verification-screenshots/feature-name-YYYYMMDD-network.png
  ```

### 交互功能验证 (Interaction Testing)
- [ ] 按钮点击响应正常
- [ ] 表单提交成功 (如适用)
- [ ] 数据刷新功能正常 (如适用)
- [ ] 页面跳转正常 (如适用)
- [ ] 其他交互: _______________________________

**Layer 4 完成时间**: ______ 分钟

---

## ✅ Layer 5: 数据验证层 (Data Validation Layer) - 预计 5-10 分钟

### 数据库连接 (Database Connection)
- [ ] 数据库类型: [ ] PostgreSQL [ ] TDengine
- [ ] 连接命令:
  ```bash
  # PostgreSQL
  pgcli -h localhost -U mystocks_user -d mystocks

  # TDengine
  taos -h localhost -u root -p taosdata
  ```

### 数据存在性检查 (Data Existence)
- [ ] 表名: _______________________________
- [ ] SQL 查询:
  ```sql
  SELECT COUNT(*) as record_count FROM table_name;
  ```
- [ ] 记录数: ______ (期望: > 0)
- [ ] 数据存在: [ ] 是 [ ] 否

### 数据时效性检查 (Data Freshness)
- [ ] SQL 查询:
  ```sql
  SELECT MAX(trade_date) as latest_date FROM table_name;
  ```
- [ ] 最新数据时间: _______________________________
- [ ] 是否满足时效要求: [ ] 是 (不超过 ____ 小时) [ ] 否

### 数据完整性检查 (Data Integrity)
- [ ] SQL 查询:
  ```sql
  SELECT COUNT(*) as null_count FROM table_name
  WHERE key_field1 IS NULL OR key_field2 IS NULL;
  ```
- [ ] NULL 记录数: ______ (期望: 0)
- [ ] 关键字段无 NULL: [ ] 是 [ ] 否

### 数据样本查看 (Data Sample)
- [ ] SQL 查询:
  ```sql
  SELECT * FROM table_name ORDER BY created_at DESC LIMIT 10;
  ```
- [ ] 数据样本合理: [ ] 是 [ ] 否
- [ ] 如发现异常数据，记录: _______________________________

**Layer 5 完成时间**: ______ 分钟

---

## 📊 验证总结 (Verification Summary)

### 完成状态 (Completion Status)
- [ ] **所有 5 层检查项通过，功能标记为"完成" (Done)**
- [ ] 部分检查项未通过，功能标记为"部分完成" (Partially Done)，需要记录未通过项

### 时间统计 (Time Statistics)
| Layer | 预计时间 | 实际时间 | 差异 |
|-------|---------|---------|------|
| Layer 1: 代码层 | 5-10 min | ______ min | ______ |
| Layer 2: API 层 | 10-15 min | ______ min | ______ |
| Layer 3: 集成层 | 5-10 min | ______ min | ______ |
| Layer 4: UI 层 | 10-20 min | ______ min | ______ |
| Layer 5: 数据层 | 5-10 min | ______ min | ______ |
| **总计** | **35-65 min** | **______ min** | **______** |

### 问题记录 (Issues)
如有任何问题、异常情况、需要改进的地方，请记录:

```
问题 1: _______________________________
解决方案: _______________________________

问题 2: _______________________________
解决方案: _______________________________
```

### 性能观察 (Performance Observations)
- [ ] API 响应时间 <1 秒
- [ ] 页面加载时间 <3 秒
- [ ] 数据库查询时间 <500ms
- [ ] 如有性能问题，记录: _______________________________

---

## 📝 备注 (Notes)

### 特殊说明 (Special Notes)
(记录任何特殊情况、依赖关系、后续需要跟进的事项)

```
_______________________________
_______________________________
_______________________________
```

### 验证截图清单 (Screenshot Checklist)
确保以下截图已保存:
- [ ] `docs/verification-screenshots/feature-name-YYYYMMDD-ui.png`
- [ ] `docs/verification-screenshots/feature-name-YYYYMMDD-console.png`
- [ ] `docs/verification-screenshots/feature-name-YYYYMMDD-network.png`

---

## ✍️ 签名确认 (Sign-off)

**验证人签名**: _______________________
**验证日期**: _______________________
**审核人签名**: _______________________ (可选)

---

## 📚 相关文档 (Related Documentation)

- [流程框架文档](../process-framework.md)
- [手动验证指南](manual-verification-checklist.md)
- [冒烟测试清单](smoke-test-checklist.md)
- [快速上手指南](../quickstart.md)

---

**版本历史**:
- v1.0 (2025-10-29): 初始版本，定义完整的 5 层验证检查清单
