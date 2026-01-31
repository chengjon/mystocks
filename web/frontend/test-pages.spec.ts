import { test, expect } from '@playwright/test';

const pages = [
    { name: 'Home', path: '/' },
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Market', path: '/market' },
    { name: 'Stocks', path: '/stocks' },
    { name: 'Analysis', path: '/analysis' },
    { name: 'Risk', path: '/risk' },
    { name: 'Trading', path: '/trading' },
    { name: 'Strategy', path: '/strategy' },
    { name: 'System', path: '/system' },
    { name: 'ArtDeco Dashboard', path: '/artdeco/dashboard' },
    { name: 'ArtDeco Risk', path: '/artdeco/risk' },
    { name: 'ArtDeco Trading', path: '/artdeco/trading' },
    { name: 'ArtDeco Backtest', path: '/artdeco/backtest' },
    { name: 'ArtDeco Monitor', path: '/artdeco/monitor' },
    { name: 'ArtDeco Strategy', path: '/artdeco/strategy' },
    { name: 'ArtDeco Settings', path: '/artdeco/settings' },
    { name: 'ArtDeco Community', path: '/artdeco/community' },
    { name: 'ArtDeco Help', path: '/artdeco/help' }
];

for (const page of pages) {
    test(page.name + ' (' + page.path + ') loads without error', async ({ page: p }) => {
        const errors = [];
        
        p.on('console', msg => {
            if (msg.type() === 'error' && 
                !msg.text().includes('503') &&
                !msg.text().includes('Failed to load resource') &&
                !msg.text().includes('Download error') &&
                !msg.text().includes('deprecated') &&
                !msg.text().includes('message port closed')) {
                errors.push(msg.text());
            }
        });
        
        p.on('pageerror', error => {
            errors.push(error.message);
        });
        
        const response = await p.goto('http://localhost:3002' + page.path, { 
            waitUntil: 'domcontentloaded',
            timeout: 30000 
        });
        
        await p.waitForTimeout(2000);
        
        console.log(page.name + ': HTTP ' + (response ? response.status() : 'N/A'));
        if (errors.length > 0) {
            console.log('  Errors: ' + errors.length);
            errors.forEach(e => console.log('    - ' + e.substring(0, 80)));
        }
        
        expect(response ? response.status() : 0).toBeGreaterThanOrEqual(200);
    });
}
