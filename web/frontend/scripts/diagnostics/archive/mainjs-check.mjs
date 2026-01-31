import { chromium } from 'playwright';

const browser = await chromium.launch();
const page = await browser.newPage();
const consoleLogs = [];

page.on('console', msg => {
  consoleLogs.push({
    type: msg.type(),
    text: msg.text()
  });
});

await page.goto('http://localhost:3001', { waitUntil: 'networkidle' });
await page.waitForTimeout(3000);

console.log('📋 控制台日志 (最近的30条):\n');
consoleLogs.slice(-30).forEach(log => {
  const prefix = log.type === 'error' ? '❌' : log.type === 'warn' ? '⚠️' : '✅';
  console.log(`${prefix} [${log.type}] ${log.text}`);
});

const hasVue = await page.evaluate(() => {
  return typeof window.$vue !== 'undefined';
});

console.log(`\n🔍 Vue实例检查: ${hasVue ? '✅ window.$vue存在' : '❌ window.$vue不存在'}`);

await browser.close();
