# The Living Past — how 32 organisms actually fit the scene

Two rules, both Eric's, that between them dissolve the "the cast doesn't fit" problem measured on
2026-07-27 (above-ground was **3.5x oversubscribed** on a single plane at 270 px/m).

## Rule 1 — per-group scale

There is no single world ruler. **Each stratum is scaled against its own reference organism**, so
the dinosaurs are true to each other and the soil fauna are true to each other — a millipede
sized against a beetle, not against a T. rex. That is the only way an ant and a tyrannosaur are
both legible on one sheet. Inside a group every true-size ratio is exact; the group as a whole
gets one multiplier. The poster states each band's ruler separately (Law #2).

Implemented in `tools/compose_scene.py --group-fit` and `tools/compose_poster.py`.

## Rule 2 — depth planes

Organisms are staged at **three distances**, not lined up on one ground line. The hero stalks from
afar, the herbivores graze in the middle distance, the small fast animals scatter far back. This
is the SCOPE §124 "size cascade," and it is what makes the arithmetic work:

| plane | scale | cast | width used | of land band |
|---|---|---|---|---|
| foreground (hero) | 1.00 | T. rex | 3510px | 68% |
| mid (grazing herd) | 0.55 | Triceratops, Edmontosaurus, Ankylosaurus | 4306px | 83% |
| far (scattered) | 0.30 | Dakotaraptor, Ornithomimus, Pachycephalosaurus, Quetzalcoatlus | 2025px | 39% |

All eight place with room to spare, and **no size is faked** — ratios stay exact within a plane;
the plane's multiplier is just distance, which is what perspective already means. The true-scale
promise is carried where a buyer actually checks it: the "Sense of scale" strip in the facts band
(human silhouette + Mosasaurus on a shared ruler).

This is also why the base plate needs **undulating topography** (v5, `env_recipe.md`) — rises,
hollows, terraces and benches give each plane a believable place to stand. A flat plain makes
three depth planes read as three pasted rows.

## The three hero anchors (SCOPE §120–124)

Everything flows around these; they are placed first and the cast arranges around them.

1. **T. rex** — far left, low worm's-eye camera, may break the title band.
2. **Mosasaurus** — far right, floating over the abyssal void. The void is the scale weapon, so
   the ocean keeps its full vertical depth even though the *soil* band gets thinner.
3. **Volcano** — the geological monument on the horizon, plus the asteroid-whisper as a single
   faint cold point in the empty top-left sky.

## Order of operations

Do **not** load organisms until the back plate is settled. The plate determines the terrace line,
the headroom, and where the three planes sit; every placement constant is derived from it, so
organisms placed against a plate that is about to change are wasted work.
