import { chromium } from 'playwright';

const browser = await chromium.launch({
  headless: false
});

const page = await browser.newPage();

// 捕获所有控制台消息
page.on('console', msg => {
  const type = msg.type();
  const text = msg.text();
  console.log(`[${type.toUpperCase()}] ${text}`);
});

// 捕获所有页面错误
page.on('pageerror', error => {
  console.log(`🔴 PAGE ERROR: ${error.message}`);
  console.log(`   Stack: ${error.stack}`);
});

// 捕获请求失败
page.on('requestfailed', request => {
  console.log(`❌ REQUEST FAILED: ${request.url()} (${request.failure().errorText})`);
});

console.log('🌐 正在访问 http://localhost:3001\n');

try {
  await page.goto('http://localhost:3001', {
    waitUntil: 'networkidle',
    timeout: 10000
  });

  console.log('\n⏳ 等待5秒收集错误...\n');
  await page.waitForTimeout(5000);

  // 检查Vue实例
  const vueCheck = await page.evaluate(() => {
    return {
      hasWindowVue: typeof window.$vue !== 'undefined',
      appHTML: document.querySelector('#app')?.innerHTML || '',
      appLength: document.querySelector('#app')?.innerHTML?.length || 0,
      bodyText: document.body.innerText
    };
  });

  console.log('\n📊 Vue状态检查:');
  console.log(`  window.$vue存在: ${vueCheck.hasWindowVue}`);
  console.log(`  #app HTML长度: ${vueCheck.appLength}`);
  console.log(`  #app内容预览: ${vueCheck.appHTML.substring(0, 200)}`);

  // 截图
  await page.screenshot({
    path: '/tmp/comprehensive-diagnostic.png',
    fullPage: true
  });
  console.log('\n📸 截图已保存: /tmp/comprehensive-diagnostic.png');

} catch (error) {
  console.error(`🔴 导航失败: ${error.message}`);
} finally {
  await browser.close();
}
