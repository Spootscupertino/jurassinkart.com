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
import pathlib
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from compose_organism import ORGS, isolate, parse_width_m

ROOT = pathlib.Path(__file__).resolve().parent.parent
BACKDROP = ROOT / "living_past/plates/backdrop_v4.png"

# plane -> (scale multiplier, ground y as fraction of canvas height)
# Ground lines eyeball-tuned on backdrop_v3: the foreground promontory, the open plain behind it,
# and the far plain by the treeline. Re-checked against backdrop_v4 (which drops the horizon and
# raises the waterline) and they still land on ground — but they WILL need a proper re-tune once
# the six micro-habitat plates land and the front band stops being two fallback hollows.
PLANES = {
    "fg":  (1.00, 0.640),
    "mid": (0.55, 0.505),
    "far": (0.30, 0.452),
}
# the reference animal spans this fraction of canvas width on the FOREGROUND plane
REF_FRAC = 0.20
REF_M = 13.0          # T. rex, the volume's land titan


def contact_shadow(size, strength=150):
    w, h = size
    sh = Image.new("L", (w, max(6, h // 7)), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(sh).ellipse((0, 0, w, sh.height), fill=strength)
    return sh.filter(ImageFilter.GaussianBlur(max(4, sh.height // 3)))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Place organisms on the assembled backdrop")
    ap.add_argument("items", nargs="+", metavar="ID:plane:plate.png")
    ap.add_argument("--out", type=pathlib.Path, default=ROOT / "working/backdrop_cast.png")
    ap.add_argument("--backdrop", type=pathlib.Path, default=BACKDROP,
                    help="plate to stand the cast on (defaults to the last locked backdrop)")
    args = ap.parse_args(argv)

    scene = Image.open(args.backdrop).convert("RGBA")
    W, H = scene.size
    px_per_m = (REF_FRAC * W) / REF_M

    placed = []
    for it in args.items:
        oid, plane, path = it.split(":", 2)
        oid = oid.upper()
        if oid not in ORGS:
            print(f"unknown id {oid}", file=sys.stderr)
            return 1
        if plane not in PLANES:
            print(f"unknown plane {plane}", file=sys.stderr)
            return 1
        placed.append((ORGS[oid], plane, pathlib.Path(path)))

    # far planes first so nearer animals occlude them
    placed.sort(key=lambda t: -PLANES[t[1]][0])
    xs = {"far": 0.30, "mid": 0.30, "fg": 0.30}
    for org, plane, path in placed:
        mul, gy = PLANES[plane]
        iso = isolate(path)
        width_m = parse_width_m(org.get("size", "")) or 1.0
        tw = max(4, round(width_m * px_per_m * mul))
        th = max(1, round(iso.height * tw / iso.width))
        fx = xs[plane]
        xs[plane] += tw / W * 1.15
        ax, ay = round(W * fx), round(H * gy)
        subj = iso.resize((tw, th), Image.LANCZOS)

        # atmospheric perspective: the further back, the more the animal takes on the haze
        if mul < 1.0:
            a = np.asarray(subj.convert("RGBA"), np.float32)
            haze = (1.0 - mul) * 0.42
            a[..., :3] = a[..., :3] * (1 - haze) + np.array([228, 205, 176], np.float32) * haze
            subj = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")

        sh = contact_shadow((tw, th), strength=int(150 * mul))
        shadow = Image.new("RGBA", sh.size, (12, 10, 8, 0))
        shadow.putalpha(sh)
        scene.alpha_composite(shadow, (ax - tw // 2, ay - sh.height // 2))
        scene.alpha_composite(subj, (ax - tw // 2, ay - th))
        print(f"  {org['id']} {org.get('commonName'):<20} {plane:<4} x{mul:.2f}  "
              f"{width_m:>5} m -> {tw:4}px ({100*tw/W:4.1f}% of width)")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    scene.convert("RGB").save(args.out)
    print(f"\nwrote {args.out}  ({W}x{H})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
