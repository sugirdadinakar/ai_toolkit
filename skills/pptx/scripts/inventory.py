#!/usr/bin/env python3
"""Extract a text inventory from a .pptx into JSON.

Usage:
    python scripts/inventory.py <pptx> <out.json>

Emits every text-bearing shape, ordered by visual position (top-to-bottom,
left-to-right), with paragraph text and non-default formatting properties.
Importable: replace.py uses `ordered_text_shapes` and `shape_to_dict` so both
tools agree on shape identity and ordering.

Requires: python-pptx  (pip install python-pptx)
"""

import json
import sys

from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import PP_PLACEHOLDER

EMU_PER_INCH = 914400


def _emu_to_in(v):
    return round(v / EMU_PER_INCH, 3) if v is not None else None


def _alignment(para):
    a = para.alignment
    if a in (None, PP_ALIGN.LEFT):
        return None
    return {PP_ALIGN.CENTER: "CENTER", PP_ALIGN.RIGHT: "RIGHT",
            PP_ALIGN.JUSTIFY: "JUSTIFY"}.get(a)


def _has_bullet(para):
    """Detect an explicit bullet via the paragraph's XML (buChar/buAutoNum)."""
    pPr = para._pPr
    if pPr is None:
        return False
    for tag in ("a:buChar", "a:buAutoNum"):
        if pPr.find(_qn(tag)) is not None:
            return True
    return False


def _qn(tag):
    from pptx.oxml.ns import qn
    return qn(tag)


def _placeholder_type(shape):
    if not shape.is_placeholder:
        return None
    try:
        return shape.placeholder_format.type
    except Exception:  # noqa: BLE001
        return None


def _ph_name(ph_type):
    if ph_type is None:
        return None
    try:
        return str(ph_type).split()[0].rstrip(":").upper().replace("PP_PLACEHOLDER.", "")
    except Exception:  # noqa: BLE001
        return str(ph_type)


def ordered_text_shapes(slide):
    """Return text-frame shapes (excluding slide-number placeholders),
    sorted top-to-bottom then left-to-right — the canonical shape order."""
    shapes = []
    for sh in slide.shapes:
        if not sh.has_text_frame:
            continue
        if _placeholder_type(sh) == PP_PLACEHOLDER.SLIDE_NUMBER:
            continue
        shapes.append(sh)
    shapes.sort(key=lambda s: ((s.top or 0), (s.left or 0)))
    return shapes


def _run_font_props(para):
    if not para.runs:
        return {}
    f = para.runs[0].font
    props = {}
    if f.name:
        props["font_name"] = f.name
    if f.size is not None:
        props["font_size"] = round(f.size.pt, 1)
    if f.bold is not None:
        props["bold"] = bool(f.bold)
    if f.italic is not None:
        props["italic"] = bool(f.italic)
    if f.underline is not None:
        props["underline"] = bool(f.underline)
    try:
        if f.color and f.color.type is not None:
            if f.color.type == 1:  # RGB
                props["color"] = str(f.color.rgb)
            else:  # theme
                props["theme_color"] = str(f.color.theme_color).split(".")[-1]
    except Exception:  # noqa: BLE001
        pass
    return props


def _para_to_dict(para):
    text = "".join(r.text for r in para.runs) if para.runs else (para.text or "")
    d = {"text": text}
    if _has_bullet(para):
        d["bullet"] = True
        d["level"] = para.level or 0
    align = _alignment(para)
    if align:
        d["alignment"] = align
    pf = para.paragraph_format
    if pf.space_before is not None:
        d["space_before"] = round(pf.space_before.pt, 1)
    if pf.space_after is not None:
        d["space_after"] = round(pf.space_after.pt, 1)
    if pf.line_spacing is not None and hasattr(pf.line_spacing, "pt"):
        d["line_spacing"] = round(pf.line_spacing.pt, 1)
    d.update(_run_font_props(para))
    return d


def _default_font_size(shape):
    """Best-effort default font size (pt) from the layout placeholder."""
    try:
        if shape.is_placeholder:
            idx = shape.placeholder_format.idx
            layout = shape.part.slide.slide_layout
            for lp in layout.placeholders:
                if lp.placeholder_format.idx == idx and lp.has_text_frame:
                    for p in lp.text_frame.paragraphs:
                        if p.runs and p.runs[0].font.size is not None:
                            return round(p.runs[0].font.size.pt, 1)
    except Exception:  # noqa: BLE001
        pass
    return None


def shape_to_dict(shape):
    ph = _placeholder_type(shape)
    d = {
        "placeholder_type": _ph_name(ph),
        "left": _emu_to_in(shape.left),
        "top": _emu_to_in(shape.top),
        "width": _emu_to_in(shape.width),
        "height": _emu_to_in(shape.height),
        "paragraphs": [_para_to_dict(p) for p in shape.text_frame.paragraphs],
    }
    dfs = _default_font_size(shape)
    if dfs is not None:
        d["default_font_size"] = dfs
    return d


def build_inventory(prs):
    inv = {}
    for si, slide in enumerate(prs.slides):
        skey = f"slide-{si}"
        inv[skey] = {}
        for shi, shape in enumerate(ordered_text_shapes(slide)):
            inv[skey][f"shape-{shi}"] = shape_to_dict(shape)
    return inv


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python inventory.py <pptx> <out.json>")
        return 1
    prs = Presentation(sys.argv[1])
    inv = build_inventory(prs)
    with open(sys.argv[2], "w", encoding="utf-8") as f:
        json.dump(inv, f, indent=2, ensure_ascii=False)
    n_shapes = sum(len(v) for v in inv.values())
    print(f"Wrote inventory: {len(inv)} slides, {n_shapes} text shapes -> {sys.argv[2]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
