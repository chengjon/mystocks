const { chromium } = require('@playwright/test');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    
    page.on('console', msg => {
        if (msg.type() === 'error' && 
            !msg.text().includes('contracts') &&
            !msg.text().includes('Failed to load resource')) {
            console.log('JS Error:', msg.text().substring(0, 200));
        }
    });
    
    // Navigate to login page
    console.log('Navigating to login page...');
    await page.goto('http://localhost:3002/login?redirect=/dashboard', { waitUntil: 'networkidle' });
    await page.waitForTimeout(3000);
    
    // Check page content
    const title = await page.textContent('h1.title, h1');
    console.log('Page title:', title);
    
    // Fill login form
    console.log('\nFilling login form...');
    
    // Find username input
    const usernameInput = await page.$('input[placeholder*="USERNAME"], input[data-testid="username-input"], input[type="text"]');
    if (usernameInput) {
        await usernameInput.fill('admin');
        console.log('Username entered');
    } else {
        console.log('Username input not found');
    }
    
    // Find password input
    const passwordInput = await page.$('input[placeholder*="PASSWORD"], input[data-testid="password-input"], input[type="password"]');
    if (passwordInput) {
        await passwordInput.fill('admin123');
        console.log('Password entered');
    } else {
        console.log('Password input not found');
    }
    
    // Find and click login button
    console.log('\nClicking login button...');
    const loginButton = await page.$('button[type="submit"], button:has-text("LOGIN"), button.el-button--primary');
    if (loginButton) {
        await loginButton.click();
        console.log('Login button clicked');
    } else {
        console.log('Login button not found');
    }
    
    // Wait for response
    await page.waitForTimeout(5000);
    
    // Check current URL
    const url = page.url();
    console.log('\nCurrent URL:', url);
    
    // Check for error message
    const errorText = await page.textContent('.el-message--error, .el-message__content, [role="alert"]');
    console.log('Error message:', errorText || 'None');
    
    // Check for success message
    const successText = await page.textContent('.el-message--success, .el-message__content');
    console.log('Success message:', successText || 'None');
    
    await browser.close();
})();
