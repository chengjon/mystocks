import { chromium } from 'playwright';

const pages = [
  { url: '/', name: 'Home' },
  { url: '/artdeco/market', name: 'ArtDeco市场数据' },
  { url: '/artdeco/trading', name: 'ArtDeco交易管理' },
  { url: '/dashboard/overview', name: 'Dashboard总览' }
];

const browser = await chromium.launch();
const page = await browser.newPage();

console.log('🔍 快速页面验证\n');

for (const p of pages) {
  try {
    await page.goto(`http://localhost:3001${p.url}`, { waitUntil: 'networkidle', timeout: 8000 });
    await page.waitForTimeout(2000);

    const appHTML = await page.locator('#app').first().innerHTML();
    const hasContent = appHTML.length > 100;
    const hasError = await page.locator('#app').first().textContent().then(t => t?.includes('错误') || t?.includes('Error'));

    console.log(`${hasContent ? '✅' : '❌'} ${p.name}: ${appHTML.length}字符 ${hasError ? '(有错误)' : ''}`);
  } catch (error) {
    console.log(`❌ ${p.name}: ${error.message}`);
  }
}

await browser.close();
