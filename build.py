"""Builds the Symbol Interactive site (symbolinteractive.com.tr): python3 build.py

Turkish pages at the root, English under en/; every page links its twin (language switch + hreflang).
Company pages use site.css (Gabarito + Atkinson Hyperlegible Next, self-hosted, OFL); the game's page /starjars uses
starjars.css (the game's own night sky, DynaPuff + Nunito). No cookies, no analytics, no third-party requests.

The legal texts follow the decisions memo:
~/game-studio/docs/superpowers/research/2026-11-04-symbol-interactive-legal-decisions.md
Never written here: CNAME and app-ads.txt (they are maintained by hand).
"""
import math
import pathlib

ROOT = pathlib.Path(__file__).parent
SITE = "https://symbolinteractive.com.tr"
MAIL = "symbolinteractive@gmail.com"  # the support address the user set in the release checklist (2026-11-03)
CONTROLLER = "Cem Tezgelen"  # the developer's own name, as the user gave it (2026-11-03)
UPDATED = {"tr": "4 Kasım 2026", "en": "4 November 2026"}  # privacy policy, terms and deletion pages

# Every page and its twin. Paths are the files; URLs are root-absolute so the 404 page works at any depth.
PAGES = {
    "home": {"tr": "index.html", "en": "en/index.html"},
    "games": {"tr": "oyunlar.html", "en": "en/games.html"},
    "about": {"tr": "hakkimizda.html", "en": "en/about.html"},
    "starjars": {"tr": "starjars.html", "en": "en/starjars.html"},
    "support": {"tr": "destek.html", "en": "en/support.html"},
    "privacy": {"tr": "gizlilik.html", "en": "en/privacy.html"},
    "terms": {"tr": "kullanim-kosullari.html", "en": "en/terms.html"},
    "delete": {"tr": "hesap-silme.html", "en": "en/delete-account.html"},
}


def u(key, lang):
    path = PAGES[key][lang]
    return {"index.html": "/", "en/index.html": "/en/"}.get(path, "/" + path)


def mailto(subject=None):
    q = f"?subject={subject.replace(' ', '%20')}" if subject else ""
    return f'<a href="mailto:{MAIL}{q}">{MAIL}</a>'


# ---------------------------------------------------------------- pieces (the studio's symbols, drawn in code)

COLORS = {"cobalt": ("#2E4BDB", "#1F35A8"), "lemon": ("#FFD23F", "#D9A915"), "olive": ("#8FA33A", "#6B7C25"), "sky": ("#7FB0FF", "#5A8DE6")}


def shape(kind, fill, cx=30, cy=30, s=1.0):
    """One game piece centred on (cx, cy) in a 60-unit cell."""
    if kind == "circle":
        return f'<circle cx="{cx}" cy="{cy}" r="{19 * s:.1f}" fill="{fill}"/>'
    if kind == "ring":
        return f'<circle cx="{cx}" cy="{cy}" r="{15 * s:.1f}" fill="none" stroke="{fill}" stroke-width="{10 * s:.1f}"/>'
    if kind == "diamond":
        r = 19 * s
        pts = f"{cx},{cy - r:.1f} {cx + r:.1f},{cy} {cx},{cy + r:.1f} {cx - r:.1f},{cy}"
        return f'<polygon points="{pts}" fill="{fill}" stroke="{fill}" stroke-width="{7 * s:.1f}" stroke-linejoin="round"/>'
    if kind == "triangle":
        r = 20 * s
        pts = " ".join(f"{cx + r * math.cos(a):.1f},{cy + 3 * s + r * math.sin(a):.1f}" for a in (-math.pi / 2, math.pi / 6, 5 * math.pi / 6))
        return f'<polygon points="{pts}" fill="{fill}" stroke="{fill}" stroke-width="{7 * s:.1f}" stroke-linejoin="round"/>'
    raise ValueError(kind)


def piece(kind, color, cx=30, cy=30, s=1.0):
    """A piece with its darker lower edge, so it reads as something you could pick up."""
    main, edge = COLORS[color]
    return shape(kind, edge, cx, cy + 3 * s, s) + shape(kind, main, cx, cy, s)


def piece_icon(kind, color, label=None):
    a11y = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    return f'<svg viewBox="0 0 60 64" {a11y}>{piece(kind, color)}</svg>'


ROWS = [("circle", "cobalt"), ("diamond", "lemon"), ("triangle", "olive"), ("ring", "sky")]
# Where each piece starts before it settles (dx, dy, rotation); fixed so the page is the same every build.
SCATTER = [(-120, -150, -40), (60, -190, 25), (150, -60, 70), (-40, -230, -15), (130, -210, 45), (-150, -40, -70), (20, -120, 90), (90, -260, -30),
           (-90, -180, 35), (170, -140, -55), (-60, -90, 20), (40, -240, -80), (110, -100, 60), (-170, -200, -25), (-10, -170, 50), (70, -50, -45)]


def board(label):
    cell, gap, pad = 60, 12, 18
    size = pad * 2 + 4 * cell + 3 * gap
    parts = [f'<rect class="tray-edge" x="0" y="10" width="{size}" height="{size}" rx="30"/>',
             f'<rect class="tray" x="1" y="1" width="{size - 2}" height="{size - 2}" rx="29"/>']
    for r in range(4):
        for c in range(4):
            x, y = pad + c * (cell + gap), pad + r * (cell + gap)
            parts.append(f'<rect class="slot" x="{x}" y="{y}" width="{cell}" height="{cell}" rx="14"/>')
    order = 0
    for r, (kind, color) in enumerate(ROWS):
        y = pad + r * (cell + gap)
        parts.append(f'<rect class="row-done" style="--row:{r}" x="{pad - 5}" y="{y - 5}" width="{4 * cell + 3 * gap + 10}" height="{cell + 10}" rx="18" '
                     f'fill="none" stroke="{COLORS[color][0]}" stroke-width="3"/>')
        for c in range(4):
            x = pad + c * (cell + gap)
            dx, dy, rot = SCATTER[order]
            parts.append(f'<g transform="translate({x} {y})"><g class="piece" style="--i:{order};--dx:{dx}px;--dy:{dy}px;--r:{rot}deg">'
                         f'{piece(kind, color, s=.92)}</g></g>')
            order += 1
    return f'<div class="board"><svg viewBox="0 0 {size} {size + 10}" role="img" aria-label="{label}">{"".join(parts)}</svg></div>'


def mark(css_vars=True):
    """The studio's mark: three pieces in place and a ring falling into the fourth slot."""
    cob = "var(--cobalt)" if css_vars else "#5B74F0"
    return (f'<svg viewBox="0 0 40 40" aria-hidden="true"><rect x="2" y="2" width="17" height="17" rx="5" style="fill:{cob}"/>'
            f'<rect x="21" y="2" width="17" height="17" rx="5" fill="#FFD23F"/><rect x="2" y="21" width="17" height="17" rx="5" fill="#8FA33A"/>'
            f'<circle cx="29.5" cy="29.5" r="5.6" fill="none" stroke-width="3.6" style="stroke:{cob}"/></svg>')


def empty_slot():
    return ('<svg viewBox="0 0 60 64" aria-hidden="true"><rect x="3" y="3" width="54" height="54" rx="14" fill="none" stroke="var(--line)" stroke-width="3" '
            'stroke-dasharray="7 6"/><circle cx="30" cy="30" r="12" fill="none" stroke="var(--muted)" stroke-width="3" stroke-dasharray="4 5"/></svg>')


# The Star Jars jar: the game's icon, drawn large on its own page; its stars drop in once on load.
def star(cx, cy, r, fill, rot=0.0, inner=0.48):
    d = ""
    for i in range(10):
        a = -math.pi / 2 + rot + i * math.pi / 5
        k = r * inner if i % 2 else r
        d += ("L" if i else "M") + f"{cx + k * math.cos(a):.1f} {cy + k * math.sin(a):.1f}"
    return f'<path d="{d}Z" fill="{fill}" stroke="#fff" stroke-width="{r * 0.18:.1f}" stroke-linejoin="round"/>'


JAR_STARS = [(77, 193, 22, "#FF4FA6", .1), (123, 191, 22, "#14DCC8", -.25), (99, 156, 22, "#FFCC2E", .3), (75, 120, 19, "#A273FF", 0), (121, 118, 19, "#3FDD77", .2)]


def jar(size_class="hero-jar", animate=True, label="Yıldızlarla dolu cam kavanoz"):
    stars = "".join(f'<g class="drop" style="--i:{i}">{star(x, y, r, c, rot)}</g>' if animate else star(x, y, r, c, rot)
                    for i, (x, y, r, c, rot) in enumerate(JAR_STARS))
    a11y = f'role="img" aria-label="{label}"' if label else 'aria-hidden="true"'
    return f'''<svg class="{size_class}" viewBox="0 0 200 240" {a11y}>
  <rect x="44" y="52" width="112" height="170" rx="40" fill="rgba(255,255,255,.13)" stroke="#fff" stroke-width="6"/>
  {stars}
  <rect x="58" y="70" width="8" height="34" rx="4" fill="#fff" opacity=".42"/>
  <rect x="62" y="30" width="76" height="28" rx="9" fill="#FFC93C" stroke="#fff" stroke-width="5"/>
</svg>'''


def shots(lang, alt):
    names = {"01-board": alt[0], "03-galaxy": alt[1], "04-exo": alt[2]}
    return "".join(f'<img src="/img/{lang}-{n}.jpg" width="270" height="587" alt="{a}" loading="lazy">' for n, a in names.items())


SHOT_ALT = {
    "tr": ["Oyun ekranı: renkli yıldızlar kavanozlarda", "Gökyüzü haritası: takımyıldızlar", "Uzay bölümü"],
    "en": ["The game board: colourful stars in jars", "The sky map: constellations", "A space chapter"],
}

# ---------------------------------------------------------------- the frame of every company page

T = {
    "tr": {"skip": "İçeriğe geç", "nav": "Ana menü", "games": "Oyunlar", "about": "Hakkımızda", "support": "Destek", "other": "English", "other_lang": "en",
           "home": "Symbol Interactive ana sayfa", "foot_about": "Aydın'da kurulmuş bağımsız bir mobil oyun stüdyosu.",
           "no_track": "Bu site çerez kullanmaz ve ziyaretçileri izlemez.", "studio": "Stüdyo", "help": "Yardım", "legal": "Yasal",
           "home_l": "Ana sayfa", "privacy": "Gizlilik politikası", "terms": "Kullanım koşulları", "delete": "Hesap silme", "starjars": "Star Jars",
           "contents": "Bu sayfada"},
    "en": {"skip": "Skip to content", "nav": "Main menu", "games": "Games", "about": "About", "support": "Support", "other": "Türkçe", "other_lang": "tr",
           "home": "Symbol Interactive home", "foot_about": "An independent mobile game studio founded in Aydın, Türkiye.",
           "no_track": "This site uses no cookies and does not track visitors.", "studio": "Studio", "help": "Help", "legal": "Legal",
           "home_l": "Home", "privacy": "Privacy policy", "terms": "Terms of use", "delete": "Delete account", "starjars": "Star Jars",
           "contents": "On this page"},
}


def alternates(key, own_lang, own_path=None):
    if key is None:
        return ""
    canon = SITE + (own_path or u(key, own_lang))
    return (f'<link rel="canonical" href="{canon}">\n'
            f'<link rel="alternate" hreflang="tr" href="{SITE}{u(key, "tr")}">\n'
            f'<link rel="alternate" hreflang="en" href="{SITE}{u(key, "en")}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{SITE}{u(key, "tr")}">')


def head(lang, title, description, key, css, own_path=None, favicon="/favicon.svg", theme=None):
    theme_meta = (f'<meta name="theme-color" content="{theme}">' if theme else
                  '<meta name="theme-color" content="#F4F6FA" media="(prefers-color-scheme: light)">\n'
                  '<meta name="theme-color" content="#0E1328" media="(prefers-color-scheme: dark)">')
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
{theme_meta}
{alternates(key, lang, own_path)}
<link rel="icon" href="{favicon}" type="image/svg+xml">
<link rel="preload" href="/fonts/{'Gabarito-latin.woff2' if css == '/site.css' else 'DynaPuff-Bold.ttf'}" as="font" crossorigin>
<link rel="stylesheet" href="{css}">
</head>'''


def header(lang, key, other_href):
    t = T[lang]
    items = []
    for k in ("games", "about", "support"):
        cur = ' aria-current="page"' if k == key or (k == "games" and key == "starjars") else ""
        items.append(f'<li><a href="{u(k, lang)}"{cur}>{t[k]}</a></li>')
    items.append(f'<li class="lang"><a href="{other_href}" lang="{t["other_lang"]}" hreflang="{t["other_lang"]}">{t["other"]}</a></li>')
    return f'''<a class="skip" href="#main">{t["skip"]}</a>
<header class="top"><div class="wrap">
  <a class="mark" href="{u("home", lang)}" aria-label="{t["home"]}">{mark()}<span>Symbol Interactive</span></a>
  <nav aria-label="{t["nav"]}"><ul>{"".join(items)}</ul></nav>
</div></header>'''


def footer(lang, other_href):
    t = T[lang]
    return f'''<footer class="bottom"><div class="wrap">
  <div class="about">
    <a class="mark" href="{u("home", lang)}" aria-label="{t["home"]}">{mark()}<span>Symbol Interactive</span></a>
    <p>{t["foot_about"]}</p>
    <p>{t["no_track"]}</p>
    <p>© 2026 Symbol Interactive</p>
  </div>
  <div><h2>{t["studio"]}</h2><ul>
    <li><a href="{u("home", lang)}">{t["home_l"]}</a></li><li><a href="{u("games", lang)}">{t["games"]}</a></li>
    <li><a href="{u("starjars", lang)}">{t["starjars"]}</a></li><li><a href="{u("about", lang)}">{t["about"]}</a></li></ul></div>
  <div><h2>{t["help"]}</h2><ul>
    <li><a href="{u("support", lang)}">{t["support"]}</a></li><li><a href="{u("delete", lang)}">{t["delete"]}</a></li>
    <li><a href="mailto:{MAIL}">{MAIL}</a></li></ul></div>
  <div><h2>{t["legal"]}</h2><ul>
    <li><a href="{u("privacy", lang)}">{t["privacy"]}</a></li><li><a href="{u("terms", lang)}">{t["terms"]}</a></li>
    <li><a href="{other_href}" lang="{t["other_lang"]}" hreflang="{t["other_lang"]}">{t["other"]}</a></li></ul></div>
