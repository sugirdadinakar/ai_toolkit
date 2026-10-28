#!/usr/bin/env node
"use strict";
/**
 * start.js — launch Chrome/Chromium with remote debugging on :9222.
 *
 *   ./tools/start.js             # fresh, isolated profile
 *   ./tools/start.js --profile   # copy your real profile (cookies, logins)
 *
 * Launches Chrome so the other puppeteer-core tools can connect on :9222.
 * (This launcher itself only needs Node built-ins.)
 */

const { spawn } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const PORT = 9222;

function findChrome() {
  if (process.env.CHROME_PATH && fs.existsSync(process.env.CHROME_PATH)) {
    return process.env.CHROME_PATH;
  }
  const plat = process.platform;
  const candidates =
    plat === "darwin"
      ? [
          "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
          "/Applications/Chromium.app/Contents/MacOS/Chromium",
          "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
        ]
      : plat === "win32"
      ? [
          path.join(process.env["PROGRAMFILES"] || "C:\\Program Files", "Google/Chrome/Application/chrome.exe"),
          path.join(process.env["PROGRAMFILES(X86)"] || "C:\\Program Files (x86)", "Google/Chrome/Application/chrome.exe"),
        ]
      : [
          "/usr/bin/google-chrome",
          "/usr/bin/google-chrome-stable",
          "/usr/bin/chromium-browser",
          "/usr/bin/chromium",
        ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return null;
}

function defaultProfileDir() {
  const home = os.homedir();
  if (process.platform === "darwin") return path.join(home, "Library/Application Support/Google/Chrome");
  if (process.platform === "win32") return path.join(process.env.LOCALAPPDATA || "", "Google/Chrome/User Data");
  return path.join(home, ".config/google-chrome");
}

function main() {
  const useProfile = process.argv.includes("--profile");
  const chrome = findChrome();
  if (!chrome) {
    console.error("Could not find Chrome/Chromium. Set CHROME_PATH to the binary.");
    process.exit(1);
  }

  let userDataDir = path.join(os.tmpdir(), "web-browser-skill-profile");
  if (useProfile) {
    const src = defaultProfileDir();
    userDataDir = path.join(os.tmpdir(), "web-browser-skill-profile-copy");
    if (fs.existsSync(src)) {
      console.error(`Copying profile from ${src} ... (first run can be slow)`);
      fs.rmSync(userDataDir, { recursive: true, force: true });
      try {
        fs.cpSync(src, userDataDir, { recursive: true, errorOnExist: false, force: true });
      } catch (e) {
        console.error(`Warning: profile copy incomplete (${e.message}); continuing.`);
      }
    } else {
      console.error(`No profile found at ${src}; starting with a fresh profile.`);
    }
  }
  fs.mkdirSync(userDataDir, { recursive: true });

  const args = [
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${userDataDir}`,
    "--no-first-run",
    "--no-default-browser-check",
    "--remote-allow-origins=*",
  ];

  const child = spawn(chrome, args, { detached: true, stdio: "ignore" });
  child.unref();

  console.log(`Chrome launched on http://127.0.0.1:${PORT}`);
  console.log(`Profile: ${userDataDir}`);
  console.log(`Targets: http://127.0.0.1:${PORT}/json`);
}

main();
