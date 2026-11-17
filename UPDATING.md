# Updating the ILCA Leagues pages

Instructions for whoever updates this site, a person or Claude. Read all of it before changing anything.

The site is plain HTML on GitHub Pages: https://goony663.github.io/ILCA-Leagues/ (repo `goony663/ILCA-Leagues`, branch `main`).
Each page is embedded in its own ilca.org.il WordPress page with an iframe (`embed.html` holds the snippet).
**Pushing to `main` is publishing.** GitHub Pages redeploys in about a minute, and the WordPress pages show the change right away (visitors may need Ctrl+Shift+R).
Nothing has to be changed in WordPress for a routine update.

## Who updates what

Two people update this site, each through their own Claude: the federation's competitions manager and Noam.
They keep their updates separate, so always:
1. `git pull` (or clone fresh) before starting. The other person may have pushed since your last update.
2. Change only what the request asks for.
3. Make one commit per update and describe it clearly in the commit message, e.g. "Calendar: add National League boulder 5.12".
4. If `git push` is rejected, run `git pull --rebase` and push again. Never force-push.

## Map of the repo

| Page | File | Built from |
|---|---|---|
| תחרויות לאומיות (landing) | `index.html` | hand-written; reads `data/calendar.json`, `data/updates.json` |
| ליגת העל | `elite.html` | **generated** by `tools/elite/build_elite.py` (never edit elite.html by hand) |
| הליגה הפתוחה / results | `open.html`, `open-results.html` | **generated** by `tools/build_pages.py` |
| הליגה הארצית / results / full season list | `national.html`, `national-results.html`, `national-season.html` | **generated** by `tools/build_pages.py` |
| אליפויות ישראל | `championships.html` | **generated** by `tools/build_pages.py` |

The generated pages load their data in the browser, so **changing a file in `data/` needs no rebuild.**
Rebuild only when you change a page's layout or text, which means editing `tools/build_pages.py` and running `python3 tools/build_pages.py`.

The shared files:
- `assets/site.css`: design.
- `assets/site.js`: helpers and `ILCA_PAGES`, the ilca.org.il address of every page. Links between pages use these addresses, so if a WordPress page address changes, update it there.

**After any change to `assets/site.css` or `assets/site.js`, bump the version:**
1. Set `V` at the top of `tools/build_pages.py` to a new value, e.g. `20261120a`.
2. Replace the old `?v=` value in `index.html` (search for `?v=`).
3. Run both build scripts.

Otherwise browsers keep the old cached files, which already caused broken back-links once.

Design: Noam's "דף תוצאות התאחדות הטיפוס" (Claude Design). Keep the existing look; don't restyle when updating data.

## Data files

### `data/calendar.json`: all competitions, all leagues

Sources (two Google Sheets):
- **הליגה הפתוחה**: "רשימת תחרויות הליגה הפתוחה- עונת 2027-2026" (id `1t7v-caJJMWF6D6ToL2j2286n3eHruvNp1NIqUqOy0k8`), tab **תחרויות לפרסום** only. Ignore the סטודנטים tab and the "תחרויות נוספות יפתחו בקרוב" row. When registration opening is "בקרוב", add `"note": "פתיחת הרישום: בקרוב"`. A month with no exact date gets `approx`.
- **All other leagues** (national, elite, championships): "רשימת תחרויות ליגה ארצית וסימולציות- עונת 2027-2026" (id `1nf2STPq1VxF4VZF2PKiMU252FJIoy8kPzrXVWVB2T_E`), one tab per league.
The sheet does not update the site by itself. When asked to update the calendar, read the sheet, then rewrite the matching items and set `"updated"` to today.

Each item looks like this:

```json
{"league": "national", "kind": "boulder", "start": "2026-12-05", "end": "2026-12-05",
 "title": "venue", "sub": "short description", "cats": "categories",
 "regClose": "2026-11-28", "hours": "...", "note": "..."}
```

| Field | Meaning |
|---|---|
| `league` | `national` / `elite` / `open` / `champ` |
| `kind` | `boulder` / `lead` / `sim` (simulation) |
| `status` | `"בוטלה"` for a cancelled competition. Keep the item; it is shown struck through. |
| `approx` | text such as `"מאי–יוני"` when there's no exact date yet. It isn't shown as an upcoming competition. |
| `fee`, `feeMember` | Open League only |
| `regOpen`, `regCloseTime`, `link` | championships; registration status is computed from these |

Quirks of the sheet:
- Merged cells mean a value applies to several rows.
- Some dates are text, not dates.
- In the adults boulder championship row the start and end dates were swapped. Always sanity-check that start ≤ end.

### `data/updates.json`: the scrolling updates bar (chyron) on the landing page

