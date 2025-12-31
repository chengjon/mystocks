# Web Development Hooks Guide

**Version**: 1.0
**Date**: 2025-12-30
**Purpose**: Configure hooks for Web development to prevent file displacement and enforce organization rules

---

## Overview

The Web Development Hooks system provides specialized file tracking, validation, and quality assurance for web development files (TypeScript, Vue, React, CSS, HTML, JavaScript) in the MyStocks project. This prevents web-specific files from being incorrectly moved or deleted by general-purpose hooks.

---

## Hook Scripts

### 1. Web-Dev File Tracker Hook

**File**: `.claude/hooks/post-tool-use-web-dev-file-tracker.sh`

**Purpose**: Track all web development file edits in `docs/web-dev/tracing/`

**Trigger**: PostToolUse (Edit|Write)

**Features**:
- Logs all web file edits with timestamps
- Classifies files by type (TypeScript, Vue, React, CSS, HTML)
- Tracks session metadata (tool, timestamp, changes)
- Separates web dev logs from Python backend logs

**Log Location**: `docs/web-dev/tracing/web-edit-tracker.jsonl`

**Example Log Entry**:
```json
{
  "timestamp": "2025-12-30T15:30:45Z",
  "file_path": "web/frontend/src/components/StockChart.vue",
  "relative_path": "web/frontend/src/components/StockChart.vue",
  "file_type": "Vue Component",
  "web_subdir": "components/",
  "tool_name": "Edit",
  "session_id": "session-123",
  "cwd": "/opt/claude/mystocks_spec"
}
```

---

### 2. Web-Dev Document Organizer Hook

**File**: `.claude/hooks/post-tool-use-web-dev-document-organizer.sh`

**Purpose**: Validate web documentation location and prevent organization violations

**Trigger**: PostToolUse (Write)

**Features**:
- Validates `.md` files are in correct locations
- Prevents moving web development docs to archive
- Checks whitelist before organizing files
- Enforces web-specific file classification rules

**Whitelist**: `.claude/web-dev-whitelist.json`

**Protected Files**:
- All files in `docs/web-dev/`
- All files in `web/` directory
- Root configuration files (package.json, tsconfig.json, etc.)

---

### 3. Web-Dev Quality Gate Hook

**File**: `.claude/hooks/stop-web-dev-quality-gate.sh`

**Purpose**: Enforce web development quality standards before session end

**Trigger**: Stop

**Timeout**: 60 seconds

**Quality Checks**:
1. **TypeScript Compilation** - `tsc --noEmit`
2. **ESLint** - JavaScript/TypeScript linting
3. **React Prop Types** - Type checking
4. **Vue Template Validation** - Template linting
5. **CSS/SCSS Linting** - Style validation
6. **Build Verification** - `npm run build` (optional)

**Exit Codes**:
- `0` - Pass (all quality checks passed)
- `1` - Error (non-critical failures)
- `2` - Block (stop session)

**Error Threshold**: 10 errors before blocking

---

## Configuration Files

### Web Dev Whitelist

**File**: `.claude/web-dev-whitelist.json`

**Purpose**: Exclude web-specific files and directories from general hooks

**Allowed Root Files**:
- `package.json`
- `tsconfig.json`
- `playwright.*.ts`
- `ecosystem.config.js`
- `pm2.config.js`
- `.env`
- `.env.production`
- `.env.example`

**Allowed Directories**:
- `web/`
- `web/backend/`
- `web/frontend/`
- `config/`
- `docs/web-dev/`

---

### Web Dev File Categories

**File**: `.claude/web-dev-file-categories.json`

**Purpose**: Define web file classification and target directories

