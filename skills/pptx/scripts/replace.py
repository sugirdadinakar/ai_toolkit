#!/usr/bin/env python3
"""Replace text in a .pptx using a JSON produced from inventory.py.

Usage:
    python scripts/replace.py <in.pptx> <replacement.json> <out.pptx>

Behaviour (matches SKILL.md):
  - Uses inventory.py's ordering so shape keys line up with the inventory.
  - Validates every slide/shape in the replacement JSON exists (all errors at
    once, then exits).
  - Clears text from ALL inventory text shapes, then applies "paragraphs" only
    to shapes that provide them.
  - Applies paragraph properties: bullet/level, alignment, space_before/after,
    line_spacing, font_name/size, bold/italic/underline, color/theme_color.

Requires: python-pptx
"""

import json
import sys

from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_AUTO_SIZE
from pptx.enum.dml import MSO_THEME_COLOR

import inventory  # same directory

ALIGN = {"CENTER": PP_ALIGN.CENTER, "RIGHT": PP_ALIGN.RIGHT,
         "LEFT": PP_ALIGN.LEFT, "JUSTIFY": PP_ALIGN.JUSTIFY}


def validate(repl, slide_shapes):
    errors = []
    for skey, shapes in repl.items():
        if skey not in slide_shapes:
            errors.append(f"Slide '{skey}' not found in inventory")
            continue
        available = ", ".join(slide_shapes[skey].keys()) or "(none)"
        for shkey in shapes:
            if shkey not in slide_shapes[skey]:
                errors.append(
                    f"Shape '{shkey}' not found on '{skey}'. Available shapes: {available}")
    return errors


def clear_text_frame(tf):
    # Keep a single empty paragraph.
    for p in list(tf.paragraphs[1:]):
        p._p.getparent().remove(p._p)
    first = tf.paragraphs[0]
    for r in list(first.runs):
        r._r.getparent().remove(r._r)


def apply_paragraph(tf, i, spec):
    para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    run = para.add_run()
    run.text = spec.get("text", "")

    if spec.get("bullet"):
        para.level = int(spec.get("level", 0))
        # bullets are left-aligned; don't override alignment
    elif "alignment" in spec and spec["alignment"] in ALIGN:
        para.alignment = ALIGN[spec["alignment"]]

    pf = para.paragraph_format
    if "space_before" in spec:
        pf.space_before = Pt(spec["space_before"])
    if "space_after" in spec:
        pf.space_after = Pt(spec["space_after"])
    if "line_spacing" in spec:
        pf.line_spacing = Pt(spec["line_spacing"])

    font = run.font
    if "font_name" in spec:
        font.name = spec["font_name"]
    if "font_size" in spec:
        font.size = Pt(spec["font_size"])
    if "bold" in spec:
        font.bold = bool(spec["bold"])
    if "italic" in spec:
        font.italic = bool(spec["italic"])
    if "underline" in spec:
        font.underline = bool(spec["underline"])
    if "color" in spec:
        font.color.rgb = RGBColor.from_string(spec["color"].lstrip("#"))
    elif "theme_color" in spec:
        try:
            font.color.theme_color = getattr(MSO_THEME_COLOR, spec["theme_color"])
        except AttributeError:
            pass


def main() -> int:
    if len(sys.argv) != 4:
        print("Usage: python replace.py <in.pptx> <replacement.json> <out.pptx>")
        return 1

    in_path, json_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    prs = Presentation(in_path)

    # Build inventory + a parallel map of actual shape objects.
    slide_shapes = {}        # skey -> {shkey: dict}
    shape_objs = {}          # (skey, shkey) -> shape
    for si, slide in enumerate(prs.slides):
        skey = f"slide-{si}"
        slide_shapes[skey] = {}
        for shi, shape in enumerate(inventory.ordered_text_shapes(slide)):
            shkey = f"shape-{shi}"
            slide_shapes[skey][shkey] = inventory.shape_to_dict(shape)
            shape_objs[(skey, shkey)] = shape

    with open(json_path, encoding="utf-8") as f:
        repl = json.load(f)

    errors = validate(repl, slide_shapes)
    if errors:
        print("ERROR: Invalid shapes in replacement JSON:")
        for e in errors:
            print(f"  - {e}")
        return 1

    # Clear ALL text shapes, then apply provided paragraphs.
    cleared = applied = 0
    for (skey, shkey), shape in shape_objs.items():
        clear_text_frame(shape.text_frame)
        cleared += 1
    for skey, shapes in repl.items():
        for shkey, spec in shapes.items():
            paras = spec.get("paragraphs")
            if not paras:
                continue
            tf = shape_objs[(skey, shkey)].text_frame
            for i, p in enumerate(paras):
                apply_paragraph(tf, i, p)
            applied += 1

    prs.save(out_path)
    print(f"Cleared {cleared} shapes, applied text to {applied} shapes -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
