# The Living Past — Next Session Launch Prompt (updated 2026-07-29)

> Paste the block below into a fresh session.

---

Vol V backdrop. Plate of record is **`plates/backdrop_v7.png`** (committed `b595714`, copied to
`_scene_live.png`). Read `PLATE_ASSEMBLY.md` → *Status — backdrop_v5* first (it covers v5–v7), then
`STAGING.md`. Serve the poster (`.claude/launch.json` → `living-past-static`, port 4599) and open
**`plate_viewer.html`** — hold SPACE to A/B against v4 — and `poster_mockup_live.html?only=1`, F for
fullscreen.

**Work the way that worked.** Eric, 2026-07-29: *"we do our best work when i create the images in mj
and we knock things out one by one."* One plate at a time: Claude prints the prompt and what to look
for, Eric fires it, Claude reads the grid in the in-app browser and argues the pick, Eric drops the
file, Claude rebuilds and re-tunes the constants that plate touches. Ten plates landed that way in
one session. Do not batch six prompts and hope.

**Do not print anything.** Eric: *"no reason to print if it doesnt look right on the computer."*

---

## The list (Eric's, 2026-07-29)

1. **Volcano further into the left corner.** It sits at `VOLCANO_X = 0.108`. Note it is now
   darken-blended (its own pale sky drops out) so it can move without dragging a patch rectangle —
   but the two circles bracket it, so all three move together or the bracket breaks.
2. **Expand the Deccan idea and the magma.** See *The Deccan is half an idea* below.
3. **Blend the micro windows so they flow organically out of the poster.** Read the tension note
   below before softening anything — done naively this undoes criticism #4.
4. **The shells look off.** Answered below: the plate was generic when the roster already named
   what it should have been.
5. **Bring the ocean further up in the right corner** — more room for water-column layers, more
   room for the river delta, and possibly a freshwater window. `SEA_TOP = 0.145`; raising it trades
   against sky, so decide what the sky loses before moving it.

## Claude's additions

6. **Put organisms on it. This is the whole gap.** 32 staged, 0 placed. Nothing else on either list
   moves the number as much, and every item above is polishing a stage with no cast. The pipeline is
   ready end to end: `stage:{x,plane}` is in `volume_v.json`, `place_on_backdrop.py` reads it,
   `ps_isolate.py` does the knockout. Start with **CR01 T. rex** — it is the hero anchor, it is the
   only organism already isolated, and it will immediately expose whether the `fg` plane's ground
   line is right on v7.
7. **The eye has no path.** At a few feet the strongest object on the poster is the bottom-left
   window — furniture, not subject. A poster needs one thing that wins, one that answers it, and
   everything else subordinate. The intended spine is T. rex / Mosasaurus / volcano and none of
   them currently wins. This is diagnosable *only* at distance and only once #6 has started.
8. **Nothing occludes anything.** Every element sits inside its own band: sky, plain, litter,
   strata, water. Overlap is the cheapest depth cue there is and the plate has almost none. One
   frond crossing the mid-distance, the litter breaking over the waterline, a bird passing in front
   of the cone — each is worth more than another texture pass.
9. **The front band is one hue.** Amber log plus one mushroom cluster. Four micro slots remain and
   each brings a value the band does not have: `micro_moss_cushion` (saturated green),
   `micro_puddle_edge` (water, and a mirror that puts sky at ground level),
   `micro_fern_crozier` (the one vertical gesture in a horizontal band), `micro_bark_crevice`
   (vertical surface). Shoot moss and puddle first — they are the two biggest colour departures.
10. **The annotation layer does not exist yet.** Callout numerals tying the 32 scene positions to
    the 32 field-guide entries, the Law #2 magnification note, a scale bar. This is what makes it a
    *scientific plate* rather than a landscape with circles on it, and it is pure vector furniture —
    no renders needed. `scalebar_audition.html` and `glyph_audition.html` already exist.

---

## How 7.5 becomes 10

Not by fixing more things. The plate is at the point where the remaining defects are small and the
remaining *absences* are large. Three moves, in order, and they are worth roughly:

