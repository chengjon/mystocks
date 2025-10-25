# Grafana配置检查清单

**使用说明**: 按顺序完成每个步骤，在完成后打勾 ✓

---

## ✅ 准备工作（已完成）

- [x] 监控数据库 `mystocks_monitoring` 已创建
- [x] 数据库表结构已初始化（6张表 + 2个视图）
- [x] 配置文件密码已修正为 `c790414J`
- [x] PostgreSQL版本设置为 `15`（兼容17.6）
- [x] 字符编码设置为 `C.UTF-8`（支持中文）
- [x] Grafana容器部署到NAS并运行正常

---

## 🎯 手动配置步骤（待完成）

### 步骤1: 访问Grafana ⏱️ 1分钟

- [ ] 打开浏览器
- [ ] 访问: http://192.168.123.104:3000
- [ ] 输入用户名: `admin`
- [ ] 输入密码: `mystocks2025`
- [ ] 成功登录到Grafana首页

**如果无法访问**:
```bash
# 检查容器状态
ssh admin@192.168.123.104
docker ps | grep grafana
docker logs mystocks-grafana
```

---

### 步骤2: 配置PostgreSQL数据源 ⏱️ 5分钟

#### 2.1 导航到数据源配置页面

- [ ] 点击左侧菜单图标（☰）
- [ ] 选择: **Configuration** (齿轮图标)
- [ ] 点击: **Data Sources**
- [ ] 点击: **Add data source** 按钮

#### 2.2 选择数据源类型

- [ ] 在搜索框输入: `PostgreSQL`
- [ ] 点击: **PostgreSQL** 图标

#### 2.3 填写连接信息

**基本设置 (Settings)**:

- [ ] **Name**: 输入 `MyStocks-Monitoring`
- [ ] **Default**: ✓ 勾选（设为默认数据源）

**PostgreSQL连接 (PostgreSQL Connection)**:

- [ ] **Host**: 输入 `192.168.123.104:5438`
- [ ] **Database**: 输入 `mystocks_monitoring`
- [ ] **User**: 输入 `postgres`
- [ ] **Password**: 输入 `c790414J`
- [ ] **TLS/SSL Mode**: 选择 `disable`

**PostgreSQL详情 (PostgreSQL details)**:

- [ ] **Version**: 选择 `15`（不要选17+）
- [ ] **TimescaleDB**: ☐ 不勾选
- [ ] **Max open**: 保持默认（留空）
- [ ] **Max idle**: 保持默认（留空）
- [ ] **Max lifetime**: 保持默认（留空）

#### 2.4 保存并测试

- [ ] 滚动到页面底部
- [ ] 点击: **Save & test** 按钮
- [ ] 等待测试结果
- [ ] 确认看到: 绿色 ✓ "Database Connection OK"

**如果测试失败**:
```bash
# 手动测试数据库连接
export PGPASSWORD='c790414J'
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks_monitoring -c "SELECT 1;"
```

---

### 步骤3: 导入监控面板 ⏱️ 2分钟

#### 3.1 进入导入页面

- [ ] 点击左侧菜单图标（☰）
- [ ] 选择: **Create** (+ 图标)
- [ ] 点击: **Import**

#### 3.2 上传JSON文件

- [ ] 点击: **Upload JSON file** 按钮
- [ ] 选择文件: `monitoring/grafana_dashboard.json`
  - 完整路径: `/mnt/wd_mycode/mystocks_spec/monitoring/grafana_dashboard.json`
- [ ] 等待文件上传和解析

#### 3.3 配置面板选项

- [ ] **Name**: 保持默认 `MyStocks System Monitoring`
- [ ] **Folder**: 选择 `General`（或创建新文件夹）
- [ ] **Unique identifier (UID)**: 保持默认
- [ ] **Select a PostgreSQL data source**: 选择 `MyStocks-Monitoring`

#### 3.4 完成导入

- [ ] 点击: **Import** 按钮
- [ ] 等待导入完成
- [ ] 自动跳转到监控面板页面

---

### 步骤4: 生成测试数据 ⏱️ 2分钟

**面板导入后可能显示"No Data"，需要生成测试数据**

#### 4.1 运行测试脚本

在开发机器上执行:

```bash
cd /mnt/wd_mycode/mystocks_spec
python test_monitoring_with_redis.py
```

- [ ] 脚本运行完成
- [ ] 看到成功消息

#### 4.2 验证数据生成

```bash
export PGPASSWORD='c790414J'
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks_monitoring -c "
SELECT
  '操作日志' as table_name, COUNT(*) as records FROM operation_logs
UNION ALL
SELECT
  '性能指标', COUNT(*) FROM performance_metrics
UNION ALL
SELECT
  '质量检查', COUNT(*) FROM data_quality_checks
UNION ALL
SELECT
  '告警记录', COUNT(*) FROM alert_records;
"
```

- [ ] 所有表都有数据（records > 0）

---

### 步骤5: 验证面板显示 ⏱️ 3分钟

#### 5.1 刷新Grafana面板

