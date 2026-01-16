# CLI-main 任务清单

**角色**: Multi-CLI协调器
**职责**: 协调所有Worker CLI，管理任务池

## 核心任务（持续进行）

### 1. CLI报到管理
- [x] 1.1 初始化Multi-CLI环境
- [x] 1.2 配置registrations.json
- [ ] 1.3 接收并确认Worker CLI报到
  - [ ] api CLI报到
  - [ ] db CLI报到
  - [ ] worker1 CLI报到
  - [ ] worker2 CLI报到
  - [ ] worker3 CLI报到

### 2. 任务池管理
- [x] 2.1 初始化任务池（TASKS_POOL.md, tasks.json）
- [ ] 2.2 发布新任务到任务池
- [ ] 2.3 监控任务认领和进度
- [ ] 2.4 审核完成的任务

### 3. 协调调度
- [ ] 3.1 启动smart_coordinator智能协调器
- [ ] 3.2 定期扫描所有CLI状态
- [ ] 3.3 处理CLI阻塞问题
- [ ] 3.4 重新分配闲置资源

### 4. 监控和报告
- [ ] 4.1 生成CLI状态报告
- [ ] 4.2 更新任务池统计
- [ ] 4.3 记录协调日志

## 当前优先级

**高优先级**:
- 等待其他CLI报到（api, db, worker{1-3}）
- 准备新任务发布

**中优先级**:
- 监控web CLI的工作进度
- 优化任务池管理流程

## 已完成

- ✅ 初始化Multi-CLI环境结构
- ✅ 创建main CLI配置文件
- ✅ 确认web CLI报到并分配角色
- ✅ 初始化任务池系统
- ✅ 创建TASKS_POOL.md和tasks.json

## 参考文档

- Multi-CLI快速参考: `CLIS/README.md`
- CLI报到指南: `docs/guides/CLI_REGISTRATION_GUIDE.md`
- 任务池指南: `docs/guides/TASK_POOL_USAGE_GUIDE.md`