| move | worth | why |
|---|---|---|
| **The cast** (#6) | +1.5 | It is a stage. A stage with nobody on it cannot exceed ~8 no matter how good the stage is. Every argument the poster makes — true relative scale, every organism has a home, the confidence system — is currently unillustrated. |
| **Composition** (#7, #8) | +0.5 | Focal hierarchy and occlusion. Both become *possible* only once organisms exist, because the organisms are what will occlude and what will win. |
| **Annotation** (#10) | +0.5 | Turns a beautiful landscape into an instrument. It is also the cheapest half-point on the list — vector work, no renders. |

Eric's 1–5 and Claude's 9 are all real and all worth doing, but honestly they are the last 0.3
between them. **They are refinements of a stage.** Do them alongside the cast rather than instead of
it — the trap this session came closest to falling into was polishing the backdrop indefinitely
because the backdrop is the part that responds immediately.

---

## Notes on the specific items

### 3 · The window-blending tension — read before softening

The windows were built as **deliberate ruled instruments**, and the argument was explicit: every
other edge on the plate is noise-warped precisely so nothing reads as drawn, so the one clean edge
reads as an *instrument of the poster* rather than a compositing artefact. "Blend them so they flow
organically" is in direct tension with that. Softened naively — feathered frames, lowered opacity —
they stop reading as instruments and become smudges, and criticism #4 comes straight back.

The resolution is to **keep the frame crisp and let the content escape more**:

- More escape lobes per window. Each currently breaks its rule in exactly one place, at the top.
  Two or three breaks on different sides reads as something growing out of the frame rather than
  one deliberate spill.
- Vignette the content *inside* the frame so it falls off toward its own edges before the rule,
  rather than meeting the brass at full strength.
- Let a neighbour cross a window — litter overlapping the bottom-left frame, a bird passing the
  volcano circles. Occlusion (see #8) is what makes something sit *in* a scene.
- Consider a second, thinner concentric rule on the circles — an optic has more than one edge.

### 4 · The shells

The intent was that the seafloor is **accumulated death** — shell hash is what marine rock actually
is, the same accuracy-moat argument as the strata. It is not reading, and unread intent is failed
intent.

The fix is not a better generic shell bed. The roster already names the answer: **CR31 Inoceramus**,
a bivalve that reached 1–2 m. A seafloor paved with metre-wide clam shells is accurate, dramatic,
legible at poster scale, *and* gives a roster organism its declared home — which generic shell hash
does not. Reshoot `ocean_shell_beds` around Inoceramus specifically, or cut the pass.

### 2 · The Deccan is half an idea

v7 carries a sulphate-aerosol veil high in the sky (`build_backdrop.py` §4d2) — the second killer,
present as the reason the sunset looks wrong. It pairs with the asteroid whisper by *kind*: the
asteroid is a point you can see, the Deccan is a stain you cannot locate.

What would finish it:

- The magma window is currently a fissure in crusted lava, which is already Deccan-style rather
  than arc-style. Eric ruled (2026-07-29) that broad Late-Cretaceous geology beats strict Montana
  locality, so this is sanctioned — but the poster should then *say* it, in the annotation layer.
- A third geological circle would close the cascade: **magma → ash → bentonite bed → the section**.
  The first two exist; the bed and the section are on the plate but not linked to the circles.
  Linking them is annotation work (#10), not a render.
- The two whispers want to be findable *together*. Right now they are on opposite sides of the sky
  with nothing connecting them.

### 5 · Raising the ocean

`SEA_TOP = 0.145`, `COAST_X = 0.55`, `COAST_TILT = 0.115`, and the seafloor profile is `SEAFLOOR`.
Raising the sea buys water-column height and costs sky — and the sky just got the cumulus and glow
plates, so decide what it gives up. The freshwater window is a good idea and cheap: `river_margin_macro`
is already a written, wired, unshot slot, and **five organisms** (CR17 Borealosuchus, CR18 Basilemys,
CR19 gar, CR20 guitarfish ray, CR21 Champsosaurus) declare the river margin as their home.

---

## State

| | state |
|---|---|
| Plate | `backdrop_v7.png` — 10 plates in, 4 macro windows, 25-layer PS export in `working/` |
| Windows | log cavity (rect), shell beds (rect), volcanic ash + magma vent (circles, bracketing the cone) |
| Strata | eroded outcrop: pinch/swell, fault, gullies, 2 ravines cut through. Still only 12% of height |
| Ocean | code-built seafloor; coastline tilts; the head-on wall plate is retired to its shallows only |
| Sky | cumulus + horizon glow live; `sky_high_cirrus` still unshot |
| Weather | procedural rain cell; `sky_squall_cell` unshot |
| Organisms | **0 of 32 placed** — staging is data in `volume_v.json`, 9 planes |
| Plates | 11 slots left: `lp_plate_prompt.py --missing` |
| Rank | 7.5/10 (was 6.5 at v5) |

## Rules that keep being re-learned

- **A source plate's geometry cannot be masked away.** Three sessions of feathering `ocean_shelf_dropoff`
  never fixed it, because it *is* a head-on wall. Harvest the region a render nailed; build the
  geometry it missed.
- **Interruption beats undulation.** Wavier strata did nothing; gullies and ravines that cross
  contacts killed the bar read.
- **Check what consumes a slot before blaming the render.** One "failed" ocean run was correct for
  the slot's new job — the prompt was written against the slot's old one.
- **"Shelf edge" is a subject noun, and MJ answers subject nouns with a hero close-up.** Recession
  is a camera position. Lead with where the camera is.
- **Everything in `build_backdrop.py` is canvas fractions, never pixels.** The micro table was the
  last pixel holdout and it silently broke when the canvas changed height.

---

_(Earlier launch prompts: `SESSION_2026-07-10.md`, `SESSION_2026-07-23.md`. The 2026-07-28 ten
criticisms and their fixes are in `PLATE_ASSEMBLY.md`.)_
