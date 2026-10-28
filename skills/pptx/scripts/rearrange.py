#!/usr/bin/env python3
"""Duplicate, reorder, and delete slides in a .pptx.

Usage:
    python scripts/rearrange.py <template.pptx> <out.pptx> <mapping>

<mapping> is a comma-separated list of 0-based slide indices from the template,
in the desired output order. Repeat an index to duplicate that slide; omit an
index to drop it.

    python scripts/rearrange.py template.pptx working.pptx 0,34,34,50,52

Copies each selected source slide (shapes + image/media relationships) into the
output order. Text and images are handled; very exotic embeds (OLE, charts with
external data) may need manual review.

Requires: python-pptx
"""

import copy
import sys

from pptx import Presentation
from pptx.oxml.ns import qn


def _duplicate_slide(prs, source_slide):
    """Append a copy of source_slide to prs; return the new slide."""
    layout = source_slide.slide_layout
    new_slide = prs.slides.add_slide(layout)

    # Remove placeholders that add_slide created from the layout.
    for shp in list(new_slide.shapes):
        shp._element.getparent().remove(shp._element)

    # Deep-copy every shape element from the source.
    spTree = new_slide.shapes._spTree
    for shp in source_slide.shapes:
        spTree.append(copy.deepcopy(shp._element))

    # Copy relationships (images, media, hyperlinks). Re-point rIds so the
    # copied shape XML keeps resolving.
    for rid, rel in source_slide.part.rels.items():
        if rel.reltype.endswith("/slideLayout"):
            continue  # already set by add_slide
        if rel.is_external:
            new_slide.part.rels.get_or_add_ext_rel(rel.reltype, rel.target_ref)
        else:
            new_slide.part.relate_to(rel.target_part, rel.reltype, rid)
    return new_slide


def _sldIdLst(prs):
    return prs.slides._sldIdLst


def main() -> int:
    if len(sys.argv) != 4:
        print("Usage: python rearrange.py <template.pptx> <out.pptx> <mapping>")
        print("Example: python rearrange.py template.pptx out.pptx 0,34,34,50,52")
        return 1

    src_path, out_path, mapping_arg = sys.argv[1], sys.argv[2], sys.argv[3]
    try:
        mapping = [int(x) for x in mapping_arg.split(",") if x.strip() != ""]
    except ValueError:
        print(f"Error: mapping must be comma-separated integers, got {mapping_arg!r}")
        return 1

    prs = Presentation(src_path)
    originals = list(prs.slides)
    n = len(originals)

    bad = [i for i in mapping if i < 0 or i >= n]
    if bad:
        print(f"Error: indices out of range (template has {n} slides, 0-{n-1}): {bad}")
        return 1

    # 1. Append a duplicate for each mapping entry (sources stay intact).
    new_slides = [_duplicate_slide(prs, originals[i]) for i in mapping]

    # 2. Remove the original slides.
    lst = _sldIdLst(prs)
    original_ids = {id(s) for s in originals}
    rid_by_slide = {}
    for sldId in list(lst):
        rid_by_slide[sldId.get(qn("r:id"))] = sldId

    # Map each slide part to its sldId element via rels on the presentation part.
    pres_part = prs.part
    remove_sldIds = []
    keep_order = []
    for sldId in list(lst):
        rid = sldId.get(qn("r:id"))
        slide_part = pres_part.rels[rid].target_part
        slide = next((s for s in prs.slides if s.part is slide_part), None)
        if slide is not None and id(slide) in original_ids:
            remove_sldIds.append(sldId)
        else:
            keep_order.append((slide, sldId))

    for sldId in remove_sldIds:
        lst.remove(sldId)

    # 3. Reorder remaining sldIds to match `new_slides` order.
    sldId_by_part = {}
    for sldId in list(lst):
        rid = sldId.get(qn("r:id"))
        sldId_by_part[pres_part.rels[rid].target_part] = sldId
    for sldId in list(lst):
        lst.remove(sldId)
    for slide in new_slides:
        sldId = sldId_by_part.get(slide.part)
        if sldId is not None:
            lst.append(sldId)

    prs.save(out_path)
    print(f"Rearranged {n} template slides into {len(mapping)} slides -> {out_path}")
    print(f"Order (source indices): {mapping}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
