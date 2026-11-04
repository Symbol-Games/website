#!/usr/bin/env python3
"""Builds the site's self-hosted fonts: make_fonts.py <titan.ttf> <archivo-black.ttf> <archivo.ttf> <archivo-narrow.ttf> <dynapuff.ttf>

Needs fonttools and brotli. All five fonts are under the SIL Open Font License. Titan One lacks the capital dotted I that Turkish
headings need, so it gets one here; its licence reserves the name "Titan", so the changed font is published as "Symbol Display".
"""
import pathlib
import sys

from fontTools import subset
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

OUT = pathlib.Path(__file__).resolve().parent.parent / "fonts"
UNICODES = [*range(0x20, 0x7F), *range(0xA0, 0x180), 0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026, 0x2192, 0x2212, 0x20BA]
TURKISH = "şŞğĞıİöÖüÜçÇ’"


def add_dotted_i(font):
    """Draws U+0130: the font's own I, and the dot it puts on Ż, centred over the I."""
    glyphs, cmap = font.getGlyphSet(), font.getBestCmap()
    assert 0x130 not in cmap, "the font already has it: drop this step"
    rec = RecordingPen()
    glyphs[cmap[0x17B]].draw(rec)
    contours, cur = [], []
    for op in rec.value:
        cur.append(op)
        if op[0] in ("closePath", "endPath"):
            contours.append(cur)
            cur = []
    top = BoundsPen(glyphs)
    glyphs[cmap[0x5A]].draw(top)  # Z
    def ys(c):
        return [p[1] for _, args in c for p in args if p is not None]
    dot = [c for c in contours if min(ys(c)) >= top.bounds[3]]
    assert len(dot) == 1, f"expected one dot above Z, found {len(dot)}"
    i_box = BoundsPen(glyphs)
    glyphs[cmap[0x49]].draw(i_box)
    xs = [p[0] for _, args in dot[0] for p in args if p is not None]
    dx = (i_box.bounds[0] + i_box.bounds[2]) / 2 - (min(xs) + max(xs)) / 2
    pen = TTGlyphPen(glyphs)
    glyphs[cmap[0x49]].draw(pen)
    moved = TransformPen(pen, (1, 0, 0, 1, round(dx), 0))
    for name, args in dot[0]:
        getattr(moved, name)(*args)
    font["glyf"]["Idotaccent"] = pen.glyph()
    order = font.getGlyphOrder()
    if "Idotaccent" not in order:  # the glyf table may have added it already
        font.setGlyphOrder([*order, "Idotaccent"])
    font["hmtx"]["Idotaccent"] = font["hmtx"][cmap[0x49]]
    for table in font["cmap"].tables:
        if table.isUnicode():
            table.cmap[0x130] = "Idotaccent"


def rename(font, family):
    for rec in font["name"].names:
        if rec.nameID in (1, 16):
            rec.string = family
        elif rec.nameID == 3:
            rec.string = f"{family};symbolinteractive.com.tr"
        elif rec.nameID == 4:
            rec.string = family
        elif rec.nameID == 6:
            rec.string = family.replace(" ", "") + "-Regular"
        elif rec.nameID == 2:
            rec.string = "Regular"


def save(font, name):
    opts = subset.Options(layout_features=["*"], name_IDs=["*"], notdef_outline=True, hinting=False, ignore_missing_unicodes=True)
    opts.drop_tables += ["hdmx", "VDMX", "LTSH", "DSIG"]  # device tables: useless on the web
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=UNICODES)
    sub.subset(font)
    font.flavor = "woff2"
    path = OUT / name
    font.save(path)
    print(name, path.stat().st_size, "bytes")
    return path


titan, black, archivo, narrow, puff = sys.argv[1:6]

f = TTFont(titan)
add_dotted_i(f)
rename(f, "Symbol Display")
out = save(f, "SymbolDisplay.woff2")
check = TTFont(out).getBestCmap()
missing = [c for c in TURKISH if ord(c) not in check]
assert not missing, f"the display font lacks {missing}"

save(TTFont(black), "ArchivoBlack.woff2")
save(instancer.instantiateVariableFont(TTFont(archivo), {"wdth": 100, "wght": (400, 700)}), "Archivo.woff2")
save(TTFont(narrow), "ArchivoNarrow.woff2")  # only a weight axis, small enough as it is
save(TTFont(puff), "DynaPuff.woff2")
