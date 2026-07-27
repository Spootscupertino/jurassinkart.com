#!/usr/bin/env python3
"""The Living Past — drop an MJ isolate, get it placed on the scene (#1, #3).

The payoff step: take a single upscaled Midjourney isolate (the `lp_organism_prompt.py`
recipe — subject on a "solid flat mid-grey background"), and:

  1. KNOCK OUT the background  — reuse the PNG's own alpha if it has one, else flood-fill
     the connected mid-grey from the four corners → transparent, then trim to content.
  2. SIZE to true scale        — width from the organism's `size` in volume_v.json via the
     same px_per_m as scale_calc (270 on master, 45 on the 1800px proof).
  3. PLACE at its zone anchor   — feet on the terrace (land), or floating in the abyss
     (ocean) — with a soft contact shadow so it sits in the world, not on top of it.

This is a PROOF composite (fast PIL, eyeball-tunable), the same class as compose_proof.py;
the finished art is still assembled in Photoshop. But it lets us see any organism on the
stage the instant its plate lands, and it locks the isolate→place recipe for all 32.

    # place the T. rex from a dropped plate onto the proof scene
    python3 tools/compose_organism.py CR01 --plate working/trex_upscaled.png

    # nudge / rescale without regenerating, then re-place
    python3 tools/compose_organism.py CR01 --plate working/trex.png --dx -40 --scale 1.08

    # just knock out + save the isolate (no placement), e.g. to hand to Photoshop
    python3 tools/compose_organism.py CR01 --plate working/trex.png --isolate-only

    # print the placement plan without writing anything
    python3 tools/compose_organism.py CR01 --plate working/trex.png --dry-run
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = pathlib.Path(__file__).resolve().parent.parent
LP = ROOT / "living_past"
PLATES = LP / "plates"
ORGANISMS = PLATES / "organisms"
TOK = json.loads((LP / "template/design_tokens.json").read_text())
VOL = json.loads((LP / "volume_v.json").read_text())
ORGS = {o["id"]: o for o in VOL["organisms"]}

# Proof scene geometry (matches compose_proof.py: base_plate_v2, WATER 0.50, COAST 0.62).
PROOF_W = 1800
PROOF_H = round(PROOF_W * 2 / 3)                       # 1200 (3:2)
MASTER_W = TOK["canvas"]["trim_px"][0]                 # 10800
PX_PER_M_MASTER = TOK["scale"]["px_per_m"]             # 270
SCENE_PROOF = PLATES / "_proof_scene.png"

# Placement anchors, eyeball-tuned on _proof_scene.png as FRACTIONS of scene W/H.
#   x, y   = where the subject's anchor point lands
#   anchor = which point of the subject box that is ("feet" = bottom-centre, "mid" = centre)
# Per-section defaults; per-id entries override. Nudge live with --dx/--dy/--scale.
SECTION_ANCHOR = {
    "above":       {"x": 0.22, "y": 0.44, "anchor": "feet", "shadow": True},
    "shoreline":   {"x": 0.40, "y": 0.49, "anchor": "feet", "shadow": True},
    "underground": {"x": 0.16, "y": 0.60, "anchor": "mid",  "shadow": False},
    "ocean":       {"x": 0.74, "y": 0.66, "anchor": "mid",  "shadow": False},
}
ID_ANCHOR = {
    # T. rex: standing on the flat terrace near the cliff edge, facing the sea.
    "CR01": {"x": 0.22, "y": 0.45, "anchor": "feet", "shadow": True},
    # Mosasaurus: rising out of the black abyss, lower-right.
    "CR25": {"x": 0.76, "y": 0.64, "anchor": "mid",  "shadow": False},
}

GREY_TOLERANCE = 78   # MJ backdrops are gradients AND often carry a faint floor plane
EDGE_FEATHER = 1.2    # px of alpha blur to de-jag the knockout edge


def px_per_m(master: bool) -> float:
    return PX_PER_M_MASTER if master else PX_PER_M_MASTER * PROOF_W / MASTER_W  # 270 or 45


def parse_width_m(size: str) -> float | None:
    """Representative width in metres = MAX of any range (full adult size)."""
    import re
    s = size.strip().lower().replace("–", "-").replace("—", "-")
    unit = next((u for u in ("cm", "mm", "km", "m")
                 if re.search(rf"\d\s*{u}\b|\d{u}\b|\b{u}\b", s)), None)
    if unit is None:
        return None
    seg = s.split(unit)[0]
    nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", seg)]
    if not nums:
        return None
    to_m = {"m": 1.0, "cm": 0.01, "mm": 0.001, "km": 1000.0}[unit]
    return max(nums) * to_m


def has_real_alpha(im: Image.Image) -> bool:
    """True if the PNG already carries a meaningful transparency channel."""
    if im.mode != "RGBA":
        return False
    a = im.getchannel("A")
    lo, hi = a.getextrema()
    return lo < 245  # some genuinely transparent pixels exist


def knockout_grey(im: Image.Image, tolerance: int = GREY_TOLERANCE) -> Image.Image:
    """Remove the connected background by flood-filling inward from the whole border.

    The MJ isolate recipe asks for a flat mid-grey field touching every edge, so the
    background is one connected region reachable from outside — flood-fill it, mark filled
    pixels transparent, feather the edge. Any grey *inside* the animal is untouched because
    it isn't connected to the border.

    Four corner seeds are not enough in practice. MJ ignores "no ground" often enough that
    plates come back with a faint floor plane under the feet, and that floor is a different
    grey from the upper field — unreachable from the top corners and a different seed colour
    from the bottom ones. It survives the fill and composites as a visible rectangular slab.
    Seeding densely along all four edges catches each distinct band."""
    rgb = im.convert("RGB")
    w, h = rgb.size
    # Sentinel colour unlikely to occur in the plate; fill matched bg with it.
    SENT = (0, 255, 1)
    step = max(8, min(w, h) // 24)
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    seeds += [(x, 0) for x in range(0, w, step)] + [(x, h - 1) for x in range(0, w, step)]
    seeds += [(0, y) for y in range(0, h, step)] + [(w - 1, y) for y in range(0, h, step)]
    for seed in seeds:
        if rgb.getpixel(seed) == SENT:
            continue                      # already cleared by an earlier fill
        ImageDraw.floodfill(rgb, seed, SENT, thresh=tolerance)
    px = rgb.load()
    alpha = Image.new("L", (w, h), 255)
    ap = alpha.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == SENT:
                ap[x, y] = 0
    if EDGE_FEATHER:
        alpha = alpha.filter(ImageFilter.GaussianBlur(EDGE_FEATHER))
    out = im.convert("RGBA")
    out.putalpha(alpha)
    return out


def trim(im: Image.Image) -> Image.Image:
    bbox = im.getchannel("A").getbbox()
    return im.crop(bbox) if bbox else im


def contact_shadow(size: tuple[int, int]) -> Image.Image:
    """Soft dark ellipse to seat the subject on the ground."""
    w, h = size
    sw, sh = int(w * 0.92), max(6, int(h * 0.12))
    sh_img = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(sh_img)
    d.ellipse((0, 0, sw, sh), fill=(0, 0, 0, 120))
    return sh_img.filter(ImageFilter.GaussianBlur(max(2, sh // 3)))


def isolate(plate_path: pathlib.Path) -> Image.Image:
    im = Image.open(plate_path)
    if has_real_alpha(im):
        iso = trim(im.convert("RGBA"))
        how = "existing alpha"
    else:
        iso = trim(knockout_grey(im))
        how = "grey flood-fill knockout"
    print(f"  isolate: {how} → {iso.width}x{iso.height} (trimmed to content)")
    return iso


def place(org: dict, iso: Image.Image, *, master: bool,
          dx: int, dy: int, scale_mul: float, dry: bool) -> Image.Image | None:
    oid = org["id"]
    width_m = parse_width_m(org.get("size", ""))
    scene_w = MASTER_W if master else PROOF_W
    scene_h = round(scene_w * 2 / 3)

    if width_m is None:
        target_w = int(iso.width)   # unparseable size — keep native, place by hand
        print(f"  size: '{org.get('size')}' unparseable → native width, tune by hand")
    else:
        target_w = int(width_m * px_per_m(master) * scale_mul)
    target_h = max(1, round(iso.height * target_w / iso.width))

    a = {**SECTION_ANCHOR.get(org.get("section", "above")), **ID_ANCHOR.get(oid, {})}
    ax = int(scene_w * a["x"]) + dx
    ay = int(scene_h * a["y"]) + dy
    left = ax - target_w // 2
    top = ay - (target_h if a["anchor"] == "feet" else target_h // 2)

    pct = 100 * target_w / scene_w
    print(f"  place: {org.get('commonName')} · true {width_m} m → {target_w}px "
          f"({pct:.0f}% of {'master' if master else 'proof'} width) "
          f"at anchor ({a['x']:.2f},{a['y']:.2f}) {a['anchor']}  dx={dx} dy={dy}")
    if dry:
        return None

    scene = Image.open(SCENE_PROOF).convert("RGBA") if not master else \
        Image.new("RGBA", (scene_w, scene_h), (8, 12, 16, 255))
    if master:
        print("  note: master mode has no 10800px scene yet — compositing on flat abyss "
              "as a scale check only (upscale scene first for real master art)")
    if scene.size != (scene_w, scene_h):
        scene = scene.resize((scene_w, scene_h), Image.LANCZOS)

    subj = iso.resize((target_w, target_h), Image.LANCZOS)
    if a["shadow"]:
        sh = contact_shadow((target_w, target_h))
        sx = ax - sh.width // 2
        sy = (top + target_h) - sh.height // 2
        scene.alpha_composite(sh, (sx, sy))
    scene.alpha_composite(subj, (left, top))
    return scene


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Living Past — place an MJ isolate on the scene")
    ap.add_argument("id", help="organism id, e.g. CR01")
    ap.add_argument("--plate", type=pathlib.Path, required=True, help="dropped MJ isolate PNG")
    ap.add_argument("--master", action="store_true", help="size at 10800px master scale")
    ap.add_argument("--isolate-only", action="store_true", help="just knock out + save the cutout")
    ap.add_argument("--dry-run", action="store_true", help="print the plan, write nothing")
    ap.add_argument("--dx", type=int, default=0, help="nudge placement x (px)")
    ap.add_argument("--dy", type=int, default=0, help="nudge placement y (px)")
    ap.add_argument("--scale", type=float, default=1.0, help="multiply true-scale width")
    args = ap.parse_args(argv)

    oid = args.id.upper()
    if oid not in ORGS:
        print(f"unknown id {oid}; have {', '.join(list(ORGS)[:6])}…", file=sys.stderr)
        return 1
    if not args.plate.exists():
        print(f"plate not found: {args.plate}", file=sys.stderr)
        return 1

    org = ORGS[oid]
    print(f"# {oid} · {org.get('commonName')} · {org.get('section')} · size {org.get('size')}")
    ORGANISMS.mkdir(parents=True, exist_ok=True)

    iso = isolate(args.plate)
    iso_out = ORGANISMS / f"{oid}_isolated.png"
    iso.save(iso_out)
    print(f"  saved isolate → {iso_out}")

    if args.isolate_only:
        return 0

    scene = place(org, iso, master=args.master, dx=args.dx, dy=args.dy,
                  scale_mul=args.scale, dry=args.dry_run)
    if scene is None:
        return 0
    out = PLATES / f"_scene_with_{oid}.png"
    scene.convert("RGB").save(out)
    print(f"  saved composite → {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
