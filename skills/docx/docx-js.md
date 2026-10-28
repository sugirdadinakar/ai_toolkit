# docx-js Reference — Creating Word Documents

Companion to [SKILL.md](SKILL.md). Use the `docx` npm library (docx-js) to build `.docx` files from JavaScript/TypeScript. Read this file fully before generating a document.

## Install
```bash
npm install docx
```

## Critical rules (read first)
1. **All text lives in a `TextRun` inside a `Paragraph`.** You cannot put a bare string where a child element is expected (except in a few props like `text:`).
2. **A `Document` needs `sections`.** Each section has `children: [...]` (an array of paragraphs/tables).
3. **Styling goes on the run or paragraph**, not on raw strings. Mixed formatting in one line = multiple `TextRun`s.
4. **Save with `Packer`** — `Packer.toBuffer(doc)` (Node) returns a Buffer you write to disk.
5. **Numbering (ordered/bulleted lists)** must be declared in the document config and referenced by `reference`.
6. Measurements: font `size` is in **half-points** (`size: 24` = 12pt). Spacing/indent are in **twips** (1/20 pt; 720 twips = 0.5").

## Minimal document
```javascript
import { Document, Packer, Paragraph, TextRun, HeadingLevel } from "docx";
import { writeFileSync } from "fs";

const doc = new Document({
  sections: [
    {
      properties: {},
      children: [
        new Paragraph({ text: "Report Title", heading: HeadingLevel.TITLE }),
        new Paragraph({
          children: [
            new TextRun("This is normal text, "),
            new TextRun({ text: "this is bold, ", bold: true }),
            new TextRun({ text: "this is italic.", italics: true }),
          ],
        }),
      ],
    },
  ],
});

writeFileSync("out.docx", await Packer.toBuffer(doc));
```

## Headings & styles
```javascript
new Paragraph({ text: "Section 1", heading: HeadingLevel.HEADING_1 });
new Paragraph({ text: "Subsection", heading: HeadingLevel.HEADING_2 });
// Alignment
import { AlignmentType } from "docx";
new Paragraph({ text: "Centered", alignment: AlignmentType.CENTER });
```

## Text formatting options (TextRun)
```javascript
new TextRun({
  text: "Styled",
  bold: true, italics: true, underline: {}, strike: true,
  size: 24,                 // 12pt (half-points)
  color: "2E74B5",          // hex, no #
  font: "Calibri",
  highlight: "yellow",
  superScript: true,        // or subScript
});
```

## Lists
```javascript
// Bulleted
new Paragraph({ text: "First bullet", bullet: { level: 0 } });
new Paragraph({ text: "Nested bullet", bullet: { level: 1 } });

// Numbered — declare numbering, then reference it
const doc = new Document({
  numbering: {
    config: [{
      reference: "my-numbers",
      levels: [{ level: 0, format: "decimal", text: "%1.", alignment: AlignmentType.START }],
    }],
  },
  sections: [{
    children: [
      new Paragraph({ text: "Step one", numbering: { reference: "my-numbers", level: 0 } }),
      new Paragraph({ text: "Step two", numbering: { reference: "my-numbers", level: 0 } }),
    ],
  }],
});
```

## Tables
```javascript
import { Table, TableRow, TableCell, WidthType } from "docx";

new Table({
  width: { size: 100, type: WidthType.PERCENTAGE },
  rows: [
    new TableRow({
      children: [
        new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Name", bold: true })] })] }),
        new TableCell({ children: [new Paragraph({ children: [new TextRun({ text: "Role", bold: true })] })] }),
      ],
    }),
    new TableRow({
      children: [
        new TableCell({ children: [new Paragraph("Jordan")] }),
        new TableCell({ children: [new Paragraph("PM")] }),
      ],
    }),
  ],
});
```

## Images
```javascript
import { ImageRun } from "docx";
import { readFileSync } from "fs";

new Paragraph({
  children: [
    new ImageRun({
      data: readFileSync("logo.png"),
      transformation: { width: 200, height: 100 },  // pixels
    }),
  ],
});
```

## Headers, footers & page numbers
```javascript
import { Header, Footer, PageNumber } from "docx";

const doc = new Document({
  sections: [{
    headers: { default: new Header({ children: [new Paragraph("Confidential")] }) },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          children: [new TextRun("Page "), new TextRun({ children: [PageNumber.CURRENT] })],
        })],
      }),
    },
    children: [ /* ... */ ],
  }],
});
```

## Page breaks & spacing
```javascript
import { PageBreak } from "docx";
new Paragraph({ children: [new PageBreak()] });
new Paragraph({ text: "Spaced", spacing: { before: 240, after: 240 } }); // twips
```

## Page size & margins
```javascript
const doc = new Document({
  sections: [{
    properties: {
      page: {
        size: { width: 11906, height: 16838 },      // A4 in twips
        margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 }, // 1"
      },
    },
    children: [ /* ... */ ],
  }],
});
```

## Saving
```javascript
// Node
import { writeFileSync } from "fs";
writeFileSync("out.docx", await Packer.toBuffer(doc));

// Browser
const blob = await Packer.toBlob(doc);
```

## Common mistakes
| Mistake | Fix |
|---|---|
| Passing a string where a child is expected | Wrap it in `new TextRun(...)` inside a `Paragraph` |
| `size: 12` giving tiny text | Size is half-points — use `24` for 12pt |
| Numbered list not numbering | Declare `numbering.config` and reference it |
| Mixed bold/normal on one line as one run | Use multiple `TextRun`s |
| Colors with `#` | Use hex without `#` (`"FF0000"`) |