**Categories**:
```json
{
  "typescript": {
    "category": "TypeScript Source",
    "directory": "web/",
    "priority": "high",
    "extensions": [".ts", ".tsx"]
  },
  "vue": {
    "category": "Vue Component",
    "directory": "web/frontend/src/components/",
    "priority": "high",
    "extensions": [".vue"]
  },
  "react": {
    "category": "React Component",
    "directory": "web/frontend/src/components/",
    "priority": "high",
    "extensions": [".tsx", ".jsx"]
  },
  "css": {
    "category": "Stylesheet",
    "directory": "web/frontend/src/styles/",
    "priority": "low",
    "extensions": [".css", ".scss", ".sass", ".less"]
  },
  "html": {
    "category": "HTML Page",
    "directory": "web/src/pages/",
    "priority": "medium",
    "extensions": [".html", ".htm"]
  },
  "config": {
    "category": "Configuration",
    "directory": "config/",
    "priority": "low",
    "extensions": [".json", ".yml", ".yaml", ".toml"]
  },
  "documentation": {
    "category": "Documentation",
    "directory": "docs/web-dev/",
    "priority": "high",
    "extensions": [".md"]
  }
}
```

---

## File Organization Rules

### Root Directory (Protected)
These files should remain in root directory:
```yaml
root_protected:
  - package.json
  - tsconfig.json
  - playwright.config.ts
  - playwright.config.simple.ts
  - playwright.grafana.config.ts
  - ecosystem.config.js
  - pm2.config.js
  - ecosystem.production.config.js
  - ecosystem.grpc.config.js
  - ecosystem.production.grpc.json
  - .env
  - .env.production
  - .env.example
  - docker-compose.test.yml
  - pyproject.toml
```

### Web Directory Structure
```yaml
web_frontend:
  root: "web/frontend/src/"
  components: "web/frontend/src/components/"
  pages: "web/frontend/src/pages/"
  styles: "web/frontend/src/styles/"
  assets: "web/frontend/src/assets/"
  utils: "web/frontend/src/utils/"
  api: "web/frontend/src/api/"

web_backend:
  root: "web/backend/src/"
  api: "web/backend/api/"
  routes: "web/backend/src/routes/"
  services: "web/backend/src/services/"
  middleware: "web/backend/src/middleware/"
```

### Documentation Structure
```yaml
web_dev_docs:
  root: "docs/web-dev/"
  guides: "docs/web-dev/guides/"
  api: "docs/web-dev/api/"
  tutorials: "docs/web-dev/tutorials/"
  deployment: "docs/web-dev/deployment/"
  tracing: "docs/web-dev/tracing/"
  archived: "docs/web-dev/archived/"
```

---

## Installation

### 1. Create Directory Structure
```bash
mkdir -p docs/web-dev/{guides,api,tutorials,deployment,tracing,archived}
mkdir -p .claude/hooks
```

### 2. Create Hook Scripts
Copy the hook scripts to `.claude/hooks/`:
- `post-tool-use-web-dev-file-tracker.sh`
- `post-tool-use-web-dev-document-organizer.sh`
- `stop-web-dev-quality-gate.sh`

### 3. Create Configuration Files
Copy configuration files to `.claude/`:
- `web-dev-whitelist.json`
- `web-dev-file-categories.json`

### 4. Update Settings
Add web-dev hooks to `.claude/settings.json`:
```json
{
  "hooks": {
    "PostToolUse": {
      "web_dev": [
        {
          "matcher": "Edit|Write",
          "hooks": [
            {
              "type": "command",
              "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-web-dev-file-tracker.sh",
              "timeout": 3
            }
          ]
        },
        {
          "matcher": "Write",
          "hooks": [
            {
              "type": "command",
              "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/post-tool-use-web-dev-document-organizer.sh",
              "timeout": 5
            }
          ]
        }
      ]
    },
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/stop-web-dev-quality-gate.sh",
            "timeout": 60
          }
        ]
      }
    ]
  }
}
```

### 5. Set Permissions
```bash
chmod +x .claude/hooks/*.sh
```

---

## Usage

### Automatic Hook Execution

Hooks execute automatically during file operations:

1. **Edit/Write File** → File Tracker runs
2. **Write File** → Document Organizer runs
3. **Session End** → Quality Gate runs

### Manual Execution

```bash
# Run file tracker manually
.claude/hooks/post-tool-use-web-dev-file-tracker.sh

# Run quality gate manually
.claude/hooks/stop-web-dev-quality-gate.sh
```

---

## Troubleshooting

### Hook Not Executing

1. Check hook permissions: `ls -la .claude/hooks/`
2. Verify settings.json syntax: `jq . .claude/settings.json`
3. Check hook logs: `cat docs/web-dev/tracing/web-edit-tracker.jsonl`