</div></footer>'''


def write(path, html):
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def page(lang, key, title, description, body, own_path=None, other_href=None):
    path = own_path.lstrip("/") if own_path else PAGES[key][lang]
    other_href = other_href or (u(key, "en" if lang == "tr" else "tr") if key else "/en/")
    html = f'''{head(lang, title, description, key, "/site.css", own_path)}
<body>
{header(lang, key, other_href)}
<main id="main"><div class="wrap">
{body}
</div></main>
{footer(lang, other_href)}
</body>
</html>
'''
    write(path, html)


def doc(lang, title, metas, intro, sections, summary=None, toc=True):
    """A long text page: title, dates, an optional summary box, numbered-free sections with a contents list."""
    meta = '<div class="metas">' + "".join(f'<p class="meta">{m}</p>' for m in metas) + "</div>"
    box = f'<section class="summary" aria-labelledby="summary"><h2 id="summary">{summary[0]}</h2><ul>{"".join(f"<li>{x}</li>" for x in summary[1])}</ul></section>' if summary else ""
    body = "".join(f'<section aria-labelledby="{sid}"><h2 id="{sid}">{stitle}</h2>{shtml}</section>' for sid, stitle, shtml in sections)
    if not toc:
        return f'<div class="doc single"><article class="prose"><h1>{title}</h1>{meta}{intro}{box}{body}</article></div>'
    links = "".join(f'<li><a href="#{sid}">{stitle}</a></li>' for sid, stitle, _ in sections)
    c = T[lang]["contents"]
    # Desktop: an open, sticky list beside the text. Phone: the title first, then the same list folded.
    return (f'<div class="doc"><div class="doc-head prose"><h1>{title}</h1>{meta}</div>'
            f'<nav class="toc" aria-label="{c}"><p class="toc-title">{c}</p><ol>{links}</ol></nav>'
            f'<details class="toc-fold"><summary>{c}</summary><ol>{links}</ol></details>'
            f'<article class="prose doc-body">{intro}{box}{body}</article></div>')


def table(caption, heads, rows):
    th = "".join(f'<th scope="col">{h}</th>' for h in heads)
    trs = "".join("<tr>" + f'<th scope="row">{r[0]}</th>' + "".join(f'<td data-label="{heads[i + 1]}">{c}</td>' for i, c in enumerate(r[1:])) + "</tr>" for r in rows)
    return f'<table class="table"><caption>{caption}</caption><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>'


# ---------------------------------------------------------------- home

VALUES = {
    "tr": [("circle", "cobalt", "Sakin ve tatmin edici", "Kısa oturumlarda açılıp kapanan, insanı rahatlatan bulmacalar tasarlıyoruz. Her hamlenin görünür bir sonucu, her bölümün güzel bir bitişi var."),
           ("triangle", "olive", "Kendi çizimimiz, kendi sesimiz", "Oyunlarımızın görsellerini, animasyonlarını ve ses efektlerini kendimiz yapıyoruz. Hazır görsel paketi kullanmıyoruz."),
           ("diamond", "lemon", "Adil para kazanma", "Oyunlarımız ücretsiz. Ödüllü reklamı izlemek senin seçimin, banner reklam yok; mağazadaki her paketin ne verdiği açıkça yazar."),
           ("ring", "sky", "Gizliliğe saygı", "Oynamak için adını, e-postanı ya da telefon numaranı istemiyoruz. Neyi neden işlediğimizi gizlilik politikasında açıkça yazıyoruz.")],
    "en": [("circle", "cobalt", "Calm and satisfying", "We design relaxing puzzles that fit into short sessions. Every move has a visible result, and every chapter a good ending."),
           ("triangle", "olive", "Our own art and sound", "We make our games' visuals, animation and sound effects ourselves. We don't use ready-made art packs."),
           ("diamond", "lemon", "Fair monetisation", "Our games are free. Watching a rewarded ad is your choice, there are no banner ads, and every shop pack says plainly what it gives."),
           ("ring", "sky", "Respect for privacy", "We never ask for your name, email or phone number to play. We say plainly what we process and why in our privacy policy.")],
}


def values(lang):
    return "".join(f'<li>{piece_icon(k, c)}<div><h3>{h}</h3><p>{p}</p></div></li>' for k, c, h, p in VALUES[lang])


def star_window(lang):
    if lang == "tr":
        return f'''<a class="window" href="{u("starjars", "tr")}">
  {jar("icon", animate=False, label=None)}
  <div>
    <h3>Star Jars Sort Deluxe</h3>
    <p class="alt">Yıldız Kavanozu</p>
    <p>Renkli yıldızları kavanozlara ayırdığın sakin bir bulmaca. Her mühürlenen kavanoz gerçek bir takımyıldızın bir yıldızını yakar.</p>
    <p class="status">Yakında App Store ve Google Play'de. 13 dilde.</p>
    <span class="go">Oyunun sayfası</span>
  </div>
</a>'''
    return f'''<a class="window" href="{u("starjars", "en")}">
  {jar("icon", animate=False, label=None)}
  <div>
    <h3>Star Jars Sort Deluxe</h3>
    <p class="alt">A calm sorting puzzle</p>
    <p>Sort colourful stars into jars. Every sealed jar lights a star of a real constellation.</p>
    <p class="status">Coming soon to the App Store and Google Play. In 13 languages.</p>
    <span class="go">The game's page</span>
  </div>
</a>'''


def next_slot(lang):
    h, p = {"tr": ("Sıradaki oyunlar", "Yeni oyunlar üzerinde çalışıyoruz. Hazır olduklarında burada olacaklar."),
            "en": ("What's next", "More games are in development. They'll appear here when they're ready.")}[lang]
    return f'<div class="next">{empty_slot()}<h3>{h}</h3><p>{p}</p></div>'


HOME = {
    "tr": f'''<section class="hero" aria-labelledby="hero">
  <div>
    <h1 id="hero">Her şeyin yerine oturduğu oyunlar</h1>
    <p class="lede">Symbol Interactive, Aydın'da kurulmuş bağımsız bir mobil oyun stüdyosu. Sakin, özenli ve oynaması keyifli bulmaca oyunları yapıyoruz.</p>
    <div class="actions"><a class="button" href="{u("games", "tr")}">Oyunlarımız</a><a class="button quiet" href="mailto:{MAIL}">Bize yaz</a></div>
  </div>
  {board("Dört sıra oyun taşı: daireler, karolar, üçgenler ve halkalar yerlerine oturmuş")}
</section>
<section class="section" aria-labelledby="games">
  <h2 id="games">Oyunlarımız</h2>
  <p>Telefonda birkaç dakikada açılan, uzun süre akılda kalan oyunlar.</p>
  <div class="games">{star_window("tr")}{next_slot("tr")}</div>
</section>
<section class="section" aria-labelledby="values">
  <h2 id="values">Nasıl oyun yapıyoruz</h2>
  <p>Küçük bir stüdyoyuz; bu yüzden her oyunu uzun süre parlatıp öyle yayımlıyoruz.</p>
  <ul class="values">{values("tr")}</ul>
</section>
<section class="section studio" aria-labelledby="studio">
  <div>
    <h2 id="studio">Stüdyo</h2>
    <p>Symbol Interactive'i 2026'da Aydın'da Cem Tezgelen kurdu. Oyunlarımızı tasarlıyor, yazıyor, çiziyor ve yayımlıyoruz; büyük bir ekip değiliz, oyunun her ayrıntısına dokunuyoruz.</p>
    <p><a href="{u("about", "tr")}">Stüdyoyu tanı</a></p>
  </div>
  <div class="contact">
    <h3>Bize yaz</h3>
    <p>Oyunlarla ilgili bir soru, bir öneri ya da bir iş birliği fikri için:</p>
    <p class="mail"><a href="mailto:{MAIL}">{MAIL}</a></p>
  </div>
</section>''',
    "en": f'''<section class="hero" aria-labelledby="hero">
  <div>
    <h1 id="hero">Games where everything falls into place</h1>
    <p class="lede">Symbol Interactive is an independent mobile game studio founded in Aydın, Türkiye. We make calm, carefully made puzzle games that are a pleasure to play.</p>
    <div class="actions"><a class="button" href="{u("games", "en")}">Our games</a><a class="button quiet" href="mailto:{MAIL}">Write to us</a></div>
  </div>
  {board("Four rows of game pieces, circles, diamonds, triangles and rings, all in place")}
</section>
<section class="section" aria-labelledby="games">
  <h2 id="games">Our games</h2>
  <p>Games that open in a few minutes on your phone and stay with you much longer.</p>
  <div class="games">{star_window("en")}{next_slot("en")}</div>
</section>
<section class="section" aria-labelledby="values">
  <h2 id="values">How we make games</h2>
  <p>We are a small studio, so we polish each game for a long time before we release it.</p>
  <ul class="values">{values("en")}</ul>
</section>
<section class="section studio" aria-labelledby="studio">
  <div>
    <h2 id="studio">The studio</h2>
    <p>Cem Tezgelen founded Symbol Interactive in Aydın in 2026. We design, write, draw and publish our games ourselves; we are not a big team, and we touch every detail of every game.</p>
    <p><a href="{u("about", "en")}">About the studio</a></p>
  </div>
  <div class="contact">
    <h3>Write to us</h3>
    <p>For a question about our games, an idea, or a partnership:</p>
    <p class="mail"><a href="mailto:{MAIL}">{MAIL}</a></p>
  </div>
</section>''',
}

# ---------------------------------------------------------------- games

GAMES = {
    "tr": f'''<h1>Oyunlar</h1>
<p class="lede">Şu an yayına hazırlanan bir oyunumuz var; yenileri üzerinde çalışıyoruz.</p>
<section class="feature" aria-labelledby="sj">
  <div>
    <div class="games" style="grid-template-columns:1fr;margin-top:0">{star_window("tr").replace("<h3>", '<h3 id="sj">', 1)}</div>
  </div>
  <div>
    <dl class="facts">
      <dt>Tür</dt><dd>Sıralama bulmacası</dd>
      <dt>Platformlar</dt><dd>iOS ve Android</dd>
      <dt>Diller</dt><dd>13 dil</dd>
      <dt>Hedef kitle</dt><dd>13 yaş ve üzeri</dd>
      <dt>Durum</dt><dd>Yakında App Store ve Google Play'de</dd>
    </dl>
    <p style="margin-top:1rem"><a href="{u("support", "tr")}">Destek</a>, <a href="{u("privacy", "tr")}">gizlilik politikası</a> ve <a href="{u("delete", "tr")}">hesap silme</a>.</p>
  </div>
</section>
<div class="shots">{shots("tr", SHOT_ALT["tr"])}</div>
<section class="section" aria-labelledby="next"><h2 id="next">Geliştirilen oyunlar</h2>
  <div class="games" style="grid-template-columns:minmax(0,1fr)">{next_slot("tr")}</div>
</section>''',
    "en": f'''<h1>Games</h1>
<p class="lede">One game is getting ready for release; more are in development.</p>
<section class="feature" aria-labelledby="sj">
  <div>
    <div class="games" style="grid-template-columns:1fr;margin-top:0">{star_window("en").replace("<h3>", '<h3 id="sj">', 1)}</div>
  </div>
  <div>
    <dl class="facts">
      <dt>Genre</dt><dd>Sorting puzzle</dd>
      <dt>Platforms</dt><dd>iOS and Android</dd>
      <dt>Languages</dt><dd>13</dd>
      <dt>Audience</dt><dd>Ages 13 and up</dd>
      <dt>Status</dt><dd>Coming soon to the App Store and Google Play</dd>
    </dl>
    <p style="margin-top:1rem"><a href="{u("support", "en")}">Support</a>, <a href="{u("privacy", "en")}">privacy policy</a> and <a href="{u("delete", "en")}">account deletion</a>.</p>
  </div>
</section>
<div class="shots">{shots("en", SHOT_ALT["en"])}</div>
<section class="section" aria-labelledby="next"><h2 id="next">In development</h2>
  <div class="games" style="grid-template-columns:minmax(0,1fr)">{next_slot("en")}</div>
</section>''',
}

# ---------------------------------------------------------------- about

ABOUT = {
    "tr": f'''<div class="studio">
<div class="prose">
<h1>Hakkımızda</h1>
<p class="lede">Symbol Interactive, telefonda birkaç dakikada açılan ama özenle yapılmış, oynayanın kendini iyi hissettiği oyunlar yapan bağımsız bir stüdyo.</p>
<h2>Vizyonumuz</h2>
<p>Mobil oyunların çoğu dikkatini çekmek için bağırıyor. Biz tersini deniyoruz: sakin, anlaşılır, dokununca tatmin eden oyunlar; adil bir ekonomi ve oyuncunun bilgilerine saygı. Büyük bir katalog yerine, her biri uzun süre parlatılmış birkaç oyun.</p>
<h2>Nasıl çalışıyoruz</h2>
<ul class="values" style="grid-template-columns:1fr">{values("tr")}</ul>
<h2>Kim</h2>
<p>Symbol Interactive'i 2026'da Aydın'da Cem Tezgelen kurdu. Symbol Interactive bir şirket unvanı değil; Cem Tezgelen'in oyunlarını yayımladığı addır. Oyunlarımızdaki kişisel verilerin sorumlusu da odur (<a href="{u("privacy", "tr")}">gizlilik politikası</a>).</p>
</div>
<div>
<dl class="facts" style="margin-top:.5rem">
  <dt>Kuruluş</dt><dd>2026</dd>
  <dt>Yer</dt><dd>Aydın, Türkiye</dd>
  <dt>Kurucu</dt><dd>Cem Tezgelen</dd>
  <dt>Oyunlar</dt><dd><a href="{u("starjars", "tr")}">Star Jars Sort Deluxe</a> (iOS, Android); yenileri geliştiriliyor</dd>
  <dt>İletişim</dt><dd><a href="mailto:{MAIL}">{MAIL}</a></dd>
