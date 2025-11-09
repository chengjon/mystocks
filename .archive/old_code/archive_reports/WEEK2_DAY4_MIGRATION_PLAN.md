# Week 2 Day 4 - 数据库迁移计划

**制定日期**: 2025-10-19
**目标**: 4数据库简化为PostgreSQL单数据库

---

## 📋 迁移概览

### 迁移目标

**当前架构**:
```
MySQL (0.38MB) + PostgreSQL (9.6MB) + TDengine (5行) + Redis (3 keys)
```

**目标架构**:
```
PostgreSQL + TimescaleDB (单数据库)
```

### 迁移范围

| 数据库 | 数据量 | 迁移方式 | 预计时间 |
|--------|--------|----------|----------|
| MySQL → PostgreSQL | 299行, 0.38MB | 数据迁移 | 1小时 |
| TDengine | 5行测试数据 | 移除 | 30分钟 |
| Redis | 3 keys | 评估后决定 | 30分钟 |

**总预计时间**: **2-3小时**

---

## 🔄 迁移方案

### 方案1: MySQL → PostgreSQL迁移

#### 步骤1: 在PostgreSQL中创建表结构
```sql
-- 基于MySQL的18个表创建对应PostgreSQL表
-- 主要表: wencai_queries, symbols, wencai_qs_*

CREATE TABLE wencai_queries (
    id SERIAL PRIMARY KEY,
    query_name VARCHAR(255),
    -- 其他列...
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 其他17个表...
```

**执行方式**: 使用pgloader或手动脚本

#### 步骤2: 数据迁移
```bash
# 方法A: 使用pgloader (推荐)
pgloader mysql://root:***@192.168.123.104/quant_research \
          postgresql://postgres:***@192.168.123.104:5438/mystocks

# 方法B: 手动导出导入
mysqldump quant_research | sed 's/AUTO_INCREMENT/SERIAL/' | \
psql -h 192.168.123.104 -p 5438 mystocks
```

**数据量**: 299行，预计<5分钟

#### 步骤3: 验证迁移
```sql
-- 检查行数
SELECT 'wencai_queries' as table, count(*) FROM wencai_queries
UNION ALL
SELECT 'symbols', count(*) FROM symbols;

-- 对比MySQL原始数据
```

#### 步骤4: 更新应用配置
```python
# 修改 .env
# MYSQL_HOST=...  # 注释掉
# 更新代码中的MySQL连接为PostgreSQL
```

**风险等级**: 🟢 低 (数据量小，易回滚)

---

### 方案2: TDengine移除

#### 步骤1: 确认无生产数据
```bash
# 已确认: 仅5行测试数据
# market_data.tick_data_000001_sz: 2行
# market_data.test_table: 1行
# db.tb: 2行
```

#### 步骤2: 代码清理
```bash
# 搜索TDengine相关代码
grep -r "TDengine\|taospy\|taosws" --include="*.py" .

# 注释或移除TDengine相关代码
# - db_manager/database_manager.py: TDengine连接配置
# - data_access.py: TDengineDataAccess类
# - adapters: TDengine相关适配器
```

#### 步骤3: 配置清理
```bash
# .env中注释TDengine配置
# TDENGINE_HOST=...
# TDENGINE_USER=...
```

#### 步骤4: 卸载依赖
```bash
# requirements.txt移除
# taospy
# taos-ws-py
```

**风险等级**: 🟢 低 (无生产数据)

---

### 方案3: Redis简化

#### 当前状态分析
- 配置db1: 0 keys (完全未使用)
- 实际db0: 3 keys (Django session等)
- 代码中有Redis调用但未实际使用

#### 选项A: 完全移除 (推荐)
```python
# 移除Redis相关代码
# - 缓存功能 → 使用PostgreSQL或内存
# - Session存储 → 使用PostgreSQL
```

#### 选项B: 保留最小配置
```python
# 仅保留必要的Redis功能
# 但基于Day 1-3评估，无必要功能
```

**建议**: 选项A - 完全移除
**风险等级**: 🟡 中 (需确认无隐藏依赖)

---

## ⚠️ 风险评估

### 风险矩阵

| 风险 | 可能性 | 影响 | 等级 | 缓解措施 |
|------|--------|------|------|----------|
| MySQL迁移数据丢失 | 低 | 中 | 🟢 | 完整备份+验证 |
| 应用代码依赖MySQL | 中 | 高 | 🟡 | 代码审查+测试 |
| TDengine隐藏依赖 | 低 | 中 | 🟢 | grep搜索+测试 |
| Redis隐藏功能 | 中 | 中 | 🟡 | 代码审查+监控 |
| PostgreSQL性能 | 低 | 低 | 🟢 | 数据量小，无风险 |

### 关键风险

