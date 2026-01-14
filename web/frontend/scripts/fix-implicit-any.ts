#!/usr/bin/env node
/**
 * 批量修复隐式any类型错误
 *
 * 使用方法:
 * npm run fix:implicit-any
 */

const fs = require('fs');
const path = require('path');

// 需要处理的文件列表
const filesToFix = [
  'src/components/artdeco/advanced/ArtDecoCapitalFlow.vue',
  'src/components/artdeco/advanced/ArtDecoChipDistribution.vue',
];

// 修复模式
const fixPatterns = [
  // reduce callbacks
  {
    pattern: /\.reduce\(\s*\((\w+),\s*(\w+)\)\s*=>/g,
    replacement: '.reduce(($1: any, $2: any) =>',
  },
  // find callbacks
  {
    pattern: /\.find\(\s*(\w+)\s*=>/g,
    replacement: '.find(($1: any) =>',
  },
  // filter callbacks
  {
    pattern: /\.filter\(\s*\((\w+),\s*(\w+)\)\s*=>/g,
    replacement: '.filter(($1: any, $2: any) =>',
  },
  // map callbacks
  {
    pattern: /\.map\(\s*\((\w+),\s*(\w+)\)\s*=>/g,
    replacement: '.map(($1: any, $2: any) =>',
  },
  // forEach callbacks
  {
    pattern: /\.forEach\(\s*(\w+)\s*=>/g,
    replacement: '.forEach(($1: any) =>',
  },
  // sort callbacks
  {
    pattern: /\.sort\(\s*\((\w+),\s*(\w+)\)\s*=>/g,
    replacement: '.sort(($1: any, $2: any) =>',
  },
];

function fixFile(filePath) {
  console.log(`\n🔧 修复文件: ${filePath}`);

  if (!fs.existsSync(filePath)) {
    console.log(`❌ 文件不存在: ${filePath}`);
    return;
  }

  let content = fs.readFileSync(filePath, 'utf8');
  let fixCount = 0;

  // 应用所有修复模式
  fixPatterns.forEach(({ pattern, replacement }) => {
    const matches = content.match(pattern);
    if (matches) {
      const newContent = content.replace(pattern, replacement);
      if (newContent !== content) {
        fixCount += (content.match(pattern) || []).length;
        content = newContent;
      }
    }
  });

  if (fixCount > 0) {
    fs.writeFileSync(filePath, content, 'utf8');
    console.log(`✅ 修复了 ${fixCount} 个隐式any类型`);
  } else {
    console.log(`ℹ️  没有需要修复的类型`);
  }
}

// 主函数
function main() {
  console.log('🚀 开始批量修复隐式any类型错误...\n');

  filesToFix.forEach(file => {
    const fullPath = path.join(process.cwd(), file);
    fixFile(fullPath);
  });

  console.log('\n✨ 修复完成！');
  console.log('\n💡 建议: 运行 npm run type-check 验证修复结果');
}

// 运行
main();
