#!/usr/bin/env python3
"""The Living Past — render the ACCURATE stratigraphic column from geology_hellcreek.json.

The structure (layer order, relative thickness, feature placement) is the accuracy moat and
is built here in code from real Hell Creek / Fox Hills geology. MJ only supplies texture per
band (each layer's `mjTexture`). This column is the spec for the poster's soil cutaway, an
accuracy key, and a web element.

    python3 tools/render_strata.py
"""
from __future__ import annotations
import json, math, pathlib
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
LP = ROOT / "living_past"
SPEC = json.loads((LP / "geology_hellcreek.json").read_text())

W, H = 940, 1340
BG = (20, 18, 12)
BRASS = (216, 181, 122); IVORY = (246, 236, 212); MUTED = (169, 156, 127)
COAL = (23, 16, 9)
CX0, CX1 = 60, 430           # column x-span
CTOP, CBOT = 150, 1210       # column y-span
LABX = 470


def _hex(h): h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def fnt(name, size):
    paths = {
        "optima": ["/System/Library/Fonts/Optima.ttc", "/System/Library/Fonts/Supplemental/Optima.ttc"],
        "cinzel": [str(LP / "fonts/Cinzel-SemiBold.ttf"), str(LP / "fonts/Cinzel-Regular.ttf")],
        "gara":   [str(LP / "fonts/EBGaramond-Italic.ttf")],
    }
    for p in paths[name]:
        try: return ImageFont.truetype(p, size)
        except Exception: continue
    return ImageFont.load_default()


def mottle(d, box, base, seed):
    import random; random.seed(seed)
    x0, y0, x1, y1 = box
    for _ in range(int((x1 - x0) * (y1 - y0) / 55)):
        x = random.uniform(x0, x1); y = random.uniform(y0, y1)
        dv = random.randint(-26, 22)
        c = tuple(max(0, min(255, base[i] + dv)) for i in range(3))
        r = random.uniform(1.2, 3.4)
        d.ellipse((x - r, y - r, x + r, y + r), fill=c)


def crossbed(d, box, base, seed):
    import random; random.seed(seed)
    x0, y0, x1, y1 = box
    dark = tuple(max(0, base[i] - 30) for i in range(3))
    y = y0
    while y < y1:
        for x in range(x0, x1, 3):
            yy = y + ((x - x0) * 0.18) % 12
            if yy < y1: d.point((x, yy), fill=dark)
        y += 9


def roots(d, x0, x1, ytop, depth, seed):
    import random; random.seed(seed)
    for _ in range(int((x1 - x0) / 46)):
        x = random.uniform(x0 + 10, x1 - 10); y = ytop
        dy = random.uniform(depth * 0.5, depth)
        n = 10
        for i in range(n):
            ny = y + dy / n; nx = x + random.uniform(-4, 4)
            w = max(1, int(3 * (1 - i / n)))
            d.line((x, y, nx, ny), fill=(150, 120, 74, 220), width=w)
            x, y = nx, ny
            if random.random() < 0.25:
                d.line((x, y, x + random.uniform(-12, 12), y + random.uniform(4, 12)), fill=(150, 120, 74, 150), width=1)


def burrow(d, cx, cy):
    d.arc((cx - 26, cy - 10, cx + 26, cy + 34), 200, 340, fill=(30, 22, 14), width=7)
    d.arc((cx - 26, cy - 10, cx + 26, cy + 34), 200, 340, fill=(120, 96, 60), width=2)


def egg_clutch(d, cx, cy):
    d.arc((cx - 34, cy - 6, cx + 34, cy + 40), 0, 180, fill=(70, 56, 34), width=3)
    for i, ox in enumerate((-20, -8, 5, 18, -6)):
        oy = cy + (6 if i == 4 else 14)
        d.ellipse((cx + ox - 7, oy - 9, cx + ox + 7, oy + 9), fill=(228, 214, 180), outline=(150, 120, 74), width=1)


