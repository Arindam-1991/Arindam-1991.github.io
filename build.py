"""
build.py — Generate index.html from content.yaml
================================================
Usage:
    python build.py

This reads content.yaml and writes a fresh index.html.
Upload only index.html to GitHub — build.py and content.yaml
stay on your computer.

Requirements:  pip install pyyaml
"""

import yaml, re, sys
from pathlib import Path
from datetime import datetime

def parse_news_date(d):
    """Parse 'Mon YYYY' style date string for sorting; returns datetime or min."""
    for fmt in ("%b %Y", "%B %Y", "%Y"):
        try:
            return datetime.strptime(str(d).strip(), fmt)
        except (ValueError, TypeError):
            pass
    return datetime.min

# ── helpers ──────────────────────────────────────────────────────────────────

def bold_authors(text):
    """Turn **Name** into <strong>Name</strong>."""
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

def escape(text):
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

SVG_ICONS = {
    "github": '<svg height="15" width="15" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>',
    "linkedin": '<svg height="15" width="15" viewBox="0 0 24 24" fill="#0A66C2"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>',
    "orcid": '<svg height="15" width="15" viewBox="0 0 24 24" fill="#A6CE39"><path d="M12 0C5.372 0 0 5.372 0 12s5.372 12 12 12 12-5.372 12-12S18.628 0 12 0zM7.369 4.378c.525 0 .947.431.947.947s-.422.947-.947.947a.95.95 0 0 1-.947-.947c0-.525.422-.947.947-.947zm-.722 3.038h1.444v10.041H6.647V7.416zm3.562 0h3.9c3.712 0 5.344 2.653 5.344 5.025 0 2.578-2.016 5.016-5.325 5.016h-3.919V7.416zm1.444 1.303v7.435h2.297c3.272 0 3.872-2.466 3.872-3.722 0-2.456-1.516-3.713-3.884-3.713h-2.285z"/></svg>',
    "scholar": '<svg height="15" width="15" viewBox="0 0 24 24" fill="#4285F4"><path d="M12 24a7 7 0 1 1 0-14 7 7 0 0 1 0 14zm0-24L0 9.5l4.838 3.94A8 8 0 0 1 12 10a8 8 0 0 1 7.162 3.44L24 9.5z"/></svg>',
    "email": '<svg height="15" width="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,12 2,6"/></svg>',
    "pdf": '<svg height="13" width="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>',
    "cv":  '<svg height="14" width="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><polyline points="9 15 12 18 15 15"/></svg>',
}

CONTACT_ICON_FALLBACK = {
    "email": "✉", "github": "⌥", "linkedin": "in",
    "orcid": "iD", "scholar": "🎓",
}

def icon(name):
    return SVG_ICONS.get(name, "")

def contact_icon_html(name):
    return SVG_ICONS.get(name, CONTACT_ICON_FALLBACK.get(name, "?"))

# ── section builders ──────────────────────────────────────────────────────────

