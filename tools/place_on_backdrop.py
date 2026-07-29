#!/usr/bin/env python3
"""The Living Past — place organisms onto the assembled backdrop (#25).

Implements STAGING.md rule 2 (depth planes) against `backdrop_v3.png`. Each organism is assigned
a plane; the plane's multiplier is *distance*, so true-size ratios stay exact within a plane and
the whole cast fits without faking any sizes.

    python3 tools/place_on_backdrop.py CR01:fg:working/mj_pull/CR01_trex.png \\
                                       CR03:mid:working/mj_pull/CR03_edmonto.png \\
                                       --out working/backdrop_cast.png
"""
from __future__ import annotations

import argparse
import math
import pathlib
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from compose_organism import ORGS, isolate, parse_width_m

ROOT = pathlib.Path(__file__).resolve().parent.parent
BACKDROP = ROOT / "living_past/plates/backdrop_v8.png"

# plane -> (scale multiplier, y as fraction of canvas height, anchor)
#
# The multiplier is *distance*, so true-size ratios stay exact within a plane and the whole cast
# fits without faking any sizes. `anchor` says what that y means: "ground" puts the animal's feet
# on it (it is standing on something), "centre" puts its middle there (it is swimming, flying or
# sectioned into the soil, and has no ground line).
#
# The three land planes were eyeball-tuned on backdrop_v3 and re-checked on v5. The other six are
# new, because criticism #3's fix needs somewhere for the other 23 organisms to actually be: an
# ocean animal has no ground plane, and a 1 cm ant has no legible size on any of them.
PLANES = {
    # land
    "fg":    (1.00, 0.640, "ground"),
    "mid":   (0.55, 0.505, "ground"),
    "far":   (0.30, 0.452, "ground"),
    # `rise` — the central rocky bluff, measured at y 0.435 (tools measured the terrain crest, it was
    # not eyeballed). Eric, 2026-07-29: "the t rex should be in the center on the high point there."
    #
    # It needs its own plane because ELEVATION DECOUPLES SCREEN-Y FROM DISTANCE, which is the one
    # assumption the other land planes are built on. On flat ground a higher y means nearer, so the
    # multiplier can be read straight off the ground line — that is why `far` at 0.452 is 0.30. But an
    # animal standing on top of a raised feature is high in frame because the GROUND is high there,
    # not because it is far away. Forcing the bluff onto the flat-ground curve would have made a 13 m
    # titan 180 px, and the reason would have been a coordinate system, not a fact about the world.
    "rise":  (0.95, 0.435, "ground"),
    # air — criticism #6. Quetzalcoatlus was always on the roster; it just had nowhere to be.
    "air":   (0.42, 0.232, "centre"),
    # water, three depths. `deep` is where the Mosasaurus hangs, over the void.
    "shore": (0.72, 0.338, "ground"),
    "shelf": (0.60, 0.300, "centre"),
    "deep":  (0.88, 0.615, "centre"),
    "abyss": (0.52, 0.815, "centre"),
    # the soil ribbon, and the macro band in front of it
    "soil":  (1.00, 0.925, "centre"),
    # Law #2 made literal: magnification changes here. A 1 cm ant is 3 px at the scene's scale and
    # invisible; inside the macro window it is drawn at ~40x, which is exactly what the window is
    # for and what the ruled brass frame is announcing. This is the one multiplier in the file that
    # is NOT distance, and it is only honest because the poster says so.
    "macro": (34.0, 0.760, "centre"),
}
MACRO_PLANES = {"macro"}
# the reference animal spans this fraction of canvas width on the FOREGROUND plane
REF_FRAC = 0.20
REF_M = 13.0          # T. rex, the volume's land titan

# Where the sea surface sits, and how much of a submerged animal the water takes. SEA_SURFACE is
# measured, not chosen: the land horizon and the waterline both fall at y 0.30 on backdrop_v8.
# WATER_TINT matches build_backdrop.py exactly — one ocean, one colour.
SEA_SURFACE = 0.30
WATER_TINT = np.array([26, 74, 84], np.float32)
WET_MIN, WET_MAX = 0.12, 0.42


