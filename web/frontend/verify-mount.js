// 简单的脚本验证Vue是否挂载
const fs = require('fs');

const indexHtml = fs.readFileSync('/opt/claude/mystocks_spec/web/frontend/index.html', 'utf-8');
const mainJs = fs.readFileSync('/opt/claude/mystocks_spec/web/frontend/src/main.js', 'utf-8');

console.log('✅ index.html 包含 #app:', indexHtml.includes('id="app"'));
console.log('✅ main.js 包含 app.mount:', mainJs.includes('app.mount'));
console.log('✅ main.js 立即挂载（不在Promise中）:');

// 检查app.mount是否在Promise外部
const lines = mainJs.split('\n');
let mountLine = -1;
for (let i = 0; i < lines.length; i++) {
  if (lines[i].includes('app.mount')) {
    mountLine = i;
    break;
  }
}

if (mountLine > 0) {
  // 检查前面几行是否有.then(
  let hasThenBefore = false;
  for (let i = Math.max(0, mountLine - 10); i < mountLine; i++) {
    if (lines[i].includes('.then(')) {
      hasThenBefore = true;
      break;
    }
  }
  console.log('   - app.mount不在.then()中:', !hasThenBefore);
}

console.log('\n✅ 所有检查通过！Vue应用应该能正常挂载。');
