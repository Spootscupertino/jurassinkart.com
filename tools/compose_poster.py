#!/usr/bin/env python3
"""The Living Past — place organisms onto the FULL poster mockup (#21).

`compose_scene.py` targets `_proof_scene.png`, the flat side-on proof plate. The actual poster
(`plates/poster_full.png`) is a different, perspectival cutaway with the furniture already on it
— title band, 4x8 field guide, facts band, timeline. This puts real organisms onto *that*, which
is the only way to judge whether the cast reads at poster scale against the type and the QR cards.

Per-group scale (Eric's rule): each stratum is ruled against its own reference animal, so the
dinosaurs are true to each other and the soil fauna are true to each other. Ratios inside a group
are exact; the group gets one multiplier.

Ground placement is *detected*, not assumed — the plateau edge falls away toward the coast, so a
fixed y would float the right-hand animals in mid-air.

    python3 tools/compose_poster.py CR01:a.png CR03:b.png --out working/poster_cast.png
"""
from __future__ import annotations

import argparse
import pathlib
import sys

from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from compose_organism import ORGS, contact_shadow, isolate, parse_width_m

ROOT = pathlib.Path(__file__).resolve().parent.parent
POSTER = ROOT / "living_past/plates/poster_full.png"

# Reference: the biggest land titan spans this fraction of poster width. Everything else in the
# group derives from it by true-size ratio, so the group stays internally honest.
LAND_REF_FRAC = 0.14
# Where each stratum's cast is laid out, as fractions of poster width.
BAND_X = {"above": (0.10, 0.44), "underground": (0.10, 0.40),
          "shoreline": (0.34, 0.52), "ocean": (0.60, 0.95)}


# The terrace line, eyeball-calibrated on poster_full.png at 3000x2000 (same method as the
# SECTION_ANCHOR fractions). Auto-detection was tried and abandoned: the cut face is heavily
# textured, so the strongest dark step is the *distant horizon*, not the near plateau edge —
# it parked the two titans on the skyline with their heads cropped off the poster.
TERRACE = [(0, 208), (600, 225), (900, 245), (1150, 322), (1400, 395)]
TOP_MARGIN = 22          # keep the tallest animal clear of the poster's top trim


def terrace_y(x: int) -> int:
    """Interpolate the walkable plateau line at this column."""
    pts = TERRACE
    if x <= pts[0][0]:
        return pts[0][1]
    if x >= pts[-1][0]:
        return pts[-1][1]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        if x0 <= x <= x1:
            t = (x - x0) / (x1 - x0)
            return round(y0 + t * (y1 - y0))
    return pts[-1][1]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Place organisms on the full poster mockup")
    ap.add_argument("items", nargs="+", metavar="ID:plate.png")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--ref-frac", type=float, default=LAND_REF_FRAC)
    args = ap.parse_args(argv)

    poster = Image.open(POSTER).convert("RGBA")
    W, H = poster.size

    pairs = []
    for it in args.items:
        oid, _, path = it.partition(":")
        oid = oid.upper()
        if oid not in ORGS:
            print(f"unknown id {oid}", file=sys.stderr)
            return 1
        pairs.append((ORGS[oid], pathlib.Path(path)))

    by_sec: dict[str, list] = {}
    for org, p in pairs:
        by_sec.setdefault(org.get("section", "above"), []).append((org, p))

    for section, group in by_sec.items():
        group.sort(key=lambda gp: -(parse_width_m(gp[0].get("size", "")) or 0))
        lo, hi = BAND_X.get(section, (0.10, 0.44))
        n = len(group)
        isos = [isolate(p) for _, p in group]
        sizes = [parse_width_m(o.get("size", "")) or 1.0 for o, _ in group]
        biggest = max(sizes)

        # Two competing rulers; the group takes whichever is smaller.
        #   width  — the reference animal spans --ref-frac of the poster (drama)
        #   height — the TALLEST animal still clears the terrace headroom (fit)
        # On this poster composition height nearly always wins: the cutaway and ocean take
        # almost the whole canvas and leave the above-ground cast a very shallow strip.
        by_width = (args.ref_frac * W) / biggest
        by_height = min(
            ((terrace_y(int(W * (lo + (hi - lo) * (i + 0.5) / n))) - TOP_MARGIN)
             / (iso.height * sizes[i] / iso.width))
            for i, iso in enumerate(isos))
        px_per_m = min(by_width, by_height)
        ruler = "headroom" if by_height < by_width else "width"
        print(f"[{section}] ruler: {px_per_m:.0f} px/m (biggest = {biggest} m, limited by {ruler})")

        for i, ((org, plate), iso) in enumerate(zip(group, isos)):
            width_m = sizes[i]
            tw = max(4, int(width_m * px_per_m))
            th = max(1, round(iso.height * tw / iso.width))
            fx = lo + (hi - lo) * (i + 0.5) / n
            ax = int(W * fx)
            gy = terrace_y(ax)
            left, top = ax - tw // 2, gy - th

            print(f"   {org['id']} {org.get('commonName'):<20} {width_m:>5} m -> {tw:4}px "
                  f"({100*tw/W:4.1f}% of poster) feet at ({ax},{gy})")
            subj = iso.resize((tw, th), Image.LANCZOS)
            sh = contact_shadow((tw, th))
            poster.alpha_composite(sh, (ax - sh.width // 2, gy - sh.height // 2))
            poster.alpha_composite(subj, (left, top))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    poster.convert("RGB").save(args.out)
    print(f"\nwrote {args.out}  ({W}x{H})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