### Quality Gate Blocking Session

1. Review error messages
2. Fix critical errors (TypeScript compilation, ESLint)
3. Temporarily disable: Remove hook from settings.json
4. Override with exit code 0 in hook script

### Files Being Incorrectly Moved

1. Verify whitelist includes file: `cat .claude/web-dev-whitelist.json`
2. Check file category classification
3. Review organization log: `cat docs/web-dev/tracing/web-edit-tracker.jsonl`

---

## Maintenance

### Update Whitelist

Edit `.claude/web-dev-whitelist.json` to add new protected files.

### Update File Categories

Edit `.claude/web-dev-file-categories.json` to add new file types.

### Review Logs

Periodically review logs:
```bash
# Recent web edits
tail -20 docs/web-dev/tracing/web-edit-tracker.jsonl

# Count edits by file type
jq -r '.file_type' docs/web-dev/tracing/web-edit-tracker.jsonl | sort | uniq -c
```

---

## Integration with Existing Hooks

### Separation of Concerns

| Hook | Purpose | Files Managed |
|------|---------|---------------|
| `post-tool-use-file-edit-tracker.sh` | Python backend tracking | `src/`, `tests/` Python files |
| `post-tool-use-web-dev-file-tracker.sh` | Web frontend tracking | `web/`, TypeScript, Vue, React |
| `post-tool-use-document-organizer.sh` | General doc organization | Root `.md` files |
| `post-tool-use-web-dev-document-organizer.sh` | Web doc validation | `docs/web-dev/` |

### Hook Execution Order

1. File Tracker (Python) → `post-tool-use-file-edit-tracker.sh`
2. File Tracker (Web) → `post-tool-use-web-dev-file-tracker.sh`
3. Database Validator → `post-tool-use-database-schema-validator.sh`
4. Mock Data Validator → `post-tool-use-mock-data-validator.sh`
5. Document Organizer (General) → `post-tool-use-document-organizer.sh`
6. Document Organizer (Web) → `post-tool-use-web-dev-document-organizer.sh`
7. Quality Gate (Python) → `stop-python-quality-gate.sh`
8. Quality Gate (Web) → `stop-web-dev-quality-gate.sh`

---

## Examples

### Example 1: Vue Component Edit

**Operation**: Edit `web/frontend/src/components/StockChart.vue`

**Hook Execution**:
1. File Tracker logs edit
2. Classification: Vue Component → components/
3. No organization needed (file in correct location)

**Log Entry**:
```json
{
  "timestamp": "2025-12-30T15:30:45Z",
  "file_path": "/opt/claude/mystocks_spec/web/frontend/src/components/StockChart.vue",
  "relative_path": "web/frontend/src/components/StockChart.vue",
  "file_type": "Vue Component",
  "web_subdir": "components/",
  "tool_name": "Edit",
  "session_id": "session-123",
  "cwd": "/opt/claude/mystocks_spec"
}
```

### Example 2: TypeScript File in Wrong Location

**Operation**: Write `src/types/StockTypes.ts` (should be in web/)

**Hook Execution**:
1. File Tracker logs write
2. Document Organizer validates location
3. Suggests move to `web/frontend/src/types/`

**Suggestion**:
```
⚠️  File Organization Warning
File: src/types/StockTypes.ts
Expected: web/frontend/src/types/StockTypes.ts
Action: Please move file to correct location
```

### Example 3: Quality Gate Failure

**Operation**: Session ends with TypeScript errors

**Hook Execution**:
1. Run `tsc --noEmit`
2. Detect 15 type errors
3. Block session (exceeds threshold of 10)

**Output**:
```
=== Web Development Quality Gate ===

1. TypeScript Compilation Check...
  ❌ TypeScript errors found

Total Errors: 15

❌ Quality check failed: 15 errors found
{
  "decision": "block",
  "reason": "Web development quality gate failed with 15 errors"
}
```

---

## Best Practices

1. **Always run quality gate before committing**
2. **Keep whitelist up to date**
3. **Review logs regularly**
4. **Follow file organization rules**
5. **Use TypeScript strict mode**
6. **Maintain consistent code style**
7. **Test hooks in development environment**
8. **Document hook changes**

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-30 | Initial version |
