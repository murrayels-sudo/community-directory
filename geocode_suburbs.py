#!/usr/bin/env python3
"""
Looks up latitude/longitude for suburbs and writes/updates
suburb-coordinates.json, which powers the "nearby areas" feature in
the app.

USAGE:
    python3 geocode_suburbs.py

By default this reads every unique suburb out of directory.json and
looks up coordinates for any that aren't already in
suburb-coordinates.json (so it's safe to re-run any time \u2014 it only
fills in what's missing, it never overwrites existing entries).

To add or fix a suburb manually instead of via lookup, just edit
suburb-coordinates.json directly:

    "Erina": { "lat": -33.4400, "lng": 151.3930 }

This uses the free OpenStreetMap Nominatim geocoding service. Be
patient \u2014 it deliberately waits a second between lookups, as required
by Nominatim's usage policy.
"""

import json
import sys
import time
import urllib.request
import urllib.parse
from pathlib import Path

DIRECTORY_PATH = Path("directory.json")
COORDS_PATH = Path("suburb-coordinates.json")
STATE_COUNTRY_SUFFIX = "NSW, Australia"  # adjust if you expand beyond NSW
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "CommunityDirectoryApp/1.0 (community support directory; contact via GitHub)"


def load_json(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def geocode(suburb_name):
    query = f"{suburb_name}, {STATE_COUNTRY_SUFFIX}"
    params = urllib.parse.urlencode({"q": query, "format": "json", "limit": 1})
    url = f"{NOMINATIM_URL}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=10) as resp:
        results = json.loads(resp.read().decode("utf-8"))
    if not results:
        return None
    return {"lat": round(float(results[0]["lat"]), 5), "lng": round(float(results[0]["lon"]), 5)}


def main():
    if not DIRECTORY_PATH.exists():
        sys.exit("directory.json not found \u2014 run this from the project folder.")

    directory = load_json(DIRECTORY_PATH, {"orgs": []})
    suburbs = sorted(set(
        (o.get("suburb") or "").strip()
        for o in directory.get("orgs", [])
        if (o.get("suburb") or "").strip()
    ))

    coords = load_json(COORDS_PATH, {})
    missing = [s for s in suburbs if s not in coords]

    if not missing:
        print("Every suburb in directory.json already has coordinates. Nothing to do.")
        return

    print(f"Looking up {len(missing)} suburb(s): {', '.join(missing)}")

    for i, suburb in enumerate(missing):
        print(f"  [{i+1}/{len(missing)}] {suburb} ...", end=" ", flush=True)
        try:
            result = geocode(suburb)
        except Exception as e:
            print(f"failed ({e})")
            continue

        if result is None:
            print("not found \u2014 add it manually if you know the coordinates")
        else:
            coords[suburb] = result
            print(f"{result['lat']}, {result['lng']}")

        if i < len(missing) - 1:
            time.sleep(1)  # Nominatim usage policy: max 1 request/second

    COORDS_PATH.write_text(json.dumps(coords, indent=2, sort_keys=True), encoding="utf-8")
    print(f"\nSaved {len(coords)} suburb(s) to {COORDS_PATH.resolve()}")


if __name__ == "__main__":
    main()