def build_hero(h, news_items=None):
    if news_items is None:
        news_items = []

    first_name = escape(h.get("first_name", ""))
    last_name  = escape(h.get("last_name", ""))
    photo_src  = h.get("photo", "img/profile.jpg")
    descriptor = escape(h.get("descriptor", "Computer Vision & AI Researcher"))
    statement  = escape(h.get("research_statement", ""))

    # Affiliation lines
    aff_html = "".join(
        f'<span class="hero-aff-item">{escape(a)}</span>'
        for a in h.get("affiliations", [])
    )

    # Research topic pills
    topics_html = "".join(
        f'<span class="hero-topic">{escape(t)}</span>'
        for t in h.get("topics", [])
    )

    # Action buttons
    btn_cls = {"cv": "btn-cv", "scholar": "btn-scholar",
               "primary": "btn-cv", "outline": "btn-outline"}
    buttons = ""
    for lnk in h.get("links", []):
        cls  = btn_cls.get(lnk.get("style", "outline"), "btn-outline")
        svg  = icon(lnk.get("icon", ""))
        lbl  = escape(lnk.get("label", ""))
        url  = lnk.get("url", "#")
        buttons += (f'<a href="{url}" class="btn {cls}" target="_blank"'
                    f' rel="noopener noreferrer" aria-label="{lbl}">'
                    f'{svg} {lbl}</a>\n      ')

    # White-card highlights (individual cards, grid layout)
    hl_html = ""
    for hl in h.get("highlights", []):
        hl_html += f"""
        <div class="hero-hl">
          <div class="hero-hl-num">{escape(str(hl['num']))}</div>
          <div class="hero-hl-label">{escape(hl['label'])}</div>
        </div>"""
    stats_html = (f'<div class="hero-highlights reveal">{hl_html}\n      </div>'
                  if hl_html else "")

    # Scalable news feed — white cards, show first 5, JS toggle for rest
    INIT_SHOW = 5
    news_html = ""
    if news_items:
        cards_html = ""
        for i, n in enumerate(news_items):
            date_str  = escape(str(n.get("date", ""))).upper()
            ntype     = escape(n.get("type", ""))
            text      = escape(n.get("text", ""))
            url       = n.get("url", "")
            extra_cls = " news-hidden" if i >= INIT_SHOW else ""
            if url:
                main = (f'<a href="{url}" class="news-link" target="_blank"'
                        f' rel="noopener noreferrer">{text}'
                        f'<span class="news-ext-icon" aria-label="opens in new tab"> ↗</span></a>')
            else:
                main = text
            cards_html += f"""
          <div class="news-card reveal{extra_cls}">
            <div class="news-card-meta">
              <span class="news-date">{date_str}</span>
              <span class="news-type">{ntype}</span>
            </div>
            <p class="news-text">{main}</p>
          </div>"""
        more_btn = ""
        if len(news_items) > INIT_SHOW:
            more_btn = ('\n          <button class="news-more-btn" id="news-more-btn"'
                        ' aria-expanded="false">Show more ↓</button>')
        news_html = f"""
  <div class="hero-news">
    <div class="hero-news-inner">
      <p class="hero-news-heading">Recent Updates</p>
      <div class="news-feed">{cards_html}
      </div>{more_btn}
    </div>
  </div>"""

    return f"""
<section id="hero">
  <div class="hero-inner">

    <div class="hero-left">
      <p class="hero-descriptor">{descriptor}</p>
      <h1 class="hero-name">{first_name}<br><em>{last_name}</em></h1>
      <p class="hero-statement reveal">{statement}</p>
      <div class="hero-affiliations reveal">{aff_html}</div>
      <div class="hero-topics reveal">{topics_html}</div>
      <div class="hero-links reveal">{buttons.strip()}</div>
    </div>

    <div class="hero-right">
      <div class="hero-portrait-area reveal">
        <div class="hero-photo-wrap">
          <img src="{photo_src}"
               alt="{h.get('first_name', '')} {h.get('last_name', '')}, Computer Vision &amp; AI Researcher"
               class="hero-photo"
               onerror="this.style.display='none';this.parentElement.querySelector('.hero-photo-placeholder').style.display='flex'">
          <div class="hero-photo-placeholder" aria-hidden="true">
            <span class="hero-photo-initials">A·S</span>
            <span class="hero-photo-hint">Add photo →<br>img/profile.jpg</span>
          </div>
        </div>
      </div>
      {stats_html}
    </div>

  </div>
  {news_html}
</section>"""

def build_about(a):
    cards = ""
    for c in a.get("cards", []):
        cards += f"""
    <div class="research-card reveal">
      <h3>{c['icon']} {escape(c['title'])}</h3>
      <p>{escape(c['text'])}</p>
    </div>"""
    return f"""
<section id="about">
  <div class="section-header reveal">
    <span class="section-num">01</span>
    <h2 class="section-title">Research Interests</h2>
    <div class="section-line"></div>
  </div>
  <div class="research-grid">{cards}
  </div>
</section>"""

def build_experience(e):
    items = ""
    for it in e.get("items", []):
        items += f"""
    <div class="tl-item reveal">
      <div class="tl-year">{escape(it['years'])}</div>
      <div class="tl-content">
        <h3>{escape(it['title'])}</h3>
        <div class="tl-institution">{escape(it['institution'])}</div>
        <p>{escape(it['description'])}</p>
        <span class="tl-tag">{escape(it['tag'])}</span>
      </div>
    </div>"""
    return f"""
<section id="experience">
  <div class="section-header reveal">
    <span class="section-num">02</span>
    <h2 class="section-title">Research Experience</h2>
    <div class="section-line"></div>
  </div>
  <div class="timeline">{items}
  </div>
</section>"""

