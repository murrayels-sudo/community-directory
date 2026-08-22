# Community Directory — offline support services app

## What this is
A PWA (installable web app) for iPhone, iPad, and Android that:
- Works fully offline once opened at least once with a connection
- Lets people search by organisation name or filter by suburb
- Shows an "Open now" indicator where hours/days are parseable
- Tap-to-call, tap-for-directions, tap-for-website, tap-to-email
- Has a "Show nearby areas" button that reveals services in suburbs
  within ~10km when someone's chosen suburb doesn't have what they need
- Has a "Share" button showing a QR code so people can pass the app on
- Automatically checks for a newer directory.json whenever the device
  does have a connection, and updates everyone's copy

## Deploying (same pattern as your other apps)
1. Push this whole folder to a GitHub Pages repo (e.g.
   `murrayels-sudo.github.io/directory/`).
2. Send people the URL. On iPhone: open in Safari → Share → "Add to
   Home Screen". On Android: open in Chrome → menu → "Install app" /
   "Add to Home screen".
3. Once added, it opens like a normal app icon — no browser chrome,
   works with the phone in airplane mode.

## Updating the directory
Two ways to convert your spreadsheet — use whichever's easier:

**Option A — in your browser (no terminal needed)**
1. Open `admin-convert.html` directly in any browser (double-click it,
   or host it privately anywhere — it's not linked from the main app).
2. Drag your CSV or Excel file onto the page.
3. Check the preview, click "Download directory.json".
4. Replace the old `directory.json` in your GitHub Pages folder with
   the downloaded one, and push.

Runs entirely client-side — nothing is uploaded anywhere. Don't put
this file somewhere publicly linked, since anyone with the URL could
use it to generate a directory.json (though they'd still need push
access to your repo to actually publish it).

**Option B — command line**
1. Keep your master list in Excel or CSV, with these column headers
   (any order): `Name of Org, Address, Suburb, Email, Phone, Website,
   Opening Times, Days, Services Provided`
   Optional: `Temporary Closure` — leave blank normally.
2. Run:
   ```
   python3 convert_csv_to_json.py your_file.csv
   ```
   (or `.xlsx` — for old `.xls` files, just "Save As" xlsx first in
   Excel)
3. This overwrites `directory.json` in this folder.

**Either way, finish with:**
4. Push the updated `directory.json` to GitHub.
5. Every installed app checks this file next time it has a connection
   and updates itself — no reinstall needed for users.

## Notes
- The app name/icon is deliberately neutral ("Community Directory")
  rather than DV-specific, in case someone's phone is checked by an
  abusive partner. You can change the wording in `manifest.json` and
  `index.html` if you'd prefer something else.
- "Days" field works best as one of: `Mon-Fri`, `7 days`, `Tue, Thu`,
  or similar. "Opening Times" works best as `9:00am-5:00pm` or
  `24 hours`. Anything the app can't confidently parse just won't show
  an open/closed dot — the hours text still displays normally.
- All data stays on the device (localStorage) plus whatever GitHub
  Pages serves — no backend, no accounts, no tracking.

## Marking a service as temporarily closed
If a service closes for a while (renovation, staff shortage, etc),
put a short note in the `Temporary Closure` column — e.g. "Temporarily
closed" or "Closed for renovations" — and leave everything else about
that listing as-is (address, hours, phone) so people can still see
when it normally reopens or call ahead to check.

When that column has text, the app automatically:
- Shows a clear amber banner with your exact wording across the top
  of that card
- Adds a faint diagonal watermark of the same text across the card
- Hides the normal "Open now" indicator for that listing (since it
  would contradict the closure notice)
- Keeps the phone number, address, and other details visible, in case
  someone wants to call ahead or check back later

To reopen a service, just clear the `Temporary Closure` cell and
re-run the converter — the banner disappears automatically.

## Nearby areas (suburb-coordinates.json)
The "Show nearby areas" button needs to know where each suburb is.
This lives in `suburb-coordinates.json` — a small file mapping suburb
name to latitude/longitude, separate from `directory.json` since it
rarely changes (it's per-suburb, not per-organisation).

Whenever you add a service in a suburb that hasn't appeared before:
```
python3 geocode_suburbs.py
```
This reads the suburb list out of `directory.json`, looks up
coordinates for any suburb not already in `suburb-coordinates.json`
(free OpenStreetMap lookup, no signup needed), and saves them. It's
safe to run any time — it only fills in what's missing.

If a suburb can't be found automatically, or you want to fix one,
just edit `suburb-coordinates.json` directly:
```json
"Erina": { "lat": -33.4400, "lng": 151.3930 }
```
Push the updated file to GitHub along with `directory.json` — same
deploy step as usual. If a suburb has no entry in this file, the
"nearby areas" button just won't appear for it — everything else
keeps working normally.
