#!/bin/bash
# Type Generation CI Integration Script
# Integrates type conflict detection into CI/CD pipeline

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "🔍 Running Type Generation CI Check..."

# Navigate to project root
cd "$PROJECT_ROOT"

# Run type generation with strict mode
echo "📝 Generating TypeScript types with conflict checking..."

# Create temporary config for CI with strict mode
cat > /tmp/ci_type_config.yaml << 'EOF'
conflict_resolution:
  priority_sources: ["nullable", "latest", "first"]
  auto_fix_rules:
    - pattern: "string vs string \| null"
      action: "prefer_nullable"
    - pattern: "number vs number \| null"
      action: "prefer_nullable"
    - pattern: "boolean vs boolean \| null"
      action: "prefer_nullable"
    - pattern: "date vs string"
      action: "prefer_string"
  ignore_conflicts: ["market", "timestamp", "id"]

output:
  warn_on_conflicts: true
  max_warnings: 20

validation:
  strict_mode: true  # Fail CI on conflicts in strict mode
  required_domains: ["common", "trading", "strategy"]
EOF

# Run type generation with CI config
if python scripts/generate_frontend_types.py --all; then
    echo "✅ Type generation completed successfully"

    # Check if any conflicts remain
    if [ -f "web/frontend/src/api/types/index.ts" ]; then
        echo "📋 Checking generated types..."

        # Count any remaining conflicts (warnings about unresolved conflicts)
        WARNING_COUNT=$(python scripts/generate_frontend_types.py --all 2>&1 | grep -c "Unresolved type conflict" || true)

        if [ "$WARNING_COUNT" -gt 0 ]; then
            echo "❌ Found $WARNING_COUNT unresolved type conflicts"
            echo "🔍 Run 'python scripts/generate_frontend_types.py --all' locally to see details"
            exit 1
        fi

        echo "✅ No unresolved type conflicts found"
    else
        echo "❌ Type generation failed - output files not created"
        exit 1
    fi
else
    echo "❌ Type generation failed with exit code $?"
    exit 1
fi

# Clean up temporary config
rm -f /tmp/ci_type_config.yaml

echo "🎉 CI Type Check passed successfully!"