import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();

// 捕获所有日志
const logs = [];
page.on('console', msg => {
  logs.push({
    type: msg.type(),
    text: msg.text(),
    args: msg.args().length
  });
});

// 捕获网络请求
const requests = [];
page.on('request', req => {
  requests.push({
    url: req.url(),
    method: req.method(),
    resourceType: req.resourceType()
  });
});

page.on('response', async (resp) => {
  if (resp.status() >= 400) {
    console.log(`❌ 网络失败: ${resp.url()} (${resp.status()})`);
  }
});

console.log('🌐 访问 http://localhost:3001\n');
await page.goto('http://localhost:3001', { waitUntil: 'networkidle' });
await page.waitForTimeout(5000);

// 分析网络请求
console.log('📡 网络请求分析:\n');
const mainRequests = requests.filter(r => r.url.includes('main.js'));
const vueRequests = requests.filter(r => r.url.includes('vue') || r.url.includes('@vue'));

console.log(`main.js请求: ${mainRequests.length}`);
mainRequests.forEach(req => {
  console.log(`  ${req.method} ${req.url}`);
});

console.log(`\nVue相关请求: ${vueRequests.length}`);
vueRequests.slice(0, 5).forEach(req => {
  console.log(`  ${req.method} ${req.url}`);
});

// 检查控制台日志
console.log(`\n📋 控制台日志 (共${logs.length}条):\n`);
if (logs.length === 0) {
  console.log('❌ 无任何日志输出');
} else {
  logs.forEach(log => {
    const prefix = log.type === 'error' ? '❌' : log.type === 'warn' ? '⚠️' : '✅';
    console.log(`${prefix} [${log.type}] ${log.text}`);
  });
}

// 检查DOM状态
const domState = await page.evaluate(() => {
  const app = document.querySelector('#app');
  return {
    appExists: !!app,
    appHTML: app ? app.innerHTML.length : 0,
    bodyText: document.body.innerText.length,
    scriptsCount: document.querySelectorAll('script').length,
    title: document.title
  };
});

console.log('\n🔍 DOM状态:');
console.log(`  #app存在: ${domState.appExists}`);
console.log(`  #app长度: ${domState.appHTML} 字符`);
console.log(`  body文本: ${domState.bodyText} 字符`);
console.log(`  script标签: ${domState.scriptsCount} 个`);
console.log(`  页面标题: ${domState.title}`);

await browser.close();
