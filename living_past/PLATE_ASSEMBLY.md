# The Living Past — the back plate is assembled, not generated

**Eric, 2026-07-27:** *"ultimately you end up taking a little from this and a little from that,
it's unrealistic to think MJ will just hit everything — it's the whole point of how we're
operating."*

Stop hunting for the one perfect base plate. No single MJ render will land the volcano, the
terraces, the coastline, the abyss and the sky all at once, and waiting for it burns GPU minutes
on near-misses. The plate is **harvested**: each render contributes the one region it nailed, and
those regions are composited. This is the same thesis already proven for organisms — MJ supplies
texture and light, code and Photoshop supply structure.

## The topography is derived from the roster, not from taste

**Eric, 2026-07-27:** *"the topography should be created to support the organisms."*

This inverts how we were working. The plate used to be designed as a landscape, and the cast was
jammed into whatever ground happened to exist — which is exactly why six underground organisms had
nowhere legible to be. Now every organism declares the terrain feature it needs, and the plate
prompt is written **from that checklist**: `tools/habitat_map.py`.

```bash
python3 tools/habitat_map.py            # checklist grouped by depth plane
python3 tools/habitat_map.py --prompt   # clauses to paste into the plate prompt
python3 tools/habitat_map.py --unmet    # features nothing needs — cut them
```

All 32 now have a declared home. Running it immediately caught a hole no amount of art direction
would have: **five organisms need a freshwater river margin** (Borealosuchus, Basilemys, the gar,
the guitarfish ray, Champsosaurus) and **no plate generated so far contained a river at all**.
It also flagged `treeline` and `drop_off` as decorative — nothing in the roster needs them.

### Two more principles from this session

- **Forest floor comes all the way to the front.** Pulling leaf litter to the bottom edge at macro
  scale gives the cm-scale organisms (ant 3px, beetle larva 8px at true scale) a place to be drawn
  *huge* — the near end of the depth cascade. It solves the legibility-floor problem that the
  underground band could not.
- **Blend several litter plates, never repeat one.** Eric: *"using multiple of those zoomed-in
  forest floor images will also make it look more diverse and lifelike."* One texture tiled across
  the front edge reads as wallpaper. Three different ones (dry litter, wet swamp, sandy bank)
  blended along the bottom read as a world.

## Component slots

| slot | source | status |
|---|---|---|
| Sky + volcano monument + ash plume | MJ — `candidates/v5_volcano_terraces.png` | **have** |
| Undulating land: terraces, benches, rises | MJ — `candidates/v5_volcano_terraces.png` | **have** |
| Short steep coastline / bluff | MJ — `candidates/v3_bigland_steepbluff.png` | **have** |
| Turquoise shallows | MJ — either candidate | have |
| **Strata cutaway (11 Hell Creek layers)** | **code** — `composite_strata.py` from `geology_hellcreek.json` | **have — never MJ** |
| Deep-ocean column + abyssal void | MJ — `plates/deep_ocean_column.png`, `plates/abyssal_void.png` | have |
| Asteroid whisper (top-left) | code — single faint point + streak | have |
| Volcano monument, positionable | MJ — cropped from `candidates/v5_volcano_terraces.png` | **have** |
| Micro-habitat set ×6 | MJ — `lp_plate_prompt.py --group micro` | wired, **to shoot** |
| Sky triptych ×3 (cirrus / cumulus / glow) | MJ — `--group sky` | wired, **to shoot** |
| River margin close-up | MJ — `--group river` | wired, **to shoot** |
| Burrow cutaway + occupant chamber | MJ — `--group burrow` | wired, **to shoot** |
| Underwater passes ×3 (algae / shells / snow) | MJ — `--group ocean` | wired, **to shoot** |
| Macro windows ×2 + registration ticks | code — `build_backdrop.py`, `MACRO_WINS` | **have** |
| **Seafloor: shelf → break → abyssal plain** | **code** — `build_backdrop.py`, `SEAFLOOR` | **have** |
| Receding drop-off | MJ — `ocean_shelf_recede` | wired, **to shoot** |
| Squall cell | MJ — `sky_squall_cell` | wired, **to shoot** (code stand-in) |
| Left bench (mid-distance terrace) | MJ — `land_left_bench` | wired, **to shoot** |
| Macro insect swarm | MJ — `air_insect_swarm` | wired, **to shoot** |
| Air traffic (distant azhdarchids) | code — `build_backdrop.py`, `pterosaur()` | **have** |