**风险1: 应用代码依赖**
- **描述**: 代码中硬编码了MySQL/TDengine/Redis连接
- **影响**: 应用启动失败或功能异常
- **缓解**: 全面代码审查，搜索所有数据库连接代码

**风险2: 未知业务逻辑**
- **描述**: 某些功能隐式依赖多数据库
- **影响**: 功能缺失
- **缓解**: 与业务团队确认，完整测试

---

## 🔙 回滚方案

### 回滚准备

**前置条件**:
1. ✅ 完整备份已创建 (Day 2)
2. ✅ 备份已验证
3. 🔲 迁移前再次备份

### 回滚步骤

#### 场景1: MySQL迁移失败
```bash
# 1. 停止应用
systemctl stop mystocks-app

# 2. 恢复.env配置
git checkout .env

# 3. 从PostgreSQL删除已迁移数据
psql -h ... -c "DROP TABLE IF EXISTS wencai_queries CASCADE;"

# 4. 重启应用
systemctl start mystocks-app
```

**预计时间**: 10分钟

#### 场景2: 应用启动失败
```bash
# 1. 回滚代码更改
git reset --hard HEAD~1

# 2. 恢复配置
cp .env.backup .env

# 3. 重启服务
systemctl restart mystocks-app
```

**预计时间**: 5分钟

#### 场景3: 完全回滚
```bash
# 使用Day 2备份完整恢复所有数据库
tar -xzf manual_20251019_172048.tar.gz
# 执行恢复脚本...
```

**预计时间**: 30分钟

---

## 📅 迁移时间表

### 阶段1: 准备 (1天)
- [ ] 代码审查 - 识别所有数据库依赖
- [ ] 创建迁移脚本
- [ ] 准备测试环境
- [ ] 再次完整备份

### 阶段2: 迁移 (1天)
- [ ] 上午: MySQL → PostgreSQL迁移
- [ ] 中午: 验证数据完整性
- [ ] 下午: TDengine移除
- [ ] 下午: Redis评估和清理

### 阶段3: 验证 (1天)
- [ ] 功能测试
- [ ] 性能测试
- [ ] 业务验证
- [ ] 监控告警

### 阶段4: 清理 (0.5天)
- [ ] 卸载TDengine/Redis
- [ ] 更新文档
- [ ] 代码清理提交

**总计**: 3.5天

---

## ✅ 成功标准

### 技术标准
- [ ] 所有MySQL数据成功迁移到PostgreSQL
- [ ] 数据完整性100%验证通过
- [ ] TDengine相关代码完全移除
- [ ] Redis依赖清理或移除
- [ ] 应用正常启动和运行
- [ ] 所有单元测试通过

### 业务标准
- [ ] 核心功能正常工作
- [ ] 数据查询响应时间<1秒
- [ ] 无数据丢失
- [ ] 无业务中断

### 运维标准
- [ ] 数据库连接数降低75%
- [ ] 备份时间缩短
- [ ] 监控告警配置更新
- [ ] 文档完整更新

---

## 📝 检查清单

### 迁移前
- [ ] 完整备份所有数据库
- [ ] 代码分支创建: `feature/single-db-migration`
- [ ] 迁移脚本准备和测试
- [ ] 团队沟通和时间窗口确认
- [ ] 回滚方案演练

### 迁移中
- [ ] 停止应用写入
- [ ] 执行MySQL迁移
- [ ] 数据验证
- [ ] 配置更新
- [ ] 代码更新
- [ ] 应用重启

### 迁移后
- [ ] 功能验证
- [ ] 性能监控
- [ ] 错误日志检查
- [ ] 业务确认
- [ ] 备份验证

---

## 🎯 关键决策点

### 决策1: Redis处理方式
**选项**:
- A) 完全移除 (推荐)
- B) 保留最小配置

**建议**: A - 基于Day 1-3评估，Redis几乎未使用

### 决策2: 迁移时机
**选项**:
- A) 立即迁移 (Week 3)
- B) 等待更多验证 (Week 4+)

**建议**: A - 数据量小，风险低，尽早简化

### 决策3: TimescaleDB使用
**选项**:
- A) 立即启用所有时序表
- B) 渐进式启用

**建议**: B - 先迁移，再优化

---

## 📊 预期收益

### 运维简化
- 数据库数量: 4 → 1 (-75%)
- 备份时间: 30分钟 → 5分钟 (-83%)
- 监控复杂度: 降低70%

### 成本节约
- 服务器资源: 降低60%
- 许可成本: 降低75% (如有)
- 运维时间: 节省50%

### 性能提升
- 连接池复用更高效
- 跨库查询变为本地查询
- 备份恢复更快速

---

**制定时间**: 2025-10-19 18:20
**审批状态**: 待审批
**下一步**: Day 5 POC验证