def contact_shadow(size, strength=150):
    w, h = size
    sh = Image.new("L", (w, max(6, h // 7)), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(sh).ellipse((0, 0, w, sh.height), fill=strength)
    return sh.filter(ImageFilter.GaussianBlur(max(4, sh.height // 3)))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Place organisms on the assembled backdrop, at the staging in volume_v.json")
    ap.add_argument("items", nargs="+", metavar="ID[:plane]:plate.png")
    ap.add_argument("--out", type=pathlib.Path, default=ROOT / "working/backdrop_cast.png")
    ap.add_argument("--backdrop", type=pathlib.Path, default=BACKDROP,
                    help="plate to stand the cast on (defaults to the last locked backdrop)")
    args = ap.parse_args(argv)

    scene = Image.open(args.backdrop).convert("RGBA")
    W, H = scene.size
    px_per_m = (REF_FRAC * W) / REF_M

    placed = []
    for it in args.items:
        parts = it.split(":")
        oid = parts[0].upper()
        if oid not in ORGS:
            print(f"unknown id {oid}", file=sys.stderr)
            return 1
        org = ORGS[oid]
        stage = org.get("stage") or {}
        # `ID:plate.png` takes the staging from the roster; `ID:plane:plate.png` still overrides it,
        # so trying a different plane is a one-liner and *keeping* it is an edit to volume_v.json.
        # That asymmetry is deliberate: the composition should only change where it is reviewable.
        if len(parts) == 2:
            plane, path = stage.get("plane"), parts[1]
        else:
            plane, path = parts[1], ":".join(parts[2:])
        if plane not in PLANES:
            print(f"unknown or unstaged plane {plane!r} for {oid}", file=sys.stderr)
            return 1
        if "x" not in stage:
            print(f"{oid} has no stage.x in volume_v.json", file=sys.stderr)
            return 1
        placed.append((org, plane, float(stage["x"]), pathlib.Path(path)))

    # far planes first so nearer animals occlude them
    placed.sort(key=lambda t: -PLANES[t[1]][0])
    for org, plane, fx, path in placed:
        mul, gy, anchor = PLANES[plane]
        iso = isolate(path)
        width_m = parse_width_m(org.get("size", "")) or 1.0
        tw = max(4, round(width_m * px_per_m * mul))
        th = max(1, round(iso.height * tw / iso.width))
        ax, ay = round(W * fx), round(H * gy)
        subj = iso.resize((tw, th), Image.LANCZOS)

        # Atmospheric perspective: the further back, the more the animal takes on the haze. Which
        # haze depends on what it is standing in — warm evening air on the land side, blue-green
        # absorption in the water. An underwater animal given the sunset haze reads as cut out and
        # pasted over the sea rather than as being in it, which is exactly the tell the whole
        # compositing method exists to avoid.
        wet = plane in ("shelf", "deep", "abyss")
        if wet:
            # Eric, 2026-07-29: "the mosasaur should be deeper in the water, make it look a little
            # more blended into the water as well." Those are one fix, not two, and the old code could
            # not do either: it derived the water blend from the PLANE MULTIPLIER, so `deep` at ×0.88
            # got 7% absorption and a 17 m animal hanging over the abyss was crisper than the water
            # around it. Distance across the frame is not what dims a submerged animal — DEPTH is.
            #
            # So it is read off the ground line instead, on the same exponential extinction curve
            # build_backdrop.py grades the water column with. The two now agree by construction: an
            # animal at a given depth takes exactly the absorption the water at that depth carries,
            # which is the only way a composited organism and a graded column can look like one scene.
            lt = min(max((gy - SEA_SURFACE) / (1.0 - SEA_SURFACE), 0.0), 1.0)
            k = (1.0 - math.exp(-3.1 * lt)) / (1.0 - math.exp(-3.1))
            absorb = WET_MIN + (WET_MAX - WET_MIN) * k
            a = np.asarray(subj.convert("RGBA"), np.float32)
            a[..., :3] = a[..., :3] * (1 - absorb) + WATER_TINT * absorb
            a[..., :3] *= 1.0 - 0.30 * k          # and light dies going down, so it darkens too
            subj = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
            print(f"       water: depth {lt:.2f} of column -> absorb {absorb:.2f}, dim {0.30*k:.2f}")
        elif mul < 1.0:
            a = np.asarray(subj.convert("RGBA"), np.float32)
            haze = (1.0 - mul) * 0.42
            tint = np.array([228, 205, 176], np.float32)
            a[..., :3] = a[..., :3] * (1 - haze) + tint * haze
            subj = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")

        # A contact shadow is a claim that the animal is standing on something. Swimming, flying and
        # sectioned-into-the-soil animals are not, and pasting an ellipse under a Mosasaurus is how
        # a composite starts looking like a collage.
        if anchor == "ground":
            sh = contact_shadow((tw, th), strength=int(150 * min(mul, 1.0)))
            shadow = Image.new("RGBA", sh.size, (12, 10, 8, 0))
            shadow.putalpha(sh)
            scene.alpha_composite(shadow, (ax - tw // 2, ay - sh.height // 2))
            top = ay - th
        else:
            top = ay - th // 2
        scene.alpha_composite(subj, (ax - tw // 2, top))
        note = "  LAW #2 magnified" if plane in MACRO_PLANES else ""
        print(f"  {org['id']} {org.get('commonName'):<20} {plane:<5} x{fx:.3f} ×{mul:<5.2f} "
              f"{width_m:>5} m -> {tw:4}px ({100*tw/W:4.1f}% of width){note}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    scene.convert("RGB").save(args.out)
    print(f"\nwrote {args.out}  ({W}x{H})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
