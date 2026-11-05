#!/usr/local/bin/python3
"""Copies what the guide pages need out of the game's source: tools/export_game.py [git ref of star-jars, default origin/main]

Writes data/game.json (constellations, star cards, rules and news, in Turkish and English) and img/guide/*.webp (pictures composed
from the game's own sprites). Reads git, so neither the game's checkout nor Unity is touched. Weekly packs are not read: they are not out yet.
Run it when the game gets something new worth showing, then python3 build.py.
"""
import io
import json
import pathlib
import re
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
SJ = pathlib.Path.home() / "game-studio/games/star-jars"
REF = sys.argv[1] if len(sys.argv) > 1 else "origin/main"
ATLAS = "Assets/Game/Runtime/Atlas"
ART = ROOT / "img" / "guide"
ENTRY = re.compile(r'\(\s*"([\w.\-]+)"\s*,\s*"((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"')
NOT_ASCII = str.maketrans("çğıöşüÇĞİÖŞÜ", "cgiosuCGIOSU")

# Mechanics that are in the code but not yet in any level players get.
UNSHIPPED = {"turning", "mini", "seal_order"}
JARS = ["ice", "label", "colour_lock", "tall_jar", "big_jar", "inverted", "oneway_gives", "oneway_takes", "locked_jar"]
STARS = ["hidden", "joker", "clock", "bundle", "planet", "crystal", "comet", "move_limit"]
BOSSES = ["vessel", "boss_funnel", "boss_onepour", "boss_key", "boss_eclipse", "boss_nova", "boss_light"]
SPACE = ["nebula", "saturn", "supernova", "leonids", "galaxy", "exoplanet", "cluster", "core", "neptune", "helix", "whitedwarf", "reddwarf", "blackhole"]
# News lines about the shop, accounts and small repairs: true, but not news a player looks for here.
NEWS_DROP = {"whatsnew.econ.shop", "whatsnew.econ.lives", "whatsnew.iap.shop", "whatsnew.iap.restore", "whatsnew.060.noads", "whatsnew.060.privacy",
             "whatsnew.064.accounts", "whatsnew.065.shop", "whatsnew.bossrules.old"}


def git(*args, text=True):
    return subprocess.run(["git", "-C", str(SJ), *args], capture_output=True, text=text, check=True).stdout


def show(path):
    return git("show", f"{REF}:{path}")


def tidy(s):
    """The game's plain quotes become the site's typographic ones."""
    s = s.replace('\\"', '"').replace("\\n", " ").replace("\\\\", "\\")
    s = re.sub(r'"([^"]*)"', "“\\1”", s)
    return s.replace("'", "’")


def game_strings():
    out = {}
    for path in git("ls-tree", "-r", "--name-only", REF, "Assets/Game/Editor").splitlines():
        if path.endswith(".cs"):
            for key, tr, en in ENTRY.findall(show(path)):
                out.setdefault(key, {"tr": tidy(tr), "en": tidy(en)})
    return out


S = game_strings()


def facts_by_name():
    src = show(f"{ATLAS}/StarFacts.cs")
    out = {}
    for m in re.finditer(r'F\("([^"]+)",\s*"([^"]*)",\s*"([^"]*)",\s*(\w+),\s*(\w+),\s*(\d+),\s*(-?[\d.]+)f(?:,\s*sup:\s*"([^"]*)"|,\s*"([^"]*)")?\)', src):
        name, letter, genitive, colour, size, ly, mag, sup1, sup2 = m.groups()
        size = {"Bright": "BrightGiant", "Super": "Supergiant"}.get(size, size)
        out[name] = {"letter": letter, "sup": sup1 or sup2 or "", "genitive": genitive, "colour": colour, "size": size, "ly": int(ly), "mag": float(mag)}
    return out


