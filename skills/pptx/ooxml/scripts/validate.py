#!/usr/bin/env python3
"""Validate an unpacked OOXML directory.

Usage:
    python ooxml/scripts/validate.py <unpacked_dir> [--original <office_file>]

Checks that every XML/.rels part is well-formed. With --original, also reports
parts added or removed versus the original package (a quick sanity check after
editing). Exits non-zero if any part is malformed.
"""

import argparse
import os
import sys
import zipfile
from xml.dom import minidom
from xml.parsers.expat import ExpatError


def xml_parts(root):
    for dirpath, _, names in os.walk(root):
        for n in names:
            if n.endswith((".xml", ".rels")):
                yield os.path.join(dirpath, n)


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate an unpacked OOXML directory.")
    ap.add_argument("directory")
    ap.add_argument("--original", help="original .pptx/.docx to compare part lists against")
    args = ap.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Error: not a directory: {args.directory}")
        return 1

    errors = []
    checked = 0
    for path in xml_parts(args.directory):
        checked += 1
        try:
            minidom.parse(path)
        except ExpatError as e:
            errors.append(f"{os.path.relpath(path, args.directory)}: {e}")
        except Exception as e:  # noqa: BLE001 - surface any parse failure
            errors.append(f"{os.path.relpath(path, args.directory)}: {e}")

    print(f"Checked {checked} XML parts.")
    if errors:
        print(f"\n{len(errors)} malformed XML part(s):")
        for e in errors:
            print(f"  [X] {e}")
    else:
        print("All XML parts are well-formed. [OK]")

    if args.original:
        if not zipfile.is_zipfile(args.original):
            print(f"\nWarning: --original is not a valid zip: {args.original}")
        else:
            with zipfile.ZipFile(args.original) as z:
                orig = set(z.namelist())
            current = set()
            for dp, _, names in os.walk(args.directory):
                for n in names:
                    rel = os.path.relpath(os.path.join(dp, n), args.directory).replace(os.sep, "/")
                    current.add(rel)
            added = sorted(current - orig)
            removed = sorted(orig - current)
            if added:
                print("\nParts added vs original:")
                for p in added:
                    print(f"  + {p}")
            if removed:
                print("\nParts removed vs original:")
                for p in removed:
                    print(f"  - {p}")
            if not added and not removed:
                print("\nPart list matches original. [OK]")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
