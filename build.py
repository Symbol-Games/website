"""Builds the Symbol Interactive site (symbolinteractive.com.tr): python3 build.py

Turkish pages at the root, English under en/; every page links its twin (language switch + hreflang). The guides (sky, jars, news) read data/game.json, made by tools/export_game.py.
The look is "Oyuncak Kutusu": Zar the die is a toy and the site is his packaging. One stylesheet (site.css), one script (site.js),
self-hosted OFL fonts. No cookies, no analytics, no third-party requests. Design: game-studio docs/superpowers/specs/2026-11-05-symbol-interactive-site-design.md

The legal texts follow the decisions memo:
~/game-studio/docs/superpowers/research/2026-11-04-symbol-interactive-legal-decisions.md
Never written here: CNAME and app-ads.txt (they are maintained by hand). After a build: python3 tools/check_site.py
"""
import json
import math
import pathlib
from html import escape as esc

ROOT = pathlib.Path(__file__).parent
SITE = "https://symbolinteractive.com.tr"
MAIL = "symbolinteractive@gmail.com"  # the support address the user set in the release checklist (2026-11-03)
CONTROLLER = "Cem Tezgelen"  # The law needs it in the privacy policy (KVKK Art. 10, GDPR Art. 13) and nowhere else: the user is not to be named on the site (2026-11-05). That page stays out of search.
NOINDEX = {"privacy"}
UPDATED = {"tr": "5 Kasım 2026", "en": "5 November 2026"}  # privacy policy, terms and deletion pages
# What the guides show comes from the game itself: tools/export_game.py writes this file.
GAMEDATA = json.loads((ROOT / "data" / "game.json").read_text(encoding="utf-8"))
SKY = GAMEDATA["constellations"]
# Every count on the site reads from here. The "+" follows the store listing (user, 2026-11-04): new constellations never make it false.
GAME = {"constellations": "20+", "levels": "150+", "languages": "13", "stars": f"{sum(len(c['stars']) for c in SKY)}+", "space": f"{len(GAMEDATA['guide']['space'])}+"}
PROMO = {"tr": "https://www.youtube.com/watch?v=xBwJEss7ArU", "en": "https://www.youtube.com/watch?v=RyvFsGcgpys"}  # a plain link: never embedded

# Every page and its twin. Paths are the files; URLs are root-absolute so the 404 page works at any depth.
PAGES = {
    "home": {"tr": "index.html", "en": "en/index.html"},
    "games": {"tr": "oyunlar.html", "en": "en/games.html"},
    "about": {"tr": "hakkimizda.html", "en": "en/about.html"},
    "starjars": {"tr": "starjars.html", "en": "en/starjars.html"},
    "press": {"tr": "basin.html", "en": "en/press.html"},
    "support": {"tr": "destek.html", "en": "en/support.html"},
    "privacy": {"tr": "gizlilik.html", "en": "en/privacy.html"},
    "terms": {"tr": "kullanim-kosullari.html", "en": "en/terms.html"},
    "delete": {"tr": "hesap-silme.html", "en": "en/delete-account.html"},
    "news": {"tr": "yenilikler.html", "en": "en/news.html"},
    "guide": {"tr": "rehber.html", "en": "en/guide.html"},
    "makingof": {"tr": "yapim-hikayesi.html", "en": "en/making-of.html"},
    "sky": {"tr": "gokyuzu/index.html", "en": "en/sky/index.html"},
    **{f"sky:{c['id']}": {"tr": f"gokyuzu/{c['slug']}.html", "en": f"en/sky/{c['id']}.html"} for c in SKY},
}


def u(key, lang):
    return "/" + PAGES[key][lang].removesuffix("index.html")


def mailto(subject=None):
    q = f"?subject={subject.replace(' ', '%20')}" if subject else ""
    return f'<a href="mailto:{MAIL}{q}">{MAIL}</a>'


# ---------------------------------------------------------------- Zar, the logo (vectors from studio-core/Tools/art/studio-logo, key "tekgoz")

Z = json.loads((ROOT / "brand" / "zar.json").read_text(encoding="utf-8"))
ZAR_VB = "120 70 790 900"


def zar(cls=""):
    """The character, inline so his eyes can move. --z-ink and --z-hole set the two colours; the logo's cuts show --z-hole."""
    return (f'<svg class="zar {cls}" viewBox="{ZAR_VB}" aria-hidden="true" focusable="false"><path class="z-ink" d="{Z["legL"]}"/><path class="z-ink" d="{Z["legR"]}"/><path class="z-ink" d="{Z["body"]}"/>'
            f'<path class="z-hole" d="{Z["eyeL"]}"/><path class="z-hole" d="{Z["eyeR"]}"/><path class="z-pup" d="{Z["pupL"]}"/><path class="z-pup" d="{Z["pupR"]}"/>'
            f'<circle class="z-lid" cx="330" cy="300" r="78"/><circle class="z-lid" cx="680" cy="272" r="78"/><path class="z-shut" d="M272 296q58 38 116 0"/><path class="z-shut" d="M622 268q58 38 116 0"/>'
            f'<path class="z-hole" d="{Z["nose"]}"/><path class="z-hole" d="{Z["cheekL"]}"/><path class="z-hole" d="{Z["cheekR"]}"/><path class="z-hole" d="{Z["smile"]}"/></svg>')


def zar_mask(uid):
    """The mark with real holes, for files shown on any ground."""
    white = "".join(f'<path d="{Z[k]}" fill="#fff"/>' for k in ("legL", "legR", "body"))
    black = "".join(f'<path d="{Z[k]}" fill="#000"/>' for k in ("eyeL", "eyeR", "nose", "cheekL", "cheekR", "smile"))
    pupils = "".join(f'<path d="{Z[k]}" fill="#fff"/>' for k in ("pupL", "pupR"))
    return f'<mask id="{uid}" maskUnits="userSpaceOnUse" x="120" y="70" width="790" height="900" style="mask-type:luminance"><rect x="120" y="70" width="790" height="900" fill="#000"/>{white}{black}{pupils}</mask>'


def logo_file(colour):
    """The horizontal lockup: mark, SYMBOL, and INTERACTIVE set to the same width, as on the approved logo."""
    (x0, y0, x1, y1), (a0, b0, a1, b1) = Z["wordBox"][:4], Z["subBox"][:4]
    k = (x1 - x0) / (a1 - a0)
    hw, gap, hs = y1 - y0, 12, (b1 - b0) * k
    h = hw + gap + hs
    mh = h * 1.34
    mw = mh * 790 / 900
    ox, top = mw + 16, (mh - h) / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ox + x1 - x0:.1f} {mh:.1f}" width="{ox + x1 - x0:.0f}" height="{mh:.0f}"><title>Symbol Interactive</title>'
            f'<g transform="scale({mh / 900:.4f}) translate(-120 -70)">{zar_mask("z")}<rect x="120" y="70" width="790" height="900" fill="{colour}" mask="url(#z)"/></g>'
            f'<path fill="{colour}" transform="translate({ox - x0:.2f} {top - y0:.2f})" d="{Z["word"]}"/>'
            f'<path fill="{colour}" transform="translate({ox - a0 * k:.2f} {top + hw + gap - b0 * k:.2f}) scale({k:.4f})" d="{Z["sub"]}"/></svg>\n'), round(ox + x1 - x0), round(mh)


LOGO_W, LOGO_H = logo_file("#111")[1:]


def logo(colour="ink"):
    return f'<img src="/img/logo-{colour}.svg" width="{LOGO_W}" height="{LOGO_H}" alt="">'


def pip_die(n):
    pos = {1: [(50, 50)], 2: [(28, 28), (72, 72)], 3: [(26, 26), (50, 50), (74, 74)], 4: [(28, 28), (72, 28), (28, 72), (72, 72)]}[n]
    return ('<svg class="pipdie" viewBox="0 0 100 100" aria-hidden="true"><rect class="pd-b" x="3" y="3" width="94" height="94" rx="24"/>'
            + "".join(f'<circle class="pd-p" cx="{x}" cy="{y}" r="9.5"/>' for x, y in pos) + "</svg>")


# The Star Jars jar: the favicon the demo and the game's page use.
def star(cx, cy, r, fill, rot=0.0, inner=0.48):
    d = ""
    for i in range(10):
        a = -math.pi / 2 + rot + i * math.pi / 5
        k = r * inner if i % 2 else r
        d += ("L" if i else "M") + f"{cx + k * math.cos(a):.1f} {cy + k * math.sin(a):.1f}"
    return f'<path d="{d}Z" fill="{fill}" stroke="#fff" stroke-width="{r * 0.18:.1f}" stroke-linejoin="round"/>'


JAR_STARS = [(77, 193, 22, "#FF4FA6", .1), (123, 191, 22, "#14DCC8", -.25), (99, 156, 22, "#FFCC2E", .3), (75, 120, 19, "#A273FF", 0), (121, 118, 19, "#3FDD77", .2)]


def jar_icon():
    stars = "".join(star(x, y, r, c, rot) for x, y, r, c, rot in JAR_STARS)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 240">
  <rect x="44" y="52" width="112" height="170" rx="40" fill="rgba(255,255,255,.13)" stroke="#fff" stroke-width="6"/>
  {stars}
  <rect x="58" y="70" width="8" height="34" rx="4" fill="#fff" opacity=".42"/>
  <rect x="62" y="30" width="76" height="28" rx="9" fill="#FFC93C" stroke="#fff" stroke-width="5"/>
</svg>
'''


# ---------------------------------------------------------------- the frame of every page

T = {
    "tr": {"skip": "İçeriğe geç", "nav": "Ana menü", "games": "Oyunlar", "about": "Hakkımızda", "studio_nav": "Stüdyo", "support": "Destek", "other": "English", "other_lang": "en",
           "home": "Symbol Interactive ana sayfa", "foot_about": "Türkiye’de kurulmuş bağımsız bir oyun stüdyosu.",
           "no_track": "Bu site çerez kullanmaz ve ziyaretçileri izlemez.", "studio": "Stüdyo", "help": "Yardım", "legal": "Yasal", "press": "Basın kiti",
           "home_l": "Ana sayfa", "privacy": "Gizlilik politikası", "terms": "Kullanım koşulları", "delete": "Hesap silme", "starjars": "Star Jars",
           "contents": "Bu sayfada", "game_page": "Oyunun sayfası", "guide": "Kavanoz ve kural rehberi", "sky": "Gökyüzü rehberi", "news": "Yenilikler", "making": "Yapım hikâyesi"},
    "en": {"skip": "Skip to content", "nav": "Main menu", "games": "Games", "about": "About", "studio_nav": "Studio", "support": "Support", "other": "Türkçe", "other_lang": "tr",
           "home": "Symbol Interactive home", "foot_about": "An independent game studio founded in Türkiye.",
           "no_track": "This site uses no cookies and does not track visitors.", "studio": "Studio", "help": "Help", "legal": "Legal", "press": "Press kit",
           "home_l": "Home", "privacy": "Privacy policy", "terms": "Terms of use", "delete": "Delete account", "starjars": "Star Jars",
           "contents": "On this page", "game_page": "The game’s page", "guide": "Jar and rule guide", "sky": "Sky guide", "news": "What’s new", "making": "The making of"},
}


def alternates(key, own_lang, own_path=None):
    if key is None:
        return '<meta name="robots" content="noindex">'
    canon = SITE + (own_path or u(key, own_lang))
    robots = '<meta name="robots" content="noindex">\n' if key in NOINDEX else ""
    return (f'{robots}<link rel="canonical" href="{canon}">\n'
            f'<link rel="alternate" hreflang="tr" href="{SITE}{u(key, "tr")}">\n'
            f'<link rel="alternate" hreflang="en" href="{SITE}{u(key, "en")}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{SITE}{u(key, "tr")}">')


def head(lang, title, description, key, own_path=None, favicon="/favicon.svg", theme="#F4B90B", og=None, ld=None):
    url = SITE + (own_path or (u(key, lang) if key else "/"))
    image = SITE + (og or f"/img/og-{lang}.jpg")
    data = f'\n<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>' if ld else ""
    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{description}">
<meta name="theme-color" content="{theme}">
{alternates(key, lang, own_path)}
<meta property="og:type" content="website">
<meta property="og:site_name" content="Symbol Interactive">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{"tr_TR" if lang == "tr" else "en_US"}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{favicon}" type="image/svg+xml">
<link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
<link rel="preload" href="/fonts/SymbolDisplay.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/site.css">{data}
</head>'''


def nav_items(lang, key, other_href):
    t = T[lang]
    labels = {"games": t["games"], "about": t["studio_nav"], "support": t["support"]}
    items = []
    in_game = key in ("starjars", "guide", "news") or (key or "").startswith("sky")
    for k, label in labels.items():
        cur = ' aria-current="page"' if k == key or (k == "games" and in_game) or (k == "about" and key == "makingof") else ""
        items.append(f'<li><a href="{u(k, lang)}"{cur}>{label}</a></li>')
    items.append(f'<li><a href="{other_href}" lang="{t["other_lang"]}" hreflang="{t["other_lang"]}">{t["other"]}</a></li>')
    return f'<nav aria-label="{t["nav"]}"><ul>{"".join(items)}</ul></nav>'


def brand(lang, colour="ink"):
    return f'<a class="brand" href="{u("home", lang)}" aria-label="{T[lang]["home"]}">{logo(colour)}</a>'


def sitebar(lang, key, other_href):
    """The quiet top of every page that is not a packaged card."""
    return f'<header class="sitebar">{brand(lang)}{nav_items(lang, key, other_href)}</header>'


def hero_bar(lang, key, other_href, colour="ink"):
    """The same menu, printed on the card."""
    return f'<header class="bar">{brand(lang, colour)}{nav_items(lang, key, other_href)}</header>'


def footer(lang, other_href):
    t = T[lang]
    return f'''<footer>
  <div><a class="brand" href="{u("home", lang)}" aria-label="{t["home"]}">{logo("yellow")}</a>
    <p class="promise">{t["foot_about"]}</p><p class="promise">{t["no_track"]}</p><p class="promise">© 2026 Symbol Interactive</p></div>
  <div><h2>{t["studio"]}</h2><ul>
    <li><a href="{u("home", lang)}">{t["home_l"]}</a></li><li><a href="{u("games", lang)}">{t["games"]}</a></li>
    <li><a href="{u("about", lang)}">{t["about"]}</a></li><li><a href="{u("makingof", lang)}">{t["making"]}</a></li><li><a href="{u("press", lang)}">{t["press"]}</a></li></ul></div>
  <div><h2>{t["starjars"]}</h2><ul>
    <li><a href="{u("starjars", lang)}">{t["game_page"]}</a></li><li><a href="{u("guide", lang)}">{t["guide"]}</a></li>
    <li><a href="{u("sky", lang)}">{t["sky"]}</a></li><li><a href="{u("news", lang)}">{t["news"]}</a></li></ul></div>
  <div><h2>{t["help"]}</h2><ul>
    <li><a href="{u("support", lang)}">{t["support"]}</a></li><li><a href="{u("delete", lang)}">{t["delete"]}</a></li>
    <li><a href="mailto:{MAIL}">{MAIL.replace("@", "<wbr>@")}</a></li></ul></div>
  <div><h2>{t["legal"]}</h2><ul>
    <li><a href="{u("privacy", lang)}">{t["privacy"]}</a></li><li><a href="{u("terms", lang)}">{t["terms"]}</a></li>
    <li><a href="{other_href}" lang="{t["other_lang"]}" hreflang="{t["other_lang"]}">{t["other"]}</a></li></ul></div>
</footer>'''


