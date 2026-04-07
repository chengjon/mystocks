# MyStocks Web 端口配置规则

> **参考指南说明**:
> 本文件用于提供 Web 子系统的使用方法、操作指引、接口接入说明、排障提示或结构参考，帮助理解局部实现与协作方式。
> 其中的步骤、示例、端口、目录和操作建议应先与 `architecture/STANDARDS.md`、当前代码实现及最新验证结果核对；若涉及仓库执行流程、命令或协作约束，再补充参考根目录 `AGENTS.md`。本文件不得单独视为仓库共享规则或当前状态的唯一事实来源。


**创建人**: Claude  
**版本**: 3.0.0  
**批准日期**: 2025-10-15  
**最后修订**: 2026-03-02  
**本次修订内容**: 固定端口统一为 `.env` 驱动，移除代码端口硬编码约束

---

## 端口分配标准（固定）

### 前端服务 (Vite)
- **主端口**: `3020`
- **备用端口**: `3021`

### 后端服务 (FastAPI)
- **主端口**: `8020`
- **备用端口**: `8021`

---

## 强制规则

1. 端口必须通过 `.env` 配置，禁止在运行时代码中硬编码端口号。
2. 前端固定使用 `3020`，备用 `3021`。
3. 后端固定使用 `8020`，备用 `8021`。
4. 启动服务前必须检查端口占用，优先释放冲突进程。
5. 任何端口变更必须先更新本文件与 `CLAUDE.md`，并同步 `.env`/`.env.example`。

---

## `.env` 配置示例

```bash
FRONTEND_PORT=3020
FRONTEND_BACKUP_PORT=3021
BACKEND_PORT=8020
BACKEND_BACKUP_PORT=8021
```

---

## 访问地址

- 前端: `http://localhost:3020`
- 后端: `http://localhost:8020`
- API 文档: `http://localhost:8020/api/docs`

---

## 启动命令（使用 `.env`）

```bash
# 后端
cd web/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port "${BACKEND_PORT}"

# 前端
cd web/frontend
npm run dev -- --port "${FRONTEND_PORT}"
```

---

## 端口冲突处理

```bash
# 查找占用进程
lsof -i :3020
lsof -i :8020

# 停止进程
kill -9 <PID>
```
