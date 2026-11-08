"""Build 'onua Hand': a lowercase display font drawn with the same pen as the onua wordmark.

Every glyph is a set of centre-line strokes in the wordmark's own coordinate space
(baseline y=132, x-height top y=62, pen ~12 units, heavier 'pressure' strokes ~16).
Strokes are stamped onto a raster with a slightly wandering, round pen, traced,
and written into a TrueType font. Uppercase maps to the lowercase forms, as in the logo.
"""
import math, random, re, sys, os
import numpy as np
import cv2
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

OUT = sys.argv[1]
os.makedirs(OUT, exist_ok=True)

PX = 8.0                 # raster pixels per logo unit
FU = 500 / 70            # font units per logo unit (x-height 70 logo units -> 500 font units)
BASE = 132
SB = 4.5                 # side bearing, logo units

G = {
 "a": ([("M344 77 C330 60 300 62 292 88 C284 112 296 134 316 132 C332 130 342 112 344 90", 11.5),
        ("M292 89 C288 106 294 124 308 131", 16), ("M348 64 C346 90 344 116 351 133 C354 139 359 139 364 134", 12.5)], -284),
 "b": ([("M10 30 C11 60 11 100 10 132", 13), ("M11 98 C18 72 40 60 56 68 C70 76 72 104 64 120 C56 134 32 138 12 128", 11.5),
        ("M58 70 C70 82 70 106 62 120", 15)], 0),
 "c": ([("M58 74 C46 60 22 64 14 88 C8 110 20 134 42 132 C52 131 58 126 62 120", 12), ("M16 82 C8 102 14 124 30 131", 16)], 0),
 "d": ([("M52 78 C38 60 10 62 4 88 C-2 112 10 134 30 132 C44 130 52 114 54 94", 11.5), ("M4 89 C0 106 6 124 20 131", 16),
        ("M56 30 C55 60 54 100 55 120 C56 132 60 136 66 132", 13)], 0),
 "e": ([("M10 100 C30 102 50 100 62 96 C64 72 46 60 30 64 C14 68 6 88 8 106 C10 126 30 136 48 130 C54 128 58 124 62 120", 12),
        ("M10 92 C6 110 14 126 28 131", 15)], 0),
 "f": ([("M54 38 C48 28 30 28 26 44 C22 60 24 100 22 134", 12.5), ("M8 66 C20 64 36 64 50 65", 10)], 0),
 "g": ([("M52 76 C38 60 10 62 4 88 C-2 110 10 130 30 128 C44 126 52 110 54 92", 11.5),
        ("M56 64 C56 100 56 130 54 150 C50 168 22 170 8 156", 12.5), ("M4 89 C0 104 6 120 18 127", 15)], 0),
 "h": ([("M10 30 C11 60 11 100 10 134", 13), ("M11 93 C18 70 40 60 56 68 C68 76 68 96 67 112 C66 122 67 128 71 134", 11.5),
        ("M56 69 C66 77 68 92 67 108", 15.5)], 0),
 "i": ([("M12 66 C13 88 12 112 14 134", 13), ("M13 40 L14 42", 15)], 0),
 "j": ([("M30 66 C31 96 31 130 28 150 C25 164 16 167 10 162", 12.5), ("M31 40 L32 42", 15)], 0),
 "k": ([("M10 30 C11 60 11 100 10 134", 13), ("M52 64 C40 76 26 90 12 102", 11.5), ("M24 92 C34 106 44 122 56 134", 13)], 0),
 "l": ([("M14 30 C15 60 14 100 16 120 C17 132 22 136 30 132", 13)], 0),
 "m": ([("M10 66 C11 88 11 112 9 134", 13), ("M11 92 C16 72 32 62 44 70 C52 76 52 100 52 134", 11),
        ("M52 94 C58 72 74 62 86 70 C94 76 94 100 94 118 C94 126 95 130 98 134", 11), ("M44 70 C52 78 52 96 52 112", 14)], 0),
 "n": ([("M120 66 C121 88 121 112 119 134", 13), ("M121 93 C128 70 150 60 166 68 C178 76 178 96 177 112 C176 122 177 128 181 134", 11.5),
        ("M166 69 C176 77 178 92 177 108", 15.5)], -110),
 "o": ([("M66 60 C40 58 26 82 30 106 C34 128 56 138 74 130 C94 120 100 92 90 74 C84 62 72 58 60 62 C54 64 50 68 48 73", 11.8),
        ("M40 76 C30 96 34 120 52 132", 14.5)], -26),
 "p": ([("M10 66 C11 100 11 130 10 162", 13), ("M11 96 C18 72 40 60 56 68 C70 76 72 104 64 120 C56 134 32 138 12 126", 11.5),
        ("M58 70 C70 82 70 106 62 120", 15)], 0),
 "q": ([("M52 78 C38 60 10 62 4 88 C-2 112 10 134 30 132 C44 130 52 114 54 94", 11.5), ("M4 89 C0 106 6 124 20 131", 16),
        ("M56 64 C55 100 55 140 57 162", 13)], 0),
 "r": ([("M10 66 C11 88 11 112 10 134", 13), ("M11 96 C16 76 30 64 48 66", 11.5)], 0),
 "s": ([("M52 72 C44 62 22 60 16 74 C10 88 24 94 36 98 C50 102 58 110 54 122 C48 136 22 136 10 124", 12),
        ("M36 98 C50 102 58 110 54 120", 15)], 0),
 "t": ([("M24 40 C25 70 24 110 26 122 C28 134 38 136 46 130", 12.5), ("M8 66 C20 64 34 64 46 65", 10)], 0),
 "u": ([("M206 64 C203 88 202 116 218 128 C234 140 260 128 264 100", 11.5), ("M206 100 C206 118 212 128 226 131", 16),
        ("M266 62 C266 90 264 116 272 134", 13)], -196),
 "v": ([("M6 64 C14 88 22 112 32 134 C42 112 50 88 58 64", 12), ("M8 70 C16 92 24 116 32 132", 14)], 0),
 "w": ([("M6 64 C12 88 18 112 26 134 C34 112 40 92 46 78 C52 92 58 112 66 134 C74 112 80 88 86 64", 11.5)], 0),
 "x": ([("M8 64 C24 86 40 110 58 134", 12.5), ("M56 64 C42 86 26 110 8 134", 11.5)], 0),
 "y": ([("M6 64 C14 86 22 106 32 124", 12), ("M58 64 C48 96 38 124 28 148 C24 160 14 166 4 160", 12.5)], 0),
 "z": ([("M10 66 C26 64 42 64 56 66 C42 88 26 110 10 132 C26 134 44 134 60 132", 12)], 0),
 "period": ([("M6 130 L7 131", 15)], 0),
 "comma": ([("M8 128 C10 134 8 142 2 148", 12)], 0),
 "quoteright": ([("M8 40 C10 48 8 56 4 62", 11)], 0),
 "question": ([("M8 50 C14 30 50 30 52 52 C54 70 32 76 30 98", 12), ("M30 128 L31 129", 14)], 0),
 "exclam": ([("M12 32 C13 60 12 86 12 104", 13), ("M12 128 L13 129", 14)], 0),
 "hyphen": ([("M6 104 C18 102 30 102 40 103", 11)], 0),
 "emdash": ([("M6 104 C40 102 80 103 112 102", 10)], 0),
}
CMAP = {chr(c): chr(c) for c in range(ord("a"), ord("z") + 1)}
CMAP.update({chr(c): chr(c + 32) for c in range(ord("A"), ord("Z") + 1)})
CMAP.update({".": "period", ",": "comma", "'": "quoteright", "’": "quoteright", "‘": "quoteright",
             "?": "question", "!": "exclam", "-": "hyphen", "—": "emdash", "–": "hyphen"})