def write(path, html):
    out = ROOT / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")


def page(lang, key, title, description, body, own_path=None, other_href=None, plain=False, script=False, og=None, ld=None):
    """plain: the body brings its own full-width sections; otherwise it is a reading page."""
    path = own_path.lstrip("/") if own_path else PAGES[key][lang]
    other_href = other_href or (u(key, "en" if lang == "tr" else "tr") if key else "/en/")
    main = f'<main id="main">\n{body}\n</main>' if plain else f'<main id="main" class="reading"><div class="wrap">\n{body}\n</div></main>'
    js = '\n<script src="/site.js" defer></script>' if script else ""
    write(path, f'''{head(lang, title, description, key, own_path, og=og, ld=ld)}
<body>
<a class="skip" href="#main">{T[lang]["skip"]}</a>
{sitebar(lang, key, other_href)}
{main}
{footer(lang, other_href)}{js}
</body>
</html>
''')


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


# ---------------------------------------------------------------- the packaging's parts, used on several pages

PLAY_ICON = '<svg width="16" height="18" viewBox="0 0 16 18" aria-hidden="true"><path fill="currentColor" d="M1 1.800c0-1 1-1.600 1.900-1.100l11.600 7.200c.8.500.8 1.700 0 2.200L2.900 17.300c-.9.500-1.900-.1-1.900-1.100Z"/></svg>'
APPLE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M16.700 12.700c0-2.300 1.900-3.400 2-3.500-1.100-1.600-2.800-1.800-3.400-1.800-1.400-.1-2.800.9-3.500.9s-1.900-.9-3.100-.8c-1.600 0-3 .9-3.800 2.300-1.600 2.800-.4 7 1.200 9.300.8 1.100 1.700 2.400 2.900 2.300 1.200 0 1.600-.7 3-.7s1.800.7 3 .7c1.300 0 2.100-1.100 2.800-2.200.9-1.300 1.300-2.500 1.300-2.600-.1 0-2.400-.9-2.400-3.900ZM14.400 5.800c.6-.8 1.100-1.900 1-3-1 0-2.100.6-2.800 1.400-.6.7-1.200 1.800-1 2.900 1.100.1 2.200-.6 2.800-1.300Z"/></svg>'
PLAY_STORE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M4 2.600v18.800c0 .4.200.7.500.9L15 12 4.500 1.700c-.3.200-.5.500-.5.900Zm14.300 6.200-3 3.200 3 3.200 3.500-2c.8-.5.800-1.900 0-2.400l-3.500-2ZM5.700 1.100 14.300 11l2.800-2.900L6.700 1.200a1.200 1.200 0 0 0-1-.1Zm0 21.800c.3.100.7.100 1-.1l10.400-6.900-2.800-2.900-8.600 9.900Z"/></svg>'

C = {
    "tr": {
        "desc": "Symbol Interactive, Türkiye’de kurulmuş bağımsız bir oyun stüdyosu. Star Jars Sort Deluxe’ü tarayıcında dene.",
        "h1": "Kutudan oyun çıkar.", "lede": "Symbol Interactive, Türkiye’de kurulmuş bağımsız bir oyun stüdyosu. Oyunlarımızı oyuncak yapar gibi, özenle yapıyoruz.",
        "our_games": "Oyunlarımız", "play_web": "Tarayıcıda oyna", "game_page": "Oyunun sayfası", "age": "13 yaş ve üstü",
        "badges": ["Pil gerekmez", "Türkiye’de yapıldı"], "burst": ("Star Jars<br>yakında!", "Star Jars<br>çıktı!"), "say": "Sonunda! Oyunlar aşağıda.",
        "open": "Ambalajı aç", "shut": "Ambalajı kapat",
        "shelf": "Raftakiler", "alt": "Yıldız Kavanozu", "box_small": f"Sort Deluxe · {GAME['levels']} seviye · {GAME['languages']} dil",
        "game_text": "Renkli yıldızları kavanozlar arasında dök, her kavanozda tek renk kalınca mühürle. Her seviye gerçek bir takımyıldızının bir yıldızını yakar.",
        "soon": ("Yakında App Store ve Google Play’de", "App Store ve Google Play’de"), "soon_short": "Yakında", "store_now": "Şimdi indir",
        "next": "Yandaki paketin içinde ne olduğunu biz de söylemiyoruz: yeni oyunlar üzerinde çalışıyoruz, hazır olduklarında burada olacaklar.",
        "film_label": "Tanıtım videosu", "film_h": "Otuz saniyede Star Jars", "film_p": "Sesi aç, kutunun içindekileri izle.", "film_alt": "Star Jars tanıtım videosu", "film_link": "YouTube’da izle",
        "clips_pause": "Videoları durdur", "clips_play": "Videoları oynat", "parts_label": "İçindekiler · Star Jars Sort Deluxe", "parts_h": "Kutudan neler çıkıyor", "parts_p": "Süre yok, acele yok: kendi hızında oyna.",
        "parts": [
            ("Gerçek takımyıldızlarını yak", f"{GAME['levels']} seviye, {GAME['constellations']} gerçek takımyıldızı: Büyük Ayı’dan Kartal’a, her yıldız gerçek adıyla.", ["map", "solve"], ["Takımyıldızı haritası", "Yıldızlar kavanoza dökülüyor"]),
            ("Her yıldızın kartı", "Uzaklığı, rengi, parlaklığı ve adının anlamı. Her yıldızın gerçek bir hikâyesi var.", ["card"], ["Yıldız kartı"]),
            ("Her takımyıldızına kendi kavanozu", "Bölüm, o takımyıldızına özel çizilmiş bir kavanozla biter. Kartal’ın kanatlı kavanozu gibi.", ["boss"], ["Kartal bölümünün kanatlı kavanozu"]),
            ("Yol boyunca yeni fikirler", "Buzlu, etiketli ve kilitli kavanozlar, joker yıldız, saatli yıldız, hamle sınırı, bağlı yıldızlar, ters ve tek yönlü kavanozlar.", ["clock"], ["Saatli yıldızlı bir seviye"]),
            ("Kendi kuralıyla uzay bölümleri", "Bulutsu, Satürn’ün halkası, Betelgeuse süpernovası, Leonid meteorları, Sombrero Gökadası ve Gliese 581.", ["galaxy"], ["Sombrero Gökadası bölümü"]),
            ("Her gün yeni bir bulmaca", "Günün bulmacası, günlük görevler, seri ödülleri ve kumbara.", ["daily"], ["Günün bulmacası"]),
            ("Yıldızlarını rafına diz", "Topladığın her gök cismi seninle kalır.", ["mystars"], ["Yıldızlarım rafı"]),
        ],
        "all_h": "Herkes oynasın", "all_p": "Renk körü modu: her rengin kendi şekli ve işareti var. Üç yazı boyutu. İnternetsiz oynanır, bulut kaydı isteğe bağlı.", "langs": f"{GAME['languages']} dil",
        "try_label": "Hemen dene", "try_h": "Kutuyu açmadan oyna", "try_p": "Dök, ayır, mühürle. İki bölümü tarayıcında oyna: oyunun gerçek kuralları ve görselleri. İndirme yok, hesap yok.", "try_note": "Süpernova bölümü oyunun ilerleyen kısmından.",
        "play": "Oyna", "demo_alt": "Demonun ilk bölümü: kavanozlarda renkli yıldızlar", "demo_title": "Star Jars demosu", "demo_close": "Kapat",
        "facts_h": "Oyun Değerleri", "facts_for": "Star Jars Sort Deluxe, bir kutu için", "facts": [("Takımyıldızı", GAME["constellations"]), ("Seviye", GAME["levels"]), ("Dil", GAME["languages"]), ("Fiyat", "Ücretsiz*")],
        "facts2": [("Yıldız kartı", GAME["stars"]), ("Uzay bölümü", GAME["space"]), ("Her gün yeni bulmaca", "1")],
        "facts_note": "* Reklam ve uygulama içi satın alma içerir. 13 yaş ve üstü içindir. Neyi neden işlediğimiz gizlilik politikasında yazar.",
        "rules_h": "Nasıl oyun yapıyoruz",
        "rules": [("Önce oynarız", "Kararı kâğıt üstünde değil, oynayarak veririz. Tutmayan fikri cilalamak yerine bırakırız."),
                  ("Her oyun kendine benzer", "Her oyunun görünüşü, sesi ve kuralları o oyun için yapılır. İki oyunumuz yan yana geldiğinde kardeş gibi durmaz."),
                  ("Ayrıntıdan vazgeçmeyiz", "Bir dokunuşun hissini, bir animasyonun süresini, bir bilginin doğruluğunu, kimse fark etmeyecek olsa da düzeltiriz."),
                  ("Çıkınca bitmez", "Yayın başlangıçtır. Oyunlarımıza düzenli olarak yeni bölüm ve yeni kural eklemeyi sürdürürüz.")],
        "maker_h": "Üretici", "maker_p": "Symbol Interactive 2026’da kuruldu. Oyunlarımızı tasarlıyor, yazıyor, çiziyor ve yayımlıyoruz; büyük bir ekip değiliz, oyunun her ayrıntısına dokunuyoruz.",
        "maker_more": "Stüdyoyu tanı", "maker_rows": [("Üretici", "Symbol Interactive"), ("Adres", "Aydın, Türkiye")], "write": "Bize yaz",
    },
    "en": {
        "desc": "Symbol Interactive is an independent game studio from Türkiye. Play Star Jars Sort Deluxe in your browser.",
        "h1": "There’s a game in this box.", "lede": "Symbol Interactive is an independent game studio founded in Türkiye. We make games the way you’d make a good toy: with care.",
        "our_games": "Our games", "play_web": "Play in your browser", "game_page": "The game’s page", "age": "Ages 13 and up",
        "badges": ["No batteries needed", "Made in Türkiye"], "burst": ("Star Jars<br>soon!", "Star Jars<br>is out!"), "say": "At last! The games are below.",
        "open": "Open the packaging", "shut": "Close the packaging",
        "shelf": "On the shelf", "alt": "A calm sorting puzzle", "box_small": f"Sort Deluxe · {GAME['levels']} levels · {GAME['languages']} languages",
        "game_text": "Pour colourful stars between jars until every jar holds a single colour, then seal it. Every level lights a star of a real constellation.",
        "soon": ("Coming soon to the App Store and Google Play", "On the App Store and Google Play"), "soon_short": "Coming soon", "store_now": "Download now",
        "next": "We’re not saying what’s in the other box either: more games are in development, and they’ll appear here when they’re ready.",
        "film_label": "The trailer", "film_h": "Star Jars in thirty seconds", "film_p": "Turn the sound on and see what’s in the box.", "film_alt": "Star Jars trailer", "film_link": "Watch on YouTube",
        "clips_pause": "Pause the clips", "clips_play": "Play the clips", "parts_label": "Contents · Star Jars Sort Deluxe", "parts_h": "What’s in the box", "parts_p": "No timers, no rush: play at your own pace.",
        "parts": [
            ("Light up real constellations", f"{GAME['levels']} levels across {GAME['constellations']} real constellations, from the Great Bear to the Eagle, every star by its real name.", ["map", "solve"], ["The constellation map", "Stars pouring into a jar"]),
            ("A card for every star", "Its distance, colour, brightness and what its name means. Every star has a true story.", ["card"], ["A star card"]),
            ("A jar for every constellation", "Each chapter ends with a jar drawn for its constellation, like the Eagle’s winged jar.", ["boss"], ["The Eagle chapter’s winged jar"]),
            ("New ideas along the way", "Icy, labelled and locked jars, joker stars, clock stars, move limits, bound stars, upside-down and one-way jars.", ["clock"], ["A level with a clock star"]),
            ("Space chapters with their own rules", "A nebula, Saturn’s ring, the Betelgeuse supernova, the Leonid meteors, the Sombrero Galaxy and Gliese 581.", ["galaxy"], ["The Sombrero Galaxy chapter"]),
            ("A new puzzle every day", "A daily puzzle, daily quests, streak rewards and a piggy bank.", ["daily"], ["The daily puzzle"]),
            ("Fill your shelf of stars", "Every sky object you win stays with you.", ["mystars"], ["The shelf of stars"]),
        ],
        "all_h": "Everyone plays", "all_p": "Colour-blind mode: every colour has its own shape and mark. Three text sizes. Plays offline; cloud save is optional.", "langs": f"{GAME['languages']} languages",
        "try_label": "Try it now", "try_h": "Play before you open it", "try_p": "Pour, sort, seal. Play two boards in your browser, with the game’s real rules and art. No download, no account.", "try_note": "The supernova chapter comes from later in the game.",
        "play": "Play", "demo_alt": "The demo’s first board: colourful stars in jars", "demo_title": "Star Jars demo", "demo_close": "Close",
        "facts_h": "Game Facts", "facts_for": "Star Jars Sort Deluxe, per box", "facts": [("Constellations", GAME["constellations"]), ("Levels", GAME["levels"]), ("Languages", GAME["languages"]), ("Price", "Free*")],
        "facts2": [("Star cards", GAME["stars"]), ("Space chapters", GAME["space"]), ("New puzzle every day", "1")],
        "facts_note": "* Contains ads and in-app purchases. For ages 13 and up. What we process and why is in the privacy policy.",
        "rules_h": "How we make games",
        "rules": [("We play first", "We decide by playing, not on paper. An idea that doesn’t work gets dropped, not polished."),
                  ("Every game looks like itself", "Each game’s look, sound and rules are made for that game. Put two of our games side by side and they won’t look like siblings."),
                  ("We don’t give up on details", "The feel of a tap, the length of an animation, the accuracy of a fact: we fix them even when nobody would notice."),
                  ("Release isn’t the end", "Release is the start. We keep adding new chapters and new rules to our games.")],
        "maker_h": "Made by", "maker_p": "Symbol Interactive was founded in 2026. We design, write, draw and publish our games ourselves; we are not a big team, and we touch every detail of every game.",
        "maker_more": "About the studio", "maker_rows": [("Made by", "Symbol Interactive"), ("Address", "Aydın, Türkiye")], "write": "Write to us",
    },
}
LANGS = [("tr", "Türkçe"), ("en", "English"), ("es", "Español"), ("pt", "Português"), ("de", "Deutsch"), ("fr", "Français"), ("it", "Italiano"), ("ru", "Русский"), ("id", "Bahasa Indonesia"), ("ja", "日本語"), ("ko", "한국어"), ("zh-Hans", "简体中文"), ("ar", "العربية")]


def live_i(lang):
    return 1 if STORES["live"] else 0


def store_buttons(lang):
    """Pills until launch day; real links once STORES["live"] is set."""
    c = C[lang]
    small = c["store_now"] if STORES["live"] else c["soon_short"]
    def one(icon, name, url):
        inner = f'{icon}<span><small>{small}</small>{name}</span>'
        return f'<a class="store" href="{url}">{inner}</a>' if STORES["live"] else f'<div class="store">{inner}</div>'
    return one(APPLE, "App Store", STORES["ios"]) + one(PLAY_STORE, "Google Play", STORES["android"])


def blister(lang, inside, say_style=""):
    c = C[lang]
    return (f'<button class="blister" id="blister" type="button" aria-label="{c["open"]}" data-open="{c["open"]}" data-shut="{c["shut"]}">{inside}<span class="bubble"></span></button>'
            f'<div class="say" aria-hidden="true"{say_style}>{c["say"]}</div>')


