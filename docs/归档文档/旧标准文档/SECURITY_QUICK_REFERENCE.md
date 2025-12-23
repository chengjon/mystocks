# Security Quick Reference Guide
**Date**: 2025-11-30
**Purpose**: Quick lookup guide for security procedures and standards

---

## 🚨 Critical Security Reminders

### ❌ NEVER DO THIS
```bash
# ❌ NEVER commit real credentials
git add .env
git commit -m "Add production credentials"

# ❌ NEVER hardcode passwords
const PASSWORD = "admin123";  // NO!
const API_KEY = "sk-real-key-12345";  // NO!

# ❌ NEVER store credentials in comments
# Password: c790414J  // NO!
# API Key: sk-12345  // NO!

# ❌ NEVER add credentials to .env.example
POSTGRESQL_PASSWORD=c790414J  # NO!
```

### ✅ ALWAYS DO THIS
```bash
# ✅ Use placeholder values in examples
POSTGRESQL_PASSWORD=your-postgres-password
API_KEY=your-api-key

# ✅ Store credentials in local .env (git-ignored)
echo ".env" >> .gitignore
echo "POSTGRESQL_PASSWORD=real-password" > .env

# ✅ Use environment variables
const PASSWORD = process.env.TEST_PASSWORD || 'admin123';
const API_KEY = process.env.API_KEY;

# ✅ Reference docs for setup
# See: DEVELOPMENT_STANDARDS.md for detailed guidelines
```

---

## 📋 Pre-Development Checklist

Before starting a new feature, verify:

- [ ] Read `docs/standards/DEVELOPMENT_STANDARDS.md` (if exists)
- [ ] No credentials hardcoded anywhere
- [ ] Using environment variables for sensitive data
- [ ] .env.example contains only placeholders
- [ ] .gitignore includes all credential files
- [ ] Local .env file created (never committed)

---

## 🔧 Setting Up Local Environment

### Step 1: Copy Example File
```bash
cp .env.example .env
cp config/.env.example config/.env
```

### Step 2: Edit with Real Credentials
```bash
# Edit .env with YOUR local database credentials
nano .env

# Change placeholders:
# your-postgres-password → your-actual-password
# your-tdengine-password → your-actual-password
```

### Step 3: Verify .gitignore
```bash
# Confirm .env is ignored
git status | grep .env  # Should show nothing
```

### Step 4: Test Connection
```bash
# Verify credentials work
python -c "from src.db_manager import DatabaseConnectionManager; \
           mgr = DatabaseConnectionManager(); \
           print('✅ Database connected!')"
```

---

## 🔐 Credential Files Reference

| File | Purpose | Version Control |
|------|---------|-----------------|
| `.env` | Local credentials | ❌ Never commit |
| `.env.example` | Template for developers | ✅ Commit with placeholders |
| `.env.production` | Production credentials | ❌ Never commit |
| `.env.local` | Local overrides | ❌ Never commit |
| `config/.env` | Local service config | ❌ Never commit |
| `config/.env.example` | Service config template | ✅ Commit with placeholders |

---

## 🚀 CI/CD Secret Management

### Using GitHub Secrets
```bash
# 1. Go to Settings → Secrets and variables → Actions
# 2. Create secret: DB_PASSWORD = actual-password
# 3. In workflow file:
env:
  DB_PASSWORD: ${{ secrets.DB_PASSWORD }}
```

### Using GitLab CI Variables
```bash
# 1. Go to Settings → CI/CD → Variables
# 2. Create variable: DB_PASSWORD = actual-password
# 3. In .gitlab-ci.yml:
variables:
  DB_PASSWORD: $DB_PASSWORD
```

---

## 🧪 Test Credential Management

### ✅ Correct Way
```javascript
// Option 1: Load from environment
const TEST_USER = process.env.TEST_USERNAME || 'admin';
const TEST_PASS = process.env.TEST_PASSWORD || 'admin123';

// Option 2: Create tests/.env.test (git-ignored)
// Run: npm test -- --env=tests/.env.test
```

### ❌ Wrong Way
```javascript
// DON'T hardcode test credentials
const TEST_USER = 'admin';
const TEST_PASS = 'admin123';
```

---

## 🔍 Pre-Commit Checks