def build_publications(p):
    badge_class = {"journal": "badge-journal", "conference": "badge-conference", "workshop": "badge-conference", "book": "badge-book"}
    badge_label = {"journal": "Journal", "conference": "Conference", "workshop": "Workshop", "book": "Book Chapter"}

    # workshop is rendered under the conference group
    def gkey(t): return "conference" if t == "workshop" else t
    group_heading = {
        "journal":    "Journal Articles",
        "conference": "Conference & Workshop Papers",
        "book":       "Book Chapters",
    }
    # prefix letter for auto-numbering within each group
    id_prefix = {"book": "B", "journal": "J", "conference": "C"}

    # ── group and sort ───────────────────────────────────────────────────────
    groups = {"book": [], "journal": [], "conference": []}
    for pub in p.get("items", []):
        ptype = pub.get("type", "journal")
        gk = gkey(ptype)
        groups.setdefault(gk, []).append(pub)

    # sort each group by year descending; stable sort preserves YAML order for ties
    for gk in groups:
        groups[gk].sort(key=lambda x: x.get("year", 0), reverse=True)

    # ── render in order: book → journal → conference ─────────────────────────
    items = ""
    for gk in ["book", "journal", "conference"]:
        group_pubs = groups.get(gk, [])
        if not group_pubs:
            continue
        items += f'\n    <div class="pub-section-head" data-group="{gk}"><span class="pub-section-label">{group_heading[gk]}</span></div>'
        prefix = id_prefix[gk]
        for idx, pub in enumerate(group_pubs, 1):
            pub_id  = f"{prefix}{idx}"
            ptype   = pub.get("type", "journal")
            pdf     = pub.get("pdf", "")
            pdf_btn = ""
            if pdf:
                pdf_btn = f' <a href="{pdf}" class="pub-pdf-btn" target="_blank">{SVG_ICONS["pdf"]} PDF</a>'
            url = pub.get("url", "")
            if url:
                title_html = f'<a href="{url}" class="pub-title-link" target="_blank">{escape(pub["title"])}</a>'
            else:
                title_html = escape(pub["title"])

            items += f"""
    <div class="pub-item reveal" data-type="{ptype}">
      <div class="pub-num">{pub_id}</div>
      <div class="pub-body">
        <div class="pub-title">{title_html}{pdf_btn}</div>
        <div class="pub-authors">{bold_authors(escape(pub['authors']))}</div>
        <div class="pub-venue">{escape(pub['venue'])}</div>
      </div>
      <div class="pub-meta">
        <span class="pub-badge {badge_class.get(ptype,'badge-journal')}">{badge_label.get(ptype,'Journal')}</span>
      </div>
    </div>"""

    return f"""
<section id="publications">
  <div class="section-header reveal">
    <span class="section-num">03</span>
    <h2 class="section-title">Publications</h2>
    <div class="section-line"></div>
  </div>
  <div class="pub-filter reveal">
    <button class="pub-filter-btn active" onclick="filterPubs('all',this)">All</button>
    <button class="pub-filter-btn" onclick="filterPubs('book',this)">Book Chapter</button>
    <button class="pub-filter-btn" onclick="filterPubs('journal',this)">Journals</button>
    <button class="pub-filter-btn" onclick="filterPubs('conference',this)">Conferences / Workshops</button>
  </div>
  <div class="pub-list" id="pub-list">{items}
  </div>
</section>"""

def build_teaching(t):
    items = ""
    for it in t.get("items", []):
        items += f"""
    <div class="tl-item reveal">
      <div class="tl-year">{escape(it['year_label'])}</div>
      <div class="tl-content">
        <h3>{escape(it['title'])}</h3>
        <div class="tl-institution">{escape(it['institution'])}</div>
        <p>{escape(it['description'])}</p>
        <span class="tl-tag">{escape(it['tag'])}</span>
      </div>
    </div>"""
    return f"""
<section id="teaching">
  <div class="section-header reveal">
    <span class="section-num">04</span>
    <h2 class="section-title">Teaching &amp; Mentoring</h2>
    <div class="section-line"></div>
  </div>
  <div class="timeline">{items}
  </div>
</section>"""

def build_skills(s):
    groups = ""
    for g in s.get("groups", []):
        tags = "".join(f'<span class="skill-tag">{escape(t)}</span>' for t in g["tags"])
        groups += f"""
    <div class="skill-group reveal">
      <h3>{escape(g['name'])}</h3>
      <div class="skill-tags">{tags}</div>
    </div>"""
    return f"""
<section id="skills">
  <div class="section-header reveal">
    <span class="section-num">05</span>
    <h2 class="section-title">Technical Skills</h2>
    <div class="section-line"></div>
  </div>
  <div class="skills-grid">{groups}
  </div>
</section>"""

def build_contact(c):
    items = ""
    for it in c.get("items", []):
        ico = contact_icon_html(it.get("icon", "email"))
        items += f"""
    <a href="{it['url']}" class="contact-item reveal" target="_blank">
      <div class="contact-icon">{ico}</div>
      <div class="contact-text">
        <div class="contact-label">{escape(it['label'])}</div>
        <div class="contact-value">{escape(it['value'])}</div>
      </div>
    </a>"""
    return f"""
<section id="contact">
  <div class="section-header reveal">
    <span class="section-num">06</span>
    <h2 class="section-title">Get in Touch</h2>
    <div class="section-line"></div>
  </div>
  <div class="contact-grid">{items}
  </div>
</section>"""

# ── CSS ───────────────────────────────────────────────────────────────────────

