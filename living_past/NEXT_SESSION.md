# The Living Past — Next Session Launch Prompt (updated 2026-07-29, evening)

> Paste the block below into a fresh session.

---

Vol V. Plate of record is **`plates/backdrop_v8.png`**; the cast state is
**`plates/_scene_cast.png`** (= `_scene_live.png`, 4 of 32 placed). Read *Status — backdrop_v8*
below, then `PLATE_ASSEMBLY.md`. Serve the poster (`.claude/launch.json` → `living-past-static`,
port 4599) and open **`poster_mockup_live.html?only=1`** for the poster with type, and
**`plate_viewer.html`** for the bare plate — hold SPACE to A/B the cast off.

**Work the way that works.** Eric creates images in MJ, Claude reads the grid in the in-app browser
and argues the pick, Eric drops the file, Claude rebuilds and re-tunes. One thing at a time.

**Show the result.** Eric, 2026-07-29: *"from now on when you make adjustments you have to show me
the updated results so i know where we are."* Every render-affecting change gets an image put in
front of him — a crop of the change plus a step-back. Never a text-only report.

**Do not print.** *"no reason to print if it doesnt look right on the computer."*

---

## State

| | state |
|---|---|
| Plate | `backdrop_v8.png` — volcano monster, borderless glass windows, zoned ocean |
| Cast | **4 of 32**: CR01 rex (`rise`), CR03 Edmontosaurus, CR04 Ankylosaurus (`mid`), CR25 Mosasaurus (`deep`) |
| Windows | 4, all borderless: log cavity, Inoceramus shell bed at the strata/ocean contact, ash-fall, magma vent |
| Ocean | zoned by exponential extinction + a step at each SCOPE boundary; floor 14.5 → 8.1 |
| Front band | 4 micro plates — log, moss, puddle, mushrooms. Fern crozier + bark crevice still unshot |
| Research | 32 content records + 32 dossiers, all tracked |
| Encyclopedia | **32 pages live** in `pages/` from one template — `python3 tools/build_organism_pages.py` |
| Rank | ~8/10 (Eric, "i like where all this is at") |

## The loop, per organism

Eric, 2026-07-29: *"as we do it one by one we will put them in their respective pages."* So each
organism is finished across all outputs before the next one starts — build the atom, not the molecule
(SCOPE §10):

1. Eric fires the prompt in MJ (`python3 tools/lp_organism_prompt.py CR##`); Claude reads the grid in
   the in-app browser and argues the pick.
2. Knockout: `python3 tools/ps_isolate.py working/mj_pull/CR##_name.png` (Photoshop Select Subject,
   ~2 s, removes the floor plane that flood fill cannot reach).
3. **Check the knockout touches no frame edge.** A truncated plate silently corrupts scale — see CR04.
4. Place: `python3 tools/place_on_backdrop.py CR##:living_past/plates/organisms/CR##_isolated.png …`
5. Rebuild its page: `python3 tools/build_organism_pages.py CR##`
6. Show Eric the result — crop plus step-back.

## The queue, in order

1. **CR04 Ankylosaurus must be reshot.** Not an art note — a scale corruption. Its tail is
   truncated at the source frame edge, and `place_on_backdrop` sets on-canvas width to the animal's
   *true* length, so a head-to-mid-tail plate gets stretched to fill 8 m and renders oversized with
   wrong proportions. It also has no tail club and wears nodosaur-style conical spikes;
   *A. magniventris* had low flat osteoderms and a club as its signature feature.
   `python3 tools/lp_organism_prompt.py CR04`
