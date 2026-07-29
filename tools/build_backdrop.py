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
STRATA_LIFT = 1.20    # Eric: brighten the strata. The section is the accuracy moat and it
                      # was reading too dark to find the contacts in — see the grade below.
COAST_X   = 0.55      # ocean wedge nominal edge
COAST_TILT = 0.115    # criticism #2: the coastline used to run straight down the frame, which is
                      # why the water read as a wall. A shore only recedes if its plan position
                      # moves with distance — this leans the seam so the land reaches further out
                      # near the viewer and pulls back toward the horizon.

# ---- the seafloor: what actually makes the abyss deep ------------------------------------------
# Criticism #2 again, and the real fix. The ground used to stop dead at the coastline, so the ocean
# was a blue rectangle with nothing under it — and a rectangle has no depth however dark you make
# it. The section already knows better: `geology_hellcreek.json` calls L09 Fox Hills "nearshore /
# shoreface" and L10 Pierre "offshore seafloor mud". Those beds do not end at the beach; they carry
# on under the water. So the strata continue offshore as a *surface* — a shelf sloping gently away,
# a break, a steep slope, and an abyssal plain lost in the dark. The void is deep because you can
# watch the floor fall away into it.
# Control points as (x fraction of canvas, y fraction of canvas).
SEAFLOOR = [(0.00, 0.330), (0.04, 0.430), (0.075, 0.570), (0.115, 0.760),
            (0.165, 0.900), (0.28, 0.955), (1.00, 0.980)]   # x is measured FROM the coastline
# How much water is between you and the bottom. Without this the floor composites as dry lit ground
# and the shelf reads as a sand dune standing in the sky — which is what the first attempt did, and
# it was worse than the blue panel it replaced. Everything under the surface is seen *through*
# water, so it loses red first, then contrast, then everything.
WATER_TINT = np.array([26, 74, 84], np.float32)
# SCOPE §4 locks four ocean depth zones (SUNLIT / TWILIGHT / DEEP / OCEAN FLOOR) and specifies that
# the painted poster marks them with brass hairlines fading in from the right edge. The lines are
# furniture and belong to the annotation layer; the *tonal* boundary is art and belongs here. These
# are the boundaries as a fraction of the water column, plus how much extra absorption each one
# steps by — small, because a boundary the eye can find is not the same as a boundary drawn.
ZONE_STEPS = ((0.16, 0.055), (0.40, 0.055), (0.72, 0.040))
WATER_MIN = 0.26      # absorption even in the shallows, at the top of the shelf
WATER_MAX = 0.66      # absorption out over the abyssal plain

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
# Eric, 2026-07-29: "the volcano should be in the left corner". Moved from 0.585.
#
# Two things move with it, and both are consequences rather than choices. The **title** was put
# top-left this morning for criticism #8 and the monument now occupies that corner, so the type
# goes back to the top right — which is defensible again precisely because the ash plume, the thing
# that made that corner busy, has left with the cone. And the **asteroid whisper** was sharing the
# left corner with the title; with the volcano there it has no quiet air left, so it moves to the
# upper centre-left, which is now the emptiest sky on the plate.
# Eric, 2026-07-29 (second pass): *"it should all fit up high in that top left corner to give
# maximum ground space for our land creatures."* This is not a taste note, it is a collision report.
# At X 0.108 / W 0.300 the cone's base landed at y≈0.425 and its mask faded out at 0.452 — and
# `place_on_backdrop.PLANES` puts the `far` ground line at 0.452 and `mid` at 0.505. The monument was
# sitting *on* the two bands the land cast has to stand in, which is why the plate looked like it had
# no room for animals: it didn't. Pushed hard into the corner (X 0) and shrunk so the base now ends
# near y 0.39 and its mask is gone by 0.41, clearing both ground lines and handing that whole
# band back to the cast. Note which knob did the work: raising Y did almost all of it, so the
# cone only gives up 5% of its width (0.300 -> 0.285) rather than the 22% first tried.
#
# Shrinking a hero is the trade, and it is the right one twice over: criticism #7 already wanted the
# cone subordinate to the T. rex, and a monument that touches two edges of the frame reads bigger
# than its pixel width because the eye completes it past the trim.
VOLCANO_X = 0.0
VOLCANO_Y = 0.030
VOLCANO_W = 0.300
# Criticism #7: the volcano and the T. rex compete. Both were large, high-contrast and upper-middle,
# so the eye had two subjects and settled on neither. The monument is supposed to be the far wall of
# the world, and the thing that puts a landmark *behind* a subject is not size, it is air: distance
# eats contrast long before it eats scale. So the cone is composited through the same aerial
# perspective the far plain already gets — flattened toward the haze colour and desaturated — and
# only trimmed slightly. It stays a monument; it stops being a rival.
VOLCANO_HAZE = 0.17         # how far the cone is mixed toward the horizon haze
VOLCANO_FLATTEN = 0.20      # contrast pulled toward its own mean

# ---- the macro windows -------------------------------------------------------------------------
# Criticism #4: one bright ruled rectangle in a corner with nothing else in the composition rhyming
# with it reads as an accident, not an instrument. One of anything is an accident. So there are two,
# deliberately unequal — a large one bottom-left in the litter and a small one on the right out over
# the water — and the plate carries brass registration ticks in the same metal at its corners, so
# the ruled line is established as the poster's own vocabulary before either window uses it.
#
# Both break their frame at the top edge: same grammar, different sentence. Matching the *rule* and
# varying the size is what makes two boxes a system; matching the size would have made them a pair,
# and varying the rule would have made them two accidents.
#   box      (x0, y0, x1, y1) as canvas fractions
#   slots    first existing candidate is the content — the right-hand window prefers a marine
#            detail because it sits over the sea, and falls back to a micro habitat
#   lobe_x   where the escaping content crosses the top rule, as a fraction of the box width
#   lift     exposure lift; a window in a dark corner has to carry its own light or it is a hole
MACRO_WINS = [
    # The big window prefers its OWN plate over whatever leads the front band. Same shoot, second
    # keeper: the band wants edge-to-edge texture and the window wants an enlargeable interior, and
    # those are different pictures. Pointing both at one plate is what made the two windows read as
    # a duplication rather than a system. Falls back to the band's lead if it was never shot.
    # `roundness` / `wobble` / `barrel` are the lens parameters (--windows lens). They are per-window
    # on purpose: Eric, 2026-07-29 — "each window will be its own unique shape to fit whatever it
    # is". A shared shape is the thing that made four windows read as four crops of one instrument.
    # The big litter window stays the squarest (a lozenge, so the wide box still fills) and bulges
    # most, because it is the one the reader is closest to and the Law #2 exemplar.
    dict(box=(0.006, 0.580, 0.196, 0.960), slots=("micro_log_cavity",),
         lobe_x=0.68, lift=1.22, over=0.30, seed=181, warm=0.12, dissolve=0.55,
         roundness=2.8, wobble=0.09, barrel=0.18,
         crop=(0.22, 0.22, 0.78, 0.78), flip=False),
    # `crop` and `flip` differ deliberately. Until the ocean plates are shot this window falls back
    # to the same micro habitat as the first one, and two windows showing the identical image is a
    # worse failure than the single window criticism #4 complains about — it turns a system into a
    # duplication. A different region of the plate, mirrored, reads as a second specimen.
    # `require` means exactly that: this window sits out over open water, so its content has to be
    # marine. Falling back to a micro habitat put a cluster of bone-white forest mushrooms floating
    # in the abyss — a window is a magnification of *what is behind it*, and pointing it at
    # something that cannot be there breaks the instrument rather than extending it. Better to run
    # one window until `ocean_shell_beds` is shot than to ship a legible lie.
    dict(box=(0.560, 0.755, 0.700, 0.985),
         slots=("ocean_shell_beds", "ocean_marine_snow", "ocean_algae_fringe"), require=True,
         lobe_x=0.34, lift=1.12, over=0.34, seed=193,
         roundness=2.2, wobble=0.12, barrel=0.13,
         crop=(0.02, 0.30, 0.40, 0.80), flip=True),
    # Eric's idea, and it completes the system: a window on the volcano, showing geology.
    #
    # The content makes an argument the poster could not otherwise make out loud. The magnified
    # material is bentonite — and bentonite is bed L06 in `geology_hellcreek.json`, the ash bed
    # whose environment field reads "ash fall from the scene's volcano — the datable marker". So
    # the window on the cone shows the stuff that becomes a named layer in the cutaway at the other
    # end of the plate. Three windows, three realms: life, sea, rock. That is a system with a
    # reason, not three boxes.
    # The volcano's pair. Eric, 2026-07-29: "the volcano is one of our 3 hero images, make that shit
    # absolutely rip" — so the monument gets two satellites rather than one, staggered down its
    # flank, and both are CIRCLES.
    #
    # Circles are the better instrument and it took him to see it. A ruled rectangle reads as a
    # crop — a decision made in software. A circle reads as a lens: it is the field of view of an
    # optic, which is exactly what a magnification window is claiming to be. Criticism #4 was that
    # the window read as an accident; a porthole cannot, because nothing accidental is round.
    # Boxes here are kept square in CANVAS pixels (w/W == h/H * H/W), or the circle is an ellipse.
    # Both satellites moved with the cone (2026-07-29). They are no longer *bracketing* it, which was
    # the old arrangement and the reason all three had to move as a unit: Eric — "i thought the magma
    # would be at the base of it". A window is a magnification of what is behind it, so the ash sits
    # on the drifting plume and the magma sits at the cone's foot. That is also a better composition
    # than a bracket: the pair now runs as a diagonal across the monument, upper-right to lower-left,
    # instead of two circles flanking it symmetrically.
    # ASH — on the GROUND, downwind of the cone, beside the lava.
    #
    # It sat in the sky for one render and read as a boulder floating in the clouds. The render was
    # not at fault: `geo_volcanic_ash` is written as "looking into a freshly fallen BED of pale grey
    # volcanic ash", so it is a ground subject, and the plate MJ returned is correct for its slot.
    # This is the trap the file already names — check what consumes a slot before blaming the render.
    # A window magnifies what is behind it, and what is behind the sky is sky.
    #
    # On the ground it also earns its keep: an ash-fall bed at the volcano's foot is bed L06 in
    # `geology_hellcreek.json` ("ash fall from the scene's volcano — the datable marker"), so the
    # cascade now runs along the base of the cone — magma in the vent, the ash it drops beside it,
    # and the same bed named again in the cutaway at the bottom of the plate.
    dict(box=(0.2455, 0.3361, 0.2905, 0.4399), shape="circle",
         slots=("geo_volcanic_ash", "tex_bentonite"),
         lobe_x=0.40, lift=1.06, over=0.26, seed=197, warm=0.15,
         roundness=2.15, wobble=0.10, barrel=0.14,
         crop=(0.30, 0.26, 0.88, 0.86), flip=False),
    # The magma vent is the most irregular of the four, and that is content-led: it is the one
    # window looking at something molten and actively moving, so a rim that wanders furthest from
    # any ideal shape is the honest one.
    # MAGMA — at the base of the cone, directly under the vent. Smaller than the ash window so the
    # whole cluster still ends above the `far` ground line (0.452); this one bottoms out at 0.385,
# which is the cone's own base — the window is sitting on the ground the vent sits on.
    dict(box=(0.1325, 0.3080, 0.1875, 0.4350), shape="circle",
         slots=("geo_magma_vent",), require=True,
         lobe_x=0.55, lift=1.00, over=0.26, seed=199, warm=0.10,
         roundness=2.1, wobble=0.11, barrel=0.16,
         crop=(0.16, 0.16, 0.74, 0.84), flip=False),
]
BRASS = (185, 143, 78)
BRASS_HI = (216, 181, 122)   # SCOPE §4 brass highlight #D8B57A — the lit side of a lens rim
# Eric, 2026-07-29: round the window corners. Applied to every window, not just the one he was
# looking at — the whole point of the second and third boxes is that they read as the same
# instrument, and a rounded box beside two square ones is three boxes again.
WIN_RADIUS = 0.012        # fraction of canvas width


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


