# html2pptx — HTML → PowerPoint Reference

Companion to [SKILL.md](SKILL.md). Build new decks by writing one HTML file per slide, then converting to `.pptx` with the bundled `html2pptx` library (Playwright for measurement + PptxGenJS for output). Read this file fully before generating a deck.

## Install the library (once)
The library lives in [`html2pptx/`](./html2pptx). Install it globally along with its peers:

```bash
# Option A — install from the source folder
npm install -g ./skills/pptx/html2pptx pptxgenjs playwright
npx playwright install chromium

# Option B — build a tarball first, then install it (matches SKILL.md)
cd skills/pptx/html2pptx && npm pack        # produces html2pptx-1.0.0.tgz
npm install -g ./html2pptx-1.0.0.tgz pptxgenjs playwright
```

Run your build scripts with the global modules on the path:
```bash
NODE_PATH=$(npm root -g) node build-deck.js
```

## Slide HTML rules
- One HTML file per slide. Size the body to the slide: **720pt × 405pt** for 16:9 (use px at ~1.333×, i.e. 960×540, or set explicit pt via CSS and let the converter scale).
- Use real text tags for all copy: `<p>`, `<h1>`–`<h6>`, `<ul>/<ol><li>`. The converter captures these as positioned text boxes.
- Mark chart/table regions with `class="placeholder"` (give them a gray background so they're visible during design). The converter returns their rectangles instead of drawing them — you fill them with native PptxGenJS charts/tables.
- **Rasterize gradients and icons to PNG first** (e.g. with Sharp), then reference the PNG in an `<img>`. Native CSS gradients/icon fonts don't translate.
- Use web-safe fonts: Arial, Helvetica, Times New Roman, Georgia, Courier New, Verdana, Tahoma, Trebuchet MS, Impact.

### Minimal slide HTML
```html
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
  html,body{margin:0}
  body{width:960px;height:540px;font-family:Arial;position:relative;background:#0F2A43;color:#fff}
  h1{position:absolute;left:48px;top:60px;font-size:48px;margin:0}
  p{position:absolute;left:48px;top:150px;width:600px;font-size:20px}
  .placeholder{position:absolute;left:520px;top:150px;width:390px;height:320px;background:#e5e7eb}
</style></head>
<body>
  <h1>Quarterly Results</h1>
  <p>Revenue grew across every region, led by enterprise renewals.</p>
  <div class="placeholder" id="revChart"></div>
</body></html>
```

## Build script
```javascript
const pptxgen = require("pptxgenjs");
const { html2pptx } = require("html2pptx");

(async () => {
  const pptx = new pptxgen();
  pptx.defineLayout({ name: "16x9", width: 10, height: 5.625 }); // inches
  pptx.layout = "16x9";

  // Slide 1
  const { slide, placeholders } = await html2pptx("slide1.html", pptx, {
    widthPt: 720, heightPt: 405,
  });

  // Drop a native chart into the "revChart" placeholder rectangle
  const box = placeholders.revChart;         // {x,y,w,h} in inches
  slide.addChart(pptx.ChartType.bar,
    [{ name: "Revenue", labels: ["Q1","Q2","Q3","Q4"], values: [12,15,18,22] }],
    { x: box.x, y: box.y, w: box.w, h: box.h });

  await html2pptx("slide2.html", pptx, { widthPt: 720, heightPt: 405 });

  await pptx.writeFile({ fileName: "deck.pptx" });
})();
```

## API
`html2pptx(htmlPath, pptx, opts) → { slide, placeholders, images }`
- `htmlPath` — path to a slide HTML file.
- `pptx` — a PptxGenJS instance.
- `opts.widthPt` / `opts.heightPt` — slide size in points (default 720×405).
- `opts.slide` — reuse an existing slide instead of adding a new one.
- Returns the `slide`, a `placeholders` map (`id` → `{x,y,w,h}` in inches) for charts/tables, and the list of `images` it placed.

## Tables into a placeholder
```javascript
const t = placeholders.dataTable;
slide.addTable(
  [[{ text: "Metric", options: { bold: true } }, { text: "Value", options: { bold: true } }],
   ["MAU", "1.2M"], ["Retention", "93%"]],
  { x: t.x, y: t.y, w: t.w, h: t.h, fontSize: 12, border: { pt: 0.5, color: "D0D0D0" } }
);
```

## Validate visually
After building, always generate a thumbnail grid and inspect it:
```bash
python scripts/thumbnail.py deck.pptx workspace/thumbnails --cols 4
```
Check for text cutoff, overlap, boundary crowding, and weak contrast; adjust the HTML and rebuild until clean.

## Gotchas
- Position text with absolute CSS so measured boxes are stable.
- Keep one logical text block per element — the converter emits one text box per leaf text element.
- `networkidle` is awaited before measuring; make sure images/fonts are local so load completes.
- Point↔pixel scale is derived from the rendered body width mapped onto `widthPt`; keep the body width consistent across slides.
