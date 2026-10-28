#!/usr/bin/env python3
"""Pack a directory of OOXML parts back into an Office file.

Usage:
    python ooxml/scripts/pack.py <input_directory> <office_file>

Re-zips an unpacked directory (produced by unpack.py) into a valid .docx/
.xlsx/.pptx. [Content_Types].xml is written first (a convention some strict
readers expect), the rest follow. Uses DEFLATE compression.
"""

import os
import sys
import zipfile


def collect_files(src_dir: str):
    files = []
    for root, _, names in os.walk(src_dir):
        for name in names:
            full = os.path.join(root, name)
            arc = os.path.relpath(full, src_dir).replace(os.sep, "/")
            files.append((full, arc))
    # [Content_Types].xml first, then everything else in stable order.
    files.sort(key=lambda p: (p[1] != "[Content_Types].xml", p[1]))
    return files


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python pack.py <input_directory> <office_file>")
        return 1

    src_dir, out_file = sys.argv[1], sys.argv[2]

    if not os.path.isdir(src_dir):
        print(f"Error: not a directory: {src_dir}")
        return 1

    files = collect_files(src_dir)
    if not any(arc == "[Content_Types].xml" for _, arc in files):
        print("Warning: [Content_Types].xml not found — output may be invalid.")

    with zipfile.ZipFile(out_file, "w", zipfile.ZIP_DEFLATED) as z:
        for full, arc in files:
            z.write(full, arc)

    print(f"Packed {len(files)} parts into {out_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
