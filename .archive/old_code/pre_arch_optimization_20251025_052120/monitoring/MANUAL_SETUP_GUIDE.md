# Grafana手动配置指南

**创建人**: Claude
**版本**: 2.0.0
**批准日期**: 2025-09-01
**最后修订**: 2025-10-16
**本次修订内容**: 手动设置指南

---

**适用场景**: Docker容器已运行，但需要手动配置数据源和面板
**预计时间**: 10-15分钟

---

## 📋 前置条件检查

- [x] Grafana容器运行正常
- [x] 端口3000已开放
- [ ] 可以通过浏览器访问 http://192.168.123.104:3000
- [ ] 监控数据库PostgreSQL可访问 (192.168.123.104:5438)

---

## 🌐 步骤1: 首次访问和登录

### 1.1 打开浏览器

在浏览器中访问: **http://192.168.123.104:3000**

### 1.2 登录

- 用户名: `admin`
- 密码: `mystocks2025`

如果首次登录要求修改密码，可以:
- 修改为新密码 (推荐)
- 或点击"Skip"跳过

### 1.3 验证登录成功

登录后应该看到Grafana欢迎页面。

---

## 🔌 步骤2: 配置PostgreSQL数据源

### 2.1 进入数据源配置

1. 点击左侧菜单 **⚙️ Configuration** → **Data sources**
2. 点击 **Add data source** 按钮

### 2.2 选择PostgreSQL

在数据源列表中搜索并选择 **PostgreSQL**

### 2.3 配置连接参数

填入以下信息:

| 字段 | 值 |
|-----|---|
| **Name** | MyStocks-Monitoring |
| **Host** | 192.168.123.104:5438 |
| **Database** | mystocks_monitoring |
| **User** | postgres |
| **Password** | Cheng.20241017 |
| **SSL Mode** | disable |
| **Version** | 17+ |
| **TimescaleDB** | ☐ (不勾选) |

### 2.4 测试连接

1. 滚动到页面底部
2. 点击 **Save & test** 按钮
3. 应该看到绿色勾选 ✓ "Database Connection OK"

**如果连接失败**:
- 检查PostgreSQL是否运行
- 检查密码是否正确
- 测试命令: `psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks_monitoring`

---

## 📊 步骤3: 导入监控面板

### 方法A: 通过JSON文件导入 (推荐)

#### 3.1 准备JSON文件

确保有 `grafana_dashboard.json` 文件（已在项目中提供）

#### 3.2 导入面板

1. 点击左侧菜单 **+** (Create) → **Import**
2. 点击 **Upload JSON file** 按钮
3. 选择 `monitoring/grafana_dashboard.json` 文件
4. 或者将JSON内容复制粘贴到文本框中

#### 3.3 配置导入选项

- **Name**: MyStocks监控面板 (可自定义)
- **Folder**: 选择或创建 "MyStocks" 文件夹
- **Unique identifier (UID)**: 保持默认或自定义
- **Select a Prometheus datasource**: 选择 **MyStocks-Monitoring**

#### 3.4 完成导入

点击 **Import** 按钮完成导入

### 方法B: 手动创建面板

如果JSON导入失败，可以手动创建关键面板:

#### 3.2.1 创建新Dashboard

1. 点击 **+** (Create) → **Dashboard**
2. 点击 **Add new panel**

#### 3.2.2 创建"今日操作总数"面板

**配置Query**:
```sql
SELECT COUNT(*) as total_operations
FROM operation_logs
WHERE created_at >= NOW() - INTERVAL '24 hours';
```

**设置可视化**:
- Visualization: **Stat**
- Title: 今日操作总数

**保存面板**: 点击右上角 **Apply**

#### 3.2.3 创建"查询时间趋势"面板

**配置Query**:
```sql
SELECT
  DATE_TRUNC('minute', created_at) +
    INTERVAL '5 minute' * FLOOR(EXTRACT(EPOCH FROM created_at - DATE_TRUNC('minute', created_at))/300) AS time,
  AVG(metric_value) as "平均",
  MAX(metric_value) as "最大",
  MIN(metric_value) as "最小"
FROM performance_metrics
WHERE metric_type = 'QUERY_TIME'
  AND created_at >= $__timeFrom()
GROUP BY time
ORDER BY time;
```

**设置可视化**:
- Visualization: **Time series**
- Title: 查询时间趋势

**保存Dashboard**: 点击右上角保存图标

---

## 📈 步骤4: 生成监控数据

为了让面板有数据显示，需要运行测试程序生成监控数据。

### 4.1 在开发机上运行

```bash
cd /mnt/wd_mycode/mystocks_spec

# 运行测试生成监控数据
python test_monitoring_with_redis.py
```

### 4.2 验证数据

在Grafana中:
1. 打开刚导入的监控面板
2. 刷新页面 (右上角刷新按钮)
3. 检查各个面板是否显示数据

---

## 🔍 步骤5: 验证各个面板

### 5.1 系统概览 (第一行)

检查以下4个Stat面板是否显示数字:
- [ ] 今日操作总数
- [ ] 慢查询数量
- [ ] 未解决告警
- [ ] 平均查询时间

### 5.2 性能监控

