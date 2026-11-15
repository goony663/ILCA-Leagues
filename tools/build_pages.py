# Generates the league pages of the ILCA-Leagues site (design: Noam). Run: python3 build.py
import os
import os
V='20261115c'  # bump after changing assets/site.css or site.js, so browsers load the new version
OUT=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..') + '/'
ARROW_L='<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"></path></svg>'
ARROW_L22=ARROW_L.replace('width="18" height="18"','width="22" height="22"')
BACK_SVG='<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"></path></svg>'
CHEV='<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M6 9l6 6 6-6"></path></svg>'
PDF_SVG='<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"></path><path d="M14 3v5h5"></path><path d="M9 13h6"></path><path d="M9 17h6"></path></svg>'
FOLDER_SVG='<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path></svg>'

def page(fname, title, h1, sub, back, body, script, gap=40):
    back_html = ''
    if back:
        attr = f'data-page="{back[0]}"' if not back[0].endswith('.html') else f'href="{back[0]}"'
        back_html = f'<a class="back" {attr}>{BACK_SVG}<span>{back[1]}</span></a>\n'
    html = f'''<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="assets/site.css?v={V}">
</head>
<body>
<div class="wrap" style="gap:{gap}px">
{back_html}<header class="site-head">
  <div>
    <h1 class="disp">{h1}</h1>
    <div class="sub">{sub}</div>
  </div>
  <img class="logo" style="height:64px" src="assets/logo.svg" alt="התאחדות הטיפוס בישראל">
</header>
{body}
</div>
<script src="assets/site.js?v={V}"></script>
<script>
{script}
</script>
</body>
</html>
'''
    open(OUT+fname,'w').write(html)

# ---------- shared JS snippets ----------
UPCOMING_JS = r'''
function upcomingRow(c, opts = {}){
  const meta = [];
  if (c.cats) meta.push(`<span>קטגוריות: <strong>${ILCA.esc(c.cats)}</strong></span>`);
  meta.push(ILCA.regText(c));
  if (c.hours) meta.push(`<span>שעות: <strong>${ILCA.esc(c.hours)}</strong></span>`);
  if (c.fee) meta.push(`<span>דמי רישום: <strong>${ILCA.esc(c.fee)}</strong>${c.feeMember ? ' · ' + ILCA.esc(c.feeMember) : ''}</span>`);
  return `<article class="item">${ILCA.dateBox(c)}<div class="body"><h3>${ILCA.esc(c.title)}</h3><div class="vn">${ILCA.esc(c.sub)}</div>
    <div class="meta">${meta.join('')}</div>${c.note ? `<div class="note">${ILCA.esc(c.note)}</div>` : ''}</div></article>`;
}
function nextOf(items, league, n){
  return items.filter(c => c.league === league && !c.status && ILCA.dayDiff(c.end || c.start) >= 0)
              .sort((a, b) => ILCA.D(a.start) - ILCA.D(b.start)).slice(0, n);
}
'''
RESULTS_JS = r'''
// Past competitions of a league (from the calendar), newest first, each with its results PDF when there is one
function resultsPage(league){
  let disc = 'boulder', cal = [], res = { items: [], drive: '' };
  const pick = d => { disc = d; draw(); };
  function draw(){
    ILCA.discButtons(document.getElementById('discs'), disc, pick);
    const label = ILCA.KIND[disc];
    document.getElementById('htitle').textContent = `תחרויות ${label} שהתקיימו`;
    const kindOk = c => c.kind === disc || (disc === 'boulder' && c.kind === 'sim' && /בולדר/.test(c.sub)) || (disc === 'lead' && c.kind === 'sim' && /הובלה/.test(c.sub));
    const past = cal.filter(c => c.league === league && !c.status && kindOk(c) && ILCA.dayDiff(c.end || c.start) < 0)
                    .sort((a, b) => ILCA.D(b.start) - ILCA.D(a.start));
    const pdfOf = c => { const r = (res.items || []).find(x => x.start === c.start && x.title === c.title); return r && r.pdf; };
    document.getElementById('list').innerHTML = past.map(c => {
      const d = ILCA.D(c.start), pdf = pdfOf(c);
      return `<article class="item" style="flex-wrap:wrap;padding:12px 0">
        <div class="date"><span class="n disp ltr">${d.getDate()}</span><span class="m">${ILCA.MONTHS[d.getMonth()]}</span></div>
        <div class="body" style="flex:1 1 260px"><h3>${ILCA.esc(c.title)}</h3><div class="vn">${ILCA.esc(c.sub)}</div>
          ${c.cats ? `<div style="font-size:13px;color:var(--muted);margin-top:2px">קטגוריות: <strong style="color:var(--navy);font-weight:600">${ILCA.esc(c.cats)}</strong></div>` : ''}</div>
        ${pdf ? `<a class="btn" href="${pdf}" target="_blank" rel="noopener">__PDF__<span>לתוצאות (PDF)</span></a>` : '<span class="chip">התוצאות יעלו בקרוב</span>'}
      </article>`;
    }).join('');
    const next = cal.filter(c => c.league === league && !c.status && kindOk(c) && ILCA.dayDiff(c.start) >= 0).sort((a, b) => ILCA.D(a.start) - ILCA.D(b.start))[0];
    document.getElementById('empty').hidden = past.length > 0;
    document.getElementById('empty').textContent = `עוד לא התקיימו תחרויות ${label} העונה.` + (next ? ` התחרות הראשונה: ${next.title}, ${ILCA.dm(ILCA.D(next.start))}.` : '');
  }
  Promise.all([ILCA.json('data/calendar.json'), ILCA.json('data/results.json')]).then(([c, r]) => {
    cal = c.items || []; res = r[league] || res;
    if (res.drive) document.getElementById('drive').href = res.drive;
    draw();
  }).catch(() => { document.getElementById('list').innerHTML = '<div class="empty">לא ניתן לטעון את התוצאות.</div>'; });
  draw();
}
'''.replace('__PDF__', PDF_SVG)

