#!/bin/bash
set -e

echo "🔧 Setting up development tools for MyStocks Frontend..."

# 检查package.json是否存在
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found!"
    exit 1
fi

# 安装依赖
echo "📦 Installing dev dependencies..."
npm install --save-dev \
    eslint \
    eslint-plugin-vue \
    @typescript-eslint/parser \
    @typescript-eslint/eslint-plugin \
    @vue/eslint-config-typescript \
    @vue/eslint-config-prettier \
    prettier \
    stylelint \
    stylelint-config-standard-scss \
    stylelint-config-recommended-vue \
    stylelint-scss \
    husky \
    lint-staged \
    -D

# 合并配置到package.json
echo "📝 Merging configuration to package.json..."
if command -v jq &> /dev/null; then
    # 使用jq合并package.json
    jq -s '.[0] * .[1]' package.json package.json.hooks > package.json.tmp
    mv package.json.tmp package.json
    rm package.json.hooks
else
    echo "⚠️  jq not found. Please manually merge package.json.hooks into package.json"
    echo "📄 Configuration saved in package.json.hooks"
fi

# 初始化husky
echo "🪝 Initializing husky..."
npx husky install

echo "✅ Development tools setup completed!"
echo ""
echo "📚 Available commands:"
echo "  npm run lint          - Run ESLint"
echo "  npm run lint:fix       - Fix ESLint errors"
echo "  npm run format         - Format code with Prettier"
echo "  npm run format:check   - Check code formatting"
echo "  npm run stylelint      - Run Stylelint"
echo "  npm run stylelint:fix  - Fix Stylelint errors"
echo "  npm run type-check     - TypeScript type check"
echo ""
echo "🪝 Git hooks configured:"
echo "  Pre-commit: lint-staged + type-check"
echo "  To skip type check: SKIP_TYPE_CHECK=true git commit"