检查以下面板:
- [ ] 查询时间趋势 (时序图)
- [ ] 数据库性能对比 (柱状图)
- [ ] 慢查询Top 10 (表格)

### 5.3 数据质量

检查以下面板:
- [ ] 质量检查状态分布 (饼图)
- [ ] 质量检查趋势 (时序图)

### 5.4 告警监控

检查以下面板:
- [ ] 告警级别分布
- [ ] 未解决告警列表

### 5.5 操作统计

检查以下面板:
- [ ] 操作类型分布 (饼图)
- [ ] 操作成功率 (表格)

---

## ⚙️ 步骤6: 配置自动刷新

1. 点击面板右上角的 **🕐** (时间选择器)
2. 设置时间范围: **Last 24 hours**
3. 设置自动刷新: **30s** (30秒刷新一次)
4. 点击 **Apply time range**

---

## 🔐 步骤7: 安全配置 (可选但推荐)

### 7.1 修改管理员密码

1. 点击左下角头像
2. 选择 **Preferences**
3. 点击 **Change Password**
4. 输入当前密码和新密码
5. 点击 **Change Password**

### 7.2 创建只读用户

1. 进入 **⚙️ Configuration** → **Users**
2. 点击 **New user**
3. 填写信息:
   - Name: Viewer
   - Email: viewer@example.com
   - Username: viewer
   - Password: viewer123
4. 设置 Role 为 **Viewer**
5. 点击 **Create user**

---

## 🎨 步骤8: 自定义面板 (可选)

### 8.1 调整面板布局

1. 点击面板右上角的 **设置图标**
2. 拖拽面板边缘调整大小
3. 拖拽面板标题移动位置
4. 点击右上角 **保存** 图标

### 8.2 添加变量 (Variables)

1. 点击面板右上角 **⚙️** (Dashboard settings)
2. 进入 **Variables** 标签
3. 点击 **Add variable**
4. 配置变量 (例如: 数据库类型, 时间范围等)
5. 保存设置

### 8.3 配置告警规则

1. 编辑任意面板
2. 切换到 **Alert** 标签
3. 点击 **Create Alert Rule from this panel**
4. 配置告警条件:
   - 例如: 慢查询数量 > 10
   - 告警级别: Warning
5. 配置通知渠道
6. 保存告警规则

---

## 📱 步骤9: 移动端访问 (可选)

### 9.1 浏览器访问

直接在手机浏览器访问: http://192.168.123.104:3000

### 9.2 官方App访问

1. 下载Grafana官方App:
   - iOS: App Store 搜索 "Grafana"
   - Android: Google Play 搜索 "Grafana"

2. 配置连接:
   - Server URL: http://192.168.123.104:3000
   - Username: admin
   - Password: mystocks2025 (或您修改后的密码)

3. 登录后可查看所有面板

---

## 🐛 常见问题排查

### Q1: 面板显示"No Data"

**原因**: 监控数据库中没有数据

**解决**:
```bash
# 1. 检查监控数据库是否有数据
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks_monitoring -c "
SELECT COUNT(*) as operation_count FROM operation_logs;
SELECT COUNT(*) as metric_count FROM performance_metrics;
"

# 2. 生成测试数据
cd /mnt/wd_mycode/mystocks_spec
python test_monitoring_with_redis.py

# 3. 刷新Grafana面板
```

### Q2: 数据源连接失败

**原因**: PostgreSQL连接配置错误

**解决**:
```bash
# 1. 测试PostgreSQL连接
psql -h 192.168.123.104 -p 5438 -U postgres -d mystocks_monitoring

# 2. 检查密码是否正确
# 3. 检查防火墙是否阻止端口5438
# 4. 在Grafana中重新配置数据源
```

### Q3: 查询超时

**原因**: 数据量大或查询复杂

**解决**:
1. 编辑面板Query
2. 添加LIMIT限制返回行数
3. 减小时间范围
4. 添加WHERE条件过滤

### Q4: 无法保存Dashboard

**原因**: 权限不足或浏览器缓存问题

**解决**:
1. 确认以admin用户登录
2. 清除浏览器缓存
3. 尝试另一个浏览器

---

## ✅ 配置完成检查清单

完成后请检查:

- [ ] 可以访问 http://192.168.123.104:3000
- [ ] 可以用admin/mystocks2025登录
- [ ] 数据源"MyStocks-Monitoring"连接正常 (绿色勾选)
- [ ] 监控面板已导入
- [ ] 至少有1个面板显示数据 (非"No Data")
- [ ] 自动刷新已配置 (30秒)
- [ ] 时间范围已设置 (Last 24 hours)
- [ ] 已修改默认管理员密码 (推荐)
- [ ] 已创建只读用户 (可选)
- [ ] 已配置告警规则 (可选)

---

## 📞 需要帮助?

如果遇到问题:

1. 检查本文档的"常见问题排查"部分
2. 查看Grafana容器日志: `docker logs mystocks-grafana`
3. 查看PostgreSQL日志
4. 参考Grafana官方文档: https://grafana.com/docs/

---

**配置指南版本**: 1.0.0
**最后更新**: 2025-10-12

🎉 **祝配置顺利!**