</dl>
</div>
</div>''',
    "en": f'''<div class="studio">
<div class="prose">
<h1>About</h1>
<p class="lede">Symbol Interactive is an independent studio making games that open in a few minutes on your phone, are made with care, and leave you feeling good.</p>
<h2>Our vision</h2>
<p>Most mobile games shout for your attention. We try the opposite: calm, clear games that feel satisfying to touch, a fair economy, and respect for players' information. A few games, each polished for a long time, rather than a big catalogue.</p>
<h2>How we work</h2>
<ul class="values" style="grid-template-columns:1fr">{values("en")}</ul>
<h2>Who</h2>
<p>Cem Tezgelen founded Symbol Interactive in Aydın, Türkiye, in 2026. Symbol Interactive is not a company name but the name under which Cem Tezgelen publishes his games; he is also the controller of the personal data in our games (<a href="{u("privacy", "en")}">privacy policy</a>).</p>
</div>
<div>
<dl class="facts" style="margin-top:.5rem">
  <dt>Founded</dt><dd>2026</dd>
  <dt>Based in</dt><dd>Aydın, Türkiye</dd>
  <dt>Founder</dt><dd>Cem Tezgelen</dd>
  <dt>Games</dt><dd><a href="{u("starjars", "en")}">Star Jars Sort Deluxe</a> (iOS, Android); more in development</dd>
  <dt>Contact</dt><dd><a href="mailto:{MAIL}">{MAIL}</a></dd>
</dl>
</div>
</div>''',
}

# ---------------------------------------------------------------- support

SUPPORT = {
    "tr": f'''<h1>Destek</h1>
<p class="lede">Bir sorun mu var, bir önerin mi? {mailto()} adresine yaz.</p>
<p>Oyunun adını, telefonunun modelini, oyunun Ayarlar ekranında görünen sürüm numarasını ve ne olduğunu kısaca anlatırsan daha çabuk yardım edebiliriz.</p>
<h2>İlerlemem nerede saklanıyor?</h2>
<p>Telefonunda. 1.0.0 sürümünden itibaren ayrıca bulut kaydında: oyun ilk açılışta senin için anonim bir hesap açar ve ilerlemeni ona kaydeder. Ayarlar → Bulut kaydı'ndan Apple ya da Google hesabını bağlarsan ilerlemen yeni telefonuna da gelir. Test sürümlerinde bulut kaydı yoktur; oyunu silersen ilerlemen de silinir.</p>
<h2>Satın aldığım bir şey görünmüyor</h2>
<p>Reklamsız gibi kalıcı satın almalar, aynı App Store ya da Google Play hesabıyla Ayarlar'daki <strong>Satın alımları geri yükle</strong>'ye dokununca geri gelir. Gelmezse bize yaz; satın alma tarihini ve mağazanın gönderdiği makbuzu eklemen yeterli.</p>
<h2>Para iadesi</h2>
<p>Ödemeleri mağazalar alır, iadeyi de onlar yapar: App Store için <a href="https://reportaproblem.apple.com">reportaproblem.apple.com</a>, Google Play için <a href="https://support.google.com/googleplay/answer/2479637">Google Play iade sayfası</a>. Ayrıntılar <a href="{u("terms", "tr")}">kullanım koşullarında</a>.</p>
<h2>Reklam ve gizlilik tercihlerimi değiştirmek istiyorum</h2>
<p>İzin sorulan ülkelerde oyunun Ayarlar ekranındaki <strong>Gizlilik seçenekleri</strong> satırından seçimini istediğin an değiştirebilirsin. iOS'ta Ayarlar → Gizlilik ve Güvenlik → Takip'ten, Android'de telefon ayarlarının reklamlar bölümünden de reklam izinlerini yönetebilirsin. Ayrıntılar <a href="{u("privacy", "tr")}">gizlilik politikasında</a>.</p>
<h2>Hesabımı ve verilerimi silmek istiyorum</h2>
<p>Hesabını ve bulut kaydını oyunun içinden silebilirsin: Ayarlar → Bulut kaydı → Hesabı sil. Oyunu açamıyorsan bize yaz. Neyin silinip neyin kaldığı <a href="{u("delete", "tr")}">hesap silme sayfasında</a>.</p>
<h2>Bir hata buldum ya da bir önerim var</h2>
<p>Çok iyi! {mailto("Star Jars")} adresine yaz; ekran görüntüsü eklersen daha da iyi.</p>''',
    "en": f'''<h1>Support</h1>
<p class="lede">Something wrong, or an idea to share? Write to {mailto()}.</p>
<p>Telling us the game, your phone model, the version number shown in the game's Settings and what happened helps us help you sooner.</p>
<h2>Where is my progress saved?</h2>
<p>On your phone. From version 1.0.0 also in your cloud save: on first launch the game creates an anonymous account for you and saves your progress to it. Link your Apple or Google account in Settings → Cloud save, and your progress comes with you to a new phone. Test versions have no cloud save; deleting the game deletes your progress.</p>
<h2>Something I bought is missing</h2>
<p>Permanent purchases, such as Remove Ads, come back when you tap <strong>Restore purchases</strong> in Settings with the same App Store or Google Play account. If one doesn't, write to us with the purchase date and the receipt the store sent you.</p>
<h2>Refunds</h2>
<p>The stores take the payments and handle refunds: <a href="https://reportaproblem.apple.com">reportaproblem.apple.com</a> for the App Store, and <a href="https://support.google.com/googleplay/answer/2479637">Google Play's refund page</a> for Google Play. The details are in the <a href="{u("terms", "en")}">terms of use</a>.</p>
<h2>Changing my ad and privacy choices</h2>
<p>In countries where the game asks for consent, the <strong>Privacy options</strong> row in the game's Settings lets you change your choice at any time. You can also manage ad permissions in iOS Settings → Privacy &amp; Security → Tracking, or in the ads section of your Android phone's settings. The details are in the <a href="{u("privacy", "en")}">privacy policy</a>.</p>
<h2>Deleting my account and data</h2>
<p>You can delete your account and cloud save in the game: Settings → Cloud save → Delete account. If you can't open the game, write to us. What is deleted and what remains is on the <a href="{u("delete", "en")}">account deletion page</a>.</p>
<h2>I found a bug, or I have an idea</h2>
<p>Great! Write to {mailto("Star Jars")}; a screenshot helps a lot.</p>''',
}

# ---------------------------------------------------------------- privacy policy (decisions memo D1–D15)

PRIVACY_SUMMARY = {
    "tr": ("Kısaca", [
        "Oynamak için adını, e-postanı ya da telefon numaranı istemeyiz; oyun senin için anonim bir hesap açar.",
        "İlerlemen telefonunda ve Avrupa'daki (Belçika) bulut kaydında durur. Hesabını istediğin an oyunun içinden silebilirsin.",
        "Türkiye'de, Avrupa Ekonomik Alanı'nda, Birleşik Krallık'ta ve İsviçre'de analitik ve kişiselleştirilmiş reklam yalnızca izin verirsen çalışır.",
        "16 yaşından küçüksen (Türkiye'de 18) izin sorulmaz; analitik ve kişiselleştirilmiş reklam kapalı kalır.",
        "Satın almaları Apple ve Google yönetir; kart bilgilerini hiç görmeyiz. Bilgilerini para karşılığında satmayız.",
        "1.0.0'dan önceki test sürümleri hiçbir kişisel veri toplamaz."]),
    "en": ("In short", [
        "We never ask for your name, email or phone number to play; the game creates an anonymous account for you.",
        "Your progress is kept on your phone and in a cloud save in Europe (Belgium). You can delete your account in the game at any time.",
        "In Türkiye, the European Economic Area, the UK and Switzerland, analytics and personalised ads run only if you allow them.",
        "If you are under 16 (under 18 in Türkiye), you are not asked for consent; analytics and personalised ads stay off.",
        "Apple and Google handle purchases; we never see your card details. We don't sell your information for money.",
        "Test versions before 1.0.0 collect no personal data."]),
}

PRIVACY = {
    "tr": [
        ("kapsam", "Bu politika neyi kapsar", f'''
