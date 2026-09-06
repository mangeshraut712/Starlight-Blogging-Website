/**
 * Capture live product screenshots for the README.
 * Usage: npx playwright install chromium && node scripts/capture-screenshots.mjs
 */
import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const BASE = process.env.STARLIGHT_URL
  || 'https://mangeshraut712.github.io/Starlight-Blogging-Website';
const OUT = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'docs', 'screenshots');

await mkdir(OUT, { recursive: true });

const browser = await chromium.launch({
  headless: true,
  args: ['--disable-dev-shm-usage'],
});
const page = await browser.newPage({
  viewport: { width: 1440, height: 900 },
  deviceScaleFactor: 1,
});

async function waitForApp() {
  await page.waitForLoadState('networkidle', { timeout: 45000 }).catch(() => {});
  await page.waitForSelector('.starlight-navbar, .hero-pro, .community-card, .login-card', {
    timeout: 30000,
  });
  await page.waitForTimeout(1200);
}

await page.goto(`${BASE}/`, { waitUntil: 'domcontentloaded', timeout: 60000 });
await waitForApp();
await page.waitForSelector('.hero-pro h1', { timeout: 20000 });
await page.screenshot({ path: path.join(OUT, '01-home.png'), fullPage: false });

await page.goto(`${BASE}/communities`, { waitUntil: 'domcontentloaded', timeout: 60000 });
await waitForApp();
if ((await page.locator('.community-card').count()) === 0) {
  await page.goto(`${BASE}/login`, { waitUntil: 'domcontentloaded', timeout: 60000 });
  await waitForApp();
  await page.waitForSelector('.login-card', { timeout: 20000 });
}
await page.screenshot({ path: path.join(OUT, '02-feature.png'), fullPage: false });

await browser.close();
console.log(`Saved screenshots to ${OUT}`);