CSS = """
  :root {
    --bg:#ffffff;--surface:#f5f6f8;--surface2:#eef0f4;
    --border:#d0d7de;--border-light:#e8ebf0;
    --navy:#1a2744;--blue:#2563a8;--blue-dim:rgba(37,99,168,.10);
    --teal:#1d7a8a;--muted:#6e7c8e;--text:#24303f;
    --green:#1a7a45;--green-dim:rgba(26,122,69,.10);
    --red-dim:rgba(180,80,50,.09);--red:#b45032;--radius:8px;
  }
  *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
  html{scroll-behavior:smooth}
  body{font-family:'DM Sans',sans-serif;background:var(--bg);color:var(--text);line-height:1.7;overflow-x:hidden}

  /* NAV */
  nav{position:fixed;top:0;left:0;right:0;z-index:100;display:flex;align-items:center;
      justify-content:space-between;padding:0 3rem;height:56px;background:var(--navy);
      box-shadow:0 2px 8px rgba(0,0,0,.15)}
  .nav-logo{font-family:'Cormorant Garamond',serif;font-size:1.2rem;font-weight:500;color:#fff;letter-spacing:.04em}
  .nav-logo span{color:#7eb8e8}
  .nav-links{display:flex;gap:0;list-style:none;height:100%}
  .nav-links a{display:flex;align-items:center;height:56px;padding:0 1.1rem;font-size:.82rem;
               font-weight:500;color:rgba(255,255,255,.72);text-decoration:none;transition:color .2s,background .2s}
  .nav-links a:hover{color:#fff;background:rgba(255,255,255,.08)}

  /* HERO */
  #hero{padding:0;background:linear-gradient(135deg,#eef3fb 0%,#e5edf8 40%,#f0f4fb 100%);
        position:relative;overflow:hidden}
  #hero::before{content:'';position:absolute;inset:0;
    background-image:linear-gradient(rgba(37,99,168,.055) 1px,transparent 1px),
                     linear-gradient(90deg,rgba(37,99,168,.055) 1px,transparent 1px);
    background-size:40px 40px;pointer-events:none;z-index:0}
  .hero-inner{position:relative;z-index:1;display:grid;grid-template-columns:58fr 42fr;
              gap:3rem;align-items:center;max-width:1420px;margin:0 auto;
              padding:7rem 3rem 4rem}
  .hero-left{display:flex;flex-direction:column}
  .hero-descriptor{font-family:'DM Mono',monospace;font-size:.7rem;letter-spacing:.14em;
                   text-transform:uppercase;color:var(--blue);background:var(--blue-dim);
                   border:1px solid rgba(37,99,168,.22);padding:.35rem .9rem;border-radius:20px;
                   margin-bottom:1.4rem;display:inline-flex;align-items:center;gap:.5rem;
                   width:fit-content;animation:fadeUp .6s ease both}
  .hero-descriptor::before{content:'●';font-size:.45rem;color:var(--teal)}
  .hero-name{font-family:'Cormorant Garamond',serif;font-size:clamp(3rem,5.5vw,4.8rem);
             font-weight:300;line-height:1.05;color:var(--navy);margin-bottom:1.2rem;
             animation:fadeUp .6s .1s ease both}
  .hero-name em{font-style:italic;color:var(--blue)}
  .hero-statement{font-size:.97rem;color:var(--text);line-height:1.85;max-width:520px;
                  margin-bottom:1.4rem}
  .hero-affiliations{display:flex;flex-direction:column;gap:.25rem;margin-bottom:1.2rem}
  .hero-aff-item{font-family:'DM Mono',monospace;font-size:.72rem;color:var(--muted);letter-spacing:.03em}
  .hero-topics{display:flex;flex-wrap:wrap;gap:.45rem;margin-bottom:1.6rem}
  .hero-topic{font-family:'DM Mono',monospace;font-size:.68rem;letter-spacing:.08em;
              text-transform:uppercase;background:var(--surface2);color:var(--navy);
              border:1px solid var(--border);padding:.28rem .75rem;border-radius:20px}
  .hero-links{display:flex;gap:.7rem;flex-wrap:wrap}
  .btn{display:inline-flex;align-items:center;gap:.4rem;padding:.5rem 1.1rem;border-radius:var(--radius);
       font-size:.76rem;font-weight:500;text-decoration:none;white-space:nowrap;
       transition:all .18s;cursor:pointer;border:none}
  .btn svg{flex-shrink:0}
  .btn-cv{background:var(--navy);color:#fff;box-shadow:0 2px 8px rgba(26,39,68,.28)}
  .btn-cv:hover{background:#0f1d3a;transform:translateY(-1px);box-shadow:0 4px 14px rgba(26,39,68,.36)}
  .btn-scholar{background:#fff;color:var(--blue);border:1.5px solid var(--blue);box-shadow:0 1px 4px rgba(37,99,168,.10)}
  .btn-scholar:hover{background:var(--blue-dim);transform:translateY(-1px)}
  .btn-outline{background:#fff;color:var(--navy);border:1px solid var(--border);box-shadow:0 1px 4px rgba(0,0,0,.06)}
  .btn-outline:hover{border-color:var(--blue);color:var(--blue);transform:translateY(-1px)}
  .hero-right{position:relative;z-index:1;display:flex;flex-direction:column;gap:1.5rem}
  .hero-portrait-area{display:flex;flex-direction:column;align-items:center;gap:.9rem}
  .hero-photo-wrap{position:relative;width:min(240px,90%);aspect-ratio:4/5;border-radius:12px;
                   overflow:hidden;border:3px solid var(--border);box-shadow:0 8px 32px rgba(26,39,68,.14)}
  .hero-photo{width:100%;height:100%;object-fit:cover;display:block}
  .hero-photo-placeholder{display:none;flex-direction:column;align-items:center;justify-content:center;
                           gap:.5rem;width:100%;height:100%;
                           background:linear-gradient(145deg,#e8edf5,#d5dce8);
                           position:absolute;inset:0}
  .hero-photo-initials{font-family:'Cormorant Garamond',serif;font-size:3rem;font-weight:400;
                        color:var(--blue);line-height:1}
  .hero-photo-hint{font-family:'DM Mono',monospace;font-size:.65rem;text-align:center;
                   color:var(--muted);letter-spacing:.06em;line-height:1.6}
  /* Highlight white cards */
  .hero-highlights{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:.7rem}
  .hero-hl{background:#fff;border:1px solid var(--border);border-radius:var(--radius);
            padding:.9rem .7rem;text-align:center;
            box-shadow:0 1px 6px rgba(0,0,0,.05);transition:border-color .18s,box-shadow .18s}
  .hero-hl:hover{border-color:var(--blue);box-shadow:0 3px 12px rgba(37,99,168,.10)}
  .hero-hl-num{font-family:'Cormorant Garamond',serif;font-size:1.6rem;font-weight:400;
               color:var(--blue);line-height:1;margin-bottom:.25rem}
  .hero-hl-label{font-family:'DM Mono',monospace;font-size:.58rem;text-transform:uppercase;
                  letter-spacing:.09em;color:var(--muted);line-height:1.45}
  /* Recent Updates — white card feed */
  .hero-news{border-top:1px solid var(--border-light);padding:2rem 3rem;
             position:relative;z-index:1}
  .hero-news-inner{max-width:1420px;margin:0 auto}
  .hero-news-heading{font-family:'DM Mono',monospace;font-size:.67rem;text-transform:uppercase;
                     letter-spacing:.13em;color:var(--muted);margin-bottom:1.25rem}
  .news-feed{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:.85rem}
  .news-card{background:#fff;border:1px solid var(--border);border-radius:var(--radius);
             padding:1rem 1.25rem;box-shadow:0 1px 6px rgba(0,0,0,.05);
             transition:border-color .18s,transform .18s,box-shadow .18s}
  .news-card:hover{border-color:var(--blue);transform:translateY(-2px);box-shadow:0 4px 14px rgba(37,99,168,.09)}
  .news-card-meta{display:flex;align-items:center;gap:.55rem;margin-bottom:.55rem}
  .news-date{font-family:'DM Mono',monospace;font-size:.65rem;color:var(--muted);
             letter-spacing:.06em;white-space:nowrap}
  .news-type{font-family:'DM Mono',monospace;font-size:.63rem;color:var(--muted);
             letter-spacing:.04em}
  .news-type::before{content:'·';margin-right:.35rem;color:var(--border)}
  .news-text{font-size:.9rem;color:var(--text);line-height:1.65;margin:0}
  .news-link{color:var(--text);text-decoration:none;border-bottom:1px solid transparent;
             transition:color .15s,border-color .15s}
  .news-link:hover{color:var(--blue);border-bottom-color:var(--blue)}
  .news-ext-icon{font-size:.78rem;color:var(--muted)}
  .news-hidden{display:none!important}
  .news-more-btn{display:none;margin-top:1.1rem;font-family:'DM Mono',monospace;
                 font-size:.7rem;letter-spacing:.08em;text-transform:uppercase;
                 background:none;border:1px solid var(--border);border-radius:4px;
                 color:var(--blue);padding:.45rem 1.1rem;cursor:pointer;
                 transition:border-color .18s,background .18s}
  .news-more-btn:hover{border-color:var(--blue);background:var(--blue-dim)}
  @media(prefers-reduced-motion:reduce){
    *,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}
    .reveal{opacity:1;transform:none;transition:none}
  }

  /* SECTIONS */
  section{padding:5rem 3rem;position:relative}
  section:nth-child(even){background:var(--surface);border-top:1px solid var(--border-light);border-bottom:1px solid var(--border-light)}
  .section-header{display:flex;align-items:baseline;gap:1rem;margin-bottom:3rem}
  .section-num{font-family:'DM Mono',monospace;font-size:.68rem;color:var(--blue);letter-spacing:.1em}
  .section-title{font-family:'Cormorant Garamond',serif;font-size:clamp(1.8rem,3vw,2.5rem);font-weight:400;color:var(--navy)}
  .section-line{flex:1;height:2px;background:linear-gradient(to right,var(--border),transparent);margin-left:1rem;max-width:200px}

  /* RESEARCH CARDS */
  .research-grid{display:grid;grid-template-columns:1fr 1fr;gap:1.2rem;max-width:1000px}
  .research-card{background:#fff;border:1px solid var(--border);border-top:3px solid var(--blue);
                 border-radius:var(--radius);padding:1.4rem 1.5rem;
                 box-shadow:0 1px 6px rgba(0,0,0,.05);transition:transform .2s,box-shadow .2s}
  .research-card:hover{transform:translateY(-3px);box-shadow:0 6px 20px rgba(37,99,168,.10)}
  .research-card h3{font-family:'Cormorant Garamond',serif;font-size:1.1rem;font-weight:600;color:var(--navy);margin-bottom:.5rem}
  .research-card p{font-size:.88rem;color:var(--muted);line-height:1.65}

  /* TIMELINE */
  .timeline{max-width:900px}
  .tl-item{display:grid;grid-template-columns:140px 1fr;gap:2rem;position:relative;padding-bottom:2.5rem}
  .tl-item:not(:last-child)::after{content:'';position:absolute;left:140px;top:1.5rem;bottom:0;
                                    width:1px;background:var(--border);margin-left:1rem}
  .tl-year{font-family:'DM Mono',monospace;font-size:.7rem;color:var(--muted);letter-spacing:.06em;
            padding-top:.25rem;text-align:right;line-height:1.5}
  .tl-content{background:#fff;border:1px solid var(--border);border-radius:var(--radius);
               padding:1.4rem 1.5rem;margin-left:1.5rem;position:relative;
               box-shadow:0 1px 6px rgba(0,0,0,.05);transition:border-color .2s,box-shadow .2s}
  .tl-content::before{content:'';position:absolute;left:-1.8rem;top:1.25rem;width:10px;height:10px;
                       border-radius:50%;background:var(--blue);border:2px solid var(--bg);
                       box-shadow:0 0 0 2px var(--blue)}
  .tl-content:hover{border-color:var(--blue);box-shadow:0 4px 16px rgba(37,99,168,.10)}
  .tl-content h3{font-family:'Cormorant Garamond',serif;font-size:1.2rem;font-weight:600;color:var(--navy);margin-bottom:.2rem}
  .tl-institution{font-family:'DM Mono',monospace;font-size:.7rem;color:var(--teal);letter-spacing:.04em;margin-bottom:.8rem}
  .tl-content p{font-size:.88rem;color:var(--text);line-height:1.75}
  .tl-tag{display:inline-block;margin-top:.8rem;font-family:'DM Mono',monospace;font-size:.63rem;
           text-transform:uppercase;letter-spacing:.1em;color:var(--blue);background:var(--blue-dim);
           border:1px solid rgba(37,99,168,.2);padding:.2rem .7rem;border-radius:20px}

  /* PUBLICATIONS */
  .pub-filter{display:flex;gap:.5rem;flex-wrap:wrap;margin-bottom:2rem}
  .pub-filter-btn{font-family:'DM Mono',monospace;font-size:.7rem;text-transform:uppercase;
                  letter-spacing:.08em;padding:.4rem 1rem;border-radius:20px;cursor:pointer;
                  border:1px solid var(--border);background:#fff;color:var(--muted);transition:all .18s}
  .pub-filter-btn:hover,.pub-filter-btn.active{border-color:var(--blue);color:var(--blue);background:var(--blue-dim)}
  .pub-list{max-width:960px;display:flex;flex-direction:column;gap:.85rem}
  .pub-section-head{display:flex;align-items:center;gap:1rem;margin:2rem 0 .4rem;padding-top:.5rem}
  .pub-section-head:first-child{margin-top:.5rem}
  .pub-section-head::before,.pub-section-head::after{content:'';flex:1;height:1px;background:var(--border)}
  .pub-section-label{font-family:'DM Mono',monospace;font-size:.63rem;text-transform:uppercase;
                     letter-spacing:.13em;white-space:nowrap;color:var(--muted);padding:0 .25rem}
  .pub-item{background:#fff;border:1px solid var(--border);border-radius:var(--radius);
             padding:1.2rem 1.5rem;display:grid;grid-template-columns:auto 1fr auto;gap:1.1rem;
             align-items:start;box-shadow:0 1px 4px rgba(0,0,0,.04);
             transition:border-color .18s,transform .18s,box-shadow .18s}
  .pub-item:hover{border-color:var(--blue);transform:translateX(4px);box-shadow:0 3px 12px rgba(37,99,168,.08)}
  .pub-item[data-type="journal"]{background:rgba(37,99,168,.035);border-color:rgba(37,99,168,.18)}
  .pub-item[data-type="conference"]{background:rgba(22,163,74,.04);border-color:rgba(22,163,74,.2)}
  .pub-item[data-type="workshop"]{background:rgba(22,163,74,.04);border-color:rgba(22,163,74,.2)}
  .pub-item[data-type="book"]{background:rgba(234,88,12,.04);border-color:rgba(234,88,12,.18)}
  .pub-num{font-family:'DM Mono',monospace;font-size:.68rem;color:var(--blue);padding-top:.1rem;min-width:28px}
  .pub-title{font-family:'Cormorant Garamond',serif;font-size:1.05rem;font-weight:600;color:var(--navy);
              line-height:1.4;margin-bottom:.3rem}
  .pub-pdf-btn{display:inline-flex;align-items:center;gap:.3rem;margin-left:.6rem;
               font-family:'DM Mono',monospace;font-size:.62rem;text-transform:uppercase;
               letter-spacing:.08em;color:var(--blue);background:var(--blue-dim);
               border:1px solid rgba(37,99,168,.25);padding:.15rem .55rem;border-radius:4px;
               text-decoration:none;vertical-align:middle;transition:all .15s}
  .pub-pdf-btn:hover{background:var(--blue);color:#fff}
  .pub-item[data-type="conference"] .pub-pdf-btn,.pub-item[data-type="workshop"] .pub-pdf-btn{color:#16a34a;background:rgba(22,163,74,.08);border-color:rgba(22,163,74,.28)}
  .pub-item[data-type="conference"] .pub-pdf-btn:hover,.pub-item[data-type="workshop"] .pub-pdf-btn:hover{background:#16a34a;color:#fff}
  .pub-item[data-type="book"] .pub-pdf-btn{color:#ea580c;background:rgba(234,88,12,.08);border-color:rgba(234,88,12,.25)}
  .pub-item[data-type="book"] .pub-pdf-btn:hover{background:#ea580c;color:#fff}
  .pub-authors{font-size:.82rem;color:var(--muted);margin-bottom:.3rem}
  .pub-authors strong{color:var(--text);font-weight:600}
  .pub-venue{font-family:'DM Mono',monospace;font-size:.7rem;color:var(--teal);letter-spacing:.02em}
  .pub-title-link{color:inherit;text-decoration:none;border-bottom:1px solid transparent;transition:color .15s,border-color .15s}
  .pub-title-link:hover{color:var(--blue);border-bottom-color:var(--blue)}
  .pub-meta{display:flex;flex-direction:column;align-items:flex-end;gap:.4rem}
  .pub-badge{font-family:'DM Mono',monospace;font-size:.62rem;text-transform:uppercase;
              letter-spacing:.1em;padding:.22rem .65rem;border-radius:20px;white-space:nowrap}
  .badge-journal{background:var(--blue-dim);color:var(--blue);border:1px solid rgba(37,99,168,.25)}
  .badge-conference{background:var(--green-dim);color:var(--green);border:1px solid rgba(26,122,69,.2)}
  .badge-book{background:var(--red-dim);color:var(--red);border:1px solid rgba(180,80,50,.2)}

  /* SKILLS */
  .skills-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:1.1rem;max-width:1000px}
  .skill-group{background:#fff;border:1px solid var(--border);border-radius:var(--radius);
                padding:1.3rem;box-shadow:0 1px 4px rgba(0,0,0,.04);transition:border-color .18s,box-shadow .18s}
  .skill-group:hover{border-color:var(--blue);box-shadow:0 3px 12px rgba(37,99,168,.08)}
  .skill-group h3{font-family:'DM Mono',monospace;font-size:.67rem;text-transform:uppercase;
                  letter-spacing:.12em;color:var(--blue);margin-bottom:.85rem;padding-bottom:.6rem;
                  border-bottom:1px solid var(--border-light)}
  .skill-tags{display:flex;flex-wrap:wrap;gap:.4rem}
  .skill-tag{font-size:.78rem;color:var(--text);background:var(--surface);border:1px solid var(--border);
              padding:.25rem .75rem;border-radius:4px;transition:all .15s}
  .skill-tag:hover{background:var(--blue-dim);border-color:var(--blue);color:var(--blue)}

  /* CONTACT */
  .contact-grid{display:grid;grid-template-columns:1fr 1fr;gap:1.1rem;max-width:800px}
  .contact-item{display:flex;gap:1rem;align-items:flex-start;background:#fff;border:1px solid var(--border);
                 border-radius:var(--radius);padding:1.2rem;text-decoration:none;
                 box-shadow:0 1px 4px rgba(0,0,0,.04);transition:border-color .18s,transform .18s,box-shadow .18s}
  .contact-item:hover{border-color:var(--blue);transform:translateY(-2px);box-shadow:0 4px 14px rgba(37,99,168,.10)}
  .contact-icon{width:36px;height:36px;border-radius:8px;background:var(--blue-dim);color:var(--blue);
                 display:flex;align-items:center;justify-content:center;font-size:1rem;flex-shrink:0;font-weight:600}
  .contact-label{font-family:'DM Mono',monospace;font-size:.63rem;text-transform:uppercase;letter-spacing:.1em;color:var(--muted)}
  .contact-value{font-size:.87rem;color:var(--text);margin-top:.15rem;word-break:break-all}

  /* FOOTER */
  footer{text-align:center;padding:1.8rem;background:var(--navy);
          font-family:'DM Mono',monospace;font-size:.68rem;color:rgba(255,255,255,.45)}
  footer a{color:#7eb8e8;text-decoration:none}

  /* ANIMATIONS */
  @keyframes fadeUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
  @keyframes fadeLeft{from{opacity:0;transform:translateX(20px)}to{opacity:1;transform:translateX(0)}}
  .reveal{opacity:0;transform:translateY(20px);transition:opacity .55s ease,transform .55s ease}
  .reveal.visible{opacity:1;transform:translateY(0)}

  ::-webkit-scrollbar{width:6px}
  ::-webkit-scrollbar-track{background:var(--surface)}
  ::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
  ::-webkit-scrollbar-thumb:hover{background:var(--blue)}

  @media(max-width:768px){
    nav{padding:0 1.2rem}.nav-links{display:none}
    .hero-inner{grid-template-columns:1fr;padding:5rem 1.5rem 2.5rem;gap:2rem}
    .hero-right{order:2}.hero-portrait-area{order:1}
    .hero-news{padding:1.2rem 1.5rem}
    .news-feed{grid-template-columns:1fr}
    .hero-links{flex-wrap:wrap}
    section{padding:3.5rem 1.5rem}
    .research-grid{grid-template-columns:1fr}
    .tl-item{grid-template-columns:1fr}.tl-item::after{display:none}
    .tl-content{margin-left:0}.tl-content::before{display:none}
    .contact-grid{grid-template-columns:1fr}
    .pub-item{grid-template-columns:auto 1fr}.pub-meta{display:none}
  }
"""

