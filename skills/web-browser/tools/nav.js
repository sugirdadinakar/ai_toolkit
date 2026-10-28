#!/usr/bin/env node
"use strict";
/**
 * nav.js — navigate the active tab, or open a new one.
 *
 *   ./tools/nav.js https://example.com
 *   ./tools/nav.js https://example.com --new
 *
 * Connects to Chrome on :9222 via puppeteer-core. Run `npm install` first.
 */

const puppeteer = require("puppeteer-core");

const BROWSER_URL = "http://127.0.0.1:9222";

async function activePage(browser) {
  const pages = await browser.pages();
  if (!pages.length) throw new Error("No open page. Run ./tools/start.js first.");
  for (const p of pages) {
    try {
      if (await p.evaluate(() => document.visibilityState === "visible")) return p;
    } catch {
      /* page may be a devtools/extension target; skip */
    }
  }
  return pages[pages.length - 1];
}

async function main() {
  const url = process.argv[2];
  const asNew = process.argv.includes("--new");
  if (!url || url.startsWith("--")) {
    console.error("Usage: ./tools/nav.js <url> [--new]");
    process.exit(1);
  }

  const browser = await puppeteer.connect({ browserURL: BROWSER_URL, defaultViewport: null });
  try {
    const page = asNew ? await browser.newPage() : await activePage(browser);
    await page.goto(url, { waitUntil: "domcontentloaded" });
    if (asNew) await page.bringToFront();
    console.log(`${asNew ? "Opened new tab" : "Navigated active tab"}: ${url}`);
  } finally {
    browser.disconnect();
  }
}

main().catch((e) => {
  console.error("Error:", e.message);
  process.exit(1);
});
