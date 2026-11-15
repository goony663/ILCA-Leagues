# Lead results -> public rows (same rules and output as the national rankings).
# python3 -I tools/results/build_lead.py COMP_ID round1.xlsx [round2.xlsx] > rows.json
#
# Round 1 (qualification, several routes): each route ranked by height (top > hold > plus), ties get the
# average of the places they cover; QP = geometric mean of route places, lower is better (Annex B §7.2).
# A climber with a result on only one route is ranked equal last on the other.
# Round 2 (one route): ranked by height; ties broken by round-1 place (§7.3 A); still equal -> shared.
# Places are recalculated inside every pool: the open pool (adults+U21+U19 climb together),
# each of U21 / U19 on its own (lead scores are relative, so the order can change), and U17 (own routes, without U15).
import sys, json, openpyxl

CAT = {'בוגרים': 'ADULT', 'בוגרות': 'ADULT', 'בנים U21': 'U21', 'בנות U21': 'U21', 'בנים U19': 'U19',
       'בנות U19': 'U19', 'בנים U17': 'U17', 'בנות U17': 'U17'}
YES = {'כן', 'yes', 'Yes', 'TRUE', 'True', True, 1, '1', '+', 'v', 'V', '✓'}


def load(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    conf = {r[0]: r[1] for r in wb['הגדרות'].iter_rows(min_row=2, values_only=True) if r[0]}
    assert conf.get('discipline') == 'lead', f"not a lead file: {conf.get('discipline')}"
    ws = wb['תוצאות']
    hdr = [c.value for c in ws[1]]
    n_routes = int(conf.get('routeCount') or 1)
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r[1]:
            continue
        d = dict(zip(hdr, r))
        d['heights'] = []
        for i in range(1, n_routes + 1):
            hold = d.get(f'מ{i} אחיזה')
            t = d.get(f'מ{i} ראש')
            top = t in YES or (isinstance(t, str) and t.strip().upper() in ('TOP', 'T', 'כן'))
            if hold in (None, '') and not top:
                d['heights'].append(None)
                continue
            num = float(str(hold).replace('+', '')) if hold not in (None, '') else 0.0
            plus = d.get(f'מ{i} פלוס') in YES or str(hold).endswith('+')
            d['heights'].append((1 if top else 0, num, 1 if plus else 0))
        rows.append(d)
    return conf, rows


def who(d):
    # match athletes between rounds by name + gender (bib numbers can change between rounds,
    # and the ID column is not always filled the same way in both files)
    return (str(d.get('שם')).strip(), d.get('מגדר'))


def frac_places(items, key):
    s = sorted(items, key=key, reverse=True)
    out, i = {}, 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and key(s[j + 1]) == key(s[i]):
            j += 1
        for k in range(i, j + 1):
            out[id(s[k])] = (i + 1 + j + 1) / 2
        i = j + 1
    return out


def comp_places(items, key):
    s = sorted(items, key=key, reverse=True)
    out, prev, place = {}, object(), 0
    for i, d in enumerate(s):
        k = key(d)
        if k != prev:
            place, prev = i + 1, k
        out[id(d)] = place
    return out


def qualification(pool):
    climbed = [d for d in pool if any(h is not None for h in d['heights'])]
    if not climbed:
        return {}
    n_routes = len(climbed[0]['heights'])
    qp = {id(d): 1.0 for d in climbed}
    for r in range(n_routes):
        on = [d for d in climbed if d['heights'][r] is not None]
        off = [d for d in climbed if d['heights'][r] is None]
        places = frac_places(on, lambda d: d['heights'][r])
        last = (len(on) + 1 + len(climbed)) / 2 if off else None
        for d in climbed:
            qp[id(d)] *= places[id(d)] if id(d) in places else last
    for k in qp:
        qp[k] = round(qp[k] ** (1 / n_routes), 3)
    return comp_places(climbed, lambda d: -qp[id(d)]), qp


def final_places(pool, r2):
    q = qualification(pool)
    if not q:
        return {}
    r1_place, _ = q
    ranked = [d for d in pool if id(d) in r1_place]
    fin = [d for d in ranked if who(d) in r2 and r2[who(d)]['heights'][0] is not None]
    dns2 = [d for d in ranked if who(d) in r2 and r2[who(d)]['heights'][0] is None]
    rest = [d for d in ranked if who(d) not in r2]
    out = {}
    out.update(comp_places(fin, lambda d: (r2[who(d)]['heights'][0], -r1_place[id(d)])))
    base = len(fin)
    out.update({k: base + v for k, v in comp_places(dns2, lambda d: -r1_place[id(d)]).items()})
    base += len(dns2)
    out.update({k: base + v for k, v in comp_places(rest, lambda d: -r1_place[id(d)]).items()})
    return out


if __name__ == '__main__':
    comp, r1p = sys.argv[1], sys.argv[2]
    r2p = sys.argv[3] if len(sys.argv) > 3 else None
    _, r1 = load(r1p)
    r2 = {who(d): d for d in load(r2p)[1]} if r2p else {}
    ok = lambda d: CAT.get(d['קטגוריה']) and d.get('דגל') != 'DNS'
    out = []
    for g in 'MW':
        rows = [d for d in r1 if d['מגדר'] == g and ok(d)]
        pools = [('open', [d for d in rows if CAT[d['קטגוריה']] in ('ADULT', 'U21', 'U19')])]
        pools += [(c, [d for d in rows if CAT[d['קטגוריה']] == c]) for c in ('U21', 'U19', 'U17')]
        for name, pool in pools:
            places = final_places(pool, r2)
            for d in pool:
                if id(d) in places:
                    out.append(dict(comp=comp, gender=g, cat=CAT[d['קטגוריה']], pool=name,
                                    athlete=str(d['שם']).strip(), club=str(d['שם אגודה'] or '').strip(),
                                    place=places[id(d)]))
    out.sort(key=lambda r: (r['gender'], r['pool'], r['place']))
    json.dump(out, sys.stdout, ensure_ascii=False, indent=0)
