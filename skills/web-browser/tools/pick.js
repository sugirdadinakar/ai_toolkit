#!/usr/bin/env node
"use strict";
/**
 * pick.js — interactive element picker in the active tab.
 *
 *   ./tools/pick.js "Click the submit button"
 *
 * Injects an overlay: hover highlights, click selects (Cmd/Ctrl+click to
 * multi-select), Enter finishes, Esc cancels. Prints JSON of picked elements
 * ({ selector, text, tag }). Zero-dependency. Node >= 21.
 */

const http = require("http");

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

// Injected page script (stringified). Resolves with the array of picks.
function pickerSource(instruction) {
  return `(async () => {
    if (window.__pickerActive) return [];
    window.__pickerActive = true;
    const INSTRUCTION = ${JSON.stringify(instruction)};
    return await new Promise((resolve) => {
      const selected = new Map(); // el -> true
      const box = document.createElement('div');
      box.style.cssText = 'position:fixed;z-index:2147483647;border:2px solid #675DF4;background:rgba(103,93,244,0.12);pointer-events:none;transition:all .03s;';
      const banner = document.createElement('div');
      banner.style.cssText = 'position:fixed;top:0;left:0;right:0;z-index:2147483647;background:#1F2533;color:#fff;font:13px system-ui;padding:8px 12px;';
      banner.textContent = INSTRUCTION + '  —  click to select, Cmd/Ctrl+click to multi-select, Enter to finish, Esc to cancel';
      document.documentElement.append(box, banner);

      function cssPath(el) {
        if (el.id) return '#' + CSS.escape(el.id);
        const parts = [];
        while (el && el.nodeType === 1 && el !== document.body) {
          let sel = el.nodeName.toLowerCase();
          const parent = el.parentNode;
          if (parent) {
            const sames = Array.from(parent.children).filter(c => c.nodeName === el.nodeName);
            if (sames.length > 1) sel += ':nth-of-type(' + (sames.indexOf(el) + 1) + ')';
          }
          parts.unshift(sel);
          el = el.parentElement;
        }
        return parts.join(' > ');
      }
      function mark(el, on) {
        el.style.outline = on ? '2px solid #00875A' : '';
      }
      function onMove(e) {
        const el = e.target;
        if (!el || el === banner) return;
        const r = el.getBoundingClientRect();
        box.style.top = r.top + 'px'; box.style.left = r.left + 'px';
        box.style.width = r.width + 'px'; box.style.height = r.height + 'px';
      }
      function onClick(e) {
        e.preventDefault(); e.stopPropagation();
        const el = e.target;
        if (el === banner) return;
        if (e.metaKey || e.ctrlKey) {
          if (selected.has(el)) { selected.delete(el); mark(el, false); }
          else { selected.set(el, true); mark(el, true); }
        } else {
          selected.forEach((_, k) => mark(k, false));
          selected.clear();
          selected.set(el, true); mark(el, true);
        }
      }
      function finish(cancelled) {
        document.removeEventListener('mousemove', onMove, true);
        document.removeEventListener('click', onClick, true);
        document.removeEventListener('keydown', onKey, true);
        box.remove(); banner.remove();
        selected.forEach((_, k) => mark(k, false));
        window.__pickerActive = false;
        if (cancelled) { resolve([]); return; }
        resolve(Array.from(selected.keys()).map(el => ({
          selector: cssPath(el),
          tag: el.nodeName.toLowerCase(),
          text: (el.textContent || '').trim().slice(0, 120),
        })));
      }
      function onKey(e) {
        if (e.key === 'Enter') { e.preventDefault(); finish(false); }
        else if (e.key === 'Escape') { e.preventDefault(); finish(true); }
      }
      document.addEventListener('mousemove', onMove, true);
      document.addEventListener('click', onClick, true);
      document.addEventListener('keydown', onKey, true);
    });
  })()`;
}

async function main() {
  const instruction = process.argv.slice(2).join(" ") || "Select element(s)";
  const page = await activePage();
  const client = cdp(page.webSocketDebuggerUrl);
  await client.ready;

  console.error(`Picker active in the browser: ${instruction}`);
  console.error("Click to select, Cmd/Ctrl+click to multi-select, Enter to finish, Esc to cancel.");

  const result = await client.send("Runtime.evaluate", {
    expression: pickerSource(instruction),
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
  console.log(JSON.stringify(result.result.value || [], null, 2));
}

main().catch((e) => {
  console.error("Error:", e.message);
  process.exit(1);
});
