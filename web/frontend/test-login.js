const { chromium } = require('@playwright/test');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    
    const errors = [];
    page.on('console', msg => {
        if (msg.type() === 'error') {
            errors.push(msg.text());
        }
    });
    page.on('pageerror', error => {
        errors.push('Page Error: ' + error.message);
    });
    
    // Navigate to login page
    await page.goto('http://localhost:3002/login?redirect=/dashboard', { waitUntil: 'domcontentloaded' });
    await page.waitForTimeout(2000);
    
    console.log('Page loaded');
    console.log('Errors:', errors.length);
    errors.forEach(e => console.log('  - ' + e.substring(0, 100)));
    
    // Try to login
    console.log('\nAttempting login...');
    const usernameInput = await page.$('input[placeholder*="USERNAME"], input[type="text"]');
    const passwordInput = await page.$('input[type="password"]');
    
    if (usernameInput && passwordInput) {
        await usernameInput.fill('admin');
        await passwordInput.fill('admin123');
        
        const loginButton = await page.$('button[type="submit"], button:has-text("LOGIN")');
        if (loginButton) {
            await loginButton.click();
            await page.waitForTimeout(5000);
            
            const url = page.url();
            console.log('Current URL after login:', url);
            
            // Check for error messages
            const errorMsgs = await page.$$('.el-message--error, [role="alert"], .error');
            console.log('Error messages found:', errorMsgs.length);
        }
    }
    
    await browser.close();
})();
