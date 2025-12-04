/**
 * UI Tests for if.emotion using Puppeteer
 * Tests the Settings modal, Export modal, and general UI functionality
 */

const puppeteer = require('puppeteer');

const TEST_URL = 'http://85.239.243.227';

async function runTests() {
  console.log('Starting browser tests...\n');

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  let passed = 0;
  let failed = 0;

  async function test(name, fn) {
    try {
      await fn();
      console.log(`PASS: ${name}`);
      passed++;
    } catch (err) {
      console.log(`FAIL: ${name}`);
      console.log(`  Error: ${err.message}`);
      failed++;
    }
  }

  // Navigate to site
  await page.goto(TEST_URL, { waitUntil: 'networkidle2', timeout: 30000 });

  // Clear localStorage to get fresh state
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: 'networkidle2' });

  // Test 1: Page loads without errors
  await test('Page loads successfully', async () => {
    const title = await page.title();
    if (!title.includes('if.emotion')) {
      throw new Error(`Expected title to contain 'if.emotion', got '${title}'`);
    }
  });

  // Test 2: Header renders with title
  await test('Header renders with if.emotion title', async () => {
    await page.waitForSelector('h1', { timeout: 5000 });
    const headerText = await page.$eval('h1', el => el.textContent);
    if (!headerText.includes('if.emotion')) {
      throw new Error(`Header text was '${headerText}'`);
    }
  });

  // Test 3: Settings button exists
  await test('Settings button exists', async () => {
    const settingsBtn = await page.$('button[title="Settings"]');
    if (!settingsBtn) {
      throw new Error('Settings button not found');
    }
  });

  // Test 4: Export button exists
  await test('Export button exists', async () => {
    const exportBtn = await page.$('button[title="Export conversation"]');
    if (!exportBtn) {
      throw new Error('Export button not found');
    }
  });

  // Test 5: Settings modal opens and shows Personality DNA toggle
  await test('Settings modal opens with Personality DNA toggle', async () => {
    await page.click('button[title="Settings"]');
    await page.waitForSelector('.fixed.inset-0', { timeout: 3000 });

    const dnaText = await page.evaluate(() => {
      return document.body.innerText.includes('Personality DNA');
    });

    if (!dnaText) {
      throw new Error('Personality DNA text not found in modal');
    }

    // Close modal
    const closeBtn = await page.$('.fixed.inset-0 button');
    if (closeBtn) await closeBtn.click();
    await page.waitForTimeout(300);
  });

  // Test 6: Export modal opens
  await test('Export modal opens with format options', async () => {
    await page.click('button[title="Export conversation"]');
    await page.waitForSelector('.fixed.inset-0', { timeout: 3000 });

    const exportText = await page.evaluate(() => {
      return document.body.innerText.includes('Export Conversation');
    });

    if (!exportText) {
      throw new Error('Export Conversation text not found in modal');
    }

    const pdfOption = await page.evaluate(() => {
      return document.body.innerText.includes('PDF');
    });

    if (!pdfOption) {
      throw new Error('PDF option not found in export modal');
    }

    const mdOption = await page.evaluate(() => {
      return document.body.innerText.includes('Markdown');
    });

    if (!mdOption) {
      throw new Error('Markdown option not found in export modal');
    }

    // Close modal
    const closeBtn = await page.$('.fixed.inset-0 button');
    if (closeBtn) await closeBtn.click();
    await page.waitForTimeout(300);
  });

  // Test 7: Chat input exists
  await test('Chat input exists and is functional', async () => {
    const input = await page.$('textarea, input[type="text"]');
    if (!input) {
      throw new Error('Chat input not found');
    }
  });

  // Test 8: No JavaScript errors
  const jsErrors = [];
  page.on('pageerror', err => jsErrors.push(err.message));

  await test('No critical JavaScript errors on page load', async () => {
    await page.reload({ waitUntil: 'networkidle2' });
    await page.waitForTimeout(1000);

    const criticalErrors = jsErrors.filter(e =>
      !e.includes('ResizeObserver') &&
      !e.includes('Non-Error promise rejection')
    );

    if (criticalErrors.length > 0) {
      throw new Error(`JS errors: ${criticalErrors.join(', ')}`);
    }
  });

  await browser.close();

  // Summary
  console.log('\n' + '='.repeat(50));
  console.log(`Results: ${passed} passed, ${failed} failed`);
  console.log('='.repeat(50));

  process.exit(failed > 0 ? 1 : 0);
}

runTests().catch(err => {
  console.error('Test runner error:', err);
  process.exit(1);
});
