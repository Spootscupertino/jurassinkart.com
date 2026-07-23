#!/usr/bin/env python3
"""The Living Past — composition study: 3 focal points, true black abyss, blocked geology.

NOT the finished art. This is a planning/scale study on top of the base plate to test the
"balance scale around the flat land" thesis before any real PS work or T. rex generation:

  * #6  TRUE BLACK ABYSS — the void plate composited hard into the lower-right so the lit
        reef is crushed into a real plunge (this part is real, promotable to the composite).
  * #5  GEOLOGY (blocked) — accurate horizontal sedimentary strata banded onto the earth
        (real), plus labelled zones for the root web / burrow / buried egg clutch (the
        organic bits are flagged for MJ/PS, never faked here).
  * FLAT-LAND TERRACE — a translucent footprint showing how much flat top surface the
        T. rex actually needs (from scale_calc), because the current lip is far too thin.
  * 3 FOCAL POINTS at true scale — (1) T. rex on the terrace, (2) the volcano, (3) the
        Mosasaurus rising out of the new black abyss.

    python3 tools/compose_study.py
"""
from __future__ import annotations
import json, pathlib
from PIL import Image, ImageDraw, ImageFont, ImageChops

ROOT = pathlib.Path(__file__).resolve().parent.parent
LP = ROOT / "living_past"
PLATES = LP / "plates"
TOK = json.loads((LP / "template/design_tokens.json").read_text())
C = TOK["color"]

W = 1800
H = round(W * 2 / 3)                      # 1200 — 3:2 scene
COAST = 0.47                              # land/ocean vertical seam
WATER = 0.31                              # sea-surface line (right side)
# proof scale: master px_per_m (270) shrunk from the 10800px master to this proof width
PX_PER_M = TOK["scale"]["px_per_m"] * W / TOK["canvas"]["trim_px"][0]   # 45 px/m


