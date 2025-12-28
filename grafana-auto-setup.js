const { chromium } = require('playwright');

(async () => {
  console.log('Grafana 自动化配置开始...');

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  try {
    // 访问 Grafana
    console.log('访问 Grafana...');
    await page.goto('http://localhost:3000', { timeout: 60000 });

    // 等待页面加载
    await page.waitForLoadState('networkidle', { timeout: 15000 });
    console.log('✅ 页面加载完成');

    // 登录
    console.log('登录 Grafana...');
    await page.fill('input[name="user"]', 'admin');
    await page.fill('input[name="password"]', 'admin');
    await page.click('button[type="submit"]');

    // 等待跳转
    console.log('等待登录完成...');
    await page.waitForTimeout(5000);
    await page.waitForURL(/\/(home|d\/s)$/, { timeout: 10000 });
    console.log('✅ 登录成功');

    // 进入 Configuration
    console.log('进入 Configuration...');
    await page.goto('http://localhost:3000/configuration');
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    // 点击 Data Sources
    console.log('查找 Data Sources...');
    try {
      const dataSourcesButton = await page.locator('a[href*="datasources"]').first();
      await dataSourcesButton.click();
      await page.waitForTimeout(3000);
      console.log('✅ 找到并点击了 Data Sources');
    } catch (e) {
      console.log('⚠️ 未找到 Data Sources 按钮，尝试手动导航...');
      await page.goto('http://localhost:3000/datasources');
      await page.waitForLoadState('networkidle', { timeout: 10000 });
      console.log('✅ 直接导航到 Data Sources');
    }

    // 检查是否已有数据源
    console.log('检查现有数据源...');
    await page.waitForTimeout(2000);

    const existingDataSources = await page.locator('.data-source-item').count();
    console.log(`现有数据源数量: ${existingDataSources}`);

    // 如果没有数据源，添加一个
    if (existingDataSources === 0) {
      console.log('没有数据源，需要添加...');

      // 点击 Add data source
      const addButton = await page.locator('button:has-text("Add new data source")').first();
      await addButton.click();
      await page.waitForTimeout(2000);

      // 填写 Prometheus
      console.log('添加 Prometheus...');
      await page.getByPlaceholder(/name/i).fill('Prometheus');
      await page.getByPlaceholder(/url/i).fill('http://mystocks-prometheus:9090');
      await page.locator('select[name="type"]').selectOption({ label: 'Prometheus' });

      // 点击 Save & Test
      await page.locator('button:has-text("Save & Test")').click();
      console.log('✅ Prometheus 数据源已添加');
      await page.waitForTimeout(3000);
    } else {
      console.log(`✅ 已有 ${existingDataSources} 个数据源`);
    }

    // 添加 Loki
    console.log('添加 Loki 数据源...');
    await page.goto('http://localhost:3000/datasources');
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    const addButton = await page.locator('button:has-text("Add new data source")').first();
    await addButton.click();
    await page.waitForTimeout(2000);

    await page.getByPlaceholder(/name/i).fill('Loki');
    await page.getByPlaceholder(/url/i).fill('http://mystocks-loki:3100');
    await page.locator('select[name="type"]').selectOption({ label: 'Loki' });
    await page.locator('button:has-text("Save & Test")').click();
    console.log('✅ Loki 数据源已添加');
    await page.waitForTimeout(3000);

    // 添加 Tempo
    console.log('添加 Tempo 数据源...');
    await page.goto('http://localhost:3000/datasources');
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    await page.locator('button:has-text("Add new data source")').first().click();
    await page.waitForTimeout(2000);

    await page.getByPlaceholder(/name/i).fill('Tempo');
    await page.getByPlaceholder(/url/i).fill('http://mystocks-tempo:3200');
    await page.locator('select[name="type"]').selectOption({ label: 'Tempo' });
    await page.locator('button:has-text("Save & Test")').click();
    console.log('✅ Tempo 数据源已添加');
    await page.waitForTimeout(3000);

    // 添加 NodeExporter
    console.log('添加 NodeExporter 数据源...');
    await page.goto('http://localhost:3000/datasources');
    await page.waitForLoadState('networkidle', { timeout: 10000 });

    await page.locator('button:has-text("Add new data source")').first().click();
    await page.waitForTimeout(2000);

    await page.getByPlaceholder(/name/i).fill('NodeExporter');
    await page.getByPlaceholder(/url/i).fill('http://mystocks-node-exporter:9100');
    await page.locator('select[name="type"]').selectOption({ label: 'Prometheus' });
    await page.locator('button:has-text("Save & Test")').click();
    console.log('✅ NodeExporter 数据源已添加');
    await page.waitForTimeout(3000);

    // 截图
    console.log('截取数据源页面...');
    await page.screenshot({ path: 'grafana-datasources-configured.png', fullPage: true });
    console.log('✅ 已保存截图');

  } catch (error) {
    console.error('❌ 执行出错:', error.message);
    await page.screenshot({ path: 'grafana-error.png', fullPage: true });
  } finally {
    await browser.close();
    console.log('✅ 配置完成');
  }
})();
