# Change: Add Comprehensive Risk Management System

## Why
MyStocks项目现有信号监控和股票监控系统提供了基础的监控能力，但缺乏完整的风险管理框架。用户需要一个专业的个股+投资组合风险控制体系，包括VaR计算、止损策略、智能预警等功能，以满足个人投资者和小型投资机构的需求。

## What Changes
- **深度集成现有监控系统**: 复用SignalRecorder、MonitoredNotificationManager、异步事件总线
- **扩展GPU加速能力**: 基于现有GPU引擎实现风险指标的高性能计算
- **增强风险计算引擎**: 在现有股票监控基础上增加VaR、CVaR、相关性矩阵等高级风险指标
- **统一预警系统**: 整合现有通知机制，支持多级风险告警
- **前端风险仪表盘**: 在现有监控界面基础上扩展风险可视化
- **数据库架构扩展**: 在现有监控表基础上增加风险专用字段和表

**BREAKING**: 无破坏性变更，所有新功能向后兼容

## Impact
- **新增代码**: ~1500行Python后端代码，~800行Vue前端代码 (减少30%，因大量复用)
- **新增文件**: 8个核心Python模块，6个Vue组件 (减少40%)
- **数据库变更**: 扩展现有监控表，新增3个风险专用表
- **API接口**: 新增8个RESTful端点，扩展2个WebSocket接口
- **依赖关系**: 深度复用SignalRecorder、GPU引擎、MonitoredNotificationManager、异步事件总线
- **部署影响**: 数据库schema扩展，向后兼容现有数据

## Timeline
- **Phase 1 (4周)**: 核心风险计算引擎 + 个股卫士功能
- **Phase 2 (4周)**: 组合平衡器 + 交易哨兵 + 前端仪表盘
- **Phase 3 (2周)**: 预警系统 + 报告生成 + 系统集成测试