def _hex(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def load_fit(name, size):
    im = Image.open(PLATES / name).convert("RGB")
    tw, th = size
    s = max(tw / im.width, th / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - tw) // 2; y = (im.height - th) // 2
    return im.crop((x, y, x + tw, y + th))


def ramp_v(h, start_frac, bot=255):
    s = int(h * start_frac)
    col = [0 if y < s else round(bot * (y - s) / max(1, h - s)) for y in range(h)]
    img = Image.new("L", (1, h)); img.putdata(col)
    return img.resize((W, h))


def ramp_h(w, start_frac, invert=False):
    s = int(w * start_frac)
    row = [0 if x < s else round(255 * (x - s) / max(1, w - s)) for x in range(w)]
    if invert:
        row = [255 - v for v in row]
    img = Image.new("L", (w, 1)); img.putdata(row)
    return img.resize((w, H))


def font(size):
    for p in ("/System/Library/Fonts/Optima.ttc",
              "/System/Library/Fonts/Supplemental/Optima.ttc"):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def earth_mask(base):
    """Warm-earth selection: where the plate is tan/brown cliff (not sky, not ocean).
    r > b and mid-bright → the eroded interior. Feathered slightly."""
    r, g, b = base.split()
    px = base.load()
    m = Image.new("L", (W, H), 0)
    mp = m.load()
    for y in range(0, H, 2):
        for x in range(0, W, 2):
            R, G, B = px[x, y]
            if R > B + 18 and 45 < R < 215 and G > B - 5:
                mp[x, y] = 255
                mp[min(W - 1, x + 1), y] = 255
                mp[x, min(H - 1, y + 1)] = 255
                mp[min(W - 1, x + 1), min(H - 1, y + 1)] = 255
    return m.filter_() if hasattr(m, "filter_") else m


def strata(scene, mask):
    """Accurate-looking horizontal sedimentary banding, masked to the earth only."""
    band = Image.new("RGB", (W, H))
    bd = ImageDraw.Draw(band)
    y = int(H * 0.30)
    i = 0
    import random
    random.seed(7)
    while y < int(H * 0.66):
        thick = random.randint(10, 26)
        # alternating warm sediment tones, subtle
        tone = [(70, 52, 30), (96, 72, 42), (58, 42, 24), (110, 86, 52)][i % 4]
        dip = random.randint(-6, 10)                 # gentle strata dip across width
        bd.polygon([(0, y), (W, y + dip), (W, y + dip + thick), (0, y + thick)], fill=tone)
        # crisp bedding line at the top of each band
        bd.line([(0, y), (W, y + dip)], fill=(30, 22, 12), width=2)
        y += thick
        i += 1
    scene = Image.composite(Image.blend(scene, band, 0.55), scene, mask)
    return scene


def silhouette(d, pts, box, fill, outline):
    x0, y0, w, h = box
    poly = [(x0 + px * w, y0 + py * h) for px, py in pts]
    d.polygon(poly, fill=fill, outline=outline)
    return poly


TREX = [(0.00,0.60),(0.30,0.46),(0.52,0.40),(0.66,0.34),(0.72,0.22),(0.80,0.14),
        (0.88,0.12),(1.00,0.18),(1.00,0.24),(0.86,0.26),(0.78,0.30),(0.74,0.42),
        (0.72,0.56),(0.70,0.92),(0.74,0.94),(0.66,0.94),(0.66,0.56),(0.60,0.50),
        (0.56,0.60),(0.52,0.96),(0.58,0.98),(0.46,0.98),(0.48,0.54),(0.30,0.56)]
MOSA = [(1.00,0.48),(0.90,0.34),(0.82,0.44),(0.60,0.40),(0.36,0.34),(0.16,0.30),
        (0.04,0.30),(0.00,0.40),(0.06,0.48),(0.20,0.48),(0.34,0.52),(0.30,0.66),
        (0.40,0.54),(0.58,0.56),(0.60,0.70),(0.68,0.56),(0.82,0.54),(0.90,0.60)]


def focal_tag(d, x, y, n, label, f):
    d.ellipse((x-14, y-14, x+14, y+14), fill=(11, 13, 14, 235), outline=(*_hex(C["brass_hi"]), 255), width=2)
    d.text((x, y), n, font=f, fill=(*_hex(C["brass_hi"]), 255), anchor="mm")
    d.text((x+22, y), label, font=f, fill=(*_hex(C["ink_ivory"]), 235), anchor="lm")


def main():
    base = load_fit("base_plate.png", (W, H))
    void = load_fit("abyssal_void.png", (W, H))
    brass = _hex(C["brass_hi"]); ivory = _hex(C["ink_ivory"]); abyss = _hex(C["abyss"])

    # ---- #6 TRUE BLACK ABYSS ------------------------------------------------
    # composite void below waterline & right of coast, ramping up to the lower-right
    m = ImageChops.multiply(ramp_v(H, WATER + 0.02), ramp_h(W, COAST - 0.02))
    m = m.point(lambda v: min(255, int(v * 1.25)))
    scene = Image.composite(void, base, m)
    # depth-darken the WHOLE right ocean column so sunlit stays bright but twilight→deep
    # genuinely fall to black (the base plate's water never dims with depth on its own)
    ocean = ImageChops.multiply(ramp_v(H, WATER), ramp_h(W, COAST - 0.02))
    ocean = ocean.point(lambda v: min(255, int(v * 2.4)))
    scene = Image.composite(Image.new("RGB", (W, H), (4, 9, 13)), scene, ocean)

    # ---- #5 GEOLOGY (real strata + flagged organic zones) -------------------
    em = earth_mask(base)
    scene = strata(scene, em)

    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(over, "RGBA")
    f_lab = font(15); f_sm = font(13); f_n = font(15); f_tag = font(17)

    # geology zone callouts (organic bits — blocked, to be composited in PS/MJ)
    def zone(x, y, label):
        d.ellipse((x-4, y-4, x+4, y+4), outline=(*brass, 230), width=2)
        for a in range(0, 360, 45):
            pass
        d.line((x, y, x+18, y-18), fill=(*brass, 150), width=1)
        d.text((x+20, y-30), label, font=f_sm, fill=(*brass, 235), anchor="lm")
    zone(int(W*0.14), int(H*0.44), "root web")
    zone(int(W*0.30), int(H*0.55), "burrow")
    zone(int(W*0.10), int(H*0.60), "buried egg clutch")
    zone(int(W*0.24), int(H*0.40), "sediment strata")

    # ---- FLAT-LAND TERRACE the T. rex actually needs ------------------------
    trex_len = 13 * PX_PER_M                       # 585 px true length on this proof
    terr_top = int(H * 0.30); terr_bot = int(H * 0.45)
    terr_x1 = int(W * 0.02); terr_x2 = int(W * 0.02 + trex_len + 60)
    d.rectangle((terr_x1, terr_top, terr_x2, terr_bot), fill=(*brass, 34), outline=(*brass, 170), width=2)
    for hx in range(terr_x1, terr_x2, 22):         # hatch = "proposed fill"
        d.line((hx, terr_top, hx+14, terr_bot), fill=(*brass, 45), width=1)
    d.text((terr_x1+10, terr_top-18), "EXTEND FLAT TERRACE — T. REX STAGE  (current lip ≈¼ of this)",
           font=f_sm, fill=(*brass, 240), anchor="lm")

    # ---- 3 FOCAL POINTS at true scale ---------------------------------------
    # (1) T. rex on the terrace, feet at the terrace floor
    tb = (terr_x1+30, terr_bot-int(trex_len*0.52), trex_len, int(trex_len*0.52))
    silhouette(d, TREX, tb, fill=(*ivory, 60), outline=(*ivory, 245))
    # (3) Mosasaurus rising from the abyss (true scale, ~17 m)
    mlen = 17 * PX_PER_M
    mb = (int(W*0.52), int(H*0.52), mlen, int(mlen*0.30))
    silhouette(d, MOSA, mb, fill=(210, 232, 240, 55), outline=(*ivory, 225))

    # focal tags
    focal_tag(d, int(W*0.09), int(H*0.24), "1", "T. REX", f_tag)
    focal_tag(d, int(W*0.55), int(H*0.12), "2", "VOLCANO", f_tag)
    focal_tag(d, int(W*0.74), int(H*0.46), "3", "MOSASAURUS", f_tag)
    # a faint balance baseline linking the three masses
    d.line([(int(W*0.24), int(H*0.34)), (int(W*0.55), int(H*0.16)), (int(W*0.74), int(H*0.55))],
           fill=(*brass, 90), width=1)

    # depth-zone hairlines fading from the right (locked #8)
    x0 = int(W * 0.60)
    for name, yf in [("SUNLIT",0.42),("TWILIGHT",0.60),("DEEP",0.78),("OCEAN FLOOR",0.94)]:
        yy = int(H*yf)
        if yf < 0.94:
            for x in range(x0, W):
                a = int(140 * (x-x0)/(W-x0))
                d.point((x, yy), fill=(*brass, a))
        d.text((W-16, yy-18), name, font=f_lab, fill=(*brass, 205), anchor="ra")

    # asteroid whisper (locked #7)
    ax, ay = int(W*0.13), int(H*0.09)
    d.line((ax, ay, ax+26, ay+14), fill=(223, 233, 255, 70), width=1)
    d.ellipse((ax-3, ay-3, ax+3, ay+3), fill=(244, 247, 255, 220))

    scene = Image.alpha_composite(scene.convert("RGBA"), over).convert("RGB")

    # study banner
    d2 = ImageDraw.Draw(scene, "RGBA")
    d2.rectangle((0, 0, W, 26), fill=(11, 13, 14, 210))
    d2.text((12, 13), "COMPOSITION STUDY — scale balance · black abyss · blocked geology  (not final art)",
            font=f_sm, fill=(*brass, 235), anchor="lm")

    out = PLATES / "_composition_study.png"
    scene.save(out)
    print(f"wrote {out} ({W}x{H})  px_per_m(proof)={PX_PER_M:.1f}  trex={trex_len:.0f}px  mosa={mlen:.0f}px")


if __name__ == "__main__":
    main()