JS = """
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });
  document.querySelectorAll('.reveal').forEach((el, i) => {
    el.style.transitionDelay = (i % 4) * 0.07 + 's';
    obs.observe(el);
  });
  function filterPubs(type, btn) {
    document.querySelectorAll('.pub-filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.pub-item').forEach(item => {
      const t = item.dataset.type;
      const match = type === 'all' || t === type || (type === 'conference' && t === 'workshop');
      item.style.display = match ? 'grid' : 'none';
    });
    document.querySelectorAll('.pub-section-head').forEach(h => {
      h.style.display = type === 'all' ? 'flex' : 'none';
    });
  }
  // News show more / show less
  (function(){
    var btn = document.getElementById('news-more-btn');
    if (!btn) return;
    btn.style.display = 'block';
    var extras = Array.from(document.querySelectorAll('.news-card.news-hidden'));
    btn.addEventListener('click', function(){
      var open = btn.getAttribute('aria-expanded') === 'true';
      extras.forEach(function(r){
        if (open) {
          r.classList.add('news-hidden');
        } else {
          r.classList.remove('news-hidden');
          obs.observe(r);           // trigger reveal animation when shown
        }
      });
      btn.setAttribute('aria-expanded', open ? 'false' : 'true');
      btn.textContent = open ? 'Show more ↓' : 'Show less ↑';
    });
  })();
  // auto-update footer year
  document.getElementById('year').textContent = new Date().getFullYear();
"""