The strata row is the moat. MJ must never invent layer order or thickness; it only supplies the
per-lithology texture tiles listed in `geology_hellcreek.json → mjTexture`.

## Status — `backdrop_v5` (2026-07-29) — the ten criticisms

Built by the same `tools/build_backdrop.py`. Every one of the 2026-07-28 criticisms is addressed in
code; four of them additionally want a plate that is now written and wired (see the slot table).

**#1 The strata were ruled bars.** `render_strata_organic.py` was rewritten. The first pass had
fixed the *texture* and left the *geometry* alone — eleven full-width bands of constant thickness —
and no texture rescues that, because what the eye reads as "drawn" is the parallel constant-thickness
stripe, not the pixels inside it. Now: per-column **pinch and swell** (channels get the most, marker
beds the least, and column totals renormalise so a swell here thins a bed there); **one shared
structural roll plus regional dip**, because real beds roll together rather than waving
independently; **a normal fault** with drag; **differential weathering** driven by a per-lithology
`RESIST` table, lit from the upper right so sandstones stand as ledges and the bentonite cuts back
into a shadowed notch — which is how you find the ash bed in the field, so the recession is
accuracy; **talus** shed by every soft bed, draping over and interrupting the contacts below;
**six gullies**, the only feature that crosses contacts; and **two ravines that cut clean through**,
returned in the ribbon's own alpha, so the section is spurs rather than a band. A band with holes in
it cannot read as a bar.

**#2 The ocean was a wall.** Two causes, and the second one is the lesson. First, the coastline ran
straight down the frame — `organic_mask` gained a `tilt` so the shore leans and its plan position
changes with distance. Second and much larger: **`ocean_shelf_dropoff.png` is itself a sheer wall
seen head-on.** No mask, grade or feather turns that into a receding shelf, because the geometry is
in the pixels — which is the harvesting thesis restated as a warning. The build now takes only the
sunlit shallows out of that render and builds the drop-off in code: `SEAFLOOR` runs a profile from
the shore across a shelf, over a break, down a slope and out onto an abyssal plain, textured from
the same Fox Hills and Pierre tiles the cutaway uses (the section already said those beds continue
offshore) and seen through depth-dependent water absorption. The void is deep because you can watch
the floor fall away into it.

**#3 The cast stacked in one band.** Placement is now data: every organism carries
`stage: {x, plane}` in `volume_v.json`, reviewable exactly like the roster. `place_on_backdrop.py`
reads it, and grew six planes beyond the original three — `air`, `shore`, `shelf`, `deep`, `abyss`,
`soil`, `macro` — because an ocean animal has no ground line and a 1 cm ant has no legible size on
any land plane. Ground planes get a contact shadow; swimming and flying ones do not.

**#4 The macro window had no answer.** There are two windows now, deliberately unequal, both
breaking their frame at the top edge — same grammar, different sentence — plus **brass registration
ticks at the four corners**, so the ruled line is established as the poster's vocabulary before
either window uses it. The windows also gained a *function*: the four cm-scale organisms are staged
on the `macro` plane, inside the big one. The window is where they live.

**#5 / #9 The left third was empty; one light, one hour.** Same hole, same fix: a **rain cell** over
the mid-left plain — dark base, leaning curtain of fallout, the ground beneath robbed of the warm
key, and a lit gap immediately to its right to read against. The world grade also stopped being a
pure vertical ramp, which is not a key light at all; it now falls off across the frame as well as
down it, so the far left is genuinely in the blue end of the evening.