def next_box():
    """The second box on the shelf: wrapped until NEXT_GAME is set, then it wears the game's name."""
    if not NEXT_GAME:
        return '<div class="box3d small wrapped" aria-hidden="true"><div class="box"><div class="bt"></div><div class="bs"><span>?</span></div><div class="bf"><b>?</b></div></div></div>'
    name = esc(NEXT_GAME["name"])
    return f'<div class="box3d small opened" aria-hidden="true"><div class="box"><div class="bt"></div><div class="bs"><span>{name}</span></div><div class="bf"><b>{name}</b></div></div></div>'


def next_line(lang):
    if not NEXT_GAME:
        return C[lang]["next"]
    n = NEXT_GAME
    steam = f' · <a href="{n["steam"]}" rel="noopener">{NEXT_STEAM[lang]}</a>' if n.get("steam") else ""
    title = f'<a href="{n["url"]}">{esc(n["name"])}</a>' if n.get("url") else f'<b>{esc(n["name"])}</b>'
    return f'{NEXT_SOON[lang]}: {title}. {esc(n[lang])}{steam}'


def shelf(lang, tag="h2", title=None, lede="", play=None):
    c = C[lang]
    play = play or u("starjars", lang) + "#dene"
    intro = f'<p class="lede">{lede}</p>' if lede else ""
    sub = "h2" if tag == "h1" else "h3"
    return f'''<section class="shelf" id="oyunlar" aria-labelledby="shelf-h">
  <{tag} id="shelf-h">{title or c["shelf"]}</{tag}>{intro}
  <div class="onshelf">
    <div class="box3d" aria-hidden="true"><div class="box">
      <div class="bt"></div>
      <div class="bs"><span>STAR JARS · SYMBOL INTERACTIVE</span></div>
      <div class="bf"><div class="bfh">{logo()}<b>13+</b></div><div class="bft"><p class="bftitle">Star Jars</p><small>{c["box_small"]}</small></div><img src="/img/sj/{lang}-board.jpg" width="560" height="1213" alt="" loading="lazy"></div>
    </div></div>
    {next_box()}
    <article class="info" aria-labelledby="sj">
      <span class="label">{c["alt"]}</span>
      <{sub} id="sj">Star Jars Sort Deluxe</{sub}>
      <p>{c["game_text"]}</p>
      <p class="soon">{c["soon"][live_i(lang)]}</p>
      <div class="actions"><a class="btn" href="{play}">{c["play_web"]}</a><a class="btn line" href="{u("starjars", lang)}">{c["game_page"]}</a></div>
      <p class="nextgame">{next_line(lang)}</p>
    </article>
  </div>
  <div class="plank" aria-hidden="true"></div>
</section>'''


def media(lang, name, alt, cls=""):
    """Clips play only while on screen (site.js); stills are lazy."""
    posters = {"map": "map", "solve": "clip-solve", "card": "clip-card"}
    if name in posters:
        return f'<div class="shot {cls}"><video class="auto" src="/media/{lang}-{name}.mp4" poster="/img/sj/{lang}-{posters[name]}.jpg" width="460" height="996" muted loop playsinline preload="none" aria-label="{alt}"></video></div>'
    return f'<div class="shot {cls}"><img src="/img/sj/{lang}-{name}.jpg" width="560" height="1100" alt="{alt}" loading="lazy"></div>'


def parts(lang, night=False):
    c = C[lang]
    tiles = ""
    for i, (title, text, names, alts) in enumerate(c["parts"]):
        letter = "ABCDEFG"[i]
        wide = " wide" if i == 0 else ""
        shots = "".join(media(lang, n, a, "s2" if j else "") for j, (n, a) in enumerate(zip(names, alts)))
        tiles += f'<article class="part{wide}"><div class="tx"><b class="let" aria-hidden="true">{letter}</b><h3>{title}</h3><p>{text}</p></div>{shots}</article>'
    names = "".join(f'<li lang="{code}"{" dir=" + chr(34) + "rtl" + chr(34) if code == "ar" else ""}>{n}</li>' for code, n in LANGS)
    tiles += f'<article class="part all"><div class="tx"><b class="let" aria-hidden="true">H</b><h3>{c["all_h"]}</h3><p>{c["all_p"]}</p><ul class="langs" aria-label="{c["langs"]}">{names}</ul></div></article>'
    return f'''<section class="inbox{" night" if night else ""}" id="ozellikler" aria-labelledby="parts-h">
  <div class="sec-head"><div><span class="label">{c["parts_label"]}</span><h2 id="parts-h">{c["parts_h"]}</h2></div><div class="sec-side"><p>{c["parts_p"]}</p><button class="clips-toggle" id="clips-toggle" type="button" hidden data-pause="{c["clips_pause"]}" data-play="{c["clips_play"]}">{c["clips_pause"]}</button></div></div>
  <div class="parts">{tiles}</div>
</section>'''


def facts_label(lang):
    c = C[lang]
    rows = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in c["facts"][:-1])
    k, v = c["facts"][-1]
    rows += f'<dt class="gap">{k}</dt><dd class="gap">{v}</dd>' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in c["facts2"])
    return f'<aside class="facts" aria-labelledby="facts-h"><h3 id="facts-h">{c["facts_h"]}</h3><p class="for">{c["facts_for"]}</p><dl>{rows}</dl><p>{c["facts_note"]}</p></aside>'


def demo_dialog(lang):
    c = C[lang]
    return f'<dialog class="demo-box" id="demo-box" aria-label="{c["demo_title"]}"><div class="demo-bar"><span>{c["demo_title"]}</span><button type="button" id="demo-close">{c["demo_close"]}</button></div><div class="demo-frame" id="demo-frame"></div></dialog>'


def demo_block(lang, gold=False):
    """The real demo. Nothing loads until asked; without JavaScript the button is a plain link to it."""
    c = C[lang]
    return f'''<section class="back{" gold" if gold else ""}" id="dene" aria-labelledby="try-h">
  <div>
    <span class="label">{c["try_label"]}</span>
    <h2 id="try-h">{c["try_h"]}</h2>
    <p class="say2">{c["try_p"]}</p>
    <small>{c["try_note"]}</small>
  </div>
  <div class="devwrap"><div class="device" id="device"><img src="/img/{lang}-demo.jpg" width="488" height="1055" alt="{c["demo_alt"]}" loading="lazy"><a class="btn gold go" href="/demo/starjars.html#web-{lang}" data-demo data-title="{c["demo_title"]}">{PLAY_ICON}{c["play"]}</a></div><button class="demo-stop" id="demo-stop" type="button" hidden>{c["demo_close"]}</button></div>
  {facts_label(lang)}
</section>'''


def film(lang, dark=False):
    """The trailer comes from our own server: the privacy policy promises nothing loads from elsewhere. Nothing downloads until play is pressed."""
    c = C[lang]
    return f'''<section class="film{" dark" if dark else ""}" id="tanitim" aria-labelledby="film-h">
  <div>
    <span class="label">{c["film_label"]}</span>
    <h2 id="film-h">{c["film_h"]}</h2>
    <p>{c["film_p"]}</p>
    <p class="filmlink"><a href="{PROMO[lang]}" rel="noopener">{c["film_link"]}</a></p>
  </div>
  <div class="device film-d"><video controls playsinline preload="none" poster="/img/sj/{lang}-promo.jpg" width="720" height="1280" aria-label="{c["film_alt"]}"><source src="/media/{lang}-promo.mp4" type="video/mp4"></video></div>
</section>'''


def rules(lang):
    c = C[lang]
    items = "".join(f"<li>{pip_die(i + 1)}<h3>{h}</h3><p>{p}</p></li>" for i, (h, p) in enumerate(c["rules"]))
    return f'<section class="howto" id="kurallar" aria-labelledby="rules-h"><h2 id="rules-h">{c["rules_h"]}</h2><ol>{items}</ol></section>'


def maker(lang):
    c = C[lang]
    rows = "".join(f"<span>{k}: {v}</span>" for k, v in c["maker_rows"])
    return f'''<section class="maker" id="studyo" aria-labelledby="maker-h">
  <div><h2 id="maker-h">{c["maker_h"]}</h2><p>{c["maker_p"]}</p><p class="more-link"><a href="{u("about", lang)}">{c["maker_more"]}</a> · <a href="{u("makingof", lang)}">{T[lang]["making"]}</a></p></div>
  <div class="spec">{rows}<span>{c["write"]}: <a href="mailto:{MAIL}">{MAIL}</a></span></div>
</section>'''


ORG = {"@context": "https://schema.org", "@type": "Organization", "name": "Symbol Interactive", "url": SITE + "/", "logo": SITE + "/img/apple-touch-icon.png", "email": MAIL,
       "foundingDate": "2026", "address": {"@type": "PostalAddress", "addressLocality": "Aydın", "addressCountry": "TR"}}


def home_page(lang):
    c = C[lang]
    other = u("home", "en" if lang == "tr" else "tr")
    badges = "".join(f'<span class="note">{b}</span>' for b in c["badges"])
    html = f'''{head(lang, "Symbol Interactive", c["desc"], "home", ld=ORG)}
<body>
<a class="skip" href="#h">{T[lang]["skip"]}</a>
<main id="main">
<section class="peg" aria-labelledby="h">
  <div class="pack">
    <div class="hook" aria-hidden="true"></div>
    <div class="tab" aria-hidden="true"><div class="slot"></div></div>
    <div class="card">
      {hero_bar(lang, "home", other)}
      <div class="front">
        <div>
          <h1 id="h" tabindex="-1">{c["h1"]}</h1>
          <p class="lede">{c["lede"]}</p>
          <div class="actions"><a class="btn" href="#oyunlar">{c["our_games"]}</a><a class="btn line" href="#dene">{c["play_web"]}</a></div>
          <div class="badges"><span class="age" aria-label="{c["age"]}">13+</span>{badges}</div>
        </div>
        <div class="blisterwrap">
          <div class="burst" aria-hidden="true"><span>{c["burst"][live_i(lang)]}</span></div>
          {blister(lang, zar())}
        </div>
      </div>
      <div class="code" aria-hidden="true"><i></i><span>TÜRKİYE · 2026</span></div>
    </div>
  </div>
</section>
{shelf(lang, play="#dene")}
{film(lang)}
{parts(lang)}
{demo_block(lang)}
{rules(lang)}
{maker(lang)}
</main>
{demo_dialog(lang)}
{footer(lang, other)}
<script src="/site.js" defer></script>
</body>
</html>
'''
    write(PAGES["home"][lang], html)


# ---------------------------------------------------------------- games, about, press

GAMES_TOP = {"tr": ("Oyunlar", ("Şu an yayına hazırlanan bir oyunumuz var; yenileri üzerinde çalışıyoruz.", "Bir oyunumuz yayında; yenileri üzerinde çalışıyoruz.")),
             "en": ("Games", ("One game is getting ready for release; more are in development.", "One game is out; more are in development."))}
GAME_ROWS = {"tr": [("Tür", "Sıralama bulmacası"), ("Platformlar", "iOS ve Android"), ("Diller", f"{GAME['languages']} dil"), ("Hedef kitle", "13 yaş ve üzeri")],
             "en": [("Genre", "Sorting puzzle"), ("Platforms", "iOS and Android"), ("Languages", GAME["languages"]), ("Audience", "Ages 13 and up")]}
HELP_LINKS = {"tr": ("Yardım ve yasal", [("support", "Destek"), ("privacy", "Gizlilik politikası"), ("terms", "Kullanım koşulları"), ("delete", "Hesap silme")]),
              "en": ("Help and legal", [("support", "Support"), ("privacy", "Privacy policy"), ("terms", "Terms of use"), ("delete", "Delete account")])}


def more_links(lang):
    title, links = HELP_LINKS[lang]
    items = "".join(f'<li><a href="{u(k, lang)}">{label}</a></li>' for k, label in links)
    return f'<section class="more" aria-labelledby="more-h"><h2 id="more-h">{title}</h2><ul>{items}</ul></section>'


def games_body(lang):
    h, lede = GAMES_TOP[lang]
    rows = "".join(f"<span>{k}: {v}</span>" for k, v in GAME_ROWS[lang])
    return f'''{shelf(lang, "h1", h, lede[live_i(lang)])}
<div class="gamespec"><div class="spec">{rows}<span>{C[lang]["soon"][live_i(lang)]}</span></div></div>
{more_links(lang)}'''


ABOUT = {
    "tr": {"h1": "Hakkımızda", "lede": "Symbol Interactive, özenle yapılmış, oynayanın kendini iyi hissettiği oyunlar yapan bağımsız bir oyun stüdyosu.",
           "vision_h": "Vizyonumuz", "vision": "Çoğu oyun dikkatini çekmek için bağırıyor. Biz tersini deniyoruz: ilk dokunuşta anlaşılan, her yeni bölümde yeni bir fikir getiren oyunlar. Büyük bir katalog yerine, üzerinde çalışmayı sürdürdüğümüz birkaç oyun.",
           "who_h": "Kim", "who": f"Symbol Interactive 2026’da Türkiye’de kuruldu. Bir şirket unvanı değil, oyunlarımızı yayımladığımız addır. Oyunlarımızdaki kişisel verilerin sorumlusu <a href=\"{u('privacy', 'tr')}\">gizlilik politikasında</a> yazar.",
           "rows": [("Kuruluş", "2026"), ("Adres", "Aydın, Türkiye")], "games": "Oyunlar", "more": "yenileri geliştiriliyor", "contact": "İletişim"},
    "en": {"h1": "About", "lede": "Symbol Interactive is an independent game studio making games with care, games that leave you feeling good.",
           "vision_h": "Our vision", "vision": "Most games shout for your attention. We try the opposite: games you understand at the first touch, with a new idea in every new chapter. A few games we keep working on, rather than a big catalogue.",
           "who_h": "Who", "who": f"Symbol Interactive was founded in Türkiye in 2026. It is not a company name but the name under which our games are published. The controller of the personal data in our games is named in the <a href=\"{u('privacy', 'en')}\">privacy policy</a>.",
           "rows": [("Founded", "2026"), ("Address", "Aydın, Türkiye")], "games": "Games", "more": "more in development", "contact": "Contact"},
}


def about_body(lang):
    a = ABOUT[lang]
    rows = "".join(f"<span>{k}: {v}</span>" for k, v in a["rows"])
    return f'''<div class="reading"><div class="wrap studio-grid">
<article class="prose">
<h1>{a["h1"]}</h1>
<p class="lede">{a["lede"]}</p>
<h2>{a["vision_h"]}</h2>
<p>{a["vision"]}</p>
<h2>{a["who_h"]}</h2>
<p>{a["who"]}</p>
<p class="more-link"><a href="{u("makingof", lang)}">{T[lang]["making"]}</a></p>
</article>
<aside class="studio-side">{zar()}
<div class="spec">{rows}<span>{a["games"]}: <a href="{u("starjars", lang)}">Star Jars Sort Deluxe</a> (iOS, Android); {a["more"]}</span><span>{a["contact"]}: <a href="mailto:{MAIL}">{MAIL}</a></span></div>
</aside>
</div></div>
{rules(lang)}'''


