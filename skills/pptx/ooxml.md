# PPTX OOXML Editing Reference

Companion to [SKILL.md](SKILL.md). How to edit an existing `.pptx` by unpacking it, modifying slide XML, validating, and repacking. Read this file fully before editing.

## The pipeline
```bash
python ooxml/scripts/unpack.py deck.pptx unpacked      # 1. unpack
# 2. edit unpacked/ppt/slides/slideN.xml (and related parts)
python ooxml/scripts/validate.py unpacked --original deck.pptx   # 3. validate (after EVERY edit)
python ooxml/scripts/pack.py unpacked edited.pptx      # 4. repack
```
Always validate after each edit and fix errors before continuing — a malformed part makes the whole file unopenable.

## Package structure
```
ppt/presentation.xml          # slide order (<p:sldIdLst>), size, references
ppt/slides/slideN.xml         # slide content (shapes, text)
ppt/slides/_rels/slideN.xml.rels   # slide relationships (images, layout, notes)
ppt/notesSlides/notesSlideN.xml    # speaker notes
ppt/slideLayouts/ , ppt/slideMasters/   # templates
ppt/theme/theme1.xml          # colors (<a:clrScheme>) and fonts (<a:fontScheme>)
ppt/media/                    # images and media
[Content_Types].xml           # MIME types for every part
```

## Namespaces
PresentationML uses three main namespaces:
```python
from lxml import etree
NS = {
  "a": "http://schemas.openxmlformats.org/drawingml/2006/main",            # text, runs, colors
  "p": "http://schemas.openxmlformats.org/presentationml/2006/main",       # slides, shapes
  "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
def a(t): return f'{{{NS["a"]}}}{t}'
def p(t): return f'{{{NS["p"]}}}{t}'
```

## Text model
Text lives in shapes: `<p:sp>` → `<p:txBody>` → `<a:p>` (paragraph) → `<a:r>` (run) → `<a:t>` (text).

```xml
<p:sp>
  <p:txBody>
    <a:p>
      <a:r><a:rPr lang="en-US" sz="2400" b="1"/><a:t>Title text</a:t></a:r>
    </a:p>
  </p:txBody>
</p:sp>
```
- Font size `sz` is in **hundredths of a point** (`2400` = 24pt).
- Bold `b="1"`, italic `i="1"`, underline `u="sng"`.
- Paragraph properties go in `<a:pPr>` (alignment `algn="ctr|r|just"`, level `lvl="1"`).

## Editing text with lxml
```python
from lxml import etree

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
tree = etree.parse("unpacked/ppt/slides/slide1.xml")
root = tree.getroot()

# Replace the text of the first run that contains a phrase
for t in root.iter("{http://schemas.openxmlformats.org/drawingml/2006/main}t"):
    if t.text and "OLD TITLE" in t.text:
        t.text = t.text.replace("OLD TITLE", "NEW TITLE")

tree.write("unpacked/ppt/slides/slide1.xml",
           xml_declaration=True, encoding="UTF-8", standalone=True)
```

Grep first to see how text is split across runs — Word/PowerPoint often splits a phrase:
```bash
grep -n "OLD TITLE" unpacked/ppt/slides/slide1.xml
```

## Colors
```xml
<a:solidFill><a:srgbClr val="C0392B"/></a:solidFill>   <!-- explicit RGB -->
<a:solidFill><a:schemeClr val="accent1"/></a:solidFill> <!-- theme color -->
```
To restyle consistently, prefer editing `ppt/theme/theme1.xml` `<a:clrScheme>` over per-shape colors.

## Speaker notes
Notes are in `ppt/notesSlides/notesSlideN.xml`, linked from the slide's `.rels`. The notes text is in a `<p:sp>` whose placeholder type is `body`. Edit the `<a:t>` runs the same way as slide text.

## Prefer python-pptx for structural edits
For adding/removing/reordering/duplicating slides or bulk text replacement, use the higher-level tools instead of hand-editing XML:
- `scripts/rearrange.py` — duplicate / reorder / delete slides
- `scripts/inventory.py` — dump all text shapes to JSON
- `scripts/replace.py` — apply formatted replacement text
Hand-edit raw XML only for things those don't cover (animations, exotic formatting, theme surgery).

## Gotchas
- Keep `xml:space="preserve"` on `<a:t>` when leading/trailing spaces matter.
- `sz` is hundredths of a point (2400 = 24pt) — a frequent off-by-100 mistake.
- Don't pretty-print/reformat the whole slide XML; it can disturb significant whitespace. `unpack.py` does not reformat.
- After any edit, run `validate.py` before packing.
- If you add a new part (e.g. an image), register it in `[Content_Types].xml` and the relevant `_rels` file.
