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

import numpy as np
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

GREY_TOLERANCE = 78   # legacy global fallback — only used if --tolerance is passed explicitly
EDGE_FEATHER = 1.2    # px of alpha blur to de-jag the knockout edge
EDGE_ERODE = 1        # px of alpha erosion BEFORE feathering — see knockout_grey
RING_SHARE = 0.08     # a border colour must own this much of the ring to count as background


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


def border_ring(arr, band_px: int | None = None):
    """The plate's own border pixels — the only part of the image we know is background."""
    h, w = arr.shape[:2]
    b = band_px or max(2, min(h, w) // 50)
    return np.concatenate([arr[:b].reshape(-1, 3), arr[-b:].reshape(-1, 3),
                           arr[:, :b].reshape(-1, 3), arr[:, -b:].reshape(-1, 3)])


def background_bands(ring, min_share: float = RING_SHARE, merge: int = 40):
    """The distinct background colours present along this plate's border.

    Two different things live on an MJ isolate's border:

      * the mid-grey field itself, usually a gentle gradient;
      * the faint floor plane MJ adds under the feet despite "no ground" — a *different* grey,
        unreachable from the top corners and a different seed colour from the bottom ones,
        which is why it survives a naive fill and composites as a pale bar under the feet.

    A colour counts as a band only if it owns a real share of the border. That share test is what
    keeps a subject touching the frame edge from seeding a flood fill into its own body: a tail
    crossing the edge is a thin run, a floor plane is a wide one."""
    q = (ring // 16).astype(np.int64)
    key = q[:, 0] * 1024 + q[:, 1] * 32 + q[:, 2]
    vals, counts = np.unique(key, return_counts=True)
    bands = []
    for i in np.argsort(-counts):
        if counts[i] / len(ring) < min_share:
            break
        centre = ring[key == vals[i]].mean(axis=0)
        if all(np.abs(centre - c).sum() > merge for c in bands):
            bands.append(centre)
    return bands or [np.median(ring, axis=0)]


# Tolerance ladder, swept per plate. PIL's floodfill compares each candidate against the SEED
# pixel using a 1-norm summed across all three channels, so these are L1 numbers — 78 (the old
# global) is only ~26 per channel.
TOL_LADDER = (20, 30, 40, 55, 70, 85, 100, 120, 145, 175, 210)
TOL_SHAPE = 1.8       # retained-shape complexity may rise this much above its best before we stop
TOL_GROWTH = 1.15     # a band may claim this much more than its base claim before we call it a burst
TOL_SLACK = 0.005     # ...plus this much of the frame, so a band with a tiny base can still breathe
SEED_RADIUS = 90      # L1 distance from a band centre within which a border pixel may seed


def _seeds(w: int, h: int):
    step = max(8, min(w, h) // 24)
    s = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    s += [(x, 0) for x in range(0, w, step)] + [(x, h - 1) for x in range(0, w, step)]
    s += [(0, y) for y in range(0, h, step)] + [(w - 1, y) for y in range(0, h, step)]
    return s


def _fill_mask(im: Image.Image, tols, bands, only: int | None = None) -> np.ndarray:
    """Flood the background inward from dense border seeds; return the filled (=transparent) mask.

    Each seed floods at the tolerance belonging to the band it matches — that is the whole point.
    `only` restricts firing to one band's seeds, which is how each band's tolerance gets swept
    independently."""
    rgb = im.convert("RGB")
    w, h = rgb.size
    SENT = (0, 255, 1)     # sentinel unlikely to occur in the plate
    for seed in _seeds(w, h):
        px = rgb.getpixel(seed)
        if px == SENT:
            continue                      # already cleared by an earlier fill
        p = np.asarray(px, np.float32)
        dists = [np.abs(p - c).sum() for c in bands]
        i = int(np.argmin(dists))
        if dists[i] > SEED_RADIUS:
            continue                      # subject crosses the frame edge here — do not seed
        if only is not None and i != only:
            continue
        ImageDraw.floodfill(rgb, seed, SENT, thresh=int(tols[i]))
    return (np.asarray(rgb) == np.array(SENT, np.uint8)).all(axis=2)


def _complexity(kept: np.ndarray) -> float:
    """Perimeter over sqrt(area) of the retained mask — how ragged the silhouette is.

    Scale-invariant, so a big animal and a small one are judged the same way, and it costs two
    array comparisons. This is the measurement that finally separated "still eating background"
    from "eating the animal": a fill chewing background leaves the silhouette smooth, while one
    breaking through the edge sprays disconnected speckles along the tail and crest — visually
    obvious in the before/after strips, and a 3-6x jump in this number."""
    a = int(kept.sum())
    if a == 0:
        return float("inf")
    p = int((kept[:, 1:] != kept[:, :-1]).sum() + (kept[1:, :] != kept[:-1, :]).sum())
    return p / (a ** 0.5)


def _knee(im: Image.Image, bands, band: int, secondary: bool) -> int:
    """Largest tolerance for one band's seeds before the fill starts eating the subject.

    Each band is swept with only its own seeds firing. Two independent stop rules, because the
    two ways a fill can go wrong look nothing alike and neither test sees both:

      * **Shape complexity** (`_complexity`) catches *fragmenting* erosion — the speckled
        chewing along a tail or crest. This is the failure on the dark field band of every plate.
      * **Claimed-area growth**, against the band's own base claim, catches *smooth* over-claiming
        — a pale band quietly swallowing pale armour as one solid blob, which leaves the
        silhouette perfectly smooth and is invisible to the complexity test. This is the failure
        on the Ankylosaurus.

    The growth test only applies to secondary bands. On the dominant field band it is worse than
    useless: a gradient background legitimately grows that band's claim from 50% to 65% of the
    frame across the ladder, so any growth ceiling tight enough to mean something there also
    stops the sweep long before the background is gone.

    A colour-distance cap was tried as well and does not work at all: the shaded parts of an
    animal sit within 7-31 L1 of the background grey, so any cap tight enough to protect them
    collapses the tolerance to nothing."""
    tols = [TOL_LADDER[0]] * len(bands)
    kept = ~_fill_mask(im, tols, bands, only=band)
    ceiling = (1.0 - kept.mean()) * TOL_GROWTH + TOL_SLACK
    best_shape = _complexity(kept)
    best = TOL_LADDER[0]
    for tol in TOL_LADDER[1:]:
        tols[band] = tol
        kept = ~_fill_mask(im, tols, bands, only=band)
        shape = _complexity(kept)
        if shape > best_shape * TOL_SHAPE:
            break
        if secondary and (1.0 - kept.mean()) > ceiling:
            break
        best_shape = min(best_shape, shape)
        best = tol
    return best


def derive_tolerances(im: Image.Image, bands) -> list[int]:
    """Choose a tolerance PER BAND, each from its own response curve on this plate.

    Two earlier attempts are worth recording, because both looked reasonable and both were wrong:

    1. *One number derived from the border's colour spread.* Measured against the three real
       plates it produced 161-180 where the right answer was 70-100, and at those values the fill
       burst through the silhouette and ate most of the T. rex. How wide the border gradient is
       simply does not predict how far the background sits from the subject.

    2. *One swept number for the whole plate.* Much better — it stopped the fill eating the
       animal — but it is capped by whichever band is closest to the subject, and on the
       Edmontosaurus plate that cap left MJ's pale floor plane sitting under the feet. One
       tolerance cannot both clear a pale floor and spare a dark flank.

    Hence per band, swept — but not symmetrically, because the two kinds of band carry very
    different risk. Measured across all three plates, every attempt to push the *dominant* band
    past the old global 78 cost silhouette: the T. rex lost its crest and tail edge, the
    Edmontosaurus its neck and tail. That band is the field the subject is composited against, so
    78 is doing real work as a calibrated safe value and it stays the ceiling for it.

    The headroom is entirely in the *secondary* bands — MJ's floor plane and backdrop hotspots.
    They are small, tonally distinct, and precisely what one global number could never clear
    without endangering the silhouette. Those sweep freely upward under the growth cap, which is
    where the pale bar under the feet finally goes."""
    tols = [_knee(im, bands, i, secondary=i > 0) for i in range(len(bands))]
    tols[0] = min(tols[0], GREY_TOLERANCE)     # bands are share-ordered, so [0] is the field
    return tols


def knockout_grey(im: Image.Image, tolerance: int | None = None) -> Image.Image:
    """Remove the connected background by flood-filling inward from the whole border.

    The MJ isolate recipe asks for a flat mid-grey field touching every edge, so the
    background is one connected region reachable from outside — flood-fill it, mark filled
    pixels transparent, feather the edge. Any grey *inside* the animal is untouched because
    it isn't connected to the border.

    Four corner seeds are not enough in practice, and neither is one tolerance for every plate:
    see `background_bands` for what else lives on the border, and `derive_tolerance` for how the
    number is chosen from this plate rather than from the average of all plates.

    Pass `tolerance` to override the derivation with a single fixed number."""
    bands = background_bands(border_ring(np.asarray(im.convert("RGB"), np.float32)))
    tols = [tolerance] * len(bands) if tolerance is not None else derive_tolerances(im, bands)
    filled = _fill_mask(im, tols, bands)
    kept = 1.0 - filled.mean()
    detail = ", ".join(f"{tuple(int(v) for v in c)}@{t}" for c, t in zip(bands, tols))
    print(f"  knockout: {len(bands)} background band(s) {detail} — {100*kept:.0f}% of frame kept")

    alpha = Image.fromarray(np.where(filled, 0, 255).astype(np.uint8), "L")
    # Erode before feathering. The knockout edge carries a 1-2px fringe of background grey
    # (MJ's own antialiasing), and against the dark plate that fringe reads as a pale halo —
    # a large part of why the composited organisms scored 4/10. Feathering alone spreads the
    # fringe instead of removing it; pulling the alpha in by a pixel first cuts it off.
    for _ in range(EDGE_ERODE):
        alpha = alpha.filter(ImageFilter.MinFilter(3))
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


def isolate(plate_path: pathlib.Path, tolerance: int | None = None) -> Image.Image:
    im = Image.open(plate_path)
    if has_real_alpha(im):
        iso = trim(im.convert("RGBA"))
        how = "existing alpha"
    else:
        iso = trim(knockout_grey(im, tolerance=tolerance))
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
    ap.add_argument("--tolerance", type=int, default=None,
                    help="override the per-plate derived knockout tolerance with one global number")
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

    iso = isolate(args.plate, tolerance=args.tolerance)
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
