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

You are working on {{ issue.identifier }} ({{ issue.title }}).
Follow AGENTS.md, stay inside the assigned scope, and record concrete verification evidence before handoff.
