/**
 * Screenshot tests for if.emotion UI
 */

const puppeteer = require('puppeteer');
const path = require('path');

const TEST_URL = 'http://85.239.243.227';
const SCREENSHOT_DIR = '/mnt/c/users/setup/pictures/screencaptures';

async function runTests() {
  console.log('Taking screenshots of if.emotion...\n');

  const browser = await puppeteer.launch({
    headless: true,
    executablePath: '/usr/bin/chromium-browser',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage']
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });

  try {
    // Navigate to site
    console.log('Loading site...');
    await page.goto(TEST_URL, { waitUntil: 'networkidle2', timeout: 30000 });

    // Clear localStorage and reload for fresh state
    await page.evaluate(() => localStorage.clear());
    await page.reload({ waitUntil: 'networkidle2' });
    await page.waitForTimeout(1000);

    // Screenshot 1: Main page
    const mainScreenshot = path.join(SCREENSHOT_DIR, 'if-emotion-main.png');
    await page.screenshot({ path: mainScreenshot, fullPage: false });
    console.log(`Saved: ${mainScreenshot}`);

    // Screenshot 2: Settings modal
    console.log('Opening Settings modal...');
    await page.click('button[title="Settings"]');
    await page.waitForTimeout(500);
    const settingsScreenshot = path.join(SCREENSHOT_DIR, 'if-emotion-settings.png');
    await page.screenshot({ path: settingsScreenshot, fullPage: false });
    console.log(`Saved: ${settingsScreenshot}`);

    // Close settings
    const closeBtn = await page.$('.fixed.inset-0 button');
    if (closeBtn) await closeBtn.click();
    await page.waitForTimeout(300);

    // Screenshot 3: Export modal
    console.log('Opening Export modal...');
    await page.click('button[title="Export conversation"]');
    await page.waitForTimeout(500);
    const exportScreenshot = path.join(SCREENSHOT_DIR, 'if-emotion-export.png');
    await page.screenshot({ path: exportScreenshot, fullPage: false });
    console.log(`Saved: ${exportScreenshot}`);

    console.log('\nAll screenshots saved successfully!');

  } catch (err) {
    console.error('Error:', err.message);
    // Take error screenshot
    await page.screenshot({ path: path.join(SCREENSHOT_DIR, 'if-emotion-error.png') });
  }

  await browser.close();
}

runTests().catch(err => {
  console.error('Test runner error:', err);
  process.exit(1);
});
