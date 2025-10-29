# 手动验证指南 (Manual Verification Guide)

**版本**: 1.0
**日期**: 2025-10-29
**适用范围**: Layer 4 (UI Layer) 和 Layer 5 (Data Validation Layer)

---

## 📖 概述 (Overview)

本指南提供**手动验证**的详细步骤和最佳实践，专注于：
- **Layer 4**: 用户界面层验证 (浏览器、DevTools)
- **Layer 5**: 数据验证层 (数据库 SQL 查询)

**为什么需要手动验证？**
- 自动化测试无法覆盖所有用户体验细节
- 数据的正确性和合理性需要人工判断
- UI 的视觉效果和交互流畅度需要人工确认

---

## 🖥️ Layer 4: 用户界面层手动验证

### 前提条件

**后端服务必须运行**:
```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 如未运行，启动后端
cd /opt/claude/mystocks_spec/web/backend
python -m uvicorn app.main:app --reload
```

**前端服务必须运行** (如果是前后端分离架构):
```bash
# 检查前端是否运行
curl http://localhost:8080

# 如未运行，启动前端
cd /opt/claude/mystocks_spec/web/frontend
npm run dev
```

---

### 步骤 1: 访问功能页面

**打开浏览器** (推荐 Chrome):
```
http://localhost:8000/<feature-path>
```

**示例**:
- 仪表板: `http://localhost:8000/dashboard`
- 龙虎榜: `http://localhost:8000/market/dragon-tiger`
- ETF 数据: `http://localhost:8000/market/etf-data`

**检查项**:
- [ ] 页面正常加载 (无白屏)
- [ ] 无 404 错误
- [ ] 页面布局正常

---

### 步骤 2: 检查 Console (控制台)

**打开 DevTools Console**:
```
方法 1: 按 F12 → 切换到 Console 标签
方法 2: 按 Ctrl+Shift+J (Windows/Linux) 或 Cmd+Option+J (macOS)
方法 3: 右键 → 检查 → Console
```

**检查内容**:

1. **红色错误 (Errors)**:
   - [ ] **无红色错误**
   - ❌ 如有错误，必须修复 (不允许有任何 Error)

2. **黄色警告 (Warnings)**:
   - [ ] 无警告，或警告不影响功能
   - ⚠️ 如有警告，确认是否影响功能

3. **常见错误类型**:
   ```javascript
   // ❌ 必须修复的错误
   Uncaught TypeError: Cannot read property 'data' of undefined
   Failed to load resource: the server responded with a status of 500
   Uncaught ReferenceError: xxx is not defined

   // ⚠️ 可接受的警告 (视情况而定)
   [Vue warn]: Component <MyComponent> is missing template or render function
   Warning: Received NaN for the `width` attribute
   ```

**截图要求**:
- 文件名: `feature-name-YYYYMMDD-console.png`
- 保存位置: `docs/verification-screenshots/`
- **必须显示**: 整个 Console 窗口，清晰可见无错误

**截图方法**:
```
1. 按 Ctrl+Shift+P (Windows/Linux) 或 Cmd+Shift+P (macOS)
2. 输入 "Capture screenshot"
3. 选择 "Capture area screenshot"
4. 框选 Console 窗口
5. 保存截图
```

---

### 步骤 3: 检查 Network (网络请求)

**打开 DevTools Network**:
```
方法 1: 按 F12 → 切换到 Network 标签
方法 2: 按 Ctrl+Shift+E (Windows/Linux)
方法 3: 右键 → 检查 → Network
```

**检查内容**:

1. **清空并刷新**:
   - 点击 Network 标签左上角的 "清除" 图标 (🚫)
   - 刷新页面 (F5 或 Ctrl+R)

2. **检查 API 请求**:
   - [ ] **所有 API 请求状态码为 200/201/204**
   - [ ] **无红色失败请求** (Status 4xx/5xx)
   - [ ] API 响应时间合理 (<1 秒)

3. **常见问题**:
   ```
   ❌ 必须修复:
   - Status 404: API 路径错误
   - Status 401: 未授权 (Token 失效或缺失)
   - Status 500: 后端错误
   - Status 0: CORS 错误或后端未启动

   ⚠️ 需要优化:
   - 响应时间 >3 秒: 性能问题
   - 多次重复请求: 可能存在死循环
   ```

4. **查看响应数据**:
   - 点击具体的 API 请求 (如 `/api/data/dashboard/summary`)
   - 切换到 "Preview" 或 "Response" 标签
   - [ ] 响应数据结构正确
   - [ ] 响应数据不为空
   - [ ] 响应数据内容合理