def organic_mask(size, axis: str, edge: float, width: float, seed: int, warp: float = 0.10,
                 tilt: float = 0.0) -> Image.Image:
    """Alpha ramp across `axis` centred on `edge`, but with the transition line displaced by
    low-frequency noise so the seam wanders instead of ruling straight across the plate.

    `tilt` leans the whole line across the *other* axis. A coastline that runs straight down the
    frame is the thing criticism #2 is about: a shore only reads as receding if its plan position
    changes with distance, and on a plate this is the one knob that does that.
    """
    w, h = size
    if axis == "y":
        base = np.tile(np.linspace(0, 1, h)[:, None], (1, w))
        other = np.tile(np.linspace(0, 1, w)[None, :], (h, 1))
    else:
        base = np.tile(np.linspace(0, 1, w)[None, :], (h, 1))
        other = np.tile(np.linspace(0, 1, h)[:, None], (1, w))
    n = noise((h, w), octaves=(2, 5, 11), seed=seed)
    line = edge + (n - 0.5) * 2 * warp + (other - 0.5) * tilt
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


def aperture(size, seed: int, roundness: float = 3.2, wobble: float = 0.16) -> np.ndarray:
    """An organic lens aperture in 0..1 — the shape a window is seen through.

    Eric, 2026-07-29: *"each window will be its own unique shape to fit whatever it is… it feels
    like a magnifying glass is popping out of the scene."*

    A circle and a rounded rectangle are both **primitives**, and a primitive announces that
    software drew it. A superellipse whose radius wanders with low-frequency noise is none of the
    standard shapes and never repeats between seeds, so each window is its own aperture without
    anyone choosing one.

    `roundness` is the superellipse exponent: **1 is a diamond, 2 is the circle/ellipse, 4+ is a
    squarish lozenge.** Keep it near 2 for anything meant to read as an optic — 3 is already a
    visible squircle, which is just a different primitive and defeats the purpose. Only the wide
    box goes higher, and only because an ellipse leaves a wide frame's corners unused.
    `wobble` is how far the rim wanders off that ideal; past ~0.15 it stops reading as a lens and
    starts reading as a torn hole.
    """
    w, h = size
    ny = (np.arange(h, dtype=np.float32)[:, None] - h / 2) / (h / 2)
    nx = (np.arange(w, dtype=np.float32)[None, :] - w / 2) / (w / 2)
    ang = (np.arctan2(ny, nx) + np.pi) / (2 * np.pi)
    # one wander per angle, not per pixel, or the rim gets fuzzy instead of irregular
    prof = noise((1, 512), octaves=(2, 4, 7), seed=seed)[0]
    idx = np.clip((ang * 511).astype(np.int32), 0, 511)
    r = (np.abs(nx) ** roundness + np.abs(ny) ** roundness) ** (1.0 / roundness)
    return (r / (1.0 + (prof[idx] - 0.5) * 2 * wobble)).astype(np.float32)


def barrel(im: Image.Image, k: float) -> Image.Image:
    """Bulge the centre of `im` outward, the way a hand lens does.

    This is the cue that actually says "magnifier" once the brass ring is gone. A flat crop pasted
    into a soft-edged hole reads as a patch of another photograph; the same crop with its middle
    swollen and its rim compressed reads as something seen THROUGH a curved piece of glass, which
    is the whole claim the window is making about scale.
    """
    a = np.asarray(im.convert("RGB"), np.float32)
    h, w = a.shape[:2]
    ny = (np.arange(h, dtype=np.float32)[:, None] - h / 2) / (h / 2)
    nx = (np.arange(w, dtype=np.float32)[None, :] - w / 2) / (w / 2)
    r = np.sqrt(nx * nx + ny * ny)
    s = 1.0 - k * np.clip(1.0 - r * r, 0, 1)          # sample tighter near the centre = magnify
    sx = np.clip((nx * s * 0.5 + 0.5) * (w - 1), 0, w - 1.001)
    sy = np.clip((ny * s * 0.5 + 0.5) * (h - 1), 0, h - 1.001)
    x0, y0 = sx.astype(np.int32), sy.astype(np.int32)
    fx, fy = (sx - x0)[..., None], (sy - y0)[..., None]
    out = (a[y0, x0] * (1 - fx) * (1 - fy) + a[y0, x0 + 1] * fx * (1 - fy) +
           a[y0 + 1, x0] * (1 - fx) * fy + a[y0 + 1, x0 + 1] * fx * fy)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def seafloor_profile(W: int, H: int, coast: np.ndarray) -> np.ndarray:
    """Per-column y of the sea bottom, in pixels, measured out from the wandering coastline.

    Taking the profile relative to `coast` rather than to a fixed x is what keeps the shelf the
    same width all the way along the shore. Anchoring it to a constant would have made the shelf
    fan out wherever the coastline wandered inland, which is the same "it doesn't recede" failure
    in a different costume.
    """
    xs = np.arange(W, dtype=np.float32)
    out = np.interp((xs - coast) / W, [p[0] for p in SEAFLOOR], [p[1] for p in SEAFLOOR]) * H
    # a seafloor is not a smooth curve: sediment waves on the shelf, slump scars on the slope
    out = out + (noise((1, W), octaves=(2, 5, 11), seed=311)[0] - 0.5) * 2 * H * 0.075
    out = out + (noise((1, W), octaves=(9, 23, 55), seed=313)[0] - 0.5) * 2 * H * 0.028
    return out.astype(np.float32)


def below(size, line: np.ndarray, feather: float, offset: float = 0.0) -> Image.Image:
    """Mask that is opaque below a per-column `line` (in pixels) and clear above it."""
    w, h = size
    yy = np.arange(h, dtype=np.float32)[:, None]
    a = np.clip((yy - (line[None, :] + offset)) / max(1.0, feather), 0, 1)
    return Image.fromarray((a * 255).astype(np.uint8), "L")