def results_body():
    return f'''<div class="dgroup" role="group" aria-label="ענף" id="discs"></div>
<section class="main" style="flex:none">
  <h2 class="disp" id="htitle" style="margin-bottom:8px">תחרויות שהתקיימו</h2>
  <div class="list" id="list"></div>
  <div class="empty" id="empty" hidden></div>
  <div class="foot"><p>התוצאות מתפרסמות כאן אחרי כל תחרות. התחרות האחרונה מופיעה ראשונה.</p>
    <a class="tlink" id="drive" href="#" target="_blank" rel="noopener">{FOLDER_SVG}<span>לכל קבצי התוצאות בדרייב</span></a></div>
</section>'''

def panel(title, links):
    out = f'<aside class="side panel" aria-label="{title}"><div class="stripe s1" aria-hidden="true"></div><div class="stripe s2" aria-hidden="true"></div><h2 class="disp">{title}</h2>'
    for kind, label, href, extra in links:
        if kind == 'big':
            out += f'<a class="bigbtn" href="{href}" target="_blank" rel="noopener"><span><strong>{label}</strong>{ARROW_L22}</span></a>'
        else:
            out += f'<a class="plink" href="{href}" target="_blank" rel="noopener"><strong>{label}</strong>{f"<span>{extra}</span>" if extra else ""}</a>'
    return out + '</aside>'

def accordion(aid, title, subtitle, inner):
    return f'''<section class="acc"><button type="button" aria-expanded="false" aria-controls="{aid}">
  <span class="acc-t"><b>{title}</b>{f"<span>{subtitle}</span>" if subtitle else ""}</span>
  <span class="acc-s"><span class="acc-lbl">פתיחה</span>{CHEV}</span></button>
  <div class="acc-p" id="{aid}" hidden>{inner}</div></section>'''

def navcard(title, text, go, href=None, page=None, bar='var(--steel)', plain=False):
    attr = f'href="{href}"' if href else (f'data-page="{page}"' if page else '')
    tag = 'a' if attr else 'div'
    cls = 'lcard' + (' plain' if plain else '')
    gocls = 'go' if attr else 'go" style="color:var(--slate)'
    return f'<{tag} class="{cls}" {attr}><div class="bar" aria-hidden="true" style="background:{bar}"></div><h3 class="disp">{title}</h3><p><span>{text}</span></p><span class="{gocls}">{go}</span></{tag}>'