def wavy(d, y):
    pts = [(CX0, y + 6 * math.sin(x / 26)) for x in range(0, CX1 - CX0 + 1, 6)]
    pts = [(CX0 + i * 6, yy) for i, (x, yy) in enumerate(pts)]
    d.line(pts, fill=(44, 35, 24), width=5)
    d.line([(x, y2 - 2) for x, y2 in pts], fill=BRASS, width=1)


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img, "RGBA")
    f_title = fnt("cinzel", 24); f_sub = fnt("gara", 17)
    f_name = fnt("optima", 17); f_lith = fnt("optima", 12); f_env = fnt("gara", 13); f_tiny = fnt("optima", 11)

    d.text((60, 42), "STRATIGRAPHY · 66 Ma", font=f_title, fill=IVORY)
    d.text((62, 82), "Hell Creek Formation over Fox Hills Sandstone — western North America", font=f_sub, fill=BRASS)
    d.text((62, 108), "structure accurate (code) · texture per band = Midjourney", font=f_tiny, fill=MUTED)

    layers = SPEC["layers"]
    total = sum(l["relThickness"] for l in layers)
    col_h = CBOT - CTOP

    # pre-impact note above the surface
    d.text((CX0, CTOP - 26), "▲ living land surface — no K–Pg layer yet (asteroid still in the sky)",
           font=f_tiny, fill=(200, 150, 120))

    y = CTOP
    slots = len(layers)
    for i, l in enumerate(layers):
        h = l["relThickness"] / total * col_h
        base = _hex(l["color"])
        box = (CX0, y, CX1, y + h)
        d.rectangle(box, fill=base)
        feats = l.get("features", [])
        seed = i * 7 + 3

        if "unconformity" in feats:
            wavy(d, y + h / 2)
        elif l["lithology"].startswith("lignite"):
            d.rectangle(box, fill=COAL)
            for gx in range(CX0, CX1, 26):
                d.line((gx, y + h * 0.4, gx + 16, y + h * 0.6), fill=(120, 92, 40), width=1)
        elif "crossbed" in feats:
            crossbed(d, box, base, seed)
        elif "marine" in feats:
            for yy in range(int(y) + 4, int(y + h), 6):
                d.line((CX0, yy, CX1, yy), fill=tuple(max(0, c - 16) for c in base), width=1)
            mottle(d, box, base, seed)
        else:
            mottle(d, box, base, seed)

        if "roots" in feats:
            roots(d, CX0, CX1, y, min(h, 60), seed)
        if "burrow" in feats:
            burrow(d, CX1 - 70, y + h * 0.5)
        if "egg_clutch" in feats:
            egg_clutch(d, CX0 + 90, y + h * 0.45)
        if "ash" in feats:
            d.text((CX0 + 6, y + h / 2), "▲ ash from the volcano", font=f_tiny, fill=(40, 40, 30), anchor="lm")

        # right-side label at an evenly spaced slot, with a leader
        slot_y = CTOP + (i + 0.5) * col_h / slots
        band_cy = y + h / 2
        d.line((CX1, band_cy, CX1 + 14, band_cy), fill=(*BRASS, 150), width=1)
        d.line((CX1 + 14, band_cy, LABX - 8, slot_y), fill=(*BRASS, 90), width=1)
        d.text((LABX, slot_y - 15), l["name"], font=f_name, fill=IVORY)
        d.text((LABX, slot_y + 4), l["lithology"], font=f_lith, fill=BRASS)
        d.text((LABX, slot_y + 20), l["environment"], font=f_env, fill=MUTED)

        y += h

    # footer
    d.line((60, CBOT + 26, W - 60, CBOT + 26), fill=(*BRASS, 70), width=1)
    d.text((60, CBOT + 40),
           "Older marine rocks (Fox Hills, Pierre) sit below — the sea was here before the coast built out.",
           font=f_env, fill=MUTED)
    d.text((60, CBOT + 64),
           "MJ texture prompts per band live in living_past/geology_hellcreek.json.",
           font=f_tiny, fill=MUTED)

    out = LP / "plates" / "_strata_accurate.png"
    img.save(out)
    print(f"wrote {out} ({W}x{H}) · {len(layers)} layers")


if __name__ == "__main__":
    main()