# ── main ─────────────────────────────────────────────────────────────────────

def build():
    src = Path("content.yaml")
    if not src.exists():
        print("ERROR: content.yaml not found. Make sure it's in the same folder as build.py.")
        sys.exit(1)

    with open(src, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    site   = data.get("site", {})
    title  = site.get("title", "Academic Page")
    author = site.get("author", "")

    # nav links match section ids
    nav_items = [
        ("about",        "About"),
        ("experience",   "Experience"),
        ("publications", "Publications"),
        ("teaching",     "Teaching"),
        ("skills",       "Skills"),
        ("contact",      "Contact"),
    ]
    nav_html = "".join(f'<li><a href="#{sid}">{label}</a></li>' for sid, label in nav_items)

    # Sort news newest-first (build.py owns ordering; YAML order is the fallback)
    raw_news = data.get("news", [])
    news_sorted = sorted(raw_news, key=lambda x: parse_news_date(x.get("date", "")), reverse=True)

    sections = "\n".join([
        build_hero(data.get("hero", {}), news_sorted),
        build_about(data.get("about", {})),
        build_experience(data.get("experience", {})),
        build_publications(data.get("publications", {})),
        build_teaching(data.get("teaching", {})),
        build_skills(data.get("skills", {})),
        build_contact(data.get("contact", {})),
    ])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)}</title>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,500;0,600;1,300;1,400&family=DM+Mono:wght@300;400&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet">
<style>
{CSS}
</style>
</head>
<body>

<nav>
  <div class="nav-logo">A<span>.</span>Sikdar</div>
  <ul class="nav-links">{nav_html}</ul>
</nav>

{sections}

<footer>
  <p>&copy; <span id="year"></span> {escape(author)} &nbsp;&middot;&nbsp;
  <a href="https://github.com/Arindam-1991">github.com/Arindam-1991</a></p>
</footer>

<script>
{JS}
</script>
</body>
</html>"""

    out = Path("index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅  index.html generated successfully ({out.stat().st_size // 1024} KB)")
    print("📤  Upload index.html to your GitHub repo to update your site.")

if __name__ == "__main__":
    build()