def parse(d):
    toks = re.findall(r"[MLCQ]|-?\d+(?:\.\d+)?", d)
    pts, i, cur, cmd = [], 0, None, None
    segs = []
    while i < len(toks):
        if toks[i] in "MLCQ":
            cmd = toks[i]; i += 1; continue
        n = {"M": 2, "L": 2, "C": 6, "Q": 4}[cmd]
        v = [float(t) for t in toks[i:i + n]]; i += n
        if cmd == "M":
            cur = (v[0], v[1])
        else:
            segs.append((cmd, cur, v)); cur = (v[-2], v[-1])
    out = []
    for cmd, p0, v in segs:
        if cmd == "L":
            ctrl = [p0, (v[0], v[1])]
        elif cmd == "Q":
            ctrl = [p0, (v[0], v[1]), (v[2], v[3])]
        else:
            ctrl = [p0, (v[0], v[1]), (v[2], v[3]), (v[4], v[5])]
        L = sum(math.dist(ctrl[k], ctrl[k + 1]) for k in range(len(ctrl) - 1))
        steps = max(4, int(L / 0.25))
        for s in range(steps + 1):
            t = s / steps
            q = ctrl[:]
            while len(q) > 1:
                q = [((1 - t) * q[k][0] + t * q[k + 1][0], (1 - t) * q[k][1] + t * q[k + 1][1]) for k in range(len(q) - 1)]
            out.append(q[0])
    return out