`items` is a list of `[title, text]` pairs, e.g. `["ליגת העל בולדר 2 · בוגרים", "X במקום הראשון, Y במקום השני, Z במקום השלישי"]`.
After every competition, replace the old podium lines with the new ones and remove lines that are no longer current.

### `data/results.json`: results links for the Open and National leagues

Per league there is a `drive` folder link and `items`. Each item is one competition: `kind`, `start`, `title`, `sub`, `cats`, `pdf` (link to the results PDF; empty = not yet).

### `data/national-leaders.json`, `data/national-photos.json`

`national-leaders.json` holds the National League leaders table. `national-photos.json` holds the slideshow photos, shown at the bottom of the landing page (`index.html`). Both are empty until there's content; the pages hide empty sections.
Photo credit: הילארי חכמון.

## Elite League (ליגת העל) after each competition

All of the Elite page's data is in `tools/elite/`:
- `meta.json`: `upcoming` (next competitions; keep in sync with `calendar.json`) and `past` (competitions with results, plus their Drive folder id; the page's "כל התוצאות" button opens that folder). It also has a `pdf` section with round-PDF ids. The page no longer shows those links (removed on request), so it doesn't need updating.
- `results_all.json`: one row per athlete per competition, in the same format as the national rankings dataset.
- `u17group.json`: the joint U15+U17 ranking. The U17 podium cards use it, with U15 athletes tagged.

The page shows podiums for בוגרים / בוגרות (the open pool, adults+U21+U19) and U17 only.

Steps:
1. **Get the files.** The results-system xlsx files (one per round) and the PDFs are in the competition's Google Drive folder.
   Download the xlsx files to a scratch folder outside the repo.
   **Never commit xlsx files; they contain ID numbers.**
2. **Compute the rows.**
   - Boulder: `python3 -I tools/results/build_boulder.py B-L3 r1.xlsx r2.xlsx > /tmp/rows.json`
   - Lead: `python3 -I tools/results/build_lead.py L-L2 r1.xlsx r2.xlsx > /tmp/rows.json`

   Competition ids: `B-L1`, `B-L2`, `B-L3` (boulder), `L-L1`, `L-L2` (lead).
3. **Check against the official PDFs before using the rows.** Compare the top places of each round-2 PDF (בוגרים, בוגרות) and the U17 PDFs with the computed places.
   They must match exactly. Rounds are matched by name + gender: the round-2 files have no ID numbers, and bib numbers can change between rounds.
   This step caught a real error in B-L2. Don't skip it.
4. **Add the rows to `results_all.json`.** Remove any old rows of that competition first, then append the new ones.
5. **Compute the U17 group** (it writes into `u17group.json` itself):
   - Boulder: `python3 -I tools/results/u17group.py B-L3 boulder r1.xlsx`
   - Lead: `python3 -I tools/results/u17group.py L-L2 lead r1.xlsx r2.xlsx`
6. **Update `meta.json`:** add the competition to `past`, with its Drive folder id. Look at an existing one for the format.
7. **Rebuild:** `python3 tools/elite/build_elite.py`. It refuses to build if a 9-digit number (an ID) appears in the data.
8. **Update the chyron:** edit the podium lines in `data/updates.json`. The Elite page builds its own chyron automatically.
9. Run the privacy check, commit, push, and check the live page (see below).

The same results also feed the national rankings (a separate repo, `goony663/National-Rankings`, with its own procedure). Updating this site does not update the rankings, and vice versa.

## Naming rules (Hebrew text)

- A round is always **סבב** (סבב 1, סבב 2), never "סיבוב" or "גמר".
- Groups are **בוגרים** and **בוגרות**, not "גברים פתוח" / "נשים פתוח".
- Competition names: "ליגת העל בולדר 1", "ליגת העל בולדר 2", "ליגת העל הובלה 1", and so on.
- Never use Times New Roman for Hebrew. The site's fonts are Karantina (headings) and Heebo, in `assets/fonts/`.

## Privacy (required)

- ID numbers (ת.ז) and birth dates must never appear in the repo.
- Before every push, run `grep -rlE '[0-9]{9}' --include=*.json --include=*.html .`. It must print nothing.
- Never commit xlsx files.

## Checking

- After pushing, wait about a minute, then open the changed page at https://goony663.github.io/ILCA-Leagues/<page>.html.
  If possible, also open its ilca.org.il page, and check that the change is there and nothing else broke.
- WordPress admin is for reading only. Don't change WordPress pages unless explicitly asked.

## For Claude: before you push

Tell the person what you are about to publish, in a short summary:
- which pages and files change;
- for results, the podiums;
- for the calendar, the competitions added, changed or removed.

Push after they confirm.
