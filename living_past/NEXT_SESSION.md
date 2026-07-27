# The Living Past — Next Session Launch Prompt (updated 2026-07-27)

> Paste the block below into a fresh session.

---

Focus this session entirely on the Vol V **backdrop** — the organism firehose stays on hold at
9/32. Read `living_past/PLATE_ASSEMBLY.md`, `STAGING.md` and `DAY_PLAN.md` first, then look at
`plates/backdrop_v3.png` and `plates/poster_draft_v1.png` to see where we ended up.

Priorities, in order:

1. **Push the zoomed-in micro habitats.** They're the best thing we unlocked and they get the
   emphasis. Build more piece by piece in MJ — one idea per prompt, never crammed — and give them
   more of the front of the plate.
2. **Fix the sky and the volcano** at the wide 3000x1300 scene ratio: the volcano crops high and
   the sky wants a calmer plate. Harvest regions, don't re-roll a mega-prompt.
3. **Rebalance the composition** — it went bottom-heavy once the litter and soil grew.
4. **Fix the organism knockout edges.** MJ's faint floor plane survives on some plates and reads
   as a pale bar under the feet. A global tolerance isn't the answer. We're happy to knock out all
   32 individually if that's what maximum detail costs — it's only 32 items.

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
| Backdrop | strong — `backdrop_v3.png`, 9 harvested components, noise-warped seams |
| Micro habitats | **the unlocked feature** — push hard |
| Strata | 50% → ~12% of height, depth-graded, non-uniform |
| Organisms on plate | ~4/10 — knockout edges are the flaw |
| Sky / volcano | need work at the wide ratio |
| Firehose | **on hold**, 9/32 fired |
| Photoshop | no longer a hard transition (`--layers`) |

## The three hero anchors — do not lose these

1. **T. rex** — far left, low worm's-eye camera, may break the title band.
2. **Mosasaurus** — far right, floating over the abyssal void. **The void is the scale weapon:**
   the ocean never gets shallower, only the soil does.
3. **The volcano** — geological monument on the horizon, plus the **asteroid whisper**: one faint
   cold point with a short streak, high in the empty top-left indigo.

## Ten ideas for next session

1. **A whole micro-habitat set, one prompt each** — rotting-log interior, moss cushion, unfurling
   fern crozier, mushroom cluster, puddle edge, bark crevice. Six plates blended along the front,
   and the cm-scale organisms finally have real places to live.
2. **A "macro window" treatment** — let one micro habitat break its own frame and run larger than
   life in the bottom-left corner, so the poster explicitly teaches that scale changes there. It
   pairs with the Law-#2 enlargement note the poster already owes the reader.
3. **Per-plate knockout tolerance**, auto-derived by sampling each plate's own corner colours
   rather than one global number. Probably fixes most of the 4/10 organism problem outright.
4. **Shoot the sky as three plates** (high cirrus / mid cumulus / horizon glow) and stack them,
   instead of hunting for one sky that does everything.
5. **Reposition the volcano for the wide slot** — it wants to sit lower and further right now the
   scene is 2.3:1, and it should overlap the treeline rather than float above it.
6. **A river-margin close-up plate.** Five organisms live there and it's currently just distant
   braided sand. It deserves the macro treatment the forest floor got.
7. **A burrow cutaway with an occupant chamber** that visibly connects the surface litter to the
   soil ribbon — tying the two habitat systems into one continuous world.
8. **Underwater detail passes** — algae fringe on the shelf, shell beds on the seafloor, marine
   snow in the abyss. The ocean is currently the emptiest quarter of the plate.
9. **Rebalance by moving the waterline, not by shrinking the litter.** Raising the sea and
   dropping the horizon may fix the bottom-heaviness without giving up any front detail.
10. **Export the layer stack and do one real Photoshop pass** on backdrop_v3, to find out what the
    code pipeline genuinely can't do before committing to code for the finish. Cheap experiment,
    settles the question with evidence instead of opinion.

---

_(Earlier launch prompts and the 2026-07-08 compositing proof are in `SESSION_2026-07-10.md`,
`SESSION_2026-07-23.md` and memory `project_living_past_composite_validated`.)_