# ---------- Open League ----------
open_cats = '''<div style="overflow-x:auto"><table class="simple"><thead><tr><th scope="col">קטגוריה</th><th scope="col">גיל</th><th scope="col">שנתונים</th></tr></thead><tbody>
<tr><th scope="row">U30</th><td>19–29</td><td>1998–2008</td></tr>
<tr><th scope="row">U40</th><td>30–39</td><td>1988–1997</td></tr>
<tr><th scope="row">Seniors</th><td>40 ומעלה</td><td>1987 ומטה</td></tr>
<tr><th scope="row">PRO</th><td>19 ומעלה</td><td>2008 ומטה</td></tr></tbody></table></div>
<ul>
<li><strong>חלוקה לגברים ונשים</strong> בכל הקטגוריות.</li>
<li><strong>קטגוריית PRO:</strong> מיועדת למטפסים ומטפסות בעלי ניסיון תחרותי משמעותי, אשר במהלך חמש השנים האחרונות השתתפו באחד או יותר מהבאים: ליגת העל, נבחרת ישראל, תחרויות בינלאומיות רשמיות, חצי גמר אליפות ישראל. הקטגוריה פתוחה גם למטפסים המעוניינים לאתגר את עצמם ולהתחרות בה.</li>
<li><strong>איחוד קטגוריות:</strong> קטגוריה שבה לא יהיו לפחות 8 משתתפים או משתתפות עשויה להתאחד עם קטגוריית גיל אחרת, בהתאם לשיקול דעת צוות ההתאחדות. קטגוריית הפרו לא תאוחד עם קטגוריה אחרת.</li>
</ul>'''
open_champ = '''<p style="margin:0;font-size:17px;font-weight:600">האליפות הפתוחה היא אירוע השיא של עונת הליגה.</p>
<p style="margin:0">בסיום העונה, בחודשים <strong>יוני–יולי</strong>, יתקיים אירוע השיא של הליגה – האליפות הפתוחה בבולדר ובהובלה. האליפות תתקיים במתכונת תחרות רשמית, בדומה לפורמט הנהוג באליפויות ישראל, ובסיומה יוענקו פרסים לזוכות ולזוכים שיעפילו לפודיום.</p>
<div style="display:flex;flex-direction:column;gap:6px"><strong>כדי להשתתף באליפות הפתוחה, יש לעמוד בתנאים הבאים:</strong>
<ul><li>רישום בהתאחדות הטיפוס.</li><li>אישור מרופא ספורט בתוקף לעונת התחרויות (שהתקבל לפני התחרות הראשונה בה אתם מעוניינים להשתתף).</li><li>השתתפות בלפחות <strong>3 תחרויות</strong> של הליגה הפתוחה במהלך העונה.</li></ul></div>
<div role="note" class="callout">אם אתם מתכננים להשתתף באליפות הפתוחה, מומלץ להסדיר את האישור הרפואי ולהתחיל לצבור את 3 תחרויות הליגה הנדרשות כבר בתחילת העונה.</div>'''
FULL = 'https://open-climbing-league.base44.app/'
page('open.html','הליגה הפתוחה – התאחדות הטיפוס','הליגה הפתוחה','הליגה הפתוחה לבוגרים ולבוגרות (18+)',('landing','חזרה לתחרויות לאומיות'),
f'''<div class="row2">
  <section class="main">
    <div class="shead"><h2 class="disp">התחרויות הקרובות</h2>
      <a class="btn" href="{FULL}" target="_blank" rel="noopener"><span>רשימת התחרויות המלאה</span>{ARROW_L}</a></div>
    <div class="list" id="upcoming"><div class="empty">טוען…</div></div>
  </section>
  {panel('הרשמה ומידע',[('big','הרשמה לתחרויות הליגה','https://loglig.com/Activity/Form/63270?seasonId=1762',''),('p','רשימת התחרויות המלאה',FULL,''),('p','מידע על הליגה','https://drive.google.com/file/d/1wagU9MQNMxekRhep0qeBUp07LfQnT6cF/view','')])}
</div>
<div class="row2" style="align-items:stretch">
  <div class="main" style="gap:18px">
    {accordion('cats','הקטגוריות','U30 · U40 · Seniors · PRO',open_cats)}
    {accordion('open-champ','האליפות הפתוחה','אירוע השיא של העונה',open_champ)}
  </div>
  <nav class="side-nav" aria-label="תוצאות וליגות נוספות">
    {navcard('תוצאות התחרויות','התוצאות המלאות של כל תחרות, בבולדר ובהובלה','לתוצאות',page='openResults')}
    {navcard('ליגת הסטודנטים','בשיתוף אס״א ישראל. ניקוד מצטבר לספורטאים ולמוסדות האקדמיים.','להרשמה ולפרטים: פנו לרכזי הספורט במוסד',bar='var(--slate)',plain=True)}
  </nav>
</div>''',
UPCOMING_JS + r'''
ILCA.accordions();
ILCA.json('data/calendar.json').then(cal => {
  const n = nextOf(cal.items || [], 'open', 3);
  document.getElementById('upcoming').innerHTML = n.length ? n.map(c => upcomingRow(c)).join('') : '<div class="empty">אין תחרויות קרובות כרגע.</div>';
}).catch(() => { document.getElementById('upcoming').innerHTML = '<div class="empty">לא ניתן לטעון את רשימת התחרויות.</div>'; });
''')

