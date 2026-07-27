#!/usr/bin/env python3
"""The Living Past — full poster rough draft (#26).

Drops the assembled backdrop (with cast) into the poster's furniture: title band, the 4x8 QR
field guide, the facts band and the deep-time timeline. Those are all already rendered in
`plates/poster_full.png`, whose scene region ends at y=1298 of 2000 (found by row variance — the
furniture band is flat and dark, the scene is not).

The title is lighten-blended back over the new sky rather than re-typeset: it is bright ivory on
a darker sky, so `max` transfers the letterforms and leaves the sky behind them alone.

    python3 tools/build_poster_draft.py --scene working/backdrop_cast.png --out working/poster_draft.png
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
POSTER = ROOT / "living_past/plates/poster_full.png"
SCENE_BOTTOM = 1298          # furniture starts here, on the 3000x2000 poster
TITLE_BOX = (2150, 20, 3000, 200)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Assemble the full poster rough draft")
    ap.add_argument("--scene", type=pathlib.Path, default=ROOT / "working/backdrop_cast.png")
    ap.add_argument("--out", type=pathlib.Path, default=ROOT / "working/poster_draft.png")
    args = ap.parse_args(argv)

    base = Image.open(POSTER).convert("RGB")
    W, H = base.size
    out = base.copy()

    scene = Image.open(args.scene).convert("RGB")
    s = max(W / scene.width, SCENE_BOTTOM / scene.height)
    scene = scene.resize((round(scene.width * s), round(scene.height * s)), Image.LANCZOS)
    scene = scene.crop((0, 0, W, SCENE_BOTTOM))
    out.paste(scene, (0, 0))
    print(f"  scene       0-{SCENE_BOTTOM}      new backdrop + cast")

    # title back over the new sky
    # Only the bright letterforms transfer. A plain max() over the whole box also carried the
    # old sky strip behind the type, which showed as a pale rectangle in the new sky.
    tb = np.asarray(base.crop(TITLE_BOX), np.float32)
    cur = np.asarray(out.crop(TITLE_BOX), np.float32)
    ink = np.clip((tb.mean(axis=2) - 150.0) / 70.0, 0, 1)[..., None]
    merged = cur * (1 - ink) + np.maximum(cur, tb) * ink
    out.paste(Image.fromarray(np.clip(merged, 0, 255).astype(np.uint8)), TITLE_BOX[:2])
    print("  title       top right       lighten-blended back over the new sky")
    print(f"  furniture   {SCENE_BOTTOM}-{H}   4x8 QR field guide + facts band + timeline (from poster_full)")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.save(args.out)
    print(f"\nwrote {args.out}  ({W}x{H})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
