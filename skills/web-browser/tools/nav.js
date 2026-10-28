#!/usr/bin/env node
"use strict";
/**
 * nav.js — navigate the active tab, or open a new one.
 *
 *   ./tools/nav.js https://example.com
 *   ./tools/nav.js https://example.com --new
 *
 * Zero-dependency (Node built-ins only). Node >= 21.
 */

const http = require("http");

const PORT = 9222;

function httpReq(method, path) {
  return new Promise((resolve, reject) => {
    const req = http.request({ host: "127.0.0.1", port: PORT, path, method }, (res) => {
      let data = "";
      res.on("data", (c) => (data += c));
      res.on("end", () => resolve(data));
    });
    req.on("error", reject);
    req.end();
  });
}

async function activePage() {
  const targets = JSON.parse(await httpReq("GET", "/json"));
  const pages = targets.filter((t) => t.type === "page" && t.webSocketDebuggerUrl);
  if (!pages.length) throw new Error("No open page. Run ./tools/start.js first.");
  return pages[0];
}

function cdp(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 0;
  const pending = new Map();
  const ready = new Promise((res, rej) => {
    ws.addEventListener("open", () => res());
    ws.addEventListener("error", () => rej(new Error("WebSocket error connecting to Chrome")));
  });
  ws.addEventListener("message", (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.id && pending.has(msg.id)) {
      const { res, rej } = pending.get(msg.id);
      pending.delete(msg.id);
      msg.error ? rej(new Error(msg.error.message)) : res(msg.result);
    }
  });
  return {
    ready,
    send: (method, params = {}) =>
      new Promise((res, rej) => {
        const mid = ++id;
        pending.set(mid, { res, rej });
        ws.send(JSON.stringify({ id: mid, method, params }));
      }),
    close: () => ws.close(),
  };
}

async function main() {
  const url = process.argv[2];
  const asNew = process.argv.includes("--new");
  if (!url || url.startsWith("--")) {
    console.error("Usage: ./tools/nav.js <url> [--new]");
    process.exit(1);
  }

  if (asNew) {
    // Newer Chrome requires PUT for /json/new.
    const out = await httpReq("PUT", "/json/new?" + encodeURIComponent(url));
    try {
      const t = JSON.parse(out);
      console.log(`Opened new tab: ${t.url || url} (${t.id || ""})`);
    } catch {
      console.log(`Opened new tab: ${url}`);
    }
    return;
  }

  const page = await activePage();
  const client = cdp(page.webSocketDebuggerUrl);
  await client.ready;
  await client.send("Page.enable");
  await client.send("Page.navigate", { url });
  console.log(`Navigated active tab to ${url}`);
  client.close();
}

main().catch((e) => {
  console.error("Error:", e.message);
  process.exit(1);
});
