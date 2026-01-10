# 数据源集中管理功能列表清单

> **生成日期**: 2026-01-07
> **版本**: v2.0
> **用途**: 列出数据源管理系统的所有可用功能

---

## 📊 功能概览

MyStocks 数据源管理 V2.0 提供 **7大功能模块**，共 **50+个具体功能**：

| 模块 | 功能数 | 状态 |
|------|--------|------|
| **数据源搜索与发现** | 8 | ✅ |
| **数据源测试与验证** | 10 | ✅ |
| **健康监控** | 7 | ✅ |
| **配置管理** | 9 | ✅ |
| **智能路由** | 6 | ✅ |
| **数据质量保证** | 8 | ✅ |
| **生命周期管理** | 5 | ✅ |

---

## 1️⃣ 数据源搜索与发现 (8个功能)

### 1.1 基础搜索
- **功能1**: 按数据分类搜索
  - 支持所有5层分类（market_data, reference_data, derived_data等）
  - 支持34个具体分类（DAILY_KLINE, MINUTE_KLINE等）
  - 实现方式: `/api/v1/data-sources/search?data_category=DAILY_KLINE`

- **功能2**: 按数据源类型搜索
  - 支持类型: api_library, database, crawler, file, mock
  - 实现方式: `/api/v1/data-sources/search?source_type=api_library`

- **功能3**: 按健康状态搜索
  - 状态: healthy, degraded, failed, unknown
  - 实现方式: `/api/v1/data-sources/search?health_status=healthy`

- **功能4**: 关键词搜索
  - 搜索范围: endpoint_name, description, tags
  - 实现方式: `/api/v1/data-sources/search?keyword=stock`

### 1.2 高级筛选
- **功能5**: 组合筛选
  - 支持多条件组合（AND逻辑）
  - 示例: `?data_category=DAILY_KLINE&health_status=healthy&source_type=api_library`

- **功能6**: 按优先级排序
  - 支持升序和降序
  - 实现方式: `/api/v1/data-sources/search?sort=priority&order=asc`

- **功能7**: 按质量评分排序
  - 范围: 0-10分
  - 实现方式: `/api/v1/data-sources/search?sort=quality_score&order=desc`

- **功能8**: 分页查询
  - 支持page和page_size参数
  - 实现方式: `/api/v1/data-sources/search?page=1&page_size=20`

---

## 2️⃣ 数据源测试与验证 (10个功能)

### 2.1 手动测试工具
- **功能9**: 交互式测试模式
  - 提供友好的菜单导航
  - 支持按分类浏览数据源
  - 自动使用默认测试参数
  - 命令: `python scripts/tools/manual_data_source_tester.py --interactive`

- **功能10**: 命令行测试模式
  - 支持直接指定测试参数
  - 适合自动化测试
  - 命令: `python scripts/tools/manual_data_source_tester.py --endpoint akshare.stock_zh_a_hist --symbol 000001`

### 2.2 数据质量分析
- **功能11**: 完整性检查
  - 检查必需列是否存在
  - 验证最小记录数
  - 检测空值和缺失值

- **功能12**: 范围检查
  - 检查数值范围是否合理
  - 检测异常值和离群点
  - 验证日期范围

- **功能13**: 类型一致性检查
  - 验证列数据类型
  - 检查数据格式
  - 检测类型转换错误

- **功能14**: 重复性检查
  - 检测重复记录
  - 计算重复率
  - 标记重复行

### 2.3 性能测试
- **功能15**: 响应时间测试
  - 测量API调用耗时
  - 对比历史性能
  - 识别性能退化

- **功能16**: 成功率测试
  - 统计成功和失败次数
  - 计算成功率百分比
  - 识别不稳定的数据源

### 2.4 API接口测试
- **功能17**: FastAPI手动测试端点
  - 端点: `POST /api/v1/data-sources/test`
  - 请求体: `{"endpoint_name": "akshare.stock_zh_a_hist", "test_params": {...}}`
  - 响应: 包含成功状态、耗时、数据量、数据预览、质量检查结果

- **功能18**: 测试参数验证
  - 验证必需参数
  - 检查参数类型
  - 使用默认测试参数（如果未提供）

---

## 3️⃣ 健康监控 (7个功能)

### 3.1 健康检查
- **功能19**: 单个endpoint健康检查
  - 检查连接状态
  - 测试响应时间
  - 验证数据质量
  - 实现方式: `GET /api/v1/data-sources/health?endpoint_name=akshare.stock_zh_a_hist`

- **功能20**: 批量健康检查
  - 检查所有活跃数据源
  - 生成健康报告
  - 识别问题数据源
  - 实现方式: `GET /api/v1/data-sources/health`