**截图要求**:
- 文件名: `feature-name-YYYYMMDD-network.png`
- 保存位置: `docs/verification-screenshots/`
- **必须显示**:
  - 所有 API 请求列表
  - 状态码清晰可见
  - 至少展开一个请求的响应数据

---

### 步骤 4: 检查数据显示

**验证数据正确性**:

1. **数据存在性**:
   - [ ] 页面显示数据 (非空白或占位符)
   - [ ] 数据表格有行 (非"暂无数据")
   - [ ] 图表有数据点 (非空图表)

2. **数据格式正确性**:
   - [ ] **日期格式**: 2025-10-29 或 2025/10/29 (非时间戳)
   - [ ] **数字格式**: 1,234.56 或 1234.56 (非科学计数法)
   - [ ] **百分比**: 12.5% (非 0.125)
   - [ ] **货币**: ¥1,234.56 或 1234.56 元

3. **数据合理性**:
   - [ ] 股票代码: 6 位数字 (如 000001, 600519)
   - [ ] 股票名称: 中文名称 (如 平安银行, 贵州茅台)
   - [ ] 价格范围: >0 且 <10000 (一般情况)
   - [ ] 涨跌幅: -10% 到 +10% (一般情况，ST 股票除外)

**截图要求**:
- 文件名: `feature-name-YYYYMMDD-ui.png`
- 保存位置: `docs/verification-screenshots/`
- **必须显示**:
  - 完整页面 (包含导航栏、数据区域)
  - 数据清晰可见 (不要过小)
  - 至少显示 5-10 条数据 (如果适用)

**截图方法**:
```
方法 1: 全页面截图
1. 按 Ctrl+Shift+P (Windows/Linux) 或 Cmd+Shift+P (macOS)
2. 输入 "Capture full size screenshot"
3. 自动保存

方法 2: 可见区域截图
1. 按 Ctrl+Shift+P
2. 输入 "Capture screenshot"
3. 自动保存
```

---

### 步骤 5: 测试交互功能

**常见交互类型**:

1. **按钮点击**:
   - [ ] 刷新按钮: 重新加载数据
   - [ ] 导出按钮: 下载文件成功
   - [ ] 搜索按钮: 返回搜索结果
   - [ ] 清除按钮: 清空表单

2. **表单提交**:
   - [ ] 输入验证: 必填项提示
   - [ ] 提交成功: 显示成功消息
   - [ ] 提交失败: 显示错误消息
   - [ ] 表单重置: 清空所有输入

3. **数据刷新**:
   - [ ] 下拉刷新: 重新加载数据
   - [ ] 自动刷新: 定时更新数据 (如适用)
   - [ ] 手动刷新: 点击刷新按钮

4. **页面跳转**:
   - [ ] 链接点击: 跳转到目标页面
   - [ ] 返回按钮: 回到上一页
   - [ ] 面包屑: 导航正常

**测试清单**:
```
对于每个交互功能:
1. 执行操作
2. 观察响应 (视觉反馈、数据更新)
3. 检查 Console 无错误
4. 检查 Network 请求正常
5. 确认结果符合预期
```

---

## 🗄️ Layer 5: 数据验证层手动验证

### PostgreSQL 数据验证

**连接数据库**:
```bash
# 方法 1: 使用快捷命令
mt-db

# 方法 2: 使用完整命令
PGPASSWORD=mystocks2025 pgcli -h localhost -U mystocks_user -d mystocks
```

**验证清单**:

#### 1. 数据存在性检查

**查询数据量**:
```sql
-- 检查表是否有数据
SELECT COUNT(*) as record_count FROM table_name;

-- 期望结果: record_count > 0
```

**示例**:
```sql
-- 检查龙虎榜数据
SELECT COUNT(*) FROM cn_stock_top;
-- 期望: > 0

-- 检查 ETF 数据
SELECT COUNT(*) FROM cn_etf_spot;
-- 期望: > 0

-- 检查资金流向数据
SELECT COUNT(*) FROM cn_stock_fund_flow_industry;
-- 期望: > 0
```

**验证标准**:
- [ ] 记录数 > 0 (表有数据)
- [ ] 如果 = 0，需要运行数据采集脚本

---

#### 2. 数据时效性检查

**查询最新数据时间**:
```sql
-- 检查最新交易日期
SELECT MAX(trade_date) as latest_date FROM table_name;

-- 期望结果: latest_date = 今天或最近交易日
```

