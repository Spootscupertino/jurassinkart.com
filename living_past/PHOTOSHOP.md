# Do we still need Photoshop?

Short answer: **not for assembly, yes for finishing — and the handoff is no longer hard.**

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
