# MyStocks 分布式量化数据工厂：跨系统集成白皮书

## 1. 设计理念 (Design Philosophy)
MyStocks 分布式架构旨在解决 WSL2 Linux 环境与 Windows 专有金融 SDK (Wind, TDX, QMT) 之间的物理隔离问题。

- **解耦 (Decoupling)**: 核心业务逻辑在 Linux，硬件级数据采集在 Windows。
- **按需触发 (Lazy Loading)**: 仅在业务需要时触发远程节点取数，拒绝无意义的资源空转。
- **数据闭环 (NAS Closure)**: 跨系统通信仅传输指令，百万级数据通过 NAS 共享存储实现静默同步。

## 2. 核心组件 (Core Components)

### 2.1 Windows Provider (提供者)
- **脚本**: `scripts/templates/windows_task_node.py`
- **职能**: 封装 SDK (WindPy, xtquant)，监听 8001 端口，直接将结果写入 NAS PostgreSQL。

### 2.2 WSL2 Consumer (消费者)
- **适配器**: `web/backend/app/services/windows_bridge_adapter.py`
- **职能**: 节点在线状态管理、任务指令下发 (Task Triggering)。

## 3. 部署方法 (Deployment)

### 3.1 节点部署
1. 在 Windows 环境准备 Python 3.10+。
2. 运行 `pip install fastapi uvicorn requests pandas sqlalchemy psycopg2`。
3. 启动节点: `python scripts/templates/windows_task_node.py`。

### 3.2 注册配置
在 `config/data_sources_registry.yaml` 中配置 `providers` IP 矩阵。

## 4. 联调验证
在 WSL2 执行一键联调脚本：
```bash
python3 scripts/tests/verify_windows_bridge_connectivity.py
```

---
**版本**: v1.0  
**作者**: Gemini CLI Agent  
**日期**: 2026-02-16
