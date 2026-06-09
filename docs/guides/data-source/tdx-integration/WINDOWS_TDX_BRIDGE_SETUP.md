# Windows TDX HTTP 桥接代理配置指南 (方案 B)

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或使用手册，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


本文档指导如何在局域网内的 Windows 机器上部署 TDX 取数代理，以便 WSL2 后端进行多源取数。

## 1. Windows 端环境要求
- **Python 3.10+** (Windows 版)
- **TDX 终端**: 需安装并确保 DLL (如 `TdxHq.dll`) 可用。
- **依赖包**: `pip install fastapi uvicorn requests`

## 2. 代理服务蓝图 (tdx_bridge.py)
```python
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="MyStocks TDX Bridge")

@app.get("/health")
async def health():
    return {"status": "online", "node_id": "WINDOWS-NODE-01"}

@app.get("/api/v1/tdx/quote/{symbol}")
async def get_quote(symbol: str):
    # 此处编写调用 TDX DLL 的逻辑
    return {"symbol": symbol, "price": 10.5, "time": "14:30:00"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
```

## 3. WSL2 后端集成配置
在 `config/data_sources_registry.yaml` 中注册多个节点：

```yaml
  tdx_node_01:
    source_name: "tdx_remote"
    source_type: "remote_bridge"
    endpoint_url: "http://example.local:8001" # Windows 机器 A
    priority: 1

  tdx_node_02:
    source_name: "tdx_remote"
    source_type: "remote_bridge"
    endpoint_url: "http://example.local:8001" # Windows 机器 B
    priority: 2
```

## 4. 关键红线
- **跨系统访问**: 必须确保 Windows 防火墙允许 8001 端口的入站连接。
- **IP 稳定性**: 建议为运行代理的 Windows 机器分配静态 IP 或通过 NAS 的 DNS 解析。
