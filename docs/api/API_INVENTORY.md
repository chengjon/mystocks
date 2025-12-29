# API端点清单 (API Inventory)

**生成时间**: 2025-12-29
**API总数**: 340个端点
**扫描范围**: `/web/backend/app/api/`

---

## 📊 统计概览

| 业务模块 | API端点数量 | 状态 | 说明 |
|---------|-----------|------|------|
| Market (市场数据) | ~60 | ✅ 已识别 | K线/行情/资金流向/龙虎榜 |
| Technical (技术指标) | ~30 | ✅ 已识别 | 指标计算/叠加/分析 |
| Trade (交易执行) | ~20 | ✅ 已识别 | 下单/持仓/委托查询 |
| Strategy (策略管理) | ~15 | ✅ 已识别 | 策略CRUD/回测/参数配置 |
| System (系统监控) | ~25 | ✅ 已识别 | 健康检查/数据质量/备份恢复 |
| Monitoring (监控告警) | ~40 | ✅ 已识别 | 告警/指标/日志查询 |
| Auth (认证授权) | ~10 | ✅ 已识别 | 登录/权限/JWT |
| Watchlist (自选股) | ~10 | ✅ 已识别 | 自选分组/CRUD |
| ML (机器学习) | ~20 | ✅ 已识别 | 模型训练/预测 |
| Backup (备份恢复) | ~30 | ✅ 已识别 | 备份/恢复/清理 |
| Notification (通知) | ~10 | ✅ 已识别 | 消息推送/历史 |
| Health (健康检查) | ~11 | ✅ 已识别 | 11个health端点重复 |
| Other (其他) | ~109 | ⚠️ 待分类 | ETF/公告/测试端点等 |
| **总计** | **340** | - | - |

---

## 🎯 核心API端点 (按优先级)

### P0 - 最高优先级 (用户核心功能)

| API端点 | 方法 | 业务模块 | 契约状态 | 缺失信息 | 责任人 |
|---------|-----|---------|---------|---------|--------|
| `/api/market/kline` | GET | Market | ⚠️ 部分定义 | 需完整错误码定义 | Backend |
| `/api/market/overview` | GET | Market | ❌ 未定义 | 完整契约 | Backend |
| `/api/market/fund-flow` | GET | Market | ⚠️ 部分定义 | 响应单位说明 | Backend |
| `/api/indicators/overlay` | GET | Technical | ⚠️ 部分定义 | 错误码定义 | Backend |
| `/api/indicators/calculate` | POST | Technical | ❌ 未定义 | 完整契约 | Backend |
| `/api/trade/order` | POST | Trade | ❌ 未定义 | 完整契约 | Backend |
| `/api/trade/positions` | GET | Trade | ❌ 未定义 | 完整契约 | Backend |
| `/api/strategy/list` | GET | Strategy | ⚠️ 部分定义 | 分页参数 | Backend |
| `/api/strategy/backtest` | POST | Strategy | ❌ 未定义 | 完整契约 | Backend |
| `/api/auth/login` | POST | Auth | ❌ 未定义 | 完整契约 | Backend |
| `/api/watchlist` | GET/POST | Watchlist | ❌ 未定义 | 完整契约 | Backend |

### P1 - 高优先级 (重要辅助功能)

| API端点 | 方法 | 业务模块 | 契约状态 | 缺失信息 |
|---------|-----|---------|---------|---------|
| `/api/market/dragon-tiger` | GET | Market | ⚠️ 部分定义 | 参数验证规则 |
| `/api/market/etf/list` | GET | Market | ❌ 未定义 | 完整契约 |
| `/api/technical/indicators/registry` | GET | Technical | ❌ 未定义 | 完整契约 |
| `/api/trade/history` | GET | Trade | ❌ 未定义 | 完整契约 |
| `/api/trade/account` | GET | Trade | ❌ 未定义 | 完整契约 |
| `/api/strategy/{id}` | GET/PUT/DELETE | Strategy | ❌ 未定义 | 完整契约 |
| `/api/system/status` | GET | System | ❌ 未定义 | 完整契约 |
| `/api/monitoring/alerts` | GET/POST | Monitoring | ⚠️ 部分定义 | 告警级别定义 |
| `/api/data-quality/summary` | GET | System | ❌ 未定义 | 完整契约 |

### P2 - 中等优先级 (管理功能)

