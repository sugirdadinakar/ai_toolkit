# PDF Reference — Advanced Operations

Companion to [SKILL.md](SKILL.md). Covers advanced Python usage, JavaScript libraries, and troubleshooting. For filling forms, see [FORMS.md](FORMS.md).

## pypdfium2 — Rendering & Fast Text

`pypdfium2` wraps Google's PDFium (the Chrome PDF engine). Use it for rendering pages to images and fast, layout-aware text extraction.

```bash
pip install pypdfium2
```

### Render pages to images
```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("document.pdf")
for i, page in enumerate(pdf):
    bitmap = page.render(scale=2)          # scale 2 ≈ 144 DPI
    image = bitmap.to_pil()
    image.save(f"page_{i+1}.png")
pdf.close()
```

### Extract text with positions
```python
pdf = pdfium.PdfDocument("document.pdf")
page = pdf[0]
textpage = page.get_textpage()
print(textpage.get_text_range())                     # all text
print(textpage.count_chars())                        # char count
# Bounded extraction (left, bottom, right, top) in PDF points
print(textpage.get_text_bounded(0, 0, 300, 800))
```

## Advanced pdfplumber

### Crop a region before extracting
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]
    header = page.crop((0, 0, page.width, 100))      # top 100pt
    print(header.extract_text())
```

### Tune table detection
```python
settings = {
    "vertical_strategy": "lines",      # or "text"
    "horizontal_strategy": "lines",
    "snap_tolerance": 3,
    "join_tolerance": 3,
}
tables = page.extract_tables(settings)
```

### Inspect words and characters
```python
for w in page.extract_words():
    print(w["text"], w["x0"], w["top"])
# page.chars, page.lines, page.rects, page.images are also available
```

## JavaScript — pdf-lib

`pdf-lib` creates and modifies PDFs in Node or the browser with no native deps.

```bash
npm install pdf-lib
```

### Create a PDF
```javascript
import { PDFDocument, StandardFonts, rgb } from "pdf-lib";
import { writeFileSync } from "fs";

const doc = await PDFDocument.create();
const page = doc.addPage([595, 842]);              // A4 in points
const font = await doc.embedFont(StandardFonts.Helvetica);
page.drawText("Hello from pdf-lib", {
  x: 50, y: 780, size: 18, font, color: rgb(0.1, 0.1, 0.1),
});
writeFileSync("out.pdf", await doc.save());
```

### Merge
```javascript
const merged = await PDFDocument.create();
for (const path of ["a.pdf", "b.pdf"]) {
  const src = await PDFDocument.load(readFileSync(path));
  const pages = await merged.copyPages(src, src.getPageIndices());
  pages.forEach((p) => merged.addPage(p));
}
writeFileSync("merged.pdf", await merged.save());
```

### Modify an existing page
```javascript
const doc = await PDFDocument.load(readFileSync("in.pdf"));
const [first] = doc.getPages();
first.drawText("DRAFT", { x: 200, y: 400, size: 60, opacity: 0.2 });
writeFileSync("out.pdf", await doc.save());
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `extract_text()` returns empty | Scanned/image-only PDF | OCR path (pytesseract + pdf2image) in SKILL.md |
| Garbled / missing glyphs | Non-embedded or CJK fonts | Render with pypdfium2 then OCR; or `pdftotext -layout` |
| `PdfReadError: file has not been decrypted` | Password-protected | `qpdf --password=PW --decrypt in.pdf out.pdf`, then process |
| Tables come out merged | Weak line detection | Switch `vertical_strategy`/`horizontal_strategy` to `"text"` |
| Huge memory on big PDFs | Loading all pages at once | Stream page-by-page; close documents; process in batches |
| Rotated text extracted out of order | Page rotation metadata | Normalise with `page.rotate(-angle)` before extracting |
| Form fields read as blank | Values in appearance streams only | See FORMS.md (`NeedAppearances`, field value vs. appearance) |

## Performance tips
- Prefer `pypdfium2` for rendering and bulk text; `pdfplumber` for tables and precise layout.
- Close documents (`pdf.close()` / context managers) to release native memory.
- For 100s of PDFs, parallelise across processes, not threads (native libs hold the GIL unevenly).
