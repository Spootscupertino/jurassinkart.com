#!/usr/bin/env python3
"""The Living Past — assemble the back plate from harvested components (#23).

Per PLATE_ASSEMBLY.md: no single MJ render lands the whole world, so the backdrop is composited
slot by slot from the best region of several renders.

**The seams are the whole job.** A straight-line alpha ramp still reads as a pasted rectangle no
matter how wide you feather it, because nothing in nature has a ruled edge. Every mask here is
therefore *noise-warped*: the transition line itself wanders, so the eye can't find where one
plate stops and the next starts.

Vertical order, and why:
  sky + angled plain + river   the world, from `land_oblique_river` (oblique sweep = more usable
                               ground for the depth planes; the braided river is the habitat five
                               shoreline organisms need)
  macro forest floor           pulled right to the front so cm-scale organisms can be drawn huge.
                               Blended from SEVERAL litter plates with irregular overlaps — one
                               repeated texture reads as wallpaper.
  strata ribbon                thin, and non-uniform (render_strata_organic.py).
  ocean                        right wedge: sunlit shelf breaking over a drop-off into an abyssal
                               void at full depth. The void is the scale weapon; it never shrinks.

    python3 tools/build_backdrop.py --out working/backdrop.png
"""
from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLATES = ROOT / "living_past/plates"
CAND = PLATES / "candidates"

W, H = 3000, 2000     # overridable: the poster's scene slot is 3000x1298, NOT 3:2, and
                      # cover-fitting a 3:2 plate into it crops away the forest floor and
                      # strata entirely. Build at the destination ratio instead.

FLOOR_TOP = 0.50      # macro litter starts (deep overlap with the land, blended away)
FLOOR_BOT = 0.875     # litter ends, strata begin. Pushed down twice: the micro habitats
                      # are the strongest part of the plate and the soil was the weakest,
                      # so the band trade goes to the litter. Strata now ~12% (was 50%).
COAST_X   = 0.55      # ocean wedge nominal edge
SEA_TOP   = 0.20      # waterline on the ocean side


def noise(shape, octaves=(3, 7, 16), seed=0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    h, w = shape
    acc = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in octaves:
        small = rng.random((max(2, o), max(2, o))).astype(np.float32)
        up = np.asarray(Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC),
                        np.float32) / 255.0
        acc += up * amp
        tot += amp
        amp *= 0.55
    return acc / tot


def organic_mask(size, axis: str, edge: float, width: float, seed: int, warp: float = 0.10) -> Image.Image:
    """Alpha ramp across `axis` centred on `edge`, but with the transition line displaced by
    low-frequency noise so the seam wanders instead of ruling straight across the plate."""
    w, h = size
    if axis == "y":
        base = np.tile(np.linspace(0, 1, h)[:, None], (1, w))
    else:
        base = np.tile(np.linspace(0, 1, w)[None, :], (h, 1))
    n = noise((h, w), octaves=(2, 5, 11), seed=seed)
    line = edge + (n - 0.5) * 2 * warp
    a = np.clip((base - line) / max(1e-4, width) + 0.5, 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(6))


