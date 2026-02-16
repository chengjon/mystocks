# MyStocks API 可用端点分析报告 (Architecture Summary)

**版本**: v3.1.0  
**日期**: 2026-02-16

## 1. 路由体系架构
系统采用双层路由治理模式：
- **逻辑源**: `web/backend/app/api/VERSION_MAPPING.py` (Single Source of Truth)。
- **物理挂载**: `web/backend/app/main.py` (基于映射动态注册)。

## 2. 前缀统计表 (Prefix Statistics)
| 业务域 | 前缀 | 版本 | 状态 |
| :--- | :--- | :--- | :--- |
| **Auth** | `/api/v1/auth` | 1.0.0 | 🟢 Stable |
| **Market** | `/api/v1/market` | 1.0.0 | 🟢 Aligned |
| **Strategy** | `/api/v1/strategy` | 1.0.0 | 🟢 Aligned |
| **Monitoring** | `/api/v1/monitoring` | 1.0.0 | 🟢 Aligned |
| **Data** | `/api/v1/data` | 1.0.0 | 🟢 Aligned |

## 3. 三数据库集成架构 (Tri-DB Architecture)
| 数据库 | 角色 | 状态 | 关键指标 |
| :--- | :--- | :--- | :--- |
| **PostgreSQL** | 关系型主库 / 注册表 | ✅ 集成 | ACID 事务支持 |
| **TDengine** | 极速时序 K 线 / Tick | ✅ 集成 | 高压缩比, 低延迟查询 |
| **Redis** | **Mandatory** L2 缓存 / 信号桥接 | ✅ 已集成 | 响应延迟 < 1ms |

## 4. 连通性分析
- **已同步端点**: 60 (基于 `data_source_registry`)
- **智能路由命中率**: 100% (DAILY_KLINE -> tushare)
