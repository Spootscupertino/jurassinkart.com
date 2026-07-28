#!/usr/bin/env python3
"""The Living Past — MJ prompt library for the BACK PLATE's harvested components.

Sibling of `lp_organism_prompt.py`. That one generates the 32 organism isolates; this one
generates the *stage* they stand on. Per PLATE_ASSEMBLY.md the plate is harvested, never
generated in one shot — so each component needs its own prompt, and those prompts have to live
somewhere reproducible instead of being retyped into MJ from memory every session.

Two rules govern everything here, both learned the hard way:

  **One idea per prompt.** A prompt that asks for the log AND the moss AND the mushrooms returns
  a muddle with none of them nailed. Six separate renders, blended along the front, read as a
  world; one crammed render reads as a bad illustration.

  **No organisms, ever.** MJ invents anatomically wrong creatures and we composite the real ones
  ourselves at true scale. Every prompt carries an explicit animal veto.

Each slot's key is the filename it must land as in `living_past/plates/candidates/`, so the
download step is deterministic:

    cp ~/Downloads/*<job-uuid>*_0.png living_past/plates/candidates/micro_moss_cushion.png

Usage:
    python3 tools/lp_plate_prompt.py --all           # every slot, annotated
    python3 tools/lp_plate_prompt.py --group micro   # just the micro-habitat set
    python3 tools/lp_plate_prompt.py --missing       # only slots with no candidate PNG yet
    python3 tools/lp_plate_prompt.py --fire          # bare prompts, one per line, for the firehose
    python3 tools/lp_plate_prompt.py micro_log_interior
"""
from __future__ import annotations

import argparse
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CAND = ROOT / "living_past/plates/candidates"

# Zone light, copied verbatim in spirit from mj_recipe.md rule 3 — "one world, one light" has to
# hold for the plate components too, or the grade pass in build_backdrop.py is trying to reconcile
# six different afternoons.
WARM = ("warm low golden sunset key light raking in from the upper right, long soft shadows, "
        "late-day amber tone")
SUBSURFACE = ("cool blue-green light falling from directly above, soft god-ray shafts, "
              "gentle particulate backscatter")

# Vetoes. MJ's habitat gravity is strong: ask for macro ground and it adds a horizon, ask for sky
# and it adds a mountain range for scale. A --no list is a far harder veto than another adjective.
NO_LIFE = "animals, dinosaurs, people, hands, faces, text, watermark, signature, border, frame"
NO_WORLD = f"{NO_LIFE}, horizon, sky, distant landscape, mountains"
NO_GROUND = f"{NO_LIFE}, ground, terrain, trees, buildings, aircraft, birds"

# Late Cretaceous (Hell Creek, 66 Ma) flora vocabulary. Named explicitly because MJ's default
# "forest floor" is a modern temperate one — maple leaves, lawn grass, pine cones — and grass in
# particular did not yet form ground cover anywhere on Earth at 66 Ma. Every micro-habitat prompt
# anchors to this list, and NO_MODERN vetoes the anachronisms on the way out: a positive adjective
# competes with MJ's prior, a --no overrides it.
FLORA = "fern, cycad, ginkgo and magnolia leaf litter with bald cypress needles"
NO_MODERN = "grass, lawn, turf, maple leaves, oak leaves, pine cones, flowers"
NO_FLOOR = f"{NO_WORLD}, {NO_MODERN}"


