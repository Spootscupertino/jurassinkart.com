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

# ---- composition balance ---------------------------------------------------------------------
# The plate went bottom-heavy once the litter and soil grew. The tempting fix is to shrink the
# litter back, but the litter is the best thing on the plate and the micro habitats live in it.
# So rebalance from the OTHER end instead: raise the sea and drop the horizon. Both put mass and
# interest into the top half without giving up a single pixel of front detail.
SEA_TOP   = 0.145     # waterline on the ocean side (was 0.20 — the sea comes up)
LAND_BIAS = 0.34      # vertical crop bias on the land plate; < 0.5 keeps more of the source's
                      # sky, which drops the horizon line down the frame and opens the top.

# ---- the volcano, at the wide ratio ------------------------------------------------------------
# At 2.3:1 the monument wants to sit lower and further right than it did on a 3:2 plate, and to
# OVERLAP the treeline rather than float above it. Fractions of the canvas, top-left of the patch.
VOLCANO_X = 0.545
VOLCANO_Y = 0.055
VOLCANO_W = 0.34

# ---- the macro window --------------------------------------------------------------------------
# Bottom-left box (x0, y0, x1, y1 as canvas fractions) that one micro habitat runs out of.
MACRO_WIN = (0.018, 0.505, 0.245, 0.945)


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