PRESS = {
    "tr": {"h1": "Basın kiti", "lede": "Oyunlarımız hakkında yazacaksan ihtiyacın olan her şey burada. Haber ve inceleme yazılarında bu görselleri kullanabilirsin.",
           "zip": "Hepsini indir", "zip_note": "logolar, ikon, ekran görüntüleri", "logos": "Logo", "logo_y": "Sarı zeminde", "logo_k": "Siyah zeminde", "logo_svg": "Vektör (SVG)", "icon": "Star Jars ikonu",
           "video": "Tanıtım videosu", "video_tr": "Türkçe", "video_en": "İngilizce", "yt": "YouTube", "mp4": "MP4 dosyası",
           "sheet": "Oyun bilgileri", "desc_h": "Kısa tanıtım", "desc": "Star Jars Sort Deluxe, sakin bir renk sıralama bulmacası: renkli yıldızları kavanozlar arasında dök, her kavanozda tek renk kalınca mühürle. Her seviye gerçek bir takımyıldızının bir yıldızını yakar.",
           "rows": [("Oyun", "Star Jars Sort Deluxe (Yıldız Kavanozu)"), ("Geliştirici", "Symbol Interactive"), ("Adres", "Aydın, Türkiye"), ("Tür", "Sıralama bulmacası"), ("Platformlar", "iOS ve Android"),
                    ("İçerik", f"{GAME['levels']} seviye, {GAME['constellations']} gerçek takımyıldızı"), ("Diller", f"{GAME['languages']} dil"), ("Fiyat", "Ücretsiz; reklam ve uygulama içi satın alma içerir")],
           "status": "Durum", "write": "Basın için yaz"},
    "en": {"h1": "Press kit", "lede": "Writing about our games? Everything you need is here. You can use these images in news and reviews.",
           "zip": "Download everything", "zip_note": "logos, icon, screenshots", "logos": "Logo", "logo_y": "On yellow", "logo_k": "On black", "logo_svg": "Vector (SVG)", "icon": "Star Jars icon",
           "video": "Trailer", "video_tr": "Turkish", "video_en": "English", "yt": "YouTube", "mp4": "MP4 file",
           "sheet": "Game facts", "desc_h": "Short description", "desc": "Star Jars Sort Deluxe is a calm colour sort puzzle: pour colourful stars between jars until every jar holds a single colour, then seal it. Every level lights a star of a real constellation.",
           "rows": [("Game", "Star Jars Sort Deluxe"), ("Developer", "Symbol Interactive"), ("Address", "Aydın, Türkiye"), ("Genre", "Sorting puzzle"), ("Platforms", "iOS and Android"),
                    ("Content", f"{GAME['levels']} levels across {GAME['constellations']} real constellations"), ("Languages", GAME["languages"]), ("Price", "Free; contains ads and in-app purchases")],
           "status": "Status", "write": "Press contact"},
}


def press_body(lang):
    p = PRESS[lang]
    zip_path = ROOT / "press" / "symbol-interactive-press-kit.zip"
    size = f" · {zip_path.stat().st_size / 1048576:.0f} MB" if zip_path.exists() else ""
    rows = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in p["rows"]) + f'<dt>{p["status"]}</dt><dd>{C[lang]["soon"][live_i(lang)]}</dd>' + f'<dt>{p["write"]}</dt><dd><a href="mailto:{MAIL}">{MAIL}</a></dd>'
    return f'''<div class="doc single press">
<article class="prose">
<h1>{p["h1"]}</h1>
<p class="lede">{p["lede"]}</p>
<p><a class="btn" href="/press/symbol-interactive-press-kit.zip">{p["zip"]}</a><span class="zipnote">{p["zip_note"]}{size}</span></p>
<h2>{p["logos"]}</h2>
<div class="kit">
  <a class="tile y" href="/press/symbol-interactive-yellow.png"><img src="/img/logo-ink.svg" width="{LOGO_W}" height="{LOGO_H}" alt=""><span>{p["logo_y"]} (PNG)</span></a>
  <a class="tile k" href="/press/symbol-interactive-black.png"><img src="/img/logo-white.svg" width="{LOGO_W}" height="{LOGO_H}" alt=""><span>{p["logo_k"]} (PNG)</span></a>
  <a class="tile" href="/img/logo-ink.svg"><img src="/img/logo-ink.svg" width="{LOGO_W}" height="{LOGO_H}" alt=""><span>{p["logo_svg"]}</span></a>
  <a class="tile sj" href="/press/star-jars-icon.png"><img class="ic" src="/img/sj/icon.jpg" width="256" height="256" alt=""><span>{p["icon"]} (PNG)</span></a>
</div>
<h2>{p["video"]}</h2>
<ul class="vids"><li><strong>{p["video_tr"]}:</strong> <a href="/media/tr-promo.mp4">{p["mp4"]}</a> · <a href="{PROMO["tr"]}" rel="noopener">{p["yt"]}</a></li><li><strong>{p["video_en"]}:</strong> <a href="/media/en-promo.mp4">{p["mp4"]}</a> · <a href="{PROMO["en"]}" rel="noopener">{p["yt"]}</a></li></ul>
<h2>{p["desc_h"]}</h2>
<p>{p["desc"]}</p>
<h2>{p["sheet"]}</h2>
<dl class="sheet">{rows}</dl>
</article>
</div>'''


# ---------------------------------------------------------------- support

