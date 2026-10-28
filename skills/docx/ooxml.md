# OOXML Editing Reference

Companion to [SKILL.md](SKILL.md). How to edit an existing `.docx` by unpacking it, modifying `word/document.xml` directly with `lxml`, and repacking. Read this file fully before editing.

> **On the "Document library":** SKILL.md refers to a Document library with `get_node` / `doc.save()`. This file provides that capability as a small, dependency-light `lxml` helper (below) plus direct-XML patterns. Define the helper inline in your edit script, or copy it into `ooxml/scripts/` if you prefer importing it.

## The pipeline
```bash
# 1. Unpack
python ooxml/scripts/unpack.py contract.docx unpacked
# 2. Edit unpacked/word/document.xml  (see patterns below)
# 3. Repack
python ooxml/scripts/pack.py unpacked reviewed.docx
# 4. Verify
pandoc --track-changes=all reviewed.docx -o verification.md
```

`unpack.py` prints a **suggested RSID** — use it on new runs (`w:rsidR`) so Word groups your edits as one revision session.

## Namespaces
`word/document.xml` uses the WordprocessingML namespace. Always register it:
```python
from lxml import etree

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
def w(tag): return f'{{{NS["w"]}}}{tag}'
```

Key elements:
- `<w:p>` paragraph · `<w:r>` run · `<w:t>` text · `<w:rPr>` run properties
- `<w:ins>` tracked insertion · `<w:del>` tracked deletion · `<w:delText>` deleted text
- `<w:commentRangeStart>` / `<w:commentRangeEnd>` / `<w:commentReference>` comments

## A minimal Document helper (lxml)
```python
from lxml import etree

NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

class Document:
    """Thin wrapper over word/document.xml for find-and-edit workflows."""
    def __init__(self, path):
        self.path = path
        self.tree = etree.parse(path)   # path = unpacked/word/document.xml
        self.root = self.tree.getroot()

    def get_nodes(self, xpath):
        """Return elements matching an XPath (w: namespace prebound)."""
        return self.root.xpath(xpath, namespaces=NS)

    def get_node(self, xpath):
        nodes = self.get_nodes(xpath)
        return nodes[0] if nodes else None

    def save(self):
        self.tree.write(self.path, xml_declaration=True,
                        encoding="UTF-8", standalone=True)
```

Usage:
```python
doc = Document("unpacked/word/document.xml")
# Find a paragraph that contains some text
para = doc.get_node('.//w:p[.//w:t[contains(text(),"Termination")]]')
# ...modify...
doc.save()
```

## Before you edit: map text to runs
Word often splits a phrase across several `<w:r>` runs. Grep first:
```bash
grep -n "30 days" unpacked/word/document.xml
```
Line numbers change after every save — re-grep before each script.

## Tracked-change patterns

Set these once:
```python
AUTHOR = "Reveleer Review"
DATE = "2026-10-28T00:00:00Z"
RSID = "00AB12CD"   # the value unpack.py suggested
```

### Insertion (`<w:ins>`)
```python
def make_ins(text, wid):
    ins = etree.SubElement(_parent, f'{{{NS["w"]}}}ins')
    ins.set(f'{{{NS["w"]}}}id', str(wid))
    ins.set(f'{{{NS["w"]}}}author', AUTHOR)
    ins.set(f'{{{NS["w"]}}}date', DATE)
    r = etree.SubElement(ins, f'{{{NS["w"]}}}r')
    t = etree.SubElement(r, f'{{{NS["w"]}}}t')
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    t.text = text
    return ins
```

### Deletion (`<w:del>` with `<w:delText>`)
```python
# Deleted text uses <w:delText>, not <w:t>
'<w:del w:id="101" w:author="Reveleer Review" w:date="2026-10-28T00:00:00Z">'
'  <w:r><w:delText xml:space="preserve">30</w:delText></w:r>'
'</w:del>'
```

