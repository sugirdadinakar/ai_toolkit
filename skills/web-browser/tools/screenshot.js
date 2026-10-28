#!/usr/bin/env node
"use strict";
/**
 * screenshot.js — capture the active tab's viewport to a temp PNG.
 * Prints the file path. Zero-dependency. Node >= 21.
 */

const http = require("http");
const fs = require("fs");
const os = require("os");
const path = require("path");

const PORT = 9222;

function httpGet(p) {
  return new Promise((resolve, reject) => {
    http
      .get({ host: "127.0.0.1", port: PORT, path: p }, (res) => {
        let data = "";
        res.on("data", (c) => (data += c));
        res.on("end", () => resolve(data));
      })
      .on("error", reject);
  });
}

async function activePage() {
  const targets = JSON.parse(await httpGet("/json"));
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
  const page = await activePage();
  const client = cdp(page.webSocketDebuggerUrl);
  await client.ready;
  const { data } = await client.send("Page.captureScreenshot", { format: "png" });
  client.close();

  const out = path.join(os.tmpdir(), `web-browser-shot-${Date.now()}.png`);
  fs.writeFileSync(out, Buffer.from(data, "base64"));
  console.log(out);
}

main().catch((e) => {
  console.error("Error:", e.message);
  process.exit(1);
});