def glyph_contours(name):
    strokes, dx = G[name]
    rnd = random.Random(name)
    polys = []
    for d, w in strokes:
        pts = [(x + dx, y) for x, y in parse(d)]
        ph = [rnd.uniform(0, 6.28) for _ in range(4)]
        polys.append((pts, w, ph))
    allx = [p[0] for pts, w, _ in polys for p in pts]
    minx = min(allx) - max(w for _, w, _ in polys) / 2
    maxx = max(allx) + max(w for _, w, _ in polys) / 2
    shift = SB - minx
    W = int((maxx - minx + 2 * SB + 4) * PX); H = int(200 * PX)
    img = np.zeros((H, W), np.uint8)
    for pts, w, ph in polys:
        acc = 0.0
        for k, (x, y) in enumerate(pts):
            if k: acc += math.dist(pts[k - 1], pts[k])
            wob = 0.45 * math.sin(acc / 9 + ph[0]) + 0.25 * math.sin(acc / 3.7 + ph[1])
            r = (w / 2) * (1 + 0.05 * math.sin(acc / 11 + ph[2]) + 0.025 * math.sin(acc / 2.9 + ph[3]))
            cx = (x + shift + wob * 0.6) * PX
            cy = (y + 20 + wob * 0.6) * PX
            cv2.circle(img, (int(round(cx)), int(round(cy))), int(round(r * PX)), 255, -1, lineType=cv2.LINE_8)
    img = cv2.GaussianBlur(img, (0, 0), 1.2)
    _, img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    cnts, hier = cv2.findContours(img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)
    contours = []
    for c, h in zip(cnts, hier[0]):
        c = cv2.approxPolyDP(c, 1.1, True)[:, 0, :]
        if len(c) < 3: continue
        fu = [(round(px / PX * FU), round((BASE + 20 - py / PX) * FU)) for px, py in c]
        area = sum(fu[i][0] * fu[(i + 1) % len(fu)][1] - fu[(i + 1) % len(fu)][0] * fu[i][1] for i in range(len(fu))) / 2
        outer = h[3] == -1
        if (outer and area > 0) or (not outer and area < 0):  # TrueType: outer clockwise
            fu = fu[::-1]
        contours.append(fu)
    adv = round((maxx - minx + 2 * SB) * FU)
    return contours, adv


fb = FontBuilder(1000, isTTF=True)
order = [".notdef", "space"] + list(G.keys())
fb.setupGlyphOrder(order)
cmap = {32: "space", 160: "space"}
for ch, g in CMAP.items():
    cmap[ord(ch)] = g
fb.setupCharacterMap(cmap)
glyphs, metrics = {}, {}
for name in order:
    pen = TTGlyphPen(None)
    if name in G:
        contours, adv = glyph_contours(name)
        for c in contours:
            pen.moveTo(c[0])
            for p in c[1:]: pen.lineTo(p)
            pen.closePath()
    else:
        adv = 230 if name == "space" else 500
    glyphs[name] = pen.glyph()
    metrics[name] = (adv, 0)
fb.setupGlyf(glyphs)
for name in order:
    g = glyphs[name]; g.recalcBounds(fb.font["glyf"]) if hasattr(g, "recalcBounds") else None
    metrics[name] = (metrics[name][0], getattr(g, "xMin", 0) or 0)
fb.setupHorizontalMetrics(metrics)
fb.setupHorizontalHeader(ascent=800, descent=-260)
fb.setupNameTable({"familyName": "onua Hand", "styleName": "Regular", "copyright": "Drawn for ONUA, 2026",
                   "uniqueFontIdentifier": "onua-hand-1.0", "fullName": "onua Hand Regular", "psName": "onuaHand-Regular",
                   "version": "Version 1.000"})
fb.setupOS2(sTypoAscender=800, sTypoDescender=-260, usWinAscent=880, usWinDescent=300, sxHeight=500, sCapHeight=500)
fb.setupPost()
fb.save(f"{OUT}/onua-hand.ttf")
fb.font.flavor = "woff"
fb.font.save(f"{OUT}/onua-hand.woff")
print("glyphs", len(order), os.path.getsize(f"{OUT}/onua-hand.woff"), "bytes woff")
