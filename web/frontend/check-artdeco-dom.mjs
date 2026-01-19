import { chromium } from 'playwright';

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();

  try {
    await page.goto('http://localhost:3001/#/dashboard', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    const domStructure = await page.evaluate(() => {
      const app = document.querySelector('#app');

      // Find all ArtDeco-specific classes
      const artdecoElements = {
        artdecoDashboard: !!app.querySelector('.artdeco-dashboard'),
        artdecoHeader: !!app.querySelector('.artdeco-header'),
        artdecoSidebar: !!app.querySelector('.artdeco-sidebar'),
        artdecoContent: !!app.querySelector('.artdeco-content'),
        baseLayout: !!app.querySelector('.base-layout'),
        layoutSidebar: !!app.querySelector('.layout-sidebar'),
        layoutHeader: !!app.querySelector('.layout-header'),
      };

      // Get actual structure
      const structure = [];
      let current = app.firstElementChild;
      let depth = 0;
      while (current && depth < 5) {
        structure.push({
          tag: current.tagName,
          classes: current.className,
          id: current.id
        });
        current = current.firstElementChild;
        depth++;
      }

      return { artdecoElements, structure };
    });

    console.log('[ARTDECO DOM CHECK]');
    console.log(JSON.stringify(domStructure.artdecoElements, null, 2));
    console.log('');
    console.log('[STRUCTURE]');
    domStructure.structure.forEach(item => {
      const className = item.classes || '(no class)';
      console.log('  ' + item.tag + ': ' + className);
    });

  } finally {
    await browser.close();
  }
})();