### Manual Verification
Before committing:
```bash
# 1. Check for passwords in staged files
git diff --cached | grep -i "password\|secret\|key\|token"

# 2. Check for .env files
git status | grep "\.env"

# 3. If found: unstage and add to .gitignore
git reset <file>
echo ".env" >> .gitignore
```

### Automated Checks
Using gitleaks (if installed):
```bash
# Run before commit
gitleaks detect --source . --verbose

# Install as pre-commit hook
pip install gitleaks
# Then configure .git/hooks/pre-commit
```

---

## 🐛 If You Accidentally Commit a Credential

### ⚠️ IMMEDIATE ACTION REQUIRED

1. **Do NOT push to remote yet** (if local commit only)

2. **Remove from commit** (if not pushed):
   ```bash
   # Option A: Amend last commit
   git reset --soft HEAD~1
   # Edit files and remove credentials
   git add .
   git commit -m "fix: Remove accidentally committed credentials"

   # Option B: Use git-filter-repo (if already pushed)
   git filter-repo --invert-paths --path config/sensitive-file
   git push --force-with-lease origin main
   ```

3. **Rotate credentials immediately**:
   - Change database password
   - Regenerate API keys
   - Revoke tokens
   - Notify team

4. **Verify removal**:
   ```bash
   # Check git history
   git log -S "credential-value" --all
   ```

5. **Document incident** in security log

---

## 📞 Escalation Contacts

| Issue | Contact | Action |
|-------|---------|--------|
| Credential accidentally committed | Security Lead | Contact immediately |
| Suspicious access/activity | Security Lead | Investigate logs |
| Vulnerability discovered | Security Lead | Plan remediation |
| Tool setup/integration issues | DevOps Team | Request support |
| Questions about standards | Project Manager | Schedule review |

---

## 📚 Full Documentation

For comprehensive information, see:

- **Security Audit Report**: `docs/standards/SECURITY_AUDIT_REPORT_20251130.md`
- **Follow-up Implementation Plan**: `docs/standards/SECURITY_FOLLOWUP_PLAN_20251130.md`
- **Development Standards** (coming soon): `docs/standards/DEVELOPMENT_STANDARDS.md`
- **Credential Management Checklist** (coming soon): `docs/standards/CREDENTIAL_MANAGEMENT_CHECKLIST.md`

---

## ✅ Monthly Verification

**First Friday of each month**, verify:

```bash
#!/bin/bash
# Quick monthly security check

echo "🔍 Checking for hardcoded credentials..."
grep -r "password\|secret\|api_key" --include="*.py" --include="*.js" \
  --exclude-dir=node_modules --exclude-dir=.git . | \
  grep -v "# password is\|# api_key is\|test_" | \
  wc -l

echo "🔍 Checking for uncommitted .env files..."
git status | grep "\.env" | wc -l

echo "🔍 Scanning git history for secrets..."
git log -S "password=" --all --oneline | wc -l

echo "✅ Monthly security check complete!"
```

---

## 🎓 Training Resources

### For New Team Members
- Watch: 15-min security briefing (presented by Security Lead)
- Read: This Quick Reference Guide (5 min)
- Practice: Set up local .env file with guidance (10 min)

### For Developers
- Reference: DEVELOPMENT_STANDARDS.md
- Checklist: CREDENTIAL_MANAGEMENT_CHECKLIST.md
- Tools: gitleaks, detect-secrets, GitGuardian

### For DevOps/Infrastructure
- Guide: SECURITY_FOLLOWUP_PLAN_20251130.md (Phase 2-3)
- Tools: Secret scanning, CI/CD integration, monitoring setup

---

## 🔗 Quick Links

| Resource | Location |
|----------|----------|
| This Guide | `docs/standards/SECURITY_QUICK_REFERENCE.md` |
| Audit Report | `docs/standards/SECURITY_AUDIT_REPORT_20251130.md` |
| Follow-up Plan | `docs/standards/SECURITY_FOLLOWUP_PLAN_20251130.md` |
| Project Standards | `docs/standards/DEVELOPMENT_STANDARDS.md` (coming) |
| Git Ignore | `.gitignore` (root directory) |
| Env Example | `.env.example` (root directory) |

---

**Last Updated**: 2025-11-30
**Version**: 1.0
**Status**: ACTIVE

For questions or updates, contact: Security Lead
