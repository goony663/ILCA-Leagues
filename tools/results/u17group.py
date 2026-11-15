"""Joint U15+U17 ranking (the U17 climbing group) for one competition → tools/elite/u17group.json

  python3 -I tools/results/u17group.py COMP_ID boulder round1.xlsx
  python3 -I tools/results/u17group.py COMP_ID lead round1.xlsx round2.xlsx

Boulder: by round-1 score, ties by fewer top attempts then fewer zone attempts (U17 has one round).
Lead: qualification points (geometric mean of route places) over U15+U17, then round 2 height, ties by round-1 place.
"""
import sys, os, json, openpyxl
YES = {'כן','yes','Yes','TRUE','True',True,1,'1','+','v','V','✓'}
GRP = {'בנים U17':'U17','בנות U17':'U17','בנים U15':'U15','בנות U15':'U15'}
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'elite', 'u17group.json')
def load(p):
    ws = openpyxl.load_workbook(p, data_only=True)['תוצאות']; it = ws.iter_rows(values_only=True); hdr = next(it)
    return [dict(zip(hdr, r)) for r in it if r[1]]
def comp_places(items, key):
    s = sorted(items, key=key, reverse=True); out, prev, place = {}, object(), 0
    for i, d in enumerate(s):
        k = key(d)
        if k != prev: place, prev = i + 1, k
        out[id(d)] = place
    return out
def frac_places(items, key):
    s = sorted(items, key=key, reverse=True); out, i = {}, 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and key(s[j+1]) == key(s[i]): j += 1
        for k in range(i, j+1): out[id(s[k])] = (i + 1 + j + 1) / 2
        i = j + 1
    return out
num = lambda v: v if isinstance(v, (int, float)) else 0
row = lambda d, place: [place, str(d['שם']).strip(), str(d['שם אגודה'] or '').strip(), GRP[d['קטגוריה']]]
def boulder(r1p):
    rows = [d for d in load(r1p) if GRP.get(d['קטגוריה']) and d.get('דגל') != 'DNS']
    out = {}
    for g in 'MW':
        pool = [d for d in rows if d['מגדר'] == g]
        key = lambda d: ((d['ניקוד סופי'] if isinstance(d['ניקוד סופי'], (int, float)) else -1),
                         -sum(num(d.get(f'מ{i} Top')) for i in range(1, 7)), -sum(num(d.get(f'מ{i} Zone')) for i in range(1, 7)))
        pl = comp_places(pool, key)
        out[g] = sorted(row(d, pl[id(d)]) for d in pool)
    return out
def heights(d, n):
    hs = []
    for i in range(1, n + 1):
        hold, t = d.get(f'מ{i} אחיזה'), d.get(f'מ{i} ראש')
        top = t in YES or (isinstance(t, str) and t.strip().upper() in ('TOP', 'T', 'כן'))
        if hold in (None, '') and not top: hs.append(None); continue
        v = float(str(hold).replace('+', '')) if hold not in (None, '') else 0.0
        plus = d.get(f'מ{i} פלוס') in YES or str(hold).endswith('+')
        hs.append((1 if top else 0, v, 1 if plus else 0))
    return hs
def lead(r1p, r2p):
    r1 = [d for d in load(r1p) if GRP.get(d['קטגוריה']) and d.get('דגל') != 'DNS']
    n = max(int(k[1:].split()[0]) for k in r1[0] if isinstance(k, str) and k.startswith('מ') and k.endswith('אחיזה'))
    for d in r1: d['h'] = heights(d, n)
    r2 = {(str(d['שם']).strip(), d['מגדר']): d for d in load(r2p)}
    for d in r2.values(): d['h'] = heights(d, 1)
    out = {}
    for g in 'MW':
        pool = [d for d in r1 if d['מגדר'] == g and any(h is not None for h in d['h'])]
        qp = {id(d): 1.0 for d in pool}
        for r in range(n):
            on = [d for d in pool if d['h'][r] is not None]
            pl = frac_places(on, lambda d: d['h'][r]); last = (len(on) + 1 + len(pool)) / 2
            for d in pool: qp[id(d)] *= pl.get(id(d), last)
        qp = {k: v ** (1 / n) for k, v in qp.items()}
        r1pl = comp_places(pool, lambda d: -round(qp[id(d)], 3))
        k = lambda d: (str(d['שם']).strip(), g)
        fin = [d for d in pool if k(d) in r2 and r2[k(d)]['h'][0] is not None]
        rest = [d for d in pool if d not in fin]
        place = comp_places(fin, lambda d: (r2[k(d)]['h'][0], -r1pl[id(d)]))
        place.update({i: len(fin) + v for i, v in comp_places(rest, lambda d: -r1pl[id(d)]).items()})
        out[g] = sorted(row(d, place[id(d)]) for d in pool)
    return out
if __name__ == '__main__':
    comp, disc = sys.argv[1], sys.argv[2]
    res = boulder(sys.argv[3]) if disc == 'boulder' else lead(sys.argv[3], sys.argv[4])
    allg = json.load(open(OUT)) if os.path.exists(OUT) else {}
    allg[comp] = res
    json.dump(allg, open(OUT, 'w'), ensure_ascii=False)
    for g, rows in res.items(): print(comp, g, len(rows), [r for r in rows if r[0] <= 3])
