#!/usr/bin/env python3
"""The Living Past — place SEVERAL organisms on the scene at once (#20).

`compose_organism.py` always rebuilds from the empty base plate, so it can only ever show one
organism. This composites a whole cast in one pass, which is the only way to actually see
whether a stratum's roster fits.

**Per-group scale (Eric's rule, 2026-07-27).** There is no single world ruler. Each stratum is
scaled against its *own* reference animal, so the dinosaurs are true to each other and the soil
fauna are true to each other — a millipede sized against a beetle, not against a T. rex. That is
what makes an ant and a tyrannosaur legible on one sheet. Within a group, every true-size ratio
is preserved exactly; the group as a whole gets one multiplier chosen so the cast fits its band.
The poster states each band's ruler separately (Law #2).

    python3 tools/compose_scene.py CR01:working/a.png CR03:working/b.png --out working/scene.png
    python3 tools/compose_scene.py ... --group-fit      # auto-derive the group multiplier
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from compose_organism import (ORGS, PROOF_W, SCENE_PROOF, SECTION_ANCHOR, ID_ANCHOR,
                              contact_shadow, isolate, parse_width_m, px_per_m)

# Where each stratum's cast is allowed to live, as fractions of scene width.
# coastline sits at 48% from the left (design_tokens layout.coastline_pct_from_left).
BAND_X = {"above": (0.04, 0.46), "underground": (0.04, 0.46),
          "shoreline": (0.30, 0.60), "ocean": (0.52, 0.97)}
OVERLAP_ALLOWANCE = 1.30   # a cast may exceed its band by 30% — animals occlude naturally


def group_multiplier(orgs: list[dict], section: str, scene_w: int) -> float:
    """One multiplier for the whole group, so every in-group size ratio is preserved."""
    lo, hi = BAND_X[section]
    band_px = (hi - lo) * scene_w
    total = sum((parse_width_m(o.get("size", "")) or 0) * px_per_m(False) for o in orgs)
    if total <= 0:
        return 1.0
    return min(1.0, band_px * OVERLAP_ALLOWANCE / total)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Place several organisms on the proof scene")
    ap.add_argument("items", nargs="+", metavar="ID:plate.png")
    ap.add_argument("--out", type=pathlib.Path, required=True)
    ap.add_argument("--group-fit", action="store_true",
                    help="auto-scale each stratum group so its cast fits its band")
    ap.add_argument("--spread", action="store_true", default=True,
                    help="lay the group out across its band instead of stacking on one anchor")
    args = ap.parse_args(argv)

    pairs = []
    for it in args.items:
        oid, _, path = it.partition(":")
        oid = oid.upper()
        if oid not in ORGS:
            print(f"unknown id {oid}", file=sys.stderr)
            return 1
        pairs.append((ORGS[oid], pathlib.Path(path)))

    scene = Image.open(SCENE_PROOF).convert("RGBA")
    scene_w, scene_h = scene.size

    # group by stratum so each gets its own ruler
    by_sec: dict[str, list] = {}
    for org, p in pairs:
        by_sec.setdefault(org.get("section", "above"), []).append((org, p))

    for section, group in by_sec.items():
        mult = group_multiplier([o for o, _ in group], section, scene_w) if args.group_fit else 1.0
        print(f"[{section}] {len(group)} organisms · group scale x{mult:.2f}")
        # sort biggest-first so titans sit behind and small animals read in front
        group.sort(key=lambda gp: -(parse_width_m(gp[0].get("size", "")) or 0))
        lo, hi = BAND_X[section]
        n = len(group)
        for i, (org, plate) in enumerate(group):
            iso = isolate(plate)
            width_m = parse_width_m(org.get("size", "")) or 1.0
            tw = max(2, int(width_m * px_per_m(False) * mult))
            th = max(1, round(iso.height * tw / iso.width))

            a = {**SECTION_ANCHOR[section], **ID_ANCHOR.get(org["id"], {})}
            if args.spread and n > 1:
                fx = lo + (hi - lo) * (i + 0.5) / n
            else:
                fx = a["x"]
            ax, ay = int(scene_w * fx), int(scene_h * a["y"])
            left = ax - tw // 2
            top = ay - (th if a["anchor"] == "feet" else th // 2)

            print(f"   {org['id']} {org.get('commonName'):<22} {width_m:>5} m -> {tw:4}px "
                  f"({100*tw/scene_w:4.1f}% of width) at x={fx:.2f}")
            subj = iso.resize((tw, th), Image.LANCZOS)
            if a.get("shadow"):
                sh = contact_shadow((tw, th))
                scene.alpha_composite(sh, (ax - sh.width // 2, (top + th) - sh.height // 2))
            scene.alpha_composite(subj, (left, top))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    scene.convert("RGB").save(args.out)
    print(f"\nwrote {args.out}  ({scene_w}x{scene_h})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