def cover(im: Image.Image, size) -> Image.Image:
    tw, th = size
    s = max(tw / im.width, th / im.height)
    r = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    return r.crop(((r.width - tw) // 2, (r.height - th) // 2,
                   (r.width - tw) // 2 + tw, (r.height - th) // 2 + th))


def load(name: str) -> Image.Image:
    p = CAND / name
    if not p.exists():
        p = PLATES / name
    if not p.exists():
        print(f"  missing component: {name}", file=sys.stderr)
        return Image.new("RGB", (1344, 896), (40, 40, 44))
    return Image.open(p).convert("RGB")


def paste(scene: Image.Image, im: Image.Image, xy, mask: Image.Image) -> None:
    layer = im.convert("RGBA")
    layer.putalpha(mask)
    scene.alpha_composite(layer, xy)


def blob_mask(size, seed: int, softness: float = 0.55) -> Image.Image:
    """An irregular blob that falls off on EVERY side.

    A one-axis ramp is fine for a horizon or a coastline, which really do run edge to edge. It is
    wrong for an inserted patch — a burrow field or a sheltered hollow has no straight sides, and
    a rectangle of detail dropped into the plate announces itself instantly. Radial falloff times
    low-frequency noise gives a patch with no findable border."""
    w, h = size
    gx = np.linspace(-1, 1, w, dtype=np.float32)[None, :]
    gy = np.linspace(-1, 1, h, dtype=np.float32)[:, None]
    r = np.sqrt(gx * gx + gy * gy) / 1.414
    n = noise((h, w), octaves=(2, 5, 11), seed=seed)
    a = np.clip((1.0 - r / max(1e-3, softness)) * (0.55 + 0.9 * n), 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(14))


def blend_into(scene: Image.Image, im: Image.Image, box, mask: Image.Image, mode: str) -> None:
    """Composite `im` into `box` using lighten/darken rather than straight alpha.

    Detail plates (roots, burrows) are drawn on their own dirt background, and knocking that out
    cleanly is hopeless — the background *is* the same material as the target. But the features
    themselves are pure tonal extremes: pale roots are lighter than any soil, burrow mouths are
    darker than any soil. So take the max (roots) or the min (burrows) per pixel and the feature
    transfers while its backing dirt disappears into the strata it lands on."""
    x0, y0, x1, y1 = box
    dst = np.asarray(scene.convert("RGB").crop(box), np.float32)
    src = np.asarray(cover(im, (x1 - x0, y1 - y0)), np.float32)
    out = np.maximum(dst, src) if mode == "lighten" else np.minimum(dst, src)
    a = (np.asarray(mask.resize((x1 - x0, y1 - y0)), np.float32) / 255.0)[..., None]
    merged = Image.fromarray(np.clip(dst * (1 - a) + out * a, 0, 255).astype(np.uint8))
    scene.paste(merged, (x0, y0))


LAYERS: list[tuple[str, Image.Image]] = []


def record(name: str, im: Image.Image, xy=(0, 0), mask=None, size=None) -> None:
    """Stash a component as a full-canvas RGBA layer.

    This is the whole answer to "is this hard to move into Photoshop?" — it is not, provided we
    never hand over a flat raster. Each component is written at full canvas size with its own
    alpha already baked in, so File > Scripts > Load Files into Stack rebuilds the exact
    composite as an editable stack, in the same order, with every mask preserved as transparency.
    """
    w, h = size or (W, H)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    src = im.convert("RGBA").copy()
    if mask is not None:
        src.putalpha(mask)
    layer.alpha_composite(src, xy)
    LAYERS.append((name, layer))


def main(argv=None) -> int:
    global W, H
    ap = argparse.ArgumentParser(description="Assemble the Living Past back plate")
    ap.add_argument("--out", type=pathlib.Path, default=ROOT / "working/backdrop.png")
    ap.add_argument("--no-grade", action="store_true", help="skip the unifying grade pass")
    ap.add_argument("--layers", type=pathlib.Path, default=None,
                    help="also export each component as its own full-canvas RGBA PNG for Photoshop")
    ap.add_argument("--width", type=int, default=W)
    ap.add_argument("--height", type=int, default=H)
    args = ap.parse_args(argv)
    W, H = args.width, args.height

    scene = Image.new("RGBA", (W, H), (12, 14, 18, 255))

    # ---- 1 · the world ------------------------------------------------------------------
    land = cover(load("land_oblique_river.png"), (W, H))
    scene.alpha_composite(land.convert("RGBA"), (0, 0))
    record("10_land", land)
    print("  land        full frame      angled plain + braided river + volcano")

    # ---- 1b · a better sky --------------------------------------------------------------
    # The land plate's own sky is flat and pale. A dedicated sky plate is blended in above the
    # horizon only, then the volcano is put back on top of it — otherwise the new sky buries the
    # monument that the whole right-hand composition hangs on.
    if (CAND / "sky_sunset.png").exists():
        skyh = round(H * 0.34)
        sky = cover(load("sky_sunset.png"), (W, skyh))
        m = np.asarray(organic_mask((W, skyh), "y", 0.74, 0.44, seed=11, warp=0.10)
                       .point(lambda v: 255 - v), np.float32)
        # Hold the new sky OUT of the volcano's airspace rather than pasting the volcano back on
        # top of it. Re-pasting left a visible bright rectangle, because the land plate's local
        # sky is hazier than the new one and the patch carried that difference with it. Masking
        # the sky instead means the volcano and the air around it are never touched at all.
        # softness must be < 1 so the blob reaches zero INSIDE its box; at 1.15 it was still
        # ~13% opaque at the corners, which showed as vertical steps in the sky.
        keep = np.asarray(blob_mask((round(W * 0.46), skyh), seed=13, softness=0.72), np.float32)
        vx = round(W * 0.49)
        m[:, vx:vx + keep.shape[1]] *= 1.0 - keep / 255.0
        _skym = Image.fromarray(m.astype(np.uint8), "L")
        paste(scene, sky, (0, 0), _skym)
        record("20_sky", sky, (0, 0), _skym)
        print("  sky         y 0.00-0.34     sunset plate, held clear of the volcano's airspace")

    # ---- 2 · ocean wedge, blended in on an irregular coastline --------------------------
    # Built as its own region (lower-right), then blended into the scene with the PRODUCT of two
    # noise-warped ramps — one for the coastline, one for the waterline — so neither edge rules
    # straight across. Building it region-local avoids the cover-fit letterboxing that put a
    # black slab in the sky on the first pass.
    ox, oy = round(W * COAST_X), round(H * SEA_TOP)
    ow, oh = W - ox, H - oy
    # The deep column fills the ENTIRE ocean region first. Pasting it as a partial-height block
    # (the first attempt) left a ruled horizontal edge where it began — there is no mask width
    # that hides a straight line, so the fix is to not have one: the water is continuous, and the
    # shelf is laid over its top and dissolved away downward.
    ocean = cover(load("ocean_column.png"), (ow, oh)).convert("RGBA")
    shelf = cover(load("ocean_shelf_dropoff.png"), (ow, round(oh * 0.66))).convert("RGB")
    paste(ocean, shelf, (0, 0),
          organic_mask((ow, round(oh * 0.66)), "y", 0.58, 0.40, seed=31, warp=0.12)
          .point(lambda v: 255 - v))
    mx = np.asarray(organic_mask((ow, oh), "x", 0.16, 0.20, seed=17, warp=0.09), np.float32)
    my = np.asarray(organic_mask((ow, oh), "y", 0.16, 0.24, seed=23, warp=0.07), np.float32)
    m = Image.fromarray((mx * my / 255.0).astype(np.uint8), "L")
    paste(scene, ocean.convert("RGB"), (ox, oy), m)
    record("30_ocean", ocean.convert("RGB"), (ox, oy), m)
    print(f"  ocean       x~{COAST_X:.2f}          shelf -> drop-off -> abyss (wandering coastline)")

    # ---- 3 · macro forest floor, several plates, irregular overlaps ---------------------
    ft, fb = round(H * FLOOR_TOP), round(H * FLOOR_BOT)
    fh = fb - ft
    litters = [n for n in ("floor_swamp_wet.png", "floor_sandy_bank.png", "floor_litter_dry.png")
               if (CAND / n).exists()] or ["floor_swamp_wet.png"]
    floor = Image.new("RGBA", (W, fh), (0, 0, 0, 0))
    n = len(litters)
    for i, name in enumerate(litters):
        tile = cover(load(name), (W, fh)).convert("RGBA")
        if i == 0:
            floor.alpha_composite(tile)
            continue
        # each subsequent plate claims a wandering territory rather than a hard column
        edge = i / n
        paste(floor, tile.convert("RGB"), (0, 0),
              organic_mask((W, fh), "x", edge, 0.30, seed=200 + i * 13, warp=0.16))
    # The litter is land, and it has to end on all three of its open sides or it reads as a
    # pasted band: dissolve upward into the middle distance, downward into the soil, and
    # sideways at the same wandering coastline the ocean and strata use.
    ftop = np.asarray(organic_mask((W, fh), "y", 0.28, 0.40, seed=57, warp=0.13), np.float32)
    fbot = np.asarray(organic_mask((W, fh), "y", 0.86, 0.22, seed=63, warp=0.09)
                      .point(lambda v: 255 - v), np.float32)
    fside = np.asarray(organic_mask((W, fh), "x", COAST_X + 0.08, 0.12, seed=17, warp=0.06)
                       .point(lambda v: 255 - v), np.float32)
    fm = Image.fromarray((ftop * fbot * fside / (255.0 * 255.0)).astype(np.uint8), "L")
    paste(scene, floor.convert("RGB"), (0, ft), fm)
    record("40_forest_floor", floor.convert("RGB"), (0, ft), fm)
    print(f"  floor       y {FLOOR_TOP:.2f}-{FLOOR_BOT:.2f}   macro litter, {n} plates on wandering territories")

    # ---- 4 · thin strata ribbon, non-uniform --------------------------------------------
    rw, rh = W, H - fb + 260
    ribbon_png = ROOT / "working/_strata_ribbon_auto.png"
    subprocess.run([sys.executable, str(ROOT / "tools/render_strata_organic.py"),
                    "--width", str(rw), "--height", str(rh), "--out", str(ribbon_png)],
                   check=True, capture_output=True)
    ribbon = Image.open(ribbon_png).convert("RGB")
    # Grade the soil the way the ocean is graded: depth darkens it. A flat evenly-lit band read
    # pale and papery against the litter above; falling off into the dark makes the ground feel
    # like it continues below the frame instead of stopping at a printed edge, and it rhymes with
    # the abyss on the other side of the plate.
    ra = np.asarray(ribbon, np.float32)
    depth = np.linspace(0, 1, ra.shape[0], dtype=np.float32)[:, None, None]
    ra *= (1.0 - 0.62 * depth ** 1.35)
    ra = ra * (1 - 0.22 * depth) + np.array([26, 22, 18], np.float32) * (0.22 * depth)
    ribbon = Image.fromarray(np.clip(ra, 0, 255).astype(np.uint8))
    # soil belongs to the land side only — fade it out under the sea, on the same wandering
    # coastline the ocean uses, so the two edges agree instead of crossing each other
    sy = np.asarray(organic_mask((rw, rh), "y", 0.34, 0.26, seed=71, warp=0.10), np.float32)
    sx = np.asarray(organic_mask((rw, rh), "x", COAST_X + 0.06, 0.10, seed=17, warp=0.06)
                    .point(lambda v: 255 - v), np.float32)
    _sm = Image.fromarray((sy * sx / 255.0).astype(np.uint8), "L")
    paste(scene, ribbon, (0, fb - 260), _sm)
    record("50_strata", ribbon, (0, fb - 260), _sm)
    print(f"  strata      y {FLOOR_BOT:.2f}-1.00   11 Hell Creek layers, {(1-FLOOR_BOT)*100:.0f}% of height (was 50%)")

    # ---- 4b · detail passes -------------------------------------------------------------
    # Roots and burrows go INTO the soil ribbon, not on top of it, via tonal blending (see
    # blend_into). Both are masked to the soil band so they can't stray into the litter or sea.
    soil_top = fb - 200
    if (CAND / "detail_roots.png").exists():
        box = (0, soil_top, round(W * 0.50), soil_top + 620)
        blend_into(scene, load("detail_roots.png"), box,
                   blob_mask((box[2] - box[0], box[3] - box[1]), seed=91, softness=0.85), "lighten")
        print("  roots       upper soil      pale root traces + mycorrhizal filaments (lighten)")
    if (CAND / "detail_burrows.png").exists():
        box = (round(W * 0.12), soil_top + 80, round(W * 0.44), soil_top + 420)
        blend_into(scene, load("detail_burrows.png"), box,
                   blob_mask((box[2] - box[0], box[3] - box[1]), seed=97, softness=0.78), "darken")
        print("  burrows     upper soil      tunnel mouths + nest chamber (darken)")

    # ---- 4c · the micro-fauna habitat ---------------------------------------------------
    # A sheltered hollow under a log, front-left in the litter — the landing spot where the
    # cm-scale organisms get drawn huge. Without it the ant and the beetle larva have nowhere
    # legible to be at all (3px and 8px at true scale).
    if (CAND / "micro_hollow.png").exists():
        # Two habitats, both large. These are the best-reading part of the plate and the place
        # the cm-scale organisms actually become legible, so they get real estate rather than a
        # polite corner. Different seeds + a mirrored second copy so they don't read as one image
        # used twice.
        for i, (fx, fy, mw, mh, flip) in enumerate([
                (0.015, 250, 1180, 720, False),
                (0.335, 505, 940, 580, True)]):   # keep both on the land side
            src = load("micro_hollow.png")
            if flip:
                src = src.transpose(Image.FLIP_LEFT_RIGHT)
            hollow = cover(src, (mw, mh))
            _hm = blob_mask((mw, mh), seed=133 + i * 29, softness=0.80)
            paste(scene, hollow, (round(W * fx), ft + fy), _hm)
            record(f"60_micro_habitat_{i+1}", hollow, (round(W * fx), ft + fy), _hm)
        print("  micro       front x2        sheltered hollows = micro-fauna habitat")

    # ---- 4d · the asteroid whisper (SCOPE §217) -----------------------------------------
    # A single faint cold point with a short streak, high in the empty top-left indigo. Subtle
    # enough to miss until you know — not a competing monument.
    ax, ay = round(W * 0.135), round(H * 0.085)
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    gd.line((ax - 58, ay + 21, ax + 8, ay - 3), fill=120, width=3)
    gd.ellipse((ax - 6, ay - 6, ax + 6, ay + 6), fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(2.2))
    tint = Image.new("RGB", (W, H), (214, 230, 255))
    _ast = Image.merge("RGBA", (*tint.split(), glow))
    scene.alpha_composite(_ast)
    LAYERS.append(("70_asteroid_whisper", _ast))
    print("  asteroid    top-left        faint cold point + streak (the whisper)")

    # ---- 5 · one world, one light -------------------------------------------------------
    # Harvested components were each lit by their own MJ render, so without this they read as
    # separate photographs no matter how well the seams are hidden. One warm sunset grade plus
    # depth haze ties them together — the same job `70_WORLD_GRADE` does in the PS build.
    if not args.no_grade:
        arr = np.asarray(scene.convert("RGB"), np.float32)
        yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        # warm key from the upper right, cooling with depth
        warm = np.array([1.045, 1.005, 0.945], np.float32)
        cool = np.array([0.945, 0.985, 1.070], np.float32)
        arr *= warm * (1 - yy) + cool * yy
        # aerial haze toward the horizon so the far plain sits back
        haze = np.clip(1.0 - np.abs(yy - 0.22) / 0.34, 0, 1) ** 2 * 0.16
        arr = arr * (1 - haze) + np.array([232, 206, 178], np.float32) * haze
        # gentle vignette to hold the eye in the frame
        gx = np.linspace(-1, 1, W, dtype=np.float32)[None, :, None]
        gy = np.linspace(-1, 1, H, dtype=np.float32)[:, None, None]
        arr *= 1.0 - 0.14 * np.clip(gx * gx + gy * gy - 0.55, 0, None)
        scene = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).convert("RGBA")
        print("  grade       whole frame     warm sunset key + depth haze + vignette")

    if args.layers:
        args.layers.mkdir(parents=True, exist_ok=True)
        for name, layer in LAYERS:
            layer.save(args.layers / f"{name}.png")
        print(f"  layers      {len(LAYERS)} full-canvas RGBA PNGs -> {args.layers}")
        print("              Photoshop: File > Scripts > Load Files into Stack (alphabetical = correct order)")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    scene.convert("RGB").save(args.out)
    print(f"\nwrote {args.out}  ({W}x{H})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
