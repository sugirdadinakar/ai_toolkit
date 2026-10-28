#!/usr/bin/env python3
"""Render a .pptx to thumbnail grid image(s) for quick visual review.

Usage:
    python scripts/thumbnail.py <pptx> [output_prefix] [--cols N]

Pipeline: pptx -> pdf (LibreOffice) -> page JPEGs (pdftoppm) -> tiled grid (PIL).
Writes <prefix>.jpg, or <prefix>-1.jpg, <prefix>-2.jpg ... for large decks.
Slides are zero-indexed in the labels.

Grid limits by columns: 3->12, 4->20, 5->30 (default), 6->42 per grid.

Requires: LibreOffice (soffice), poppler (pdftoppm), Pillow.
"""

import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

PER_GRID = {3: 12, 4: 20, 5: 30, 6: 42}


def _which(name):
    return shutil.which(name)


def pptx_to_pdf(pptx, workdir):
    soffice = _which("soffice") or _which("libreoffice")
    if not soffice:
        raise RuntimeError("LibreOffice (soffice) not found on PATH")
    subprocess.run([soffice, "--headless", "--convert-to", "pdf",
                    "--outdir", workdir, pptx], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = os.path.splitext(os.path.basename(pptx))[0]
    pdf = os.path.join(workdir, base + ".pdf")
    if not os.path.isfile(pdf):
        raise RuntimeError("PDF conversion failed")
    return pdf


def pdf_to_images(pdf, workdir, dpi=90):
    if not _which("pdftoppm"):
        raise RuntimeError("pdftoppm (poppler-utils) not found on PATH")
    prefix = os.path.join(workdir, "page")
    subprocess.run(["pdftoppm", "-jpeg", "-r", str(dpi), pdf, prefix], check=True)
    return sorted(glob.glob(prefix + "*.jpg"))


def make_grid(images, out_path, cols, start_index, cell_w=360):
    rows = (len(images) + cols - 1) // cols
    thumbs = []
    for img_path in images:
        im = Image.open(img_path).convert("RGB")
        ratio = cell_w / im.width
        thumbs.append(im.resize((cell_w, int(im.height * ratio))))
    cell_h = max(t.height for t in thumbs)
    pad, label_h = 10, 22
    grid_w = cols * cell_w + (cols + 1) * pad
    grid_h = rows * (cell_h + label_h) + (rows + 1) * pad
    grid = Image.new("RGB", (grid_w, grid_h), "white")
    draw = ImageDraw.Draw(grid)
    try:
        font = ImageFont.load_default()
    except Exception:  # noqa: BLE001
        font = None
    for i, thumb in enumerate(thumbs):
        r, c = divmod(i, cols)
        x = pad + c * (cell_w + pad)
        y = pad + r * (cell_h + label_h + pad)
        draw.text((x, y), f"Slide {start_index + i}", fill="black", font=font)
        grid.paste(thumb, (x, y + label_h))
    grid.save(out_path, quality=85)
    return out_path


def main() -> int:
    ap = argparse.ArgumentParser(description="Create thumbnail grid(s) of a .pptx")
    ap.add_argument("pptx")
    ap.add_argument("output_prefix", nargs="?", default="thumbnails")
    ap.add_argument("--cols", type=int, default=5, choices=[3, 4, 5, 6])
    args = ap.parse_args()

    if not os.path.isfile(args.pptx):
        print(f"Error: file not found: {args.pptx}")
        return 1

    out_dir = os.path.dirname(args.output_prefix)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    per_grid = PER_GRID[args.cols]
    with tempfile.TemporaryDirectory() as work:
        try:
            pdf = pptx_to_pdf(args.pptx, work)
            images = pdf_to_images(pdf, work)
        except RuntimeError as e:
            print(f"Error: {e}")
            return 1

        if not images:
            print("No slides rendered.")
            return 1

        batches = [images[i:i + per_grid] for i in range(0, len(images), per_grid)]
        outputs = []
        for bi, batch in enumerate(batches):
            if len(batches) == 1:
                out = f"{args.output_prefix}.jpg"
            else:
                out = f"{args.output_prefix}-{bi + 1}.jpg"
            make_grid(batch, out, args.cols, start_index=bi * per_grid)
            outputs.append(out)

    print(f"Rendered {len(images)} slides into {len(outputs)} grid image(s):")
    for o in outputs:
        print(f"  {o}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
