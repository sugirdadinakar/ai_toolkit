"use strict";
/**
 * html2pptx — convert an HTML slide to a PptxGenJS slide with accurate positioning.
 *
 * Usage:
 *   const pptxgen = require("pptxgenjs");
 *   const { html2pptx } = require("html2pptx");
 *   const pptx = new pptxgen();
 *   pptx.defineLayout({ name: "16x9", width: 10, height: 5.625 });
 *   pptx.layout = "16x9";
 *   const { slide, placeholders } = await html2pptx("slide1.html", pptx, { widthPt: 720, heightPt: 405 });
 *   // add charts/tables into `placeholders` (keyed by element id / class)
 *   await pptx.writeFile({ fileName: "out.pptx" });
 *
 * Approach: render the HTML in headless Chromium (Playwright), measure every
 * text element's bounding box in CSS px, convert px -> points using the slide's
 * point dimensions, and emit matching PptxGenJS text boxes. Elements marked
 * class="placeholder" are returned (not drawn) so the caller can drop native
 * charts/tables into those rectangles.
 *
 * Requires peer deps: playwright, pptxgenjs.
 */

const { chromium } = require("playwright");

const PT_PER_IN = 72;

function pxToPt(px, pxPerPt) {
  return +(px / pxPerPt).toFixed(2);
}

const TEXT_TAGS = new Set([
  "P", "H1", "H2", "H3", "H4", "H5", "H6", "LI", "SPAN", "BLOCKQUOTE", "FIGCAPTION",
]);

const ALIGN_MAP = { left: "left", center: "center", right: "right", justify: "justify" };

async function extractBoxes(page) {
  return page.evaluate(() => {
    const px = (v) => parseFloat(v) || 0;
    const out = { width: document.body.scrollWidth, height: document.body.scrollHeight, texts: [], placeholders: [], images: [] };
    const walk = (el) => {
      const cs = getComputedStyle(el);
      if (cs.display === "none" || cs.visibility === "hidden") return;
      const rect = el.getBoundingClientRect();

      if (el.classList.contains("placeholder")) {
        out.placeholders.push({
          id: el.id || null,
          cls: [...el.classList].filter((c) => c !== "placeholder"),
          x: rect.left, y: rect.top, w: rect.width, h: rect.height,
        });
        return; // don't descend into placeholders
      }

      if (el.tagName === "IMG") {
        out.images.push({ src: el.src, x: rect.left, y: rect.top, w: rect.width, h: rect.height });
        return;
      }

      const tag = el.tagName;
      const directText = [...el.childNodes]
        .filter((n) => n.nodeType === 3)
        .map((n) => n.textContent)
        .join("")
        .trim();

      if (["P","H1","H2","H3","H4","H5","H6","LI","BLOCKQUOTE","FIGCAPTION"].includes(tag) && directText) {
        out.texts.push({
          text: el.innerText.trim(),
          x: rect.left, y: rect.top, w: rect.width, h: rect.height,
          fontSizePx: px(cs.fontSize),
          fontFamily: cs.fontFamily.split(",")[0].replace(/["']/g, "").trim(),
          bold: px(cs.fontWeight) >= 600 || cs.fontWeight === "bold",
          italic: cs.fontStyle === "italic",
          underline: cs.textDecorationLine.includes("underline"),
          color: cs.color,
          align: cs.textAlign,
          bullet: tag === "LI",
        });
        return; // leaf text captured
      }
      for (const child of el.children) walk(child);
    };
    walk(document.body);
    return out;
  });
}

function rgbToHex(rgb) {
  const m = rgb && rgb.match(/\d+/g);
  if (!m) return "000000";
  return m.slice(0, 3).map((n) => (+n).toString(16).padStart(2, "0")).join("").toUpperCase();
}

/**
 * @param {string} htmlPath  path to the slide HTML file
 * @param {object} pptx      a PptxGenJS instance
 * @param {object} opts      { widthPt=720, heightPt=405, slide? }
 * @returns {Promise<{slide, placeholders: object, images: array}>}
 */
async function html2pptx(htmlPath, pptx, opts = {}) {
  const widthPt = opts.widthPt || 720;
  const heightPt = opts.heightPt || 405;

  const browser = await chromium.launch();
  try {
    const page = await browser.newPage({ viewport: { width: Math.round(widthPt * 1.333), height: Math.round(heightPt * 1.333) } });
    const url = "file://" + require("path").resolve(htmlPath);
    await page.goto(url, { waitUntil: "networkidle" });
    const data = await extractBoxes(page);

    // px -> pt scale from the rendered page width mapping onto the slide width.
    const pxPerPt = data.width / widthPt;

    const slide = opts.slide || pptx.addSlide();

    for (const img of data.images) {
      slide.addImage({
        path: img.src.replace("file://", ""),
        x: pxToPt(img.x, pxPerPt) / PT_PER_IN,
        y: pxToPt(img.y, pxPerPt) / PT_PER_IN,
        w: pxToPt(img.w, pxPerPt) / PT_PER_IN,
        h: pxToPt(img.h, pxPerPt) / PT_PER_IN,
      });
    }

    for (const t of data.texts) {
      slide.addText(t.bullet ? [{ text: t.text, options: { bullet: true } }] : t.text, {
        x: pxToPt(t.x, pxPerPt) / PT_PER_IN,
        y: pxToPt(t.y, pxPerPt) / PT_PER_IN,
        w: pxToPt(t.w, pxPerPt) / PT_PER_IN,
        h: pxToPt(t.h, pxPerPt) / PT_PER_IN,
        fontSize: +(t.fontSizePx / pxPerPt).toFixed(1),
        fontFace: t.fontFamily,
        bold: t.bold,
        italic: t.italic,
        underline: t.underline ? { style: "sng" } : undefined,
        color: rgbToHex(t.color),
        align: ALIGN_MAP[t.align] || "left",
        valign: "top",
        margin: 0,
      });
    }

    // Placeholders returned to caller (keyed by id, else class, else index).
    const placeholders = {};
    data.placeholders.forEach((p, i) => {
      const key = p.id || p.cls[0] || `placeholder-${i}`;
      placeholders[key] = {
        x: pxToPt(p.x, pxPerPt) / PT_PER_IN,
        y: pxToPt(p.y, pxPerPt) / PT_PER_IN,
        w: pxToPt(p.w, pxPerPt) / PT_PER_IN,
        h: pxToPt(p.h, pxPerPt) / PT_PER_IN,
      };
    });

    return { slide, placeholders, images: data.images };
  } finally {
    await browser.close();
  }
}

module.exports = { html2pptx };
