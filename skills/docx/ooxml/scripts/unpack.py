#!/usr/bin/env python3
"""Unpack an OOXML file (.docx/.xlsx/.pptx) into a directory of its parts.

Usage:
    python ooxml/scripts/unpack.py <office_file> <output_directory>

The archive is extracted as-is (no XML reformatting) so it round-trips
byte-for-byte with pack.py and significant whitespace is preserved. After
unpacking, a random RSID is suggested for tracked changes — reuse it on the
w:rsidR attribute of new runs so Word groups your edits as one revision.
"""

import os
import random
import sys
import zipfile


def suggest_rsid() -> str:
    return "".join(random.choice("0123456789ABCDEF") for _ in range(8))


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: python unpack.py <office_file> <output_directory>")
        return 1

    src, out_dir = sys.argv[1], sys.argv[2]

    if not os.path.isfile(src):
        print(f"Error: file not found: {src}")
        return 1
    if not zipfile.is_zipfile(src):
        print(f"Error: not a valid OOXML/zip file: {src}")
        return 1

    os.makedirs(out_dir, exist_ok=True)

    with zipfile.ZipFile(src) as z:
        bad = z.testzip()
        if bad is not None:
            print(f"Error: corrupt entry in archive: {bad}")
            return 1
        names = z.namelist()
        z.extractall(out_dir)

    print(f"Unpacked {len(names)} parts into {out_dir}/")
    for name in sorted(names):
        print(f"  {name}")

    rsid = suggest_rsid()
    print()
    print(f"Suggested RSID for tracked changes: {rsid}")
    print('Use it on new runs, e.g. <w:r w:rsidR="%s">...</w:r>' % rsid)
    print("Main content: %s/word/document.xml" % out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
