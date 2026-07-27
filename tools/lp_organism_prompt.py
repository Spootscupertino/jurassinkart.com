#!/usr/bin/env python3
"""The Living Past — single-organism MJ isolate prompt generator (#17).

Assembles a clean knockout-plate prompt from a volume_v.json record per the
recipe in living_past/mj_recipe.md. Prints the prompt ONLY — params (--ar,
--stylize, --ow) and reference images are the user's to add (collaboration-over-
automation workflow).

    python3 tools/lp_organism_prompt.py CR01
    python3 tools/lp_organism_prompt.py --all
    python3 tools/lp_organism_prompt.py CR25 --volume living_past/volume_v.json
"""
from __future__ import annotations
import argparse, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_VOL = ROOT / "living_past/volume_v.json"

# Framing lead — front-loaded because MJ weights early tokens hardest, so it must commit to the
# WHOLE subject in frame before any detail/ref pulls it into a portrait (the fix that beat the
# T. rex head-crop; see epic_scale_recipe). But the RIGHT framing depends on the body plan:
#   figure — long-bodied vertebrates: head-to-tail, wide, seen from a distance
#   wing   — pterosaurs: the clipped axis is the wingtip-to-wingtip span, not body length
#   macro  — cm-scale inverts: "distance" is backwards; they need a filling close focus
#   plate  — plants/fungi: a scientific specimen plate, no "animal/limbs/scales" language
FRAMING = {
    # Rule 8 (2026-07-27): the head-crop is beaten but the TAIL still runs off the right edge —
    # MJ fills the frame with the animal and the tail is the last thing it will sacrifice. Naming
    # the two extremities explicitly, and asking for empty space at the edges, is what holds it.
    "figure": ("full-length wide shot, zoomed out, the entire animal from snout to tail-tip within "
               "the frame, both the tip of the tail and the tip of the snout well clear of the "
               "frame edges with empty background all around them, seen from several metres back "
               "so the whole figure fits with room to spare"),
    "wing":   ("full flight shot with the entire wingspan wingtip to wingtip inside the frame, "
               "generous empty margin past both wingtips, the whole animal seen from below and in front"),
    "macro":  ("full macro studio shot, the entire specimen sharp and filling the frame with a clean "
               "even margin on every side, close focus, nothing cropped"),
    "plate":  ("clean scientific specimen plate, the whole organism within the frame with even "
               "margin on every side"),
}
FRAMING_BY_TYPE = {
    "land_animal": "figure", "marine_reptile": "figure", "fish": "figure", "mammal": "figure",
    "flying_reptile": "wing", "invertebrate": "macro", "plant": "plate",
}
# "Nothing clipped" clause — feet/flippers/wings/legs differ by body plan.
COMPLETE = {
    "land_animal":    "full body, all limbs, both feet and the complete untruncated tail visible",
    "marine_reptile": "full body, all flippers and the complete untruncated tail visible",
    "fish":           "full body, every fin and the complete untruncated tail fin visible",
    "mammal":         "full body, all four limbs and the tail visible",
    "flying_reptile": "whole body, both wings fully spread and the head crest visible",
    "invertebrate":   "whole body, every leg, segment and appendage visible",
    "plant":          "the whole organism and its structure visible",
}
# Surface-detail clause — "feathers/scales" is wrong for a fungus, a crab, or a fish.
SURFACE = {
    "land_animal":    "cleanly detailed skin, scales and feathers",
    "marine_reptile": "cleanly detailed skin and scales",
    "fish":           "cleanly detailed scales and fins",
    "mammal":         "cleanly detailed fur",
    "flying_reptile": "cleanly detailed pycnofibre fuzz and taut wing membrane",
    "invertebrate":   "cleanly detailed cuticle and segmentation",
    "plant":          "cleanly detailed surface texture",
}

