# Do we still need Photoshop?

Short answer: **not for assembly, yes for finishing — and the handoff is no longer hard.**

## ⭐ The experiment, run 2026-07-28 — and it moved the line

Idea #10 was "export the layer stack and do one real Photoshop pass, to find out what the code
pipeline genuinely can't do before committing to code for the finish." It was run against
`working/backdrop_layers_v4` (11 layers) and three real organism plates. Results, in order of how
much they changed the plan:

| test | result |
|---|---|
| **Select Subject on organism plates** | **Beats our knockout outright, and it is scriptable.** ~1.8-2.3 s per plate. |
| Load Files into Stack | Works exactly as claimed — 11 layers, alpha preserved, nothing to align. |
| Content-Aware Fill | Works. Synthesises replacement pixels; there is no numpy equivalent at all. |
| Curves adjustment layer via JSX | Failed (`"Make" is not currently available`). Non-destructive grading stays a hand step for now. |

**The headline is the knockout.** Our flood fill is geometric: it can only remove background that
is *connected to the frame border* and *tonally near it*. MJ's faint floor plane is neither — it is
continuous with the animal's own contact point and a different grey from the field — so no
tolerance clears it without also eating silhouette. That is the whole reason the composited
organisms scored 4/10, and it is not a tuning problem; it is a limit of the method.

Select Subject is an ML segmentation with no connectivity constraint. On all three plates it
removed the floor plane completely with the silhouette intact. See `tools/ps_isolate.py`.

**This also corrects a standing assumption.** `mj_recipe.md` recorded background removal as
"UI-only, not scriptable", and the isolate recipe was shaped around that. It is reachable from
JSX as `executeAction(stringIDToTypeID("autoCutout"))`, so the entire isolate step automates —
about a minute for all 32.

The one non-obvious requirement: a freshly opened PNG is a locked Background layer, and clearing
to transparency silently does nothing until `activeLayer.isBackgroundLayer = false`.

```bash
python3 tools/ps_isolate.py --check                     # is Photoshop reachable?
python3 tools/ps_isolate.py working/mj_pull/*.png       # knock out every pulled plate
```

Output carries a real alpha channel, and `compose_organism.isolate()` already prefers existing
alpha over flood-filling, so nothing downstream changes. The flood-fill path stays as the
no-Photoshop fallback.

## Why it stopped being hard

`build_backdrop.py --layers <dir>` writes every component as its **own full-canvas RGBA PNG**
with its mask already baked into the alpha:

```
10_land.png  20_sky.png  30_ocean.png  40_forest_floor.png
50_strata.png  60_micro_habitat_1.png  60_micro_habitat_2.png  70_asteroid_whisper.png
```

In Photoshop: **File > Scripts > Load Files into Stack**. Alphabetical order is the correct
stacking order by construction, and because each layer is full-canvas nothing needs aligning.
That rebuilds the exact composite as an editable stack with every mask preserved as transparency.

The thing that would have made this painful is handing over a flattened raster. We simply never do.

## What code should keep doing

- **Assembly and masking.** Noise-warped seams, blob masks, per-group scale, depth planes. All of
  it is deterministic, reproducible and versioned in git. Re-running after a component changes is
  one command; in Photoshop it would be an afternoon of manual re-masking.
- **The strata.** Layer order and thickness come from `geology_hellcreek.json`. That is the
  accuracy moat and it must stay generated, never hand-painted.
- **Placement.** Every organism's size derives from its true measurement through one ruler per
  group. Dragging things around by eye is exactly the "art gamble" the whole project avoids.

## What Photoshop is still for

- **Organic brushwork and retouch** — the knockout edges, blending a plate that fights the grade,
  hand-work on anything MJ botched. Established previously: mouse-driven PS is good at
  setup/composite/grade and bad at organic brushwork, so this is the human's hand, not Claude's.
- **The print master.** Final output is 10800x7200 at 300dpi, sRGB. The current pipeline works at
  3000px for speed; the real master gets assembled once, in PS, from upscaled components.
- **Non-destructive final grade** — adjustment layers beat a baked numpy grade when Eric wants to
  push it by eye.

## Recommendation

Keep composing in code until the layout is locked, then export layers **once** and finish in
Photoshop. Doing it the other way round — moving to PS now, while the composition is still
changing — means re-doing the manual work every time a component is re-harvested.
