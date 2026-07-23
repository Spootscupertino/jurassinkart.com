#!/usr/bin/env python3
"""The Living Past — meter-grid auto-size calculator (SCOPE §6, first real code).

Turns an organism's `size` string into exact on-canvas pixel dimensions on the
locked 24×36" master, enforcing the true-scale law and the micro-organism
exception (Law #2): anything too small to see at true scale is drawn enlarged
for visibility, with its true size reported so it can be stated in the key.

Reads px_per_m and the canvas from living_past/template/design_tokens.json so the
scale is never hand-typed. Importable (`compute_size`, `size_report`) and a CLI:

    python3 tools/scale_calc.py "12-13 m"        # one size
    python3 tools/scale_calc.py --ws "10 m"      # wingspan (width) dimension
    python3 tools/scale_calc.py --demo           # run the Volume-V roster sizes
    python3 tools/scale_calc.py --roster living_past/volume_v.json   # size a whole roster
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from dataclasses import dataclass, asdict

ROOT = pathlib.Path(__file__).resolve().parent.parent
TOKENS = json.loads((ROOT / "living_past/template/design_tokens.json").read_text())

PX_PER_M: float = TOKENS["scale"]["px_per_m"]          # 270
MASTER_W: int = TOKENS["canvas"]["trim_px"][0]         # 10800
# Smallest thing readable on the printed poster before we enlarge it (master px).
# ~60 px on a 10800-px-wide 36" poster ≈ 0.2" mark ≈ 22 cm of true world size.
MIN_DISPLAY_PX: float = 60.0

_UNIT_TO_M = {"m": 1.0, "cm": 0.01, "mm": 0.001, "km": 1000.0}


@dataclass
class SizeResult:
    raw: str                 # original size string
    parsed_m: float | None   # representative real dimension (m); None if unparseable
    dimension: str           # "length" | "wingspan" | "unknown"
    true_px: float | None    # exact px at true scale on the master
    display_px: float | None # px to actually draw (== true_px unless enlarged)
    enlarged: bool
    enlarge_factor: float    # display_px / true_px (1.0 if not enlarged)
    note: str                # human-readable, e.g. key caption

    def as_dict(self) -> dict:
        d = asdict(self)
        for k in ("parsed_m", "true_px", "display_px"):
            if d[k] is not None:
                d[k] = round(d[k], 2)
        d["enlarge_factor"] = round(d["enlarge_factor"], 2)
        return d


def _parse_meters(size: str) -> tuple[float | None, str]:
    """Return (representative_meters, dimension). Uses the MAX of a range
    (the animal's full adult size). Detects 'ws' → wingspan (a width)."""
    s = size.strip().lower()
    dimension = "wingspan" if re.search(r"\bws\b|wingspan", s) else "length"

    # collect all "<number><unit>" and bare-number ranges like "12-13 m"
    # normalize en-dash / unicode ranges to hyphen
    s_norm = s.replace("–", "-").replace("—", "-")
    # find the last unit token present
    unit = None
    for u in ("cm", "mm", "km", "m"):
        if re.search(rf"\b{u}\b|\d\s*{u}\b|\d{u}\b", s_norm):
            unit = u
            break
    if unit is None:
        return None, dimension

    # numbers appearing before that unit (take the segment up to the unit)
    seg = s_norm.split(unit)[0]
    nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", seg)]
    if not nums:
        return None, dimension
    meters = max(nums) * _UNIT_TO_M[unit]
    return meters, dimension


def compute_size(size: str, force_wingspan: bool = False) -> SizeResult:
    meters, dimension = _parse_meters(size)
    if force_wingspan:
        dimension = "wingspan"

    if meters is None:
        return SizeResult(size, None, "unknown", None, None, False, 1.0,
                          "unparseable size — place by hand")

    true_px = meters * PX_PER_M
    factor = MIN_DISPLAY_PX / true_px if true_px > 0 else float("inf")

    # Visible at true scale, or close enough that a nudge isn't a Law-#2 concern.
    if factor < 1.5:
        note = f"true scale · {dimension} {meters:.2f} m → {true_px:.0f} px on master"
        return SizeResult(size, meters, dimension, true_px, true_px, False, 1.0, note)

    # Genuine micro-organism: drawn enlarged for visibility, true size stated in key.
    display_px = MIN_DISPLAY_PX
    true_str = f"{meters*100:.0f} cm" if meters < 1 else f"{meters:.1f} m"
    fstr = f"{factor:.0f}×" if factor >= 10 else f"{factor:.1f}×"
    note = f"drawn {fstr} enlarged for visibility · true {true_str} (stated in key)"
    return SizeResult(size, meters, dimension, true_px, display_px, True, factor, note)


def size_report(size: str, force_wingspan: bool = False) -> str:
    r = compute_size(size, force_wingspan)
    tag = "ENLARGED" if r.enlarged else ("—" if r.parsed_m is None else "true")
    tp = f"{r.true_px:.0f}" if r.true_px is not None else "—"
    dp = f"{r.display_px:.0f}" if r.display_px is not None else "—"
    return f"{r.raw:<16} {tag:<9} true={tp:>7}px  draw={dp:>7}px  · {r.note}"


# --- Volume-V roster sizes (from dummy_v9.html field guide) for --demo ---
_DEMO = [
    "12-13 m", "8-9 m", "9-12 m", "6-8 m", "6-7 m ws", "10 m ws", "4 m", "3 m",
    "1 m", "20 cm", "3 cm", "1 cm", "10 cm", "4 cm", "17 cm", "soil",
    "10 m", "4 m", "1.5 m", "30 cm", "1.5 m", "3 m", "30 cm", "1 m",
    "12-17 m", "10 m", "5-6 m", "1.5 m", "3-5 m", "30 cm", "0.5-2 m", "10-40 cm",
]


def _run_roster(path: pathlib.Path) -> None:
    data = json.loads(path.read_text())
    orgs = data if isinstance(data, list) else data.get("organisms", [])
    for o in orgs:
        r = compute_size(o.get("size", ""))
        oid = o.get("id", "?")
        name = o.get("commonName") or o.get("scientificName") or ""
        o["_scale"] = r.as_dict()
        print(f"{oid:<5} {name:<28} {size_report(o.get('size',''))}")
    # write sized copy next to the roster
    out = path.with_name(path.stem + ".sized.json")
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"\nwrote {out}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Living Past auto-size calculator")
    ap.add_argument("size", nargs="?", help='e.g. "12-13 m", "30 cm", "10 m ws"')
    ap.add_argument("--ws", action="store_true", help="treat as wingspan (width)")
    ap.add_argument("--demo", action="store_true", help="run the Volume-V roster sizes")
    ap.add_argument("--roster", type=pathlib.Path, help="size every organism in a volume JSON")
    args = ap.parse_args(argv)

    print(f"# px_per_m={PX_PER_M}  master_w={MASTER_W}px  min_display={MIN_DISPLAY_PX}px\n")

    if args.roster:
        _run_roster(args.roster)
        return 0
    if args.demo:
        for s in _DEMO:
            print(size_report(s))
        return 0
    if args.size:
        print(size_report(args.size, args.ws))
        return 0
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