**示例**:
```sql
-- 检查龙虎榜最新数据
SELECT MAX(trade_date) as latest_date FROM cn_stock_top;
-- 期望: 2025-10-29 或最近交易日

-- 检查数据分布 (最近 5 个交易日)
SELECT trade_date, COUNT(*) as count
FROM cn_stock_top
GROUP BY trade_date
ORDER BY trade_date DESC
LIMIT 5;
```

**验证标准**:
- [ ] 最新数据时间不超过 1 个工作日 (日线数据)
- [ ] 最新数据时间不超过 1 小时 (高频数据)
- [ ] 如果数据过期，需要运行数据更新脚本

---

#### 3. 数据完整性检查

**检查关键字段无 NULL**:
```sql
-- 检查关键字段 NULL 值数量
SELECT COUNT(*) as null_count
FROM table_name
WHERE key_field1 IS NULL OR key_field2 IS NULL;

-- 期望结果: null_count = 0
```

**示例**:
```sql
-- 检查龙虎榜数据完整性
SELECT COUNT(*) as null_count
FROM cn_stock_top
WHERE stock_code IS NULL OR stock_name IS NULL;
-- 期望: 0

-- 检查关键字段统计
SELECT
  COUNT(*) as total_records,
  COUNT(stock_code) as has_code,
  COUNT(stock_name) as has_name,
  COUNT(trade_date) as has_date
FROM cn_stock_top;
-- 期望: total_records = has_code = has_name = has_date
```

**验证标准**:
- [ ] 关键字段无 NULL 值
- [ ] 如有 NULL 值，检查数据采集逻辑

---

#### 4. 数据合理性检查

**查看数据样本**:
```sql
-- 查看最新 10 条记录
SELECT * FROM table_name
ORDER BY created_at DESC
LIMIT 10;
```

**示例**:
```sql
-- 查看龙虎榜样本
SELECT stock_code, stock_name, trade_date, close_price, change_percent
FROM cn_stock_top
ORDER BY trade_date DESC, change_percent DESC
LIMIT 10;

-- 检查数据范围
SELECT
  MIN(close_price) as min_price,
  MAX(close_price) as max_price,
  AVG(close_price) as avg_price,
  MIN(change_percent) as min_change,
  MAX(change_percent) as max_change
FROM cn_stock_top
WHERE trade_date = (SELECT MAX(trade_date) FROM cn_stock_top);
```

**验证标准**:
- [ ] 股票代码: 6 位数字 (000001-999999)
- [ ] 股票名称: 非空字符串
- [ ] 价格: > 0 且 < 10000 (一般情况)
- [ ] 涨跌幅: -10% 到 +10% (一般情况)
- [ ] 数据无明显异常 (如价格为 0, 涨跌幅为 1000% 等)

---

### TDengine 数据验证 (如适用)

**连接数据库**:
```bash
# 方法 1: 使用快捷命令
mt-td

# 方法 2: 使用完整命令
taos -h 192.168.123.104 -u root -ptaosdata
```

**验证清单**:

#### 1. 数据存在性检查
```sql
-- 切换到 market_data 数据库
USE market_data;

-- 检查 tick 数据量
SELECT COUNT(*) FROM tick_data;

-- 检查分钟数据量
SELECT COUNT(*) FROM minute_data;
```

#### 2. 数据时效性检查
```sql
-- 检查最新 tick 数据
SELECT LAST(*) FROM tick_data;

-- 检查最新分钟数据
SELECT LAST(*) FROM minute_data;
```

#### 3. 数据样本查看
```sql
-- 查看最近 10 条 tick 数据
SELECT * FROM tick_data ORDER BY ts DESC LIMIT 10;

-- 查看最近 10 条分钟数据
SELECT * FROM minute_data ORDER BY ts DESC LIMIT 10;
```

**退出数据库**:
```sql
-- PostgreSQL
\q

-- TDengine
quit;
```

---

## 📋 验证结果记录

### 验证记录模板

