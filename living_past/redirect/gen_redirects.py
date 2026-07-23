#!/usr/bin/env python3
"""The Living Past — redirect-table generator (SCOPE §8).

Print is forever. A printed QR encodes a stable ID-based redirect we own
(jrk.art/x/<id>); this table maps <id> → the current page path. Restructure the
site freely; the printed codes never die because only this table changes.

Reads every living_past/volume_*.json and emits redirect/redirects.json:
    { "CR01": {"slug": "tyrannosaurus-rex", "path": "/late-cretaceous/tyrannosaurus-rex", "volume": "V"}, ... }

    python3 living_past/redirect/gen_redirects.py
"""
from __future__ import annotations
import json, pathlib, re, glob

ROOT = pathlib.Path(__file__).resolve().parent.parent          # living_past/
OUT = pathlib.Path(__file__).parent / "redirects.json"

# volume title → URL base segment
VOLUME_BASE = {"V": "late-cretaceous"}


def slugify(name: str) -> str:
    s = name.lower()
    s = re.sub(r"\([^)]*\)", "", s)               # drop parentheticals
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def main() -> None:
    table: dict[str, dict] = {}
    for vp in sorted(glob.glob(str(ROOT / "volume_*.json"))):
        data = json.loads(pathlib.Path(vp).read_text())
        vol = data["$meta"]["volume"]
        base = VOLUME_BASE.get(vol, slugify(data["$meta"]["title"]))
        for o in data["organisms"]:
            slug = o.get("slug") or slugify(o["commonName"])
            table[o["id"]] = {
                "slug": slug,
                "path": f"/{base}/{slug}",
                "volume": vol,
            }
    OUT.write_text(json.dumps(table, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUT.name}: {len(table)} redirects across volumes {sorted({v['volume'] for v in table.values()})}")


if __name__ == "__main__":
    main()