page('open-results.html','תוצאות התחרויות – הליגה הפתוחה','תוצאות התחרויות','הליגה הפתוחה · עונת <span class="ltr">2026/27</span>',('open','חזרה לליגה הפתוחה'),
results_body(), RESULTS_JS + "resultsPage('open');", gap=28)

# ---------- National League ----------
nat_hero = f'''<section class="hero" id="hero" aria-label="תמונות מתחרויות הליגה">
  <div class="frames">
    <div class="fr side" id="frR"></div>
    <div class="fr mid" id="frC" aria-roledescription="carousel" aria-label="תמונות מתחלפות"></div>
    <div class="fr side" id="frL"></div>
  </div>
  <div class="ctl"><div style="display:flex;align-items:center;gap:10px"><button type="button" class="pp" id="pp"></button><div class="dots" id="dots"></div></div>
    <div class="credit" id="credit"></div></div>
</section>'''
page('national.html','הליגה הארצית – התאחדות הטיפוס','הליגה הארצית','ליגת הילדים והנוער, קטגוריות: U11 עד U19 (שנתונים 2009 עד 2018)',('landing','חזרה לתחרויות לאומיות'),
nat_hero + f'''
<div class="row2">
  <section class="main">
    <div class="shead"><h2 class="disp">התחרויות הקרובות</h2>
      <a class="tlink" data-page="nationalSeason"><span>לרשימה המלאה</span>{ARROW_L}</a></div>
    <div class="list" id="upcoming"><div class="empty">טוען…</div></div>
  </section>
  {panel('הרשמה ומידע',[('big','הרשמה לתחרויות הליגה','https://loglig.com/Activity/Form/62989?seasonId=1762',''),('big','הרשמה לסימולציות מזכות','https://loglig.com/Activity/Form/63057?seasonId=1762',''),('p','מידע על הליגה','https://drive.google.com/file/d/1UrtAh3AUyAHpVd7kk7866ywP-9Vo0WlQ/view',''),('p','תקנון הליגה הארצית בבולדר','https://drive.google.com/file/d/1Uifrd67mOIvQqn55A7LkGWIWy8ZeGSMJ/view',''),('p','תקנון הליגה הארצית בהובלה','https://drive.google.com/file/d/11wfNcS_49COjTQXKWt13NESmXUJ7uGfZ/view','')])}
</div>
<div class="row2" style="align-items:stretch">
  <section class="main" id="leaders-sec">
    <div class="shead" style="align-items:center"><h2 class="disp">מובילי הליגה</h2>
      <div style="display:flex;flex-wrap:wrap;align-items:center;gap:10px"><div class="dgroup" style="border:0;padding:0" role="group" aria-label="ענף" id="ldiscs"></div>
      <label style="display:flex;align-items:center;gap:8px;font-size:14px;color:var(--slate)"><span>קטגוריה</span><select class="sel" id="lcat"></select></label></div></div>
    <ol class="list" id="leaders" style="list-style:none;margin:0;padding:0"></ol>
    <div style="margin-top:8px;font-size:13px;color:var(--muted)" id="lnote"></div>
  </section>
  <nav class="side-nav" aria-label="תוצאות">
    {navcard('תוצאות התחרויות','התוצאות המלאות של כל תחרות, בבולדר ובהובלה','לתוצאות',page='nationalResults')}
    {navcard('תוצאות הליגה','הניקוד המצטבר בבולדר ובהובלה, לפי קטגוריה','בקרוב',bar='var(--navy)')}
  </nav>
</div>''',
UPCOMING_JS + r'''
ILCA.json('data/calendar.json').then(cal => {
  const n = nextOf(cal.items || [], 'national', 3);
  document.getElementById('upcoming').innerHTML = n.length ? n.map(c => upcomingRow(c)).join('') : '<div class="empty">אין תחרויות קרובות כרגע.</div>';
}).catch(() => { document.getElementById('upcoming').innerHTML = '<div class="empty">לא ניתן לטעון את רשימת התחרויות.</div>'; });

/* league leaders: data/national-leaders.json  {updatedAfter, boulder:{'U13 בנות':[[name, club, points],...]}, lead:{...}} */
(function(){
  const cats = []; ['U11','U13','U15','U17','U19'].forEach(a => { cats.push(a + ' בנות'); cats.push(a + ' בנים'); });
  let disc = 'boulder', cat = cats[0], data = null;
  const sel = document.getElementById('lcat');
  sel.innerHTML = cats.map(c => `<option>${c}</option>`).join('');
  sel.onchange = () => { cat = sel.value; draw(); };
  const fills = ['var(--navy)','var(--slate)','var(--steel)'];
  function draw(){
    ILCA.discButtons(document.getElementById('ldiscs'), disc, d => { disc = d; draw(); });
    const rows = data && data[disc] && data[disc][cat] || [];
    document.getElementById('leaders').innerHTML = rows.length ? rows.slice(0, 3).map((r, i) => `
      <li class="item" style="gap:16px"><span class="lead-badge" style="background:${fills[i]}"><span>${i + 1}</span></span>
        <div class="body"><strong style="font-size:17px">${ILCA.esc(r[0])}</strong><span style="font-size:13px;color:var(--muted)">${ILCA.esc(r[1])}</span></div>
        <div style="display:flex;flex-direction:column;align-items:flex-end"><strong class="disp" style="font-size:30px">${ILCA.esc(r[2])}</strong><span style="font-size:12px;color:var(--muted)">נקודות בליגה</span></div></li>`).join('')
      : '<li class="empty">טבלת מובילי הליגה תתפרסם כאן במהלך העונה.</li>';
    document.getElementById('lnote').textContent = data && data.updatedAfter ? `${ILCA.KIND[disc]} · ${cat} · מעודכן אחרי ${data.updatedAfter}` : '';
  }
  draw();
  ILCA.json('data/national-leaders.json').then(d => { data = d; draw(); }).catch(() => {});
})();

/* photo slideshow: data/national-photos.json {credit, center:[{src,alt}], right:[...], left:[...]} — hidden until photos are added */
ILCA.json('data/national-photos.json').then(p => {
  if (!p || !(p.center || []).length) return;
  const hero = document.getElementById('hero'); hero.classList.add('has');
  const fill = (el, list) => { el.innerHTML = list.map((s, i) => `<img src="${s.src}" alt="${ILCA.esc(s.alt || '')}" class="${i ? '' : 'on'}" loading="lazy">`).join(''); return [...el.querySelectorAll('img')]; };
  const C = fill(document.getElementById('frC'), p.center), R = fill(document.getElementById('frR'), p.right || []), L = fill(document.getElementById('frL'), p.left || []);
  document.getElementById('credit').textContent = p.credit ? 'צילום: ' + p.credit : '';
  let c = 0, r = 0, l = 0, tick = 0, paused = false;
  try { paused = matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  const show = (arr, i) => arr.forEach((im, k) => im.classList.toggle('on', k === i));
  const dots = document.getElementById('dots');
  const drawDots = () => { dots.innerHTML = C.map((_, i) => `<button type="button" aria-label="תמונה ${i + 1} מתוך ${C.length}" aria-current="${i === c}"><span></span></button>`).join('');
    dots.querySelectorAll('button').forEach((b, i) => b.onclick = () => { c = i; show(C, c); drawDots(); }); };
  const pp = document.getElementById('pp');
  const drawPP = () => { pp.setAttribute('aria-label', paused ? 'הפעלת התמונות המתחלפות' : 'עצירת התמונות המתחלפות');
    pp.innerHTML = paused ? '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"></path></svg>' : '<svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><rect x="6" y="5" width="4" height="14"></rect><rect x="14" y="5" width="4" height="14"></rect></svg>'; };
  pp.onclick = () => { paused = !paused; drawPP(); };
  drawDots(); drawPP();
  setInterval(() => { if (paused) return; tick++;
    if (tick % 2 === 0) { c = (c + 1) % C.length; show(C, c); drawDots(); }
    if (R.length && tick % 8 === 3) { r = (r + 1) % R.length; show(R, r); }
    if (L.length && tick % 8 === 7) { l = (l + 1) % L.length; show(L, l); } }, 3000);
}).catch(() => {});
''')

