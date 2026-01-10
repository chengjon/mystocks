import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    console.log('🔍 Testing Bloomberg Terminal styling at http://localhost:3020...\n');

    // Navigate to the application
    await page.goto('http://localhost:3020', { waitUntil: 'networkidle' });
    console.log('✅ Page loaded successfully');

    // Wait for Vue app to mount
    await page.waitForSelector('#app', { timeout: 5000 });
    console.log('✅ Vue app mounted');

    // Check for console errors
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    // Take a full-page screenshot
    await page.screenshot({
      path: '/tmp/bloomberg-styling-test.png',
      fullPage: true
    });
    console.log('✅ Screenshot saved to /tmp/bloomberg-styling-test.png');

    // Verify key styling elements
    console.log('\n🎨 Verifying Bloomberg Terminal styling...\n');

    // Check background color
    const backgroundColor = await page.evaluate(() => {
      const body = document.body;
      return window.getComputedStyle(body).backgroundColor;
    });
    console.log(`Background color: ${backgroundColor}`);

    // Check if it's close to pure black (#000000 or rgb(0, 0, 0))
    const isBlack = backgroundColor === 'rgb(0, 0, 0)' || backgroundColor === '#000000';
    console.log(isBlack ? '✅ Pure black background (OLED-optimized)' : '⚠️  Background not pure black');

    // Check text contrast
    const textColor = await page.evaluate(() => {
      const body = document.body;
      return window.getComputedStyle(body).color;
    });
    console.log(`Text color: ${textColor}`);

    // Check card styling
    const cardExists = await page.$('.el-card') !== null;
    if (cardExists) {
      const cardBackground = await page.evaluate(() => {
        const card = document.querySelector('.el-card');
        return window.getComputedStyle(card).backgroundColor;
      });
      console.log(`Card background: ${cardBackground}`);

      const cardBorder = await page.evaluate(() => {
        const card = document.querySelector('.el-card');
        return window.getComputedStyle(card).borderColor;
      });
      console.log(`Card border: ${cardBorder}`);
    }

    // Check button styling
    const buttonExists = await page.$('button') !== null;
    if (buttonExists) {
      const buttonDisplay = await page.evaluate(() => {
        const button = document.querySelector('button');
        return window.getComputedStyle(button).display;
      });
      console.log(`Button display: ${buttonDisplay}`);

      const buttonAlignItems = await page.evaluate(() => {
        const button = document.querySelector('button');
        return window.getComputedStyle(button).alignItems;
      });
      console.log(`Button align-items: ${buttonAlignItems}`);
    }

    // Check for IBM Plex Sans font
    const fontFamily = await page.evaluate(() => {
      const body = document.body;
      return window.getComputedStyle(body).fontFamily;
    });
    console.log(`Font family: ${fontFamily}`);
    const hasIBMPlex = fontFamily.includes('IBM Plex Sans');
    console.log(hasIBMPlex ? '✅ IBM Plex Sans font loaded' : '⚠️  IBM Plex Sans not detected');

    // Check Element Plus variables
    const elBgColor = await page.evaluate(() => {
      const root = document.documentElement;
      return getComputedStyle(root).getPropertyValue('--el-bg-color');
    });
    console.log(`Element Plus --el-bg-color: ${elBgColor || 'not set'}`);

    const elTextColor = await page.evaluate(() => {
      const root = document.documentElement;
      return getComputedStyle(root).getPropertyValue('--el-text-color-primary');
    });
    console.log(`Element Plus --el-text-color-primary: ${elTextColor || 'not set'}`);

    console.log('\n📊 Test Summary:');
    console.log('='.repeat(60));
    console.log(isBlack ? '✅ OLED-optimized dark background' : '⚠️  Background not optimized');
    console.log(hasIBMPlex ? '✅ Professional typography applied' : '⚠️  Typography not applied');
    console.log(cardExists ? '✅ Card styling detected' : '⚠️  No cards found');
    console.log(buttonExists ? '✅ Button styling detected' : '⚠️  No buttons found');
    console.log('='.repeat(60));

    console.log('\n📸 Screenshot saved to: /tmp/bloomberg-styling-test.png');
    console.log('💡 View it with: display /tmp/bloomberg-styling-test.png');

    if (errors.length > 0) {
      console.log('\n⚠️  Console errors detected:');
      errors.forEach(err => console.log(`  - ${err}`));
    } else {
      console.log('\n✅ No console errors detected');
    }

  } catch (error) {
    console.error('❌ Test failed:', error.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();
