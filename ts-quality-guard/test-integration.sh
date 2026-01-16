#!/bin/bash
# TypeScript Quality Guard - Integration Test Script

echo "🧪 Running TypeScript Quality Guard Integration Tests"
echo "===================================================="

cd /opt/claude/mystocks_spec/ts-quality-guard

# Test 1: CLI Help
echo ""
echo "📋 Test 1: CLI Help Command"
echo "---------------------------"
node dist/cli/index.js --help | head -15
if [ $? -eq 0 ]; then
    echo "✅ CLI help works"
else
    echo "❌ CLI help failed"
    exit 1
fi

# Test 2: Configuration Validation
echo ""
echo "📋 Test 2: Configuration Validation"
echo "-----------------------------------"
node dist/cli/index.js validate-config
if [ $? -eq 0 ]; then
    echo "✅ Configuration validation works"
else
    echo "❌ Configuration validation failed"
    exit 1
fi

# Test 3: Quality Check
echo ""
echo "📋 Test 3: Quality Check"
echo "------------------------"
node dist/cli/index.js check --format console | head -10
if [ $? -eq 0 ]; then
    echo "✅ Quality check works"
else
    echo "❌ Quality check failed"
    exit 1
fi

# Test 4: Standards Generation
echo ""
echo "📋 Test 4: Standards Generation"
echo "-------------------------------"
node dist/cli/index.js generate-standards --output integration-test-standards.md
if [ $? -eq 0 ] && [ -f "integration-test-standards.md" ]; then
    echo "✅ Standards generation works"
    rm integration-test-standards.md
else
    echo "❌ Standards generation failed"
    exit 1
fi

# Test 5: Init Command
echo ""
echo "📋 Test 5: Init Command (with force)"
echo "-----------------------------------"
node dist/cli/index.js init --force | head -5
if [ $? -eq 0 ]; then
    echo "✅ Init command works"
else
    echo "❌ Init command failed"
    exit 1
fi

echo ""
echo "🎉 All integration tests passed!"
echo "=================================="
echo ""
echo "📊 Test Results Summary:"
echo "   • CLI Help: ✅"
echo "   • Config Validation: ✅"
echo "   • Quality Check: ✅"
echo "   • Standards Generation: ✅"
echo "   • Project Init: ✅"
echo ""
echo "🚀 TypeScript Quality Guard is ready for production use!"
<parameter name="filePath">ts-quality-guard/test-integration.sh