| API端点 | 方法 | 业务模块 | 契约状态 | 说明 |
|---------|-----|---------|---------|------|
| `/api/backup/*` | POST/GET | Backup | ❌ 未定义 | 备份恢复API |
| `/api/models/train` | POST | ML | ❌ 未定义 | 模型训练 |
| `/api/notification` | GET/POST | Notification | ❌ 未定义 | 通知推送 |
| `/api/cache/clear` | POST | System | ❌ 未定义 | 缓存管理 |
| `/api/scheduler/jobs` | GET | System | ❌ 未定义 | 定时任务 |

---

## 📁 按文件分类的API清单

### 1. `market.py` - 市场数据API
- **端点数量**: ~20个
- **主要功能**: K线数据、资金流向、龙虎榜、ETF列表
- **契约状态**: ⚠️ 部分定义 (需要补全错误码和详细参数说明)

### 2. `technical_analysis.py` - 技术分析API
- **端点数量**: ~15个
- **主要功能**: 指标计算、叠加指标、指标库
- **契约状态**: ⚠️ 部分定义

### 3. `trade/routes.py` - 交易执行API
- **端点数量**: ~15个
- **主要功能**: 下单、查询持仓、委托历史、账户信息
- **契约状态**: ❌ 未定义 (需完整契约)

### 4. `strategy_management.py` - 策略管理API
- **端点数量**: ~10个
- **主要功能**: 策略CRUD、回测、参数配置
- **契约状态**: ⚠️ 部分定义

### 5. `monitoring/routes.py` - 监控告警API
- **端点数量**: ~25个
- **主要功能**: 告警管理、指标查询、日志查看
- **契约状态**: ❌ 未定义

### 6. `backup_recovery.py` - 备份恢复API
- **端点数量**: ~20个
- **主要功能**: 全量/增量备份、PITR恢复、备份清理
- **契约状态**: ❌ 未定义

### 7. `auth.py` - 认证授权API
- **端点数量**: ~8个
- **主要功能**: 登录、登出、权限验证
- **契约状态**: ❌ 未定义

### 8. `watchlist.py` - 自选股API
- **端点数量**: ~10个
- **主要功能**: 自选分组、CRUD操作
- **契约状态**: ❌ 未定义

### 9. `notification.py` - 通知API
- **端点数量**: ~8个
- **主要功能**: 消息推送、历史查询
- **契约状态**: ❌ 未定义

### 10. `data_quality.py` - 数据质量API
- **端点数量**: ~10个
- **主要功能**: 数据完整性、准确性检查
- **契约状态**: ❌ 未定义

### 11. `health.py` - 健康检查API
- **端点数量**: 11个 (重复定义)
- **主要功能**: 系统健康状态
- **契约状态**: ⚠️ 简单定义
- **注意**: 存在11个重复的`@router.get("/health")`端点,需要去重

---

## 🔍 契约补全优先级

### 阶段1 (本周完成): P0核心API
1. Market模块: `/api/market/kline`, `/api/market/overview`, `/api/market/fund-flow`
2. Technical模块: `/api/indicators/overlay`, `/api/indicators/calculate`
3. Trade模块: `/api/trade/order`, `/api/trade/positions`
4. Strategy模块: `/api/strategy/list`, `/api/strategy/backtest`

### 阶段2 (下周完成): P1高优先级API
1. Market模块补充: 龙虎榜、ETF列表
2. Trade模块补充: 委托历史、账户信息
3. Strategy模块补充: 策略CRUD
4. System模块: 系统状态、数据质量

### 阶段3 (未来迭代): P2管理功能API
1. Backup/Recovery完整契约
2. Monitoring告警契约
3. Notification通知契约

---

## ✅ 验收标准

- [ ] 所有P0 API有完整的OpenAPI 3.0契约定义
- [ ] 所有P0 API使用Pydantic请求/响应模型
- [ ] 所有API返回统一的`APIResponse`格式
- [ ] 错误响应包含详细的错误码和中文提示
- [ ] 契约定义与代码实现一致性校验通过

---

## 📝 更新日志

- **2025-12-29**: 初始版本,统计340个API端点,识别核心业务模块
- 下一步: 为P0核心API创建完整契约定义

---

**文档维护**: CLI-2 Backend API Architect
**联系方式**: 参考 README.md
