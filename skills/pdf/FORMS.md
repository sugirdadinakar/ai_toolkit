# Filling PDF Forms

Companion to [SKILL.md](SKILL.md). How to inspect and fill AcroForm fields in PDFs.

## Step 1: Inspect the form fields first

Never guess field names — enumerate them.

```python
from pypdf import PdfReader

reader = PdfReader("form.pdf")
fields = reader.get_fields()
if not fields:
    print("No AcroForm fields found (may be a flat PDF or XFA form).")
else:
    for name, f in fields.items():
        print(f"{name!r}: type={f.get('/FT')}, value={f.get('/V')}, "
              f"states={f.get('/_States_')}")
```

Field types (`/FT`):
- `/Tx` — text field
- `/Btn` — checkbox or radio button (use the state names from `/_States_`)
- `/Ch` — choice (dropdown / list box)
- `/Sig` — signature

## Step 2: Fill fields with pypdf

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("form.pdf")
writer = PdfWriter()
writer.append(reader)

# Text fields: name -> value. Checkboxes: name -> on-state (e.g. "/Yes").
writer.update_page_form_field_values(
    writer.pages[0],
    {
        "full_name": "Jordan Lee",
        "email": "jordan@example.com",
        "subscribe": "/Yes",       # checkbox on-state from /_States_
        "plan": "Enterprise",      # dropdown value
    },
    auto_regenerate=False,
)

with open("filled.pdf", "wb") as out:
    writer.write(out)
```

### Make values visible in all viewers (NeedAppearances)
Some viewers won't render filled values unless `NeedAppearances` is set.

```python
from pypdf.generic import NameObject, BooleanObject

writer.set_need_appearances_writer(True)   # pypdf >= 3.x helper
# Fallback if the helper is unavailable:
# writer._root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(True)
```

### Checkboxes and radio buttons
The "on" value is NOT always `/Yes`. Read it from the field:
```python
f = reader.get_fields()["subscribe"]
on_state = next(s for s in f["/_States_"] if s != "/Off")
writer.update_page_form_field_values(writer.pages[0], {"subscribe": on_state})
```

## Step 3: Flatten (optional)
Flattening bakes values into page content so they can't be edited and render everywhere.

```javascript
// pdf-lib flattens reliably:
import { PDFDocument } from "pdf-lib";
import { readFileSync, writeFileSync } from "fs";

const doc = await PDFDocument.load(readFileSync("filled.pdf"));
const form = doc.getForm();
form.getTextField("full_name").setText("Jordan Lee");
form.getCheckBox("subscribe").check();
form.flatten();                        // makes fields non-editable
writeFileSync("flattened.pdf", await doc.save());
```

## pdf-lib form filling (JavaScript)
```javascript
const form = doc.getForm();
form.getTextField("email").setText("jordan@example.com");
form.getDropdown("plan").select("Enterprise");
form.getRadioGroup("tier").select("gold");
```

## XFA forms (LiveCycle)
If `get_fields()` returns nothing but the PDF clearly has fields, it may be an **XFA** form (common in government/banking PDFs).
- pypdf/pdf-lib handle the AcroForm layer, not the XFA layer.
- Options: fill via the AcroForm fallback if present; or use a dedicated XFA tool; or render to image, overlay text with reportlab, and flatten.

## Overlay approach (flat PDFs with no fields)
When there are no form fields at all, stamp text at coordinates:

```python
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter
import io

buf = io.BytesIO()
c = canvas.Canvas(buf)
c.drawString(120, 650, "Jordan Lee")      # x, y in points from bottom-left
c.save()
buf.seek(0)

overlay = PdfReader(buf).pages[0]
reader = PdfReader("flat.pdf")
writer = PdfWriter()
page = reader.pages[0]
page.merge_page(overlay)
writer.add_page(page)
with open("stamped.pdf", "wb") as out:
    writer.write(out)
```

## Checklist
1. Enumerate fields — never guess names.
2. Use exact checkbox/radio on-states from `/_States_`.
3. Set `NeedAppearances` if values don't show.
4. Flatten only when the form should become read-only.
5. Verify: re-open and `get_fields()` or convert to image to confirm.