page('national-results.html','תוצאות התחרויות – הליגה הארצית','תוצאות התחרויות','הליגה הארצית וסימולציות · עונת <span class="ltr">2026/27</span>',('national','חזרה לליגה הארצית'),
results_body(), RESULTS_JS + "resultsPage('national');", gap=28)

page('national-season.html','כל תחרויות העונה – הליגה הארצית','כל תחרויות העונה','הליגה הארצית וסימולציות · עונת <span class="ltr">2026/27</span>',('national','חזרה לליגה הארצית'),
'''<div style="display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px 20px;border-top:3px solid var(--navy);border-bottom:1px solid var(--mist);padding:12px 0">
  <div role="group" aria-label="סוג תחרות" style="display:flex;flex-wrap:wrap;gap:6px" id="filters"></div>
  <label style="display:inline-flex;align-items:center;gap:8px;min-height:44px;font-size:15px;color:var(--slate);cursor:pointer">
    <input type="checkbox" id="hide" style="width:20px;height:20px;accent-color:var(--navy);margin:0"><span>להסתיר תחרויות שכבר התקיימו</span></label>
</div>
<div id="months" style="display:flex;flex-direction:column;gap:28px"></div>
<div class="empty" id="empty" hidden>אין תחרויות שמתאימות לסינון.</div>
<div style="display:flex;flex-wrap:wrap;gap:10px">
  <a class="btn" href="https://loglig.com/Activity/Form/62989?seasonId=1762" target="_blank" rel="noopener">הרשמה לתחרויות הליגה</a>
  <a class="btn ghost" href="https://loglig.com/Activity/Form/63057?seasonId=1762" target="_blank" rel="noopener">הרשמה לסימולציות מזכות</a>
</div>''',
r'''
let kind = 'all', hidePast = false, items = [];
const FIL = [['all','הכל'],['boulder','ליגה · בולדר'],['lead','ליגה · הובלה'],['sim','סימולציות']];
function draw(){
  const f = document.getElementById('filters');
  f.innerHTML = FIL.map(([id, l]) => `<button type="button" class="fbtn" data-k="${id}" aria-pressed="${id === kind}">${l}</button>`).join('');
  f.querySelectorAll('button').forEach(b => b.onclick = () => { kind = b.dataset.k; draw(); });
  const months = [];
  items.filter(c => c.league === 'national').sort((a, b) => ILCA.D(a.start) - ILCA.D(b.start)).forEach(c => {
    const past = ILCA.dayDiff(c.end || c.start) < 0;
    if (kind !== 'all' && c.kind !== kind) return;
    if (hidePast && past) return;
    const d = ILCA.D(c.start), title = `${ILCA.MONTHS[d.getMonth()]} ${d.getFullYear()}`;
    let m = months[months.length - 1]; if (!m || m.title !== title) { m = { title, rows: [] }; months.push(m); }
    m.rows.push({ c, past });
  });
  document.getElementById('months').innerHTML = months.map(m => `<section><h2 class="disp" style="margin-bottom:8px">${m.title}</h2><div class="list">${m.rows.map(({c, past}) => {
    const s = ILCA.D(c.start), e = c.end ? ILCA.D(c.end) : null;
    const day = e ? `${s.getDate()}–${e.getDate()}` : `${s.getDate()}`;
    const wd = e ? `${ILCA.DAYS[s.getDay()]}-${ILCA.DAYS[e.getDay()]}` : `יום ${ILCA.DAYS[s.getDay()]}`;
    return `<article class="item ${past || c.status ? 'off' : ''}" style="align-items:flex-start">
      <div class="date" style="min-width:72px"><span class="n disp ltr" style="font-size:32px">${day}</span><span class="w" style="margin-top:3px">${wd}</span></div>
      <div class="body"><div style="display:flex;flex-wrap:wrap;align-items:center;gap:4px 10px"><h3 style="${c.status ? 'text-decoration:line-through' : ''}">${ILCA.esc(c.title)}</h3>${ILCA.kindTag(c.kind)}
        ${c.status ? `<span class="status">${ILCA.esc(c.status)}</span>` : past ? '<span class="past-tag">התקיימה</span>' : ''}</div>
        <div class="vn">${ILCA.esc(c.sub)}</div>
        <div class="meta"><span>קטגוריות: <strong>${ILCA.esc(c.cats)}</strong></span><span>סגירת רישום: <strong class="ltr">${ILCA.dm(ILCA.D(c.regClose))}</strong></span>${c.hours ? `<span>שעות: <strong>${ILCA.esc(c.hours)}</strong></span>` : ''}</div>
        ${c.note ? `<div class="note">${ILCA.esc(c.note)}</div>` : ''}</div></article>`;
  }).join('')}</div></section>`).join('');
  document.getElementById('empty').hidden = months.length > 0;
}
document.getElementById('hide').onchange = e => { hidePast = e.target.checked; draw(); };
ILCA.json('data/calendar.json').then(cal => { items = cal.items || []; draw(); })
  .catch(() => { document.getElementById('months').innerHTML = '<div class="empty">לא ניתן לטעון את רשימת התחרויות.</div>'; });
''', gap=28)

