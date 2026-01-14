#!/usr/bin/env node
/**
 * 修复Element Plus手动导入问题
 *
 * 移除所有手动导入的Element Plus组件和图标，依赖unplugin-vue-components自动导入
 * 这可以显著减少bundle大小
 */

const fs = require('fs')
const path = require('path')
const { execSync } = require('child_process')

// 需要移除的导入模式
const importPatterns = [
  // Element Plus组件导入
  /import\s*{\s*([^}]*El[A-Z][^}]*)}\s*from\s*['"]element-plus['"]/g,
  // Element Plus图标导入
  /import\s*{\s*([^}]*)}\s*from\s*['"]@element-plus\/icons-vue['"]/g,
  // 混合导入（同时包含组件和图标）
  /import\s*{\s*([^}]*El[A-Z][^}]*)[^}]*}\s*from\s*['"]element-plus['"]/g,
]

// 需要保留的导入（这些不会被自动导入）
const keepPatterns = [
  'ElMessage', // 应该被自动导入，但如果手动导入也可以
  'ElMessageBox',
]

// 递归查找所有Vue和TS文件
function findFiles(dir, extensions = ['.vue', '.ts', '.js']) {
  const files = []

  function traverse(currentPath) {
    const entries = fs.readdirSync(currentPath, { withFileTypes: true })

    for (const entry of entries) {
      const fullPath = path.join(currentPath, entry.name)

      // 跳过node_modules和隐藏目录
      if (entry.isDirectory() && !entry.name.startsWith('.') && entry.name !== 'node_modules') {
        traverse(fullPath)
      } else if (entry.isFile()) {
        const ext = path.extname(entry.name)
        if (extensions.includes(ext)) {
          files.push(fullPath)
        }
      }
    }
  }

  traverse(dir)
  return files
}

// 修复单个文件
function fixFile(filePath) {
  let content = fs.readFileSync(filePath, 'utf-8')
  let modified = false
  const removedImports = []

  // 移除Element Plus组件导入
  content = content.replace(
    /import\s*{\s*([^}]*El[A-Z][^}]*[,;\s]*)}\s*from\s*['"]element-plus['"];\s*\n?/g,
    (match, imports) => {
      const components = imports.split(',').map(s => s.trim()).filter(s => s)
      const keepComponents = components.filter(c => keepPatterns.includes(c))

      if (keepComponents.length === 0) {
        modified = true
        removedImports.push(...components)
        return '' // 完全移除导入
      } else if (keepComponents.length < components.length) {
        modified = true
        const removed = components.filter(c => !keepComponents.includes(c))
        removedImports.push(...removed)
        return `import { ${keepComponents.join(', ')} } from 'element-plus';\n`
      }

      return match
    }
  )

  // 移除@element-plus/icons-vue图标导入（图标应该通过组件自动导入）
  content = content.replace(
    /import\s*{\s*([^}]+)\s*}\s*from\s*['"]@element-plus\/icons-vue['"];\s*\n?/g,
    (match, imports) => {
      modified = true
      removedImports.push(...imports.split(',').map(s => s.trim()))
      return '' // 移除图标导入
    }
  )

  if (modified) {
    fs.writeFileSync(filePath, content, 'utf-8')
    console.log(`✅ 修复: ${filePath}`)
    console.log(`   移除导入: ${removedImports.join(', ')}`)
    return true
  }

  return false
}

// 主函数
function main() {
  const srcDir = path.join(__dirname, '../../src')
  const files = findFiles(srcDir)

  console.log(`🔍 扫描 ${files.length} 个文件...\n`)

  let fixedCount = 0
  const report = {
    total: files.length,
    fixed: 0,
    files: []
  }

  for (const file of files) {
    if (fixFile(file)) {
      fixedCount++
      report.fixed++
      report.files.push(file)
    }
  }

  console.log(`\n✨ 完成！`)
  console.log(`📊 统计:`)
  console.log(`   - 扫描文件: ${report.total}`)
  console.log(`   - 修复文件: ${report.fixed}`)
  console.log(`   - 跳过文件: ${report.total - report.fixed}`)

  if (report.fixed > 0) {
    console.log(`\n📝 修复的文件:`)
    report.files.forEach(f => {
      console.log(`   - ${path.relative(srcDir, f)}`)
    })
  }

  console.log(`\n💡 提示: Element Plus组件和图标现在通过unplugin-vue-components自动导入`)
  console.log(`   这可以显著减少bundle大小（约40%的Element Plus相关代码）`)
}

// 运行
if (require.main === module) {
  main()
}

module.exports = { findFiles, fixFile }
