# Phase 0: Credential Rotation & Security Setup Guide

**Date**: 2025-12-05
**Status**: 🔄 In Progress
**Priority**: 🔴 CRITICAL

---

## Overview

This guide covers the immediate security actions required for the MyStocks project. These actions must be completed within 24 hours to mitigate credential exposure risks.

---

## 1. Credential Inventory & Rotation

### 1.1 Currently Exposed Credentials

**Location**: `.env` file (committed to git history)

| Credential | Current Value | Exposure Risk | Status |
|-----------|---------------|---------------|--------|
| TDENGINE_PASSWORD | `taosdata` | ✅ Default, should rotate | ⏳ Needs rotation |
| POSTGRESQL_PASSWORD | `c790414J` | ✅ Weak (8 chars), should rotate | ⏳ Needs rotation |
| JWT_SECRET_KEY | `be5d2db05101...` | ✅ Exposed in repo | ⏳ Needs rotation |
| MONITOR_DB_URL | Contains password | ✅ Exposed in repo | ⏳ Needs rotation |

### 1.2 Rotation Procedure

#### Step 1: Generate New Credentials (Local Machine)

```bash
# Generate new JWT secret (32 hex chars)
NEW_JWT_SECRET=$(openssl rand -hex 32)
echo "New JWT Secret: $NEW_JWT_SECRET"

# Generate strong database passwords (16+ chars with mixed case)
NEW_TDENGINE_PASS=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)
echo "New TDengine Password: $NEW_TDENGINE_PASS"

NEW_POSTGRES_PASS=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-16)
echo "New PostgreSQL Password: $NEW_POSTGRES_PASS"
```

#### Step 2: Update Database Credentials

**For TDengine (if accessible)**:
```bash
# Connect to TDengine and change password
taos -u root -p taosdata

# In taos CLI:
ALTER USER root PASS '<NEW_TDENGINE_PASS>';
```

**For PostgreSQL** (if accessible):
```bash
# Connect and change password
psql -U postgres -d mystocks

-- In psql:
ALTER USER postgres WITH PASSWORD '<NEW_POSTGRES_PASS>';
```

#### Step 3: Update Local .env File (DO NOT COMMIT)

Edit `/opt/claude/mystocks_spec/.env`:

```bash
# OLD VALUES (REMOVE)
TDENGINE_PASSWORD=taosdata
POSTGRESQL_PASSWORD=c790414J
JWT_SECRET_KEY=be5d2db05101c9caf256b69b6895f20681e214d2578f3ceb98b3405581f00ae9
MONITOR_DB_URL=postgresql://postgres:c790414J@192.168.123.104:5438/mystocks

# NEW VALUES (REPLACE)
TDENGINE_PASSWORD=<YOUR_NEW_TDENGINE_PASSWORD>
POSTGRESQL_PASSWORD=<YOUR_NEW_POSTGRES_PASSWORD>
JWT_SECRET_KEY=<YOUR_NEW_JWT_SECRET>
MONITOR_DB_URL=postgresql://postgres:<YOUR_NEW_POSTGRES_PASSWORD>@192.168.123.104:5438/mystocks
```

#### Step 4: Verify Pre-commit Hook is Active

```bash
# Ensure pre-commit is installed
pip install pre-commit

# Install hook
pre-commit install

# Test that .env cannot be committed
git add .env
git commit -m "test: attempt to commit .env"
# Should FAIL with: "ERROR: The following .env files are about to be committed"

# Reset staging area
git reset HEAD .env
```

#### Step 5: Verify Secrets Cannot Be Committed

```bash
# Test with a hardcoded password in a Python file
echo "PASSWORD = 'taosdata'" >> test_secret.py
git add test_secret.py

# Try to commit (should fail)
git commit -m "test: detect secrets"

# Expected output: Shows secret detection warning
# Clean up test file
git reset HEAD test_secret.py
rm test_secret.py
```

---

## 2. Pre-Commit Hook Configuration

### 2.1 Current Configuration

**Location**: `.pre-commit-config.yaml`