2. **Keep the fauna coming.** Next best value: **CR06 Quetzalcoatlus** (the sky has 11 drawn
   silhouettes and no real animal), **CR02 Triceratops** (`mid`), **CR31 Inoceramus** (`abyss`, and
   it is the shell window's subject). Then the four `macro`-plane invertebrates — ant, beetle larva,
   earthworm, cicada nymph — which are the moat: drawn at 34× inside the log window, they are the
   only place a viewer sees Cretaceous anatomy at hand-lens scale.
3. **`land_lava_flow`** — the one plate the parked lava field is waiting on. Camera a few hundred
   metres back, dark crust dominant. The close-up fissure plates cannot do this job; see below.
4. **The annotation layer still does not exist.** Callout numerals tying scene positions to the 32
   field-guide entries, the Law #2 magnification note, the scale bar. Pure vector furniture, no
   renders needed, and it is what makes this a *scientific plate* rather than a landscape.
   `scalebar_audition.html` and `glyph_audition.html` already exist.
5. **Two confidence badges over-claim, and they print.** CR23 horseshoe crab is `well_documented` in
   the roster and `speculative` in its own research; CR24 Baculites is `well_documented` vs
   `reasonable_inference`. The research carries the claim ledgers and postdates the roster values, so
   the roster is very likely wrong. Needs Eric's decision — the build reports it and changes nothing.
   CR09's age range also disagrees ([69,66] roster vs [72,66] research), which feeds
   `roster_audit.py`'s Law #1 check.
6. **Seven records describe their own poster placement in prose**, and CR01/CR16 already disagree with
   current staging — CR01 says "crossing the foreground" and he now stands on the central rise. The
   durable fix is generating that sentence from `stage` data instead of hand-writing it.
7. **CR03's feathering vs. its confidence badge.** It is shaggy-feathered along the neck and back;
   hadrosaur skin impressions show scales, and the roster marks it `well_documented`. The badge and
   the reconstruction disagree. Disclosure is meant to be the trust signal.

## Composition, honestly

The hierarchy now works — rex leads, Mosasaurus answers, the monster explains why — and the size
cascade is doing the poster's central job: Edmontosaurus and Ankylosaurus sit on the *same* plane,
so 305 px against 203 px is nothing but the honest difference between 12 m and 8 m.

Still open: **the far right and the underground are empty of life.** Six underground organisms and
seven more marine ones have declared homes and no bodies. The `shore` plane has nobody at all, and
five organisms name the river margin as home while no plate contains a river.

## Status — `backdrop_v8` (2026-07-29)

- **Windows lost their borders.** `--windows glass` is the shipped mode: per-window organic aperture
  (`aperture()`), barrel bulge, dissolving rim, no brass. Eric: *"i like no borders, the transparency
  looks soo cool… it really pops when you step back."* It pops at distance because a dissolving edge
  discards high frequency, which distance eats anyway — what survives is the low-frequency signal of
  a patch at a different scale. A ruled border is the opposite: loud at two feet, gone at six.
- **The volcano is a monster, and it needed two blend passes.** Darken transfers only what is darker
  than the destination, and everything that makes the reshoot violent — lightning, incandescent
  crater, flank lava — is *brighter* than our sky. One pass would have composited the cone and
  deleted the eruption. It now gets darken for the rock plus a **warmth-keyed lighten** for the fire
  (fire runs R−B ≈ 200, the peach sky ≈ 70, which separates where no brightness threshold could).
- **The ocean got zones, not more room.** The waterline *is* the horizon — both measure y 0.30 — so
  it cannot rise on the right without breaking at the coast. What was missing was differentiation.
- **`rise` is a new plane.** Elevation decouples screen-y from distance: on flat ground higher means
  further, but an animal atop a raised feature is high because the *ground* is. Forcing the bluff
  onto the flat-ground curve made a 13 m titan 180 px.
- **Water blending reads depth, not plane distance.** `deep` at ×0.88 was getting 7% absorption, so a
  17 m animal over the abyss was crisper than its water. Now on the same extinction curve the column
  is graded with, so organism and ocean agree by construction.

## Traps re-learned this session

- **A source plate's geometry cannot be masked away.** Four attempts to use close-up fissure plates
  as mid-distance lava field failed identically. Lighten drops the black crust that makes lava
  legible; alpha keeps it and reads as a pale wedge. Same shape of failure as `ocean_shelf_dropoff`
  being a head-on wall. Harvest what a render nailed; shoot the geometry it missed.
- **Check what consumes a slot before blaming the render.** `geo_volcanic_ash` was written as a
  ground ash *bed* and MJ delivered exactly that; putting it in the sky was the error, not the plate.
- **A mask still partly opaque where its own canvas ends is a ruled edge.** Hit twice: `blob_mask` at
  a 7:1 aspect is ~18% opaque at its short-axis edges, and the micro band had no coastline hold-out
  at all, so the puddle composited into the sea.
- **Value, not hue, is what stops a plate seating.** A brilliant-white ash bed cannot be placed
  anywhere in an orange sunset world; no position and no tint fixed it. The prompt had asked for
  "pale grey".
- **A comment is not a mechanism.** "All stay on the land side" was false for two of four plates.

## Housekeeping

- **8 commits unpushed** at session end, on branch `add-carnotaurus-species` — a stale name now
  carrying Living Past work. Worth renaming or branching cleanly.
- `printify/CLAUDE.md` and `printify/printify_publisher.py` carry uncommitted edits from an earlier
  session — not this session's work, left alone deliberately.
- `.agents/`, `.codex/`, `AGENTS.md` are untracked config from another agent runtime. Left untracked
  pending a decision.
- Session close: `tools/end_session_daddy.sh`. LFS objects need a separate sync to the dev mirror.

_(Earlier launch prompts: `SESSION_2026-07-10.md`, `SESSION_2026-07-23.md`. The 2026-07-28 ten
criticisms and their fixes are in `PLATE_ASSEMBLY.md`.)_
