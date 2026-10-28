#!/usr/bin/env python3
"""Recalculate all formulas in an Excel workbook and report any errors.

Usage:
    python recalc.py <excel_file> [timeout_seconds]

How it works:
  - Drives a headless LibreOffice to open and recalculate the workbook, then
    save it back in place. Recalc-on-load is forced via a throwaway LibreOffice
    user profile (created on first run) whose registry sets the Calc recalc
    mode to "always" — so no macro installation and no changes to your real
    LibreOffice profile.
  - Then scans every cell with openpyxl for Excel error values and counts
    formulas, returning a JSON summary on stdout.

Requires: LibreOffice (`soffice`) and openpyxl. Works on macOS and Linux.

Output (JSON):
    {
      "status": "success" | "errors_found" | "error",
      "total_errors": <int>,
      "total_formulas": <int>,
      "error_summary": { "#REF!": {"count": N, "locations": ["Sheet1!B5", ...]} }
    }
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

ERROR_TOKENS = {
    "#REF!", "#DIV/0!", "#VALUE!", "#NAME?", "#N/A", "#NULL!",
    "#NUM!", "#ERROR!", "#SPILL!", "#CALC!", "#GETTING_DATA",
}


def find_soffice():
    if os.environ.get("SOFFICE_PATH") and os.path.exists(os.environ["SOFFICE_PATH"]):
        return os.environ["SOFFICE_PATH"]
    for c in (
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",  # macOS
        shutil.which("soffice"),
        shutil.which("libreoffice"),
        "/usr/bin/soffice",
        "/usr/bin/libreoffice",
    ):
        if c and os.path.exists(c):
            return c
    return None


# Registry that forces "recalculate on load" for both OOXML and ODF formulas
# (0 = Always, 1 = Never, 2 = Prompt).
_REGMOD = """<?xml version="1.0" encoding="UTF-8"?>
<oor:items xmlns:oor="http://openoffice.org/2001/registry" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
 <item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop></item>
 <item oor:path="/org.openoffice.Office.Calc/Formula/Load"><prop oor:name="ODFRecalcMode" oor:op="fuse"><value>0</value></prop></item>
</oor:items>
"""


def make_profile():
    """Create a throwaway LibreOffice user profile with recalc-on-load set."""
    prof = tempfile.mkdtemp(prefix="recalc-loprofile-")
    user_dir = os.path.join(prof, "user")
    os.makedirs(user_dir, exist_ok=True)
    with open(os.path.join(user_dir, "registrymodifications.xcu"), "w", encoding="utf-8") as f:
        f.write(_REGMOD)
    return prof


def recalc(path, soffice, timeout):
    prof = make_profile()
    outdir = tempfile.mkdtemp(prefix="recalc-out-")
    try:
        cmd = [
            soffice,
            f"-env:UserInstallation=file://{prof}",
            "--headless", "--invisible", "--nologo", "--nofirststartwizard",
            "--calc",
            "--convert-to", "xlsx:Calc MS Excel 2007 XML",
            "--outdir", outdir,
            path,
        ]
        subprocess.run(cmd, check=True, timeout=timeout,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        produced = os.path.join(outdir, os.path.splitext(os.path.basename(path))[0] + ".xlsx")
        if not os.path.isfile(produced):
            raise RuntimeError("LibreOffice did not produce a recalculated file")
        shutil.move(produced, path)
    finally:
        shutil.rmtree(prof, ignore_errors=True)
        shutil.rmtree(outdir, ignore_errors=True)


def scan(path):
    from openpyxl import load_workbook

    formulas = 0
    wb = load_workbook(path, data_only=False)
    for ws in wb.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                v = cell.value
                if (isinstance(v, str) and v.startswith("=")) or cell.data_type == "f":
                    formulas += 1
    wb.close()

    errors = {}
    total = 0
    wbv = load_workbook(path, data_only=True)
    for ws in wbv.worksheets:
        for row in ws.iter_rows():
            for cell in row:
                v = cell.value
                if isinstance(v, str) and v in ERROR_TOKENS:
                    total += 1
                    loc = f"{ws.title}!{cell.coordinate}"
                    entry = errors.setdefault(v, {"count": 0, "locations": []})
                    entry["count"] += 1
                    if len(entry["locations"]) < 50:
                        entry["locations"].append(loc)
    wbv.close()
    return formulas, total, errors


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "Usage: python recalc.py <excel_file> [timeout_seconds]"}))
        return 1

    path = os.path.abspath(sys.argv[1])
    timeout = int(sys.argv[2]) if len(sys.argv) > 2 else 120

    if not os.path.isfile(path):
        print(json.dumps({"status": "error", "message": f"file not found: {path}"}))
        return 1

    soffice = find_soffice()
    if not soffice:
        print(json.dumps({"status": "error", "message": "LibreOffice (soffice) not found. Set SOFFICE_PATH."}))
        return 1

    try:
        recalc(path, soffice, timeout)
    except subprocess.TimeoutExpired:
        print(json.dumps({"status": "error", "message": f"recalculation timed out after {timeout}s"}))
        return 1
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"status": "error", "message": f"recalculation failed: {e}"}))
        return 1

    try:
        formulas, total, errors = scan(path)
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"status": "error", "message": f"recalc ok but error scan failed: {e}"}))
        return 1

    result = {
        "status": "errors_found" if total else "success",
        "total_errors": total,
        "total_formulas": formulas,
    }
    if total:
        result["error_summary"] = errors
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
