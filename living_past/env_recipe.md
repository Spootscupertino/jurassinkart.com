# The Living Past — environment / 4-zone recipe (build the world before the organisms)

The scene is built **before** any organism plate. Method (proven in
`experiment/scene_composite.psd`, memory `project_living_past_composite_validated`):

> **MJ for texture · PS gradients for the void.** A scripted gradient scaffold paints the
> four zones as flat color fields (the "void"); rich MJ base/detail plates are composited
> in and feathered; then organisms; then the one-world grade.

**Golden rule (memory):** lean on content, *generous on mood*. Strip invented strata/roots/
creatures from the prompts — MJ fakes those; we composite them accurately. But pour on
light, atmosphere, depth, scale, or MJ hands back a flat gray slab. Scale comes from the
**abyssal void + cliff height, never from lifting the camera** (aerial framing kills the
underwater cutaway). Keep `--iw` low so refs don't dominate the composition.

---

## Composition — 3 focal points + flat-land scale balance (locked 2026-07-10)

The scene balances around **three focal masses**, and scale is anchored on the flat land:

1. **T. rex** — stands on a **broad flat terrace** in the top-left. This is the scale anchor:
   at true scale (`scale_calc.py`) a 13 m T. rex is **~⅓ of the poster width** (585 px on the
   1800 px proof / ~3510 px on the 10800 px master). The current base-plate lip is only ~¼ the
   width it needs — hence base-plate **v2** widens the flat foreground. Everything else reads
   its size against the T. rex.
2. **Volcano** — the single background focal point, center-right on the horizon, smoking.
3. **Mosasaurus** — rises out of the **black abyss** (lower-right), ~17 m ≈ 43% of the width.

Study: `plates/_composition_study.png` (via `tools/compose_study.py`) — ghosted true-scale
silhouettes + the terrace footprint + the blocked geology. **Not final art**; it's the map.

