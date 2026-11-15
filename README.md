# ILCA Leagues pages

Public competition pages of the Israel Climbing Federation (התאחדות הטיפוס בישראל), season 2026/27.
Design by Noam ("דף תוצאות התאחדות הטיפוס"); built as plain HTML for GitHub Pages and embedded in ilca.org.il with an iframe (`embed.html`).

Pages
- `index.html` – landing page, all leagues (תחרויות לאומיות)
- `open.html`, `open-results.html` – הליגה הפתוחה and its results
- `national.html`, `national-results.html`, `national-standings.html`, `national-season.html` – הליגה הארצית, its competition results, the league table (תוצאות הליגה) and the full season list
- `elite.html` – ליגת העל
- `championships.html` – אליפויות ישראל

Data (routine updates change only these)
- `data/calendar.json` – all competitions of all leagues (league, kind, dates, registration…)
- `data/results.json` – results PDF links and Drive folders per league
- `data/updates.json` – lines for the updates bar on the landing page
- `data/national-leaders.json`, `data/national-photos.json` – הליגה הארצית leaders table and slideshow (empty until filled)

Where pages link to: `ILCA_PAGES` at the top of `assets/site.js` (ilca.org.il address of each page).
`tools/build_pages.py` regenerates the league pages.
