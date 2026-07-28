# The Living Past — Next Session Launch Prompt (updated 2026-07-28)

> **2026-07-28 — the ten ideas below were worked. Read this box first, then the launch prompt.**
>
> Done in code: #2 (knockout), #1 macro window, #3 sky triptych wiring, #5 volcano, #6 river
> margin, #7 burrow cutaway, #8 underwater passes, #9 waterline rebalance, #10 Photoshop pass.
> Current plate: `plates/backdrop_v4.png`.
>
> **The one finding that changes the plan: the knockout belongs in Photoshop.** Select Subject is
> scriptable (`tools/ps_isolate.py`), takes ~2 s a plate, and clears MJ's floor plane — which the
> flood fill *cannot* reach at any tolerance, because that plane is neither connected to the frame
> border nor tonally near it. That was the 4/10. See `PHOTOSHOP.md`.
>
> **What is left is generation, not code.** Fourteen plate prompts are written and every slot that
> consumes them is wired and tested with stand-ins:
>
> ```bash
> python3 tools/lp_plate_prompt.py --missing     # the 14 that still need shooting
> ```
>
> Shoot those, drop them into `plates/candidates/` under the exact slot names the tool prints, and
> re-run `build_backdrop.py` — no further code changes needed. Until then the build falls back to
> the old single sky and the two mirrored hollows.

> Paste the block below into a fresh session.

---

Vol V **backdrop**, still — the organism firehose stays on hold at 9/32. Read
`living_past/PLATE_ASSEMBLY.md`, `PHOTOSHOP.md` and `STAGING.md` first, then serve the poster
(`.claude/launch.json` → `living-past-static`, port 4599) and open `poster_mockup_live.html`.
That HTML is the poster of record; `poster_full.png` and `poster_draft_v1.png` are stale renders.

The code side of the backdrop is done. **This session is generation and composition**, in order:

1. **Shoot the 14 missing plates** — `python3 tools/lp_plate_prompt.py --missing`. Every slot that
   consumes them is wired and tested. One idea per prompt, never crammed. Nothing else unblocks
   as much.
2. **Isolate the fired organisms** with `tools/ps_isolate.py`, then re-place them. The knockout
   itself is solved; the backlog just hasn't been run.
3. **Compose the cast deliberately** — placement is currently a left-to-right walk from one x,
   which piles the animals into a single band.
4. **Then the criticisms below**, hardest first: the strata still read as ruled bars and the ocean
   still reads as a wall.

Personalization is OFF in MJ; keep it off. Keep every plate change reproducible in
`tools/build_backdrop.py`, and export `--layers` so the Photoshop handoff stays free.

---

## Why the backdrop earns a whole session (or two)

Once it's locked the project is roughly **half done**. Every downstream constant derives from it —
the terrace line, the headroom, where the three depth planes sit, where each habitat is. Organisms
composited against a plate that's still moving are wasted work, which is exactly why the firehose
is paused rather than grinding.

## Where things stand

