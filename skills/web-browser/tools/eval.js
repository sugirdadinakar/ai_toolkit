#!/usr/bin/env node
"use strict";
/**
 * eval.js — evaluate JavaScript in the active tab.
 *
 *   ./tools/eval.js 'document.title'
 *   ./tools/eval.js 'document.querySelectorAll("a").length'
 *
 * Connects to Chrome on :9222 via puppeteer-core. Run `npm install` first.
 * The expression runs in page context; a returned promise is awaited.
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
      /* skip non-evaluable targets */
    }
  }
  return pages[pages.length - 1];
}

async function main() {
  const expr = process.argv[2];
  if (!expr) {
    console.error("Usage: ./tools/eval.js '<javascript expression>'");
    process.exit(1);
  }

  const browser = await puppeteer.connect({ browserURL: BROWSER_URL, defaultViewport: null });
  try {
    const page = await activePage(browser);
    // Evaluate as an expression; puppeteer awaits a returned promise and
    // serializes the result.
    const result = await page.evaluate(`(async () => (${expr}))()`);
    if (result === undefined) {
      console.log("undefined");
    } else if (typeof result === "object") {
      console.log(JSON.stringify(result, null, 2));
    } else {
      console.log(result);
    }
  } finally {
    browser.disconnect();
  }
}

main().catch((e) => {
  console.error("Error:", e.message);
  process.exit(1);
});