PLATES: dict[str, dict] = {
    # ---- the micro-habitat set (idea #1) ------------------------------------------------------
    # Six plates blended along the front of the poster. This is the session's emphasis: the
    # cm-scale organisms (ant 3px, beetle larva 8px at true scale) have nowhere legible to be
    # until the front of the plate is drawn at macro scale.
    "micro_log_interior": dict(
        group="micro", ar="3:2",
        idea="rotting log split open — the single best cavity for cm-scale organisms",
        prompt=(
            "extreme macro photograph of the inside of a rotting fallen log, the trunk split open "
            "lengthwise to reveal soft punky red-brown decayed heartwood, crumbling fibrous grain, "
            "old beetle galleries winding through the wood, pale fungal threads webbing the "
            f"cavity, damp bark shelf above, {FLORA} scattered at the base, {WARM}, "
            "shallow depth of field, natural color, photographic, nothing stylised"),
        no=NO_FLOOR),
    "micro_moss_cushion": dict(
        group="micro", ar="3:2",
        idea="moss cushion — the soft, saturated green note the front edge lacks",
        prompt=(
            "extreme macro photograph of a dense cushion of moss growing over damp dark earth and "
            "a half-buried stone, individual moss shoots sharp and separate, tiny water droplets "
            f"caught on the tips, liverwort creeping at the margin, {WARM}, shallow depth of "
            "field, deep saturated green, natural color, photographic, nothing stylised"),
        no=NO_FLOOR),
    "micro_fern_crozier": dict(
        group="micro", ar="2:3",
        idea="unfurling fern crozier — the one vertical gesture in an otherwise horizontal band",
        prompt=(
            "extreme macro photograph of a single unfurling fern crozier, the tight spiral "
            "fiddlehead rising on a fuzzy scaled stem, fine russet hairs catching the light along "
            f"its curve, blurred fern fronds behind it, {WARM} backlighting and rimming the "
            "spiral, shallow depth of field, natural color, photographic, nothing stylised"),
        no=NO_FLOOR),
    "micro_mushroom_cluster": dict(
        group="micro", ar="3:2",
        idea="mushroom cluster — gives the decomposer/fungi roster entries a real home",
        prompt=(
            "extreme macro photograph of a tight cluster of small pale mushrooms erupting from "
            "the base of a rotting stump, gills visible beneath the caps, wet earth and dark leaf "
            f"litter around the stems, one cap broken open, {WARM}, shallow depth "
            "of field, natural color, photographic, nothing stylised"),
        no=NO_FLOOR),
    "micro_puddle_edge": dict(
        group="micro", ar="3:2",
        idea="puddle edge — a water note at macro scale, and a mirror that adds sky without sky",
        prompt=(
            "extreme macro photograph of the muddy edge of a shallow rain puddle on a forest "
            "floor, the meniscus curving against a rim of dark silt, sunken leaves visible under "
            "the water, a faint warm reflection on the still surface, cracked drying mud beyond "
            f"the rim, {FLORA} at the margin, {WARM}, shallow depth of field, natural color, "
            "photographic, nothing stylised"),
        no=NO_FLOOR),
    "micro_bark_crevice": dict(
        group="micro", ar="2:3",
        idea="bark crevice — the vertical surface habitat; everything else in the set is ground",
        prompt=(
            "extreme macro photograph of a deep vertical crevice in the thick fissured bark of an "
            "ancient conifer, ridged plates of grey-brown bark separated by a dark sheltered "
            "channel, dried resin bleeding down one ridge, lichen crusting the outer plates, "
            f"{WARM} raking across the ridges so the fissure reads deep, shallow depth of field, "
            "natural color, photographic, nothing stylised"),
        no=NO_FLOOR),

    # ---- the sky, as three stacked plates (idea #4) -------------------------------------------
    # Stop hunting for one sky that does everything. Three plates, stacked by altitude, each doing
    # one job — exactly the harvesting thesis applied to the top third of the poster.
    "sky_high_cirrus": dict(
        group="sky", ar="16:9",
        idea="top band — thin ice cloud in deep indigo; the asteroid whisper lands here",
        prompt=(
            "photograph of high altitude sky only, looking straight up into deep clear indigo, "
            "thin wispy cirrus ice clouds streaked in fine parallel filaments across the upper "
            "atmosphere, faintly lit warm from below by a sun already low out of frame, vast empty "
            "airy space, natural color, photographic, nothing stylised"),
        no=NO_GROUND),
    "sky_mid_cumulus": dict(
        group="sky", ar="16:9",
        idea="middle band — the sculpted volume that gives the sky depth",
        prompt=(
            "photograph of mid-altitude sky only, scattered cumulus clouds with sculpted sunlit "
            "tops and soft violet-grey undersides, lit from low on the right so each cloud casts "
            "its own shadow across the one behind it, clear air between them, natural color, "
            "photographic, nothing stylised"),
        no=NO_GROUND),
    "sky_horizon_glow": dict(
        group="sky", ar="16:9",
        idea="bottom band — the warm gradient the land dissolves up into",
        prompt=(
            "photograph of a sunset horizon glow only, a broad smooth gradient from deep amber and "
            "burnt orange at the base up through rose into pale blue, faint volcanic haze "
            "thickening the lowest band, no clouds, no sun disc, nothing but graded air, natural "
            "color, photographic, nothing stylised"),
        no=f"{NO_GROUND}, sun disc, clouds"),

    # ---- the river margin (idea #6) ----------------------------------------------------------
    # habitat_map.py caught this: five organisms (Borealosuchus, Basilemys, the gar, the guitarfish
    # ray, Champsosaurus) need a freshwater river margin, and it is currently distant braided sand.
    "river_margin_macro": dict(
        group="river", ar="3:2",
        idea="close-up river margin — five organisms live here and it's currently distant sand",
        prompt=(
            "photograph of the close-up margin of a slow freshwater river, wet dark sand shelving "
            "into shallow tea-coloured water, rippled silt bars and scattered water-worn pebbles, "
            "a half-sunk driftwood snag, horsetails and ferns crowding the bank behind, fine "
            f"debris line marking the last high water, {WARM} skimming across the wet sand, "
            "natural color, photographic, nothing stylised"),
        no=f"{NO_LIFE}, sky, mountains, waterfall, boats"),

    # ---- the burrow cutaway (idea #7) --------------------------------------------------------
    # The one plate that ties the two habitat systems into a single continuous world: the viewer
    # should be able to follow a tunnel from surface leaf litter down into the soil ribbon.
    "burrow_cutaway": dict(
        group="burrow", ar="3:2",
        idea="cutaway tying surface litter to the soil ribbon — one continuous world",
        prompt=(
            "cutaway cross-section photograph of soil seen from the side as if a trench wall had "
            "been cut clean, the top centimetres of dark leaf litter and root mat at the very top, "
            "a smooth open burrow tunnel descending from that surface through the earth and "
            "widening into a rounded hollow nest chamber lined with dry plant fibre, fine pale "
            "roots threading the surrounding soil, distinct earth layers darkening with depth, "
            "even soft light inside the cut, natural color, photographic, scientific accuracy, "
            "nothing stylised"),
        no=f"{NO_LIFE}, sky, horizon, diagram, labels, arrows, illustration"),

    # ---- underwater detail passes (idea #8) --------------------------------------------------
    # The ocean is the emptiest quarter of the plate. Three passes, shallow to deep, each blended
    # into its own depth band rather than one "underwater scene" laid over the whole wedge.
    "ocean_algae_fringe": dict(
        group="ocean", ar="3:2",
        idea="shelf band — the sunlit fringe that makes the shallows feel inhabited",
        prompt=(
            "underwater photograph of a sunlit shallow seafloor fringe, dense ribbons of brown and "
            "olive algae swaying over pale rippled sand, encrusting growth on scattered rock, "
            "bright dappled caustic light patterns moving across the bottom, clear turquoise "
            "water, natural color, photographic, nothing stylised"),
        no=f"{NO_LIFE}, fish, coral reef, divers, boats, sky, surface"),
    "ocean_shell_beds": dict(
        group="ocean", ar="3:2",
        idea="mid band — a densely littered seafloor; reads as accumulated time, not decoration",
        prompt=(
            "underwater photograph of a seafloor densely paved with empty shells, thick beds of "
            "broken and whole bivalve and ammonite shells half-buried in grey sediment, layers of "
            f"shell hash packed together, {SUBSURFACE}, natural color, photographic, "
            "nothing stylised"),
        no=f"{NO_LIFE}, living animals, fish, coral reef, divers, sky, surface"),
    "ocean_marine_snow": dict(
        group="ocean", ar="3:2",
        idea="abyss band — the only texture the void gets, and the thing that proves it's water",
        prompt=(
            "underwater photograph of the open deep sea in near darkness, drifting marine snow "
            "falling slowly through the water column, thousands of tiny pale organic particles "
            "suspended at every distance, a single faint shaft of light from far above dying out "
            "into black, immense empty water, natural color, photographic, nothing stylised"),
        no=f"{NO_LIFE}, fish, jellyfish, seafloor, ground, coral, submarine, sky, surface"),
}