SUPPORT = {
    "tr": f'''<h1>Destek</h1>
<p class="lede">Bir sorun mu var, bir önerin mi? {mailto()} adresine yaz.</p>
<p>Oyunun adını, telefonunun modelini, oyunun Ayarlar ekranında görünen sürüm numarasını ve ne olduğunu kısaca anlatırsan daha çabuk yardım edebiliriz.</p>
<h2>İlerlemem nerede saklanıyor?</h2>
<p>Telefonunda. 0.63.0 sürümünden itibaren (test sürümleri dahil) ayrıca bulut kaydında: oyun ilk açılışta senin için anonim bir hesap açar ve ilerlemeni ona kaydeder. Ayarlar → Bulut kaydı'ndan Apple ya da Google hesabını bağlarsan ilerlemen yeni telefonuna da gelir. Daha eski sürümlerde bulut kaydı yoktur; oyunu silersen ilerlemen de silinir.</p>
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
<p>On your phone. From version 0.63.0 (test versions included) also in your cloud save: on first launch the game creates an anonymous account for you and saves your progress to it. Link your Apple or Google account in Settings → Cloud save, and your progress comes with you to a new phone. Earlier versions have no cloud save; deleting the game deletes your progress.</p>
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
        "0.56.0 ve önceki test sürümleri hiçbir kişisel veri toplamaz; 0.62.0'dan itibaren test sürümleri de bu politikaya tabidir."]),
    "en": ("In short", [
        "We never ask for your name, email or phone number to play; the game creates an anonymous account for you.",
        "Your progress is kept on your phone and in a cloud save in Europe (Belgium). You can delete your account in the game at any time.",
        "In Türkiye, the European Economic Area, the UK and Switzerland, analytics and personalised ads run only if you allow them.",
        "If you are under 16 (under 18 in Türkiye), you are not asked for consent; analytics and personalised ads stay off.",
        "Apple and Google handle purchases; we never see your card details. We don't sell your information for money.",
        "Test versions 0.56.0 and earlier collect no personal data; from 0.62.0, test versions follow this policy too."]),
}

PRIVACY = {
    "tr": [
        ("kapsam", "Bu politika neyi kapsar", f'''
<p>Bu politika, Symbol Interactive'in mobil oyunu <strong>Star Jars Sort Deluxe</strong>'ı (Türkçede Yıldız Kavanozu) iOS ve Android'de <strong>0.62.0 sürümünden itibaren (test sürümleri dahil)</strong> kapsar: hangi bilgileri neden işlediğimizi, kimlerin aldığını, ne kadar saklandığını ve haklarını anlatır. 6698 sayılı Kişisel Verilerin Korunması Kanunu (KVKK) kapsamındaki aydınlatma metnimiz ve Avrupa'daki oyuncular için GDPR'ın istediği bilgilendirme budur. Yeni bir oyun yayımladığımızda onun bilgilerini de bu sayfaya ekleriz.</p>
<p><strong>Test sürümleri.</strong> 0.56.0 ve önceki test sürümleri analitik, reklam, hesap ya da bulut kaydı içermez ve bizim için hiçbir kişisel veri toplamaz; ilerleme yalnızca telefonda kalır. 0.62.0'dan itibaren test sürümleri bu politikada anlatılan analitiği (iznine bağlı), çökme raporlarını ve reklamları içerir; bulut kaydı ve hesap bağlama 0.63.0 ile gelir. Bir teste katılırsan seni davet etmek için e-posta adresini kullanırız. Apple ve Google, TestFlight ya da Google Play üzerinden gönderdiğin geri bildirimleri ve test sürümünün çökme raporlarını bize iletebilir; bunları yalnızca hataları düzeltmek için kullanırız.</p>
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
<p><strong>İlk adım sayacı.</strong> Oyunun ilk dakikalarını nasıl geçirdiğini anlamak için, her kurulumdan birkaç adımı (oyunun açılması, tanıtımın bitmesi, ilk seviyelerin kazanılması gibi) birer kez sayarız. Giden bilgi yalnızca adımın adı, işletim sistemi ve oyun sürümüdür; kimlik, reklam kimliği ya da hesap bilgisi gitmez. Saklanan tek şey her gün ve her adım için toplam sayıdır, kim olduğunu gösteren bir kayıt tutulmaz. İsteğin ulaşması için IP adresin Google'ın sunucusuna ulaşır ve sunucu günlüklerinde en çok 30 gün kalabilir; bunu ayrıca kapatmak için çalışıyoruz. Hukuki sebep meşru menfaattir (KVKK m. 5/2-f). AEA, Birleşik Krallık ve İsviçre'de sayaç yalnızca analitik iznini verdikten sonra çalışır; 13 yaşından küçük olduğunu bildirdiysen çalışmaz.</p>
<p><strong>Gökyüzü Penceresi.</strong> Gökyüzü Penceresi'nde kamerayı açarsan görüntü yalnızca yıldızların arkasında, telefonunun ekranında gösterilir: kaydetmeyiz, işlemeyiz, telefonundan çıkmaz. Kamera izni yalnızca kamera düğmesine bastığında sorulur; vermesen de pencere kamerasız çalışır. Konum izni istemeyiz: şehrini telefonun saat diliminden tahmin ederiz ya da listeden sen seçersin, seçimin yalnızca bu telefonda kalır, bulut kaydına girmez ve bize gelmez. Telefonun yönünü, gökyüzünü ekranda döndürmek için o an telefonda kullanırız; saklanmaz, gönderilmez. Gök olayı hatırlatmaları (meteor yağmuru, tutulma) telefonunda zamanlanır, bize bir şey gelmez; Ayarlar → Bildirimler kapalıysa ya da 13 yaşından küçük olduğunu bildirdiysen zamanlanmaz.</p>
<p><strong>Bildirimler.</strong> Telefonun bildirim iznini verdiysen ve Ayarlar → Bildirimler açıksa, oyundan haber ve etkinlik bildirimleri göndermek için Firebase Cloud Messaging kullanırız. Bunun için Firebase, oyunun bu kurulumuna özgü bir bildirim belirteci oluşturur. Bu belirteci bir oyuncu listesinde tutmayız: bildirimler herkese ve dile göre konulara gider. Bildirimleri Ayarlar'dan kapatınca konulardan çıkarsın ve belirteç silinir. 13 yaşından küçük olduğunu bildiğimiz oyunculara bildirim göndermeyiz.</p>
<p><strong>Saat kontrolü.</strong> Günlük ödüllerin saatini doğrulamak için oyun, ara sıra bu sitenin sunucusuna, ulaşamazsa Google'ın Firebase sunucusuna kısa bir istek gönderir ve yalnızca yanıttaki saati okur. Bu istekte oyuncu kimliği ya da hesap bilgisi yoktur. İstek sırasında sunucu, her internet bağlantısında olduğu gibi IP adresini görür; bunu oyuncuyla eşleştirmeyiz.</p>
<p><strong>Yeni bölümler.</strong> Oyun, yeni takımyıldızı bölümlerini indirmek için ara sıra (en çok 6 saatte bir) Google'ın Firebase Hosting sunucusuna kısa bir istek gönderir. İndirilen yalnızca oyun içeriğidir: seviyeler, yazılar ve resimler. Bu istekte oyuncu kimliği ya da hesap bilgisi yoktur. İstek sırasında sunucu, her internet bağlantısında olduğu gibi IP adresini görür; bunu oyuncuyla eşleştirmeyiz.</p>
<h3>Arkadaşlar ve sıralama</h3>
<p>Arkadaşlar'ı ya da günün bulmacasının sıralamasını açmadıkça bu bölümdeki hiçbir bilgi gönderilmez. İlk açtığında hesabına bağlı bir arkadaş profili oluştururuz. Profilde Yıldız Kodun, hazır listeden seçtiğin takma adın, avatarın, seviyen, yıldız sayın, seviye başına en iyi hamle sayıların, en son oynadığın gün, arkadaş listen, gönderdiğin ve aldığın arkadaşlık istekleri, gönderdiğin ve aldığın canlar, engellediğin oyuncular, seni davet eden oyuncu, davet ödülün ve son günlerde günün bulmacasındaki hamle ve deneme sayıların bulunur. Kayıt, bulut kaydınla aynı yerde (europe-west1) saklanır.</p>
<p>Arkadaşların takma adını, avatarını, seviyeni, yıldızlarını, seviye başına en iyi hamlelerini, en son oynadığın günü ve günün bulmacası sonucunu görür. Bir arkadaş eklemek için Yıldız Kodunu bilmek gerekir ve eklenen oyuncu isteği kabul etmedikçe arkadaş olunmaz. Görünür ol'u kapatırsan arkadaşların yalnızca takma adını ve avatarını görür, kodunla seni kimse ekleyemez ve dünya sıralamasında görünmezsin: bugünün sıralamasındaki satırın hemen silinir, eski günlerin satırları en geç 7 gün içinde kalkar. Dünya sıralamasında oyuncular birbirinin takma adını, avatarını, hamle ve deneme sayısını görür. Serbest yazılan ad, sohbet ya da mesaj yoktur. İstediğin zaman bir arkadaşını çıkarabilir ya da engelleyebilir, Ayarlar'dan Arkadaşlar'ı kapatabilirsin.</p>
<p>13 yaşından küçük olduğunu söyleyen oyuncular için bu özellikler kapalıdır ve bu bilgiler hiç oluşmaz.</p>
<h3>İzin tercihlerin</h3>
<p>Verdiğin ya da vermediğin izinler telefonunda saklanır; böylece her açılışta yeniden sorulmaz ve reklam ortaklarına iletilebilir.</p>
<h3>Destek yazışmaları</h3>
<p>Bize e-posta yazarsan, adresini ve mesajını yalnızca cevap vermek ve isteğini yerine getirmek için kullanırız.</p>'''),
        ("hukuki-sebepler", "Hangi hukuki sebeple", table("Her amacın hukuki sebebi", ["Amaç", "KVKK", "GDPR (AEA, Birleşik Krallık, İsviçre)"], [
            ("Hesap, bulut kaydı, satın almalar ve geri yükleme", "Sözleşmenin kurulması ve ifası (m. 5/2-c)", "Sözleşme (m. 6/1-b)"),
            ("Arkadaşlar ve günün bulmacasının sıralaması", "Sözleşmenin ifası (m. 5/2-c)", "Sözleşme (m. 6/1-b)"),
            ("Destek yazışmaları ve hak başvuruları", "Sözleşmenin ifası; hukuki yükümlülük (m. 5/2-c, ç)", "Sözleşme; hukuki yükümlülük (m. 6/1-b, c)"),
            ("Analitik", "Açık rıza (m. 5/1)", "Rıza (m. 6/1-a)"),
            ("Kişiselleştirilmiş reklam", "Açık rıza (m. 5/1)", "Rıza (m. 6/1-a), Google'ın rıza mesajıyla"),
            ("Reklamların gösterilmesi, sayılması, dolandırıcılığın önlenmesi", "Meşru menfaat (m. 5/2-f)", "Meşru menfaat (m. 6/1-f); telefona bilgi yazılması ve okunması rıza mesajındaki seçimine göre"),
            ("Çökme raporları", "Meşru menfaat (m. 5/2-f)", "Rıza (m. 6/1-a)"),
            ("Uzaktan ayarlar", "Meşru menfaat (m. 5/2-f)", "Meşru menfaat (m. 6/1-f)"),
            ("Sunucu istek kayıtları: hataları ve kötüye kullanımı incelemek", "Meşru menfaat (m. 5/2-f)", "Meşru menfaat (m. 6/1-f)"),
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
<li><strong>Google</strong> (Google LLC ve bağlı şirketleri). Firebase Authentication, Cloud Firestore, Cloud Messaging, Crashlytics, Remote Config ve Analytics'te Google, bilgileri bizim adımıza ve talimatımızla işleyen <strong>veri işleyendir</strong>. AdMob'da ve Google Play'de Google, bilgileri kendi amaçları için de kullanan ayrı bir <strong>veri sorumlusudur</strong>. <a href="https://policies.google.com/privacy">Google Gizlilik Politikası</a>, <a href="https://firebase.google.com/support/privacy">Firebase'de gizlilik</a>, <a href="https://policies.google.com/technologies/partner-sites">Google'ın, hizmetlerini kullanan uygulamalardan gelen bilgileri nasıl kullandığı</a>.</li>
<li><strong>Unity</strong> (Unity Technologies ve bağlı şirketleri; ironSource bir Unity şirketidir): LevelPlay, Unity Ads ve ironSource Ads. Unity, reklam verilerinin ayrı bir veri sorumlusudur. <a href="https://unity.com/legal/game-player-and-app-user-privacy-policy">Unity'nin oyuncu ve uygulama kullanıcısı gizlilik politikası</a>.</li>
<li><strong>Apple</strong> (Apple Inc. ve bağlı şirketleri): App Store, satın almalar ve Apple ile Giriş; Apple ayrı bir veri sorumlusudur. <a href="https://www.apple.com/legal/privacy/">Apple Gizlilik Politikası</a>.</li>
</ul>
<p><strong>Diğer oyuncular.</strong> Arkadaşlar'ı ya da sıralamayı kullanırsan, yukarıdaki "Arkadaşlar ve sıralama" bölümünde yazılı bilgilerini arkadaşların ve sıralamadaki oyuncular görür. Bu bilgilerle gerçek adın, e-postan ya da oyuncu kimliğin onlara gitmez.</p>
<p>Bir yasa ya da yetkili bir makamın kararı gerektirirse bilgileri yetkili kurum ve kuruluşlarla da paylaşırız.</p>'''),
        ("yurt-disi", "Yurt dışına aktarım", '''
<p>Bilgilerin Türkiye dışında işlenir: bulut kaydın Avrupa Birliği'nde (Belçika), hesap kaydın (Firebase Authentication) Amerika Birleşik Devletleri'nde; analitik, çökme raporları, uzaktan ayarlar ve reklam verileri Google'ın ve Unity'nin başta ABD olmak üzere çeşitli ülkelerdeki sunucularında. Bu aktarımlar yukarıda yazılan amaçlarla ve yalnızca yukarıdaki şirketlere yapılır. Türkiye'den yurt dışına aktarım KVKK'nın 9. maddesine tabidir.</p>
<p>AEA'daki, Birleşik Krallık'taki ve İsviçre'deki oyuncular için ABD'ye aktarımlar, alıcı sertifikalıysa (Google gibi) AB-ABD Veri Gizliliği Çerçevesi'ne ve onun Birleşik Krallık ve İsviçre uzantılarına, değilse (Unity gibi) Avrupa Komisyonu'nun standart sözleşme hükümlerine dayanır. Bu güvencelerin bir kopyasını bize yazarak isteyebilirsin.</p>'''),
        ("saklama", "Ne kadar saklıyoruz", '''
<ul>
<li><strong>Hesap ve bulut kaydı:</strong> sen silene kadar. Oyun bir hesapla 24 ay boyunca hiç açılmazsa o hesabı ve bulut kaydını biz sileriz.</li>
<li><strong>Arkadaş profili:</strong> hesabınla birlikte silinir. Gelen canlar 7 gün sonra geçersiz olur; yanıtlanmayan arkadaşlık istekleri 30 gün, reddedilenler 7 gün sonra. Kayıtları, oyunu bir sonraki açışında silinir.</li>
<li><strong>Günün bulmacası sıralaması:</strong> 7 gün.</li>
<li><strong>Hesapların IP kayıtları:</strong> birkaç hafta.</li>
<li><strong>Sunucu istek kayıtları:</strong> oyunun sunucumuza gönderdiği isteklerde (ilk adım sayacı, arkadaşlar ve sıralama, hesap silme) IP adresin, cihaz ve uygulama bilgisini gösteren user agent satırı ve isteğin zamanı Google'ın sunucu günlüklerinde en çok 30 gün kalabilir. Bu kayıtlara isteğin içeriğini ve hesap kimliğini yazmayız; onları yalnızca hataları ve kötüye kullanımı incelemek için kullanırız.</li>
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
<p>This policy covers Symbol Interactive's mobile game <strong>Star Jars Sort Deluxe</strong> (Yıldız Kavanozu in Turkish) on iOS and Android <strong>from version 0.62.0 (test versions included)</strong>: what information it processes and why, who receives it, how long it is kept and what your rights are. It is our privacy notice under Türkiye's Personal Data Protection Law No. 6698 (KVKK) and the information the GDPR requires for players in Europe. When we release a new game, we add its details to this page.</p>
<p><strong>Test versions.</strong> Test versions 0.56.0 and earlier have no analytics, ads, account or cloud save and collect no personal data for us; progress stays on the phone. From 0.62.0, test versions include the analytics (with your consent), crash reports and ads described in this policy; cloud save and account linking arrive with 0.63.0. If you join a test, we use your email address to invite you. Apple and Google may pass on feedback you send through TestFlight or Google Play and crash reports from test versions; we use them only to fix bugs.</p>
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
<p><strong>First-steps counter.</strong> To understand how the game's first minutes go, we count a few steps once per installation (the game opening, the tour ending, the first levels being won). Only the step's name, the operating system and the game version are sent, with no ID, advertising ID or account details. All we keep is a total per day and step, with no record of who anyone is. For the request to arrive, your IP address reaches Google's server and may stay in its server logs for up to 30 days; we are working on switching this off as well. The legal basis is legitimate interest. In the EEA, the UK and Switzerland the counter only runs after you allow analytics, and it does not run if you told us you are under 13.</p>
<p><strong>Sky window.</strong> If you turn on the camera in the sky window, the picture is only shown behind the stars on your phone's screen: we don't save it or process it, and it doesn't leave your phone. The camera permission is asked only when you tap the camera button; without it the window works with no camera. We don't ask for your location: we guess your city from your phone's time zone or you pick one from a list, and your choice stays on this phone, out of the cloud save, and never reaches us. Your phone's direction is used on the phone at that moment to turn the sky on the screen; it isn't kept or sent. Sky event reminders (meteor showers, eclipses) are scheduled on your phone and nothing reaches us; they aren't scheduled if Settings → Notifications is off or you told us you're under 13.</p>
<p><strong>Notifications.</strong> If you allowed notifications on your phone and Settings → Notifications is on, we use Firebase Cloud Messaging to send news and events from the game. For this, Firebase creates a notification token unique to this installation of the game. We do not keep this token in a list of players: notifications go to topics, for everyone and by language. Turning notifications off in Settings takes you off the topics and deletes the token. We do not send notifications to players we know are under 13.</p>
<p><strong>Clock check.</strong> To check the time for daily rewards, the game now and then sends a short request to this site's server or, if it can't reach it, to Google's Firebase server, and reads only the time in the answer. The request carries no player ID or account details. As with any internet connection, the server sees the IP address during the request; we don't match it to a player.</p>
<p><strong>New chapters.</strong> To download new constellation chapters, the game now and then (at most every 6 hours) sends a short request to Google's Firebase Hosting server. What it downloads is game content only: levels, words and pictures. The request carries no player ID or account details. As with any internet connection, the server sees your IP address during the request; we don't match it to a player.</p>
<h3>Friends and the ranking</h3>
<p>Nothing in this section is sent unless you open Friends or the daily puzzle's ranking. The first time you do, we create a friends profile tied to your account. It holds your star code, the nickname you picked from a preset list, your avatar, your level, your star count, your best move count per level, the last day you played, your friends list, the friend requests you sent and received, the lives you sent and received, the players you blocked, the player who invited you and your invite reward, and your moves and tries in the daily puzzle over the last few days. It is stored in the same place as your cloud save (europe-west1).</p>
<p>Your friends see your nickname, avatar, level, stars, best moves per level, the last day you played and your daily puzzle result. Adding a friend takes your star code, and nobody becomes a friend until the other player accepts. If you turn off Visible to others, friends see only your nickname and avatar, nobody can add you by your code, and you don't appear on the world ranking: your line on today's ranking is deleted at once, and lines on earlier days go within 7 days. On the world ranking, players see each other's nickname, avatar, moves and tries. There are no typed names, no chat and no messages. You can remove or block a friend at any time, and turn Friends off in Settings.</p>
<p>These features are off for players who say they are under 13, and none of this information is created for them.</p>
<h3>Your consent choices</h3>
<p>The permissions you give or refuse are stored on your phone, so that you aren't asked at every launch and so that they can be passed on to ad partners.</p>
<h3>Support emails</h3>
<p>If you write to us, we use your address and message only to answer you and carry out your request.</p>'''),
        ("legal-bases", "Legal bases", table("The legal basis for each purpose", ["Purpose", "KVKK", "GDPR (EEA, UK, Switzerland)"], [
            ("Account, cloud save, purchases and restoring them", "Entering into and performing a contract (Art. 5(2)(c))", "Contract (Art. 6(1)(b))"),
            ("Friends and the daily puzzle's ranking", "Performing a contract (Art. 5(2)(c))", "Contract (Art. 6(1)(b))"),
            ("Support emails and rights requests", "Performing a contract; legal obligation (Art. 5(2)(c), (ç))", "Contract; legal obligation (Art. 6(1)(b), (c))"),
            ("Analytics", "Explicit consent (Art. 5(1))", "Consent (Art. 6(1)(a))"),
            ("Personalised ads", "Explicit consent (Art. 5(1))", "Consent (Art. 6(1)(a)), through Google's consent message"),
            ("Showing and counting ads, preventing fraud", "Legitimate interests (Art. 5(2)(f))", "Legitimate interests (Art. 6(1)(f)); storing and reading information on the phone follows your choice in the consent message"),
            ("Crash reports", "Legitimate interests (Art. 5(2)(f))", "Consent (Art. 6(1)(a))"),
            ("Remote settings", "Legitimate interests (Art. 5(2)(f))", "Legitimate interests (Art. 6(1)(f))"),
            ("Server request logs: looking into errors and abuse", "Legitimate interests (Art. 5(2)(f))", "Legitimate interests (Art. 6(1)(f))"),
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
<li><strong>Google</strong> (Google LLC and its affiliates). For Firebase Authentication, Cloud Firestore, Cloud Messaging, Crashlytics, Remote Config and Analytics, Google is our <strong>processor</strong>, acting on our behalf and instructions. For AdMob and Google Play, Google is a separate <strong>controller</strong> that also uses information for its own purposes. <a href="https://policies.google.com/privacy">Google Privacy Policy</a>, <a href="https://firebase.google.com/support/privacy">Privacy and security in Firebase</a>, <a href="https://policies.google.com/technologies/partner-sites">How Google uses information from sites or apps that use its services</a>.</li>
<li><strong>Unity</strong> (Unity Technologies and its affiliates; ironSource is a Unity company): LevelPlay, Unity Ads and ironSource Ads. Unity is a separate controller of ad data. <a href="https://unity.com/legal/game-player-and-app-user-privacy-policy">Unity Game Player and App User Privacy Policy</a>.</li>
<li><strong>Apple</strong> (Apple Inc. and its affiliates): the App Store, purchases and Sign in with Apple; Apple is a separate controller. <a href="https://www.apple.com/legal/privacy/">Apple Privacy Policy</a>.</li>
</ul>
<p><strong>Other players.</strong> If you use Friends or the ranking, your friends and the players on the ranking see the information listed under "Friends and the ranking" above. Your real name, email and player ID do not go to them.</p>
<p>If a law or a decision of a competent authority requires it, we also share information with the competent authorities.</p>'''),
        ("transfers", "Transfers abroad", '''
<p>Your information is processed outside Türkiye: your cloud save in the European Union (Belgium), your account record (Firebase Authentication) in the United States, and analytics, crash reports, remote settings and ad data on Google's and Unity's servers in several countries, mainly the United States. These transfers are made for the purposes above and only to the companies above. Transfers from Türkiye are subject to Article 9 of the KVKK.</p>
<p>For players in the EEA, the UK and Switzerland, transfers to the United States rely on the EU-US Data Privacy Framework and its UK and Swiss extensions where the recipient is certified (such as Google), and otherwise on the European Commission's standard contractual clauses (such as Unity). You can ask us for a copy of these safeguards.</p>'''),
        ("retention", "How long we keep it", '''
<ul>
<li><strong>Account and cloud save:</strong> until you delete them. If the game isn't opened with an account for 24 months, we delete that account and its cloud save.</li>
<li><strong>Friends profile:</strong> deleted with your account. Lives waiting for you stop being valid after 7 days, unanswered friend requests after 30 days and declined ones after 7. Their records are deleted the next time you open the game.</li>
<li><strong>Daily puzzle ranking:</strong> 7 days.</li>
<li><strong>Account IP logs:</strong> a few weeks.</li>
<li><strong>Server request logs:</strong> for the requests the game sends to our server (the first-steps counter, friends and the ranking, deleting an account), your IP address, a user agent line showing device and app details, and the time of the request may stay in Google's server logs for up to 30 days. We don't write the request's content or your account ID to these logs, and we use them only to look into errors and abuse.</li>
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
<p>Oyunları Symbol Interactive adıyla bireysel bir geliştirici geliştirir ve yayımlar (Aydın, Türkiye; {mailto()}); kimliği <a href="{u("privacy", "tr")}">gizlilik politikasında</a> yazar. Bu koşullarda "biz" bu geliştiriciyi anlatır.</p>
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
<p>The games are made and published as Symbol Interactive by an individual developer (Aydın, Türkiye; {mailto()}), identified in the <a href="{u("privacy", "en")}">privacy policy</a>. "We" in these terms means that developer.</p>
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
<li><strong>Arkadaş profilin:</strong> Yıldız Kodun, takma adın, arkadaş listen, gelen canların ve engellediğin oyuncular; arkadaşlarının listesinden de çıkarsın. Bugünün sıralamasındaki satırın da silinir; eski günlerin satırları en geç 7 gün içinde kalkar.</li>
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
<li><strong>Your friends profile:</strong> your star code, nickname, friends list, waiting lives and blocked players; you also leave your friends' lists. Your line on today's ranking goes too, and lines from earlier days go within 7 days.</li>
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

# Launch day: set "live" to True, run build.py, push. /starjars and the demo's end screen (via /demo/stores.js) then show the store links.
# The demo itself (demo/starjars.html) is built by ~/.cache/star-jars-tools/ads/playable2/build_web.py and only reads this.
STORES = {"live": False, "ios": "https://apps.apple.com/app/id6830266206", "android": "https://play.google.com/store/apps/details?id=com.symbolinteractive.starjars"}

# The wrapped box on the shelf. On the day a game is announced, set this, run build.py, push: the wrapping comes off and the line under Star Jars names it.
# This repo is public, so a name goes here only once it is announced. Shape: {"name": "...", "tr": "bir cümle", "en": "one line", "url": "/... or https://...", "steam": "https://store.steampowered.com/app/..."}; url and steam are optional.
NEXT_GAME = None
NEXT_SOON = {"tr": "Sıradaki kutu", "en": "The next box"}
NEXT_STEAM = {"tr": "Steam’de istek listene ekle", "en": "Wishlist it on Steam"}

# ---------------------------------------------------------------- the game's own box

STARJARS = {
    "tr": {"title": "Star Jars Sort Deluxe · Yıldız Kavanozu", "desc": "Star Jars Sort Deluxe (Yıldız Kavanozu): yıldızları ayır, takımyıldızlarını yak. Symbol Interactive’in sakin bulmaca oyunu.",
           "alt": "Yıldız Kavanozu", "lede": "Gece göğünün altında sakin bir renk sıralama bulmacası. Yıldızları sırala, kavanozları mühürle, gerçek takımyıldızlarını yak.",
           "burst": ("Yakında!", "Çıktı!"), "say": "Bir yıldız daha!", "notes": ["Süre yok, acele yok", "İnternetsiz oynanır"], "by": "Bir Symbol Interactive oyunu", "jar": "Yıldızlarla dolu cam kavanozlar",
           "code": f"{GAME['levels']} SEVİYE · {GAME['languages']} DİL"},
    "en": {"title": "Star Jars Sort Deluxe", "desc": "Star Jars Sort Deluxe: sort the stars, light up the constellations. A calm puzzle game by Symbol Interactive.",
           "alt": "A calm sorting puzzle", "lede": "A calm colour sort puzzle under the night sky. Sort stars, seal jars and light up real constellations.",
           "burst": ("Coming<br>soon!", "Out<br>now!"), "say": "One more star!", "notes": ["No timers, no rush", "Plays offline"], "by": "A Symbol Interactive game", "jar": "Glass jars full of stars",
           "code": f"{GAME['levels']} LEVELS · {GAME['languages']} LANGUAGES"},
}


def starjars_page(lang):
    t, c = STARJARS[lang], C[lang]
    other = u("starjars", "en" if lang == "tr" else "tr")
    notes = "".join(f'<span class="note">{n}</span>' for n in t["notes"])
    ld = {"@context": "https://schema.org", "@type": "MobileApplication", "name": "Star Jars Sort Deluxe", "operatingSystem": "iOS, Android", "applicationCategory": "GameApplication",
          "description": t["desc"], "url": SITE + u("starjars", lang), "image": SITE + "/img/sj/icon.jpg", "author": {"@type": "Organization", "name": "Symbol Interactive", "url": SITE + "/"},
          "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}}
    inside = f'<img class="inside" src="/img/sj/jar.png" width="512" height="512" alt="{t["jar"]}">'
    say = c["say"]
    c_say = blister(lang, inside, ' style="color:#111"').replace(say, t["say"])
    html = f'''{head(lang, t["title"], t["desc"], "starjars", favicon="/img/starjars-icon.svg", theme="#2A1A78", og=f"/img/og-starjars-{lang}.jpg", ld=ld)}
<body>
<a class="skip" href="#title">{T[lang]["skip"]}</a>
<main id="main">
<section class="peg" aria-labelledby="title">
  <div class="pack">
    <div class="hook" aria-hidden="true"></div>
    <div class="tab sjt" aria-hidden="true"><div class="slot"></div></div>
    <div class="card sjc">
      {hero_bar(lang, "starjars", other, "yellow")}
      <div class="front">
        <div>
          <span class="label">{t["alt"]}</span>
          <h1 id="title" tabindex="-1">Star Jars</h1>
          <div class="subt">Sort Deluxe</div>
          <p class="lede">{t["lede"]}</p>
          <div class="actions"><a class="btn gold" href="#dene">{PLAY_ICON}{c["play_web"]}</a>{store_buttons(lang)}</div>
          <div class="badges"><span class="age" aria-label="{c["age"]}">13+</span>{notes}<a class="maker-stamp" href="{u("home", lang)}">{zar()}{t["by"]}</a></div>
        </div>
        <div class="blisterwrap">
          <div class="burst" aria-hidden="true"><span>{t["burst"][live_i(lang)]}</span></div>
          {c_say}
        </div>
      </div>
      <div class="code" aria-hidden="true"><i></i><span>{t["code"]}</span></div>
    </div>
  </div>
</section>
{demo_block(lang, gold=True)}
{film(lang, dark=True)}
{parts(lang, night=True)}
{learn(lang)}
{more_links(lang)}
</main>
{demo_dialog(lang)}
{footer(lang, other)}
<script src="/site.js" defer></script>
</body>
</html>
'''
    write(PAGES["starjars"][lang], html)


NOT_FOUND = f'''<div class="empty">
{zar("asleep")}
<div>
<h1>Bu kutu boş</h1>
<p class="lede">Adres yanlış yazılmış ya da sayfa taşınmış olabilir.</p>
<div class="actions"><a class="btn" href="/">Ana sayfaya dön</a><a class="btn line" href="/destek.html">Destek</a></div>
<div lang="en" class="lang-block">
<h2>This box is empty</h2>
<p>The address may be mistyped, or the page may have moved.</p>
<div class="actions"><a class="btn" href="/en/">Go to the home page</a><a class="btn line" href="/en/support.html">Support</a></div>
</div>
</div>
</div>'''

# ---------------------------------------------------------------- the game's guides. Their words and numbers come from the game (data/game.json), so the site never says something the game doesn't.

def label_tile(src, alt=""):
    return f'<div class="gpic"><img src="{src}" width="560" height="560" alt="{alt}" loading="lazy"></div>'


def pagehead(label, title, lede, art="", chips=(), night=False):
    links = ""
    if chips:
        links = '<ul class="chips">' + "".join(f'<li><a href="{href}">{text}</a></li>' for href, text in chips) + "</ul>"
    pic = f'<img class="headart" src="{art}" width="560" height="560" alt="" loading="lazy">' if art else ""
    return f'<section class="pagehead{" night" if night else ""}"><div><span class="label">{label}</span><h1>{title}</h1><p class="lede">{lede}</p>{links}</div>{pic}</section>'


def try_strip(lang):
    """Every guide ends the same way: go and play it."""
    c = C[lang]
    return (f'<section class="trystrip"><div><h2>{TRY_STRIP[lang][0]}</h2><p>{TRY_STRIP[lang][1]}</p></div>'
            f'<div class="actions"><a class="btn" href="{u("starjars", lang)}#dene">{PLAY_ICON}{c["play_web"]}</a><a class="btn line" href="{u("starjars", lang)}">{c["game_page"]}</a></div></section>')


TRY_STRIP = {"tr": ("Okumak yetmez", "İki bölümü şimdi tarayıcında oyna. İndirme yok, hesap yok."), "en": ("Reading isn’t enough", "Play two boards in your browser now. No download, no account.")}

# ---- what's new

NEWS = {
    "tr": {"title": "Yenilikler", "desc": "Star Jars Sort Deluxe’e eklenen takımyıldızları, uzay bölümleri ve özellikler. En yenisi en üstte.", "lede": "Star Jars yayına hazırlanırken oyuna neler eklendi? En yenisi en üstte.", "version": "Sürüm"},
    "en": {"title": "What’s new", "desc": "The constellations, space chapters and features added to Star Jars Sort Deluxe, newest first.", "lede": "What has been added to Star Jars as it gets ready for release? Newest first.", "version": "Version"},
}
# A line that names something the guides explain links to it.
NEWS_LINKS = {"whatsnew.053.cygnus": "sky:cygnus", "whatsnew.054.cancer": "sky:cancer", "whatsnew.055.aquila": "sky:aquila", "whatsnew.057.lyra": "sky:lyra", "whatsnew.andromeda.chapter": "sky:andromeda",
              "whatsnew.054.space": "guide#uzay", "whatsnew.055.space": "guide#uzay", "whatsnew.057.space": "guide#uzay", "whatsnew.andromeda.space": "guide#uzay", "whatsnew.6i.space": "guide#uzay",
              "whatsnew.bossrules.new": "guide#bolum-kavanozlari"}


def news_body(lang):
    n = NEWS[lang]
    batches = ""
    for batch in GAMEDATA["news"]:
        lines = ""
        for line in batch["lines"]:
            text = esc(line[lang])
            target = NEWS_LINKS.get(line["key"])
            if target:
                key, _, anchor = target.partition("#")
                text = f'<a href="{u(key, lang)}{"#" + anchor if anchor else ""}">{text}</a>'
            lines += f"<li>{text}</li>"
        batches += f'<li class="batch"><h2><small>{n["version"]}</small>{batch["version"]}</h2><ul>{lines}</ul></li>'
    return f'{pagehead("Star Jars Sort Deluxe", n["title"], n["lede"], "/img/guide/comet.webp")}<section class="newslist"><ol>{batches}</ol></section>{try_strip(lang)}'


# ---- the jars and the rules

GUIDE = {
    "tr": {"title": "Kavanoz ve kural rehberi", "seo": "Star Jars kavanoz ve kural rehberi", "desc": "Star Jars Sort Deluxe’teki her kavanoz, yıldız türü, bölüm kavanozu ve uzay bölümü kuralı, tek sayfada.", "label": "Kutudan çıkan kılavuz",
           "lede": "Star Jars’ta karşına çıkacak her kavanoz, her yıldız ve her kural, oyunun kendi sözleriyle.",
           "basic_h": "Temel kural", "basic": [("pour", "Dök", "Bir kavanoza, sonra başka birine dokun. En üstteki aynı renk yıldızlar oraya geçer. Hedef ya boş olmalı ya da en üstünde aynı renk bulunmalı."),
                                                ("sort", "Ayır", "Her rengin kendi şekli var. Bir kavanozda tek renk kalana kadar sırala. Takılırsan hamleni geri alabilir ya da ipucu isteyebilirsin."),
                                                ("seal", "Mühürle", "Tek renkle dolan kavanoz mühürlenir. Her kavanoz mühürlü ya da boş kalınca seviye biter ve takımyıldızının bir yıldızı yanar.")],
           "jars_h": "Kavanozlar", "jars_p": "Yeni bir kavanoz ilk çıktığında oyun onu sana tanıtır. Hepsi burada bir arada.",
           "stars_h": "Yıldızlar ve kurallar", "stars_p": "Bazı yıldızlar ve seviyeler ek bir kuralla gelir.",
           "boss_h": "Bölüm kavanozları", "boss_p": "Her takımyıldızı, ona özel çizilmiş büyük bir kavanozla biter. Bazılarının kendi kuralı vardır.",
           "space_h": "Uzay bölümleri", "space_p": "Haritada ilerledikçe açılan özel bölümler. Her biri gerçek bir gök cismini anlatır ve kendi kuralıyla gelir.", "real": "Gerçekte"},
    "en": {"title": "Jar and rule guide", "seo": "Star Jars jar and rule guide", "desc": "Every jar, star type, chapter jar and space chapter rule in Star Jars Sort Deluxe, on one page.", "label": "The leaflet in the box",
           "lede": "Every jar, every star and every rule you’ll meet in Star Jars, in the game’s own words.",
           "basic_h": "The basic rule", "basic": [("pour", "Pour", "Tap a jar, then another. The matching stars on top move across. The target must be empty or have the same colour on top."),
                                                  ("sort", "Sort", "Every colour has its own shape. Sort until a jar holds a single colour. If you get stuck, undo a move or ask for a hint."),
                                                  ("seal", "Seal", "A jar full of one colour seals. When every jar is sealed or empty, the level ends and a star of the constellation lights up.")],
           "jars_h": "Jars", "jars_p": "The game introduces each new jar the first time it appears. Here they all are together.",
           "stars_h": "Stars and rules", "stars_p": "Some stars and levels come with an extra rule.",
           "boss_h": "Chapter jars", "boss_p": "Every constellation ends with a big jar drawn just for it. Some have a rule of their own.",
           "space_h": "Space chapters", "space_p": "Special chapters that open as you travel the map. Each tells of a real object in the sky and brings its own rule.", "real": "In reality"},
}


def guide_cards(lang, items):
    return "".join(f'<article class="gcard">{label_tile("/img/guide/" + i["key"] + ".webp")}<h3>{esc(i["title"][lang])}</h3><p>{esc(i["line"][lang])}</p></article>' for i in items)


def guide_body(lang):
    g, d = GUIDE[lang], GAMEDATA["guide"]
    chips = [("#temel", g["basic_h"]), ("#kavanozlar", g["jars_h"]), ("#yildizlar", g["stars_h"]), ("#bolum-kavanozlari", g["boss_h"]), ("#uzay", g["space_h"])]
    steps = "".join(f'<li>{label_tile("/img/guide/" + key + ".webp")}<div>{pip_die(i + 1)}<h3>{h}</h3><p>{p}</p></div></li>' for i, (key, h, p) in enumerate(g["basic"]))
    space = "".join(f'<article class="scard"><img src="/img/guide/{i["key"]}.webp" width="560" height="560" alt="" loading="lazy"><div><span class="label">{esc(i["object"][lang])}</span><h3>{esc(i["title"][lang])}</h3>'
                    f'<p class="rule">{esc(i["line"][lang])}</p><p><b>{g["real"]}:</b> {esc(i["fact"][lang])}</p></div></article>' for i in d["space"])
    return f'''{pagehead(g["label"], g["title"], g["lede"], "/img/guide/ice.webp", chips)}
<section class="gsec" id="temel" aria-labelledby="temel-h"><h2 id="temel-h">{g["basic_h"]}</h2><ol class="gsteps">{steps}</ol></section>
<section class="gsec cream" id="kavanozlar" aria-labelledby="jars-h"><h2 id="jars-h">{g["jars_h"]}</h2><p class="intro">{g["jars_p"]}</p><div class="gcards">{guide_cards(lang, d["jars"])}</div></section>
<section class="gsec" id="yildizlar" aria-labelledby="stars-h"><h2 id="stars-h">{g["stars_h"]}</h2><p class="intro">{g["stars_p"]}</p><div class="gcards">{guide_cards(lang, d["stars"])}</div></section>
<section class="gsec gold" id="bolum-kavanozlari" aria-labelledby="boss-h"><h2 id="boss-h">{g["boss_h"]}</h2><p class="intro">{g["boss_p"]}</p><div class="gcards">{guide_cards(lang, d["bosses"])}</div></section>
<section class="gsec night" id="uzay" aria-labelledby="space-h"><h2 id="space-h">{g["space_h"]}</h2><p class="intro">{g["space_p"]}</p><div class="scards">{space}</div></section>
{try_strip(lang)}'''


# ---- the sky

SKYT = {
    "tr": {"title": "Gökyüzü rehberi", "seo": "Gökyüzü rehberi: takımyıldızları nasıl bulunur?", "label": "Star Jars · Gökyüzü rehberi",
           "desc": "Star Jars’taki gerçek takımyıldızları: nasıl bulunur, en iyi ne zaman görünür, hangi efsaneyi anlatır. Her yıldızın uzaklığı, rengi ve adının anlamı.",
           "lede": "Oyundaki her takımyıldızı gökyüzünde gerçekten var. Nasıl bulunur, en iyi ne zaman görünür, hangi efsaneyi anlatır? Her yıldızın uzaklığı, rengi ve adının anlamı da burada.",
           "regions": {"north": "Kuzey göğü", "equator": "Gök ekvatoru", "zodiac": "Burç kuşağı"}, "months": ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"],
           "cal_h": "Bu ay hangisi?", "cal_p": "Her takımyıldızının akşam 21.00 sularında en iyi göründüğü ay.", "now": "bu ay", "best_short": "En iyi: {0}",
           "best": "En iyi {0} akşamları, 21.00 sularında", "rank": "88 takımyıldızı arasında büyüklükte {0}.", "brightest": "En parlak yıldızı {0} ({1} kadir)", "count": "Bu rehberde {0} yıldız",
           "find": "Gökyüzünde bul", "legend": "Efsane", "sign": "Burç", "stars": "Yıldızları", "stars_p": "Kadir, yıldızın bize ne kadar parlak göründüğünü söyler: sayı küçüldükçe yıldız parlar.",
           "type": "Tür", "distance": "Uzaklık", "ly": "yaklaşık {0} ışık yılı", "mag": "Parlaklık", "mag_v": "{0} kadir", "name_m": "Adı", "map": "{0} takımyıldızının haritası", "all": "Tüm takımyıldızları", "crumb": "Yol",
           "prev": "Önceki", "next": "Sonraki",
           "note": "Haritadaki çizimler oyundaki hâliyledir, gökyüzündeki yerleri birebir göstermez.",
           "src": "Kaynaklar: takımyıldızı alanları Uluslararası Astronomi Birliği (IAU) sınırlarına göre; yıldız değerleri Hipparcos ve Gaia ölçümlerine dayanan Wikipedia maddelerinden; Güneş’in tarihleri EarthSky’dan. Uzaklıklar yuvarlanmıştır.",
           "seo_one": "{0} takımyıldızı: nasıl bulunur, yıldızları ve efsanesi", "desc_one": "{0} Nasıl bulunur, en iyi ne zaman görünür, yıldızları ve efsanesi."},
    "en": {"title": "Sky guide", "seo": "Sky guide: how to find the constellations", "label": "Star Jars · Sky guide",
           "desc": "The real constellations in Star Jars: how to find them, when they are best seen and the legends they tell. Every star’s distance, colour and the meaning of its name.",
           "lede": "Every constellation in the game is really up there. How do you find it, when is it best seen, what legend does it tell? Every star’s distance, colour and the meaning of its name are here too.",
           "regions": {"north": "Northern sky", "equator": "Celestial equator", "zodiac": "Zodiac"}, "months": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
           "cal_h": "Which one this month?", "cal_p": "The month each constellation is best seen, around 9 p.m.", "now": "this month", "best_short": "Best in {0}",
           "best": "Best in {0}, around 9 p.m.", "rank": "No. {0} of the 88 constellations by area", "brightest": "Brightest star {0} (magnitude {1})", "count": "{0} stars in this guide",
           "find": "Find it in the sky", "legend": "Legend", "sign": "Sign", "stars": "Its stars", "stars_p": "Magnitude says how bright a star looks from here: the smaller the number, the brighter the star.",
           "type": "Type", "distance": "Distance", "ly": "about {0} light years", "mag": "Brightness", "mag_v": "magnitude {0}", "name_m": "Name", "map": "Map of the constellation {0}", "all": "All constellations", "crumb": "Path",
           "prev": "Previous", "next": "Next",
           "note": "The drawings on these maps are the game’s, and don’t show exact positions in the sky.",
           "src": "Sources: constellation areas follow the International Astronomical Union (IAU) boundaries; star values come from Wikipedia’s articles, based on Hipparcos and Gaia; the Sun’s dates come from EarthSky. Distances are rounded.",
           "seo_one": "The constellation {0}: how to find it, its stars and legend", "desc_one": "{0} How to find it, when it is best seen, its stars and its legend."},
}


def num(lang, value, digits=2):
    text = f"{value:,.{digits}f}"
    return text.translate(str.maketrans(",.", ".,")) if lang == "tr" else text


def star_xy(s):
    return 90 + s["x"] * 820, 90 + (1 - s["y"]) * 820


def star_r(s):
    return max(8, 24 - s["mag"] * 4)


def label_spots(c, size=34):
    """Where each star's name goes: the side that covers the fewest other names, stars and lines. Brightest stars choose first."""
    stars, taken, spots = c["stars"], [], {}
    points = [star_xy(s) for s in stars]
    segments = [(points[a], points[b]) for a, b in c["lines"]]

    def hits(box):
        x0, y0, x1, y1 = box
        cost = 1000 if x0 < 4 or x1 > 996 or y0 < 4 or y1 > 996 else 0
        cost += sum(100 for a0, b0, a1, b1 in taken if x0 < a1 and a0 < x1 and y0 < b1 and b0 < y1)
        cost += sum(60 for s, (px, py) in zip(stars, points) if x0 - star_r(s) < px < x1 + star_r(s) and y0 - star_r(s) < py < y1 + star_r(s))
        for (ax, ay), (bx, by) in segments:
            cost += 8 * sum(1 for i in range(21) if x0 < ax + (bx - ax) * i / 20 < x1 and y0 < ay + (by - ay) * i / 20 < y1)
        return cost

    for i in sorted(range(len(stars)), key=lambda n: stars[n]["mag"]):
        x, y = points[i]
        r, w = star_r(stars[i]) + 11, len(stars[i]["name"]) * size * .5
        options = [("start", x + r, y + size * .34, (x + r, y - size / 2, x + r + w, y + size / 2)), ("end", x - r, y + size * .34, (x - r - w, y - size / 2, x - r, y + size / 2)),
                   ("middle", x, y - r - 6, (x - w / 2, y - r - size, x + w / 2, y - r)), ("middle", x, y + r + size * .8, (x - w / 2, y + r, x + w / 2, y + r + size))]
        best = min(options, key=lambda o: hits(o[3]))
        taken.append(best[3])
        spots[i] = best[:3]
    return spots


def sky_map(c, lang=None):
    """The constellation as the game draws it. With a language: a real map with names that link to the star cards. Without: a small picture."""
    stars = c["stars"]
    lines = "".join('<line x1="{:.0f}" y1="{:.0f}" x2="{:.0f}" y2="{:.0f}"/>'.format(*star_xy(stars[a]), *star_xy(stars[b])) for a, b in c["lines"])
    if lang is None:
        dots = "".join('<circle class="halo c-{}" cx="{:.0f}" cy="{:.0f}" r="{:.0f}"/><circle class="c-{}" cx="{:.0f}" cy="{:.0f}" r="{:.0f}"/>'.format(s["colour"], *star_xy(s), star_r(s) * 2.6, s["colour"], *star_xy(s), star_r(s) * 1.5) for s in stars)
        return f'<svg class="skymap mini" viewBox="0 0 1000 1000" aria-hidden="true" focusable="false">{lines}{dots}</svg>'
    spots = label_spots(c)
    dots = ""
    for i, s in enumerate(stars):
        x, y = star_xy(s)
        anchor, tx, ty = spots[i]
        dots += (f'<a href="#{s["slug"]}"><circle class="halo c-{s["colour"]}" cx="{x:.0f}" cy="{y:.0f}" r="{star_r(s) * 2.1:.0f}"/><circle class="c-{s["colour"]}" cx="{x:.0f}" cy="{y:.0f}" r="{star_r(s):.0f}"/>'
                 f'<text x="{tx:.0f}" y="{ty:.0f}" text-anchor="{anchor}">{esc(s["name"])}</text></a>')
    title = SKYT[lang]["map"].format(esc(c["name"][lang]))
    return f'<svg class="skymap" viewBox="0 0 1000 1000" role="group" aria-label="{title}">{lines}{dots}</svg>'


def sky_index_body(lang):
    t = SKYT[lang]
    groups = ""
    for region in ("north", "equator", "zodiac"):
        cards = ""
        for c in (x for x in SKY if x["region"] == region):
            cards += (f'<a class="skycard" href="{u("sky:" + c["id"], lang)}">{sky_map(c)}<span class="name">{esc(c["name"][lang])}</span><span class="latin" lang="la">{esc(c["latin"])}</span>'
                      f'<span class="when">{t["best_short"].format(t["months"][c["month"] - 1])}</span></a>')
        groups += f'<h2 id="{region}-h">{t["regions"][region]}</h2><div class="chartgrid">{cards}</div>'
    months = ""
    for m in range(1, 13):
        links = "".join(f'<a href="{u("sky:" + c["id"], lang)}">{esc(c["name"][lang])}</a>' for c in SKY if c["month"] == m)
        months += f'<li data-month="{m}"><h3 data-now="{t["now"]}">{t["months"][m - 1]}</h3>{links}</li>'
    orion = next(c for c in SKY if c["id"] == "orion")
    return f'''<section class="skyhero"><div><span class="label">{t["label"]}</span><h1>{t["title"]}</h1><p class="lede">{t["lede"]}</p></div>{sky_map(orion)}</section>
<section class="chart" aria-label="{t["title"]}">{groups}</section>
<section class="gsec cream" id="takvim" aria-labelledby="cal-h"><h2 id="cal-h">{t["cal_h"]}</h2><p class="intro">{t["cal_p"]}</p><ol class="months">{months}</ol></section>
{try_strip(lang)}
<section class="skysrc"><p>{t["note"]} {t["src"]}</p></section>'''


def sky_page_body(lang, i):
    t, c = SKYT[lang], SKY[i]
    name = esc(c["name"][lang])
    month = t["months"][c["month"] - 1]
    # The brightest star's number is the one on its own card, so a page never shows two values for one star.
    spec = "".join(f"<span>{x}</span>" for x in (t["best"].format(month), t["rank"].format(c["rank"]), t["brightest"].format(esc(c["brightest"]), num(lang, next(s for s in c["stars"] if s["name"] == c["brightest"])["mag"])), t["count"].format(len(c["stars"]))))
    texts = f'<article><h2>{t["find"]}</h2><p>{esc(c["find"][lang])}</p></article><article><h2>{t["legend"]}</h2><p>{esc(c["legend"][lang])}</p></article>'
    if c["sign"]:
        texts += f'<article><h2>{t["sign"]}</h2><p>{esc(c["sign"][lang])}. {esc(c["sun"][lang])}</p></article>'
    cards = ""
    for s in c["stars"]:
        kind = GAMEDATA["starTypes"]["colour"][s["colour"]][lang] + " " + GAMEDATA["starTypes"]["size"][s["size"]][lang]
        cards += (f'<article class="starcard" id="{s["slug"]}"><span class="orb c-{s["colour"]}" aria-hidden="true"></span><h3>{esc(s["name"])}</h3><p class="bayer">{esc(s["greek"][lang])}{s["sup"]} {esc(s["genitive"])}</p>'
                  f'<dl><dt>{t["type"]}</dt><dd>{kind}</dd><dt>{t["distance"]}</dt><dd>{t["ly"].format(num(lang, s["ly"], 0))}</dd><dt>{t["mag"]}</dt><dd>{t["mag_v"].format(num(lang, s["mag"]))}</dd><dt>{t["name_m"]}</dt><dd>{esc(s["meaning"][lang])}</dd></dl>'
                  f'<p>{esc(s["note"][lang])}</p></article>')
    before, after = SKY[i - 1], SKY[(i + 1) % len(SKY)]
    latin = f'<p class="latin" lang="la">{esc(c["latin"])}</p>' if c["latin"] != c["name"][lang] else ""
    return f'''<nav class="crumbs" aria-label="{t["crumb"]}"><a href="{u("sky", lang)}">{t["title"]}</a><span aria-hidden="true">›</span><span aria-current="page">{name}</span></nav>
<section class="skyhero one"><div><span class="label">{t["regions"][c["region"]]}</span><h1>{name}</h1>{latin}<p class="lede">{esc(c["fact"][lang])}</p><div class="skyspec">{spec}</div></div>
<div class="mapwrap">{sky_map(c, lang)}<p class="mapnote">{t["note"]}</p></div></section>
<section class="skytext">{texts}</section>
<section class="gsec cream" id="yildizlari" aria-labelledby="sl-h"><h2 id="sl-h">{t["stars"]}</h2><p class="intro">{t["stars_p"]}</p><div class="starcards">{cards}</div></section>
{try_strip(lang)}
<nav class="skynav" aria-label="{t["all"]}"><a href="{u("sky:" + before["id"], lang)}"><small>{t["prev"]}</small>{esc(before["name"][lang])}</a><a href="{u("sky", lang)}"><small>{t["title"]}</small>{t["all"]}</a><a href="{u("sky:" + after["id"], lang)}"><small>{t["next"]}</small>{esc(after["name"][lang])}</a></nav>
<section class="skysrc"><p>{t["src"]}</p></section>'''


def sky_ld(lang, title, desc, key):
    return {"@context": "https://schema.org", "@type": "Article", "headline": title, "description": desc, "inLanguage": lang, "url": SITE + u(key, lang), "image": f"{SITE}/img/og-starjars-{lang}.jpg",
            "author": {"@type": "Organization", "name": "Symbol Interactive", "url": SITE + "/"}, "publisher": {"@type": "Organization", "name": "Symbol Interactive", "logo": {"@type": "ImageObject", "url": SITE + "/img/apple-touch-icon.png"}}}


# ---- the making of. Told without dates. Only what the game's changelog and design notes show to be true.

MAKING = {
    "tr": {"title": "Yapım hikâyesi", "seo": "Star Jars’ın yapım hikâyesi", "desc": "Star Jars Sort Deluxe nasıl yapıldı: kurallardan kodla çizilen görsellere, gerçek takımyıldızlarından 13 dile.", "label": "Star Jars Sort Deluxe",
           "lede": "Star Jars tek bir soruyla başladı: renkli yıldızları sıralarken gerçek bir gökyüzünü yakmak nasıl olurdu? Kutunun içine neyin nasıl girdiğini burada anlatıyoruz.",
           "steps": [("Önce kurallar", "İlk sürümde tek bir çizim yoktu. Hamle kuralları, geri alma ve seviyeleri çözmeyi deneyen bir çözücü vardı. Çözücüden geçmeyen seviye oyuna girmez; bu kural bugün de geçerli.", "art:pour", ""),
                     ("Çizimler koddan çıktı", "Yıldızları, kavanozları, mühürleri kodla çiziyoruz. Bir ayrıntıyı değiştirmek için birkaç satırı düzeltip bütün çizimleri yeniden üretmek yetiyor. Bu yüzden oyunda hazır görsel paketi yok.", "art:vessel", ""),
                     ("Her rengin kendi şekli", "Bu oyunun özü renkleri ayırmak, ama herkes renkleri aynı görmüyor. O yüzden her rengin bir şekli de var: yıldız, küre, kalp, damla, elmas, hilal, üçgen, gezegen, kristal.", "strip:shapes", ""),
                     ("Bulmaca gökyüzüne bağlandı", "Baştan beri aklımızdaki fark buydu: sıraladığın yıldızlar gerçek olacaktı. Ana ekran bir haritaya dönüştü, her seviye gerçek bir takımyıldızının bir yıldızını yakar oldu. Kartlardaki uzaklık ve parlaklık değerlerini kaynaklarıyla karşılaştırdık.", "shot:card", "sky"),
                     ("Her bölüme yeni bir fikir", "Aynı bulmacayı yüzlerce kez çözdürmek istemedik. Buzlu kavanoz, etiket, renk kilidi, saatli yıldız, ters kavanoz: yol boyunca yeni kurallar geldi. Bölümler o takımyıldızına özel bir kavanozla bitiyor, uzay bölümleri de kendi kuralını getiriyor.", "shot:boss", "guide"),
                     ("13 dil", "Oyun Türkçe başladı, sonra İngilizce geldi, ardından Arapça dahil 13 dile çıktı. Çevrilen yalnızca düğmeler değil, yıldız kartları da her dilde.", "langs", ""),
                     ("Şimdi", "Oyun test sürümlerinde, mağazalara hazırlanıyor. Bu sayfayı son güncellediğimizde {version} sürümündeydi. Yayından sonra da yeni bölümler eklemeyi sürdüreceğiz.", "zar", "news")],
           "more": {"sky": "Gökyüzü rehberine git", "guide": "Kavanoz ve kural rehberine git", "news": "Yeniliklere bak"}, "alts": {"card": "Oyundaki bir yıldız kartı", "boss": "Bir takımyıldızına özel bölüm kavanozu"}},
    "en": {"title": "The making of", "seo": "The making of Star Jars", "desc": "How Star Jars Sort Deluxe was made: from the rules to art drawn in code, from real constellations to 13 languages.", "label": "Star Jars Sort Deluxe",
           "lede": "Star Jars began with one question: what if sorting colourful stars lit up a real sky? Here is what went into the box, and how.",
           "steps": [("Rules first", "The first version had no drawings at all. It had the rules of a move, undo, and a solver that tries to solve the levels. A level the solver can’t get through doesn’t go in the game, and that still holds today.", "art:pour", ""),
                     ("Art out of code", "We draw the stars, jars and seals in code. To change a detail we fix a few lines and make every drawing again. That’s why there are no ready-made art packs in the game.", "art:vessel", ""),
                     ("A shape for every colour", "The heart of this game is telling colours apart, but not everyone sees them the same. So every colour has a shape too: star, orb, heart, drop, diamond, crescent, triangle, planet, crystal.", "strip:shapes", ""),
                     ("The puzzle met the sky", "This was the difference we wanted from the start: the stars you sort would be real. The home screen became a map, and every level came to light a star of a real constellation. We checked the distances and brightness on the cards against their sources.", "shot:card", "sky"),
                     ("A new idea in every chapter", "We didn’t want you solving the same puzzle hundreds of times. Icy jars, labels, colour locks, clock stars, upside-down jars: new rules arrived along the way. Chapters end with a jar drawn for their constellation, and space chapters bring rules of their own.", "shot:boss", "guide"),
                     ("13 languages", "The game began in Turkish, then came English, then 13 languages including Arabic. Not just the buttons: the star cards are in every language too.", "langs", ""),
                     ("Now", "The game is in test versions, getting ready for the stores. When we last updated this page it was at version {version}. We’ll keep adding new chapters after release.", "zar", "news")],
           "more": {"sky": "Go to the sky guide", "guide": "Go to the jar and rule guide", "news": "See what’s new"}, "alts": {"card": "A star card in the game", "boss": "A chapter jar drawn for one constellation"}},
}


def making_body(lang):
    m = MAKING[lang]
    rows = ""
    for i, (title, text, media_key, more) in enumerate(m["steps"]):
        kind, _, name = media_key.partition(":")
        if kind == "art":
            pic = f'<div class="smed panel"><img src="/img/guide/{name}.webp" width="560" height="560" alt="" loading="lazy"></div>'
        elif kind == "strip":
            pic = f'<div class="smed panel strip"><img src="/img/guide/{name}.webp" width="1944" height="216" alt="" loading="lazy"></div>'
        elif kind == "shot":
            pic = f'<div class="smed phone"><img src="/img/sj/{lang}-{name}.jpg" width="560" height="1213" alt="{m["alts"][name]}" loading="lazy"></div>'
        elif kind == "langs":
            names = "".join(f'<li lang="{code}"{" dir=" + chr(34) + "rtl" + chr(34) if code == "ar" else ""}>{n}</li>' for code, n in LANGS)
            pic = f'<div class="smed panel"><ul class="langs big">{names}</ul></div>'
        else:
            pic = f'<div class="smed zarbox">{zar()}</div>'
        link = f'<p class="more-link"><a href="{u(more, lang)}">{m["more"][more]}</a></p>' if more else ""
        version = GAMEDATA["gameVersion"].removesuffix(".0")
        rows += f'<li><div class="stx"><b class="let" aria-hidden="true">{i + 1}</b><h2>{title}</h2><p>{text.format(version=version)}</p>{link}</div>{pic}</li>'
    return f'{pagehead(m["label"], m["title"], m["lede"], "/img/guide/seal.webp")}<ol class="story">{rows}</ol>{try_strip(lang)}'


LEARN = {
    "tr": ("Oyunu yakından tanı", [("guide", "Kavanoz ve kural rehberi", "Her kavanoz, her yıldız, her kural.", "ice"), ("sky", "Gökyüzü rehberi", f"{GAME['constellations']} takımyıldızı ve {GAME['stars']} yıldız: nasıl bulunur, ne anlatır.", "saturn"),
                                   ("news", "Yenilikler", "Oyuna son eklenenler.", "comet"), ("makingof", "Yapım hikâyesi", "Kutuya ne girdi, nasıl girdi.", "pour")]),
    "en": ("Get to know the game", [("guide", "Jar and rule guide", "Every jar, every star, every rule.", "ice"), ("sky", "Sky guide", f"{GAME['constellations']} constellations and {GAME['stars']} stars: how to find them, what they tell.", "saturn"),
                                    ("news", "What’s new", "The latest additions to the game.", "comet"), ("makingof", "The making of", "What went into the box, and how.", "pour")]),
}


def learn(lang):
    title, items = LEARN[lang]
    cards = "".join(f'<a class="learncard" href="{u(k, lang)}"><img src="/img/guide/{art}.webp" width="560" height="560" alt="" loading="lazy"><span><b>{h}</b>{p}</span></a>' for k, h, p, art in items)
    return f'<section class="learn" aria-labelledby="learn-h"><h2 id="learn-h">{title}</h2><div class="learngrid">{cards}</div></section>'


# ---------------------------------------------------------------- write everything

L = {"tr": {"privacy": "Gizlilik politikası", "terms": "Kullanım koşulları", "delete": "Hesap silme", "updated": "Son güncelleme",
            "applies": "Star Jars Sort Deluxe 1.0.0 ve sonraki sürümler için geçerlidir.", "game": "Oyun: Star Jars Sort Deluxe (Yıldız Kavanozu). Geliştirici: Symbol Interactive."},
     "en": {"privacy": "Privacy policy", "terms": "Terms of use", "delete": "Deleting your account", "updated": "Last updated",
            "applies": "Applies to Star Jars Sort Deluxe 1.0.0 and later.", "game": "Game: Star Jars Sort Deluxe. Developer: Symbol Interactive."}}

TERMS_INTRO = {
    "tr": "<p>Bu koşullar, Symbol Interactive'in oyunlarını (şu an Star Jars Sort Deluxe) oynarken seninle aramızdaki kuralları anlatır. Oyunu indirerek ya da oynayarak bu koşulları kabul etmiş olursun. Kısa ve anlaşılır tutmaya çalıştık; bir sorun olursa önce bize yaz.</p>",
    "en": "<p>These terms set out the rules between you and us when you play Symbol Interactive's games (currently Star Jars Sort Deluxe). By downloading or playing a game you accept them. We've tried to keep them short and clear; if there's a problem, write to us first.</p>",
}

for lang in ("tr", "en"):
    l = L[lang]
    tag = " · Symbol Interactive"
    home_page(lang)
    page(lang, "games", {"tr": "Oyunlar", "en": "Games"}[lang] + tag, {"tr": "Symbol Interactive’in oyunları: Star Jars Sort Deluxe ve geliştirilenler.",
                                                                      "en": "Games by Symbol Interactive: Star Jars Sort Deluxe and more in development."}[lang], games_body(lang), plain=True, script=True)
    page(lang, "about", {"tr": "Hakkımızda", "en": "About"}[lang] + tag, {"tr": "Symbol Interactive’in vizyonu, nasıl çalıştığı ve kim olduğu.",
                                                                        "en": "Symbol Interactive's vision, how we work, and who we are."}[lang], about_body(lang), plain=True, script=True)
    page(lang, "press", PRESS[lang]["h1"] + tag, {"tr": "Symbol Interactive basın kiti: logolar, ekran görüntüleri, tanıtım videosu ve oyun bilgileri.",
                                                  "en": "Symbol Interactive press kit: logos, screenshots, the trailer and game facts."}[lang], press_body(lang))
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
    page(lang, "news", NEWS[lang]["title"] + " · Star Jars", NEWS[lang]["desc"], news_body(lang), plain=True, og=f"/img/og-starjars-{lang}.jpg")
    page(lang, "guide", GUIDE[lang]["seo"], GUIDE[lang]["desc"], guide_body(lang), plain=True, og=f"/img/og-starjars-{lang}.jpg")
    page(lang, "makingof", MAKING[lang]["seo"] + tag, MAKING[lang]["desc"], making_body(lang), plain=True, script=True, og=f"/img/og-starjars-{lang}.jpg")
    page(lang, "sky", SKYT[lang]["seo"], SKYT[lang]["desc"], sky_index_body(lang), plain=True, script=True, og=f"/img/og-starjars-{lang}.jpg", ld=sky_ld(lang, SKYT[lang]["seo"], SKYT[lang]["desc"], "sky"))
    for i, one in enumerate(SKY):
        one_key = f"sky:{one['id']}"
        one_title = SKYT[lang]["seo_one"].format(esc(one["name"][lang]))
        one_desc = SKYT[lang]["desc_one"].format(esc(one["fact"][lang]))
        page(lang, one_key, one_title, one_desc, sky_page_body(lang, i), plain=True, og=f"/img/og-starjars-{lang}.jpg", ld=sky_ld(lang, one_title, one_desc, one_key))
write("demo/stores.js", "window.SJ_STORES=" + json.dumps(STORES) + ";\n")

# The App Store's support URL (the user, 2026-11-03): /support, English first and Turkish below, on one page.
page("en", "support", "Support · Symbol Interactive", "Support for Symbol Interactive games, in English and Turkish.",
     f'<div class="doc single"><article class="prose">{SUPPORT["en"]}<div class="lang-block" lang="tr">'
     + SUPPORT["tr"].replace("<h1>Destek</h1>", '<h2 style="font-size:clamp(1.8rem,4vw,2.4rem)">Destek (Türkçe)</h2>', 1) + "</div></article></div>",
     own_path="/support.html", other_href=u("support", "tr"))
# Plan 6h: where a shared star code lands. One page for every language: English unless the browser says Turkish.
FRIEND_LINK = {
    "tr": ("Yıldız Kodu", "Bir arkadaşın seni Star Jars'ta arkadaş olmaya çağırıyor.", "Kopyala", "Kopyalandı", "Oyunda Arkadaşlar → Arkadaş ekle'ye dokun, kodu yapıştır.", "Bu bağlantıda geçerli bir kod yok. Arkadaşından kodunu yeniden iste.", "Yakında App Store ve Google Play'de."),
    "en": ("Star code", "A friend is inviting you to be friends in Star Jars.", "Copy", "Copied", "In the game, tap Friends → Add friend and paste the code.", "This link has no valid code. Ask your friend to send it again.", "Coming soon to the App Store and Google Play."),
}
page("tr", None, "Yıldız Kodu · Star Jars", "Star Jars'ta arkadaş olmak için Yıldız Kodu. A star code to be friends in Star Jars.", f'''<div class="doc single"><article class="prose" id="friend" style="text-align:center">
<h1 id="f-title">{FRIEND_LINK["tr"][0]}</h1>
<p id="f-line">{FRIEND_LINK["tr"][1]}</p>
<p id="f-code" style="font-size:clamp(2rem,9vw,3.2rem);font-weight:700;letter-spacing:.04em;margin:.6em 0;overflow-wrap:anywhere"></p>
<p><button id="f-copy" type="button" style="font:inherit;padding:.7em 1.6em;border-radius:999px;border:0;background:var(--ink);color:var(--paper);cursor:pointer">{FRIEND_LINK["tr"][2]}</button></p>
<p id="f-how">{FRIEND_LINK["tr"][4]}</p>
<p id="f-stores">{FRIEND_LINK["tr"][6]}</p>
</article></div>
<script src="/demo/stores.js"></script>
<script>
(function () {{
  var words = {json.dumps(FRIEND_LINK, ensure_ascii=False)};
  var lang = (navigator.language || "en").toLowerCase().indexOf("tr") === 0 ? "tr" : "en";
  var t = words[lang];
  document.documentElement.lang = lang;
  var by = function (id) {{ return document.getElementById(id); }};
  by("f-title").textContent = t[0];
  by("f-line").textContent = t[1];
  by("f-how").textContent = t[4];
  var code = (new URLSearchParams(location.search).get("k") || "").toUpperCase();
  var copy = by("f-copy");
  if (/^[A-Z]{{2,8}}-[0-9]{{6}}$/.test(code)) {{
    by("f-code").textContent = code;
    copy.textContent = t[2];
    copy.addEventListener("click", function () {{
      navigator.clipboard.writeText(code).then(function () {{ copy.textContent = t[3]; }});
    }});
  }} else {{
    by("f-line").textContent = t[5];
    by("f-how").hidden = true;
    copy.hidden = true;
  }}
  var stores = by("f-stores");
  var s = window.SJ_STORES || {{}};
  if (s.live) {{
    stores.textContent = "";
    [["App Store", s.ios], ["Google Play", s.android]].forEach(function (store, i) {{
      var a = document.createElement("a");
      a.href = store[1];
      a.textContent = store[0];
      if (i) stores.appendChild(document.createTextNode(" · "));
      stores.appendChild(a);
    }});
  }} else {{
    stores.textContent = t[6];
  }}
}})();
</script>''', own_path="/arkadas.html", other_href="/en/")
page("tr", None, "Sayfa yok · Symbol Interactive", "Sayfa bulunamadı. This page doesn't exist.", NOT_FOUND, own_path="/404.html", other_href="/en/")

# Files made from Zar and the jar.
(ROOT / "img" / "logo-ink.svg").write_text(logo_file("#111")[0], encoding="utf-8")
(ROOT / "img" / "logo-yellow.svg").write_text(logo_file("#F4B90B")[0], encoding="utf-8")
(ROOT / "img" / "logo-white.svg").write_text(logo_file("#fff")[0], encoding="utf-8")
(ROOT / "favicon.svg").write_text(
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><rect width="1000" height="1000" rx="220" fill="#F4B90B"/>'
    f'<g transform="translate(58 26) scale(.9)">{zar_mask("z")}<rect x="120" y="70" width="790" height="900" fill="#111" mask="url(#z)"/></g></svg>\n', encoding="utf-8")
(ROOT / "img" / "starjars-icon.svg").write_text(jar_icon(), encoding="utf-8")

# Search engines: every page and its twin.
urls = ""
for key, paths in PAGES.items():
    if key in NOINDEX:
        continue
    for lang in paths:
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{a}" href="{SITE}{u(key, a)}"/>' for a in paths)
        urls += f"<url><loc>{SITE}{u(key, lang)}</loc>{alts}</url>\n"
write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n{urls}</urlset>\n')
write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")

# Guards: no review notes, every page has its twin, and the two hand-kept files are untouched by this script.
pages = [*ROOT.glob("*.html"), *ROOT.glob("en/*.html"), *ROOT.glob("gokyuzu/*.html"), *ROOT.glob("en/sky/*.html")]
assert not any("REVIEW" in p.read_text(encoding="utf-8") for p in pages), "a REVIEW note is left in a page"
for key, paths in PAGES.items():
    for lang, path in paths.items():
        assert (ROOT / path).exists(), path
print(f"built {len(pages)} pages")
