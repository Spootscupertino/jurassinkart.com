#!/usr/bin/env python3
"""The Living Past — the strata as an eroded outcrop face, not a bar chart (#24, criticism #1).

Eric, 2026-07-27: *"even diving into the strata layers, blending a couple of each will make it
look more lifelike and non-uniform, which is what soil actually looks like."*

Eric, 2026-07-28 (criticism #1): *"the strata read as flat ruled bars. They're the accuracy moat
and the most obviously generated thing on the plate. Every other edge is noise-warped; these are
still stripes."*

He is right twice. The first pass fixed the *texture* (two or three variants per layer, cross-faded)
and left the *geometry* alone: eleven full-width bands of constant thickness with ±3% wobble on the
contacts. No amount of texture rescues that, because the thing the eye reads as "drawn" is the
parallel-constant-thickness stripe, not the pixels inside it.

So this renderer keeps the accuracy moat exactly where it was — **layer order and relative
thickness still come from `geology_hellcreek.json` and are never invented** — and rebuilds the
geometry as an outcrop:

  1. **Pinch and swell.** Every bed's thickness is a function of x, not a constant. Channel
     sandstones get the strongest swell and a scoured base, because that is literally what a
     channel is: a lens that cut down into the floodplain it sits in. Column totals are
     renormalised, so a bed that swells makes its neighbours thin — compensational stacking, and
     the parallel-stripe read dies with it.
  2. **One shared structural roll.** Real beds are not independently wavy; they roll *together*,
     because they were all folded and tilted by the same thing afterwards. Every contact carries
     the same low-frequency roll plus a regional dip, and only then its own local wander. This is
     the difference between "sedimentary rock" and "stacked ribbons".
  3. **A normal fault.** One clean offset across the whole section, with drag on the beds either
     side of it. Nothing says *geology* like a section that has been broken and moved.
  4. **Differential weathering, lit.** Each lithology gets a `resistance`; that becomes a height
     field, and the height field gets lit from the upper right like the rest of the plate. Hard
     sandstones stand out as ledges with a lit top and a cast shadow under the overhang; the
     bentonite — the softest thing in the section — cuts back into a shadowed notch. In the field
     that notch is how you *find* the ash bed, so the recession is accuracy, not styling.
  5. **Erosion rills.** Vertical run-off streaking down the soft beds, strongest low on the face.
     The one place a vertical line belongs.
  6. **An eroded top.** The ribbon is returned RGBA with the land surface as its own alpha edge,
     so the caller never has to fake a ground contact with a straight ramp.

    python3 tools/render_strata_organic.py --width 3000 --height 440 --out working/strata.png
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import numpy as np
from PIL import Image, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
LP = ROOT / "living_past"
PLATES = LP / "plates"
SPEC = json.loads((LP / "geology_hellcreek.json").read_text())

TEX = {
    "L01": "tex_topsoil", "L02": "tex_mudstone", "L03": "tex_lignite", "L04": "tex_sandstone",
    "L05": "tex_paleosol", "L06": "tex_bentonite", "L07": "tex_mudstone", "L08": "tex_sandstone",
    "U01": None, "L09": "tex_foxhills", "L10": "tex_pierre",
}

# How hard each bed is, 0 (weathers to a slope) .. 1 (stands out as a ledge). This is a real
# property of the lithology, not a look — it is why a Hell Creek badland is a staircase of tan
# sandstone benches separated by grey mudstone slopes, and why the bentonite is always the notch.
RESIST = {
    "L01": 0.14,   # rooted topsoil — slumps
    "L02": 0.22,   # overbank mudstone — slope former
    "L03": 0.34,   # lignite — holds a small dark bench
    "L04": 0.92,   # channel sandstone — the ledge
    "L05": 0.33,   # sandy paleosol
    "L06": 0.04,   # bentonite — popcorn clay, the softest thing in the section
    "L07": 0.20,   # overbank mudstone
    "L08": 0.86,   # channel sandstone — the second ledge
    "U01": 0.55,   # the scour surface itself
    "L09": 0.74,   # Fox Hills sandstone
    "L10": 0.16,   # Pierre shale — fissile, weathers to chips
}

# How much each bed pinches and swells along the face, as a fraction of its own thickness.
# Channels are lenses and get much the most; the marker beds (ash, coal) are ash-falls and peat
# swamps — laterally the most persistent things in the section, so they get the least. That
# ordering is itself accurate and it is what makes the section scan as real.
SWELL = {"L04": 1.15, "L08": 1.05, "L03": 0.30, "L06": 0.22, "U01": 0.35}
SWELL_DEFAULT = 0.60

ROLL = 0.055          # shared low-frequency structural roll, fraction of ribbon height
DIP = 0.045           # regional dip across the full width
WANDER = 0.016        # each contact's own local wander on top of the shared roll
FAULT_X = 0.335       # normal fault, fraction of width
FAULT_THROW = 0.052   # downthrown to the right, fraction of ribbon height
FAULT_DRAG = 0.030    # beds bend into the fault plane over this fraction of width
TOP_EROSION = 0.055   # relief on the land surface at the top of the ribbon

# Gullies. These matter more than anything else in this file for killing the ruled-bar read,
# because they are the only feature that crosses contacts: a run-off gully cuts down through five
# beds at once, and where it does, five horizontal lines stop being horizontal lines. Each entry
# is (x fraction, width fraction, depth as a fraction of ribbon height).
GULLIES = [(0.085, 0.030, 0.72), (0.215, 0.018, 0.44), (0.395, 0.042, 1.00),
           (0.545, 0.022, 0.52), (0.700, 0.036, 0.88), (0.885, 0.024, 0.58)]

# Where a gully is deep enough it stops being shading and becomes a ravine: the rock is gone, the
# alpha goes to zero, and the land behind the section shows through the notch. Two of the six cut
# right through. This is what makes the outcrop a set of spurs instead of one continuous band —
# and a band that is physically interrupted cannot read as a ruled bar.
INCISE_FROM = 0.62    # gully strength at which the cut starts removing rock
INCISE_MAX = 0.78     # deepest cut, as a fraction of the exposed section

TALUS_MAX = 0.42      # how far a soft bed's debris spills down the face, as a fraction of height


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


def _box(a: np.ndarray, r: int, axis: int) -> np.ndarray:
    if r < 1:
        return a
    pad = [(0, 0), (0, 0)]
    pad[axis] = (r, r)
    p = np.pad(a, pad, mode="edge")
    c = np.cumsum(p, axis=axis, dtype=np.float32)
    zero = np.zeros_like(np.take(c, [0], axis=axis))
    c = np.concatenate([zero, c], axis=axis)
    n = a.shape[axis]
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return (hi - lo) / (2 * r + 1)


def fblur(a: np.ndarray, sigma: float) -> np.ndarray:
    """Gaussian blur in float32.

    PIL's GaussianBlur refuses "F" images, and round-tripping through uint8 quantises the height
    field the relief shading differentiates — 1/255 steps in `resist` become visible terracing in
    the lit result. Three separable box passes is a standard gaussian approximation and stays in
    float the whole way.
    """
    r = max(1, int(round(sigma * 1.2)))
    out = a.astype(np.float32)
    for _ in range(3):
        out = _box(_box(out, r, 0), r, 1)
    return out


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


def gully_field(W: int) -> np.ndarray:
    """Per-column erosional recession of the outcrop face, 0 (spur, standing out) .. 1 (gully).

    Two components: a broad low-frequency undulation of the whole face, plus the discrete gullies
    in GULLIES. The result is used three ways — it notches the skyline, it occludes the rock inside
    each re-entrant, and it decides where talus collects — so all three agree with each other
    instead of being three independent noises.
    """
    xs = np.linspace(0.0, 1.0, W, dtype=np.float32)
    base = (smooth_noise((1, W), octaves=(3, 7), seed=1201)[0] - 0.35) * 0.55
    g = np.clip(base, 0, None)
    for cx, cw, depth in GULLIES:
        g = np.maximum(g, depth * np.exp(-(((xs - cx) / max(1e-4, cw)) ** 2)))
    return np.clip(g, 0.0, 1.0).astype(np.float32)


def contacts(layers, W: int, H: int, gully: np.ndarray) -> list[np.ndarray]:
    """Per-column y of every bed contact, top of L01 down to the base of the section.

    Returns `len(layers)+1` arrays of length W. The accuracy moat lives in the *proportions* —
    each bed still occupies its `relThickness` share of the column on average — while the
    geometry is free to pinch, roll, tilt and break.
    """
    # 1 · thickness as a function of x
    th = np.zeros((len(layers), W), np.float32)
    for i, l in enumerate(layers):
        amp = SWELL.get(l["id"], SWELL_DEFAULT)
        n = smooth_noise((1, W), octaves=(2, 4, 9), seed=311 + i * 17)[0]
        th[i] = l["relThickness"] * (1.0 + amp * (n - 0.5) * 2.0)
    th = np.clip(th, 1e-4, None)
    th /= th.sum(axis=0, keepdims=True)          # renormalise: a swell here thins a bed there

    # 2 · the surface the whole section hangs from: eroded top, shared roll, regional dip
    xs = np.linspace(0.0, 1.0, W, dtype=np.float32)
    roll = (smooth_noise((1, W), octaves=(2, 5), seed=7)[0] - 0.5) * 2 * ROLL
    dip = (xs - 0.5) * DIP
    top = TOP_EROSION * 1.3 + (smooth_noise((1, W), octaves=(3, 8, 19), seed=13)[0] - 0.5) * 2 * TOP_EROSION
    top = top + gully * TOP_EROSION * 2.6          # the gullies notch the skyline too

    # 3 · the fault: one clean offset, with the beds dragged into the plane on both sides
    d = (xs - FAULT_X) / max(1e-4, FAULT_DRAG)
    throw = FAULT_THROW / (1.0 + np.exp(-d * 4.0))            # smooth step = the drag zone
    throw = throw.astype(np.float32)

    edges: list[np.ndarray] = []
    acc = np.zeros(W, np.float32)
    usable = 1.0 - top                                        # room left under the land surface
    for i in range(len(layers) + 1):
        y = top + acc * usable + roll + dip + throw
        if i > 0:                                             # interior contacts get local wander
            n = smooth_noise((1, W), octaves=(3, 8, 17), seed=901 + i * 23)[0]
            y = y + (n - 0.5) * 2 * WANDER
        edges.append(np.clip(y, 0.0, 1.4).astype(np.float32) * H)
        if i < len(layers):
            acc = acc + th[i]
    return edges


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Render the strata as an eroded outcrop face")
    ap.add_argument("--width", type=int, default=3000)
    ap.add_argument("--height", type=int, default=440)
    ap.add_argument("--out", type=pathlib.Path, default=ROOT / "working/strata_ribbon.png")
    ap.add_argument("--flat", action="store_true",
                    help="skip the weathering relief (texture + geometry only)")
    args = ap.parse_args(argv)
    W, H = args.width, args.height

    layers = SPEC["layers"]
    canvas = np.zeros((H, W, 3), np.float32)
    gully = gully_field(W)
    edges = contacts(layers, W, H, gully)
    yy = np.arange(H, dtype=np.float32)[:, None]

    resist = np.zeros((H, W), np.float32)
    covered = np.zeros((H, W), np.float32)
    bands: list[np.ndarray] = []

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

        top = edges[i][None, :]
        bot = edges[i + 1][None, :]
        mask = ((yy >= top) & (yy < bot)).astype(np.float32)
        # soften the contact a touch (a hard line only for the unconformity and the channel scours,
        # which really are erosive surfaces and really are sharp)
        soft = 0.8 if (l["id"] == "U01" or "crossbed" in l.get("features", [])) else 2.4
        if soft > 1:
            mask = fblur(mask, soft)
        canvas = canvas * (1 - mask[..., None]) + band * mask[..., None]
        resist = resist * (1 - mask) + RESIST.get(l["id"], 0.4) * mask
        covered = np.maximum(covered, mask)
        bands.append(band)
        rel = l["relThickness"]
        print(f"  {l['id']} {l['name'][:26]:<26} {src:<6} rel={rel:.3f} "
              f"resist={RESIST.get(l['id'], 0.4):.2f} swell={SWELL.get(l['id'], SWELL_DEFAULT):.2f}")

    if not args.flat:
        # ---- talus: the debris that breaks every contact -------------------------------------
        # This is the single most important pass in the file. A soft bed does not sit in an outcrop
        # with a clean line under it — it sheds, continuously, and its own debris drapes down over
        # everything below. Where the drape lands, the contact underneath simply is not visible,
        # and a horizontal line that is interrupted in six places over three metres stops reading
        # as a ruled line at all. The colour comes from the shedding bed's own texture (desaturated
        # and darkened, because scree is shadowed, broken and damp), so the debris is provably the
        # bed above it rather than a generic grey wash.
        depth_f = np.linspace(0.0, 1.0, H, dtype=np.float32)[:, None]
        for i, l in enumerate(layers):
            r = RESIST.get(l["id"], 0.4)
            if r > 0.42 or l["relThickness"] < 0.03:
                continue
            base = edges[i + 1][None, :]
            reach = H * TALUS_MAX * (1.0 - r) * (0.45 + 0.55 * l["relThickness"] / 0.18)
            # gullies funnel debris: the spill runs furthest where the face is cut back
            reach = reach * (0.55 + 0.9 * gully[None, :])
            t = (yy - base) / np.maximum(reach, 1.0)
            a = np.clip(1.0 - t, 0, 1) ** 1.5 * (t >= 0)
            # patchy, not a curtain — lobes and fans with bare rock between them
            lob = smooth_noise((H, W), octaves=(3, 9, 24), seed=1500 + i * 31)
            a = a * np.clip((lob - 0.40) * 3.0, 0, 1)
            a = fblur(a, max(1.5, H * 0.006))
            scree = np.clip(bands[i] * 0.80 + 10.0, 0, 255)
            grey = scree.mean(axis=2, keepdims=True)
            scree = scree * 0.74 + grey * 0.26                # weathered debris loses its colour
            canvas = canvas * (1 - a[..., None]) + scree * a[..., None]
            resist = resist * (1 - a) + 0.30 * a              # talus is soft, and shades like it

        # ---- differential weathering, lit ----------------------------------------------------
        # `resist` is a height field: hard beds stand proud, soft beds are cut back. Light it from
        # the upper right like the rest of the plate and the bar chart becomes a cliff — the
        # vertical gradient puts a lit lip on the top of every ledge and a cast shadow in the
        # overhang beneath it. Restrained on purpose: the first attempt used a gain of 26 and every
        # sandstone came out looking like chrome pipe, because a gradient that strong draws a hard
        # bright line on BOTH contacts of the bed and the eye reads a highlighted bar — the exact
        # failure this whole file exists to remove.
        h = fblur(resist, max(2.0, H * 0.016))
        shade = 1.0 + 7.5 * np.gradient(h, axis=0) + 2.5 * np.gradient(h, axis=1)
        shade *= 0.86 + 0.18 * h                              # soft beds sit back in their shade
        shade *= 1.0 - 0.30 * np.clip(fblur(h, max(5.0, H * 0.07)) - h, 0, 1)   # overhang AO

        # ---- the gullies, occluded ------------------------------------------------------------
        # Inside a re-entrant you are looking at rock that is further away and lit by sky only, so
        # it goes darker and cooler; the spurs between keep the warm key. This is what gives the
        # face its third dimension — without it the gullies are only a wiggle in the skyline.
        g2 = fblur(np.repeat(gully[None, :], H, axis=0), max(2.0, W * 0.002))
        shade *= 1.0 - 0.46 * g2 * (0.50 + 0.50 * depth_f)
        shade = np.clip(shade, 0.22, 1.55)

        # ---- erosion rills -------------------------------------------------------------------
        # Run-off streaking down the face, strongest on the soft beds and low on the outcrop where
        # the wash has had longest to work. The only vertical lines that belong here.
        rill = np.repeat(smooth_noise((1, W), octaves=(9, 26, 70), seed=421)[0][None, :], H, axis=0)
        shade *= 1.0 - 0.24 * np.clip((rill - 0.5) * 2.0, 0, 1) * (1.0 - h) * (0.35 + 0.65 * depth_f)

        canvas = np.clip(canvas * shade[..., None], 0, 255)
        # cool the shadowed rock rather than only darkening it — skylight is blue, and a face that
        # only loses value reads as a print problem while one that also shifts hue reads as depth
        cool = np.clip((1.0 - shade) * 0.9, 0, 1)[..., None]
        canvas = np.clip(canvas * (1 - cool * 0.22) +
                         np.array([44, 52, 66], np.float32) * cool * 0.22, 0, 255)
        soft_ids = [l["id"] for l in layers if RESIST.get(l["id"], 0.4) <= 0.42
                    and l["relThickness"] >= 0.03]
        print(f"  talus     {len(soft_ids)} shedding beds ({', '.join(soft_ids)}) drape over the contacts below")
        print(f"  gullies   {len(GULLIES)} re-entrants cut across every bed — the only feature that "
              f"crosses contacts")
        print(f"  relief    ledges {', '.join(k for k, v in RESIST.items() if v > 0.7)}; "
              f"notch {min(RESIST, key=RESIST.get)} (bentonite — how you find the ash bed in the field)")

    # ---- alpha: the eroded land surface, and the ravines that cut through it -----------------
    # Returned as the ribbon's own alpha so the caller never has to invent a ground contact with a
    # straight ramp. Above the top contact there is simply no rock — and where a gully is deep
    # enough, there is no rock well below it either: the section is cut into separate spurs and the
    # world behind shows through the notches. A band with real holes in it cannot read as a bar.
    alpha = np.clip(covered, 0, 1)
    incise = np.clip((gully - INCISE_FROM) / max(1e-4, 1.0 - INCISE_FROM), 0, 1) ** 0.8
    if incise.max() > 0:
        cut_to = edges[0] + incise * INCISE_MAX * np.maximum(H - edges[0], 1.0)
        # ragged, not a clean bite: the floor of a ravine wanders
        cut_to = cut_to + (smooth_noise((1, W), octaves=(5, 14, 33), seed=1777)[0] - 0.5) * H * 0.06
        alpha *= np.clip((yy - cut_to[None, :]) / max(2.0, H * 0.04), 0, 1)
        print(f"  ravines   {int((incise > 0.15).sum() / W * 100)}% of the face cut clean through — "
              f"the section is spurs, not a band")
    alpha = fblur(alpha, 1.2)
    out = np.dstack([np.clip(canvas, 0, 255), np.clip(alpha, 0, 1) * 255]).astype(np.uint8)
    Image.fromarray(out, "RGBA").save(args.out)
    print(f"\nwrote {args.out}  ({W}x{H}, RGBA)  — {len(layers)} layers, pinch/swell, "
          f"shared roll {ROLL}, dip {DIP}, one normal fault at x={FAULT_X}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