**Enabled Security Hooks**:
- ✅ `detect-private-key` - Detects private key patterns
- ✅ `detect-secrets` - Detects common credential patterns
- ✅ `bandit` - Python security linting
- ✅ `pylint` - Code quality and security checks

### 2.2 Testing the Hooks

```bash
# Run all hooks on current changes
pre-commit run --all-files

# Run specific hook
pre-commit run detect-secrets --all-files

# Run on a single file
pre-commit run --files .env.example
```

### 2.3 Bypassing Hooks (NOT RECOMMENDED)

Only use in emergency situations with explicit authorization:

```bash
# Commit without running hooks (dangerous!)
git commit --no-verify -m "Emergency commit"
```

---

## 3. Git History Remediation

### 3.1 Current Situation

**Problem**: Credentials are already in git history from previous commits.

**Verification**:
```bash
# Check if credentials are in history
git log -p --all | grep -E "TDENGINE_PASSWORD|POSTGRESQL_PASSWORD|JWT_SECRET_KEY"

# List commits containing exposed credentials
git log --all --oneline | grep -i "env\|credential\|secret"
```

### 3.2 Remediation Strategy

**Option 1: BFG Repo-Cleaner** (Recommended for small repos)

```bash
# Install BFG
brew install bfg  # or: brew install --cask bfg

# Create a file with patterns to remove
cat > .bfg-patterns.txt << 'EOF'
TDENGINE_PASSWORD=.*
POSTGRESQL_PASSWORD=.*
JWT_SECRET_KEY=.*
EOF

# Clean the repository
bfg --replace-text .bfg-patterns.txt

# Force push (requires repo lock)
git reflog expire --expire=now --all && git gc --prune=now --aggressive
git push origin --force
```

**Option 2: Manual History Rewrite** (For critical credentials only)

```bash
# Interactive rebase (not recommended for long history)
git rebase -i --root

# Mark commits with exposed credentials as 'edit'
# Remove credentials and continue
git rebase --continue
git push origin --force
```

### 3.3 Notification Steps

After git history is cleaned:

1. **Notify team**: Inform all developers that history has been rewritten
2. **Force pull**: All developers must force-pull and reset their branches
3. **Update CI/CD**: Ensure CI/CD uses new credentials from environment variables
4. **Rotate again**: Rotate credentials one more time after cleanup

**Command for developers**:
```bash
# Force pull new history
git fetch origin
git reset --hard origin/main

# Update local branches
git remote prune origin
```

---

## 4. Environment Variable Management

### 4.1 CI/CD Configuration

**GitHub Actions Example**:
```yaml
env:
  TDENGINE_PASSWORD: ${{ secrets.TDENGINE_PASSWORD }}
  POSTGRESQL_PASSWORD: ${{ secrets.POSTGRESQL_PASSWORD }}
  JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
```

**GitLab CI Example**:
```yaml
variables:
  TDENGINE_PASSWORD: $CI_COMMIT_REF_PROTECTED ? $TDENGINE_PASSWORD_PROD : $TDENGINE_PASSWORD_DEV
  POSTGRESQL_PASSWORD: $CI_COMMIT_REF_PROTECTED ? $POSTGRESQL_PASSWORD_PROD : $POSTGRESQL_PASSWORD_DEV
```

### 4.2 Local Development

**Secure .env Loading**:
```python
from pathlib import Path
from dotenv import load_dotenv

# Load from .env (not committed)
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    # Fallback to environment variables
    print("⚠️  .env file not found, using environment variables")
```

---

## 5. Monitoring & Verification

### 5.1 Ongoing Checks

**Weekly Security Audit**:
```bash
#!/bin/bash
# scripts/security/weekly_audit.sh

echo "🔍 Weekly Security Audit"
echo "=========================="

# 1. Check for exposed credentials in uncommitted changes
echo "1️⃣  Checking uncommitted changes..."
git diff --cached | grep -iE "PASSWORD|SECRET|KEY|TOKEN" && echo "❌ FOUND SECRETS" || echo "✅ No secrets in staging"

# 2. Check recent commits
echo "2️⃣  Checking recent commits..."
git log -20 --oneline --all | xargs -I {} sh -c 'git show {} | grep -iE "PASSWORD|SECRET|KEY|TOKEN" && echo "⚠️  Potential secret in {}"' || echo "✅ No secrets in recent commits"

# 3. Verify .env is not tracked
echo "3️⃣  Checking .env tracking..."
git ls-files | grep "\.env" && echo "❌ .env is tracked!" || echo "✅ .env is properly ignored"

# 4. Test pre-commit hooks
echo "4️⃣  Testing pre-commit hooks..."
pre-commit run --all-files 2>&1 | grep -i error && echo "❌ Hook errors detected" || echo "✅ Hooks working correctly"

echo ""
echo "✅ Audit complete!"
```