GROUPS = ("micro", "sky", "river", "burrow", "ocean")


def build(slot: str) -> str:
    p = PLATES[slot]
    return f"{p['prompt']} --style raw --ar {p['ar']} --no {p['no']}"


def have(slot: str) -> bool:
    return (CAND / f"{slot}.png").exists()


def emit(slot: str) -> None:
    p = PLATES[slot]
    mark = "have" if have(slot) else "MISSING"
    print(f"# {slot}  [{p['group']}]  {mark}")
    print(f"#   {p['idea']}")
    print(f"#   lands as: living_past/plates/candidates/{slot}.png")
    print(build(slot))
    print()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Living Past MJ back-plate component prompts")
    ap.add_argument("slot", nargs="?", help="slot name, e.g. micro_log_interior")
    ap.add_argument("--all", action="store_true", help="print every slot")
    ap.add_argument("--group", choices=GROUPS, help="print one group only")
    ap.add_argument("--missing", action="store_true",
                    help="restrict to slots with no candidate PNG yet")
    ap.add_argument("--fire", action="store_true",
                    help="bare prompts, one per line, for a firehose executor")
    args = ap.parse_args(argv)

    if args.slot:
        if args.slot not in PLATES:
            print(f"unknown slot {args.slot}; have {', '.join(PLATES)}", file=sys.stderr)
            return 1
        sel = [args.slot]
    elif args.all or args.group or args.missing or args.fire:
        sel = [s for s in PLATES if not args.group or PLATES[s]["group"] == args.group]
    else:
        ap.print_help()
        return 1

    if args.missing:
        sel = [s for s in sel if not have(s)]
    if not sel:
        print("# nothing to do — every selected slot already has a candidate PNG")
        return 0

    if args.fire:
        for s in sel:
            print(build(s))
        return 0
    for s in sel:
        emit(s)
    print(f"# {len(sel)} slot(s).  Personalization stays OFF in MJ (see MJ_FIREHOSE.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