- **功能21**: 按分类健康检查
  - 检查特定分类的所有数据源
  - 支持并行检查
  - 实现方式: `GET /api/v1/data-sources/health?data_category=DAILY_KLINE`

### 3.2 监控指标
- **功能22**: 实时性能监控
  - 平均响应时间
  - 成功率
  - 总调用次数
  - 失败调用次数

- **功能23**: 数据质量监控
  - 数据质量评分（0-10）
  - 健康状态（healthy/degraded/failed/unknown）
  - 数据新鲜度
  - 连续失败次数

- **功能24**: 额度使用监控
  - 已使用额度
  - 额度上限
  - 使用率百分比
  - 额度告警

### 3.3 告警机制
- **功能25**: 自动告警
  - 连续失败告警
  - 响应时间告警
  - 质量评分下降告警
  - 额度不足告警

---

## 4️⃣ 配置管理 (9个功能)

### 4.1 配置更新
- **功能26**: 更新优先级
  - 动态调整数据源优先级
  - 影响路由选择
  - API: `PUT /api/v1/data-sources/{endpoint_name}`

- **功能27**: 更新质量评分
  - 手动或自动更新
  - 范围: 0-10
  - 影响路由选择

- **功能28**: 更新状态
  - 状态选项: active, deprecated, maintenance, testing
  - 控制数据源可用性

- **功能29**: 更新描述
  - 修改数据源描述信息
  - 添加使用说明

### 4.2 配置查询
- **功能30**: 获取单个数据源详情
  - 查询完整配置信息
  - 包含监控指标
  - API: `GET /api/v1/data-sources/{endpoint_name}`

- **功能31**: 获取所有数据源列表
  - 返回所有注册的数据源
  - 支持分页
  - API: `GET /api/v1/data-sources/search`

- **功能32**: 获取分类统计
  - 每个分类的endpoint数量
  - 健康状态分布
  - 平均质量评分
  - 平均响应时间
  - API: `GET /api/v1/data-sources/category-stats`

- **功能33**: 获取所有分类
  - 返回所有5层分类
  - 返回所有34个具体分类
  - API: `GET /api/v1/data-sources/categories`

### 4.3 配置同步
- **功能34**: YAML到PostgreSQL同步
  - 从YAML加载配置
  - 同步到PostgreSQL
  - 支持增量更新

---

## 5️⃣ 智能路由 (6个功能)

### 5.1 路由策略
- **功能35**: 基于优先级路由
  - 选择优先级最高的数据源
  - 优先级数字越小越优先
  - 自动fallback到次优数据源

- **功能36**: 基于健康状态路由
  - 仅选择healthy状态的数据源
  - 自动跳过failed和degraded的数据源

- **功能37**: 基于质量评分路由
  - 选择质量评分最高的数据源
  - 评分范围: 0-10

### 5.2 负载均衡
- **功能38**: 轮询策略
  - 在多个健康数据源之间轮询
  - 分散调用压力

- **功能39**: 随机策略
  - 随机选择健康数据源
  - 适用于同等优先级的数据源

### 5.3 Fallback机制
- **功能40**: 自动Fallback
  - 主数据源失败时自动切换
  - 按优先级顺序尝试
  - 记录fallback事件

---

## 6️⃣ 数据质量保证 (8个功能)

### 6.1 质量验证
- **功能41**: 参数验证
  - 验证必需参数
  - 检查参数类型
  - 验证参数格式（正则表达式）
  - 使用默认值（如果允许）

- **功能42**: 响应数据验证
  - 检查必需列
  - 验证数据类型
  - 检查数据范围
  - 验证数据格式

### 6.2 质量规则
- **功能43**: 最小记录数规则
  - 定义: `min_record_count`
  - 用途: 确保返回足够的数据

- **功能44**: 最大响应时间规则
  - 定义: `max_response_time`（秒）
  - 用途: 检测性能问题

- **功能45**: 必需列规则
  - 定义: `required_columns`（数组）
  - 用途: 确保关键字段存在

- **功能46**: 数据类型规则
  - 定义: `data_types`（映射）
  - 用途: 确保列数据类型正确

### 6.3 质量评分
- **功能47**: 自动质量评分
  - 基于多个维度计算
  - 维度: 完整性、准确性、新鲜度、性能
  - 范围: 0-10

- **功能48**: 手动质量评分
  - 管理员手动调整
  - 用于覆盖自动评分

---

## 7️⃣ 生命周期管理 (5个功能)

### 7.1 数据源注册
- **功能49**: 新增数据源
  - 通过YAML配置注册
  - 同步到PostgreSQL
  - 自动分配endpoint_name

