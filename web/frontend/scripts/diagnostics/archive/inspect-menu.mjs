import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    await page.goto('http://localhost:3001/#/dashboard', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    // Get all sidebar links
    const links = await page.evaluate(() => {
      const sidebar = document.querySelector('.layout-sidebar');
      if (!sidebar) return [];

      const links = Array.from(sidebar.querySelectorAll('a, [role="menuitem"], button'));
      return links.map(link => ({
        tag: link.tagName,
        text: link.textContent?.trim().substring(0, 50),
        class: link.className,
        href: link.getAttribute('href')
      }));
    });

    console.log('[SIDEBAR LINKS] Total:', links.length);
    links.slice(0, 15).forEach((link, i) => {
      const className = link.class ? link.class.substring(0, 30) : 'no-class';
      console.log('  [' + i + '] ' + link.tag + ': "' + link.text + '" (class: ' + className + ')');
    });

  } finally {
    await browser.close();
  }
})();