```markdown
## 功能验证记录

**功能名称**: _____________
**验证人**: _____________
**验证日期**: _____________

### Layer 4: UI 层验证

**页面 URL**: http://localhost:8000/_____________

**Console 检查**:
- [ ] 无红色错误
- [ ] 截图保存: `_______________-console.png`

**Network 检查**:
- [ ] 所有 API 请求状态 200
- [ ] API 请求列表:
  - `_______________` - 状态: ___
  - `_______________` - 状态: ___
- [ ] 截图保存: `_______________-network.png`

**数据显示**:
- [ ] 数据正确显示
- [ ] 数据格式正确
- [ ] 数据合理性检查通过
- [ ] 截图保存: `_______________-ui.png`

**交互功能**:
- [ ] 按钮响应正常
- [ ] 表单提交正常 (如适用)
- [ ] 页面跳转正常 (如适用)

### Layer 5: 数据层验证

**数据库**: [ ] PostgreSQL [ ] TDengine

**表名**: _____________

**数据存在性**:
```sql
SELECT COUNT(*) FROM table_name;
-- 结果: _____ (期望 > 0)
```

**数据时效性**:
```sql
SELECT MAX(trade_date) FROM table_name;
-- 结果: _____ (期望: 最近交易日)
```

**数据完整性**:
```sql
SELECT COUNT(*) FROM table_name WHERE key_field IS NULL;
-- 结果: _____ (期望: 0)
```

**数据合理性**:
- [ ] 数据样本检查通过
- [ ] 无异常数据

### 验证结论

- [ ] **所有检查项通过，功能验证完成**
- [ ] 部分检查项未通过，问题记录: _____________

**签名**: _____________
```

---

## ⚠️ 常见问题和解决方案

### 问题 1: 页面白屏

**可能原因**:
1. 前端服务未启动
2. 路由配置错误
3. 前端编译错误

**排查步骤**:
```bash
# 1. 检查前端服务
curl http://localhost:8080

# 2. 查看前端日志
cd web/frontend
npm run dev

# 3. 检查 Console 错误信息
# 按 F12 查看 Console
```

---

### 问题 2: API 请求失败 (Status 0)

**可能原因**:
1. 后端服务未启动
2. CORS 配置错误

**排查步骤**:
```bash
# 1. 检查后端服务
curl http://localhost:8000/health

# 2. 启动后端
cd web/backend
python -m uvicorn app.main:app --reload

# 3. 检查 CORS 配置
# 查看 web/backend/app/main.py 中的 CORS 中间件配置
```

---

### 问题 3: 数据库连接失败

**可能原因**:
1. 数据库服务未启动
2. 连接参数错误
3. 防火墙阻止连接

**排查步骤**:
```bash
# PostgreSQL
# 1. 检查服务
sudo systemctl status postgresql

# 2. 测试连接
PGPASSWORD=mystocks2025 psql -h localhost -U mystocks_user -d mystocks -c "SELECT 1;"

# TDengine
# 1. 检查服务
systemctl status taosd

# 2. 测试连接
taos -h 192.168.123.104 -u root -ptaosdata -s "SELECT SERVER_VERSION();"
```

---

### 问题 4: 数据为空

**可能原因**:
1. 数据采集脚本未运行
2. 数据采集失败
3. 数据库表未创建

**排查步骤**:
```bash
# 1. 检查表是否存在
mt-db
\dt  # 列出所有表

# 2. 检查数据量
SELECT COUNT(*) FROM table_name;

# 3. 运行数据采集脚本
cd /opt/claude/mystocks_spec
python scripts/collect_data.py

# 4. 重新检查数据
SELECT COUNT(*) FROM table_name;
```

---

## 📚 相关文档

- **[Definition of Done](definition-of-done.md)**: 完整的 5 层验证模型
- **[完成检查清单](../../specs/006-web-90-1/contracts/definition-of-done-checklist.md)**: 详细的逐项检查清单
- **[快速上手指南](../../specs/006-web-90-1/quickstart.md)**: 30 分钟快速入门

---

**版本历史**:
- v1.0 (2025-10-29): 初始版本，提供 Layer 4/5 手动验证详细步骤

---

## 时间估算参考

根据工作类型，各层验证的预期时间：

### 简单 Bug 修复（5-10 分钟总计）
- Layer 5 (数据库): 1 分钟
- Layer 2 (API): 1 分钟
- Layer 4 (UI): 2 分钟
- Layer 3 (集成): 1 分钟（可选）

### 中等功能开发（20-30 分钟总计）
- Layer 5 (数据库): 3 分钟
- Layer 2 (API): 5 分钟
- Layer 4 (UI): 7 分钟
- Layer 3 (集成): 10 分钟
- 截图和文档: 5 分钟

### 复杂功能/重构（40-60 分钟总计）
- Layer 5 (数据库): 5 分钟
- Layer 2 (API): 10 分钟
- Layer 4 (UI): 15 分钟
- Layer 3 (集成): 20 分钟
- 全面测试: 10 分钟

**原则**: 验证时间不应超过开发时间的 30%

**示例**:
- 2 小时的功能 → 最多 36 分钟验证
- 1 天的功能 → 最多 2.4 小时验证
- 1 周的功能 → 最多 1.5 天验证

**如果验证时间过长**: 考虑是否过度验证或功能过于复杂。