def pterosaur(span: int, seed: int = 0) -> Image.Image:
    """A soaring azhdarchid in silhouette, as an alpha mask `span` px across.

    Criticism #6 — nothing is in the air — is the one that quietly contradicts the whole thesis of
    the poster, so the sky cannot wait on a render that may not come. Drawn rather than harvested:
    at the size these read at (20–90 px) an MJ plate would be spending a thousand pixels of detail
    on something the viewer resolves as a shape, and MJ's pterosaurs are anatomically wrong in
    exactly the ways this project exists to avoid. A silhouette can be *right*: azhdarchid wings
    are long, narrow and cranked forward at the wrist, the neck is as long as the body and held
    out straight in a glide, and the tail is a stub.
    """
    rng = np.random.default_rng(seed)
    im = Image.new("L", (span, max(10, round(span * 0.46))), 0)
    d = ImageDraw.Draw(im)
    cx, cy = span * 0.5, im.height * 0.60
    dihedral = im.height * rng.uniform(0.22, 0.40)      # how far the wings are held above the body
    crank = span * rng.uniform(0.03, 0.07)              # forward sweep at the wrist
    # Chord matters more than any other proportion here. The first attempt made it a fixed few
    # pixels, so every bird came out as a horizontal dash — which is what a wing with no chord IS.
    # Scaling it to the span keeps the shape a wing at 22 px and at 180 px alike.
    root, wrist, tip = span * 0.115, span * 0.075, span * 0.022
    for sgn in (-1, 1):
        d.polygon([(cx + sgn * span * 0.035, cy - root * 0.45),
                   (cx + sgn * span * 0.26, cy - dihedral * 0.62 - crank * 0.4),
                   (cx + sgn * span * 0.50, cy - dihedral - crank),
                   (cx + sgn * span * 0.485, cy - dihedral - crank + tip),
                   (cx + sgn * span * 0.27, cy - dihedral * 0.62 + wrist * 0.7),
                   (cx + sgn * span * 0.045, cy + root * 0.55)], fill=255)
    d.ellipse((cx - span * 0.048, cy - span * 0.034, cx + span * 0.048, cy + span * 0.040), fill=255)
    d.line((cx + span * 0.02, cy - span * 0.006, cx + span * 0.20, cy - im.height * 0.19),
           fill=255, width=max(1, round(span * 0.022)))                    # long neck + head
    d.line((cx - span * 0.02, cy, cx - span * 0.085, cy + im.height * 0.07),
           fill=255, width=max(1, round(span * 0.016)))                    # stub tail
    return im.filter(ImageFilter.GaussianBlur(max(0.4, span * 0.008)))


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
    ap.add_argument("--windows", choices=("glass", "crisp", "hybrid", "soft", "lens"), default="glass",
                    help="how the macro windows meet the plate. glass = custom aperture, no border, dissolving rim (SHIPPED); crisp = ruled instrument; "
                         "hybrid = crisp rule, content softened inside it, three escape points; "
                         "soft = no rule at all, content dissolves into the plate; "
                         "lens = per-window organic aperture + barrel bulge (a hand lens, not a crop)")
    ap.add_argument("--no-weather", action="store_true",
                    help="skip the rain cell (one light, one hour — the state criticism #9 names)")
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
    # (slot, centre altitude, half-width, seed) — all as canvas fractions.
    #
    # The first version cut each plate to its own altitude slot and cover-fit it there, which meant
    # crushing a 16:9 sky into a 3000x208 ribbon: the cumulus came out as a row of specks and the
    # horizon glow composited as a hard red ruled stripe straight across the frame — the strata
    # mistake, in the one part of the plate with nothing to hide it behind.
    #
    # The bands have to be layered by MASK, not by crop. Every plate is now cover-fit into the same
    # generous region (so its aspect and its cloud sizes survive intact) and then masked to a soft,
    # noise-warped altitude band. Overlapping bands are the point — that is what makes them layer
    # rather than stack.
    SKY_REGION = 0.46
    TRIPTYCH = [("sky_high_cirrus.png", 0.030, 0.150, 41),
                ("sky_mid_cumulus.png", 0.132, 0.122, 43),
                ("sky_horizon_glow.png", 0.275, 0.135, 47)]
    have_tri = [t for t in TRIPTYCH if (CAND / t[0]).exists()]
    if have_tri:
        rh_sky = round(H * SKY_REGION)
        yc = (np.arange(rh_sky, dtype=np.float32) / H)[:, None]
        for i, (name, centre, half, seed) in enumerate(have_tri):
            band = cover(load(name), (W, rh_sky))
            n = noise((rh_sky, W), octaves=(2, 5, 11), seed=seed)
            c = centre + (n - 0.5) * 2 * 0.035          # the band's own altitude wanders
            a = np.clip(1.0 - np.abs(yc - c) / half, 0, 1) ** 0.75
            # Hold every band out of the volcano's airspace. This protection previously lived only
            # in the single-plate fallback, so switching to the triptych silently removed it and
            # the monument came back hovering in a sky that had been painted over it.
            keep = np.asarray(blob_mask((round(W * 0.46), rh_sky), seed=13, softness=0.72), np.float32)
            vx = max(0, round(W * (VOLCANO_X - 0.02)))
            a[:, vx:vx + keep.shape[1]] *= 1.0 - keep / 255.0 * 0.85
            _bm = Image.fromarray((np.clip(a, 0, 1) * 255).astype(np.uint8), "L") \
                       .filter(ImageFilter.GaussianBlur(8))
            paste(scene, band, (0, 0), _bm)
            record(f"2{i}_sky_{name[4:-4]}", band, (0, 0), _bm)
            print(f"  sky         alt {centre:.3f}±{half:.2f}  {name[4:-4].replace('_', ' ')}")

    if not have_tri and (CAND / "sky_sunset.png").exists():
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
        vx = max(0, round(W * (VOLCANO_X - 0.02)))
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
        # The crop region only makes sense when the cone is being HARVESTED out of a wider
        # landscape. `volcano_monument` is shot for this slot — the cone already fills its frame
        # against clean sky — so cropping it is cutting a small window out of the middle of the
        # subject, which is exactly what made the monument vanish once the plate landed.
        if (CAND / "volcano_monument.png").exists():
            cx0, cy0, cx1, cy1 = 0, 0, src.width, src.height
        else:
            cx0, cy0, cx1, cy1 = (round(src.width * 0.30), 0,
                                  round(src.width * 0.62), round(src.height * 0.44))
        vw = round(W * VOLCANO_W)
        crop = src.crop((cx0, cy0, cx1, cy1))
        vh = round(crop.height * vw / crop.width)
        volc = crop.resize((vw, vh), Image.LANCZOS)
        # aerial perspective — see VOLCANO_HAZE. Done before the mask so the plume recedes with the
        # cone; the ash column is the loudest thing in the crop and pushing the rock back while
        # leaving the smoke forward just moves the competition rather than ending it.
        va = np.asarray(volc, np.float32)
        # Fire is self-luminous, so distance dims it far less than it dims lit rock — and flattening
        # contrast toward the local mean is exactly wrong for it. `volc_hot` keeps a barely-hazed copy
        # for the lighten pass below; the aerial perspective still applies in full to the cone itself,
        # so the monument recedes while its eruption stays hot. Same plate, two atmospheres, because
        # they are two different kinds of light.
        vhot = va * (1 - VOLCANO_HAZE * 0.25) + np.array([206, 186, 172], np.float32) * (VOLCANO_HAZE * 0.25)
        volc_hot = Image.fromarray(np.clip(vhot, 0, 255).astype(np.uint8))
        va = va.mean(axis=2, keepdims=True) * VOLCANO_FLATTEN + va * (1 - VOLCANO_FLATTEN)
        va = va * (1 - VOLCANO_HAZE) + np.array([206, 186, 172], np.float32) * VOLCANO_HAZE
        volc = Image.fromarray(np.clip(va, 0, 255).astype(np.uint8))
        vx, vy = round(W * VOLCANO_X), round(H * VOLCANO_Y)
        # Blob mask, not a ramp: the monument is an inserted patch with no straight sides, and its
        # own local sky has to dissolve into ours on every edge. The bottom is additionally cut
        # back so the cone's base disappears INTO the treeline instead of ending on a visible line.
        vm = np.asarray(blob_mask((vw, vh), seed=19, softness=0.70), np.float32)
        vm *= np.asarray(organic_mask((vw, vh), "y", 0.86, 0.30, seed=29, warp=0.12)
                         .point(lambda v: 255 - v), np.float32) / 255.0
        _vm = Image.fromarray(vm.astype(np.uint8), "L")
        if (CAND / "volcano_monument.png").exists():
            # The dedicated plate is a dark cone and a dark ash column on clean PALE sky — which is
            # the exact condition `blend_into` documents for tonal blending: the feature is a tonal
            # extreme against its own background, so taking the per-pixel minimum transfers the
            # monument and lets its borrowed sky vanish into ours. Alpha-compositing it instead is
            # what kept drawing a soft rectangle in the air, because the patch's sky is a different
            # sky no matter how wide the mask feathers.
            box = (vx, vy, min(W, vx + vw), min(H, vy + vh))
            bw3, bh3 = box[2] - box[0], box[3] - box[1]
            blend_into(scene, volc, box, _vm.crop((0, 0, bw3, bh3)), "darken")
            record("25_volcano", volc, (vx, vy), _vm)
            # ---- second pass: the fire, which darken CANNOT carry ------------------------------
            # The reshot monster (2026-07-29) broke the single-pass assumption. Darken transfers only
            # what is darker than the destination, and everything that makes this plate a monster —
            # the volcanic lightning inside the column, the incandescent crater, the lava on the
            # flanks — is BRIGHTER than our sky. One darken pass would composite the cone and quietly
            # delete the eruption, which is the whole point of the reshoot.
            #
            # The plate is tonally extreme in BOTH directions against its own mid-pale sky, so it gets
            # one pass each way. Lighten alone is not enough either: the source's pale sky is also
            # brighter than ours in places and would paste itself back in. So the fire is keyed on
            # WARMTH rather than brightness — fire runs R-B ≈ 200+, the peach sky about 70, which
            # separates cleanly at a threshold no amount of exposure tuning could find.
            fa2 = np.asarray(volc_hot, np.float32)
            warm_key = np.clip((fa2[..., 0] - fa2[..., 2] - 90.0) / 60.0, 0, 1)
            warm_key *= np.clip((fa2.max(axis=2) - 120.0) / 70.0, 0, 1)
            fk = (warm_key * (np.asarray(_vm, np.float32) / 255.0) * 255.0)
            _fm = Image.fromarray(np.clip(fk, 0, 255).astype(np.uint8), "L") \
                       .filter(ImageFilter.GaussianBlur(2.0))
            blend_into(scene, volc_hot, box, _fm.crop((0, 0, bw3, bh3)), "lighten")
            record("25b_volcano_fire", volc_hot, (vx, vy), _fm)
            print(f"  volcano     x {VOLCANO_X:.2f} y {VOLCANO_Y:.2f}   monument, darken + a "
                  f"warmth-keyed lighten pass so the lightning and crater survive")
        else:
            paste(scene, volc, (vx, vy), _vm)
            record("25_volcano", volc, (vx, vy), _vm)
            print(f"  volcano     x {VOLCANO_X:.2f} y {VOLCANO_Y:.2f}   monument dropped onto the treeline")

    # ---- 1c · the lava field: the eruption reaches the ground ----------------------------
    # Eric dropped two extra fissure plates — "i hit you with a couple extra magma vents cuz they are
    # sooo cool" — and the best use of them is not a third window. Windows QUOTE the world; these put
    # the eruption INTO it. Blended onto the plain at the cone's foot, the volcano stops being a
    # picture of a distant disaster and becomes the reason the left third of this world is dying.
    #
    # Two different plates rather than one twice — the same rule the litter band follows, and for the
    # same reason: one texture used twice reads as wallpaper, and a repeated lava flow would read as a
    # copy-paste faster than almost anything else on the plate.
    #
    # Lighten, not alpha: the plates are incandescent channels on near-black crust, which is the exact
    # tonal-extreme condition blend_into documents. The dark crust loses to our lit plain and vanishes;
    # only the glowing rivers survive. Keyed on warmth as well, so the grey ash haze in the source
    # cannot brighten our ground.
    # Aspect matters more than position here. The first attempt gave these a 690x97 strip — a 7:1
    # canvas — and blob_mask's radial term is dominated by the SHORT axis at that ratio: at the left
    # edge it is still ~18% opaque, which composited as a pale ruled trapezoid on the plain. Same trap
    # the macro windows hit, same fix, so the mask is explicitly damped to zero at its own bounds
    # rather than trusted to fall off on its own. Kept near the cone's foot and to the left so the
    # eruption does not eat the central plain the land cast needs.
    # The two plates want DIFFERENT blend modes, and that is not a detail. Lava's legibility comes
    # from the contrast between near-black crust and incandescent channels — lighten discards the
    # crust by construction (it loses to our lit plain), so a lighten-only lava field arrives as a
    # warm glow with no form, which is what the first attempt looked like. So the near field is
    # ALPHA-pasted: crust and channels both land, and a dark crusted flow is the correct thing for
    # ground to be. The second plate stays a lighten pass, because that is what lighten is genuinely
    # good at — adding light to a surface rather than adding an object to a scene. One flow, and the
    # glow it throws on the plain beside it.
    # PARKED 2026-07-29, and the reason is the law this file keeps re-learning: **a source plate's
    # geometry cannot be masked away.** Eric's two extra fissure plates are magnificent and they are
    # extreme CLOSE-UPS — a metre from a vent. Used as mid-distance ground they were cover-fit into a
    # ~4:1 strip, which crops a thin band of pure fountain glow with none of the crust-and-channel
    # contrast that makes lava legible, and no blend mode rescued it: lighten dropped the black crust
    # and gave a formless warm haze, alpha kept the crust and gave a soft pale wedge. Four attempts,
    # same failure, same cause as `ocean_shelf_dropoff` being a head-on wall.
    #
    # The idea is right — the eruption should reach the ground, not just be quoted in a lens — so the
    # wiring stays and waits for a plate shot FOR this slot: a flow seen at mid distance across a
    # plain, where the crust reads as ground. `land_lava_flow` in lp_plate_prompt.py. Until then the
    # magma plates do the job they are actually superb at, which is the window at the cone's foot.
    for lname, lx, ly, lw, lh, lseed, lmode in [
            ("land_lava_flow", 0.000, 0.398, 0.205, 0.132, 311, "alpha"),
            ("land_lava_glow", 0.170, 0.410, 0.150, 0.105, 317, "lighten")]:
        if not (CAND / f"{lname}.png").exists():
            continue
        fw2, fh2 = round(W * lw), round(H * lh)
        lav = cover(load(f"{lname}.png"), (fw2, fh2))
        la = np.asarray(lav, np.float32)
        wk = np.clip((la[..., 0] - la[..., 2] - 70.0) / 70.0, 0, 1)
        wk *= np.clip((la.max(axis=2) - 90.0) / 80.0, 0, 1)
        wk *= np.asarray(blob_mask((fw2, fh2), seed=lseed, softness=0.80), np.float32) / 255.0
        _ex = np.clip(np.minimum(np.arange(fw2), fw2 - 1 - np.arange(fw2)) / (fw2 * 0.16), 0, 1)
        _ey = np.clip(np.minimum(np.arange(fh2), fh2 - 1 - np.arange(fh2)) / (fh2 * 0.16), 0, 1)
        wk *= _ey[:, None] * _ex[None, :]
        if lmode == "alpha":
            # keep the crust: the mask is shape only, not a warmth key
            wk = (np.asarray(blob_mask((fw2, fh2), seed=lseed, softness=0.80), np.float32) / 255.0
                  * _ey[:, None] * _ex[None, :])
        _lm = Image.fromarray(np.clip(wk * 255, 0, 255).astype(np.uint8), "L") \
                   .filter(ImageFilter.GaussianBlur(3.0))
        lx0, ly0 = round(W * lx), round(H * ly)
        if lmode == "alpha":
            paste(scene, lav, (lx0, ly0), _lm)
        else:
            blend_into(scene, lav, (lx0, ly0, min(W, lx0 + fw2), min(H, ly0 + fh2)),
                       _lm.crop((0, 0, min(W, lx0 + fw2) - lx0, min(H, ly0 + fh2) - ly0)), "lighten")
        record(f"26_lava_{lname[-1]}", lav, (lx0, ly0), _lm)
        print(f"  lava        x {lx:.2f} y {ly:.2f}    {lname} on the plain, {lmode}")

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
    # `ocean_shelf_dropoff` is where criticism #2 actually came from, and it is worth naming: the
    # render is a sheer wall seen head-on, dropping into black across the whole frame. Composited
    # whole it does not *depict* a drop-off, it depicts a wall — no mask or grade was ever going to
    # fix that, because the geometry is in the pixels. Per PLATE_ASSEMBLY the answer is to harvest
    # only the region it nailed, which is the sunlit rippled shallows in its upper left, and let the
    # drop-off be built in code where it can be made to recede (see SEAFLOOR).
    if (CAND / "ocean_shelf_recede.png").exists():
        _sh = load("ocean_shelf_recede.png")          # shot for the job: oblique, converging
    else:
        _sh = load("ocean_shelf_dropoff.png")
        _sh = _sh.crop((0, 0, round(_sh.width * 0.42), round(_sh.height * 0.62)))
    shelf = cover(_sh, (ow, round(oh * 0.66))).convert("RGB")
    paste(ocean, shelf, (0, 0),
          organic_mask((ow, round(oh * 0.66)), "y", 0.58, 0.40, seed=31, warp=0.12)
          .point(lambda v: 255 - v))
    # The coastline leans now (COAST_TILT): near the bottom of the frame — the water closest to the
    # viewer — the land reaches further out, and toward the horizon the shore pulls back. That one
    # change is the difference between a shoreline and a vertical join.
    mx = np.asarray(organic_mask((ow, oh), "x", 0.16, 0.20, seed=17, warp=0.09,
                                 tilt=-COAST_TILT), np.float32)
    my = np.asarray(organic_mask((ow, oh), "y", 0.16, 0.24, seed=23, warp=0.07), np.float32)
    m = Image.fromarray((mx * my / 255.0).astype(np.uint8), "L")
    # Underwater detail passes, blended into the ocean region BEFORE it goes down on the scene so
    # they inherit the same coastline mask and can't spill onto the land. The ocean is the emptiest
    # quarter of the plate; each pass belongs to one depth band, shallow to deep, because a single
    # "underwater scene" laid over the whole wedge would flatten the drop-off that the abyss —
    # and therefore the Mosasaurus's scale — depends on.
    for name, y0, y1, edge, seed in [("ocean_algae_fringe.png", 0.00, 0.34, 0.62, 51),
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

    # ---- 2a1b · the water column reads as ZONES, not as one wash ---------------------------
    # Item 5, and the measurement that reframed it. Eric: "bring the ocean even more up in the right
    # corner so we can expand on the different layers." But the waterline IS the horizon — measured,
    # land and ocean both meet at y≈0.30, and the 0.40 transition on the land side is the near plain's
    # crest, not the skyline — so it cannot be raised on the right without the horizon breaking at the
    # coastline. The ocean already owns 70% of the height over there. What was missing was never room,
    # it was DIFFERENTIATION: one smooth gradient from surface to floor, which is a wash, not zones.
    #
    # Applied to the region AFTER the shelf and the detail passes are in it, so every submerged thing
    # inherits one water column — the same ordering argument the seafloor's own absorption makes.
    # Two corrections, both physical. Light falls off exponentially (Beer-Lambert), so most of the
    # loss belongs near the surface, which is exactly why the sunlit zone is thin and bright and the
    # twilight under it goes dark fast. Then each of SCOPE's four zone boundaries gets a small extra
    # step, so the eye can FIND the boundary with no line drawn: the tonal edge does the work the
    # brass hairlines will later merely label (§4). The envelope stays gentle because the plate
    # already carries a falloff of its own — the aim is structure, not more darkness.
    oa = np.asarray(ocean.convert("RGB"), np.float32)
    surf = 0.16                       # the region's top 16% dissolves into the sky; water starts below
    lt = np.clip((np.arange(oh, dtype=np.float32) / oh - surf) / (1 - surf), 0, 1)[:, None, None]
    kc = 3.1
    abz = 0.06 + 0.28 * ((1.0 - np.exp(-kc * lt)) / (1.0 - np.exp(-kc)))
    for zb, amt in ZONE_STEPS:
        abz = abz + amt * (0.5 + 0.5 * np.tanh((lt - zb) * 26.0))
    abz = np.clip(abz, 0.0, 0.90)
    # The tint has to FADE OUT with depth, and getting this wrong is instructive: WATER_TINT is a mid
    # teal, so mixing toward it at full strength in the abyss *lightens* near-black pixels — the first
    # attempt took the deepest water from 14 to 22 and made the void shallower, which is precisely the
    # thing this file protects (the abyss is the Mosasaurus's scale weapon). Physically the tint is
    # scattered sunlight, so it can only exist where sunlight still does. Colour lives in the upper
    # column; the deep gets darkness instead.
    oa = oa * (1 - abz * (1.0 - 0.88 * lt)) + WATER_TINT * (abz * (1.0 - 0.88 * lt))
    oa *= 1.0 - 0.58 * ((1.0 - np.exp(-2.6 * lt)) / (1.0 - np.exp(-2.6)))
    ocean = Image.fromarray(np.clip(oa, 0, 255).astype(np.uint8)).convert("RGBA")
    print(f"  ocean zones surface->floor  sunlit/twilight/deep/floor at "
          f"{'/'.join(f'{z:.2f}' for z, _ in ZONE_STEPS)} of the column (tonal, unlabelled)")

    paste(scene, ocean.convert("RGB"), (ox, oy), m)
    record("30_ocean", ocean.convert("RGB"), (ox, oy), m)
    print(f"  ocean       x~{COAST_X:.2f}          shelf -> drop-off -> abyss (wandering coastline)")

    # ---- 2a2 · the seafloor, so the abyss has a bottom to fall away into -------------------
    # See SEAFLOOR. The rock does not stop at the beach; the marine half of the section is what the
    # water sits on. Built from the same two marine lithology tiles the strata ribbon uses — Fox
    # Hills on the shelf, Pierre out in the deep — so the floor offshore is provably the same beds
    # you can read in the cutaway on land. That is the accuracy moat paying for itself twice.
    coast_line = np.full(W, W * COAST_X, np.float32)
    coast_line += (noise((1, W), octaves=(2, 5, 11), seed=17)[0] - 0.5) * 2 * W * 0.09
    coast_line += (np.linspace(0, 1, W, dtype=np.float32) * 0)      # profile is measured per column
    sf = seafloor_profile(W, H, coast_line)

    shelf_tex = cover(load("tex_foxhills.png"), (W, H))
    deep_tex = cover(load("tex_pierre.png"), (W, H))
    # foreshorten hard: the floor is a surface seen at a glancing angle, so its texture has to
    # compress toward the horizon or it reads as a wall painted with sand
    fa = np.asarray(shelf_tex, np.float32)
    da = np.asarray(deep_tex, np.float32)
    depth_t = np.clip((np.arange(H, dtype=np.float32)[:, None, None] - H * 0.28) / (H * 0.58), 0, 1)
    floor_a = fa * (1 - depth_t) + da * depth_t
    # light dies with depth, fast. This is the whole scale weapon: the eye reads the darkening as
    # distance, and the Mosasaurus hanging above it inherits that distance as size.
    floor_a *= 1.0 - 0.66 * (1.0 - np.exp(-2.6 * depth_t)) / (1.0 - np.exp(-2.6))
    # ...and everything down there is being looked at through several hundred metres of seawater.
    # See WATER_TINT: absorption is what tells the eye "submerged" rather than "lit ground", and
    # without it the shelf is a tan dune sitting in the middle of the sky.
    # Item 5, and the measurement that reframed it. Eric asked to "bring the ocean even more up in
    # the right corner so we can expand on the different layers" — but the waterline IS the horizon
    # (measured: land and ocean both meet at y≈0.30; the 0.40 transition is the near plain's crest),
    # so it cannot be raised on the right without breaking the horizon at the coastline. The ocean
    # already owns 70% of the height there. What was missing was not room, it was DIFFERENTIATION:
    # absorption was a straight line from WATER_MIN to WATER_MAX, and a linear ramp is a wash, not a
    # set of zones.
    #
    # Two corrections, both physical. Light falls off exponentially with depth (Beer-Lambert), so
    # most of the loss belongs in the first stretch — which is exactly why the sunlit zone is thin
    # and bright and the twilight below it goes dark fast. And each of SCOPE's four zone boundaries
    # gets a small extra step, so the eye can find the boundary without a ruled line being drawn:
    # the tonal band edge does the work the brass hairlines will later label (§4).
    k = 3.1
    absorb = WATER_MIN + (WATER_MAX - WATER_MIN) * (
        (1.0 - np.exp(-k * depth_t)) / (1.0 - np.exp(-k)))
    for zb, amt in ZONE_STEPS:
        absorb = absorb + amt * (0.5 + 0.5 * np.tanh((depth_t - zb) * 26.0))
    absorb = np.clip(absorb, 0.0, 0.93)
    floor_a = floor_a * (1 - absorb) + WATER_TINT * absorb
    floor_a = floor_a * (1 - 0.16 * depth_t) + np.array([8, 15, 26], np.float32) * (0.16 * depth_t)
    # Shell beds are not suspended in the water column — they ARE the bottom. Wired as a midwater
    # detail pass they composited as a band of rubble hanging in open water halfway down the
    # abyss. They belong to the floor's shallow half, where accumulation actually happens, and
    # they inherit the same depth absorption as everything else down there.
    if (CAND / "ocean_shell_beds.png").exists():
        sb = np.asarray(cover(load("ocean_shell_beds.png"), (W, H)), np.float32)
        sb = sb * (1 - absorb) + WATER_TINT * absorb
        band = np.clip(1.0 - np.abs(depth_t - 0.22) / 0.34, 0, 1) ** 1.2
        band = band * (0.45 + 0.75 * noise((H, W), octaves=(3, 8, 19), seed=57)[..., None])
        floor_a = floor_a * (1 - band * 0.8) + sb * (band * 0.8)
        print("  shell beds  shelf floor     accumulated shell hash, ON the bottom not above it")
    floor = Image.fromarray(np.clip(floor_a, 0, 255).astype(np.uint8))
    fm = np.asarray(below((W, H), sf, feather=H * 0.105), np.float32)
    fm *= np.asarray(organic_mask((W, H), "x", COAST_X + 0.012, 0.055, seed=17, warp=0.09,
                                  tilt=-COAST_TILT), np.float32) / 255.0
    _fm = Image.fromarray(fm.astype(np.uint8), "L")
    paste(scene, floor, (0, 0), _fm)
    record("32_seafloor", floor, (0, 0), _fm)

    # the shelf break, caught by the light — the edge the drop-off happens at
    brk = Image.new("L", (W, H), 0)
    bd = ImageDraw.Draw(brk)
    for x in range(0, W, 3):
        bd.line((x, sf[x] - 4, x, sf[x] + 4), fill=180)
    ba = np.asarray(brk.filter(ImageFilter.GaussianBlur(H * 0.010)), np.float32)
    # Only over the slope itself. The first version lit the whole shelf edge and drew a pale crest
    # right across the frame — a highlight that long stops being an edge and becomes a dune ridge.
    ba *= np.clip(1.0 - np.abs(sf[None, :] / H - 0.55) / 0.20, 0, 1)
    ba *= np.asarray(organic_mask((W, H), "x", COAST_X + 0.03, 0.05, seed=17, warp=0.09,
                                  tilt=-COAST_TILT), np.float32) / 255.0
    _brk = Image.merge("RGBA", (*Image.new("RGB", (W, H), (150, 196, 190)).split(),
                                Image.fromarray(np.clip(ba * 0.30, 0, 255).astype(np.uint8), "L")))
    scene.alpha_composite(_brk)
    LAYERS.append(("33_shelf_break", _brk))
    print(f"  seafloor    coast->right    shelf {SEAFLOOR[1][1]:.2f}H -> break -> abyssal plain "
          f"{SEAFLOOR[-1][1]:.2f}H (the drop-off recedes)")

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

    # ---- 2c · the left bench (criticism #5) -----------------------------------------------
    # The mid-left is the poster's emptiest and most valuable real estate. The rain cell gives it
    # atmosphere but atmosphere is not terrain — an undifferentiated plain with weather over it is
    # still an undifferentiated plain. A low eroded bench running away obliquely gives that third
    # of the frame a middle distance, and gives the `mid` and `far` staging planes something to
    # stand on over there instead of open ground.
    if (CAND / "land_left_bench.png").exists():
        lw, lh = round(W * 0.40), round(H * 0.20)
        lx, ly = round(W * 0.015), round(H * 0.325)
        # Crop the source's own sky away first. This patch sits BELOW the plate's real horizon, and
        # every usable render of a terrace carries its own horizon about a third down — dropped in
        # whole that composites as a second horizon line inside the first, which no mask hides
        # because the eye finds horizons by their straightness, not their edges.
        _bn = load("land_left_bench.png")
        _bn = _bn.crop((0, round(_bn.height * 0.34), _bn.width, _bn.height))
        ben = cover(_bn, (lw, lh))
        _lm = blob_mask((lw, lh), seed=311, softness=0.86)
        paste(scene, ben, (lx, ly), _lm)
        record("36_left_bench", ben, (lx, ly), _lm)
        print("  bench       x 0.02 y 0.33    eroded terrace — the empty left third gets a middle distance")

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
    ribbon_rgba = Image.open(ribbon_png).convert("RGBA")
    # The renderer now hands back its own alpha: the eroded land surface at the top, and the
    # ravines that cut clean through the section. Both are geology, so neither is this file's
    # business to invent — it just has to stop throwing the channel away, which the old
    # `.convert("RGB")` did.
    ribbon_alpha = np.asarray(ribbon_rgba.getchannel("A"), np.float32) / 255.0
    ribbon = ribbon_rgba.convert("RGB")
    # Grade the soil the way the ocean is graded: depth darkens it. A flat evenly-lit band read
    # pale and papery against the litter above; falling off into the dark makes the ground feel
    # like it continues below the frame instead of stopping at a printed edge, and it rhymes with
    # the abyss on the other side of the plate.
    ra = np.asarray(ribbon, np.float32) * STRATA_LIFT + 7
    depth = np.linspace(0, 1, ra.shape[0], dtype=np.float32)[:, None, None]
    ra *= (1.0 - 0.38 * depth ** 1.35)
    ra = ra * (1 - 0.13 * depth) + np.array([26, 22, 18], np.float32) * (0.13 * depth)
    ribbon = Image.fromarray(np.clip(ra, 0, 255).astype(np.uint8))
    # soil belongs to the land side only — fade it out under the sea, on the same wandering
    # coastline the ocean uses, so the two edges agree instead of crossing each other
    sy = np.asarray(organic_mask((rw, rh), "y", 0.34, 0.26, seed=71, warp=0.10), np.float32)
    sx = np.asarray(organic_mask((rw, rh), "x", COAST_X + 0.06, 0.10, seed=17, warp=0.06,
                                 tilt=-COAST_TILT).point(lambda v: 255 - v), np.float32)
    _sm = Image.fromarray((sy * sx * ribbon_alpha / 255.0).astype(np.uint8), "L")
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
    # Every entry is (slot, x, y-offset from the litter top, width, height, flip) — all as canvas
    # FRACTIONS. They were absolute pixels tuned against the module default of 3000x2000, and the
    # poster's scene slot is 3000x1300: a y-offset of 505 px and a height of 545 px meant something
    # completely different on a canvas 700 px shorter, so both habitats hung off the bottom edge and
    # the mushrooms composited sliced in half by the frame. Nothing else in this file uses pixels;
    # this table was the last holdout.
    MICRO = [("micro_log_interior",     0.010, 0.1175, 0.373, 0.350, False),
             ("micro_moss_cushion",     0.150, 0.2350, 0.253, 0.235, False),
             ("micro_fern_crozier",     0.268, 0.0900, 0.173, 0.330, False),
             ("micro_puddle_edge",      0.352, 0.1500, 0.215, 0.280, False),
             ("micro_mushroom_cluster", 0.335, 0.2100, 0.293, 0.273, True),
             ("micro_bark_crevice",     0.050, 0.0600, 0.157, 0.310, True)]
    # a plate that ends up under two neighbours needs its contrast back
    MICRO_LIFT = {"micro_mushroom_cluster": 1.20}
    placed = [m for m in MICRO if (CAND / f"{m[0]}.png").exists()]
    if not placed and (CAND / "micro_hollow.png").exists():
        # the pre-set fallback: one hollow, twice, mirrored so it doesn't read as one image reused
        placed = [("micro_hollow", 0.015, 0.1250, 0.393, 0.360, False),
                  ("micro_hollow", 0.335, 0.2100, 0.313, 0.290, True)]
    # "All stay on the land side" was a comment, not a mechanism, and the comment was wrong: the
    # mushrooms run to x 0.628 and the puddle to 0.715 against a coastline at 0.55, so both were
    # compositing over open water. The puddle made it obvious — a freshwater rain pool in the sea,
    # with the blob mask's own bounds showing as a ruled rectangle in the water (the trap this file
    # already documents: a mask still partly opaque where its canvas ends IS a straight edge).
    # So it is enforced here instead. Same seed, warp and tilt as the coastline itself, so the front
    # band ends exactly where the water begins rather than at some second, disagreeing line.
    land_hold = organic_mask((W, H), "x", COAST_X + 0.012, 0.055, seed=17, warp=0.09,
                             tilt=-COAST_TILT).point(lambda v: 255 - v)
    for i, (slot, fx, fy, fw, fh, flip) in enumerate(placed):
        mw, mh = round(W * fw), round(H * fh)
        fy = round(H * fy)
        src = load(f"{slot}.png")
        if flip:
            src = src.transpose(Image.FLIP_LEFT_RIGHT)
        hab = cover(src, (mw, mh))
        if slot in MICRO_LIFT:
            _ha = np.asarray(hab, np.float32) * MICRO_LIFT[slot] + 5
            _ha = np.where(_ha > 205, 205 + (_ha - 205) * 0.45, _ha)
            hab = Image.fromarray(np.clip(_ha, 0, 255).astype(np.uint8))
        mx0, my0 = round(W * fx), ft + fy
        _hm = blob_mask((mw, mh), seed=133 + i * 29, softness=0.80)
        _hm = Image.fromarray(
            (np.asarray(_hm, np.float32)
             * (np.asarray(land_hold.crop((mx0, my0, mx0 + mw, my0 + mh)), np.float32) / 255.0)
             ).astype(np.uint8), "L")
        paste(scene, hab, (mx0, my0), _hm)
        record(f"60_micro_{i+1}_{slot}", hab, (mx0, my0), _hm)
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
    for wi, spec in enumerate(MACRO_WINS if placed else []):
        # Resolve against BOTH directories, exactly as load() does. Checking only `candidates/`
        # meant the geological window could never find `tex_bentonite` — which lives in `plates/`
        # because it is a strata tile — and silently fell through to a forest habitat instead.
        slot = next((s for s in (spec["slots"] or ())
                     if (CAND / f"{s}.png").exists() or (PLATES / f"{s}.png").exists()), None)
        if slot is None and spec.get("require"):
            print(f"  macro win {wi + 1} SKIPPED         needs one of: "
                  f"{', '.join(spec['slots'])} — a window magnifies what is BEHIND it, "
                  f"so it stays dark rather than showing the wrong realm")
            continue
        slot = slot or placed[min(wi, len(placed) - 1)][0]
        mx0, my0 = round(W * spec["box"][0]), round(H * spec["box"][1])
        mx1, my1 = round(W * spec["box"][2]), round(H * spec["box"][3])
        bw2, bh2 = mx1 - mx0, my1 - my0
        # zoomed FURTHER in than the same plate reads at in the front band — that difference in
        # magnification is the whole message of the window
        over = round(bh2 * spec["over"])         # how far past the rule the habitat escapes
        cw, ch = bw2 + over, bh2 + over
        big = load(f"{slot}.png")
        if spec["flip"]:
            big = big.transpose(Image.FLIP_LEFT_RIGHT)
        c0, c1, c2, c3 = spec["crop"]
        big = cover(big.crop((round(big.width * c0), round(big.height * c1),
                              round(big.width * c2), round(big.height * c3))), (cw, ch))
        # A window in a dark corner has to carry its own light or it reads as a hole rather than as
        # an enlargement. But a fixed multiplier only suits the plate it was tuned on: 1.22 was set
        # against the dark fallback hollow, and the first real plate to land was bright enough that
        # the same number clipped half the window to paper white — which reads as a blown highlight,
        # not an enlargement, and is the loudest thing on the plate. So the lift is normalised
        # against the content's own mean and `lift` becomes a bias on top of that. Every plate that
        # lands from here gets the same exposure regardless of how the render came out.
        ba = np.asarray(big, np.float32)
        gain = np.clip(118.0 / max(1.0, float(ba.mean())), 0.80, 1.45) * spec["lift"]
        ba = ba * gain + 8
        # protect the top end: compress rather than clip, so texture survives in the brightest wood
        ba = np.where(ba > 200, 200 + (ba - 200) * 0.42, ba)
        # Exposure was never the whole problem. A window also has to be lit by the SAME SUN as the
        # plate, and `geo_volcanic_ash` proved it: pale grey ash dropped into a low-orange sunset world
        # read as a boulder pasted on, in the sky and on the ground alike, because no amount of
        # brightness fixes a hue that belongs to a different time of day. This is the same argument
        # `place_on_backdrop.py` makes when it refuses to give an underwater animal the sunset haze.
        #
        # Multiplicative rather than a mix toward a flat colour: grey material under warm light is
        # grey times the light, so scaling the channels warms it while leaving every bit of the
        # texture contrast — which is the one thing a magnification window may not give up.
        if spec.get("warm"):
            w = float(spec["warm"])
            ba *= np.array([1.0 + w * 0.30, 1.0, 1.0 - w * 0.28], np.float32)
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
        cx, cy, rad = bw2 * spec["lobe_x"], float(over), bw2 * 0.30
        lobe = np.exp(-(((gx - cx) ** 2 + ((gy - cy) * 2.2) ** 2) / (2 * rad * rad)))
        # `hybrid` adds two more escape points on other sides. One break reads as a single decision;
        # three read as something that is genuinely growing out of the frame — which is what "blend
        # them so they flow organically" is asking for, without touching the rule's crispness.
        if args.windows == "hybrid":
            for lx, ly, lr in ((0.06, 0.42, 0.24), (0.72, 1.00, 0.20)):
                px2, py2 = bw2 * lx, over + bh2 * ly
                rr = bw2 * lr
                lobe = np.maximum(lobe, 0.85 * np.exp(
                    -(((gx - px2) ** 2 + ((gy - py2) * 1.4) ** 2) / (2 * rr * rr))))
        lobe *= 0.72 + 0.55 * noise((ch, cw), octaves=(2, 5, 11), seed=spec["seed"])
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

        # The CONTENT has to be rounded too, not just the rule drawn over it. A square photograph
        # behind a rounded frame leaves four little corners of image poking out past the brass,
        # which is more obviously wrong than square corners ever were.
        rfield = None
        if args.windows == "glass":
            # THE SHIPPED TREATMENT. Eric, 2026-07-29: *"i like no borders, remember the transparency
            # looks soo cool. each micro view will be its own custom shape. it really pops on the
            # poster when you step back and look at it."*
            #
            # This is the combination none of the first three modes was: `soft` dropped the rule but
            # kept a primitive outline, and `lens` got the custom outline but had a brass ring bolted
            # round it. Here the aperture supplies the custom shape, the bulge supplies the glass, and
            # the rim DISSOLVES instead of being drawn — so the thing that separates the window from
            # the plate is magnification and curvature, not a border.
            #
            # Why it pops at a distance rather than disappearing: a dissolving edge removes the
            # highest-frequency detail in the region, and at reading distance high frequency is the
            # first thing to go anyway. What survives the walk backwards is the low-frequency
            # difference — a patch of the plate at a different scale and a different contrast — which
            # is exactly the signal that says "look closer". A ruled border is the opposite: it is
            # pure high frequency, so it is loud up close and gone at six feet.
            rfield = aperture((bw2, bh2), seed=spec["seed"],
                              roundness=spec.get("roundness", 2.2),
                              wobble=spec.get("wobble", 0.12))
            # Wander the radius in 2D as well as per-angle, so the dissolve itself is organic. Same
            # law as every other seam on this plate: nothing in nature has a ruled edge, and that now
            # includes the edge of the window.
            warp = 0.90 + 0.20 * noise((bh2, bw2), octaves=(2, 5, 11), seed=spec["seed"] + 7)
            edge = spec.get("dissolve", 0.38)
            t = np.clip((1.0 - rfield * warp) / edge, 0, 1)
            shaped = t * t * (3.0 - 2.0 * t)      # smoothstep: no visible start-of-fade contour
            big = barrel(big, spec.get("barrel", 0.15))
        elif args.windows == "lens":
            # Eric, 2026-07-29: each window its own unique shape, "like a magnifying glass popping
            # out of the scene". Both halves of that matter and they are separate mechanisms: the
            # APERTURE stops the outline being a primitive (a circle and a rounded rectangle are
            # both shapes software owns), and the BARREL bulge is what makes it read as glass rather
            # than as a differently-shaped crop. Shape alone just relocates the artefact.
            rfield = aperture((bw2, bh2), seed=spec["seed"],
                              roundness=spec.get("roundness", 3.2),
                              wobble=spec.get("wobble", 0.16))
            # Feather in the shape's OWN units, sized to land at ~2 px, so the glass rim stays crisp
            # (it is a hard edge in the world) without aliasing along the wander.
            feath = 2.0 / max(4.0, min(bw2, bh2) / 2.0)
            shaped = np.clip((1.0 - rfield) / feath, 0, 1)
            # Outside r = 1 the bulge is identity, so this leaves the escape lobe undistorted for
            # free — the content that has climbed out of the glass is not seen through it.
            big = barrel(big, spec.get("barrel", 0.15))
        else:
            corner = Image.new("L", (bw2, bh2), 0)
            if spec.get("shape") == "circle":
                ImageDraw.Draw(corner).ellipse((0, 0, bw2 - 1, bh2 - 1), fill=255)
            else:
                ImageDraw.Draw(corner).rounded_rectangle((0, 0, bw2 - 1, bh2 - 1),
                                                         radius=round(W * WIN_RADIUS), fill=255)
            shaped = np.asarray(corner, np.float32) / 255.0
        # ---- the three window modes (--windows) ---------------------------------------------
        # `crisp` is the shipped behaviour and the argument behind it: every other edge on the plate
        # is noise-warped precisely so nothing reads as drawn, so the one clean edge reads as an
        # INSTRUMENT of the poster rather than a compositing artefact.
        # `soft` is the opposite proposition — no rule at all, the content simply dissolving into
        # the plate. `hybrid` keeps the crisp rule and softens only what is inside it.
        if args.windows in ("soft", "hybrid"):
            # radial falloff measured in units of the shape's own half-size, so it behaves the same
            # on the tall circles and the wide rectangle
            ny = (np.arange(bh2, dtype=np.float32)[:, None] - bh2 / 2) / (bh2 / 2)
            nx = (np.arange(bw2, dtype=np.float32)[None, :] - bw2 / 2) / (bw2 / 2)
            r2 = np.sqrt(np.clip(nx * nx + ny * ny, 0, None))
            start = 0.30 if args.windows == "soft" else 0.72   # where the fade begins
            fade = np.clip((1.0 - r2) / max(1e-3, 1.0 - start), 0, 1)
            fade *= 0.55 + 0.75 * noise((bh2, bw2), octaves=(2, 5, 12), seed=spec["seed"] + 5)
            shaped = shaped * np.clip(fade, 0, 1)
        mask = np.zeros((ch, cw), np.float32)
        mask[over:, :bw2] = shaped                                    # the framed content
        mask = np.maximum(mask, lobe)                                 # the part that escapes

        # A window may now sit hard against the top edge — Eric wants the volcano cluster high in the
        # corner — and then its escape lobe starts ABOVE the canvas. Both consumers of that origin
        # fail differently and neither fails loudly: PIL's alpha_composite rejects a negative
        # destination outright, and the numpy slice for the rule's cut degenerates to height 0 and
        # raises a broadcast error. Trim the content down to the canvas rather than nudging the box,
        # because moving the box to suit the compositor is letting the code pick the composition.
        py0 = my0 - over
        if py0 < 0:
            big = big.crop((0, -py0, big.width, big.height))
            mask, lobe = mask[-py0:, :], lobe[-py0:, :]
            ch, py0 = mask.shape[0], 0

        # ---- the glass sits PROUD of the plate ------------------------------------------------
        # This is what "popping out of the scene" actually needs, and the aperture shape alone does
        # not supply it: a hole and a lens can have identical outlines. What separates them is that
        # a lens is an object in front of the poster, so it casts onto it. Shadow first, under the
        # content; the lit rim comes after, on top of the ring.
        # Direction is not free — the whole plate is keyed from the upper right (the micro plates are
        # shot "raking in from the upper right", the strata are lit from there, the grade agrees), so
        # the shadow falls down-left or the window belongs to a different world than its own contents.
        if rfield is not None and args.windows == "lens":
            sdx, sdy = -round(bw2 * 0.020), round(bh2 * 0.026)
            sm = np.zeros((H, W), np.float32)
            ty0, tx0 = my0 + sdy, mx0 + sdx
            sy0, sx0 = max(0, ty0), max(0, tx0)
            sy1, sx1 = min(H, ty0 + bh2), min(W, tx0 + bw2)
            if sy1 > sy0 and sx1 > sx0:
                sm[sy0:sy1, sx0:sx1] = shaped[sy0 - ty0:sy1 - ty0, sx0 - tx0:sx1 - tx0]
            _sh = Image.fromarray((np.clip(sm, 0, 1) * 150).astype(np.uint8), "L") \
                       .filter(ImageFilter.GaussianBlur(max(3.0, W * 0.006)))
            _shl = Image.merge("RGBA", (*Image.new("RGB", (W, H), (8, 7, 9)).split(), _sh))
            scene.alpha_composite(_shl)
            LAYERS.append((f"6{2 + wi * 2}_macro_window_{wi + 1}_dropshadow", _shl))
        _mm = Image.fromarray((np.clip(mask, 0, 1) * 255).astype(np.uint8), "L") \
                   .filter(ImageFilter.GaussianBlur(5.0 if args.windows in ("soft", "hybrid") else 1.6))
        paste(scene, big, (mx0, py0), _mm)
        record(f"6{2 + wi * 2}_macro_window_{wi + 1}", big, (mx0, py0), _mm)

        if args.windows in ("soft", "glass"):
            _lbl = ("no border, dissolving rim, own shape"
                    if args.windows == "glass" else "SOFT, no rule")
            print(f"  macro win {wi + 1} {spec['box'][0]:.2f},{spec['box'][1]:.2f}      "
                  f"{slot.replace('micro_', '').replace('ocean_', '')} — {_lbl}")
            continue

        # the brass rule, genuinely interrupted where the habitat crosses it
        rad = round(W * WIN_RADIUS)
        rw3 = max(2, round(H * 0.0035 * (1 if wi == 0 else 0.7)))
        if rfield is not None:
            # The ring is pulled from the same radius field as the aperture, so the metal follows the
            # wander exactly. Drawing it as a separate primitive would put a ruled ellipse next to an
            # organic edge and undo the whole point.
            #
            # The profile needs a PLATEAU, not a peak. `1 - |r-1|/t` is triangular: it only reaches
            # full alpha on the single contour r == 1, so a nominally 5 px ring averages well under
            # half strength and the metal reads as a ghost beside the crisp variant's solid stroke.
            # Full alpha out to 0.55t, falling to nothing at 1.25t, matches a drawn stroke's weight
            # while keeping an antialiased edge on both sides.
            t = rw3 / max(4.0, min(bw2, bh2) / 2.0)
            prof = np.clip((1.25 - np.abs(rfield - 1.0) / t) / 0.70, 0, 1)
            ra = np.zeros((H, W), np.float32)
            ra[my0:my0 + bh2, mx0:mx0 + bw2] = prof * 255.0
        else:
            rule = Image.new("L", (W, H), 0)
            rd = ImageDraw.Draw(rule)
            if spec.get("shape") == "circle":
                rd.ellipse((mx0, my0, mx1, my1), outline=255, width=rw3)
            else:
                rd.rounded_rectangle((mx0, my0, mx1, my1), radius=rad, outline=255, width=rw3)
            ra = np.asarray(rule, np.float32)
        cut = np.zeros((H, W), np.float32)
        y0c, x0c = py0, mx0
        cut[y0c:y0c + ch, x0c:x0c + cw] = lobe
        ra *= 1.0 - np.clip(cut * 1.9, 0, 1)
        # Flat brass is correct for small repeated furniture (SCOPE §4 brass finish), but a ring that
        # is claiming to be the edge of a physical lens is not small repeated furniture — it is a
        # round object, and a round object lit from one side is brighter on that side. Without this
        # the ring reads as a drawn outline sitting ON the plate rather than as metal above it.
        ringrgb = Image.new("RGB", (W, H), BRASS)
        if rfield is not None:
            ny2 = (np.arange(bh2, dtype=np.float32)[:, None] - bh2 / 2) / (bh2 / 2)
            nx2 = (np.arange(bw2, dtype=np.float32)[None, :] - bw2 / 2) / (bw2 / 2)
            n = np.sqrt(np.clip(nx2 * nx2 + ny2 * ny2, 1e-6, None))
            lit = np.clip(0.5 + 0.5 * (nx2 / n * 0.70 + (-ny2 / n) * 0.71), 0, 1) ** 1.3
            patch = (np.array(BRASS, np.float32) * (1 - lit[..., None])
                     + np.array(BRASS_HI, np.float32) * lit[..., None])
            ringrgb.paste(Image.fromarray(np.clip(patch, 0, 255).astype(np.uint8), "RGB"),
                          (mx0, my0))
        _rule = Image.merge("RGBA", (*ringrgb.split(),
                                     Image.fromarray(ra.astype(np.uint8), "L")))
        scene.alpha_composite(_rule)
        LAYERS.append((f"6{3 + wi * 2}_macro_window_{wi + 1}_rule", _rule))
        _how = (f"LENS r{spec.get('roundness', 3.2):.1f} w{spec.get('wobble', 0.16):.2f} "
                f"k{spec.get('barrel', 0.15):.2f}" if rfield is not None else "breaks its frame")
        print(f"  macro win {wi + 1} {spec['box'][0]:.2f},{spec['box'][1]:.2f}      "
              f"{slot.replace('micro_', '').replace('ocean_', '')} {_how} (Law #2)")

    # ---- 4c3 · registration ticks: the rule, established as vocabulary --------------------
    # Two windows are a system only if the poster has already told you that a brass straight line is
    # one of its instruments. Four corner ticks do that for the price of almost no ink — the same
    # metal, the same weight, drawn where nothing is happening. They read as the plate's own
    # register marks, so by the time the eye reaches a window the ruled box is a continuation of
    # something rather than the first and only one of its kind.
    ticks = Image.new("L", (W, H), 0)
    td = ImageDraw.Draw(ticks)
    tk, inset, tw2 = round(W * 0.021), round(W * 0.012), max(2, round(H * 0.0022))
    for cxr, cyr in ((0, 0), (1, 0), (0, 1), (1, 1)):
        px = inset if cxr == 0 else W - inset
        py = round(H * 0.030) if cyr == 0 else H - round(H * 0.030)
        sx2 = 1 if cxr == 0 else -1
        sy2 = 1 if cyr == 0 else -1
        td.line((px, py, px + sx2 * tk, py), fill=150, width=tw2)
        td.line((px, py, px, py + sy2 * round(tk * 0.62)), fill=150, width=tw2)
    # In `soft` mode the windows have no rule, so corner register marks are vocabulary for a
    # language the poster no longer speaks — four brass ticks and nothing else ruled anywhere.
    if args.windows not in ("soft", "glass"):
        _tk = Image.merge("RGBA", (*Image.new("RGB", (W, H), BRASS).split(), ticks))
        scene.alpha_composite(_tk)
        LAYERS.append(("68_registration_ticks", _tk))
        print("  ticks       4 corners       brass register marks — the rule as vocabulary, not accident")

    # ---- 4d · the asteroid whisper (SCOPE §217) -----------------------------------------
    # A single faint cold point with a short streak, high in the empty top-left indigo. Subtle
    # enough to miss until you know — not a competing monument.
    # Moved right and down from (0.135, 0.085): the title comes to this corner (criticism #8), and
    # the whisper used to sit exactly where the type now lands. It stays in the same quiet quarter,
    # just clear of the words — the two sharing a corner is the point, overlapping is not.
    ax, ay = round(W * 0.430), round(H * 0.098)
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

    # ---- 4d2 · the Deccan whisper -------------------------------------------------------
    # Eric's, 2026-07-29, and its twin already existed. The asteroid gets a whisper because it is
    # in the sky and can be drawn; the OTHER end-Cretaceous kill mechanism — the Deccan Traps
    # flood basalts, erupting through the boundary — is 12,000 km away in India and cannot be seen
    # from Montana at all.
    #
    # But its *air* can. A large eruption loads the stratosphere with sulphate aerosol, and the
    # documented signature is a sunset that is wrong: a high, thin, banded veil, too red, sitting
    # above the real glow. Krakatoa produced exactly this in 1883 and it was painted from life. So
    # the poster can carry the second killer honestly, as the reason its sky looks the way it does.
    #
    # The pairing is the point, and it is a pairing of KINDS, not of shapes. The asteroid is a
    # point: sharp, cold, locatable, one thing you could put a finger on. The Deccan is a stain:
    # warm, diffuse, banded, everywhere and nowhere. Drawing the second as another bright mark
    # would have made it a twin of the wrong sort — two objects in a sky instead of two ways of
    # being doomed. It sits well above the true horizon glow so it reads as stratospheric, i.e.
    # not weather.
    dgx = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    dgy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    veil = np.zeros((H, W), np.float32)
    for cy2, amp, thick in ((0.062, 1.00, 0.017), (0.085, 0.72, 0.011),
                            (0.104, 0.55, 0.022), (0.128, 0.34, 0.009)):
        veil += amp * np.exp(-(((dgy - cy2) / thick) ** 2))
    veil *= np.exp(-(((dgx - 0.63) / 0.34) ** 2))          # thickest where the light comes from
    veil *= 0.55 + 0.85 * noise((H, W), octaves=(2, 6, 14), seed=911)
    veil = np.clip(veil, 0, 1) * 0.115                     # a whisper: miss it until you know
    arr_d = np.asarray(scene.convert("RGB"), np.float32)
    arr_d = arr_d + np.array([205, 92, 74], np.float32) * veil[..., None]
    scene = Image.fromarray(np.clip(arr_d, 0, 255).astype(np.uint8)).convert("RGBA")
    LAYERS.append(("71_deccan_whisper", Image.merge(
        "RGBA", (*Image.new("RGB", (W, H), (205, 92, 74)).split(),
                 Image.fromarray((veil / 0.115 * 255).astype(np.uint8), "L")))))
    print("  deccan      high sky        sulphate aerosol veil — the other killer, seen as its air")

    # ---- 4e · air traffic (criticism #6) ---------------------------------------------------
    # "Nothing is in the air" is the criticism that quietly contradicts the whole thesis: a poster
    # whose argument is that every organism has a home cannot leave a third of its surface as
    # scenery. Quetzalcoatlus is already on the roster (CR06) at an 11 m span, so the sky is
    # somebody's habitat whether or not it is drawn as one.
    #
    # Placement does a second job. The mid-left was the emptiest quarter of the plate (criticism
    # #5), and birds cost nothing to put there — so the flock is weighted left, high and small at
    # the back, larger and lower as it comes forward, which reads as one group crossing the frame
    # rather than as decals scattered on the sky.
    AIR = [(0.115, 0.300, 96), (0.163, 0.352, 132), (0.086, 0.395, 178),
           (0.212, 0.268, 74), (0.258, 0.318, 58), (0.318, 0.238, 44),
           (0.392, 0.208, 34), (0.447, 0.262, 30), (0.072, 0.198, 40),
           (0.505, 0.196, 26), (0.148, 0.150, 22)]
    air = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for i, (fx, fy, span) in enumerate(AIR):
        span = max(10, round(span * W / 3000))
        bird = pterosaur(span, seed=900 + i * 7)
        # aerial perspective on the wing, not just on the ground: the small ones are far, so they
        # sit closer to the haze and lose contrast. Without this a 22 px silhouette at full black
        # punches a hole in the sky and reads as a speck of dirt on the print.
        near = np.clip((span / (96 * W / 3000)) ** 0.7, 0.22, 1.0)
        a = np.asarray(bird, np.float32) * (0.30 + 0.52 * near)
        tint_a = Image.new("RGB", bird.size, (58, 48, 52))
        layer_b = Image.merge("RGBA", (*tint_a.split(), Image.fromarray(a.astype(np.uint8), "L")))
        air.alpha_composite(layer_b, (round(W * fx), round(H * fy)))
    # ...and the other end of Law #2: insects at macro scale, next to the window that announces the
    # magnification change. The sky is habitat at 11 m of wingspan and at 4 mm of it.
    if (CAND / "air_insect_swarm.png").exists():
        iw, ih = round(W * 0.22), round(H * 0.20)
        ix, iy = round(W * 0.255), round(H * 0.545)
        sw = cover(load("air_insect_swarm.png"), (iw, ih))
        _im = blob_mask((iw, ih), seed=821, softness=0.84)
        paste(scene, sw, (ix, iy), _im)
        record("73_insect_swarm", sw, (ix, iy), _im)
        print("  insects     x 0.26 y 0.55    macro swarm beside the window (Law #2, the other end)")
    scene.alpha_composite(air)
    LAYERS.append(("72_air_traffic", air))
    print(f"  air         mid-left        {len(AIR)} azhdarchids, far/small to near/large "
          f"(the sky becomes habitat)")

    # ---- 4f · a second weather (criticisms #5 and #9) --------------------------------------
    # One light, one hour, one weather flattens three million years into a single evening — and the
    # left third of the plate was doing no work at all. Both are the same hole, and a rain cell is
    # the same fix: a squall standing over the mid-left plain, with the warm sunset key surviving
    # only to the right of it.
    #
    # A weather cell is three things stacked, and it fails if you build fewer: a darkened, cooled
    # cloud base; a curtain of fallout hanging *below* that base and not reaching the ground
    # cleanly; and the ground beneath it robbed of the warm key. Rain without the dark base reads
    # as a scratched negative, and a dark base without the fallout reads as a smudge.
    if not args.no_weather and (CAND / "sky_squall_cell.png").exists():
        # A shot cell beats a synthesised one for the same reason every other slot here is
        # harvested: real fallout has structure — the curtain is ragged, it evaporates before it
        # lands, and the base is a shape rather than a gradient. The procedural version below
        # exists so the composition can be judged before the render arrives, not instead of it.
        sw2, sh2 = round(W * 0.46), round(H * 0.42)
        sx2, sy2 = round(W * 0.015), round(H * 0.020)
        sq = cover(load("sky_squall_cell.png"), (sw2, sh2))
        _sq = blob_mask((sw2, sh2), seed=617, softness=0.90)
        paste(scene, sq, (sx2, sy2), _sq)
        record("74_weather_cell", sq, (sx2, sy2), _sq)
        print("  weather     x 0.02-0.48     harvested squall cell (two hours, not one)")
    elif not args.no_weather:
        cxw, cw2 = 0.300, 0.215          # centre and half-width of the cell, canvas fractions
        gxw = np.linspace(0, 1, W, dtype=np.float32)[None, :]
        gyw = np.linspace(0, 1, H, dtype=np.float32)[:, None]
        across = np.exp(-(((gxw - cxw) / cw2) ** 2) * 1.9)
        across = across * (0.72 + 0.56 * noise((1, W), octaves=(2, 6, 13), seed=613))
        # the cell occupies the air between the cloud base and the horizon, fading out on the ground
        band = np.clip(1.0 - np.abs(gyw - 0.205) / 0.215, 0, 1) ** 1.25
        cell = np.clip(across * band, 0, 1)

        # The fallout: fine near-vertical streaking, sheared with the wind.
        #
        # `noise()` cannot do this. It builds from square grids, so it is isotropic by construction
        # — the first attempt asked it for 900 octaves and got 3 px speckle, which composites as
        # sensor grain, not rain. Falling water is anisotropic: essentially white noise across the
        # wind and almost perfectly correlated along the fall. So the streaks are built as one row
        # of noise smeared down the frame, then sheared so the squall leans.
        rng = np.random.default_rng(619)
        row = rng.random((1, W)).astype(np.float32)
        row = np.asarray(Image.fromarray((row * 255).astype(np.uint8), "L")
                         .filter(ImageFilter.GaussianBlur(1.1)), np.float32) / 255.0
        streak = np.repeat(row, H, axis=0)
        shear = (np.arange(H) * 0.06).astype(int)                 # the lean of the falling water
        idx = np.clip(np.arange(W)[None, :] + shear[:, None], 0, W - 1)
        streak = np.take_along_axis(streak, idx, axis=1)
        # Break the columns up, or it is a comb rather than rain — every streak has to start and
        # stop somewhere. Two things do that: low-frequency noise fading individual streaks in and
        # out, and a cloud base above which there is no fallout at all. The version without the
        # base ran the streaks clean off the top of the frame, which reads as a scratched negative
        # (the whole point of a squall is that you can see where it is coming from).
        streak *= 0.35 + 1.05 * noise((H, W), octaves=(3, 11, 34), seed=631)
        streak *= np.clip((gyw - 0.085) / 0.075, 0, 1)            # the cloud base
        streak = np.asarray(Image.fromarray((np.clip(streak, 0, 1) * 255).astype(np.uint8), "L")
                            .filter(ImageFilter.GaussianBlur(1.8)), np.float32) / 255.0
        veil = np.clip((streak - 0.50) * 3.0, 0, 1) * cell * 0.55

        arrw = np.asarray(scene.convert("RGB"), np.float32)
        rain = np.array([150, 158, 172], np.float32)
        arrw = arrw * (1 - veil[..., None] * 0.50) + rain * (veil[..., None] * 0.50)
        # under the cell the world loses its sun: value down, saturation down, hue toward slate
        k = (cell * 0.78)[..., None]
        grey = arrw.mean(axis=2, keepdims=True)
        arrw = arrw * (1 - k) + (grey * 0.55 + np.array([96, 106, 124], np.float32) * 0.45) * k
        # ...and gains it back immediately to the right, so the plate has a lit gap to read against
        gap = np.exp(-(((gxw - (cxw + cw2 * 1.75)) / (cw2 * 0.85)) ** 2)) * band
        arrw = np.clip(arrw * (1 + 0.13 * gap[..., None]), 0, 255)
        scene = Image.fromarray(arrw.astype(np.uint8)).convert("RGBA")
        LAYERS.append(("74_weather_cell", Image.merge(
            "RGBA", (*Image.new("RGB", (W, H), (120, 130, 148)).split(),
                     Image.fromarray((np.clip(cell * 0.62 + veil, 0, 1) * 255).astype(np.uint8), "L")))))
        print(f"  weather     x~{cxw:.2f}          rain cell over the mid-left plain, "
              f"lit gap to its right (two hours, not one)")

    # ---- 4g · the title's quarter (criticism #8) -------------------------------------------
    # The title used to sit top-right, on the cumulus and the ash plume, surviving on a text-shadow.
    # It moves to the top-left indigo — the calm quarter — and the plate meets it halfway: a very
    # soft darkening exactly where the type lands, so legibility comes from the art rather than from
    # a drop shadow bolted onto the words. Soft-edged and off-centre on purpose; a rectangle of
    # darkening in the sky would be the ruled-bar mistake all over again, in the one place on the
    # plate where there is nothing to hide it behind.
    tgx = np.linspace(0, 1, W, dtype=np.float32)[None, :]
    tgy = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    patch = np.exp(-((((tgx - 0.855) / 0.19) ** 2 + ((tgy - 0.085) / 0.115) ** 2)))
    patch *= 0.68 + 0.55 * noise((H, W), octaves=(2, 4, 9), seed=727)
    arrt = np.asarray(scene.convert("RGB"), np.float32)
    k = np.clip(patch, 0, 1)[..., None] * 0.30
    arrt = arrt * (1 - k) + np.array([26, 30, 46], np.float32) * k
    scene = Image.fromarray(np.clip(arrt, 0, 255).astype(np.uint8)).convert("RGBA")
    print("  title patch top-right       calm quarter deepened so the type needs no drop shadow")

    # ---- 5 · one world, one light — but a light with a DIRECTION -------------------------
    # Harvested components were each lit by their own MJ render, so without this they read as
    # separate photographs no matter how well the seams are hidden. One warm sunset grade plus
    # depth haze ties them together — the same job `70_WORLD_GRADE` does in the PS build.
    #
    # The old grade was a pure vertical ramp, which is not a key light at all: it says "warm at the
    # top, cool at the bottom" everywhere across a 2.3:1 frame, and that is precisely the flatness
    # criticism #9 names. A low sun in the upper right has to fall off ACROSS the plate as well as
    # down it, so the far left is genuinely in the blue end of the evening while the seaward side
    # keeps the amber. That gradient plus the rain cell is what makes it a world with weather in it
    # rather than one evening stamped over everything.
    if not args.no_grade:
        arr = np.asarray(scene.convert("RGB"), np.float32)
        yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        xx = np.linspace(0, 1, W, dtype=np.float32)[None, :, None]
        warm = np.array([1.045, 1.005, 0.945], np.float32)
        cool = np.array([0.945, 0.985, 1.070], np.float32)
        key = np.clip(0.30 + 0.70 * xx, 0, 1) * (1 - yy * 0.72)   # strongest upper right
        arr *= warm * key + cool * (1 - key)
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
