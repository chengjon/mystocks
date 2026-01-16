import { test, expect } from '@playwright/test';
import path from 'path';

test.describe('Grafana Setup Automation', () => {
  test.beforeAll(async ({ page }) => {
    console.log('开始 Grafana 自动化配置...');
    
    // 访问 Grafana
    console.log('访问 Grafana...');
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    // 登录
    console.log('登录 Grafana...');
    await page.locator('input[name="user"]').fill('admin');
    await page.locator('input[name="password"]').fill('admin');
    await page.locator('button[type="submit"]').click();
    
    // 等待登录完成
    await page.waitForURL(/(\/$|\/home|\/d\/s|\/d\/u|\/d\/u\/[a-z]+)/);
    await page.waitForLoadState('networkidle');
    console.log('✅ 登录成功');
  });

  test('添加 Prometheus 数据源', async ({ page }) => {
    console.log('配置 Prometheus 数据源...');
    
    // 检查是否已存在
    const prometheusSource = page.getByRole('menuitem').filter({ hasText: 'Data sources' }).first();
    await prometheusSource.click();
    await page.waitForLoadState('networkidle');
    
    // 查找现有的Prometheus数据源
    const existingSources = page.locator('a').filter({ hasText: 'Prometheus' });
    const prometheusCount = await existingSources.count();
    
    if (prometheusCount > 0) {
      console.log('✅ Prometheus 数据源已存在');
    } else {
      console.log('添加 Prometheus 数据源...');
      await page.locator('button:has-text("Add new data source")').click();
      await page.waitForLoadState('networkidle');
      
      // 填写数据源信息
      await page.getByPlaceholder(/name/i).fill('Prometheus');
      await page.getByPlaceholder(/url/i).fill('http://mystocks-prometheus:9090');
      await page.getByPlaceholder(/type/i).selectOption({ label: 'Prometheus' });
      await page.locator('button:has-text("Save & Test")').click();
      
      // 等待保存完成
      await page.waitForTimeout(5000);
      console.log('✅ Prometheus 数据源已添加');
    }
    
    // 返回到Data Sources页面
    await page.goto('http://localhost:3000/datasources');
    await page.waitForLoadState('networkidle');
  });

  test('添加 Loki 数据源', async ({ page }) => {
    console.log('配置 Loki 数据源...');
    
    await page.locator('a').filter({ hasText: 'Data sources' }).click();
    await page.waitForLoadState('networkidle');
    
    // 查找现有的Loki数据源
    const existingSources = page.locator('a').filter({ hasText: 'Loki' });
    const lokiCount = await existingSources.count();
    
    if (lokiCount > 0) {
      console.log('✅ Loki 数据源已存在');
    } else {
      console.log('添加 Loki 数据源...');
      await page.locator('button:has-text("Add new data source")').click();
      await page.waitForLoadState('networkidle');
      
      // 填写数据源信息
      await page.getByPlaceholder(/name/i).fill('Loki');
      await page.getByPlaceholder(/url/i).fill('http://mystocks-loki:3100');
      await page.getByPlaceholder(/type/i).selectOption({ label: 'Loki' });
      await page.locator('button:has-text("Save & Test")').click();
      
      await page.waitForTimeout(5000);
      console.log('✅ Loki 数据源已添加');
    }
    
    await page.goto('http://localhost:3000/datasources');
    await page.waitForLoadState('networkidle');
  });

  test('添加 Tempo 数据源', async ({ page }) => {
    console.log('配置 Tempo 数据源...');
    
    await page.locator('a').filter({ hasText: 'Data sources' }).click();
    await page.waitForLoadState('networkidle');
    
    // 查找现有的Tempo数据源
    const existingSources = page.locator('a').filter({ hasText: 'Tempo' });
    const tempoCount = await existingSources.count();
    
    if (tempoCount > 0) {
      console.log('✅ Tempo 数据源已存在');
    } else {
      console.log('添加 Tempo 数据源...');
      await page.locator('button:has-text("Add new data source")').click();
      await page.waitForLoadState('networkidle');
      
      await page.getByPlaceholder(/name/i).fill('Tempo');
      await page.getByPlaceholder(/url/i).fill('http://mystocks-tempo:3200');
      await page.getByPlaceholder(/type/i).selectOption({ label: 'Tempo' });
      await page.locator('button:has-text("Save & Test")').click();
      
      await page.waitForTimeout(5000);
      console.log('✅ Tempo 数据源已添加');
    }
    
    await page.goto('http://localhost:3000/datasources');
    await page.waitForLoadState('networkidle');
  });

  test('添加 NodeExporter 数据源', async ({ page }) => {
    console.log('配置 NodeExporter 数据源...');
    
    await page.locator('a').filter({ hasText: 'Data sources' }).click();
    await page.waitForLoadState('networkidle');
    
    // 查找现有的NodeExporter数据源
    const existingSources = page.locator('a').filter({ hasText: 'NodeExporter' });
    const nodeCount = await existingSources.count();
    
    if (nodeCount > 0) {
      console.log('✅ NodeExporter 数据源已存在');
    } else {
      console.log('添加 NodeExporter 数据源...');
      await page.locator('button:has-text("Add new data source")').click();
      await page.waitForLoadState('networkidle');
      
      await page.getByPlaceholder(/name/i).fill('NodeExporter');
      await page.getByPlaceholder(/url/i).fill('http://mystocks-node-exporter:9100');
      await page.getByPlaceholder(/type/i).selectOption({ label: 'Prometheus' });
      await page.locator('button:has-text("Save & Test")').click();
      
      await page.waitForTimeout(5000);
      console.log('✅ NodeExporter 数据源已添加');
    }
    
    await page.goto('http://localhost:3000/datasources');
    await page.waitForLoadState('networkidle');
  });

  test('创建 Dashboard', async ({ page }) => {
    console.log('创建 MyStocks Monitoring Dashboard...');
    
    // 点击 New Dashboard
    await page.goto('http://localhost:3000');
    await page.waitForLoadState('networkidle');
    
    await page.locator('button:has-text("New dashboard")').click();
    await page.waitForLoadState('networkidle');
    
    // 添加面板 1: 系统状态
    console.log('添加系统状态面板...');
    await page.locator('button[aria-label="Add panel"]').first().click();
    await page.waitForTimeout(2000);
    
    await page.getByPlaceholder(/title/i).fill('System Status');
    await page.getByRole('option').filter({ hasText: 'Stat' }).click();
    await page.getByPlaceholder(/select data source/i).selectOption({ label: 'Prometheus' });
    await page.getByPlaceholder(/query/i).fill('up');
    await page.locator('button:has-text("Apply")').click();
    await page.waitForTimeout(1000);
    
    // 添加面板 2: API 延迟
    console.log('添加 API 延迟面板...');
    await page.locator('button[aria-label="Add panel"]').nth(1).click();
    await page.waitForTimeout(2000);
    
    await page.getByPlaceholder(/title/i).fill('API Latency (P95)');
    await page.getByRole('option').filter({ hasText: 'Time series' }).click();
    await page.getByPlaceholder(/select data source/i).selectOption({ label: 'Prometheus' });
    await page.getByPlaceholder(/query/i).fill('histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))');
    await page.locator('input[placeholder="Unit"]').fill('s(秒)');
    await page.locator('button:has-text("Apply")').click();
    await page.waitForTimeout(1000);
    
    // 添加面板 3: CPU 使用率
    console.log('添加 CPU 使用率面板...');
    await page.locator('button[aria-label="Add panel"]').nth(2).click();
    await page.waitForTimeout(2000);
    
    await page.getByPlaceholder(/title/i).fill('CPU Usage');
    await page.getByRole('option').filter({ hasText: 'Gauge' }).click();
    await page.getByPlaceholder(/select data source/i).selectOption({ label: 'Prometheus' });
    await page.getByPlaceholder(/query/i).fill('100 * (1 - avg(rate(process_cpu_seconds_total[5m])))');
    await page.locator('input[placeholder="Min"]').fill('0');
    await page.locator('input[placeholder="Max"]').fill('100');
    await page.locator('input[placeholder="Unit"]').fill('percent(0-100)');
    
    // 设置阈值
    await page.locator('.panel-options-section').locator('.thresholds-row .thresholds .thresholds .input').first().fill('80');
    await page.locator('.panel-options-section').locator('.thresholds-row .thresholds .input').nth(1).fill('90');
    
    await page.locator('button:has-text("Apply")').click();
    await page.waitForTimeout(1000);
    
    // 添加面板 4: 内存使用
    console.log('添加内存使用面板...');
    await page.locator('button[aria-label="Add panel"]').nth(3).click();
    await page.waitForTimeout(2000);
    
    await page.getByPlaceholder(/title/i).fill('Memory Usage');
    await page.getByRole('option').filter({ hasText: 'Gauge' }).click();
    await page.getByPlaceholder(/select data source/i).selectOption({ label: 'Prometheus' });
    await page.getByPlaceholder(/query/i).fill('process_resident_memory_bytes / 1024 / 1024 / 1024');
    await page.locator('input[placeholder="Min"]').fill('0');
    await page.locator('input[placeholder="Max"]').fill('16');
    await page.locator('input[placeholder="Unit"]').fill('GB(GB)');
    
    // 设置阈值
    await page.locator('.panel-options-section').locator('.thresholds-row .thresholds .input').first().fill('12');
    await page.locator('.panel-options-section').locator('.thresholds-row .thresholds .input').nth(1).fill('14');
    
    await page.locator('button:has-text("Apply")').click();
    await page.waitForTimeout(1000);
    
    // 保存 Dashboard
    console.log('保存 Dashboard...');
    await page.locator('button:has-text("Save dashboard")').click();
    await page.waitForTimeout(2000);
    await page.getByPlaceholder(/name/i).fill('MyStocks Monitoring');
    await page.getByRole('option').filter({ hasText: 'General' }).click();
    await page.locator('button:has-text("Save")').click();
    await page.waitForTimeout(3000);
    
    console.log('✅ Dashboard 创建成功');
  });

  test('等待并截图', async ({ page }) => {
    console.log('等待并截图...');
    await page.waitForTimeout(5000);
    await page.screenshot({ path: 'playwright-tests/grafana/grafana-setup.png', fullPage: true });
    console.log('✅ 已保存截图');
  });
});