**Status of the plate fixes:**
- ✅ **Black abyss (#6)** — real, in `tools/compose_proof.py`: the right ocean column
  depth-darkens so sunlit stays bright and twilight→deep fall to black. In `_proof_scene.png`.
- ◑ **Geology (#5)** — sedimentary **strata banding is done in code** (masked to the earth);
  the **organic bits (root web, burrow, buried egg clutch) are still to be composited** from
  the soil-cutaway plate / a dedicated MJ texture — never faked (env golden rule).
- ⬜ **Flat terrace** — needs base-plate **v2** regenerated (above); can't be faked in PIL.

---

## The four zones (spatial regions of the cross-section)

Coastline seam at **48%** of width (locked). Ground-and-water line splits above/below.

| # | Zone | §7 group | PS gradient (the void) — from `template/design_tokens.json` |
|---|---|---|---|
| 1 | **SKY / ABOVE** (top band, full width) | `10_SKY` | vertical: `#24325F → #6A5480 → #C66A34 → #F2A250 → #FFD488` (indigo→fire→gold) |
| 2 | **LAND + UNDERGROUND** (below ground line, left of 48%) | `30_LAND_MIDGROUND` + `50_UNDERGROUND` | vertical: terrain `#5c4a2a` → bedrock `#241A10` |
| 3 | **SHORELINE** (the 48% seam + shallows) | seam of `30`/`60` | sand `#CDB184` sheen over the land→sea transition, feathered |
| 4 | **OCEAN** (below water line, right of 48%) | `60_OCEAN_COLUMN` | vertical: sunlit `#6f8a84` → `#2f5560` → `#16313d` → abyss `#08151C` |

Depth-zone hairlines (SUNLIT/TWILIGHT/DEEP/FLOOR) fade in from the right edge (locked #8).
Asteroid whisper = faint cold point, top-left of zone 1 (locked #7).

---

## MJ plates to generate (build on your proven experiment prompts)

### 0 · Master base plate (does most of zones 2–4 in one shot — like your cliff plate)

**v5 / SURFACE-PLATE ARCHITECTURE (2026-07-27, Eric's call) — stop asking MJ for the whole world.**

Up to v4 the base plate tried to be sky + land + cutaway + ocean in a single MJ image. That fights
the moat: the strata are *code-built* from `geology_hellcreek.json` (accurate order and thickness),
and MJ has no business inventing them. It also caused every composition problem so far — the soil
ate half the canvas, and the terrace had no headroom.

**New split:** MJ generates only the **surface world** — sky, undulating plain, short coastline.
The accurate strata and the deep-ocean column are composited *underneath* it from plates we
already build. Geology stays code; texture and light stay MJ.

Two further requirements, both from Eric:
- **Undulating topography.** Rolling rises, hollows, terraces and benches — varied ground levels
  give organisms real places to stand and read as scale cues. A billiard-table plain gives neither.
- **Three hero anchors** (SCOPE §120–124, re-confirmed): T. rex far left on a worm's-eye camera,
  Mosasaurus far right over the abyss, volcano as the geological monument, asteroid-whisper in an
  empty top-left sky. Everything else flows around those three.

Note the abyss is **not** the thing to shrink. "Underground is too thick" means the *soil* band;
the ocean void is the scale weapon that sells the Mosasaurus and it keeps its vertical depth.

```
Wide panoramic view of a Late Cretaceous coastal plain seen from a low worm's-eye camera close
to the ground. Gently rolling undulating topography — low rises and shallow hollows, a step of
terraces, a small ridge, a sandy bench — giving many different ground levels and standing places,
the land receding from a near foreground through a clear middle distance to a hazed far treeline
and low blue hills. A single smoking volcano with a lit crater and a long drifting ash plume
stands on the horizon as the monument. On the right the plain ends in a short steep bluff where
the sea begins in sunlit turquoise shallows. A dramatic volcanic sunset sky fills the upper
third, deep indigo and empty in the top-left corner. The undulating ground fills the lower two
thirds of the frame and runs off the bottom edge. Flat horizon-level view, no cutaway, no
cross-section, no underground layers, nothing sliced open. Epic scale, cinematic god rays,
painterly realism, no animals, no people, no text --ar 3:2 --style raw
--no cross-section, cutaway, sliced ground, exposed soil layers, underground
```

**v3 (2026-07-27) — more land, shorter shoreline, real headroom over the terrace.**
Three faults in v2, all visible once organisms were actually placed on it:
1. *The beach is a long diagonal.* It sweeps from upper-left to mid-right and spends most of the
   land area on empty wet sand. Eric: "the shoreline might be a bit long."
2. *Not enough land.* Eight above-ground organisms have to share what's left after the beach takes
   its cut.
3. *No headroom.* The terrace sits so high in the frame that a T. rex placed on it is capped at
   10.4% of poster width by the poster's top trim — the animal is limited by the plate, not by
   any design decision.

The fix is one composition: push the coastline right, make the waterline run **steeply down the
frame instead of across it**, and drop the terrace to sit low with open sky above it.

```
Cross-section cutaway of an ancient coastal world seen through the glass wall of a giant
aquarium, split by the ground-and-water line. LEFT AND CENTRE: a vast broad flat open coastal
plain of bare ground and low scrub filling the left two thirds of the frame, a deep generous
expanse of level standing room, the flat ground sitting low in the frame with a tall open
expanse of sky and distant sea above it, its far edge cut away to reveal an eroded
earth-and-rock cliff in cross-section. RIGHT: the land ends abruptly in a short compact
shoreline, the waterline running steeply down the frame rather than sweeping across it, then
sunlit turquoise shallows falling fast to cold abyssal blue-black depths, a true dark plunge
into black in the lower-right corner. BACKGROUND: distant hazed shoreline and one smoking
volcano under a dramatic volcanic sunset. Epic scale, cinematic god rays, painterly realism,
no animals, no people, no text --ar 3:2 --style raw
```

**v2 (2026-07-10) — bakes in the flat T. rex terrace + the black abyss (see Composition below):**
```
Cross-section cutaway of an ancient coastal world seen through the glass wall of a giant
aquarium, split by the ground-and-water line. LEFT: a broad flat open coastal terrace of
bare ground and low scrub across the whole foreground — generous empty flat standing room —
its far edge cut away to reveal an eroded earth-and-rock cliff in cross-section. RIGHT:
sunlit turquoise shallows falling fast to cold abyssal blue-black depths, a true dark plunge
into black in the lower-right. BACKGROUND: distant hazed shoreline and one smoking volcano
under a dramatic volcanic sunset. Epic scale, cinematic god rays, painterly realism, low
horizon, no animals, no people, no text --ar 3:2 --style raw
```
_(low `--iw`; this is the workhorse — the seam and cliff carry the whole diorama. **v2 fixes:**
the left third must read as flat, open, standable ground before the cut — that's the T. rex
stage; the lower-right must already fall to black so we're not fighting a lit reef.)_

_v1 (original — kept for reference):_
```
Cross-section cutaway of an ancient coastal world seen through the glass wall of a giant
aquarium, split by the ground-and-water line: sunlit turquoise shallows on the right fading
to abyssal blue-black depths, an eroded earth-and-rock cliff on the left revealed in cross
section, distant hazed shoreline and a smoking volcano under a dramatic volcanic sunset,
epic scale, cinematic god rays, painterly realism, no animals, no text --ar 3:2 --style raw
```

### 1 · Sky tile → `10_SKY`
```
Dramatic volcanic-sunset sky, deep indigo fading down through violet, fiery orange and gold
at the horizon, epic backlit cumulus clouds, long god rays, a distant smoking volcano at
right with a drifting ash plume, faint hazed mountains, no ground, no animals, no text
--ar 3:2 --style raw
```

### 4a · Deep-ocean column tile → `60_OCEAN_COLUMN`
```
Deep ocean water column, sunlit turquoise at the top fading through teal to abyssal
blue-black, drifting marine-snow particulate, soft light shafts, immense sense of depth,
underwater, no creatures, no seafloor detail, no text --ar 2:3 --style raw
```

### 4b · Abyssal-void tile (the scale weapon) → `60_OCEAN_COLUMN`
```
Deep underwater camera looking out into vast open ocean, cold blue-black emptiness,
faint suspended particulate, a single distant shaft of light, overwhelming scale and
silence, no creatures, no text --ar 3:2 --style raw
```

### 2 · Soil / cliff-cutaway texture tile → `50_UNDERGROUND` (texture only!)
```
Extreme close cross-section of eroded earth and layered sedimentary rock, warm sunset-lit
cliff face, dry crumbling soil and pebbles, painterly realism, no roots, no burrows, no
animals, no text --ar 2:3 --style raw
```
_(roots, burrows, buried egg clutch, accurate strata lines = composited/painted in PS, not MJ.)_

### 3 · Shoreline / shallows tile → seam
```
Ancient coastline where land meets a calm turquoise sea, wet sand and shallow water, warm
low sunset light, gentle foam line, no animals, no text --ar 3:2 --style raw
```

---

## Assembly order (PS, scripted via osascript + jsx)
1. Build the **gradient void** scaffold (zones 1–4 as flat fields) — scriptable.
2. Composite the **master base plate**; align its waterline to the 48% seam.
3. Drop **detail tiles** into each zone; feather seams on BOTH axes (waterline = gradient
   mask; zone-to-zone = second gradient in Darken mode).
4. Paint/composite the **accurate** bits: soil strata lines, root web, burrow, buried clutch,
   depth-zone hairlines, volcano crater glow, asteroid whisper.
5. Only then place **organisms** (T. rex, etc.) at true scale (`scale_calc.py`).
6. Finish with the **`70_WORLD_GRADE`** one-light pass.

## Next action
Generate plate **0 (master base plate)** and **4b (abyssal void)** first — they set the
scale and mood the rest hangs on. Save to `living_past/plates/` (I can make the folder).
Then we scaffold the gradient void and start compositing.
