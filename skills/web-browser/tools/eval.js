#!/usr/bin/env node
"use strict";
/**
 * eval.js — evaluate JavaScript in the active tab (async context).
 *
 *   ./tools/eval.js 'document.title'
 *   ./tools/eval.js 'document.querySelectorAll("a").length'
 *
 * Prints the returned value (JSON for objects). Zero-dependency. Node >= 21.
 */

const http = require("http");

const PORT = 9222;

function httpGet(path) {
  return new Promise((resolve, reject) => {
    http
      .get({ host: "127.0.0.1", port: PORT, path }, (res) => {
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
  const expr = process.argv[2];
  if (!expr) {
    console.error("Usage: ./tools/eval.js '<javascript expression>'");
    process.exit(1);
  }

  const page = await activePage();
  const client = cdp(page.webSocketDebuggerUrl);
  await client.ready;

  // Wrap in an async IIFE so `await` works and the expression's value is returned.
  const wrapped = `(async () => { return (${expr}); })()`;
  const result = await client.send("Runtime.evaluate", {
    expression: wrapped,
    awaitPromise: true,
    returnByValue: true,
    userGesture: true,
  });
  client.close();

  if (result.exceptionDetails) {
    const ex = result.exceptionDetails;
    console.error("Error:", (ex.exception && ex.exception.description) || ex.text);
    process.exit(1);
  }

  const v = result.result && result.result.value;
  if (v === undefined) {
    console.log(result.result ? result.result.type : "undefined");
  } else if (typeof v === "object") {
    console.log(JSON.stringify(v, null, 2));
  } else {
    console.log(v);
  }
}

main().catch((e) => {
  console.error("Error:", e.message);
  process.exit(1);
});