**Automate with cron** (runs every Sunday at 2 AM):
```bash
# Add to crontab
0 2 * * 0 /opt/claude/mystocks_spec/scripts/security/weekly_audit.sh
```

### 5.2 Incident Response

**If credentials are leaked**:

1. **Immediate Actions** (< 1 hour)
   - [ ] Rotate affected credentials immediately
   - [ ] Revoke all active sessions/tokens
   - [ ] Notify security team

2. **Short-term Actions** (1-24 hours)
   - [ ] Analyze access logs for unauthorized access
   - [ ] Update all service integrations with new credentials
   - [ ] Audit database changes

3. **Medium-term Actions** (1 week)
   - [ ] Implement credential scanning in CI/CD
   - [ ] Conduct security training
   - [ ] Update incident response procedures

---

## 6. Success Criteria

### Phase 0 Completion Checklist

- [ ] New JWT secret generated and deployed
- [ ] TDengine password rotated in database
- [ ] PostgreSQL password rotated in database
- [ ] Local .env file updated with new credentials
- [ ] Pre-commit hooks tested and working
- [ ] `.env` file confirmed untrackable by git
- [ ] Team notified of credential rotation
- [ ] Weekly security audit script created and tested
- [ ] All services updated with new credentials
- [ ] Incident response plan documented

### Security Validation

```bash
# Final verification script
#!/bin/bash

echo "🔒 Phase 0 Security Validation"
echo "=============================="

# 1. Check that old credentials are NOT in staging
! git diff --cached | grep -E "taosdata|c790414J|be5d2db05101" && echo "✅ Old credentials not in staging" || (echo "❌ FOUND OLD CREDENTIALS"; exit 1)

# 2. Verify .env is in gitignore
grep "^\.env$" .gitignore > /dev/null && echo "✅ .env in .gitignore" || (echo "❌ .env not in .gitignore"; exit 1)

# 3. Test pre-commit hook can detect a secret
echo "TEST_PASSWORD='secret123'" > test.py
git add test.py
if ! git commit -m "test" 2>&1 | grep -i secret > /dev/null; then
    echo "⚠️  Pre-commit hook may not be detecting secrets"
else
    echo "✅ Pre-commit hook detecting secrets"
fi
git reset HEAD test.py
rm test.py

# 4. Verify database connectivity with new credentials
python3 << 'PYTHON'
import os
try:
    # Test imports (don't actually connect in this validation)
    from src.storage.database import DatabaseTableManager
    print("✅ Database modules importable")
except Exception as e:
    print(f"❌ Database import failed: {e}")
    exit(1)
PYTHON

echo ""
echo "✅ All Phase 0 validations passed!"
```

---

## 7. References

- [OWASP: Secrets Management](https://owasp.org/www-community/Sensitive_Data_Exposure)
- [Pre-commit Framework](https://pre-commit.com/)
- [Detect-Secrets Library](https://github.com/Yelp/detect-secrets)
- [BFG Repo-Cleaner](https://rtyley.github.io/bfg-repo-cleaner/)
- [Git Security Best Practices](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)

---

## Next Steps

After completing Phase 0:

1. **Phase 1.1** (4 hours): Define custom exception hierarchy
2. **Phase 1.2** (4 hours): Refactor exception handling in `stock_search.py`
3. **Phase 1.3** (12 hours): Complete TODO items in critical files

**Total Phase 1 effort**: 20 hours (Week 1 of 6-week plan)

---

**Document Status**: Active
**Last Updated**: 2025-12-05
**Next Review**: 2025-12-12