<p>Bu politika, Symbol Interactive'in mobil oyunu <strong>Star Jars Sort Deluxe</strong>'ı (Türkçede Yıldız Kavanozu) iOS ve Android'de <strong>1.0.0 sürümünden itibaren</strong> kapsar: hangi bilgileri neden işlediğimizi, kimlerin aldığını, ne kadar saklandığını ve haklarını anlatır. 6698 sayılı Kişisel Verilerin Korunması Kanunu (KVKK) kapsamındaki aydınlatma metnimiz ve Avrupa'daki oyuncular için GDPR'ın istediği bilgilendirme budur. Yeni bir oyun yayımladığımızda onun bilgilerini de bu sayfaya ekleriz.</p>
<p><strong>Test sürümleri.</strong> 1.0.0'dan önceki test sürümleri (şu an TestFlight'ta ve Google Play testinde olan 0.56.0 gibi) analitik, reklam, hesap ya da bulut kaydı içermez ve bizim için hiçbir kişisel veri toplamaz; ilerleme yalnızca telefonda kalır. Bir teste katılırsan seni davet etmek için e-posta adresini kullanırız. Apple ve Google, TestFlight ya da Google Play üzerinden gönderdiğin geri bildirimleri ve test sürümünün çökme raporlarını bize iletebilir; bunları yalnızca hataları düzeltmek için kullanırız.</p>
<p><strong>Bu site.</strong> symbolinteractive.com.tr çerez kullanmaz, ziyaretçileri izlemez ve başka sitelerden yazı tipi ya da betik yüklemez. Site GitHub Pages'te barındırılır; GitHub, sayfaları sunarken IP adresini kendi kayıtlarında işleyebilir (<a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub Gizlilik Bildirimi</a>).</p>'''),
        ("sorumlu", "Veri sorumlusu ve iletişim", f'''
<p>Veri sorumlusu <strong>{CONTROLLER}</strong>'dir: Symbol Interactive adıyla oyun geliştiren bireysel geliştirici, Aydın, Türkiye.</p>
<p>Her soru ve istek için: {mailto()}. Yazılı başvuru yapmak istersen posta adresimizi e-postayla isteyebilirsin.</p>'''),
        ("bilgiler", "Hangi bilgileri, neden işliyoruz", f'''
<p>Bilgiler oyun çalışırken, oyunun ve içindeki hizmet sağlayıcı kütüphanelerinin (SDK) yardımıyla otomatik olarak toplanır; bize e-posta yazarsan e-postayla. Hangi bilginin hangi ülkede hangi izinle işlendiği <a href="#hukuki-sebepler">hukuki sebepler</a> ve <a href="#izinler">izinler</a> bölümlerinde.</p>
<h3>Yaş sorusu</h3>
<p>Oyun ilk açıldığında doğum yılını sorar. Telefonunda yalnızca yaş grubun saklanır (13'ten küçük, 16'dan küçük — Türkiye'de 18'den küçük — ya da daha büyük); doğum yılın da yaş grubun da bize ya da başka birine gönderilmez. Yaş grubun, hangi izinlerin sorulacağını ve hangi özelliklerin kapalı kalacağını belirler (<a href="#cocuklar">çocuklar ve gençler</a>).</p>
<h3>Hesap</h3>
<p>Oyun ilk açıldığında Google Firebase Authentication senin için anonim bir hesap açar. Bu hesabın yalnızca rastgele bir kimlik numarası vardır; Ayarlar → Bulut kaydı'nda <strong>oyuncu kimliği</strong> olarak görünür. iPhone'da Game Center'a, Android'de Google Play Oyunlar'a giriş yapmışsan oyun hesabını ona kendiliğinden bağlar; bunu yapmak için hiçbir pencere açmaz. İstersen hesabını Ayarlar → Bulut kaydı'ndan Apple ile Giriş'e de bağlayabilirsin (iPhone'da ve Android'de; iki telefon arasında ilerlemeni böyle taşırsın). O zaman Firebase, Apple'ın, Game Center'ın ya da Google'ın bu oyun için verdiği hesap ya da oyuncu kimliğini ve sağlayıcının girişle birlikte gönderdiği temel profil bilgilerini (örneğin Google Play Oyunlar'daki oyuncu adını) alır. Bağlarken senden ad ya da e-posta izni istemeyiz. Bunları yalnızca seni tanımak ve ilerlemeni başka bir telefona taşımak için kullanırız. Firebase Authentication, hesapları kötüye kullanıma karşı korumak için IP adreslerini birkaç hafta kayıtlı tutar.</p>
<h3>Bulut kaydı</h3>
<p>İlerlemeni kaybetmemen ve yeni bir telefona taşıyabilmen için kaydın, hesabına bağlı olarak Google Cloud Firestore'da, Avrupa Birliği'ndeki europe-west1 bölgesinde (Belçika) saklanır. Kayıtta oyun ilerlemen (seviyeler, yıldızlar, yıldız tozu ve öğelerin), bir ilerleme özeti (seviye, yıldız ve toz sayısı), cihazının türü (iPhone, iPad ya da Android), oyunun sürümü ve kaydın zamanları bulunur. Ayarların, verdiğin izinler ve mağaza kayıtları telefonunda kalır, buluta gitmez. Bu kaydı yalnızca senin hesabın okuyup yazabilir. İlerlemenin bir kopyası telefonunda da durur.</p>
<h3>Satın almalar</h3>
<p>Ödemeyi App Store ya da Google Play alır; kart bilgilerini hiç görmeyiz. Mağazadan yalnızca satın alma makbuzunu (hangi ürün, işlem numarası, zaman) alırız; öğeyi vermek ve gerektiğinde geri yüklemek için makbuzu telefonunda doğrularız. Analitik açıksa satın almanın tutarı ve para birimi, gelir raporlarımız için Firebase Analytics'e de gider.</p>
<h3>Reklamlar</h3>
<p>Oyun, Unity LevelPlay aracılığıyla ironSource Ads, Unity Ads ve Google AdMob reklamları gösterir: bir ödül için izlemeyi kendin seçtiğin ödüllü reklamlar ve bazı galibiyetlerden sonra iki seviye arasında çıkan geçiş reklamları. Banner reklam yoktur. Bu servisler reklamları seçmek, göstermek, saymak ve dolandırıcılığı önlemek için IP adresini ve ona dayanan yaklaşık konumunu, cihaz bilgilerini (model, işletim sistemi, dil gibi), reklamlarla etkileşimini ve izin verdiysen reklam kimliğini (Android'de reklam kimliği; iOS'ta IDFA, yalnızca uygulama takibine izin verirsen) işler. Kişiselleştirilmiş reklamda reklam ortakları, ilgi alanlarını tahmin etmek için bu bilgileri başka uygulama ve sitelerden gelen bilgilerle birleştirebilir; kişiselleştirilmiş reklam olmadan reklamlar ilgi alanlarına göre seçilmez. Oyun hesabını ya da oyuncu kimliğini reklam ortaklarına vermeyiz. <strong>Reklamsız</strong> satın alımı geçiş reklamlarını kapatır; ödüllü reklamlar, istediğinde izleyebilmen için kalır. Analitik açıksa reklam gösterimlerinin gelirini (reklam ağı, reklam türü, tutar) Firebase Analytics'te ölçeriz.</p>
<h3>Analitik</h3>
<p>Oyunu geliştirmek ve zorluğunu dengelemek için Google Firebase Analytics kullanırız. Analytics; oyundaki etkileşimlerini (açılan ekranlar, başlanan, kazanılan ve kaybedilen seviyeler, oturum süresi, satın almalar, izlenen reklamlar), cihaz ve uygulama bilgilerini (model, işletim sistemi, uygulama sürümü, dil), oyunun bu telefondaki kopyasına özgü bir kimliği ve IP adresinden çıkarılan yaklaşık konumu (ülke ve şehir düzeyinde) işler. Analytics reklam kimliğini toplamaz; bu bilgiler oyun hesabına, adına ya da e-postana bağlanmaz. Türkiye'de, Avrupa Ekonomik Alanı'nda (AEA), Birleşik Krallık'ta ve İsviçre'de Analytics yalnızca izin verirsen çalışır; izin vermezsen hiç veri toplamaz.</p>
<h3>Çökme raporları</h3>
<p>Hataları bulup düzeltmek için Firebase Crashlytics kullanırız. Oyun çöktüğünde ya da bir hata kaydettiğinde Crashlytics; hata kaydını, teşhis bilgilerini (cihaz modeli, işletim sistemi ve uygulama sürümü, bellek durumu, zaman) ve rastgele bir kurulum kimliğini alır. AEA'da, Birleşik Krallık'ta ve İsviçre'de çökme raporları yalnızca izin verirsen gönderilir.</p>
<h3>Uzaktan ayarlar</h3>
<p>Firebase Remote Config ile oyunun bazı ayarlarını (örneğin geçiş reklamlarının sıklığını) güncelleme yayınlamadan değiştiririz. Ayarlar herkes için aynıdır, kişiye göre seçilmez. Bunun için Firebase, oyunun bu kurulumuna özgü bir kimlik (Firebase kurulum kimliği) kullanır.</p>
<h3>İzin tercihlerin</h3>
<p>Verdiğin ya da vermediğin izinler telefonunda saklanır; böylece her açılışta yeniden sorulmaz ve reklam ortaklarına iletilebilir.</p>
<h3>Destek yazışmaları</h3>
<p>Bize e-posta yazarsan, adresini ve mesajını yalnızca cevap vermek ve isteğini yerine getirmek için kullanırız.</p>'''),
        ("hukuki-sebepler", "Hangi hukuki sebeple", table("Her amacın hukuki sebebi", ["Amaç", "KVKK", "GDPR (AEA, Birleşik Krallık, İsviçre)"], [
            ("Hesap, bulut kaydı, satın almalar ve geri yükleme", "Sözleşmenin kurulması ve ifası (m. 5/2-c)", "Sözleşme (m. 6/1-b)"),
            ("Destek yazışmaları ve hak başvuruları", "Sözleşmenin ifası; hukuki yükümlülük (m. 5/2-c, ç)", "Sözleşme; hukuki yükümlülük (m. 6/1-b, c)"),
            ("Analitik", "Açık rıza (m. 5/1)", "Rıza (m. 6/1-a)"),
            ("Kişiselleştirilmiş reklam", "Açık rıza (m. 5/1)", "Rıza (m. 6/1-a), Google'ın rıza mesajıyla"),
            ("Reklamların gösterilmesi, sayılması, dolandırıcılığın önlenmesi", "Meşru menfaat (m. 5/2-f)", "Meşru menfaat (m. 6/1-f); telefona bilgi yazılması ve okunması rıza mesajındaki seçimine göre"),
            ("Çökme raporları", "Meşru menfaat (m. 5/2-f)", "Rıza (m. 6/1-a)"),
            ("Uzaktan ayarlar", "Meşru menfaat (m. 5/2-f)", "Meşru menfaat (m. 6/1-f)"),
            ("Yetkili makamların yasal talepleri", "Kanunlarda öngörülme; hukuki yükümlülük (m. 5/2-a, ç)", "Hukuki yükümlülük (m. 6/1-c)"),
        ]) + '''
<p>Meşru menfaatimiz, oyunu çalışır, güvenli, dengeli ve ücretsiz tutmaktır. Bu işlemeye itiraz edebilirsin.</p>
<p><strong>Diğer ülkelerde</strong> analitik ve çökme raporları meşru menfaatimize dayanır; kişiselleştirilmiş reklam, telefonunun ayarlarına (iOS'ta takip izni, Android'de reklam kimliği) ve ülkenin yasasının tanıdığı vazgeçme haklarına göre çalışır.</p>
<p><strong>Zorunlu olan ve olmayan.</strong> Hesap kimliği ve bulut kaydı hizmetin parçasıdır; onlar olmadan bulut kaydı çalışmaz. Analitik, izin sorulan yerlerde çökme raporları ve kişiselleştirilmiş reklam isteğe bağlıdır; reddetmen oyunu oynamanı engellemez.</p>
<p><strong>Otomatik kararlar.</strong> Hakkında hukuki ya da benzer önemde sonuç doğuran, yalnızca otomatik işlemeye dayanan bir karar vermeyiz. Kişiselleştirilmiş reklama izin verdiysen reklam ortakları ilgi alanlarını tahmin etmek için profil oluşturur.</p>'''),
        ("izinler", "İzinleri nerede ve nasıl soruyoruz", f'''
<ul>
<li><strong>Türkiye:</strong> oyun, ilk açılışta kendi izin kartında iki ayrı soru sorar: analitik ve kişiselleştirilmiş reklam. İkisi de kapalı başlar.</li>
<li><strong>AEA, Birleşik Krallık ve İsviçre:</strong> Google'ın rıza mesajı reklam ortaklarını ve reklam kişiselleştirmesini sorar; oyunun izin kartı analitiği ve çökme raporlarını sorar.</li>
<li><strong>ABD'nin gizlilik yasası olan eyaletleri:</strong> Google'ın eyalet mesajıyla, bilgilerinin kişiselleştirilmiş reklam için kullanılmasını (yasanın deyişiyle "satılmasını" ya da "paylaşılmasını") reddedebilirsin.</li>
<li><strong>iOS:</strong> reklam kimliği (IDFA) yalnızca Apple'ın uygulama takibi sorusuna izin verirsen kullanılır. Kişiselleştirilmiş reklamı reddettiysen ya da yaşın küçükse bu soru hiç sorulmaz.</li>
<li><strong>16 yaşından küçükler (Türkiye'de 18):</strong> izin sorulmaz; analitik ve kişiselleştirilmiş reklam kapalı kalır.</li>
</ul>
<p>Seçimini istediğin an değiştirebilirsin: izin sorulan her yerde oyunun Ayarlar ekranında <strong>Gizlilik seçenekleri</strong> satırı bulunur. Her ülkede telefonunun ayarlarını da kullanabilirsin: iOS'ta Ayarlar → Gizlilik ve Güvenlik → Takip'ten oyunun takip iznini kapatabilir, Android'de telefon ayarlarının reklamlar bölümünden reklam kimliğini silebilir ya da sıfırlayabilirsin. İznini geri alman, o ana kadar yapılan işlemeyi etkilemez.</p>'''),
        ("alicilar", "Kimler alır", '''
<p>Bilgilerini kimseye para karşılığında satmayız. Yukarıdaki işler için bilgiler şu şirketlere gider:</p>
<ul>
<li><strong>Google</strong> (Google LLC ve bağlı şirketleri). Firebase Authentication, Cloud Firestore, Crashlytics, Remote Config ve Analytics'te Google, bilgileri bizim adımıza ve talimatımızla işleyen <strong>veri işleyendir</strong>. AdMob'da ve Google Play'de Google, bilgileri kendi amaçları için de kullanan ayrı bir <strong>veri sorumlusudur</strong>. <a href="https://policies.google.com/privacy">Google Gizlilik Politikası</a>, <a href="https://firebase.google.com/support/privacy">Firebase'de gizlilik</a>, <a href="https://policies.google.com/technologies/partner-sites">Google'ın, hizmetlerini kullanan uygulamalardan gelen bilgileri nasıl kullandığı</a>.</li>
<li><strong>Unity</strong> (Unity Technologies ve bağlı şirketleri; ironSource bir Unity şirketidir): LevelPlay, Unity Ads ve ironSource Ads. Unity, reklam verilerinin ayrı bir veri sorumlusudur. <a href="https://unity.com/legal/game-player-and-app-user-privacy-policy">Unity'nin oyuncu ve uygulama kullanıcısı gizlilik politikası</a>.</li>
<li><strong>Apple</strong> (Apple Inc. ve bağlı şirketleri): App Store, satın almalar ve Apple ile Giriş; Apple ayrı bir veri sorumlusudur. <a href="https://www.apple.com/legal/privacy/">Apple Gizlilik Politikası</a>.</li>
</ul>
<p>Bir yasa ya da yetkili bir makamın kararı gerektirirse bilgileri yetkili kurum ve kuruluşlarla da paylaşırız.</p>'''),
        ("yurt-disi", "Yurt dışına aktarım", '''
<p>Bilgilerin Türkiye dışında işlenir: bulut kaydın Avrupa Birliği'nde (Belçika), hesap kaydın (Firebase Authentication) Amerika Birleşik Devletleri'nde; analitik, çökme raporları, uzaktan ayarlar ve reklam verileri Google'ın ve Unity'nin başta ABD olmak üzere çeşitli ülkelerdeki sunucularında. Bu aktarımlar yukarıda yazılan amaçlarla ve yalnızca yukarıdaki şirketlere yapılır. Türkiye'den yurt dışına aktarım KVKK'nın 9. maddesine tabidir.</p>
<p>AEA'daki, Birleşik Krallık'taki ve İsviçre'deki oyuncular için ABD'ye aktarımlar, alıcı sertifikalıysa (Google gibi) AB-ABD Veri Gizliliği Çerçevesi'ne ve onun Birleşik Krallık ve İsviçre uzantılarına, değilse (Unity gibi) Avrupa Komisyonu'nun standart sözleşme hükümlerine dayanır. Bu güvencelerin bir kopyasını bize yazarak isteyebilirsin.</p>'''),
        ("saklama", "Ne kadar saklıyoruz", '''
<ul>
<li><strong>Hesap ve bulut kaydı:</strong> sen silene kadar. Oyun bir hesapla 24 ay boyunca hiç açılmazsa o hesabı ve bulut kaydını biz sileriz.</li>
<li><strong>Hesapların IP kayıtları:</strong> birkaç hafta.</li>
<li><strong>Analitik:</strong> olay verileri 14 ay sonra silinir. Bunlardan üretilen, kimseyi tanıtmayan toplu sayılar (örneğin günlük oyuncu sayısı) daha uzun kalabilir.</li>
<li><strong>Çökme raporları:</strong> 90 gün.</li>
<li><strong>Firebase kurulum kimliği:</strong> 270 gün kullanılmazsa Firebase tarafından silinir.</li>
<li><strong>Silinen veriler:</strong> Google, silinen hesap verilerini canlı ve yedek sistemlerinden en geç 180 gün içinde temizler.</li>
<li><strong>Reklam ortakları:</strong> kendi politikalarındaki sürelerle (bağlantılar yukarıda).</li>
<li><strong>Satın almalar:</strong> aldığın öğeler ilerlemenin parçası olarak yukarıdaki gibi saklanır. Apple ve Google kendi satın alma kayıtlarını kendi politikalarına göre tutar.</li>
<li><strong>Destek yazışmaları:</strong> iş bittikten sonra en geç bir yıl içinde silinir.</li>
<li><strong>Yaş grubu ve izin tercihlerin:</strong> telefonunda, oyunu silene kadar.</li>
</ul>
<p>Süre dolunca bilgiler silinir ya da kimseyi tanıtmayacak biçimde anonim hâle getirilir.</p>'''),
        ("haklar", "Hakların", f'''
<p>KVKK'nın 11. maddesine göre şu hakların var: kişisel verilerinin işlenip işlenmediğini öğrenme; işlendiyse bilgi isteme; işleme amacını ve amaca uygun kullanılıp kullanılmadığını öğrenme; yurt içinde ya da yurt dışında kimlere aktarıldığını bilme; eksik ya da yanlışsa düzeltilmesini isteme; kanundaki şartlar varsa silinmesini ya da yok edilmesini isteme; düzeltme ve silme işlemlerinin bilgilerin aktarıldığı kişilere bildirilmesini isteme; yalnızca otomatik sistemlerle yapılan bir analizin aleyhine bir sonuç doğurmasına itiraz etme ve kanuna aykırı işleme yüzünden zarara uğradıysan zararının giderilmesini isteme.</p>
<p>AEA'da, Birleşik Krallık'ta ya da İsviçre'deysen GDPR ve benzeri yasalara göre bilgilerine erişme, düzeltilmesini ya da silinmesini isteme, işlemenin kısıtlanmasını isteme, bilgilerini taşınabilir bir biçimde alma, meşru menfaate dayanan işlemeye itiraz etme ve verdiğin rızayı istediğin an geri alma hakların da var. Yaşadığın ülkenin yasası sana başka haklar da tanıyorsa (örneğin Brezilya'da LGPD), onları da aynı yoldan kullanabilirsin.</p>
<h3>Nasıl başvurursun</h3>
<ul>
<li><strong>Oyunun içinden:</strong> hesabını ve bulut kaydını Ayarlar → Bulut kaydı → Hesabı sil ile kendin silebilirsin.</li>
<li><strong>E-postayla:</strong> {mailto()} adresine yaz ve oyunun Ayarlar ekranında görünen oyuncu kimliğini ekle; bilgilerini bu kimlikle buluruz.</li>
<li><strong>Yazılı olarak:</strong> posta adresimizi e-postayla isteyebilirsin.</li>
</ul>
<p>Başvurunu en geç 30 gün içinde, ücretsiz ve yazılı olarak (e-postayla) cevaplarız. Kimliğinden emin olmamız gerekirse ek bilgi isteyebiliriz.</p>
<p><strong>Şikâyet.</strong> Başvurun reddedilirse, cevabımızı yetersiz bulursan ya da süresinde cevap vermezsek, cevabı öğrendiğin tarihten itibaren 30 gün ve her hâlde başvuru tarihinden itibaren 60 gün içinde <a href="https://www.kvkk.gov.tr">Kişisel Verileri Koruma Kurulu</a>'na şikâyette bulunabilirsin. Avrupa'daysan yaşadığın ülkenin veri koruma otoritesine şikâyette bulunabilirsin.</p>'''),
        ("abd", "ABD'deki oyuncular", '''
<p>Bilgilerini para karşılığında satmayız. Ancak ABD'nin bazı eyalet yasaları (Kaliforniya'nın CCPA'sı gibi), reklam ortaklarının kişiselleştirilmiş reklam için tanımlayıcıları almasını "satış" ya da "paylaşım" sayar. Bu yasal anlamda, kişiselleştirilmiş reklam için Unity'ye ve Google'a şu kategorilerdeki bilgileri "satmış" ya da "paylaşmış" sayılabiliriz: tanımlayıcılar (reklam kimliği, IP adresi), uygulama içi etkinlik (reklamlarla etkileşim) ve yaklaşık konum. Bunu oyunun Ayarlar → Gizlilik seçenekleri satırından ya da telefonunun reklam ayarlarından reddedebilirsin.</p>
<p>Topladığımız bilgi kategorileri, kaynakları (sen ve telefonun), amaçları ve saklama süreleri yukarıdaki bölümlerde. Hassas kişisel bilgi toplamayız. 16 yaşından küçüklerin bilgilerini bilerek satmaz ya da paylaşmayız.</p>
<p>Eyaletinin yasası sana hangi bilgileri topladığımızı öğrenme, düzeltilmesini ya da silinmesini isteme, satışı ve paylaşımı reddetme ve reddedilen bir talebe itiraz etme hakları verebilir. Bunun için bize e-postayla yazman yeterli. Bu haklarını kullandığın için sana farklı davranmayız.</p>'''),
        ("hesap", "Hesabını silmek", f'''
<p>Hesabını ve bulut kaydını oyunun içinden silebilirsin: <strong>Ayarlar → Bulut kaydı → Hesabı sil</strong>. Oyunu açamıyorsan bize e-postayla yazabilirsin. Neyin silinip neyin kaldığı ve ne kadar sürdüğü <a href="{u("delete", "tr")}">hesap silme sayfasında</a>.</p>'''),
        ("cocuklar", "Çocuklar ve gençler", f'''
<p>Oyunlarımız 13 yaş ve üzeri içindir; 13 yaşından küçük çocuklara yönelik değildir. Oyun doğum yılını, gerektiği ilk anda (bir izin sormadan önce) sorar ve buna göre davranır; "Söylemek istemiyorum" diyen küçük sayılır:</p>
<ul>
<li><strong>16 yaşından küçüksen (Türkiye'de 18):</strong> izin sorulmaz; analitik ve kişiselleştirilmiş reklam kapalı kalır, iOS'ta takip sorusu gösterilmez. AEA'da, Birleşik Krallık'ta ve İsviçre'de çökme raporları da gönderilmez. Reklamlar ilgi alanlarına göre seçilmez.</li>
<li><strong>13 yaşından küçüksen:</strong> bunlara ek olarak reklam ortaklarına seni çocuk olarak işlemeleri bildirilir ve hesap bağlama (Game Center, Apple ya da Google) yapılmaz.</li>
</ul>
<p>13 yaşından küçük bir çocuğun bilgilerinin bize ulaştığını düşünüyorsan {mailto()} adresine yaz; bilgileri sileriz.</p>'''),
        ("guvenlik", "Güvenlik", '''
<p>Bilgiler telefonunla sunucular arasında şifreli bağlantıyla (HTTPS/TLS) gider. Bulut kaydını yalnızca senin hesabın okuyup yazabilir. Kart bilgilerini hiç görmeyiz. Bir veri ihlali olursa yasaların istediği şekilde Kurul'a ve gerekirse sana haber veririz.</p>'''),
        ("degisiklikler", "Değişiklikler", '''
<p>Bu politikayı değiştirirsek güncel hâlini bu sayfada, yeni tarihiyle yayınlarız. Yeni bir amaç izin gerektiriyorsa iznini yeniden sorarız.</p>'''),
    ],
    "en": [
        ("scope", "What this policy covers", f'''
<p>This policy covers Symbol Interactive's mobile game <strong>Star Jars Sort Deluxe</strong> (Yıldız Kavanozu in Turkish) on iOS and Android <strong>from version 1.0.0</strong>: what information it processes and why, who receives it, how long it is kept and what your rights are. It is our privacy notice under Türkiye's Personal Data Protection Law No. 6698 (KVKK) and the information the GDPR requires for players in Europe. When we release a new game, we add its details to this page.</p>
<p><strong>Test versions.</strong> Test versions before 1.0.0 (such as 0.56.0, now in TestFlight and Google Play testing) have no analytics, ads, account or cloud save and collect no personal data for us; progress stays on the phone. If you join a test, we use your email address to invite you. Apple and Google may pass on feedback you send through TestFlight or Google Play and crash reports from test versions; we use them only to fix bugs.</p>
<p><strong>This website.</strong> symbolinteractive.com.tr uses no cookies, does not track visitors and loads no fonts or scripts from other sites. It is hosted on GitHub Pages; GitHub may process your IP address in its own logs when serving the pages (<a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub Privacy Statement</a>).</p>'''),
        ("controller", "Data controller and contact", f'''
<p>The data controller is <strong>{CONTROLLER}</strong>, an individual developer making games as Symbol Interactive, Aydın, Türkiye.</p>
<p>For any question or request: {mailto()}. If you want to apply in writing by post, ask us for our postal address by email.</p>'''),
        ("information", "What information we process, and why", f'''
<p>Information is collected automatically while the game runs, through the game and the service providers' libraries (SDKs) inside it; and by email if you write to us. Which information is processed where and on what basis is in <a href="#legal-bases">legal bases</a> and <a href="#consent">consent</a>.</p>
<h3>Age question</h3>
<p>When the game first opens it asks for your year of birth. Only your age group is kept on your phone (under 13, under 16 — under 18 in Türkiye — or older); neither your year of birth nor your age group is sent to us or anyone else. Your age group decides which permissions are asked and which features stay off (<a href="#children">children and teenagers</a>).</p>
<h3>Account</h3>
<p>When the game first opens, Google Firebase Authentication creates an anonymous account for you. All it has is a random ID, shown in Settings → Cloud save as your <strong>player ID</strong>. If you're signed in to Game Center on iPhone or to Google Play Games on Android, the game links the account to it by itself, without opening any window. If you like, you can also link it to Sign in with Apple in Settings → Cloud save (on iPhone and Android; that's how your progress moves between the two). Firebase then receives the account or player ID that Apple, Game Center or Google gives for this game, and the basic profile details the provider sends with the sign-in (such as your Google Play Games gamer name). We don't ask for your name or email when you link. We use these only to recognise you and to bring your progress to another phone. Firebase Authentication keeps a log of IP addresses for a few weeks to protect accounts from abuse.</p>
<h3>Cloud save</h3>
<p>So that you don't lose your progress and can take it to a new phone, your save is stored with your account in Google Cloud Firestore, in the europe-west1 region (Belgium, in the European Union). It holds your game progress (levels, stars, stardust and your items), a progress summary (level, stars and stardust), your device type (iPhone, iPad or Android), the game's version and when it was saved. Your settings, the permissions you gave and the store's records stay on your phone and never go to the cloud. Only your own account can read or write it. A copy of your progress also stays on your phone.</p>
<h3>Purchases</h3>
<p>The App Store or Google Play takes the payment; we never see your card details. From the store we receive only the purchase receipt (which product, the transaction ID, the time), which we check on your phone to give you the item and to restore it when needed. If analytics is on, the amount and currency of a purchase also go to Firebase Analytics for our revenue reports.</p>
<h3>Ads</h3>
<p>The game shows ads from ironSource Ads, Unity Ads and Google AdMob through Unity LevelPlay: rewarded ads, which you choose to watch for a reward, and interstitial ads, which appear between levels after some wins. There are no banner ads. To choose, show and count ads and to prevent fraud, these services process your IP address and the approximate location it suggests, device information (such as model, operating system and language), how you interact with ads and, if you allow it, your advertising ID (the advertising ID on Android; the IDFA on iOS, only if you allow app tracking). For personalised ads, ad partners may combine this with information from other apps and websites to guess your interests; without personalisation, ads are not chosen by your interests. We never give your game account or player ID to ad partners. The <strong>Remove Ads</strong> purchase turns interstitial ads off; rewarded ads stay, for whenever you want one. If analytics is on, we measure ad revenue (ad network, ad format, amount) in Firebase Analytics.</p>
<h3>Analytics</h3>
<p>To improve the game and balance its difficulty we use Google Firebase Analytics. Analytics processes how you interact with the game (screens opened, levels started, won and lost, session length, purchases, ads watched), device and app information (model, operating system, app version, language), an ID unique to the game's copy on this phone, and the approximate location derived from your IP address (country and city level). Analytics does not collect the advertising ID, and this information is not linked to your game account, name or email. In Türkiye, the European Economic Area (EEA), the UK and Switzerland, Analytics runs only if you allow it; if you don't, it collects nothing.</p>
<h3>Crash reports</h3>
<p>To find and fix bugs we use Firebase Crashlytics. When the game crashes or logs an error, Crashlytics receives the error log, diagnostic information (device model, operating system and app version, memory state, time) and a random installation ID. In the EEA, the UK and Switzerland, crash reports are sent only if you allow it.</p>
<h3>Remote settings</h3>
<p>With Firebase Remote Config we change some of the game's settings (how often interstitial ads appear, for example) without releasing an update. The settings are the same for everyone, not chosen per person. For this, Firebase uses an ID unique to this installation of the game (the Firebase installation ID).</p>
<h3>Your consent choices</h3>
<p>The permissions you give or refuse are stored on your phone, so that you aren't asked at every launch and so that they can be passed on to ad partners.</p>
<h3>Support emails</h3>
<p>If you write to us, we use your address and message only to answer you and carry out your request.</p>'''),
        ("legal-bases", "Legal bases", table("The legal basis for each purpose", ["Purpose", "KVKK", "GDPR (EEA, UK, Switzerland)"], [
            ("Account, cloud save, purchases and restoring them", "Entering into and performing a contract (Art. 5(2)(c))", "Contract (Art. 6(1)(b))"),
            ("Support emails and rights requests", "Performing a contract; legal obligation (Art. 5(2)(c), (ç))", "Contract; legal obligation (Art. 6(1)(b), (c))"),
            ("Analytics", "Explicit consent (Art. 5(1))", "Consent (Art. 6(1)(a))"),
            ("Personalised ads", "Explicit consent (Art. 5(1))", "Consent (Art. 6(1)(a)), through Google's consent message"),
            ("Showing and counting ads, preventing fraud", "Legitimate interests (Art. 5(2)(f))", "Legitimate interests (Art. 6(1)(f)); storing and reading information on the phone follows your choice in the consent message"),
            ("Crash reports", "Legitimate interests (Art. 5(2)(f))", "Consent (Art. 6(1)(a))"),
            ("Remote settings", "Legitimate interests (Art. 5(2)(f))", "Legitimate interests (Art. 6(1)(f))"),
            ("Lawful requests from authorities", "Required by law; legal obligation (Art. 5(2)(a), (ç))", "Legal obligation (Art. 6(1)(c))"),
        ]) + '''
<p>Our legitimate interest is keeping the game working, safe, balanced and free to play. You can object to this processing.</p>
<p><strong>In other countries</strong> analytics and crash reports rely on our legitimate interests; personalised ads follow your phone's settings (app tracking on iOS, the advertising ID on Android) and the opt-out rights your country's law gives you.</p>
<p><strong>What is required and what is not.</strong> The account ID and the cloud save are part of the service; without them the cloud save doesn't work. Analytics, crash reports where we ask, and personalised ads are optional; refusing them doesn't stop you playing.</p>
<p><strong>Automated decisions.</strong> We make no decision based solely on automated processing that has legal or similarly significant effects on you. If you allow personalised ads, ad partners build a profile to guess your interests.</p>'''),
        ("consent", "Where and how we ask for consent", f'''
<ul>
<li><strong>Türkiye:</strong> on first launch the game asks two separate questions on its own consent card: analytics, and personalised ads. Both start off.</li>
<li><strong>EEA, UK and Switzerland:</strong> Google's consent message asks about ad partners and ad personalisation; the game's consent card asks about analytics and crash reports.</li>
<li><strong>US states with privacy laws:</strong> Google's state message lets you opt out of your information being used for personalised ads (a "sale" or "sharing" in those laws' words).</li>
<li><strong>iOS:</strong> the advertising ID (IDFA) is used only if you allow app tracking when Apple's prompt asks. If you refused personalised ads, or you are under age, the prompt is never shown.</li>
<li><strong>Under 16 (under 18 in Türkiye):</strong> no consent is asked; analytics and personalised ads stay off.</li>
</ul>
<p>You can change your choice at any time: wherever the game asks for consent, a <strong>Privacy options</strong> row appears in its Settings. Everywhere, you can also use your phone's settings: on iOS, turn off tracking for the game in Settings → Privacy &amp; Security → Tracking; on Android, delete or reset your advertising ID in the ads section of your phone's settings. Withdrawing consent does not affect processing that took place before.</p>'''),
        ("recipients", "Who receives it", '''
<p>We don't sell your information to anyone for money. For the purposes above, information goes to these companies:</p>
<ul>
<li><strong>Google</strong> (Google LLC and its affiliates). For Firebase Authentication, Cloud Firestore, Crashlytics, Remote Config and Analytics, Google is our <strong>processor</strong>, acting on our behalf and instructions. For AdMob and Google Play, Google is a separate <strong>controller</strong> that also uses information for its own purposes. <a href="https://policies.google.com/privacy">Google Privacy Policy</a>, <a href="https://firebase.google.com/support/privacy">Privacy and security in Firebase</a>, <a href="https://policies.google.com/technologies/partner-sites">How Google uses information from sites or apps that use its services</a>.</li>
<li><strong>Unity</strong> (Unity Technologies and its affiliates; ironSource is a Unity company): LevelPlay, Unity Ads and ironSource Ads. Unity is a separate controller of ad data. <a href="https://unity.com/legal/game-player-and-app-user-privacy-policy">Unity Game Player and App User Privacy Policy</a>.</li>
<li><strong>Apple</strong> (Apple Inc. and its affiliates): the App Store, purchases and Sign in with Apple; Apple is a separate controller. <a href="https://www.apple.com/legal/privacy/">Apple Privacy Policy</a>.</li>
</ul>
<p>If a law or a decision of a competent authority requires it, we also share information with the competent authorities.</p>'''),
        ("transfers", "Transfers abroad", '''
<p>Your information is processed outside Türkiye: your cloud save in the European Union (Belgium), your account record (Firebase Authentication) in the United States, and analytics, crash reports, remote settings and ad data on Google's and Unity's servers in several countries, mainly the United States. These transfers are made for the purposes above and only to the companies above. Transfers from Türkiye are subject to Article 9 of the KVKK.</p>
<p>For players in the EEA, the UK and Switzerland, transfers to the United States rely on the EU-US Data Privacy Framework and its UK and Swiss extensions where the recipient is certified (such as Google), and otherwise on the European Commission's standard contractual clauses (such as Unity). You can ask us for a copy of these safeguards.</p>'''),
        ("retention", "How long we keep it", '''
<ul>
<li><strong>Account and cloud save:</strong> until you delete them. If the game isn't opened with an account for 24 months, we delete that account and its cloud save.</li>
<li><strong>Account IP logs:</strong> a few weeks.</li>
<li><strong>Analytics:</strong> event data is deleted after 14 months. Aggregate figures made from it that identify no one (daily player counts, for example) may be kept longer.</li>
<li><strong>Crash reports:</strong> 90 days.</li>
<li><strong>Firebase installation ID:</strong> deleted by Firebase after 270 days without use.</li>
<li><strong>Deleted data:</strong> Google clears deleted account data from its live and backup systems within 180 days.</li>
<li><strong>Ad partners:</strong> for the periods in their own policies (linked above).</li>
<li><strong>Purchases:</strong> the items you bought are kept as part of your progress, as above. Apple and Google keep their own purchase records under their own policies.</li>
<li><strong>Support emails:</strong> deleted within a year of the matter being closed.</li>
<li><strong>Your age group and consent choices:</strong> on your phone, until you delete the game.</li>
</ul>
<p>When a period ends, the information is deleted or made anonymous so that it identifies no one.</p>'''),
        ("rights", "Your rights", f'''
<p>Under Article 11 of the KVKK you can: learn whether your personal data is processed; if it is, ask for information about it; learn why it is processed and whether it is used for that purpose; know who receives it in Türkiye or abroad; have it corrected if it is incomplete or wrong; have it deleted or destroyed where the law's conditions are met; have corrections and deletions passed on to whoever received it; object to a result against you that comes solely from automated analysis; and claim compensation if unlawful processing has harmed you.</p>
<p>If you are in the EEA, the UK or Switzerland, the GDPR and similar laws also give you the right to access your information, have it corrected or deleted, restrict its processing, receive it in a portable format, object to processing based on legitimate interests and withdraw your consent at any time. If the law where you live gives you other rights (for example the LGPD in Brazil), you can use them the same way.</p>
<h3>How to apply</h3>
<ul>
<li><strong>In the game:</strong> delete your account and cloud save yourself in Settings → Cloud save → Delete account.</li>
<li><strong>By email:</strong> write to {mailto()} with the player ID shown in the game's Settings; we find your information by that ID.</li>
<li><strong>In writing:</strong> ask us for our postal address by email.</li>
</ul>
<p>We answer within 30 days, free of charge, in writing (by email). If we need to be sure who you are, we may ask for more information.</p>
<p><strong>Complaints.</strong> If your application is refused, you find our answer inadequate or we don't answer in time, you can complain to the <a href="https://www.kvkk.gov.tr">Personal Data Protection Board</a> in Türkiye within 30 days of learning our answer, and in any case within 60 days of your application. If you are in Europe, you can complain to the data protection authority of the country you live in.</p>'''),
        ("us", "Players in the United States", '''
<p>We don't sell your information for money. But some US state laws (such as California's CCPA) count ad partners receiving identifiers for personalised advertising as a "sale" or "sharing". In that legal sense, we may "sell" or "share" these categories of information with Unity and Google for personalised ads: identifiers (advertising ID, IP address), in-app activity (how you interact with ads) and approximate location. You can opt out in the game's Settings → Privacy options row, or in your phone's ad settings.</p>
<p>The categories of information we collect, their sources (you and your phone), purposes and retention periods are in the sections above. We collect no sensitive personal information. We do not knowingly sell or share the information of anyone under 16.</p>
<p>Your state's law may give you the right to know what information we collect, to have it corrected or deleted, to opt out of sale and sharing, and to appeal a refused request. Just email us. We won't treat you differently for using these rights.</p>'''),
        ("deleting", "Deleting your account", f'''
<p>You can delete your account and cloud save in the game: <strong>Settings → Cloud save → Delete account</strong>. If you can't open the game, you can email us. What is deleted, what remains and how long it takes is on the <a href="{u("delete", "en")}">account deletion page</a>.</p>'''),
        ("children", "Children and teenagers", f'''
<p>Our games are for ages 13 and up; they are not directed at children under 13. The game asks for your year of birth the first time it needs it (before asking for a permission) and acts on it; "I'd rather not say" counts as under age:</p>
<ul>
<li><strong>Under 16 (under 18 in Türkiye):</strong> no consent is asked; analytics and personalised ads stay off and the iOS tracking prompt is not shown. In the EEA, the UK and Switzerland crash reports are not sent either. Ads are not chosen by your interests.</li>
<li><strong>Under 13:</strong> in addition, ad partners are told to treat you as a child, and no account is linked (Game Center, Apple or Google).</li>
</ul>
<p>If you think a child under 13 has given us information, write to {mailto()} and we will delete it.</p>'''),
        ("security", "Security", '''
<p>Information travels between your phone and the servers over encrypted connections (HTTPS/TLS). Only your own account can read or write your cloud save. We never see your card details. If a data breach happens, we notify the authorities and, where needed, you, as the law requires.</p>'''),
        ("changes", "Changes", '''
<p>If we change this policy, we publish the new version on this page with its new date. If a new purpose needs your consent, we ask for it again.</p>'''),
    ],
}