| | state |
|---|---|
| Backdrop | `backdrop_v4.png` — 11 components + 11 more slots wired, awaiting renders |
| Micro habitats | **the emphasis** — 6 prompts written, 0 shot; build still falls back to 2 hollows |
| Strata | 12% of height, depth-graded — but still read as ruled bars (criticism #1) |
| Organisms on plate | knockout **solved** via `ps_isolate.py`; placement is not |
| Sky | 3-plate triptych wired, none shot; falls back to the single sunset plate |
| Volcano | **fixed** — own component, sits on the treeline at 2.3:1 |
| Firehose | **on hold**, 9/32 fired — the 14 plate prompts outrank it |
| Photoshop | scriptable, and now owns the knockout (`PHOTOSHOP.md`) |
| Poster preview | `poster_mockup_live.html` on :4599, reads `plates/_scene_live.png` |

## The three hero anchors — do not lose these

1. **T. rex** — far left, low worm's-eye camera, may break the title band.
2. **Mosasaurus** — far right, floating over the abyssal void. **The void is the scale weapon:**
   the ocean never gets shallower, only the soil does.
3. **The volcano** — geological monument on the horizon, plus the **asteroid whisper**: one faint
   cold point with a short streak, high in the empty top-left indigo.

## Ten criticisms of the poster as it stands (2026-07-28)

Written down because they are easier to see now than they will be next session.

1. **The strata read as flat ruled bars.** They are the accuracy moat and the most obviously
   generated thing on the plate. Every other edge is noise-warped; these are still stripes.
2. **The ocean is a wall, not a shelf.** The waterline runs almost straight down the coast — the
   drop-off never reads as receding away from the viewer, so the abyss is a blue panel, not depth.
3. **The cast stacks in one vertical band.** `place_on_backdrop.py` walks animals left-to-right
   from a single x, so three animals pile at the same place instead of being composed.
4. **The macro window has no answer.** One bright ruled rectangle in the bottom-left corner with
   nothing anywhere else in the composition rhyming with it. It reads as an accident.
5. **The left third is empty.** After the horizon dropped, the mid-left is an undifferentiated
   plain — a lot of the poster's most valuable real estate doing no work.
6. **Nothing is in the air.** No pterosaurs, no insects, no birds. The sky is scenery rather than
   habitat, which quietly contradicts the whole "every organism has a home" thesis.
7. **The volcano and the T. rex compete.** Both are large, high-contrast, upper-middle. The
   volcano is supposed to be a monument on the horizon, not a second subject.
8. **The title sits on the busiest part of the sky.** Top-right is where the cumulus and the ash
   plume are. Legibility is surviving on a text-shadow.
9. **One light, one weather, one hour.** Everything is warm sunset from the upper right. The plate
   never varies its mood, which flattens 3 million years of a world into one evening.
10. **The QR field guide is visually inert.** 32 identical small rows with placeholder thumbnails.
    It is the half of the poster a buyer actually reads and it currently looks like a spreadsheet.

## Ten ideas for next session (2026-07-28)

1. **Shoot the 14 plates.** `python3 tools/lp_plate_prompt.py --missing` — every slot that consumes
   them is already wired and tested. This is the highest-value hour available and needs no code.
2. **Run the whole cast through `ps_isolate.py`** and re-place all 9 fired organisms. The knockout
   is solved; the backlog of plates isn't isolated yet.
3. **Give the strata the same treatment as every other edge.** They're the last ruled lines on the
   plate. Warp the contacts, vary the tone per layer, let the litter genuinely interlock with them.
4. **Make the drop-off recede.** Curve the coastline in plan, not just in elevation, so the shelf
   turns away from the viewer and the abyss becomes distance rather than a blue panel.
5. **Compose the cast by hand.** Replace the left-to-right walk in `place_on_backdrop.py` with a
   per-organism (x, plane) in `volume_v.json`, so placement is data and reviewable like the roster.
6. **Put something in the air.** Quetzalcoatlus high and small, insects at macro scale near the
   window. It costs two plates and fixes the emptiest third of the composition.
7. **Answer the macro window.** Either a second, smaller window somewhere on the right, or a
   repeated brass rule in the furniture, so the one ruled box reads as a system.
8. **Move the title, or darken its patch.** Top-left indigo is the calm quarter and it's where the
   asteroid whisper already lives — the two could share a corner deliberately.
9. **Design the field guide as a page, not a table.** 32 rows of equal weight is a spreadsheet;
   vary scale, let the hero anchors take bigger cells, and use the confidence dots as real signal.
10. **Print one.** A 2.3:1 plate judged on a screen at 800px is being judged on nothing. One cheap
    poster print will surface more real problems than another session of pixel work.

---

_(Earlier launch prompts and the 2026-07-08 compositing proof are in `SESSION_2026-07-10.md`,
`SESSION_2026-07-23.md` and memory `project_living_past_composite_validated`.)_