**#6 Nothing in the air.** Eleven azhdarchid silhouettes, drawn not harvested (`pterosaur()`).
At 20–90 px an MJ plate spends a thousand pixels on something the viewer resolves as a shape, and
MJ's pterosaurs are wrong in exactly the ways this project exists to avoid — a silhouette can be
*right*: long narrow wings cranked forward at the wrist, neck as long as the body, stub tail. They
are weighted left, so they also work on #5.

**#7 The volcano competed with the T. rex.** What puts a landmark behind a subject is not size, it
is air — distance eats contrast long before it eats scale. The cone is composited through the same
aerial perspective the far plain gets (`VOLCANO_HAZE`, `VOLCANO_FLATTEN`) and only slightly trimmed.

**#8 The title sat on the busiest sky.** It moves to the top-left indigo and the plate meets it
halfway with a soft, off-centre darkening where the type lands, so legibility comes from the art
rather than a drop shadow. The asteroid whisper moved right and down to share that corner
deliberately rather than collide with the words.

**#10 The field guide was inert.** `poster_mockup_live.html`: every entry now carries its **type
glyph** from `glyphs.svg` (the set has mapped 1:1 onto the roster's `type` field since 2026-07-09
and was never used) — 32 varying marks instead of 32 identical grey squares, for no new art. Each
section leads with its position-1 organism in a double-height cell, which drops two of the three
hero anchors out for free. Column heads carry the section's documented count, so the confidence dots
resolve into a statistic. The per-item QR stays (SCOPE §8) but drops in contrast.

### Two traps worth keeping

> **A source plate's geometry cannot be masked away.** `ocean_shelf_dropoff` was a beautiful render
> of the wrong thing, and three sessions of feathering it were three sessions of trying to fix
> composition with alpha. Harvest the region it nailed; build the geometry it missed.

> **`noise()` is isotropic and cannot make rain.** It is built from square grids, so asking it for
> vertical streaks returns speckle that composites as sensor grain. Falling water is white noise
> across the wind and correlated along the fall — one row of noise smeared down the frame, then
> sheared. Any anisotropic feature (rain, rills, fibres, grain) needs the same treatment.

## Status — `backdrop_v4` (2026-07-28)

Built by the same `tools/build_backdrop.py`. Five changes, all reproducible, all parameterised at
the top of the file:

- **The volcano is its own harvested component** (`25_volcano`), no longer whatever the land plate
  happened to contain. It was cropping high and floating because the land plate is 3:2 and the
  scene slot is 2.3:1, so its horizon furniture landed near the top edge. Now cropped from
  `v5_volcano_terraces` — the render that actually nailed the cone and plume — and placed at
  `VOLCANO_X/Y/W`, lower and further right, deliberately **overlapping the treeline**.
- **Rebalanced from the top, not the bottom.** The plate went bottom-heavy, but the litter is the
  best thing on it, so the fix came from the other end: `SEA_TOP` 0.20 → 0.145 (the sea comes up)
  and `LAND_BIAS` 0.34 (a vertical crop bias on the land plate that drops the horizon and opens the
  sky). Not one pixel of front detail was given up.
- **The macro window** (`62/63`) — a brass-ruled box bottom-left that one micro habitat runs out
  of, larger than life. It is the only ruled line on the plate, and that is the point: everything
  else is noise-warped so nothing reads as drawn, so the one deliberate straight edge reads as an
  instrument of the poster. The Law #2 caption belongs to the type layer, not here.
- **Eleven new component slots wired**, each optional-if-missing so the build runs before the
  renders land: the six-plate micro-habitat set, the three-plate sky, the river margin, the burrow
  cutaway, and three underwater detail passes. Prompts: `tools/lp_plate_prompt.py`.
- **The knockout moved to Photoshop.** See `PHOTOSHOP.md` — the flood fill cannot reach MJ's floor
  plane by construction, and Select Subject can, scriptably.

