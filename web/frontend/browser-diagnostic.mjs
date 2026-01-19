import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();

console.log('🔍 浏览器诊断: 检查Vue应用挂载状态\n');

// 访问首页
await page.goto('http://localhost:3001', { waitUntil: 'networkidle' });

// 诊断1: 检查#app元素
const appHTML = await page.locator('#app').innerHTML();
const appLength = appHTML.length;
const textLength = await page.locator('body').innerText().then(t => t.length);

console.log('📊 #app元素分析:');
console.log(`   HTML长度: ${appLength} 字符`);
console.log(`   文本长度: ${textLength} 字符`);

if (appLength === 0) {
  console.log('   ❌ 场景A: #app为空 - Vue未挂载');
} else if (appLength < 100) {
  console.log('   ⚠️  场景B: #app几乎为空 - Vue部分挂载');
  console.log(`   内容预览: ${appHTML.substring(0, 100)}`);
} else {
  console.log('   ✅ 场景C: #app有内容 - Vue已挂载');
}

// 诊断2: 检查控制台错误
const errors = [];
page.on('console', msg => {
  if (msg.type() === 'error') {
    errors.push(msg.text());
  }
});

// 等待一下收集错误
await page.waitForTimeout(2000);

console.log(`\n🔍 控制台错误: ${errors.length}个`);
if (errors.length > 0) {
  errors.forEach(err => console.log(`   ❌ ${err}`));
} else {
  console.log('   ✅ 无控制台错误');
}

// 诊断3: 检查Vue DevTools
const hasVueDevTools = await page.evaluate(() => {
  return typeof window.__VUE_DEVTOOLS_GLOBAL_HOOK__ !== 'undefined';
});

console.log(`\n🔍 Vue DevTools: ${hasVueDevTools ? '✅ 已安装' : '❌ 未检测到'}`);

// 诊断4: 截图
await page.screenshot({ path: '/tmp/browser-diagnostic.png', fullPage: true });
console.log('\n📸 截图已保存: /tmp/browser-diagnostic.png');

await browser.close();