def constellations():
    facts = facts_by_name()
    src = show(f"{ATLAS}/Constellations.cs")
    card = {}
    for m in re.finditer(r'Id = "([\w-]+)", Latin = "([^"]+)", RegionKey = "sky\.region\.(\w+)", AreaRank = (\d+), Brightest = "([^"]+)", BrightestMagnitude = (-?[\d.]+)f, BestMonth = (\d+)', show(f"{ATLAS}/ConstellationFacts.cs")):
        card[m[1]] = {"latin": m[2], "region": m[3], "rank": int(m[4]), "brightest": m[5], "month": int(m[7])}
    out = []
    for m in re.finditer(r'Id = "([\w-]+)", NameKey = "[^"]+",\s*Stars = new\[\] \{(.*?)\},\s*Lines = new\[\] \{(.*?)\}', src, re.S):
        cid, stars_src, lines_src = m.groups()
        stars = []
        for name, x, y in re.findall(r'S\("([^"]+)", ([\d.]+)f, ([\d.]+)f\)', stars_src):
            slug = name.lower().replace(" ", "-")
            f = facts[name]
            greek = S.get(f"greek.{f['letter']}", {"tr": f["letter"], "en": f["letter"]})
            stars.append({"name": name, "slug": slug, "x": float(x), "y": float(y), **f, "greek": greek, "meaning": S[f"star.{slug}.meaning"], "note": S[f"star.{slug}.note"]})
        name = S[f"chapter.{cid}"]
        out.append({"id": cid, "slug": name["tr"].translate(NOT_ASCII).lower().replace(" ", "-"), "name": name, **card[cid], "fact": S[f"chapter.{cid}.fact"], "legend": S[f"sky.{cid}.legend"], "find": S[f"sky.{cid}.find"],
                    "sign": S.get(f"sky.{cid}.sign"), "sun": S.get(f"sky.{cid}.sun"), "stars": stars, "lines": [[int(a), int(b)] for a, b in re.findall(r"\((\d+), (\d+)\)", lines_src)]})
    return out


def news():
    src = show("Assets/Game/Runtime/Meta/WhatsNew.cs")
    sky = re.search(r'SkyVersion = "([\d.]+)"', src)[1]
    first = {}
    for version, keys in re.findall(r'\((?:"([\d.]+)"|SkyVersion), new\[\] \{(.*?)\}\)', src):
        v = tuple(int(x) for x in (version or sky).split("."))
        for key in re.findall(r'"(whatsnew\.[\w.]+)"', keys):
            if key not in NEWS_DROP and (key not in first or v < first[key]):
                first[key] = v
    groups = {}
    for key, v in first.items():
        groups.setdefault(v[:2], []).append(key)
    return [{"version": f"{v[0]}.{v[1]}", "lines": [{"key": k, **S[k]} for k in sorted(groups[v])]} for v in sorted(groups, reverse=True)]


def guide():
    def card(key):
        return {"key": key, "title": S[f"intro.{key}.title"], "line": S[f"intro.{key}.line"]}
    def space(key):
        return {**card(key), "object": S[f"space.{key}.object"], "fact": S[f"space.{key}.fact"]}
    return {"jars": [card(k) for k in JARS], "stars": [card(k) for k in STARS], "bosses": [card(k) for k in BOSSES], "space": [space(k) for k in SPACE]}


# ---------------------------------------------------------------- the pictures, from the game's own sprites

_sprites = {}


def sprite(name):
    if name not in _sprites:
        raw = git("show", f"{REF}:Assets/Game/Art/Sprites/{name}.png", text=False)
        _sprites[name] = Image.open(io.BytesIO(raw)).convert("RGBA")
    return _sprites[name]


def scaled(im, k):
    return im.resize((max(1, round(im.width * k)), max(1, round(im.height * k))), Image.LANCZOS)


def put(canvas, im, cx, cy):
    canvas.alpha_composite(im, (round(cx - im.width / 2), round(cy - im.height / 2)))


C = 560  # every picture is square; the page sets it on the night tile
JAR_K = .66


def jar(stars=(), back="jar_back", flip=False, slots=4):
    """A jar as the game draws one: back glass, stars from the bottom up, front glass. Returns a picture the size of the sprite."""
    b, f = sprite(back), sprite("jar_front")
    out = Image.new("RGBA", b.size)
    out.alpha_composite(b)
    step = 600 / slots
    for i, s in enumerate(stars):
        y = (668 - step / 2 - i * step) if not flip else (34 + step / 2 + i * step)
        put(out, scaled(sprite(s), min(.8, step / 180)), b.width / 2, y)
    out.alpha_composite(f.rotate(180) if flip else f)
    return out


