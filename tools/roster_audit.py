#!/usr/bin/env python3
"""The Living Past — roster temporal-fit auditor (SCOPE Law #1).

Checks every organism's ageRange_Ma against the volume interval_Ma and reports
which ones don't overlap ("temporal guardrail"), plus the 4×8 strata balance.

    python3 tools/roster_audit.py living_past/volume_v.json
"""
from __future__ import annotations
import json, pathlib, sys
from collections import Counter

SECTIONS = ["above", "underground", "shoreline", "ocean"]


def overlaps(a: list[float], b: list[float]) -> bool:
    # ranges are [older, younger] in Ma (older = larger number)
    a_old, a_yng = max(a), min(a)
    b_old, b_yng = max(b), min(b)
    return a_yng <= b_old and b_yng <= a_old


def main(path: str) -> int:
    data = json.loads(pathlib.Path(path).read_text())
    interval = data["$meta"]["interval_Ma"]
    orgs = data["organisms"]
    print(f"Volume {data['$meta']['volume']} — interval {interval[0]}–{interval[1]} Ma")
    print(f"{data['$meta']['interval_label']}\n")

    fails, marginals = [], []
    for o in orgs:
        ar = o.get("ageRange_Ma")
        if not ar:
            marginals.append((o["id"], o["commonName"], "no ageRange"))
            continue
        if not overlaps(ar, interval):
            gap = round(min(ar) - interval[0], 1)  # how far its youngest is before interval start
            fails.append((o["id"], o["commonName"], f"{ar[0]}–{ar[1]} Ma", gap))

    print(f"TEMPORAL FAILS ({len(fails)}) — youngest fossil predates the interval:")
    for oid, nm, rng, gap in fails:
        print(f"  ✗ {oid} {nm:<34} {rng:<16} (ends ~{gap} My before interval opens)")
    if not fails:
        print("  none — all organisms overlap the interval ✓")

    print("\nSTRATA BALANCE (target 8 each):")
    counts = Counter(o["section"] for o in orgs)
    for s in SECTIONS:
        mark = "✓" if counts[s] == 8 else "✗"
        print(f"  {mark} {s:<12} {counts[s]}")

    ids = [o["id"] for o in orgs]
    dupes = [i for i, c in Counter(ids).items() if c > 1]
    print(f"\nTOTAL {len(orgs)} organisms · unique ids: {'ok' if not dupes else 'DUPES ' + str(dupes)}")
    print(f"Confidence mix: {dict(Counter(o['confidence'] for o in orgs))}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "living_past/volume_v.json"))
