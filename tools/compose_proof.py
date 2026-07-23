#!/usr/bin/env python3
"""The Living Past — quick PIL proof-composite of the scene (no Photoshop needed).

Assembles the environment plates into the locked scene layout so we can eyeball the
world before the real PS composite: base plate foundation, abyssal void deepened into
the lower-right ocean, depth-zone hairlines fading from the right edge, asteroid
whisper top-left, and the real Cinzel title. Proof only — the finished art is built
in Photoshop.

    python3 tools/compose_proof.py
"""
from __future__ import annotations
import json, pathlib
from PIL import Image, ImageDraw, ImageFont, ImageChops

ROOT = pathlib.Path(__file__).resolve().parent.parent
LP = ROOT / "living_past"
PLATES = LP / "plates"
TOK = json.loads((LP / "template/design_tokens.json").read_text())
C = TOK["color"]

W = 1800                          # proof width
H = round(W * 2 / 3)              # 3:2 scene
BASE_NAME = "base_plate_v2.png"  # v2: flat T. rex terrace + natural dark deep (2026-07-10)
COAST = 0.62                      # land/deep vertical split on v2 (underwater)
WATER = 0.50                      # above/below waterline split on v2


def _hex(h):
    h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def load_fit(name, size):
    im = Image.open(PLATES / name).convert("RGB")
    # cover-fit into size
    tw, th = size
    s = max(tw / im.width, th / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - tw) // 2; y = (im.height - th) // 2
    return im.crop((x, y, x + tw, y + th))


def ramp_v(h, start_frac, top=0, bot=255):
    """1×h vertical ramp: 0 above start_frac, linear to bot below."""
    col = []
    s = int(h * start_frac)
    for y in range(h):
        col.append(top if y < s else round(bot * (y - s) / max(1, h - s)))
    img = Image.new("L", (1, h)); img.putdata(col)
    return img.resize((W, h))


def ramp_h(w, start_frac):
    """w×1 horizontal ramp: 0 left of start_frac, linear to 255 at right."""
    row = []
    s = int(w * start_frac)
    for x in range(w):
        row.append(0 if x < s else round(255 * (x - s) / max(1, w - s)))
    img = Image.new("L", (w, 1)); img.putdata(row)
    return img.resize((w, H))


def font(path, size):
    try:
        return ImageFont.truetype(str(path), size)
    except Exception:
        return ImageFont.load_default()


def main():
    base = load_fit(BASE_NAME, (W, H))
    scene = base

    # v2 already has a naturally dark deep on the right; just deepen the far lower-right
    # corner so it reads as a true black plunge for the Mosasaurus (keep the god-ray).
    ocean = ImageChops.multiply(ramp_v(H, WATER + 0.04), ramp_h(W, COAST - 0.02))
    ocean = ocean.point(lambda v: min(255, int(v * 1.6)))
    scene = Image.composite(Image.new("RGB", (W, H), (4, 9, 13)), scene, ocean)

    d = ImageDraw.Draw(scene, "RGBA")
    brass = _hex(C["brass_hi"]); ivory = _hex(C["ink_ivory"])

    # depth-zone hairlines fading in from the right edge (locked #8)
    optima = "/System/Library/Fonts/Optima.ttc"
    lab_f = font(optima, 15)
    zones = [("SUNLIT", 0.57), ("TWILIGHT", 0.71), ("DEEP", 0.85), ("OCEAN FLOOR", 0.96)]
    x0 = int(W * 0.62)
    for name, yf in zones:
        y = int(H * yf)
        if yf < 0.95:
            for x in range(x0, W):
                a = int(150 * (x - x0) / (W - x0))
                d.point((x, y), fill=(*brass, a))
        d.text((W - 18, y - 20), name, font=lab_f, fill=(*brass, 210), anchor="ra")

    # asteroid whisper — faint cold point top-left (locked #7)
    ax, ay = int(W * 0.13), int(H * 0.11)
    d.line((ax, ay, ax + 26, ay + 14), fill=(223, 233, 255, 70), width=1)
    d.ellipse((ax - 3, ay - 3, ax + 3, ay + 3), fill=(244, 247, 255, 220))

    # (title is added as crisp HTML furniture in poster_mockup.html, not baked here)

    out = PLATES / "_proof_scene.png"
    scene.save(out)
    print(f"wrote {out} ({W}x{H})")


if __name__ == "__main__":
    main()