- [ ] 返回Grafana浏览器标签页
- [ ] 点击右上角的刷新按钮（🔄）
- [ ] 或按快捷键: `Ctrl + R` (Windows) / `Cmd + R` (Mac)

#### 5.2 检查各个面板

**系统概览（顶部4个Stat面板）**:

- [ ] **今日操作总数**: 显示数字（不是"No Data"）
- [ ] **慢查询数量**: 显示数字
- [ ] **未解决告警**: 显示数字
- [ ] **平均查询时间**: 显示时间（ms）

**性能监控（中间3个面板）**:

- [ ] **查询时间趋势**: 显示折线图
- [ ] **数据库性能对比**: 显示柱状图（TDengine, PostgreSQL, MySQL）
- [ ] **慢查询Top 10**: 显示表格数据

**数据质量（2个面板）**:

- [ ] **质量检查状态分布**: 显示饼图（PASS/WARN/FAIL）
- [ ] **质量检查趋势**: 显示时序图

**告警监控（2个面板）**:

- [ ] **告警级别分布**: 显示Bar Gauge（CRITICAL/HIGH/MEDIUM/LOW）
- [ ] **未解决告警列表**: 显示表格

**操作统计（底部2个面板）**:

- [ ] **操作类型分布**: 显示饼图（QUERY/INSERT/UPDATE/DELETE）
- [ ] **操作成功率**: 显示表格（按数据库统计）

#### 5.3 检查时间范围

- [ ] 右上角时间选择器设置为: `Last 24 hours`
- [ ] 自动刷新间隔设置为: `30s` 或 `1m`

---

### 步骤6: 安全配置（可选） ⏱️ 5分钟

#### 6.1 修改管理员密码

- [ ] 点击左下角用户头像
- [ ] 选择: **Profile**
- [ ] 点击: **Change Password**
- [ ] 输入当前密码: `mystocks2025`
- [ ] 输入新密码（建议更复杂的密码）
- [ ] 确认新密码
- [ ] 点击: **Change Password** 按钮

#### 6.2 创建只读用户（可选）

- [ ] 左侧菜单: **Configuration** → **Users**
- [ ] 点击: **New user**
- [ ] 填写用户信息:
  - Name: `viewer`
  - Email: `viewer@mystocks.local`
  - Username: `viewer`
  - Password: 设置密码
- [ ] 角色设置为: `Viewer`
- [ ] 点击: **Create user**

---

## 🎉 完成验证

完成所有步骤后，您应该能看到：

- ✅ Grafana正常访问和登录
- ✅ PostgreSQL数据源连接成功（绿色勾）
- ✅ 监控面板成功导入（13个面板）
- ✅ 所有面板显示实时数据（不是No Data）
- ✅ 图表正常渲染（折线图、柱状图、饼图、表格）
- ✅ 数据刷新正常（时间范围可调整）

---

## 🐛 故障排查快速参考

### 问题1: 数据源连接失败

```bash
# 测试PostgreSQL连接
export PGPASSWORD='c790414J'
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks_monitoring -c "SELECT version();"
```

**常见原因**:
- ❌ 密码错误（应该是 `c790414J`）
- ❌ 数据库名称错误（应该是 `mystocks_monitoring`）
- ❌ 端口错误（应该是 `5438`）
- ❌ PostgreSQL服务未运行

### 问题2: 面板显示"No Data"

```bash
# 检查数据是否存在
export PGPASSWORD='c790414J'
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks_monitoring -c "
SELECT COUNT(*) FROM operation_logs;
"
```

**解决方案**:
```bash
# 生成测试数据
cd /mnt/wd_mycode/mystocks_spec
python test_monitoring_with_redis.py
```

### 问题3: Grafana无法访问

```bash
# 检查容器状态
ssh admin@192.168.123.104
docker ps | grep grafana

# 查看日志
docker logs mystocks-grafana --tail 50

# 重启容器
docker restart mystocks-grafana
```

### 问题4: JSON导入失败

**解决方案**:
- 确认JSON文件路径正确
- 确认文件未损坏（可以用文本编辑器打开查看）
- 如果上传失败，可以复制JSON内容直接粘贴到"Import via panel json"区域

---

## 📚 参考文档

- **FINAL_SETUP_SUMMARY.md** - 完整配置总结
- **CONFIGURATION_CORRECTIONS.md** - 配置修正说明
- **MANUAL_SETUP_GUIDE.md** - 详细手动配置指南
- **QUICK_REFERENCE.md** - 快速参考卡片

---

## ⏱️ 预计总时间

- 步骤1 (访问Grafana): 1分钟
- 步骤2 (配置数据源): 5分钟
- 步骤3 (导入面板): 2分钟
- 步骤4 (生成数据): 2分钟
- 步骤5 (验证显示): 3分钟
- 步骤6 (安全配置): 5分钟（可选）

**总计**: 约 **13-18分钟**

---

**状态**: ✅ 所有准备工作已完成，可以开始配置！

🎯 **开始第一步**: 打开浏览器访问 http://192.168.123.104:3000
