#!/usr/bin/env python3
"""The Living Past — 4-zone gradient scaffold ("the void") renderer.

Paints the environment's four zones as flat gradient fields at the locked master
proportions, from template/design_tokens.json. This is the base layer the rich MJ
plates and organisms composite onto (memory: "MJ for texture, PS gradients for the
void"). Output PNG → drop into Photoshop as the bottom of 10_SKY / 30 / 60.

    python3 tools/build_scene_scaffold.py                 # 2000px proof
    python3 tools/build_scene_scaffold.py --master        # full 10800px scene plate
    python3 tools/build_scene_scaffold.py --out foo.png --width 3000
"""
from __future__ import annotations
import argparse, json, pathlib
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOK = json.loads((ROOT / "living_past/template/design_tokens.json").read_text())
C = TOK["color"]

# scene occupies the top 65% of the poster (locked layout). Coastline at 48%.
SCENE_FRAC = TOK["layout"]["rows_pct"]["scene"] / 100.0
COAST = TOK["layout"]["coastline_pct_from_left"] / 100.0
HORIZON = 0.40   # ground/water line as a fraction of scene height (matches the proof plate)


def _hex(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(px, x0, y0, x1, y1, stops):
    """Paint a vertical multi-stop gradient into region [x0,x1)×[y0,y1)."""
    n = len(stops) - 1
    h = max(1, y1 - y0)
    for yy in range(y0, y1):
        f = (yy - y0) / h
        seg = min(int(f * n), n - 1)
        t = f * n - seg
        col = _lerp(stops[seg], stops[seg + 1], t)
        for xx in range(x0, x1):
            px[xx, yy] = col


def build(width: int) -> Image.Image:
    # scene aspect: poster is 3:2 (36:24); scene height = 65% of poster height.
    poster_h = width * 2 / 3
    scene_h = round(poster_h * SCENE_FRAC)
    img = Image.new("RGB", (width, scene_h))
    px = img.load()

    horizon_y = round(scene_h * HORIZON)
    coast_x = round(width * COAST)

    sky = [_hex(s) for s in C["sunset_stops"]]
    land = [_hex(C["strata_grounds"]["above"]), _hex(C["bedrock"])]
    ocean = [_hex("#6f8a84"), _hex("#2f5560"), _hex("#16313d"), _hex(C["abyss"])]

    # 1 SKY — full width, top band down to horizon
    vgrad(px, 0, 0, width, horizon_y, sky)
    # 2 LAND — below horizon, left of coastline
    vgrad(px, 0, horizon_y, coast_x, scene_h, land)
    # 4 OCEAN — below horizon, right of coastline
    vgrad(px, coast_x, horizon_y, width, scene_h, ocean)
    # 3 SHORELINE seam — thin sand sheen at the coastline just below the waterline
    sand = _hex(C["strata_grounds"]["shoreline"])
    seam_w = max(2, width // 300)
    for yy in range(horizon_y, min(scene_h, horizon_y + scene_h // 6)):
        f = 1 - (yy - horizon_y) / (scene_h // 6)
        for dx in range(-seam_w, seam_w):
            xx = coast_x + dx
            if 0 <= xx < width:
                base = px[xx, yy]
                px[xx, yy] = _lerp(base, sand, 0.35 * f)
    return img


def main() -> int:
    ap = argparse.ArgumentParser(description="Living Past 4-zone gradient scaffold")
    ap.add_argument("--master", action="store_true", help="full 10800px master width")
    ap.add_argument("--width", type=int, default=2000, help="output width px (proof)")
    ap.add_argument("--out", type=pathlib.Path, default=ROOT / "living_past/plates/scene_scaffold.png")
    args = ap.parse_args()

    width = TOK["canvas"]["trim_px"][0] if args.master else args.width
    args.out.parent.mkdir(parents=True, exist_ok=True)
    img = build(width)
    img.save(args.out)
    print(f"wrote {args.out} ({img.width}×{img.height}) — sky/land/ocean zones, coast at {int(COAST*100)}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