### Principle — minimal, precise edits
Only mark what changes. Keep unchanged text in its original run (preserve its RSID).

Changing "The term is 30 days." → "The term is 60 days.":
```xml
<w:r w:rsidR="00AB12CD"><w:t xml:space="preserve">The term is </w:t></w:r>
<w:del w:id="1" w:author="Reveleer Review" w:date="2026-10-28T00:00:00Z">
  <w:r><w:delText>30</w:delText></w:r>
</w:del>
<w:ins w:id="2" w:author="Reveleer Review" w:date="2026-10-28T00:00:00Z">
  <w:r><w:t>60</w:t></w:r>
</w:ins>
<w:r w:rsidR="00AB12CD"><w:t xml:space="preserve"> days.</w:t></w:r>
```

### Practical insertion helper (replace text in a run)
```python
def tracked_replace(doc, old, new, wid_start):
    """Split the run containing `old` into unchanged + del + ins + unchanged."""
    t = doc.get_node(f'.//w:t[contains(text(),"{old}")]')
    if t is None:
        raise ValueError(f"text not found: {old!r}")
    run = t.getparent()                     # <w:r>
    para = run.getparent()
    idx = list(para).index(run)
    before, _, after = t.text.partition(old)

    def run_with(text):
        r = etree.Element(w("r")); e = etree.SubElement(r, w("t"))
        e.set("{http://www.w3.org/XML/1998/namespace}space", "preserve"); e.text = text
        return r
    def wrap(tag, text, wid, deltext=False):
        node = etree.Element(w(tag))
        node.set(w("id"), str(wid)); node.set(w("author"), AUTHOR); node.set(w("date"), DATE)
        r = etree.SubElement(node, w("r"))
        e = etree.SubElement(r, w("delText" if deltext else "t"))
        e.set("{http://www.w3.org/XML/1998/namespace}space", "preserve"); e.text = text
        return node

    para.remove(run)
    new_nodes = []
    if before: new_nodes.append(run_with(before))
    new_nodes.append(wrap("del", old, wid_start, deltext=True))
    new_nodes.append(wrap("ins", new, wid_start + 1))
    if after: new_nodes.append(run_with(after))
    for off, node in enumerate(new_nodes):
        para.insert(idx + off, node)
```

## Comments
Comments live in `word/comments.xml` and are anchored in `document.xml`.

1. Add the comment body to `word/comments.xml`:
```xml
<w:comment w:id="0" w:author="Reveleer Review" w:date="2026-10-28T00:00:00Z" w:initials="RR">
  <w:p><w:r><w:t>Please confirm this figure.</w:t></w:r></w:p>
</w:comment>
```
2. Anchor it around the target text in `document.xml`:
```xml
<w:commentRangeStart w:id="0"/>
<w:r><w:t>the disputed clause</w:t></w:r>
<w:commentRangeEnd w:id="0"/>
<w:r><w:rPr><w:rStyle w:val="CommentReference"/></w:rPr><w:commentReference w:id="0"/></w:r>
```
3. Ensure `word/_rels/document.xml.rels` and `[Content_Types].xml` reference `comments.xml` (present already if the doc had comments; otherwise add the relationship + content-type override).

## Batching & verification
- Implement 3–10 related changes per script, then repack and verify before the next batch.
- Verify with pandoc + grep:
```bash
pandoc --track-changes=all reviewed.docx -o verification.md
grep "original phrase" verification.md   # should be gone / shown as deleted
grep "replacement phrase" verification.md  # should be present / shown as inserted
```

## Gotchas
- `xml:space="preserve"` on `<w:t>` whenever leading/trailing spaces matter.
- Unique `w:id` per `<w:ins>`/`<w:del>`/comment — never reuse within a document.
- Don't reformat/pretty-print the whole XML — it can alter significant whitespace. `unpack.py` intentionally does not reformat.
- Deleted text uses `<w:delText>`; inserted/normal text uses `<w:t>`.