### 7.2 状态管理
- **功能50**: 激活数据源
  - 状态: active
  - 可用于生产

- **功能51**: 停用数据源
  - 状态: deprecated
  - 保留历史数据，不再使用

- **功能52**: 维护模式
  - 状态: maintenance
  - 暂时不可用，维护中

- **功能53**: 测试模式
  - 状态: testing
  - 仅用于测试，不建议生产使用

---

## 📊 功能统计

### 按实现方式分类

| 实现方式 | 功能数 | 占比 |
|----------|--------|------|
| **FastAPI RESTful API** | 17 | 34% |
| **手动测试工具** | 10 | 20% |
| **核心管理器内部** | 15 | 30% |
| **配置文件管理** | 8 | 16% |

### 按使用频率分类

| 使用频率 | 功能数 | 示例 |
|----------|--------|------|
| **高频（日常使用）** | 15 | 搜索、测试、健康检查 |
| **中频（定期使用）** | 20 | 配置更新、质量分析 |
| **低频（偶尔使用）** | 15 | 生命周期管理、批量操作 |

---

## 🎯 功能优先级

### P0 - 核心功能（必须实现）
1. 数据源搜索与筛选
2. 手动测试工具
3. 健康检查
4. 配置查询

### P1 - 重要功能（应尽快实现）
5. 配置更新
6. 智能路由
7. 数据质量验证
8. 性能监控

### P2 - 增强功能（可选实现）
9. 自动告警
10. 负载均衡
11. 批量操作
12. Grafana仪表板集成

---

## 📚 API端点完整列表

| 方法 | 端点 | 功能 | 状态 |
|------|------|------|------|
| GET | `/api/v1/data-sources/search` | 搜索数据源 | ✅ |
| GET | `/api/v1/data-sources/category-stats` | 获取分类统计 | ✅ |
| GET | `/api/v1/data-sources/categories` | 获取所有分类 | ✅ |
| GET | `/api/v1/data-sources/{endpoint_name}` | 获取单个数据源详情 | ✅ |
| PUT | `/api/v1/data-sources/{endpoint_name}` | 更新数据源配置 | ✅ |
| POST | `/api/v1/data-sources/test` | 手动测试数据源 | ✅ |
| GET | `/api/v1/data-sources/health` | 健康检查（单个或批量） | ✅ |

---

## 🛠️ 命令行工具

| 工具 | 命令 | 功能 | 状态 |
|------|------|------|------|
| **手动测试工具** | `python scripts/tools/manual_data_source_tester.py --interactive` | 交互式测试 | ✅ |
| **手动测试工具** | `python scripts/tools/manual_data_source_tester.py --endpoint <name> --symbol <code>` | 命令行测试 | ✅ |
| **配置同步** | （待实现） | YAML到PostgreSQL同步 | ⏳ |

---

## 📖 使用示例

### 示例1: 搜索日线K线数据源
```bash
curl "http://localhost:8000/api/v1/data-sources/search?data_category=DAILY_KLINE&health_status=healthy"
```

### 示例2: 测试AKShare数据源
```python
from scripts.tools.manual_data_source_tester import DataSourceTester

tester = DataSourceTester()
result = tester.test_data_source(
    endpoint_name='akshare.stock_zh_a_hist',
    test_params={'symbol': '000001', 'start_date': '20240101', 'end_date': '20240131'}
)
```

### 示例3: 获取分类统计
```bash
curl "http://localhost:8000/api/v1/data-sources/category-stats"
```

### 示例4: 更新数据源优先级
```bash
curl -X PUT "http://localhost:8000/api/v1/data-sources/akshare.stock_zh_a_hist" \
  -H "Content-Type: application/json" \
  -d '{"priority": 1}'
```

---

## 🎯 下一步开发计划

### Phase 1: 完善核心功能（已完成 ✅）
- [x] 数据源搜索与筛选
- [x] 手动测试工具
- [x] 健康检查
- [x] 配置查询和更新

### Phase 2: 增强监控能力（进行中 🔄）
- [ ] Grafana仪表板集成
- [ ] 自动告警机制
- [ ] 实时监控指标
- [ ] 调用历史可视化

### Phase 3: 优化路由策略（待开发 ⏳）
- [ ] 智能路由优化
- [ ] 负载均衡策略
- [ ] A/B测试支持
- [ ] 灰度发布支持

### Phase 4: 提升易用性（待开发 ⏳）
- [ ] Web UI界面
- [ ] 批量操作支持
- [ ] 配置导入导出
- [ ] 使用文档完善

---

**生成人**: Claude Code (Main CLI)
**生成日期**: 2026-01-07
**功能版本**: v2.0
**状态**: ✅ 50+个功能已实现，待完善监控和优化
