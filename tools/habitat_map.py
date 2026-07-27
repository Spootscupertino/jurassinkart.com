#!/usr/bin/env python3
"""The Living Past — derive the required TOPOGRAPHY from the roster (#22).

Eric, 2026-07-27: *"the topography should be created to support the organisms."*

Backwards from how we were working. Until now the plate was designed as a landscape and the cast
was jammed into whatever ground happened to exist — which is why six underground organisms had
nowhere legible to be and the shoreline species had no water margin to stand in.

This inverts it: every organism declares the terrain feature it needs to be believable, and the
tool emits the feature checklist the base plate has to satisfy. The plate prompt is then written
*from that list*, not from taste.

    python3 tools/habitat_map.py              # the checklist, grouped by depth plane
    python3 tools/habitat_map.py --prompt     # feature clauses ready to paste into an MJ prompt
    python3 tools/habitat_map.py --unmet      # features nothing in the roster needs (cut them)
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import OrderedDict

ROOT = pathlib.Path(__file__).resolve().parent.parent
VOL = json.loads((ROOT / "living_past/volume_v.json").read_text())

# Each feature: what the plate must contain, and which depth plane it belongs to.
# plane order = how far from camera: 0 macro foreground .. 4 horizon, 5+ underwater
FEATURES = OrderedDict([
    ("leaf_litter",   dict(plane=0, desc="deep leaf-litter forest floor pressed right to the bottom edge, "
                                          "huge fallen leaves, mossy rotting log, damp humus")),
    ("root_zone",     dict(plane=0, desc="exposed root buttresses and a root zone threading down into soil")),
    ("open_plain",    dict(plane=2, desc="broad open flat grazing plain of bare ground and low scrub")),
    ("foreground_hollow", dict(plane=1, desc="a low foreground hollow and rise the camera looks up out of, "
                                             "worm's-eye standing room")),
    ("rocky_rise",    dict(plane=2, desc="a rocky upland rise with boulders and broken ground")),
    ("scrub",         dict(plane=2, desc="patches of low woody scrub and cycads")),
    ("sandy_bench",   dict(plane=1, desc="a raised sandy overbank bench and levee of soft dry sand")),
    ("river_margin",  dict(plane=2, desc="a freshwater river channel and muddy bank cutting across the plain")),
    ("intertidal",    dict(plane=3, desc="a wet intertidal sand flat with tide pools where land meets sea")),
    ("treeline",      dict(plane=4, desc="a hazed distant conifer treeline and low blue hills")),
    ("shallow_shelf", dict(plane=5, desc="clear sunlit turquoise shallow shelf")),
    ("drop_off",      dict(plane=5, desc="a steep drop-off where the shelf falls away")),
    ("open_water",    dict(plane=6, desc="a vast open midwater column with light shafts")),
    ("abyss",         dict(plane=7, desc="an enormous cold blue-black abyssal void of great vertical depth")),
    ("seafloor",      dict(plane=7, desc="a dim seafloor of muddy substrate")),
])

# organism id -> the feature it needs to stand in / on
NEEDS = {
    "CR01": "foreground_hollow", "CR02": "open_plain", "CR03": "open_plain", "CR04": "open_plain",
    "CR05": "scrub", "CR06": "rocky_rise", "CR07": "open_plain", "CR08": "rocky_rise",
    "CR09": "root_zone", "CR10": "root_zone", "CR11": "leaf_litter", "CR12": "leaf_litter",
    "CR13": "leaf_litter", "CR14": "root_zone", "CR15": "sandy_bench", "CR16": "root_zone",
    "CR17": "river_margin", "CR18": "river_margin", "CR19": "river_margin", "CR20": "river_margin",
    "CR21": "river_margin", "CR22": "scrub", "CR23": "intertidal", "CR24": "shallow_shelf",
    "CR25": "abyss", "CR26": "abyss", "CR27": "open_water", "CR28": "open_water",
    "CR29": "open_water", "CR30": "open_water", "CR31": "seafloor", "CR32": "seafloor",
}


def build() -> OrderedDict:
    orgs = {o["id"]: o for o in VOL["organisms"]}
    out: OrderedDict = OrderedDict((f, []) for f in FEATURES)
    for oid, feat in NEEDS.items():
        if oid in orgs:
            out[feat].append(orgs[oid])
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Derive required topography from the roster")
    ap.add_argument("--prompt", action="store_true", help="emit feature clauses for an MJ prompt")
    ap.add_argument("--unmet", action="store_true", help="list features no organism needs")
    args = ap.parse_args(argv)

    m = build()
    if args.unmet:
        for f, orgs in m.items():
            if not orgs:
                print(f"{f}: needed by nothing — cut it from the plate")
        return 0

    if args.prompt:
        # ordered near -> far, which is also how the clauses should read in the prompt
        for f, spec in sorted(FEATURES.items(), key=lambda kv: kv[1]["plane"]):
            if m[f]:
                print(f"{spec['desc']},")
        return 0

    planes = {0: "MACRO FOREGROUND", 1: "FOREGROUND", 2: "MIDDLE DISTANCE", 3: "SHORE",
              4: "HORIZON", 5: "SHALLOWS", 6: "MIDWATER", 7: "DEEP"}
    cur = None
    total = 0
    for f, spec in sorted(FEATURES.items(), key=lambda kv: kv[1]["plane"]):
        if spec["plane"] != cur:
            cur = spec["plane"]
            print(f"\n=== {planes[cur]} ===")
        orgs = m[f]
        total += len(orgs)
        names = ", ".join(f"{o['id']} {o['commonName']}" for o in orgs) or "—"
        print(f"  {f:<18} n={len(orgs):2}  {names}")
    print(f"\n{total}/{len(VOL['organisms'])} organisms have a declared home.")
    missing = [o["id"] for o in VOL["organisms"] if o["id"] not in NEEDS]
    if missing:
        print(f"NO HOME DECLARED: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