# ---------- Championships ----------
crit = '''<div style="display:flex;flex-wrap:wrap;gap:14px">
<div style="flex:1 1 300px;background:var(--mist);padding:16px 18px;display:flex;flex-direction:column;gap:4px"><strong class="disp" style="font-size:26px">אליפות ישראל בבולדר</strong><p style="margin:0">השלמת לפחות <strong>3 תחרויות מזכות</strong> לפני מועד האליפות.</p></div>
<div style="flex:1 1 300px;background:var(--mist);padding:16px 18px;display:flex;flex-direction:column;gap:4px"><strong class="disp" style="font-size:26px">אליפות ישראל בהובלה</strong><p style="margin:0">השלמת לפחות <strong>3 תחרויות מזכות</strong> לפני מועד האליפות, כאשר <strong>לפחות אחת מהן היא תחרות הובלה</strong>.</p></div></div>
<div style="display:flex;flex-direction:column;gap:6px"><strong style="font-size:17px">תחרויות מזכות הן:</strong>
<ul style="gap:2px"><li>תחרויות הליגה הארצית</li><li>סימולציות נוער-בוגרים שהוגדרו כתחרויות מזכות</li><li>תחרויות ליגת העל (לזכאים)</li></ul></div>
<div role="note" class="callout warn"><svg aria-hidden="true" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex:0 0 auto;margin-top:2px"><path d="M12 9v4"></path><path d="M12 17h.01"></path><path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"></path></svg>
<div style="display:flex;flex-direction:column;gap:4px"><strong style="font-size:17px">שימו לב</strong><p style="margin:0">החל מהעונה הקרובה יבוטל הפטור הגורף שניתן למשתתפי ליגת העל מחובת השתתפות ב-3 תחרויות כתנאי סף לרישום לאליפות.</p><p style="margin:0">על כל הספורטאים המעוניינים להשתתף באליפויות ישראל להשלים את מספר התחרויות הנדרש לפני מועד האליפות.</p></div></div>'''
page('championships.html','אליפויות ישראל – התאחדות הטיפוס','אליפויות ישראל','בבולדר ובהובלה: ילדים, נוער, בוגרים · עונת <span class="ltr">2026/27</span>',('landing','חזרה לתחרויות לאומיות'),
f'''<section class="main" style="flex:none">
  <h2 class="disp" style="margin-bottom:10px">אליפויות העונה</h2>
  <div class="list" id="champs"><div class="empty">טוען…</div></div>
</section>
{accordion('criteria','קריטריונים להשתתפות באליפויות ישראל','',crit)}''',
r'''
ILCA.accordions();
ILCA.json('data/calendar.json').then(cal => {
  const now = new Date();
  const list = (cal.items || []).filter(c => c.league === 'champ').sort((a, b) => ILCA.D(a.start) - ILCA.D(b.start));
  document.getElementById('champs').innerHTML = list.map(c => {
    const s = ILCA.D(c.start), e = c.end ? ILCA.D(c.end) : null;
    const days = c.approx || (e ? `${s.getDate()}–${e.getDate()}` : `${s.getDate()}`);
    const month = c.approx ? 'מועד מדויק יפורסם' : ILCA.MONTHS[s.getMonth()];
    const closeAt = c.regClose ? new Date(c.regClose + 'T' + (c.regCloseTime || '23:59')) : null;
    const isClosed = closeAt && now > closeAt;
    const isOpen = !isClosed && c.regOpen && ILCA.dayDiff(c.regOpen) <= 0;
    const soon = !isOpen && !isClosed && (ILCA.D(c.start) - now) / 864e5 <= 92;
    const meta = [`<span>קטגוריות: <strong>${ILCA.esc(c.cats)}</strong></span>`];
    if (c.regOpen && !isOpen && !isClosed) meta.push(`<span>פתיחת רישום: <strong class="ltr">${ILCA.dm(ILCA.D(c.regOpen))}</strong></span>`);
    if (c.regClose && !isClosed) meta.push(`<span>סגירת רישום: <strong><span class="ltr">${ILCA.dm(ILCA.D(c.regClose))}</span>${c.regCloseTime ? ' בשעה <span class="ltr">' + c.regCloseTime + '</span>' : ''}</strong></span>`);
    let act = '';
    if (isOpen && c.link) act = `<a class="btn steel" href="${c.link}" target="_blank" rel="noopener"><span>להרשמה</span><svg aria-hidden="true" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"></path></svg></a>`;
    else if (isClosed) act = '<span class="chip" style="background:#f1f4f6;color:var(--muted)">ההרשמה נסגרה</span>';
    else if (soon) act = '<span class="chip">ההרשמה תיפתח בקרוב</span>';
    return `<article class="item" style="flex-wrap:wrap;gap:14px 18px;padding:12px 0">
      <div class="date" style="min-width:76px"><span class="n disp ltr" style="font-size:${c.approx ? 22 : 32}px">${days}</span><span class="m">${month}</span></div>
      <div class="body" style="flex:1 1 280px"><div style="display:flex;flex-wrap:wrap;align-items:center;gap:4px 10px"><h3 style="font-size:18px">${ILCA.esc(c.title)}</h3>${ILCA.kindTag(c.kind)}</div>
        <div class="meta">${meta.join('')}</div></div>${act}</article>`;
  }).join('');
}).catch(() => { document.getElementById('champs').innerHTML = '<div class="empty">לא ניתן לטעון את רשימת האליפויות.</div>'; });
''', gap=36)
print('built')
