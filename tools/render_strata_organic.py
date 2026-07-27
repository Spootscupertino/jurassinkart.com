#!/usr/bin/env python3
"""The Living Past — non-uniform strata ribbon (#24).

Eric, 2026-07-27: *"even diving into the strata layers, blending a couple of each will make it
look more lifelike and non-uniform, which is what soil actually looks like."*

He's right, and the old renderer had two structural reasons it looked like wallpaper:
  1. **8 texture tiles cover 11 layers** — `tex_mudstone` is used for BOTH L02 and L07, and
     `tex_sandstone` for BOTH L04 and L08, so those bands were pixel-identical twins.
  2. **Each band was one flat cover-fit** of a single tile, with ruler-straight boundaries.

Real sediment is none of those things. This renderer keeps the accuracy moat untouched — layer
order and relative thickness still come from `geology_hellcreek.json` and are never invented —
but breaks the uniformity:

  * **Two or three variants per layer**, made by cropping different regions of the tile and
    flipping/rotating them, cross-faded through smooth low-frequency noise. Repeated lithologies
    get different crops and a different jitter seed, so L02 and L07 stop being twins.
  * **Wavy boundaries.** Each contact is displaced by low-frequency noise (a real bed contact
    undulates; only an unconformity is sharp, and that one gets a harder, deeper scour).
  * **Per-layer tonal jitter** so no band is one flat colour.

    python3 tools/render_strata_organic.py --width 3000 --height 440 --out working/strata.png
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
LP = ROOT / "living_past"
PLATES = LP / "plates"
SPEC = json.loads((LP / "geology_hellcreek.json").read_text())

TEX = {
    "L01": "tex_topsoil", "L02": "tex_mudstone", "L03": "tex_lignite", "L04": "tex_sandstone",
    "L05": "tex_paleosol", "L06": "tex_bentonite", "L07": "tex_mudstone", "L08": "tex_sandstone",
    "U01": None, "L09": "tex_foxhills", "L10": "tex_pierre",
}
# how much each contact undulates, as a fraction of ribbon height
WAVE = 0.030
UNCONFORMITY_WAVE = 0.055     # a scour surface has real relief (up to ~3 m in the spec)


def smooth_noise(shape, octaves=(4, 9, 20), seed=0) -> np.ndarray:
    """Low-frequency noise in 0..1, built by upsampling small random grids."""
    rng = np.random.default_rng(seed)
    h, w = shape
    acc = np.zeros((h, w), np.float32)
    amp = 1.0
    tot = 0.0
    for o in octaves:
        small = rng.random((max(2, o), max(2, o))).astype(np.float32)
        up = np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC),
                        np.float32) / 255.0
        acc += up * amp
        tot += amp
        amp *= 0.55
    return acc / tot


def variant(tile: Image.Image, size, seed: int) -> np.ndarray:
    """One look at a tile: random sub-crop, optional flip/rotate, cover-fit to size."""
    rng = np.random.default_rng(seed)
    w, h = tile.size
    cw = int(w * rng.uniform(0.55, 0.95))
    ch = int(h * rng.uniform(0.55, 0.95))
    x0 = int(rng.integers(0, max(1, w - cw)))
    y0 = int(rng.integers(0, max(1, h - ch)))
    im = tile.crop((x0, y0, x0 + cw, y0 + ch))
    if rng.random() < 0.5:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if rng.random() < 0.25:
        im = im.transpose(Image.FLIP_TOP_BOTTOM)
    tw, th = size
    s = max(tw / im.width, th / im.height)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    im = im.crop(((im.width - tw) // 2, (im.height - th) // 2,
                  (im.width - tw) // 2 + tw, (im.height - th) // 2 + th))
    return np.asarray(im.convert("RGB"), np.float32)


def hexrgb(h: str):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Render a non-uniform strata ribbon")
    ap.add_argument("--width", type=int, default=3000)
    ap.add_argument("--height", type=int, default=440)
    ap.add_argument("--out", type=pathlib.Path, default=ROOT / "working/strata_ribbon.png")
    args = ap.parse_args(argv)
    W, H = args.width, args.height

    layers = SPEC["layers"]
    tot = sum(l["relThickness"] for l in layers)
    canvas = np.zeros((H, W, 3), np.float32)

    # boundary y for each contact, undulating
    xs = np.arange(W)
    edges, acc = [0.0], 0.0
    for l in layers:
        acc += l["relThickness"] / tot
        edges.append(acc)

    ymaps = []
    for i, e in enumerate(edges):
        base = e * H
        if i == 0 or i == len(edges) - 1:
            ymaps.append(np.full(W, base, np.float32))
            continue
        amp = (UNCONFORMITY_WAVE if layers[min(i, len(layers) - 1)]["id"] == "U01" else WAVE) * H
        n = smooth_noise((1, W), octaves=(3, 7, 15), seed=100 + i)[0]
        ymaps.append(base + (n - 0.5) * 2 * amp)

    yy = np.arange(H)[:, None]
    for i, l in enumerate(layers):
        name = TEX.get(l["id"])
        size = (W, H)
        if name and (PLATES / f"{name}.png").exists():
            tile = Image.open(PLATES / f"{name}.png").convert("RGB")
            # two or three different looks at the tile, cross-faded through noise
            seed_base = hash(l["id"]) % 9973
            v1 = variant(tile, size, seed_base)
            v2 = variant(tile, size, seed_base + 401)
            m = smooth_noise((H, W), octaves=(3, 8), seed=seed_base + 7)[..., None]
            band = v1 * m + v2 * (1 - m)
            if l["relThickness"] > 0.10:            # thick beds get a third look
                v3 = variant(tile, size, seed_base + 913)
                m2 = smooth_noise((H, W), octaves=(2, 5), seed=seed_base + 19)[..., None]
                band = band * m2 + v3 * (1 - m2)
            src = "tex"
        else:
            band = np.ones((H, W, 3), np.float32) * hexrgb(l.get("color", "#4a3d28"))
            src = "color"

        # tonal jitter so the band is never one flat value
        j = smooth_noise((H, W), octaves=(2, 6, 14), seed=(hash(l["id"]) % 811) + 3)[..., None]
        band = np.clip(band * (0.86 + 0.28 * j), 0, 255)

        top = ymaps[i][None, :]
        bot = ymaps[i + 1][None, :]
        mask = ((yy >= top) & (yy < bot)).astype(np.float32)
        # soften the contact a touch (a hard line only for the unconformity)
        soft = 1.0 if l["id"] == "U01" else 2.5
        if soft > 1:
            mask = np.asarray(Image.fromarray((mask * 255).astype(np.uint8))
                              .filter(__import__("PIL.ImageFilter", fromlist=["x"]).GaussianBlur(soft)),
                              np.float32) / 255.0
        canvas = canvas * (1 - mask[..., None]) + band * mask[..., None]
        print(f"  {l['id']} {l['name'][:26]:<26} {src:<6} rel={l['relThickness']:.3f}")

    Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8)).save(args.out)
    print(f"\nwrote {args.out}  ({W}x{H})  — {len(layers)} layers, wavy contacts, 2-3 variants each")
    return 0


if __name__ == "__main__":
    sys.exit(main())