def cover(im: Image.Image, size, bias: float = 0.5) -> Image.Image:
    """Scale to cover `size` and crop. `bias` picks WHERE the vertical crop is taken from:
    0.5 centres it (the default everywhere), lower keeps more of the source's top. That knob is
    how the horizon gets moved without re-rolling the plate — see LAND_BIAS."""
    tw, th = size
    s = max(tw / im.width, th / im.height)
    r = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    x = (r.width - tw) // 2
    y = round((r.height - th) * min(max(bias, 0.0), 1.0))
    return r.crop((x, y, x + tw, y + th))


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
    land = cover(load("land_oblique_river.png"), (W, H), bias=LAND_BIAS)
    scene.alpha_composite(land.convert("RGBA"), (0, 0))
    record("10_land", land)
    print(f"  land        full frame      angled plain + braided river (bias {LAND_BIAS} drops the horizon)")

    # ---- 1b · a better sky --------------------------------------------------------------
    # The land plate's own sky is flat and pale. A dedicated sky plate is blended in above the
    # horizon only, then the volcano is put back on top of it — otherwise the new sky buries the
    # monument that the whole right-hand composition hangs on.
    # Three plates stacked by altitude beat one sky that tries to do everything — the same
    # harvesting thesis as the rest of the plate, applied upward. Each is masked to its own band
    # with a noise-warped edge so the bands don't rule straight lines across the air:
    #   high cirrus  the top, where the asteroid whisper lands
    #   mid cumulus  the sculpted volume that gives the sky depth
    #   horizon glow the warm gradient the land dissolves up into
    # Falls back to the single sky_sunset plate whenever the triptych hasn't been shot yet.
    TRIPTYCH = [("sky_high_cirrus.png", 0.00, 0.16, 0.55, 41),
                ("sky_mid_cumulus.png", 0.10, 0.26, 0.62, 43),
                ("sky_horizon_glow.png", 0.20, 0.36, 0.70, 47)]
    for name, y0, y1, edge, seed in [t for t in TRIPTYCH if (CAND / t[0]).exists()]:
        top, bot = round(H * y0), round(H * y1)
        band = cover(load(name), (W, bot - top))
        bm = np.asarray(organic_mask((W, bot - top), "y", edge, 0.52, seed=seed, warp=0.11)
                        .point(lambda v: 255 - v), np.float32)
        # fade the top edge too for every band below the first, so they layer instead of stack
        if y0 > 0:
            bm *= np.asarray(organic_mask((W, bot - top), "y", 0.18, 0.34, seed=seed + 1,
                                          warp=0.09), np.float32) / 255.0
        _bm = Image.fromarray(bm.astype(np.uint8), "L")
        paste(scene, band, (0, top), _bm)
        record(f"2{TRIPTYCH.index((name, y0, y1, edge, seed))}_sky_{name[4:-4]}", band, (0, top), _bm)
        print(f"  sky         y {y0:.2f}-{y1:.2f}     {name[4:-4].replace('_', ' ')}")

    if not any((CAND / t[0]).exists() for t in TRIPTYCH) and (CAND / "sky_sunset.png").exists():
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

    # ---- 1c · the volcano, harvested and placed ------------------------------------------
    # The volcano used to be whatever the land plate happened to contain, which is why it crops
    # high and floats: the land plate is 3:2 and the scene slot is 2.3:1, so its horizon furniture
    # lands too near the top edge. v5_volcano_terraces is the render that actually nailed the cone
    # and the ash plume, so the monument becomes its own harvested component with its own
    # coordinates — lower and further right, deliberately overlapping the treeline rather than
    # hovering above it, which is what makes it read as sitting IN the world at this ratio.
    if (CAND / "volcano_monument.png").exists() or (CAND / "v5_volcano_terraces.png").exists():
        src = load("volcano_monument.png" if (CAND / "volcano_monument.png").exists()
                   else "v5_volcano_terraces.png")
        # cone + plume region of the v5 plate, generous enough to carry its own local sky
        cx0, cy0, cx1, cy1 = (round(src.width * 0.26), 0,
                              round(src.width * 0.70), round(src.height * 0.50))
        vw = round(W * VOLCANO_W)
        crop = src.crop((cx0, cy0, cx1, cy1))
        vh = round(crop.height * vw / crop.width)
        volc = crop.resize((vw, vh), Image.LANCZOS)
        vx, vy = round(W * VOLCANO_X), round(H * VOLCANO_Y)
        # Blob mask, not a ramp: the monument is an inserted patch with no straight sides, and its
        # own local sky has to dissolve into ours on every edge. The bottom is additionally cut
        # back so the cone's base disappears INTO the treeline instead of ending on a visible line.
        vm = np.asarray(blob_mask((vw, vh), seed=19, softness=0.86), np.float32)
        vm *= np.asarray(organic_mask((vw, vh), "y", 0.86, 0.30, seed=29, warp=0.12)
                         .point(lambda v: 255 - v), np.float32) / 255.0
        _vm = Image.fromarray(vm.astype(np.uint8), "L")
        paste(scene, volc, (vx, vy), _vm)
        record("25_volcano", volc, (vx, vy), _vm)
        print(f"  volcano     x {VOLCANO_X:.2f} y {VOLCANO_Y:.2f}   monument dropped onto the treeline")

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
    # Underwater detail passes, blended into the ocean region BEFORE it goes down on the scene so
    # they inherit the same coastline mask and can't spill onto the land. The ocean is the emptiest
    # quarter of the plate; each pass belongs to one depth band, shallow to deep, because a single
    # "underwater scene" laid over the whole wedge would flatten the drop-off that the abyss —
    # and therefore the Mosasaurus's scale — depends on.
    for name, y0, y1, edge, seed in [("ocean_algae_fringe.png", 0.00, 0.34, 0.62, 51),
                                     ("ocean_shell_beds.png",   0.26, 0.62, 0.58, 53),
                                     ("ocean_marine_snow.png",  0.52, 1.00, 0.40, 59)]:
        if not (CAND / name).exists():
            continue
        t, b = round(oh * y0), round(oh * y1)
        det = cover(load(name), (ow, b - t))
        dm = np.asarray(blob_mask((ow, b - t), seed=seed, softness=0.92), np.float32)
        dm *= np.asarray(organic_mask((ow, b - t), "y", edge, 0.55, seed=seed + 1, warp=0.13),
                         np.float32) / 255.0
        paste(ocean, det, (0, t), Image.fromarray(dm.astype(np.uint8), "L"))
        print(f"  ocean det   y {y0:.2f}-{y1:.2f}     {name[6:-4].replace('_', ' ')}")

    paste(scene, ocean.convert("RGB"), (ox, oy), m)
    record("30_ocean", ocean.convert("RGB"), (ox, oy), m)
    print(f"  ocean       x~{COAST_X:.2f}          shelf -> drop-off -> abyss (wandering coastline)")

    # ---- 2b · the freshwater river margin -----------------------------------------------
    # habitat_map.py caught this and nothing else would have: five organisms (Borealosuchus,
    # Basilemys, the gar, the guitarfish ray, Champsosaurus) declare a freshwater river margin as
    # their home, and every plate so far had it only as distant braided sand — too far back for any
    # of them to be drawn at a legible size. It sits in the middle distance on the land side,
    # nearer than the braid but behind the macro litter, which then overlaps its lower edge.
    if (CAND / "river_margin_macro.png").exists():
        rw2, rh2 = round(W * 0.40), round(H * 0.26)
        rx, ry = round(W * 0.30), round(H * 0.30)
        riv = cover(load("river_margin_macro.png"), (rw2, rh2))
        _rm = blob_mask((rw2, rh2), seed=77, softness=0.88)
        paste(scene, riv, (rx, ry), _rm)
        record("35_river_margin", riv, (rx, ry), _rm)
        print("  river       x 0.30 y 0.30    close-up freshwater margin (5 organisms live here)")

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

    # The cutaway is the plate that makes the poster ONE world instead of two stacked systems.
    # It has to straddle the litter/soil contact — a tunnel that starts in surface leaf litter and
    # ends in an occupied chamber down in the ribbon — so unlike the burrow-mouth detail pass it is
    # composited straight rather than tonally blended: the point is that you can follow it down,
    # and darken-blending would keep only the tunnel's shadow and throw away the chamber.
    if (CAND / "burrow_cutaway.png").exists():
        bw, bh = round(W * 0.30), round(H * 0.30)
        bx, by = round(W * 0.055), fb - round(bh * 0.62)      # spans the litter/soil contact
        cut = cover(load("burrow_cutaway.png"), (bw, bh))
        _cm = blob_mask((bw, bh), seed=101, softness=0.82)
        paste(scene, cut, (bx, by), _cm)
        record("55_burrow_cutaway", cut, (bx, by), _cm)
        print("  burrow cut  litter->soil    surface litter to occupant chamber, one continuous world")

    # ---- 4c · the micro-habitat set ------------------------------------------------------
    # The front band is where the cm-scale organisms get drawn huge. Without it the ant and the
    # beetle larva have nowhere legible to be at all (3px and 8px at true scale).
    # One plate per idea (tools/lp_plate_prompt.py --group micro). Six different habitats
    # blended along the front beat one hollow used twice for the same reason three litter plates
    # beat one tiled texture: a repeated image reads as wallpaper, and the whole point of the front
    # band is that it should read as a world the cm-scale organisms could actually live in.
    #
    # Each entry is (slot, x-fraction, y-offset from the litter top, width, height, flip). They
    # overlap deliberately — a row of discrete patches is just a different kind of wallpaper — and
    # every one gets its own blob seed so no two edges fall the same way. All stay on the land side.
    MICRO = [("micro_log_interior",     0.010, 235, 1120, 700, False),
             ("micro_moss_cushion",     0.150, 470,  760, 470, False),
             ("micro_fern_crozier",     0.268, 180,  520, 660, False),
             ("micro_mushroom_cluster", 0.335, 505,  880, 545, True),
             ("micro_puddle_edge",      0.415, 300,  900, 560, False),
             ("micro_bark_crevice",     0.050, 120,  470, 620, True)]
    placed = [m for m in MICRO if (CAND / f"{m[0]}.png").exists()]
    if not placed and (CAND / "micro_hollow.png").exists():
        # the pre-set fallback: one hollow, twice, mirrored so it doesn't read as one image reused
        placed = [("micro_hollow", 0.015, 250, 1180, 720, False),
                  ("micro_hollow", 0.335, 505, 940, 580, True)]
    for i, (slot, fx, fy, mw, mh, flip) in enumerate(placed):
        src = load(f"{slot}.png")
        if flip:
            src = src.transpose(Image.FLIP_LEFT_RIGHT)
        hab = cover(src, (mw, mh))
        _hm = blob_mask((mw, mh), seed=133 + i * 29, softness=0.80)
        paste(scene, hab, (round(W * fx), ft + fy), _hm)
        record(f"60_micro_{i+1}_{slot}", hab, (round(W * fx), ft + fy), _hm)
    if placed:
        print(f"  micro       front x{len(placed):<7} {', '.join(m[0].replace('micro_', '') for m in placed)}")

    # ---- 4c2 · the macro window ----------------------------------------------------------
    # One habitat breaks its own frame and runs larger than life in the bottom-left corner. The
    # poster already owes the reader the Law #2 note — that magnification changes here — and a
    # ruled box with something climbing out of it *shows* that in a way a caption only asserts.
    #
    # Breaking the frame is the entire mechanism, so it has to be built as a break: the content
    # mask is the box UNION an overflow lobe, and the brass rule is then drawn with that same lobe
    # subtracted from its alpha. The line is therefore genuinely interrupted where the habitat
    # crosses it, rather than the habitat being drawn over an intact line — which reads as a
    # sticker on top of a frame instead of something coming out of one.
    #
    # The frame is the only ruled line anywhere on this plate, and that is the point: everything
    # else is noise-warped precisely so nothing reads as drawn. The one deliberate straight edge
    # is legible as an instrument of the poster rather than an artefact of the compositing.
    # The Law #2 caption itself belongs to the type layer, not here — the backdrop stays a stage.
    if placed:
        slot = placed[0][0]
        mx0, my0 = round(W * MACRO_WIN[0]), round(H * MACRO_WIN[1])
        mx1, my1 = round(W * MACRO_WIN[2]), round(H * MACRO_WIN[3])
        bw2, bh2 = mx1 - mx0, my1 - my0
        # zoomed FURTHER in than the same plate reads at in the front band — that difference in
        # magnification is the whole message of the window
        over = round(bh2 * 0.30)                 # how far past the rule the habitat escapes
        cw, ch = bw2 + over, bh2 + over
        big = load(f"{slot}.png")
        big = cover(big.crop((round(big.width * 0.22), round(big.height * 0.22),
                              round(big.width * 0.78), round(big.height * 0.78))), (cw, ch))
        # A window in the dark bottom-left corner has to carry its own light or it reads as a hole
        # rather than as an enlargement, so the content gets a small lift before the world grade.
        ba = np.asarray(big, np.float32) * 1.22 + 12
        big = Image.fromarray(np.clip(ba, 0, 255).astype(np.uint8))

        # The mask is the box UNION a lobe that straddles the box's top edge. An explicit gaussian
        # bump is used rather than blob_mask here: the lobe has to sit at a KNOWN place relative to
        # the rule (centred on the top edge, right of middle) so that it reliably covers both sides
        # of the line. A noise blob's centre of mass wanders with the seed, and a spill that lands
        # entirely inside or entirely outside the box teaches the reader nothing.
        gy = np.arange(ch, dtype=np.float32)[:, None]
        gx = np.arange(cw, dtype=np.float32)[None, :]
        # The vertical falloff is deliberately much tighter than the horizontal one. A round lobe
        # wide enough to look like a habitat climbing out is also tall enough to stay ~80% opaque
        # at the top of the canvas, which composites as a pale slab hanging over the corner rather
        # than as a spill. Squashing it keeps the width and kills the slab.
        cx, cy, rad = bw2 * 0.68, float(over), bw2 * 0.30
        lobe = np.exp(-(((gx - cx) ** 2 + ((gy - cy) * 2.2) ** 2) / (2 * rad * rad)))
        lobe *= 0.72 + 0.55 * noise((ch, cw), octaves=(2, 5, 11), seed=181)   # keep its edge organic
        # Force the lobe to zero at the content canvas edges. Same trap as blob_mask's softness:
        # the gaussian is still ~16% opaque at the top-right corner, and 16% opacity that stops
        # dead at a boundary is a ruled line — it composited as a faint rectangle hanging over the
        # corner, which is precisely what the rest of this file's noise-warping exists to avoid.
        # Only the lobe is damped; the framed content keeps its hard edge, because there the
        # straight line is the point.
        # The falloff distance is the overflow depth itself, so the damping runs out exactly at the
        # rule and the lobe is undamped where it crosses. Any wider and it flattens the peak, which
        # removes the break entirely — the rule comes back intact and the window stops teaching.
        fall = max(1, over)
        ex = np.clip(np.minimum(gx, cw - 1 - gx) / fall, 0, 1)
        ey = np.clip(np.minimum(gy, ch - 1 - gy) / fall, 0, 1)
        lobe = np.clip(lobe * ex * ey, 0, 1)

        mask = np.zeros((ch, cw), np.float32)
        mask[over:, :bw2] = 1.0                                       # the framed content
        mask = np.maximum(mask, lobe)                                 # the part that escapes
        _mm = Image.fromarray((np.clip(mask, 0, 1) * 255).astype(np.uint8), "L") \
                   .filter(ImageFilter.GaussianBlur(1.6))
        paste(scene, big, (mx0, my0 - over), _mm)
        record("62_macro_window", big, (mx0, my0 - over), _mm)

        # the brass rule, genuinely interrupted where the habitat crosses it
        rule = Image.new("L", (W, H), 0)
        rd = ImageDraw.Draw(rule)
        rd.rectangle((mx0, my0, mx1, my1), outline=255, width=max(3, round(H * 0.0035)))
        ra = np.asarray(rule, np.float32)
        cut = np.zeros((H, W), np.float32)
        y0c, x0c = my0 - over, mx0
        cut[y0c:y0c + ch, x0c:x0c + cw] = lobe
        ra *= 1.0 - np.clip(cut * 1.9, 0, 1)
        _rule = Image.merge("RGBA", (*Image.new("RGB", (W, H), (185, 143, 78)).split(),
                                     Image.fromarray(ra.astype(np.uint8), "L")))
        scene.alpha_composite(_rule)
        LAYERS.append(("63_macro_window_rule", _rule))
        print(f"  macro win   bottom-left     {slot.replace('micro_', '')} breaks its frame (Law #2)")

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
