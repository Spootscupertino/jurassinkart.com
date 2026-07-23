#!/usr/bin/env python3
"""The Living Past — clad the base-plate v2 cliff with the ACCURATE Hell Creek strata.

Structure (layer order + relative thickness) comes from geology_hellcreek.json — the moat.
Each layer's MJ texture tile is reprojected onto the cliff using the plate's own luminance,
so the strata follow the eroded 3D form instead of looking like pasted stripes. Textures that
haven't been generated yet fall back to the layer's spec colour, so this improves as tiles land.

    python3 tools/composite_strata.py            # writes _proof_scene_strata.png (preview)
    python3 tools/composite_strata.py --promote  # also overwrite _proof_scene.png (poster)
"""
from __future__ import annotations
import json, sys, pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
LP = ROOT / "living_past"
PLATES = LP / "plates"
SPEC = json.loads((LP / "geology_hellcreek.json").read_text())

W, H = 1800, 1200
WATER = 0.50          # above/below split on v2
COAST = 0.62          # land/deep divide (underwater)
CLIFF_TOP = 0.49      # strata start just under the terrace lip
CLIFF_BOT = 0.99

# layer id -> texture tile (reused where lithology repeats). Missing files -> spec colour.
TEXMAP = {
    "L01": "tex_topsoil", "L02": "tex_mudstone", "L03": "tex_lignite", "L04": "tex_sandstone",
    "L05": "tex_paleosol", "L06": "tex_bentonite", "L07": "tex_mudstone", "L08": "tex_sandstone",
    "U01": None, "L09": "tex_foxhills", "L10": "tex_pierre",
}


def _hex(h): h = h.lstrip("#"); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def load_fit(name, size):
    im = Image.open(PLATES / name).convert("RGB")
    tw, th = size
    s = max(tw / im.width, th / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x = (im.width - tw) // 2; y = (im.height - th) // 2
    return im.crop((x, y, x + tw, y + th))


def tex_or_color(layer, size):
    """Return an (h,w,3) float array for the band: the MJ texture cover-fit, else spec colour."""
    tw, th = size
    tid = TEXMAP.get(layer["id"])
    if tid and (PLATES / f"{tid}.png").exists():
        arr = np.asarray(load_fit(f"{tid}.png", size)).astype(np.float32)
        return arr, True
    col = np.array(_hex(layer["color"]), np.float32)
    arr = np.empty((th, tw, 3), np.float32); arr[:] = col
    arr += np.random.default_rng(3).normal(0, 6, (th, tw, 3))   # a little grain
    return np.clip(arr, 0, 255), False


def cliff_mask(base):
    """Earth of the exposed cross-section: below the waterline, minus open water AND the
    bright turquoise shallows, with a fade toward the deep so strata don't stripe the sea."""
    r, g, b = base[..., 0], base[..., 1], base[..., 2]
    lum = base.mean(axis=2)
    blue_excess = b - (r + g) / 2.0
    cyan = (g + b) / 2.0 - r
    ys = np.arange(H)[:, None]; xs = np.arange(W)[None, :]
    below = ys > int(H * (WATER + 0.005))
    open_water = (blue_excess > 16) & (xs > int(W * (COAST - 0.04)))
    turquoise = (cyan > 26) & (lum > 120)          # the bright shallows
    m = (below & ~open_water & ~turquoise).astype(np.float32)
    # fade out toward the right/deep so any residual doesn't paint the sea
    fade = np.clip((int(W * (COAST + 0.06)) - xs) / (W * 0.14), 0, 1).astype(np.float32)
    m *= fade
    mimg = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))
    return np.asarray(mimg).astype(np.float32) / 255.0


def main():
    promote = "--promote" in sys.argv
    base_img = load_fit("base_plate_v2.png", (W, H))
    base = np.asarray(base_img).astype(np.float32)
    gray = base.mean(axis=2)
    mask = cliff_mask(base)
    out = base.copy()

    layers = SPEC["layers"]
    total = sum(l["relThickness"] for l in layers)
    y_top, y_bot = int(H * CLIFF_TOP), int(H * CLIFF_BOT)
    span = y_bot - y_top

    # 1) build the FLAT strata stack (each band = its texture), then extend past the ends
    strata = np.zeros((H, W, 3), np.float32)
    used = []; bounds = []; y = y_top
    for l in layers:
        h = max(4, round(l["relThickness"] / total * span))
        y0, y1 = y, min(y_bot, y + h)
        tex, real = tex_or_color(l, (W, y1 - y0))
        strata[y0:y1] = tex
        bounds.append((l, y0, y1)); used.append((l["id"], "tex" if real else "color")); y = y1
    strata[:y_top] = strata[y_top]; strata[y_bot:] = strata[y_bot - 1]

    # 2) warp the stack vertically per column: a gentle dip + undulation so strata aren't
    #    ruler-straight but follow a natural bedding line
    xs = np.arange(W)
    off = (72 * (xs / W) + 13 * np.sin(2 * np.pi * xs / 560)
           + 7 * np.sin(2 * np.pi * xs / 190 + 1.3)).astype(int)
    yy, xx = np.mgrid[0:H, 0:W]
    src_y = np.clip(yy - off[None, :], 0, H - 1)
    strata_w = strata[src_y, xx]

    # 3) relight the warped strata by the cliff's own luminance (keeps the 3D eroded form)
    m_sel = mask > 0.25
    mean = gray[m_sel].mean() if m_sel.any() else 128.0
    shade = np.clip(gray / mean, 0.5, 1.7)[..., None]
    clad = np.clip(strata_w * shade, 0, 255)
    a = (mask * 0.82)[..., None]
    out = base * (1 - a) + clad * a

    out_img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))

    # 4) subtle warped bedding lines + the pale ash accent, masked to the cliff
    d = ImageDraw.Draw(out_img, "RGBA")
    mask_u8 = (mask * 255).astype(np.uint8)
    for l, y0, y1 in bounds:
        for x in range(0, W, 2):
            yb = y0 + off[x]
            if 0 <= yb < H and mask_u8[yb, x] > 80:
                d.point((x, yb), fill=(18, 12, 7, 110))
        if "ash" in l.get("features", []):
            ymid = (y0 + y1) // 2
            for x in range(0, W, 2):
                ya = ymid + off[x]
                if 0 <= ya < H and mask_u8[ya, x] > 80:
                    d.point((x, ya), fill=(206, 202, 178, 160))

    # depth-zone hairlines + asteroid whisper (same furniture as compose_proof)
    from PIL import ImageFont
    def font(p, s):
        try: return ImageFont.truetype(p, s)
        except Exception: return ImageFont.load_default()
    lab = font("/System/Library/Fonts/Optima.ttc", 15)
    brass = (216, 181, 122)
    x0 = int(W * 0.62)
    for name, yf in [("SUNLIT", 0.57), ("TWILIGHT", 0.71), ("DEEP", 0.85)]:
        yy = int(H * yf)
        for x in range(x0, W):
            a = int(130 * (x - x0) / (W - x0))
            d.point((x, yy), fill=(*brass, a))
        d.text((W - 16, yy - 18), name, font=lab, fill=(*brass, 200), anchor="ra")

    out_path = PLATES / "_proof_scene_strata.png"
    out_img.save(out_path)
    print(f"wrote {out_path}")
    print("layers:", ", ".join(f"{i}:{k}" for i, k in used))
    if promote:
        out_img.save(PLATES / "_proof_scene.png")
        print("promoted -> _proof_scene.png")


if __name__ == "__main__":
    main()
