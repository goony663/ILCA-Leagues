/* Shared helpers for the federation's competitions pages */
(function () {
  // Embedded in the federation site (iframe): report our height so the iframe grows with the page.
  if (window.parent !== window) {
    document.documentElement.classList.add('ilca-embedded');
    let last = 0;
    const send = () => {
      const h = Math.ceil(document.documentElement.scrollHeight);
      if (Math.abs(h - last) > 2) { last = h; window.parent.postMessage({ ilcaHeight: h }, '*'); }
    };
    window.addEventListener('load', send);
    window.addEventListener('resize', send);
    try { new ResizeObserver(send).observe(document.body); } catch (e) { setInterval(send, 1000); }
  }
})();

/* Where every page lives. wp = its address on ilca.org.il (opens as a whole page);
   null = not on the federation site yet, so the GitHub file opens inside the current frame. */
const ILCA_PAGES = {
  landing:  { file: 'index.html',            wp: 'https://ilca.org.il/%D7%A1%D7%A4%D7%95%D7%A8%D7%98/%D7%AA%D7%97%D7%A8%D7%95%D7%99%D7%95%D7%AA-%D7%9C%D7%90%D7%95%D7%9E%D7%99%D7%95%D7%AA-2/' },
  elite:    { file: 'elite.html',            wp: 'https://ilca.org.il/%D7%9C%D7%99%D7%92%D7%AA-%D7%94%D7%A2%D7%9C/' },
  open:     { file: 'open.html',             wp: null },
  national: { file: 'national.html',         wp: null },
  champ:    { file: 'championships.html',    wp: null },
  rankings: { file: null,                    wp: 'https://ilca.org.il/%d7%94%d7%9e%d7%93%d7%a8%d7%92-%d7%94%d7%9c%d7%90%d7%95%d7%9e%d7%99-%d7%91%d7%98%d7%99%d7%a4%d7%95%d7%a1/' }
};

const ILCA = {
  MONTHS: ['ינואר','פברואר','מרץ','אפריל','מאי','יוני','יולי','אוגוסט','ספטמבר','אוקטובר','נובמבר','דצמבר'],
  DAYS: ['ראשון','שני','שלישי','רביעי','חמישי','שישי','שבת'],
  DAYS_SHORT: ['א׳','ב׳','ג׳','ד׳','ה׳','ו׳','ש׳'],
  esc: s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])),
  D: s => { const [y,m,d] = s.split('-').map(Number); return new Date(y, m-1, d); },
  today: (() => { const t = new Date(); return new Date(t.getFullYear(), t.getMonth(), t.getDate()); })(),
  dayDiff(s) { return Math.round((this.D(s) - this.today) / 864e5); },
  dm: d => `${d.getDate()}.${d.getMonth()+1}`,
  async json(path) { const r = await fetch(path, { cache: 'no-cache' }); if (!r.ok) throw new Error(path); return r.json(); },

  // Big date block like the design: day number(s), month, weekday(s)
  dateBox(c) {
    const s = this.D(c.start), e = c.end ? this.D(c.end) : s;
    const multi = +e !== +s;
    const n = !multi ? `${s.getDate()}` : s.getMonth() === e.getMonth() ? `${s.getDate()}–${e.getDate()}` : `${s.getDate()}.${s.getMonth()+1}–${e.getDate()}.${e.getMonth()+1}`;
    const w = multi ? `${this.DAYS_SHORT[s.getDay()]}–${this.DAYS_SHORT[e.getDay()]}` : `יום ${this.DAYS[s.getDay()]}`;
    return `<div class="date"><span class="n disp ltr">${n}</span><span class="m">${this.MONTHS[s.getMonth()]}</span><span class="w">${w}</span></div>`;
  },
  regText(c) {
    if (!c.regClose) return '';
    const left = this.dayDiff(c.regClose), d = this.dm(this.D(c.regClose));
    if (left < 0) return `<span>הרישום נסגר <strong class="ltr">${d}</strong></span>`;
    const tag = left === 0 ? ' (היום)' : left === 1 ? ' (מחר)' : '';
    return `<span class="${left <= 2 ? 'soon' : ''}">סגירת רישום: <strong><span class="ltr">${d}</span>${tag}</strong></span>`;
  },

  // Scrolling updates bar (RTL)
  chyron(items) {
    const tr = document.getElementById('chtrack'), bar = document.getElementById('chbar');
    if (!tr || !items.length) { const c = document.querySelector('.chyron'); if (c) c.hidden = true; return; }
    const html = items.map(([k, v]) => `<span class="ch-item"><b>${this.esc(k)}</b>${this.esc(v)}</span>`).join('');
    tr.innerHTML = html + `<span aria-hidden="true" style="display:contents">${html}</span>`;
    requestAnimationFrame(() => tr.style.setProperty('--dur', Math.max(20, tr.scrollWidth / 2 / 70) + 's'));
    bar.onclick = () => bar.classList.toggle('paused');
  },

  // <a data-page="landing"> → the right address and target
  wireLinks(root = document) {
    root.querySelectorAll('a[data-page]').forEach(a => {
      const p = ILCA_PAGES[a.dataset.page]; if (!p) return;
      if (p.wp) { a.href = p.wp; a.target = '_top'; } else { a.href = p.file; a.target = '_self'; }
    });
  },
  KIND: { boulder: 'בולדר', lead: 'הובלה', sim: 'סימולציה' },
  kindTag(k) { return `<span class="ktag k-${k}">${this.KIND[k] || ''}</span>`; },
  // Two skewed toggle buttons (בולדר / הובלה)
  discButtons(el, current, onPick) {
    el.innerHTML = [['boulder','בולדר'],['lead','הובלה']].map(([id, l]) =>
      `<button type="button" class="dbtn" data-d="${id}" aria-pressed="${id === current}"><span>${l}</span></button>`).join('');
    el.querySelectorAll('button').forEach(b => b.onclick = () => onPick(b.dataset.d));
  },
  // Expandable section (border box with navy header button)
  accordions(root = document) {
    root.querySelectorAll('.acc > button').forEach(b => {
      const panel = document.getElementById(b.getAttribute('aria-controls'));
      const lbl = b.querySelector('.acc-lbl');
      const set = open => { b.setAttribute('aria-expanded', open); panel.hidden = !open; if (lbl) lbl.textContent = open ? 'סגירה' : 'פתיחה'; };
      set(false); b.onclick = () => set(b.getAttribute('aria-expanded') !== 'true');
    });
  }
};
document.addEventListener('DOMContentLoaded', () => ILCA.wireLinks());
