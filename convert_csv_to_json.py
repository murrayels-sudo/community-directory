#!/usr/bin/env python3
"""
Converts your CSV or Excel spreadsheet into directory.json for the
Community Directory app.

USAGE:
    python3 convert_csv_to_json.py my_services.csv
    python3 convert_csv_to_json.py my_services.xlsx

Your spreadsheet's column headers should be (case-insensitive, order
doesn't matter):
    Name of Org, Address, Suburb, Email, Phone, Website,
    Opening Times, Days, Services Provided

Optional column:
    Temporary Closure — leave blank normally. If a service is closed,
    under renovation, etc, put a short note here (e.g. "Temporarily
    closed" or "Closed for renovations") and the app will show it
    clearly over that listing.

After running this, copy the generated directory.json over the old one
in your GitHub Pages folder and push. Every installed app will pick up
the change automatically next time it has an internet connection.
"""

import sys
import json
import csv
from datetime import datetime, timezone
from pathlib import Path

COLUMN_MAP = {
    "name of org": "name",
    "org": "name",
    "organisation": "name",
    "organization": "name",
    "name": "name",
    "address": "address",
    "suburb": "suburb",
    "email": "email",
    "phone": "phone",
    "phone number": "phone",
    "website": "website",
    "opening times": "hours",
    "hours": "hours",
    "days": "days",
    "services provided": "services",
    "services": "services",
    "temporary closure": "closureNote",
    "temporarily closed": "closureNote",
    "closure": "closureNote",
    "closed": "closureNote",
    "status": "closureNote",
}


def normalize_row(raw_row):
    out = {}
    for key, value in raw_row.items():
        if key is None:
            continue
        norm_key = COLUMN_MAP.get(key.strip().lower())
        if norm_key:
            out[norm_key] = (str(value).strip() if value is not None else "")
    return out


def read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return [normalize_row(row) for row in reader]


def read_excel(path):
    try:
        import openpyxl
    except ImportError:
        sys.exit("Excel support needs openpyxl. Run: pip install openpyxl --break-system-packages")

    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        return []
    headers = [str(h).strip() if h is not None else "" for h in rows[0]]
    result = []
    for row in rows[1:]:
        raw = dict(zip(headers, row))
        result.append(normalize_row(raw))
    return result


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    src = Path(sys.argv[1])
    if not src.exists():
        sys.exit(f"File not found: {src}")

    if src.suffix.lower() == ".csv":
        rows = read_csv(src)
    elif src.suffix.lower() in (".xlsx", ".xlsm"):
        rows = read_excel(src)
    else:
        sys.exit("Please provide a .csv or .xlsx file (for old .xls, save as .xlsx first).")

    orgs = []
    for i, row in enumerate(rows, start=1):
        if not row.get("name"):
            continue
        orgs.append({
            "id": str(i),
            "name": row.get("name", ""),
            "address": row.get("address", ""),
            "suburb": row.get("suburb", ""),
            "email": row.get("email", ""),
            "phone": row.get("phone", ""),
            "website": row.get("website", ""),
            "days": row.get("days", ""),
            "hours": row.get("hours", ""),
            "services": row.get("services", ""),
            "closureNote": row.get("closureNote", ""),
        })

    now = datetime.now(timezone.utc)
    output = {
        "version": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "updated_display": now.strftime("%-d %b %Y"),
        "orgs": orgs,
    }

    out_path = Path("directory.json")
    out_path.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(f"Wrote {len(orgs)} organisations to {out_path.resolve()}")


if __name__ == "__main__":
    main()
