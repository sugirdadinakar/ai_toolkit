#!/usr/bin/env node
"use strict";
/**
 * screenshot.js — capture the active tab's viewport to a temp PNG.
 * Prints the file path. Connects to Chrome on :9222 via puppeteer-core.
 */

const puppeteer = require("puppeteer-core");
const os = require("os");
const path = require("path");

const BROWSER_URL = "http://127.0.0.1:9222";

async function activePage(browser) {
  const pages = await browser.pages();
  if (!pages.length) throw new Error("No open page. Run ./tools/start.js first.");
  for (const p of pages) {
    try {
      if (await p.evaluate(() => document.visibilityState === "visible")) return p;
    } catch {
      /* skip */
    }
  }
  return pages[pages.length - 1];
}

async function main() {
  const browser = await puppeteer.connect({ browserURL: BROWSER_URL, defaultViewport: null });
  try {
    const page = await activePage(browser);
    const out = path.join(os.tmpdir(), `web-browser-shot-${Date.now()}.png`);
    await page.screenshot({ path: out, type: "png" });
    console.log(out);
  } finally {
    browser.disconnect();
  }
}

main().catch((e) => {
  console.error("Error:", e.message);
  process.exit(1);
});
