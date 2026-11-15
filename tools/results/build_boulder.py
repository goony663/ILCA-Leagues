# python3 -I tools/results/build_boulder.py COMP_ID round1.xlsx [round2.xlsx] [--youth-nc] > rows.json
import sys, json, openpyxl
CAT = {'בוגרים':'ADULT','בוגרות':'ADULT','בנים U21':'U21','בנות U21':'U21','בנים U19':'U19','בנות U19':'U19','בנים U17':'U17','בנות U17':'U17'}
args = [a for a in sys.argv[1:] if not a.startswith('--')]; youth_nc = '--youth-nc' in sys.argv
comp, r1p = args[0], args[1]; r2p = args[2] if len(args) > 2 else None
num = lambda v: v if isinstance(v, (int, float)) else 0
def load(p):
    ws = openpyxl.load_workbook(p, data_only=True)['תוצאות']
    hdr = [c.value for c in ws[1]]; out = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r[1]: continue
        d = dict(zip(hdr, r)); s = d['ניקוד סופי']
        d['score'] = s if isinstance(s, (int, float)) else None
        d['top_att'] = sum(num(d.get(f'מ{i} Top')) for i in range(1, 7))
        d['zone_att'] = sum(num(d.get(f'מ{i} Zone')) for i in range(1, 7))
        out.append(d)
    return out
def rank_desc(rows, key):
    rows = sorted(rows, key=key, reverse=True); res, prev, place = [], object(), 0
    for i, r in enumerate(rows):
        k = key(r)
        if k != prev: place = i + 1; prev = k
        res.append((place, r))
    return res
sc = lambda d: ((d['score'] if d['score'] is not None else -1), -d['top_att'], -d['zone_att'])
who = lambda d: (str(d.get('שם')).strip(), d.get('מגדר'))  # match rounds by name + gender
r1 = load(r1p); r2 = {who(d): d for d in load(r2p)} if r2p else {}
ok = lambda d: CAT.get(d['קטגוריה']) and d.get('דגל') != 'DNS'
out = []
def emit(pool_rows, pool_name, use_r2):
    R1 = {who(d): p for p, d in rank_desc(pool_rows, sc)}
    place = {}
    if use_r2:
        fin = [d for d in pool_rows if who(d) in r2]
        k = lambda d: (sc(r2[who(d)])[0], -R1[who(d)], sc(r2[who(d)])[1], sc(r2[who(d)])[2])
        for p, d in rank_desc(fin, k): place[who(d)] = p
    for d in pool_rows: place.setdefault(who(d), R1[who(d)])
    for d in pool_rows:
        out.append(dict(comp=comp, gender=d['מגדר'], cat=CAT[d['קטגוריה']], pool=pool_name,
                        athlete=str(d['שם']).strip(), club=str(d['שם אגודה'] or '').strip(), place=place[who(d)]))
for g in 'MW':
    rows = [d for d in r1 if d['מגדר'] == g and ok(d)]
    if youth_nc:
        for c in ('U21', 'U19', 'U17'):
            emit([d for d in rows if CAT[d['קטגוריה']] == c], c, bool(r2))
    else:
        emit([d for d in rows if CAT[d['קטגוריה']] in ('ADULT', 'U21', 'U19')], 'open', bool(r2))
        emit([d for d in rows if CAT[d['קטגוריה']] == 'U17'], 'U17', False)
names = [(r['athlete'], r['gender']) for r in out]
assert len(names) == len(set(names)), 'duplicate athlete name in one competition'
json.dump(out, sys.stdout, ensure_ascii=False, indent=0)
