#!/usr/bin/env node

/**
 * Simple page error checker using Puppeteer
 */

import puppeteer from 'puppeteer';

async function checkPage() {
  const browser = await puppeteer.launch({
    headless: false,
    args: ['--no-sandbox']
  });

  const page = await browser.newPage();

  // Capture console messages
  const consoleMessages = [];
  page.on('console', (msg) => {
    consoleMessages.push({
      type: msg.type(),
      text: msg.text()
    });
    console.log(`[${msg.type()}]`, msg.text());
  });

  // Capture page errors
  const pageErrors = [];
  page.on('pageerror', (error) => {
    pageErrors.push(error.toString());
    console.error('Page Error:', error.toString());
  });

  // Capture request failures
  const requestFailures = [];
  page.on('requestfailed', (request) => {
    requestFailures.push({
      url: request.url(),
      failure: request.failure().errorText
    });
    console.error('Request Failed:', request.url(), request.failure().errorText);
  });

  try {
    console.log('Navigating to http://localhost:3001');
    await page.goto('http://localhost:3001', {
      waitUntil: 'networkidle2',
      timeout: 10000
    });

    // Wait a bit more for JS to execute
    await page.waitForTimeout(3000);

    // Get page content
    const content = await page.evaluate(() => {
      return {
        title: document.title,
        appHTML: document.querySelector('#app')?.innerHTML || '',
        bodyHTML: document.body.innerHTML.substring(0, 500)
      };
    });

    console.log('\n=== Page Content ===');
    console.log('Title:', content.title);
    console.log('#app inner HTML length:', content.appHTML.length);
    console.log('Body HTML preview:', content.bodyHTML.substring(0, 200));

    // Take screenshot
    await page.screenshot({ path: 'page-state.png' });
    console.log('\nScreenshot saved to page-state.png');

  } catch (error) {
    console.error('Error during page load:', error);
  }

  console.log('\n=== Summary ===');
  console.log('Total console messages:', consoleMessages.length);
  console.log('Total page errors:', pageErrors.length);
  console.log('Total request failures:', requestFailures.length);

  if (pageErrors.length > 0) {
    console.log('\n=== Page Errors ===');
    pageErrors.forEach((err, i) => console.log(`  ${i + 1}. ${err}`));
  }

  if (requestFailures.length > 0) {
    console.log('\n=== Request Failures ===');
    requestFailures.forEach((fail, i) => console.log(`  ${i + 1}. ${fail.url}: ${fail.failure}`));
  }

  await browser.close();
}

checkPage().catch(console.error);