# ---------------------------------------------------------------- terms of use (memo D16)

TERMS = {
    "tr": [
        ("biz", "Biz kimiz", f'''
<p>Oyunları Symbol Interactive adıyla {CONTROLLER} geliştirir ve yayımlar (bireysel geliştirici, Aydın, Türkiye; {mailto()}). Bu koşullarda "biz" bunu anlatır.</p>
<p>Oyunu App Store'dan indirdiysen Apple'ın standart <a href="https://www.apple.com/legal/internet-services/itunes/dev/stdeula/">Lisanslı Uygulama Son Kullanıcı Lisans Sözleşmesi</a> da geçerlidir; oyunu kullanma lisansı konusunda bu koşullarla farklılık olursa Apple'ın sözleşmesi esas alınır. Google Play'den indirdiysen Google Play'in hizmet şartları da geçerlidir.</p>'''),
        ("yas", "Yaş", '''
<p>Oyunlarımız 13 yaş ve üzeri içindir. 18 yaşından küçüksen satın alma yapmadan önce anne, baba ya da vasinden izin al.</p>'''),
        ("lisans", "Oyunu kullanma hakkın", '''
<p>Sana oyunu kendi cihazlarında, kişisel ve ticari olmayan amaçla oynaman için kişisel, devredilemez ve münhasır olmayan bir kullanım hakkı veriyoruz. Oyunun kodu, çizimleri, animasyonları, sesleri ve metinleri bize ya da lisans verenlerimize aittir. Yasaların açıkça izin verdiği durumlar dışında oyunu kopyalayamaz, değiştiremez, tersine mühendislikle çözemez, kiralayamaz ya da satamazsın.</p>'''),
        ("ogeler", "Oyun içi öğeler", '''
<p>Oyunda yıldız tozu, can, ipucu, ek kavanoz ve geri alma gibi oyun içi para ve öğeler kazanabilir ya da satın alabilirsin. Bunlar yalnızca oyunda kullanılan bir lisanstır:</p>
<ul>
<li>Gerçek para değerleri yoktur; paraya çevrilemez, satılamaz ve başka bir oyuncuya aktarılamaz.</li>
<li>Oyunu dengeli tutmak için öğelerin oyundaki fiyatlarını, miktarlarını ve etkilerini değiştirebiliriz; satın aldığın bir paketin içeriğini sonradan geri alıp azaltmayız.</li>
<li>Reklamsız gibi kalıcı satın almalar mağaza hesabına bağlıdır; aynı App Store ya da Google Play hesabıyla Ayarlar'daki <strong>Satın alımları geri yükle</strong> ile geri gelir.</li>
<li>Diğer öğeler ilerlemenle birlikte saklanır. Bulut kaydı olmadan oyunu silersen ya da telefon değiştirirsen bunlar kaybolabilir; bulut kaydı 1.0.0 sürümüyle gelir.</li>
<li>Hileyle ya da bir hatayı kötüye kullanarak elde edilen öğeleri düzeltebilir ya da kaldırabiliriz.</li>
</ul>'''),
        ("satin-alma", "Satın almalar ve fiyatlar", '''
<p>Satın almaları App Store ya da Google Play üzerinden yaparsın; ödemeyi, vergileri ve makbuzu mağaza yönetir ve satın alma mağazanın koşullarına da tabidir. Fiyatlar mağazada, ülkenin para birimiyle ve vergiler dahil gösterilir; ülkeden ülkeye farklı olabilir. Süreli kampanyalar oyunda gösterilen süre boyunca geçerlidir. Satın aldığın bir şey oyuna gelmezse bize yaz; satın alma tarihini ve mağazanın gönderdiği makbuzu eklemen yeterli.</p>'''),
        ("iade", "İade ve cayma hakkı", '''
<p>Ödemeleri mağazalar aldığı için iadeyi de mağazalar yapar: App Store için <a href="https://reportaproblem.apple.com">reportaproblem.apple.com</a>, Google Play için <a href="https://support.google.com/googleplay/answer/2479637">Google Play iade sayfası</a>.</p>
<p>Türkiye'de tüketiciysen, Mesafeli Sözleşmeler Yönetmeliği'nin 15. maddesine göre elektronik ortamda anında ifa edilen hizmetlerde ve tüketiciye anında teslim edilen gayrimaddi mallarda cayma hakkı yoktur; oyun içi satın almalar ödeme onaylanınca hemen teslim edilir. Avrupa Birliği'nde ve Birleşik Krallık'ta da dijital içeriğin teslimine senin açık onayınla başlandığında cayma hakkı sona erer. Bunlar, hiç teslim edilmeyen ya da hatalı bir ürün için yasal haklarını ve mağazaların kendi iade kurallarını etkilemez.</p>'''),
        ("reklamlar", "Reklamlar", f'''
<p>Oyun ücretsizdir ve reklamlarla desteklenir. Ödüllü reklamları izleyip izlememek senin seçimindir. Bazı galibiyetlerden sonra iki seviye arasında geçiş reklamı çıkabilir. Reklamsız satın alımı geçiş reklamlarını kapatır; ödüllü reklamlar, bir ödül istediğinde izleyebilmen için kalır. Reklamların içeriğini reklam ağları seçer; uygunsuz bir reklam görürsen bize yaz. Reklamlarla ilgili bilgiler <a href="{u("privacy", "tr")}">gizlilik politikasında</a>.</p>'''),
        ("hesap", "Hesap ve bulut kaydı", f'''
<p>1.0.0 sürümünden itibaren oyun senin için anonim bir hesap açar ve ilerlemeni buluta kaydeder. Hesabını Apple ya da Google hesabına bağlarsan, o hesabın güvenliği senin sorumluluğundadır. Hesabını istediğin an oyunun içinden silebilirsin (<a href="{u("delete", "tr")}">hesap silme</a>).</p>'''),
        ("adil", "Adil oyun", '''
<p>Hile yapmak, oyunu değiştiren ya da kendi kendine oynayan araçlar kullanmak, bir hatayı bilerek kötüye kullanmak ve oyunun sunucularına zarar vermeye çalışmak yasaktır. Bunu görürsek ilgili öğeleri düzeltebilir ya da bulut kaydını kapatabiliriz. Bir hata bulursan bize haber vermen bizi çok sevindirir.</p>'''),
        ("degisiklik", "Oyundaki değişiklikler ve oyunun sona ermesi", '''
<p>Oyunu güncelleyerek içerik ekleyebilir, değiştirebilir ya da kaldırabiliriz. Satın alınabilir öğeleri olan bir oyunu tamamen kapatmaya karar verirsek bunu en az 30 gün önceden bu sitede duyururuz.</p>'''),
        ("sorumluluk", "Sorumluluk", '''
<p>Oyunu özenle yapıyoruz ama her cihazda kesintisiz ve hatasız çalışacağını garanti edemeyiz. Kanunun izin verdiği ölçüde, oyunun kullanımından doğan dolaylı zararlardan sorumlu değiliz. Kastımızla ya da ağır ihmalimizle verdiğimiz zararlardan ve tüketici olarak vazgeçilemeyen haklarından doğan sorumluluğumuz saklıdır.</p>'''),
        ("hukuk", "Uygulanacak hukuk ve uyuşmazlıklar", '''
<p>Bu koşullara Türk hukuku uygulanır. Başka bir ülkede tüketiciysen o ülkenin tüketiciyi koruyan zorunlu kuralları da geçerlidir. Bir sorun olursa önce bize yaz; çoğu şeyi birlikte çözebiliriz. Türkiye'de tüketiciysen, 6502 sayılı Tüketicinin Korunması Hakkında Kanun'daki parasal sınırlar içinde tüketici hakem heyetine, bu sınırların üstünde tüketici mahkemesine başvurabilirsin.</p>'''),
        ("gizlilik", "Gizlilik", f'''
<p>Hangi bilgileri neden işlediğimiz <a href="{u("privacy", "tr")}">gizlilik politikasında</a>.</p>'''),
        ("degisiklikler", "Bu koşulların değişmesi", f'''
<p>Bu koşulları değiştirirsek yeni hâlini bu sayfada yeni tarihiyle yayınlarız; değişiklikler yayınlandıkları tarihten sonraki kullanım için geçerlidir. Sorular için: {mailto()}.</p>'''),
    ],
    "en": [
        ("us", "Who we are", f'''
<p>The games are made and published as Symbol Interactive by {CONTROLLER} (an individual developer, Aydın, Türkiye; {mailto()}). "We" in these terms means him.</p>
<p>If you downloaded the game from the App Store, Apple's standard <a href="https://www.apple.com/legal/internet-services/itunes/dev/stdeula/">Licensed Application End User License Agreement</a> also applies; where it and these terms differ about the licence to use the game, Apple's agreement prevails. If you downloaded it from Google Play, Google Play's terms of service also apply.</p>'''),
        ("age", "Age", '''
<p>Our games are for ages 13 and up. If you are under 18, ask a parent or guardian before you buy anything.</p>'''),
        ("licence", "Your right to use the game", '''
<p>We give you a personal, non-transferable, non-exclusive right to play the game on your own devices for personal, non-commercial purposes. The game's code, art, animation, sound and text belong to us or our licensors. Except where the law expressly allows it, you may not copy, modify, reverse-engineer, rent or sell the game.</p>'''),
        ("items", "Virtual items", '''
<p>In the game you can earn or buy virtual currency and items such as stardust, lives, hints, extra jars and undos. They are a licence to use inside the game only:</p>
<ul>
<li>They have no real-money value; they can't be cashed out, sold or transferred to another player.</li>
<li>To keep the game balanced we may change their in-game prices, amounts and effects; we won't take back or reduce what a pack you bought gave you.</li>
<li>Permanent purchases such as Remove Ads belong to your store account; with the same App Store or Google Play account they come back through <strong>Restore purchases</strong> in Settings.</li>
<li>Other items are kept with your progress. Without a cloud save they can be lost if you delete the game or change phones; the cloud save arrives with version 1.0.0.</li>
<li>We may correct or remove items obtained by cheating or by exploiting a bug.</li>
</ul>'''),
        ("purchases", "Purchases and prices", '''
<p>You buy through the App Store or Google Play; the store handles payment, taxes and receipts, and the purchase is also subject to the store's terms. Prices are shown in the store, in your country's currency and including taxes; they can differ between countries. Time-limited offers are valid for the time shown in the game. If something you bought doesn't arrive in the game, write to us with the purchase date and the receipt the store sent you.</p>'''),
        ("refunds", "Refunds and the right of withdrawal", '''
<p>The stores take the payments, so the stores handle refunds: <a href="https://reportaproblem.apple.com">reportaproblem.apple.com</a> for the App Store, and <a href="https://support.google.com/googleplay/answer/2479637">Google Play's refund page</a> for Google Play.</p>
<p>If you are a consumer in Türkiye, under Article 15 of the Distance Contracts Regulation there is no right of withdrawal for services performed instantly online or intangible goods delivered instantly; in-game purchases are delivered as soon as the payment is confirmed. In the European Union and the UK, too, the right of withdrawal ends once delivery of digital content has begun with your express consent. None of this affects your legal rights for a product that is never delivered or is faulty, or the stores' own refund rules.</p>'''),
        ("ads", "Ads", f'''
<p>The game is free and supported by ads. Watching rewarded ads is your choice. After some wins, an interstitial ad may appear between levels. The Remove Ads purchase turns interstitial ads off; rewarded ads stay, for whenever you want a reward. Ad networks choose the ads' content; if you see an inappropriate ad, tell us. How ads use information is in the <a href="{u("privacy", "en")}">privacy policy</a>.</p>'''),
        ("account", "Account and cloud save", f'''
<p>From version 1.0.0 the game creates an anonymous account for you and saves your progress to the cloud. If you link it to an Apple or Google account, keeping that account secure is up to you. You can delete your account in the game at any time (<a href="{u("delete", "en")}">account deletion</a>).</p>'''),
        ("fair-play", "Fair play", '''
<p>Cheating, using tools that modify the game or play it for you, knowingly exploiting a bug, and trying to harm the game's servers are not allowed. If we see this, we may correct the items involved or turn off the cloud save. If you find a bug, telling us makes our day.</p>'''),
        ("ending", "Changes to the game and ending a game", '''
<p>We may add, change or remove content through updates. If we decide to shut down a game that has items for sale, we will announce it on this site at least 30 days in advance.</p>'''),
        ("liability", "Liability", '''
<p>We make the game with care, but we can't promise that it will run without interruption or errors on every device. To the extent the law allows, we are not liable for indirect losses from using the game. Nothing here limits our liability for harm caused intentionally or by gross negligence, or the rights you have as a consumer that cannot be waived.</p>'''),
        ("law", "Governing law and disputes", '''
<p>These terms are governed by Turkish law. If you are a consumer in another country, that country's mandatory consumer protection rules also apply. If there is a problem, write to us first; we can sort most things out together. Consumers in Türkiye can apply to the consumer arbitration committee (tüketici hakem heyeti) within the monetary limits of Consumer Protection Law No. 6502, and to the consumer courts above them.</p>'''),
        ("privacy", "Privacy", f'''
<p>What information we process and why is in the <a href="{u("privacy", "en")}">privacy policy</a>.</p>'''),
        ("changes", "Changes to these terms", f'''
<p>If we change these terms, we publish the new version on this page with its new date; changes apply to use after the date they are published. Questions: {mailto()}.</p>'''),
    ],
}

