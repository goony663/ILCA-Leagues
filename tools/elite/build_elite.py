"""Builds elite.html (ליגת העל page) from the files in this folder.

  python3 tools/elite/build_elite.py

Inputs (all in tools/elite/):
  template.html     page design (Noam's style); placeholders __FONTS__ __LOGO__ __RESULTS__ __META__
  meta.json         calendar: "upcoming" (next comps), "past" (comps with results), "pdf" (PDF links per comp/gender/category)
  results_all.json  one row per athlete per competition: comp, gender (M/W), cat (ADULT/U21/U19/U17), pool, athlete, club, place
                    (same rows as the national rankings' data/results.json; NO ID numbers or birth dates, ever)
  u17group.json     joint U15+U17 ranking per comp and gender (used for the U17 podium cards, U15 athletes tagged)
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
p = lambda f: os.path.join(HERE, f)

def rerank(rows):
    rows = sorted(rows, key=lambda r: r['place']); out = []; prev = None; place = 0
    for i, r in enumerate(rows):
        if r['place'] != prev: place = i + 1; prev = r['place']
        out.append(dict(r, place=place))
    return out

res = json.load(open(p('results_all.json')))
compact = {}
for comp in sorted({r['comp'] for r in res}):
    cr = [r for r in res if r['comp'] == comp]
    d = {}
    for g in 'MW':
        gr = [r for r in cr if r['gender'] == g]
        open_ = sorted([r for r in gr if r['pool'] == 'open'], key=lambda r: r['place'])
        tabs = {'OPEN': open_}
        for c in ('U21', 'U19', 'U17'):
            own = [r for r in gr if r['pool'] == c]
            if own: tabs[c] = sorted(own, key=lambda r: r['place'])
            else:
                sub = [r for r in open_ if r['cat'] == c]   # boulder: youth places from their order in the open pool
                if sub: tabs[c] = rerank(sub)
        d[g] = {k: [[r['place'], r['athlete'], r['club'], r['cat']] for r in v] for k, v in tabs.items()}
    compact[comp] = d
u17 = json.load(open(p('u17group.json')))
for comp, v in u17.items():
    for g, rows in v.items():
        if comp in compact: compact[comp][g]['U17'] = rows

# asset version: same as the other pages
v = re.search(r"V='([^']+)'", open(os.path.join(HERE, '..', 'build_pages.py')).read()).group(1)
t = open(p('template.html')).read()
t = (t.replace('__FONTS__', open(p('fonts.css')).read())
      .replace('__LOGO__', open(p('logo.svg')).read())
      .replace('__RESULTS__', json.dumps(compact, ensure_ascii=False, separators=(',', ':')))
      .replace('__META__', open(p('meta.json')).read()))
t = t.replace('</body>', f'<script src="assets/site.js?v={v}"></script>\n</body>', 1)
assert not re.search(r'\b\d{9}\b', t), 'ID number found in page data'
open(os.path.join(ROOT, 'elite.html'), 'w').write(t)
print('elite.html built:', {c: {g: {k: len(x) for k, x in d.items()} for g, d in dd.items()} for c, dd in compact.items()})