POSE = {
    # angled ~30° off front (not a straight-on charge) so the flank and long tail read as length,
    # which is what actually keeps the body from vanishing behind the head.
    "land_animal":   "three-quarter view angled about thirty degrees from the front, mid-stride, head turned slightly toward camera, long tail sweeping out behind",
    "flying_reptile":"wings fully spread wingtip to wingtip, banking in flight, seen from below and in front",
    "marine_reptile":"full lateral view, mid-swim, subtle body roll revealing flippers/paddle",
    "fish":          "full lateral view, dynamic swimming curve, jaw and fin detail",
    "invertebrate":  "three-quarter view, whole body and segmentation clearly shown",
    "plant":         "isolated whole specimen, even frontal light",
    "mammal":        "low three-quarter view, whole body in an alert crouch",
}
ZONE_LIGHT = {
    "above":       "warm low golden sunset key light from the upper right, soft directional modelling on the form",
    "underground": "warm low golden sunset key light from the upper right, earthy ambient fill",
    "shoreline":   "warm low golden sunset key light from the upper right, faint water sheen",
    "ocean":       "cool blue-green light from directly above, soft god-ray falloff, gentle backscatter",
}
# Real, submittable aspect ratios — an executor firing these into MJ can't interpret
# "3:2 or 2:3 by build". Override per record with an `ar` field.
AR_BY_TYPE = {
    "flying_reptile": "16:9",   # the wingspan is the axis that clips
    "marine_reptile": "3:2",
    "fish": "3:2",
    "land_animal": "3:2",       # long tails make even bipeds read wide
    "mammal": "3:2",
    "invertebrate": "1:1",
    "plant": "2:3",
}
# Rule 7 — MJ resolves "isolated on flat grey" against the subject's implied habitat and the
# habitat wins for anything airborne or submerged (the Quetzalcoatlus run came back on open
# sky). A --no list is a much harder veto than another background adjective.
NEGATIVE = "--no background scenery, sky, horizon, clouds, ground, terrain, water surface, seabed, cast shadow"


def resolve_ar(o: dict) -> str:
    return o.get("ar") or AR_BY_TYPE.get(o.get("type", ""), "3:2")


def build_prompt(o: dict) -> str:
    """Assemble the isolate prompt. Every type-derived clause can be overridden per record —
    the roster has genuinely odd body plans (an egg clutch, a stalked crinoid, a straight-shelled
    ammonite) whose `type` is right for the encyclopedia but wrong as a drawing instruction."""
    t = o.get("type", "land_animal")
    pose = o.get("pose") or POSE.get(t, POSE["land_animal"])
    light = ZONE_LIGHT.get(o.get("section", "above"), ZONE_LIGHT["above"])
    framing = FRAMING[o.get("framing_mode") or FRAMING_BY_TYPE.get(t, "figure")]
    complete = o.get("complete") or COMPLETE.get(t, COMPLETE["land_animal"])
    surface = o.get("surface") or SURFACE.get(t, SURFACE["land_animal"])
    recon = o.get("recon") or ("accurate scientific reconstruction" if t == "plant"
                               else "anatomically accurate paleoart reconstruction")
    diet = o.get("diet", "").strip()
    # a diet-driven "build" reads oddly for plants/fungi ("symbiont-appropriate") — animals only
    diet_clause = f"{diet.lower()}-appropriate build, " if diet and diet not in ("", "—") and t != "plant" else ""
    sci, common = o.get("scientificName", ""), o.get("commonName", "")
    subject = f"{sci} ({common})" if sci and common and sci != common else (sci or common)
    return (
        f"{framing} of {subject}, {pose}, {complete}, "
        f"{recon}, {diet_clause}"
        f"{light}, isolated on a plain seamless flat mid-grey studio backdrop, no ground, "
        f"no cast shadow, natural color, {surface} "
        f"--style raw --ar {resolve_ar(o)} {NEGATIVE}"
    )


def emit(o: dict) -> None:
    conf = o.get("confidence", "")
    refs = " · needs refs" if o.get("needsRefs") else ""
    print(f"# {o['id']} · {o.get('commonName','')} · {o.get('size','')} · {conf}{refs}")
    print(f"#   --ar {resolve_ar(o)} is baked into the prompt   (add --ow / refs / --stylize yourself)")
    print(f"#   full-body tip: keep close-up/head refs at LOW weight (--ow ~3-8) or they force a head-crop;")
    print(f"#   for the full-figure plate use a full-body skeletal/paleoart ref, save head-orefs for a detail pass")
    print(build_prompt(o))
    print()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Living Past MJ isolate prompt generator")
    ap.add_argument("id", nargs="?", help="organism id, e.g. CR01")
    ap.add_argument("--all", action="store_true", help="print prompts for every organism")
    ap.add_argument("--volume", type=pathlib.Path, default=DEFAULT_VOL)
    args = ap.parse_args(argv)

    data = json.loads(args.volume.read_text())
    orgs = {o["id"]: o for o in data["organisms"]}

    if args.all:
        for o in data["organisms"]:
            emit(o)
        return 0
    if args.id:
        key = args.id.upper()
        if key not in orgs:
            print(f"unknown id {key}; have {', '.join(list(orgs)[:5])}…", file=sys.stderr)
            return 1
        emit(orgs[key])
        return 0
    ap.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
