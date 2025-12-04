#!/usr/bin/env node
/**
 * if.emotion E2E Test Suite
 * Tests all UI features with screenshots
 */

const puppeteer = require('puppeteer');
const path = require('path');

const SCREENSHOTS_DIR = '/mnt/c/users/setup/pictures/screencaptures';
const BASE_URL = 'http://85.239.243.227';

async function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function takeScreenshot(page, name) {
    const filepath = path.join(SCREENSHOTS_DIR, `if-emotion-${name}-${Date.now()}.png`);
    await page.screenshot({ path: filepath, fullPage: true });
    console.log(`Screenshot: ${filepath}`);
    return filepath;
}

async function runTests() {
    console.log('Starting if.emotion E2E tests...\n');

    const browser = await puppeteer.launch({
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-web-security',
            '--disable-features=IsolateOrigins,site-per-process,HttpsUpgrades,AutoupgradeMixedContent',
            '--allow-running-insecure-content',
            '--disable-extensions',
            '--disable-plugins',
            '--ignore-certificate-errors',
            '--ignore-ssl-errors',
            '--disable-hsts',
            '--no-first-run',
            '--disable-background-networking',
            '--unsafely-treat-insecure-origin-as-secure=http://85.239.243.227'
        ]
    });

    const page = await browser.newPage();
    await page.setViewport({ width: 1280, height: 800 });

    // Debug: Log all requests and responses
    page.on('requestfailed', request => {
        console.log(`Request failed: ${request.url()} - ${request.failure()?.errorText}`);
    });

    page.on('console', msg => {
        console.log(`Browser console: ${msg.type()}: ${msg.text()}`);
    });

    const results = {
        passed: [],
        failed: []
    };

    try {
        // Test 1: Load the page
        console.log('TEST 1: Load main page');
        await page.goto(BASE_URL, { waitUntil: 'networkidle2', timeout: 30000 });
        await delay(2000);
        await takeScreenshot(page, '01-initial-load');
        results.passed.push('Page loads');

        // Test 2: Check header elements
        console.log('TEST 2: Verify header elements');
        const title = await page.$eval('h1', el => el.textContent).catch(() => null);
        if (title && title.includes('if.emotion')) {
            results.passed.push('Header title present');
        } else {
            results.failed.push('Header title missing');
        }

        // Test 3: Check for Settings button
        console.log('TEST 3: Check settings button');
        const settingsBtn = await page.$('button[title="Settings"]');
        if (settingsBtn) {
            results.passed.push('Settings button present');

            // Click settings and take screenshot
            await settingsBtn.click();
            await delay(500);
            await takeScreenshot(page, '02-settings-modal');

            // Close modal with Escape key
            await page.keyboard.press('Escape');
            await delay(300);
        } else {
            results.failed.push('Settings button missing');
        }

        // Test 4: Check for Export button
        console.log('TEST 4: Check export button');
        const exportBtn = await page.$('button[title="Export Journey"]');
        if (exportBtn) {
            results.passed.push('Export button present');

            await exportBtn.click();
            await delay(500);
            await takeScreenshot(page, '03-export-modal');

            // Close modal with Escape key
            await page.keyboard.press('Escape');
            await delay(300);
        } else {
            // Try finding by icon
            const exportBtnAlt = await page.evaluate(() => {
                const buttons = Array.from(document.querySelectorAll('button'));
                return buttons.find(b => b.innerHTML.includes('Download') || b.title?.includes('Export')) ? true : false;
            });
            if (exportBtnAlt) results.passed.push('Export button present (alt)');
            else results.failed.push('Export button missing');
        }

        // Test 5: Check chat input
        console.log('TEST 5: Check chat input');
        const chatInput = await page.$('textarea');
        if (chatInput) {
            results.passed.push('Chat input present');

            const placeholder = await page.$eval('textarea', el => el.placeholder);
            console.log(`  Placeholder: "${placeholder}"`);
        } else {
            results.failed.push('Chat input missing');
        }

        // Test 6: Check Privacy/Mode toggle
        console.log('TEST 6: Check Mode toggle');
        const modeToggle = await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            return buttons.find(b => b.textContent.includes('Mode') || b.textContent.includes('Normal') || b.textContent.includes('Private')) ? true : false;
        });
        if (modeToggle) {
            results.passed.push('Mode toggle present');
        } else {
            results.failed.push('Mode toggle missing');
        }

        // Test 7: Send a test message
        console.log('TEST 7: Send test message');
        if (chatInput) {
            await chatInput.type('Hello Sergio! This is a test message.');
            await takeScreenshot(page, '04-message-typed');

            // Click send button
            const sendBtn = await page.$('button[type="button"]:last-of-type');
            if (sendBtn) {
                await sendBtn.click();
                console.log('  Message sent, waiting for response...');

                // Wait for response (up to 60 seconds)
                await delay(3000);
                await takeScreenshot(page, '05-waiting-response');

                // Check for loading indicator or response
                let attempts = 0;
                while (attempts < 20) {
                    const messages = await page.$$('.max-w-4xl > div');
                    if (messages.length > 1) {
                        console.log(`  Found ${messages.length} messages`);
                        break;
                    }
                    await delay(3000);
                    attempts++;
                }

                await takeScreenshot(page, '06-after-response');
                results.passed.push('Message sent');
            }
        }

        // Test 8: Check sidebar (mobile view)
        console.log('TEST 8: Check mobile sidebar');
        await page.setViewport({ width: 375, height: 667 });
        await delay(500);
        await takeScreenshot(page, '07-mobile-view');

        const menuBtn = await page.$('button[aria-label="Open sidebar"]');
        if (menuBtn) {
            await menuBtn.click();
            await delay(500);
            await takeScreenshot(page, '08-sidebar-open');
            results.passed.push('Mobile sidebar opens');
        } else {
            results.failed.push('Mobile menu button missing');
        }

        // Test 9: Toggle privacy mode
        console.log('TEST 9: Toggle privacy mode');
        await page.setViewport({ width: 1280, height: 800 });
        await delay(500);

        // Close sidebar if open
        const overlay = await page.$('.fixed.inset-0.bg-sergio-900\\/20');
        if (overlay) await overlay.click();
        await delay(300);

        // Find and click save toggle
        const privacyToggle = await page.evaluate(() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const toggle = buttons.find(b => b.textContent.includes('SAVE'));
            if (toggle) {
                toggle.click();
                return true;
            }
            return false;
        });

        if (privacyToggle) {
            await delay(500);
            await takeScreenshot(page, '09-privacy-mode');
            results.passed.push('Privacy toggle works');
        }

        // Final screenshot
        await takeScreenshot(page, '10-final-state');

    } catch (error) {
        console.error('Test error:', error.message);
        await takeScreenshot(page, 'error-state');
        results.failed.push(`Error: ${error.message}`);
    } finally {
        await browser.close();
    }

    // Print results
    console.log('\n' + '='.repeat(50));
    console.log('TEST RESULTS');
    console.log('='.repeat(50));
    console.log(`\nPassed: ${results.passed.length}`);
    results.passed.forEach(t => console.log(`  ✓ ${t}`));
    console.log(`\nFailed: ${results.failed.length}`);
    results.failed.forEach(t => console.log(`  ✗ ${t}`));
    console.log('\n' + '='.repeat(50));

    return results;
}

runTests().catch(console.error);
