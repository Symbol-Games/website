#!/usr/bin/env python3
"""Checks the built site against a base ref: python3 tools/check_site.py [origin/main]

Nothing the stores or players rely on may break, and the site's own promises must stay true:
every old address exists, the legal and support text is word for word the same, every local link resolves,
nothing loads from another host, and the place name stays in the address (user, 2026-11-05).
"""
import html
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
SAME_TEXT = ["gizlilik.html", "kullanim-kosullari.html", "hesap-silme.html", "destek.html", "support.html",
             "en/privacy.html", "en/terms.html", "en/delete-account.html", "en/support.html"]
LEGAL = set(SAME_TEXT)
KEEP = ["CNAME", "app-ads.txt", "demo/starjars.html", "demo/stores.js", "img/starjars-icon.svg"]
# foreground, background: the pairs body text and controls actually use
PAIRS = [("#111111", "#F4B90B"), ("#111111", "#FFFDF5"), ("#111111", "#FFF3CE"), ("#F4B90B", "#111111"), ("#FFFDF5", "#111111"),
         ("#FFFFFF", "#2A1A78"), ("#FFD76A", "#2A1A78"), ("#F4B90B", "#2A1A78"), ("#D6CEFF", "#2A1A78"), ("#A62D10", "#FFF3CE"), ("#454238", "#FFFDF5"), ("#C9C6B8", "#111111")]
errors = []


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=True).stdout


def main_text(markup):
    m = re.search(r'<main[^>]*>(.*)</main>', markup, re.S)
    t = re.sub(r"<script.*?</script>", " ", m.group(1) if m else markup, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t))).strip()


def luminance(c):
    v = [int(c[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = [x / 12.92 if x <= .03928 else ((x + .055) / 1.055) ** 2.4 for x in v]
    return .2126 * r + .7152 * g + .0722 * b


def contrast(a, b):
    x, y = sorted((luminance(a), luminance(b)), reverse=True)
    return (x + .05) / (y + .05)


base_pages = [p for p in git("ls-tree", "-r", "--name-only", BASE).splitlines() if p.endswith(".html")]
for p in base_pages:
    if not (ROOT / p).exists():
        errors.append(f"address gone: /{p}")
for p in KEEP:
    if not (ROOT / p).exists():
        errors.append(f"file gone: {p}")
for p in SAME_TEXT:
    if (ROOT / p).exists() and main_text((ROOT / p).read_text(encoding="utf-8")) != main_text(git("show", f"{BASE}:{p}")):
        errors.append(f"text changed: {p}")

pages = [*ROOT.glob("*.html"), *ROOT.glob("en/*.html")]
css = (ROOT / "site.css").read_text(encoding="utf-8")
sources = [(p.relative_to(ROOT).as_posix(), p.read_text(encoding="utf-8")) for p in pages] + [("site.css", css)]
for name, text in sources:
    if "%%" in text or "REVIEW" in text:
        errors.append(f"leftover marker: {name}")
    refs = re.findall(r'\b(?:href|src|poster)="(/[^"]*)"', text) + re.findall(r'url\("?(/[^")]+)"?\)', text)
    for ref in refs:
        path = ref.split("#")[0].split("?")[0]
        target = ROOT / path.lstrip("/")
        if path in ("/", "/en/"):
            target = target / "index.html"
        if not target.exists():
            errors.append(f"broken link in {name}: {ref}")
    for anchor in re.findall(r'href="#([^"]+)"', text):
        if f'id="{anchor}"' not in text:
            errors.append(f"broken anchor in {name}: #{anchor}")
    outside = re.findall(r'<(?:script|img|video|source|iframe|audio)[^>]+\bsrc="(https?:[^"]+)"', text)
    outside += re.findall(r'<link[^>]+rel="(?:stylesheet|preload|preconnect)"[^>]+href="(https?:[^"]+)"', text)
    outside += re.findall(r'url\("?(https?:[^")]+)', text)
    for x in outside:
        errors.append(f"loads from another host in {name}: {x}")
    if name not in LEGAL and name.endswith(".html"):
        visible = html.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>", " ", text, flags=re.S)))
        meta = " ".join(re.findall(r'<(?:meta|title)[^>]*>[^<]*', text))
        for m in re.finditer(r"Aydın", visible + " " + meta):
            around = (visible + " " + meta)[m.start():m.start() + 14]
            if not around.startswith("Aydın, Türkiye"):
                errors.append(f"place name outside an address in {name}: {around!r}")
        if re.search(r"mobil oyun stüdyosu|mobile game studio", visible):
            errors.append(f"old studio line in {name}")
for fg, bg in PAIRS:
    if contrast(fg, bg) < 4.5:
        errors.append(f"contrast {fg} on {bg}: {contrast(fg, bg):.2f}")

print("\n".join(errors) if errors else f"ok: {len(pages)} pages, {len(base_pages)} old addresses, {len(SAME_TEXT)} legal texts")
sys.exit(1 if errors else 0)