# ---------------------------------------------------------------- account deletion (memo D14; Google Play's Data safety URL)

DELETE = {
    "tr": [
        ("oyunda", "Oyunun içinden", '''
<ol class="steps">
<li><span>Oyunda <strong>Ayarlar</strong>'ı aç.</span></li>
<li><span><strong>Bulut kaydı</strong> bölümüne dokun.</span></li>
<li><span><strong>Hesabı sil</strong>'e (hesap bağlamadıysan <strong>Bulut kaydını sil</strong>'e) dokun ve <strong>Sil</strong> ile onayla.</span></li>
</ol>
<p>Hesabın ve bulut kaydın o anda silinir; silme bitince oyun bunu sana gösterir. Apple ile Giriş'i bağladıysan ve iPhone'dan siliyorsan Apple'ın oyuna verdiği yetkiyi de geri çekeriz; Android'den sildiysen bu yetkiyi Apple Kimliği ayarlarındaki "Apple ile Giriş" listesinden kaldırabilirsin. Bu telefondaki ilerlemen kalır ve oyun onunla devam eder; bulut kaydı, sen Ayarlar → Bulut kaydı'ndan yeniden açana ya da bir hesap bağlayana kadar kapalı kalır ve buluta hiçbir şey yüklenmez. Bu telefondaki ilerlemeyi de silmek istersen oyunu telefonundan kaldır.</p>'''),
        ("e-posta", "E-postayla", f'''
<p>Oyunu açamıyorsan ya da silmeyi bizim yapmamızı istersen, {mailto("Hesap silme")} adresine konusu <strong>Hesap silme</strong> olan bir e-posta gönder ve oyunun Ayarlar → Bulut kaydı ekranında görünen <strong>oyuncu kimliğini</strong> ekle. Hesabını bu kimlikle bulur, en geç 30 gün içinde siler ve bittiğinde sana e-postayla haber veririz.</p>
<p>Oyunu sildiğin için kimliğini göremiyorsan: hesabını Apple ya da Google ile bağladıysan oyunu yeniden yükleyip aynı hesapla giriş yap; kimliğin Ayarlar'da yine görünür ve silmeyi oradan kendin de yapabilirsin. Hesabını hiç bağlamadıysan, anonim hesap yalnızca o telefondaki oyuna bağlıydı ve hangi hesabın senin olduğunu bilemeyiz; böyle bir hesap 24 ay kullanılmadığında kendiliğinden silinir.</p>'''),
        ("silinenler", "Neler silinir", '''
<ul>
<li><strong>Bulut kaydın:</strong> Cloud Firestore'daki kayıt belgen; içindeki ilerlemen, ilerleme özetin, cihaz türün, oyunun sürümü ve kayıt zamanları.</li>
<li><strong>Firebase hesabın:</strong> anonim hesap kimliğin ve, bağladıysan, Apple ya da Google hesabınla olan bağlantısı.</li>
<li><strong>Apple ile Giriş yetkisi:</strong> bağladıysan ve iPhone'dan siliyorsan, Apple'ın oyuna verdiği yetki geri çekilir.</li>
</ul>
<p>Silinen bulut kaydı geri getirilemez. Reklamsız gibi kalıcı satın almalar mağaza hesabına bağlıdır; aynı App Store ya da Google Play hesabıyla geri yükleyebilirsin.</p>'''),
        ("kalanlar", "Neler kalır ve ne kadar", '''
<ul>
<li><strong>Google'ın yedekleri:</strong> Google, silinen hesap verilerini canlı ve yedek sistemlerinden en geç 180 gün içinde temizler.</li>
<li><strong>Analitik ve çökme verileri:</strong> Firebase Analytics ve Crashlytics'teki kayıtlar oyun hesabına değil, oyunun telefondaki kopyasına özgü kimliklere bağlıdır ve kendiliğinden silinir: Analytics olayları 14 ay, çökme kayıtları 90 gün sonra. Bunlardan üretilmiş, kimseyi tanıtmayan toplu sayılar (örneğin günlük oyuncu sayısı) kalır.</li>
<li><strong>Uzaktan ayarlar için kurulum kimliği:</strong> 270 gün kullanılmazsa Firebase tarafından silinir.</li>
<li><strong>Reklam ortaklarının verileri:</strong> Unity (LevelPlay, Unity Ads, ironSource Ads) ve Google AdMob, reklam için işledikleri bilgileri kendi politikalarına göre saklar ve siler: <a href="https://unity.com/legal/game-player-and-app-user-privacy-policy">Unity</a>, <a href="https://policies.google.com/privacy">Google</a>. Bu bilgiler oyun hesabına bağlı değildir; telefonunun ayarlarından reklam kimliğini silebilir ya da sıfırlayabilirsin.</li>
<li><strong>Mağaza satın alma kayıtları:</strong> Apple ve Google, satın almalarının kayıtlarını kendi politikalarına göre tutar.</li>
<li><strong>Yazışmalar:</strong> silme için bize yazdıysan, yazışmamız iş bittikten sonra en geç bir yıl içinde silinir.</li>
</ul>'''),
        ("sure", "Ne kadar sürer", f'''
<p>Oyunun içinden istediğinde hemen; e-postayla istediğinde en geç 30 gün içinde. Google'ın yedeklerinden temizlenmesi en geç 180 gün sürer.</p>
<p>Bilgilerinin nasıl işlendiği <a href="{u("privacy", "tr")}">gizlilik politikasında</a>. Soruların için: {mailto()}.</p>'''),
    ],
    "en": [
        ("in-game", "In the game", '''
<ol class="steps">
<li><span>Open <strong>Settings</strong> in the game.</span></li>
<li><span>Tap <strong>Cloud save</strong>.</span></li>
<li><span>Tap <strong>Delete account</strong> (or <strong>Delete cloud save</strong> if you never linked an account) and confirm with <strong>Delete</strong>.</span></li>
</ol>
<p>Your account and cloud save are deleted at once, and the game shows you when it's done. If you linked Sign in with Apple and delete on an iPhone, we also revoke the permission Apple gave the game; if you delete on Android, you can remove it from "Sign in with Apple" in your Apple ID settings. The progress on this phone stays and the game carries on with it; the cloud save stays off, and nothing is uploaded, until you turn it back on in Settings → Cloud save or link an account. To remove the progress on this phone too, uninstall the game.</p>'''),
        ("email", "By email", f'''
<p>If you can't open the game, or would rather we did it, email {mailto("Account deletion")} with the subject line <strong>Account deletion</strong> and include the <strong>player ID</strong> shown in the game's Settings → Cloud save. We find your account by that ID, delete it within 30 days and email you when it's done.</p>
<p>If you can't see your ID because you deleted the game: if you linked your account to Apple or Google, install the game again and sign in with the same account; your ID appears in Settings again, and you can delete the account there yourself. If you never linked it, the anonymous account belonged only to the game on that phone and we cannot tell which account is yours; such an account is deleted on its own after 24 months without use.</p>'''),
        ("deleted", "What is deleted", '''
<ul>
<li><strong>Your cloud save:</strong> your save document in Cloud Firestore, with your progress, progress summary, device type, game version and save times.</li>
<li><strong>Your Firebase account:</strong> your anonymous account ID and, if you linked one, its link to your Apple or Google account.</li>
<li><strong>Sign in with Apple permission:</strong> if you linked it and delete on an iPhone, the permission Apple gave the game is revoked.</li>
</ul>
<p>A deleted cloud save cannot be brought back. Permanent purchases such as Remove Ads belong to your store account; you can restore them with the same App Store or Google Play account.</p>'''),
        ("remains", "What remains, and for how long", '''
<ul>
<li><strong>Google's backups:</strong> Google clears deleted account data from its live and backup systems within 180 days.</li>
<li><strong>Analytics and crash data:</strong> records in Firebase Analytics and Crashlytics are tied not to your game account but to IDs unique to the game's copy on your phone, and they are deleted on their own: Analytics events after 14 months, crash logs after 90 days. Aggregate figures made from them that identify no one (daily player counts, for example) remain.</li>
<li><strong>The installation ID for remote settings:</strong> deleted by Firebase after 270 days without use.</li>
<li><strong>Ad partners' data:</strong> Unity (LevelPlay, Unity Ads, ironSource Ads) and Google AdMob keep and delete what they processed for ads under their own policies: <a href="https://unity.com/legal/game-player-and-app-user-privacy-policy">Unity</a>, <a href="https://policies.google.com/privacy">Google</a>. This information is not tied to your game account; you can delete or reset your advertising ID in your phone's settings.</li>
<li><strong>Store purchase records:</strong> Apple and Google keep records of your purchases under their own policies.</li>
<li><strong>Emails:</strong> if you wrote to us to delete your account, the emails we exchanged are deleted within a year of the matter being closed.</li>
</ul>'''),
        ("time", "How long it takes", f'''
<p>In the game, at once; by email, within 30 days. Clearing Google's backups takes up to 180 days.</p>
<p>How your information is processed is in the <a href="{u("privacy", "en")}">privacy policy</a>. Questions: {mailto()}.</p>'''),
    ],
}