def scene():
    return Image.new("RGBA", (C, C))


def jar_in(pic, stars=(), x=C / 2, y=C / 2 + 14, **kw):
    im = scaled(jar(stars, **kw), JAR_K)
    put(pic, im, x, y)
    return y - im.height / 2  # the mouth


def arc(pic, a, b, lift=120, colour=(255, 215, 106, 255)):
    d = ImageDraw.Draw(pic)
    n = 15
    for i in range(1, n):
        t = i / n
        x = (1 - t) ** 2 * a[0] + 2 * (1 - t) * t * (a[0] + b[0]) / 2 + t ** 2 * b[0]
        y = (1 - t) ** 2 * a[1] + 2 * (1 - t) * t * (min(a[1], b[1]) - lift) + t ** 2 * b[1]
        r = 5
        d.ellipse((x - r, y - r, x + r, y + r), fill=colour)


def art():
    ART.mkdir(parents=True, exist_ok=True)
    out = {}

    p = scene()
    m1 = jar_in(p, ["star_1", "star_0"], x=170, y=330)
    m2 = jar_in(p, ["star_3", "star_2"], x=400, y=330)
    put(p, scaled(sprite("star_2"), .62), 170, m1 - 30)
    arc(p, (205, m1 - 44), (396, m2 + 34), lift=60)
    out["pour"] = p

    p = scene()
    jar_in(p, ["star_1", "star_0", "star_1", "star_0"], x=120, y=300)
    jar_in(p, ["star_3", "star_3", "star_3"], x=280, y=300)
    jar_in(p, ["star_2", "star_2"], x=440, y=300)
    out["sort"] = p

    p = scene()
    m = jar_in(p, ["star_4"] * 4, back="jar_back_done", y=320)
    put(p, scaled(sprite("cork_0"), .62), C / 2, m + 12)
    put(p, sprite("newborn_star"), 430, 100)
    put(p, scaled(sprite("newborn_star"), .6), 130, 170)
    out["seal"] = p

    p = scene()
    m = jar_in(p, ["star_3", "star_0", "star_1", "star_2"])
    put(p, scaled(sprite("ice_cap"), .78), C / 2, m + 34)
    out["ice"] = p

    p = scene()
    jar_in(p, ["star_0", "star_0"], x=C / 2 - 34)
    put(p, scaled(sprite("intro_label"), 1.05), C / 2 + 112, 150)
    out["label"] = p

    p = scene()
    m = jar_in(p, ["star_1", "star_2", "star_0"])
    put(p, scaled(sprite("intro_lock"), 1.0), C / 2, m + 26)
    out["colour_lock"] = p

    for key, name in (("tall_jar", "intro_jar"), ("big_jar", "intro_big_jar")):
        p = scene()
        im = sprite(name)
        put(p, scaled(im, 500 / max(im.size)), C / 2, C / 2)
        out[key] = p

    p = scene()
    jar_in(p, ["star_6", "star_1", "star_0"], y=C / 2 - 40, flip=True)
    put(p, scaled(sprite("inverted_arrow"), .72), C / 2, 505)
    out["inverted"] = p

    p = scene()
    m = jar_in(p, ["star_5", "star_5", "star_2"], y=C / 2 + 34)
    put(p, scaled(sprite("oneway_spout"), .78), C / 2 + 24, m - 4)
    out["oneway_gives"] = p

    p = scene()
    m = jar_in(p, ["star_6", "star_6"], y=C / 2 + 34)
    put(p, scaled(sprite("oneway_funnel"), .78), C / 2, m - 4)
    out["oneway_takes"] = p

    p = scene()
    jar_in(p)
    put(p, scaled(sprite("icon_lock"), .8), C / 2, C / 2 + 14)
    out["locked_jar"] = p

    p = scene()
    jar_in(p, ["star_empty", "star_empty", "star_empty", "star_1"])
    for y in (408, 309, 210):  # the game's own cloud over each hidden star
        put(p, scaled(sprite("puff"), .62), C / 2, y)
    out["hidden"] = p

    p = scene()
    put(p, scaled(sprite("star_joker"), 2), C / 2, C / 2)
    put(p, scaled(sprite("newborn_star"), .8), 120, 130)
    put(p, scaled(sprite("newborn_star"), .55), 450, 420)
    out["joker"] = p

    p = scene()
    put(p, scaled(sprite("star_0"), 1.8), C / 2 - 44, C / 2 - 30)
    put(p, scaled(sprite("clock_face"), 1.2), C / 2 + 112, C / 2 + 96)
    out["clock"] = p

    p = scene()
    for y in (C / 2 - 104, C / 2 + 104):
        put(p, scaled(sprite("bundle_capsule"), 1.04), C / 2, y)
        put(p, scaled(sprite("star_6"), .84), C / 2, y)
    put(p, scaled(sprite("bundle_bow"), 1.2), C / 2, C / 2)
    out["bundle"] = p

    for key, name in (("planet", "star_7"), ("crystal", "star_8")):
        p = scene()
        put(p, scaled(sprite(name), 2.2), C / 2, C / 2)
        out[key] = p

    p = scene()
    put(p, scaled(sprite("comet"), .74), C / 2, C / 2)
    out["comet"] = p

    p = scene()
    jar_in(p, ["star_3", "star_2", "star_1", "star_0"], x=C / 2 - 86)
    d = ImageDraw.Draw(p)
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Black.ttf", 84)
    box = (C / 2 + 20, C / 2 - 74, C / 2 + 214, C / 2 + 74)
    d.rounded_rectangle(box, 38, fill=(255, 201, 60, 255), outline=(255, 255, 255, 255), width=8)
    d.text(((box[0] + box[2]) / 2, (box[1] + box[3]) / 2 - 2), "12", font=font, fill=(42, 26, 120, 255), anchor="mm")
    out["move_limit"] = p

    p = scene()
    glass = scaled(sprite("seal_glass"), 1.05)
    put(p, glass, C / 2, C / 2 + 4)
    for dx, dy, s in ((-84, 92, "star_0"), (2, 104, "star_0"), (84, 92, "star_0"), (-44, 8, "star_1"), (44, 8, "star_1")):
        put(p, scaled(sprite(s), .5), C / 2 + dx, C / 2 + dy)
    out["vessel"] = p

    for key in BOSSES[1:]:
        p = scene()
        put(p, scaled(sprite(key), 2.2) if sprite(key).width < 240 else scaled(sprite(key), 500 / sprite(key).width), C / 2, C / 2)
        out[key] = p
    for key in SPACE:
        im = sprite(f"space_{key}")
        p = scene()
        put(p, scaled(im, 540 / max(im.size)), C / 2, C / 2)
        out[key] = p

    names = [f"star_{i}" for i in range(9)]
    row = Image.new("RGBA", (9 * 216, 216))
    for i, name in enumerate(names):
        row.alpha_composite(sprite(name), (i * 216, 0))
    out["shapes"] = row

    total = 0
    for key, im in out.items():
        path = ART / f"{key}.webp"
        im.save(path, "WEBP", quality=86, method=6)
        total += path.stat().st_size
    print(len(out), "pictures,", total // 1024, "KB")


SKY = constellations()
assert len(SKY) == 20 and sum(len(c["stars"]) for c in SKY) == 150, (len(SKY), sum(len(c["stars"]) for c in SKY))
types = {"colour": {k: S[f"startype.colour.{k}"] for k in sorted({s["colour"] for c in SKY for s in c["stars"]})}, "size": {k: S[f"startype.size.{k}"] for k in sorted({s["size"] for c in SKY for s in c["stars"]})}}
data = {"gameVersion": git("describe", "--tags", "--abbrev=0", REF).strip().lstrip("v"), "constellations": SKY, "starTypes": types, "guide": guide(), "news": news()}
assert not UNSHIPPED & {c["key"] for g in data["guide"].values() for c in g}, "an unshipped mechanic is in the guide"
(ROOT / "data").mkdir(exist_ok=True)
(ROOT / "data" / "game.json").write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("game", data["gameVersion"], "·", len(SKY), "constellations ·", len(data["news"]), "news groups")
art()
