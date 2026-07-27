# The Living Past — unattended day plan (2026-07-27)

What Claude runs while Eric is at work, in order, with the decision points marked. Everything
here is proven end-to-end today except where flagged.

## Standing rules for the run

- **MJ is the storage.** No selection, no rating, no upscaling during the run. Tile index 0 is
  taken as the default pull; Eric re-picks later from the library.
- **No screenshots inside the firing loop** — that is where Claude usage actually goes.
- **Personalization is OFF** (turned off 2026-07-27 with Eric's go-ahead). Renders should carry
  no `--profile`. If one appears in the metadata, the toggle got re-enabled — turn it back off.
- Anything needing an `--sref` / `--oref` attachment is **skipped and logged**, not guessed at.

## Top priority added 2026-07-27 (Eric, in session)

**A. Rebuild the scene on `base_plate_v3.png`.** The v3 land plate is downloaded and approved
(variant B, tile 0): far more land, and a short steep shoreline instead of v2's long diagonal
beach. It is *not* wired in yet — `compose_proof.py` and `composite_strata.py` carry geometry
constants calibrated to v2 (`WATER 0.50`, `COAST 0.62`, `CLIFF_TOP 0.49`) and v3's composition
is different, so those must be re-derived against the new plate before the strata will clad the
cliff correctly. Do this before placing any more organisms — everything downstream depends on it.

**B. `poster_full.png` is stale, not broken.** Eric flagged that the labelled earth layers were
missing from the poster. They were never missing from the pipeline: `composite_strata.py` clads
the cliff with all 11 Hell Creek layers, and `poster_mockup.html` builds the poster from
`plates/_proof_scene.png`. `poster_full.png` was simply a one-off render made *before* the strata
were promoted. Re-rendering the mockup restores them — verified in session. **`poster_full.png`
should be regenerated from the mockup, never hand-edited**, or this desync recurs.

## REVISED PRIORITY (Eric, in session)

> *"it's not worth loading all our organisms until the back pane is unbelievable."*

**The firehose is paused at 9/32 and stays paused.** Organisms are not the bottleneck; the back
plate is. Every placement constant — terrace line, headroom, the three depth planes — derives from
the plate, so organisms composited now would be thrown away. Work the plate instead:

**DONE in session:** plate assembly pipeline (`build_backdrop.py`), organic strata
(`render_strata_organic.py`), habitat-driven terrain (`habitat_map.py`), soil thinned 50% -> 21%,
`plates/backdrop_v1.png` built from 10 harvested components.

Remaining, in order:

**DONE:** seams fixed, detail passes in (roots + burrows), grade pass in, sky + volcano +
asteroid whisper in, micro-fauna hollow in, personalization turned OFF. -> `backdrop_v2.png`.

**DONE (session 2):** micro habitats doubled + enlarged (Eric's favourite part), strata cut to
~12% and depth-graded like the ocean, layer export for Photoshop, depth planes coded
(`place_on_backdrop.py`), full poster rough draft with QR furniture ->
`plates/poster_draft_v1.png`, `plates/backdrop_v3.png`.

1. **Knockout edges on the organisms.** Still the most visible flaw — MJ's faint floor plane
   survives on some plates and reads as a pale bar under the feet. Tolerance is at 78; the real
   fix is probably a per-plate tolerance or a proper matte, not a global number.
2. **Sky and volcano.** Eric flagged both. At the 3000x1300 scene ratio the volcano gets cropped
   high — it needs repositioning for the wide slot, and the sky wants a calmer plate.
3. **Composition is bottom-heavy** — litter + soil take a lot of the wide slot now. Rebalance.
4. Then the organism sequence below.

## Sequence (resumes after the plate is settled)

1. **Fire the remaining 23 organisms** — `tools/mj_firehose.py next` → form_input → send →
   `mj_firehose.py fired`. Batches of 4, ~3 min apart. ~25 min of wall time.
2. **Let the queue drain** (~2 min after the last batch).
3. **Pull one tile per organism** — Chrome download button per job, `~/Downloads` →
   `working/mj_pull/<ID>.png`. See MJ_FIREHOSE.md for why only Chrome works.
4. **Knock out + composite per stratum** — `tools/compose_scene.py --group-fit` for each of the
   four bands, so each stratum can be judged on its own ruler.
5. **Render the full poster** — `tools/compose_poster.py` with the whole cast onto
   `plates/poster_full.png`.
6. **Write a review sheet** — per organism: did it come back whole, was the background clean,
   did the tail/wing/appendage clip. Anything that failed goes on a requeue list rather than
   being silently re-fired.

## Open decisions parked for Eric (do NOT resolve these unattended)

- **Where the micro-fauna actually live.** `backdrop_v2` now has two candidate homes: the macro
  forest floor at the front, and the soil ribbon with its burrows. Both are legible. Which one
  each of CR11-CR14 belongs to is a design call, not a technical one.
- **Above-ground headroom** is no longer capped by the plate the way it was on `poster_full.png`
  — the new backdrop gives the land real vertical room. Re-measure before assuming the old
  10.4% ceiling still applies.

RESOLVED in session: `--profile` (now off); soil band thickness (50% -> 21%); whether the roster
fits (yes, via per-group scale + depth planes, see STAGING.md).

## Known recipe gaps still open

- Tail clipping on long bodies — Rule 8 added today, **not yet validated on a live run**. The
  first ocean batch (Mosasaurus, Prognathodon, Xiphactinus) is the real test.
- MJ still renders a faint floor plane despite `--no ground, cast shadow`. The border-seeded
  knockout absorbs it, but a truly flat plate would be better.
