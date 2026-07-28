# The Living Past — single-organism MJ isolate recipe (#17)

Every organism is generated **alone**, as a clean knockout plate, then composited
to true scale in Photoshop (SCOPE §10; proven in `project_living_past_composite_validated`).
The recipe below is what `tools/lp_organism_prompt.py` assembles from each
`volume_v.json` record. It follows the project's 5-section priority
(Subject → Interaction → Environment → Lighting → Camera) but bends it for **isolation**.

## The five rules of an isolate plate
1. **One subject, whole.** Full body, every limb visible, anatomically accurate — the moat is conquering the hard anatomy others botch (Brand vision). No scenery, no second animal.
2. **Knockout-friendly background.** Solid flat background, no ground contact, no cast shadow — so the knockout is clean. **Correction (2026-07-28):** background removal is *not* UI-only as recorded here previously. Photoshop's Select Subject runs from JSX (`executeAction(stringIDToTypeID("autoCutout"))`) at ~2 s a plate, and it clears the faint floor plane that the flood-fill knockout provably cannot reach. Use `tools/ps_isolate.py`; see `PHOTOSHOP.md`. Keeping the edge easy still matters, but it is no longer the only defence.
3. **Matched light = composites for free.** Light direction/temperature is set by the organism's **zone** so all 32 share "one world, one light" before the `70_WORLD_GRADE` pass:
   - above / underground / shoreline → **warm low sunset key from the upper right**, long golden light (matches the volcanic-sunset sky).
   - ocean → **cool blue-green light from directly above**, soft god-ray falloff, slight backscatter (matches the depth column).
4. **Distinct POV per species** (Brand vision — "species how we see them"). Pose defaults come from `type`; override per record with a `pose` field.
5. **Lean on content, generous on nothing fake.** MJ invents bad strata/roots/creatures — we composite those accurately. The isolate prompt asks only for the animal, superbly rendered.

## Prompt skeleton
```
<framing-lead-by-type> of <scientificName> (<commonName>), <pose-by-type>,
<completeness-by-type>, <reconstruction>, <diet-build (animals only)>,
<zone-light>, isolated on a solid flat mid-grey background,
no shadow, no ground, natural color, <surface-by-type>
--ar <by-pose> --style raw
```

**Framing is type-aware** (2026-07-23) — one lead does not fit all body plans:

| mode | for | lead commits to |
|---|---|---|
| `figure` | land_animal, marine_reptile, fish, mammal | whole animal head→tail, wide, seen from a distance |
| `wing` | flying_reptile | full **wingspan wingtip-to-wingtip** (the axis that clips), from below/front |
| `macro` | invertebrate | full specimen **filling the frame, close focus** (distance is backwards at cm scale) |
| `plate` | plant / fungi | scientific specimen plate, no "animal/limbs/scales" language |

Completeness ("nothing clipped") and surface-detail clauses also vary by type (feet vs flippers
vs wings vs legs; scales/feathers vs cuticle vs wing-membrane vs surface texture). Genuinely odd
body plans (crinoid, belemnite, baculites, inoceramus bivalve, mycorrhizal fungi) still need a
one-line per-record `pose` override — same mechanism as the T. rex roar.
- Params (`--ar`, `--stylize`, `--ow`, refs) are **left to the user** per the collaboration-over-automation workflow — the generator prints the clean prompt only. Suggested `--ar`: long-body → `3:2`, tall/standing → `2:3`, wingspan → `16:9`.
- Mid-grey (`#8a8a8a`) knockout reads cleanly against both feathered and pale subjects; switch to dark grey for pale/white animals.

## Rule 6 — get the WHOLE animal in frame (the crop fix)
The isolate's #1 failure is MJ cropping to a hero head/chest. It's the same "portrait
gravity" the epic-scale recipe beat, and the fixes are the same:
1. **Front-load the framing.** The prompt now leads with a full-length/margin/distance
   clause *before* the subject, because MJ weights early tokens hardest — it commits to the
   whole figure before detail or refs pull it into a portrait.
2. **Ref weight is the balance knob.** A close-up/head oref at high `--ow` votes on the whole
   composition and forces a head-crop. Keep head refs at **`--ow ~3-8`**, or use a **full-body**
   skeletal/paleoart ref for the full-figure plate and save the head oref for a separate
   detail pass.
3. **Don't invite the zoom.** Dropped `studio knockout / museum-grade / hyper-detailed` (macro
   cues that pull MJ in close) in favour of plain `cleanly detailed skin/feathers/scales`.
4. **Angle off straight-front.** Land animals now pose ~30° off front with the tail sweeping
   out, so body length reads instead of foreshortening away behind the skull.

## Pose defaults by type
| type | default POV / pose |
|---|---|
| land_animal | 3/4 front, striding, head slightly toward camera, worm's-eye for titans |
| flying_reptile | wings fully spread, banking, seen from below-front |
| marine_reptile | full lateral, mid-swim, subtle roll to show paddle/flipper |
| fish | full lateral, dynamic curve, jaw detail |
| invertebrate | macro 3/4, showing shell/segmentation clearly |
| plant | isolated specimen, whole frond/leaf, even light |
| mammal | low 3/4, alert crouch, fur detail |

## Usage
```
python3 tools/lp_organism_prompt.py CR01          # T. rex isolate prompt
python3 tools/lp_organism_prompt.py --all         # every organism in Volume V
```