DELETE_INTRO = {
    "tr": '<p class="lede">Star Jars Sort Deluxe\'teki hesabını ve bulut kaydını nasıl sileceğin, neyin silinip neyin kaldığı.</p><p>Hesap ve bulut kaydı oyunun 1.0.0 sürümüyle gelir. Daha önceki test sürümlerinde hesap yoktur; ilerlemen yalnızca telefonundadır ve oyunu kaldırınca silinir.</p>',
    "en": '<p class="lede">How to delete your Star Jars Sort Deluxe account and cloud save, and what is deleted and what remains.</p><p>The account and cloud save arrive with version 1.0.0 of the game. Earlier test versions have no account; your progress is only on your phone and goes when you uninstall the game.</p>',
}

# ---------------------------------------------------------------- the game's own page (night sky)

STARJARS = {
    "tr": {"title": "Star Jars Sort Deluxe · Yıldız Kavanozu", "desc": "Star Jars Sort Deluxe (Yıldız Kavanozu): yıldızları ayır, takımyıldızlarını yak. Symbol Interactive'in sakin bulmaca oyunu.",
           "alt": "Yıldız Kavanozu", "studio": "Symbol Interactive", "other": "English",
           "lede": "Renkli yıldızları kavanozlara ayırdığın sakin bir bulmaca. Her mühürlenen kavanoz gerçek bir takımyıldızın bir yıldızını yakar.",
           "status": "Yakında App Store ve Google Play'de.", "inside": "Oyunda neler var",
           "features": [("18 takımyıldızı, 136 seviye", "Gökyüzünü yıldız yıldız yakarak ilerlersin; her bölüm gerçek bir takımyıldızı."),
                        ("Gerçek bilgilerle yıldız kartları", "Yaktığın her yıldızın adı, türü ve bize uzaklığı kartında."),
                        ("Kendi kuralıyla uzay bölümleri", "Bulutsular, kümeler ve gökadalar; her birinin kendi kuralı var."),
                        ("13 dilde", "Türkçe ve İngilizce başta olmak üzere on üç dilde oynanır.")],
           "more": "Yardım ve yasal", "links": [("support", "Destek"), ("privacy", "Gizlilik politikası"), ("terms", "Kullanım koşulları"), ("delete", "Hesap silme")],
           "by": "Bir Symbol Interactive oyunu.", "jar": "Yıldızlarla dolu cam kavanoz", "skip": "İçeriğe geç"},
    "en": {"title": "Star Jars Sort Deluxe", "desc": "Star Jars Sort Deluxe: sort the stars, light up the constellations. A calm puzzle game by Symbol Interactive.",
           "alt": "A calm sorting puzzle", "studio": "Symbol Interactive", "other": "Türkçe",
           "lede": "A calm puzzle where you sort colourful stars into jars. Every sealed jar lights a star of a real constellation.",
           "status": "Coming soon to the App Store and Google Play.", "inside": "What's inside",
           "features": [("18 constellations, 136 levels", "Light up the sky star by star; every chapter is a real constellation."),
                        ("Star cards with real facts", "The name, type and distance of every star you light, on its card."),
                        ("Space chapters with their own rules", "Nebulae, clusters and galaxies, each with a rule of its own."),
                        ("In 13 languages", "Play in English, Turkish and eleven more languages.")],
           "more": "Help and legal", "links": [("support", "Support"), ("privacy", "Privacy policy"), ("terms", "Terms of use"), ("delete", "Delete account")],
           "by": "A Symbol Interactive game.", "jar": "A glass jar full of stars", "skip": "Skip to content"},
}


