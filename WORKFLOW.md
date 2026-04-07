---
tracker:
  kind: local
  sqlite_path: $SYMPHONY_TRACKER_DB
workspace:
  root: $SYMPHONY_WORKSPACE_ROOT
runtime:
  cli_name: $MAESTRO_CLI_NAME
  collab_backend: sqlite
  collab_mongo_uri: mongodb://localhost:27017
  collab_mongo_db: mystocks_coord
---

> **使用说明**:
> 本文件是本地工作流模板与执行入口，不是仓库共享规则的唯一事实来源。
> 仓库级共享规则与审批门禁以 `architecture/STANDARDS.md` 为准；涉及执行流程、命令与协作约束，再参考根目录 `AGENTS.md` 与根目录 `CLAUDE.md`。

You are working on {{ issue.identifier }} ({{ issue.title }}).
Follow AGENTS.md, stay inside the assigned scope, and record concrete verification evidence before handoff.