Two masking traps re-learned while building the macro window, both the *same* trap as the
`blob_mask` softness lesson below and worth stating as a general law:

> **Any mask that is still partly opaque where its own canvas ends composites as a ruled
> rectangle.** The window's overflow lobe was ~16% opaque at the corner and read as a pale slab
> hanging over the corner. The fix is to force the mask to zero inside its own bounds — but the
> falloff distance must stop exactly at the feature it is protecting, because a falloff wide enough
> to be safe also flattens the lobe's peak, and then the rule came back intact and the window
> stopped teaching anything.

## Superseded — `plates/backdrop_v2.png` (2026-07-27)

Nine components. Adds over v1: dedicated sunset sky, the asteroid whisper, root traces and
burrows blended into the soil, and the micro-fauna hollow. **Personalization is now OFF** — every
render before this carried `--profile uxjzh3u`, pushing all of them toward one learned look,
which is the opposite of what harvesting diverse components needs.

Three masking lessons, all learned the hard way and all now encoded in the tool:

1. **One-axis ramps are only right for edges that genuinely run edge-to-edge** (horizon,
   coastline, waterline). For an *inserted patch* — burrows, a hollow — use `blob_mask`, which
   falls off on every side. A rectangle of detail dropped into the plate announces itself instantly.
2. **`blob_mask` softness must be < 1.0** or the blob is still partly opaque at its own box
   corners. At 1.15 it left visible vertical steps in the sky.
3. **Lighten/darken blending only works when the source is tonally extreme against the target.**
   It transfers pale roots and dark burrow mouths beautifully — their backing dirt vanishes into
   the strata. It ghosted an entire second landscape into the sky when used on a whole daylit
   volcano plate. When the source isn't extreme, mask the *destination* instead: the sky is now
   held out of the volcano's airspace rather than the volcano being pasted back over it.

Still open: the strata read pale against the litter and want their own grade; the litter/soil
contact is the softest-focus area of the plate.

## Superseded — `plates/backdrop_v1.png` (2026-07-27)

First assembled draft, built by `tools/build_backdrop.py` from 5 harvested renders. What landed:
angled plain with the braided river, volcano monument, rocky promontory giving real elevation,
macro forest floor at the front-left, shelf breaking into the abyss, strata at **21% of height
(was 50%)**.

**The seams are the whole job.** A straight alpha ramp still reads as a pasted rectangle however
wide you feather it, because nothing in nature has a ruled edge. Every mask is therefore
*noise-warped* — the transition line itself wanders. Three edges all reference the **same
wandering coastline seed (17)** so the ocean, the litter and the soil agree with each other
instead of crossing.

Known rough edges, in priority order for the next pass:
1. The deep-water column's top edge on the right is still close to a straight horizontal.
2. The shelf-to-deep transition inside the ocean region needs the same organic treatment.
3. Strata read a little pale and flat against the litter above them; wants a grade pass.
4. No burrows / root traces / detail passes yet (Eric's next item).

## Assembly order (bottom to top)

1. Deep-ocean column and abyssal void on the right, at full vertical depth. **The void is the
   scale weapon for the Mosasaurus — it does not get thinner.**
2. Strata ribbon along the bottom-left, thin. Eric: the *soil* is what was eating the canvas
   (50% of scene height for 2 of 10 layers in the spec). Target ~20%.
3. Surface world on top: undulating plain, coastline, sky, volcano.
4. Asteroid whisper in the empty top-left indigo.

## Why undulation matters

Rolling ground is not decoration. It creates the **standing places** for the three depth planes in
[STAGING.md](./STAGING.md) — a foreground hollow for the T. rex, a mid-distance bench for the
grazing herd, a far rise for scattered small animals. On a billiard-table plain the three planes
read as three pasted rows.

## Rule

**Do not place organisms until this plate is settled.** Every placement constant — terrace line,
headroom, plane positions — derives from it. Organisms composited against a plate that is about
to change are wasted work.