def starjars_page(lang):
    t = STARJARS[lang]
    other = "en" if lang == "tr" else "tr"
    feats = "".join(f"<li><strong>{h}</strong>{p}</li>" for h, p in t["features"])
    links = "".join(f'<li><a href="{u(k, lang)}">{label}</a></li>' for k, label in t["links"])
    html = f'''{head(lang, t["title"], t["desc"], "starjars", "/starjars.css", favicon="/img/starjars-icon.svg", theme="#1E1452")}
<body>
<a class="skip" href="#main">{t["skip"]}</a>
<header class="top"><div class="wrap">
  <a class="studio-link" href="{u("home", lang)}">{t["studio"]}</a>
  <nav><a class="lang" href="{u("starjars", other)}" lang="{other}" hreflang="{other}">{t["other"]}</a></nav>
</div></header>
<main id="main"><div class="wrap">
<section class="hero" aria-labelledby="title">
  <div>
    <h1 id="title">Star Jars Sort Deluxe</h1>
    <p class="alt">{t["alt"]}</p>
    <p class="lede">{t["lede"]}</p>
    <p class="status">{t["status"]}</p>
  </div>
  {jar(label=t["jar"])}
</section>
<div class="shots">{shots(lang, SHOT_ALT[lang])}</div>
<section aria-labelledby="inside"><h2 id="inside">{t["inside"]}</h2><ul class="features">{feats}</ul></section>
<section aria-labelledby="more"><h2 id="more">{t["more"]}</h2><ul class="links">{links}</ul></section>
</div></main>
<footer class="bottom"><div class="wrap"><p>{t["by"]} <a href="mailto:{MAIL}">{MAIL}</a></p><p>© 2026 Symbol Interactive</p></div></footer>
</body>
</html>
'''
    write(PAGES["starjars"][lang], html)


NOT_FOUND = '''<div class="prose">
<h1>Bu sayfa yok</h1>
<p class="lede">Adres yanlış yazılmış ya da sayfa taşınmış olabilir.</p>
<div class="actions"><a class="button" href="/">Ana sayfaya dön</a><a class="button quiet" href="/destek.html">Destek</a></div>
<div lang="en" class="lang-block">
<h2>This page doesn't exist</h2>
<p>The address may be mistyped, or the page may have moved.</p>
<div class="actions"><a class="button" href="/en/">Go to the home page</a><a class="button quiet" href="/en/support.html">Support</a></div>
</div>
</div>'''

# ---------------------------------------------------------------- write everything

L = {"tr": {"privacy": "Gizlilik politikası", "terms": "Kullanım koşulları", "delete": "Hesap silme", "updated": "Son güncelleme",
            "applies": "Star Jars Sort Deluxe 1.0.0 ve sonraki sürümler için geçerlidir.", "game": "Oyun: Star Jars Sort Deluxe (Yıldız Kavanozu). Geliştirici: Symbol Interactive (Cem Tezgelen)."},
     "en": {"privacy": "Privacy policy", "terms": "Terms of use", "delete": "Deleting your account", "updated": "Last updated",
            "applies": "Applies to Star Jars Sort Deluxe 1.0.0 and later.", "game": "Game: Star Jars Sort Deluxe. Developer: Symbol Interactive (Cem Tezgelen)."}}

TERMS_INTRO = {
    "tr": "<p>Bu koşullar, Symbol Interactive'in oyunlarını (şu an Star Jars Sort Deluxe) oynarken seninle aramızdaki kuralları anlatır. Oyunu indirerek ya da oynayarak bu koşulları kabul etmiş olursun. Kısa ve anlaşılır tutmaya çalıştık; bir sorun olursa önce bize yaz.</p>",
    "en": "<p>These terms set out the rules between you and us when you play Symbol Interactive's games (currently Star Jars Sort Deluxe). By downloading or playing a game you accept them. We've tried to keep them short and clear; if there's a problem, write to us first.</p>",
}

for lang in ("tr", "en"):
    l = L[lang]
    tag = " · Symbol Interactive"
    page(lang, "home", "Symbol Interactive", {"tr": "Symbol Interactive: Aydın'da kurulmuş bağımsız mobil oyun stüdyosu. Sakin, özenli bulmaca oyunları.",
                                              "en": "Symbol Interactive: an independent mobile game studio from Aydın, Türkiye. Calm, carefully made puzzle games."}[lang], HOME[lang])
    page(lang, "games", {"tr": "Oyunlar", "en": "Games"}[lang] + tag, {"tr": "Symbol Interactive'in oyunları: Star Jars Sort Deluxe ve geliştirilenler.",
                                                                      "en": "Games by Symbol Interactive: Star Jars Sort Deluxe and more in development."}[lang], GAMES[lang])
    page(lang, "about", {"tr": "Hakkımızda", "en": "About"}[lang] + tag, {"tr": "Symbol Interactive'in vizyonu, nasıl çalıştığı ve kim olduğu.",
                                                                        "en": "Symbol Interactive's vision, how we work, and who we are."}[lang], ABOUT[lang])
    page(lang, "support", {"tr": "Destek", "en": "Support"}[lang] + tag, {"tr": "Symbol Interactive oyunları için destek.", "en": "Support for Symbol Interactive games."}[lang],
         f'<div class="doc single"><article class="prose">{SUPPORT[lang]}</article></div>')
    page(lang, "privacy", l["privacy"] + tag, {"tr": "Symbol Interactive oyunlarının gizlilik politikası (KVKK aydınlatma metni ve GDPR bilgilendirmesi).",
                                               "en": "Privacy policy of Symbol Interactive games (KVKK notice and GDPR information)."}[lang],
         doc(lang, l["privacy"], [f'{l["updated"]}: {UPDATED[lang]}', l["applies"]], "", PRIVACY[lang], summary=PRIVACY_SUMMARY[lang]))
    page(lang, "terms", l["terms"] + tag, {"tr": "Symbol Interactive oyunlarının kullanım koşulları: oyun içi öğeler, satın almalar, iadeler.",
                                           "en": "Terms of use of Symbol Interactive games: virtual items, purchases, refunds."}[lang],
         doc(lang, l["terms"], [f'{l["updated"]}: {UPDATED[lang]}'], TERMS_INTRO[lang], TERMS[lang]))
    page(lang, "delete", l["delete"] + tag, {"tr": "Star Jars Sort Deluxe hesabını ve bulut kaydını silme: adımlar, silinen ve kalan veriler, süreler.",
                                             "en": "Delete your Star Jars Sort Deluxe account and cloud save: steps, what is deleted and kept, and how long it takes."}[lang],
         doc(lang, {"tr": "Hesap silme", "en": "Deleting your account"}[lang], [l["game"], f'{l["updated"]}: {UPDATED[lang]}'], DELETE_INTRO[lang], DELETE[lang]))
    starjars_page(lang)

# The App Store's support URL (the user, 2026-11-03): /support, English first and Turkish below, on one page.
page("en", "support", "Support · Symbol Interactive", "Support for Symbol Interactive games, in English and Turkish.",
     f'<div class="doc single"><article class="prose">{SUPPORT["en"]}<div class="lang-block" lang="tr">'
     + SUPPORT["tr"].replace("<h1>Destek</h1>", '<h2 style="font-size:clamp(1.8rem,4vw,2.4rem)">Destek (Türkçe)</h2>', 1) + "</div></article></div>",
     own_path="/support.html", other_href=u("support", "tr"))
page("tr", None, "Sayfa yok · Symbol Interactive", "Sayfa bulunamadı. This page doesn't exist.", NOT_FOUND, own_path="/404.html", other_href="/en/")

(ROOT / "favicon.svg").write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><rect width="40" height="40" rx="9" fill="#161C33"/>'
    + mark(css_vars=False).replace('<svg viewBox="0 0 40 40" aria-hidden="true">', '<g transform="translate(4 4) scale(.8)">').replace("</svg>", "</g>") + "</svg>\n", encoding="utf-8")
(ROOT / "img" / "starjars-icon.svg").write_text(jar("fav", animate=False, label=None).replace('<svg class="fav"', '<svg xmlns="http://www.w3.org/2000/svg"').replace(' aria-hidden="true"', "") + "\n", encoding="utf-8")

# Guards: no review notes, every page has its twin, and the two hand-kept files are untouched by this script.
pages = [*ROOT.glob("*.html"), *ROOT.glob("en/*.html")]
assert not any("REVIEW" in p.read_text(encoding="utf-8") for p in pages), "a REVIEW note is left in a page"
for key, paths in PAGES.items():
    for lang, path in paths.items():
        assert (ROOT / path).exists(), path
print(f"built {len(pages)} pages")
