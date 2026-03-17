# Public Repo History Remediation

Date: 2026-03-17

## Goal

Clean the already-published git history after the working tree has been sanitized, without rewriting history in a dirty local checkout.

## Preconditions

1. Real credentials have already been rotated.
2. The branch tip you want to preserve already contains the current sanitized files.
3. You are running from a clean clone or from a committed branch tip.

## Files

- Replacement rules: `filter-repo-replacements.txt`
- Path removals: `filter-repo-remove-paths.txt`
- Rewrite runner: `rewrite_public_history.sh`

## Required Environment Variables

Before running the rewrite, export the old leaked values locally:

```bash
export OLD_PROVIDER_API_KEY='...'
export OLD_FUCAI_API_KEY='...'
export OLD_MODEL_CATALOG_API_KEY='...'
export OLD_WEB_READER_TOKEN='...'
export OLD_JWT_TOKEN='...'
export OLD_POSTGRES_PASSWORD='...'
export OLD_INTERNAL_HOST='...'
```

## Recommended Flow

1. Commit the current sanitization changes on the branch that will become the new public baseline.
2. Run:

```bash
./rewrite_public_history.sh /path/to/repo /tmp/mystocks_spec-public-sanitized.git
```

3. Inspect the rewritten mirror:

```bash
git -C /tmp/mystocks_spec-public-sanitized.git log --stat -n 5
```

4. Force-push all refs once verified:

```bash
git -C /tmp/mystocks_spec-public-sanitized.git push --force --mirror origin
```

## What Gets Cleaned

- Replaces the confirmed leaked provider keys, bearer token, JWT, database password, and internal host.
- Removes tracked trace files, secret backups, config backups, and archived `.parcel-cache` artifacts from history.

## Important Limitation

The rewrite script clones committed git history only. Uncommitted files in the current worktree are not included in the rewritten mirror. Do not run the rewrite before committing the sanitized tree you want to preserve.
