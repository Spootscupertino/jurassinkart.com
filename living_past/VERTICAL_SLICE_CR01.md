# The Living Past — T. rex vertical slice runbook (#16)

Take ONE organism (T. rex, `CR01`) the entire distance to prove the atom and time it
(SCOPE §12 step 4). Everything except the two hands-on creative steps is wired and ready.

| Step | Command / action | Status |
|---|---|---|
| 1. Record | `CR01` in `living_past/volume_v.json` | ✅ done |
| 2. MJ prompt | `python3 tools/lp_organism_prompt.py CR01` → paste into Midjourney, add your `--ar 3:2 --ow` + refs | ⏳ **you, in MJ** |
| 3. Knockout | Photoshop *Remove Background* on the isolate plate (UI-only) | ⏳ you, in PS |
| 4. Size | `python3 tools/scale_calc.py "12-13 m"` → **3510 px** wide on the master (32% of poster) | ✅ ready |
| 5. Place | Drop into `40_ORGANISMS/ABOVE/CR01_trex`, snap to 3510 px, scripted shadow+grade (osascript+jsx) | ⏳ you, in PS |
| 6. Page | Astro template already renders `/late-cretaceous/tyrannosaurus-rex`; set `image` path in the record | ✅ ready |
| 7. QR | `jrk.art/x/CR01` → 301 to the page (`living_past/redirect/`) | ✅ ready |

**Time it:** note wall-clock from step 2 to a finished, placed, page-live T. rex. That
per-unit time × 32 is the Volume-V build estimate — the number that tells us if the atom
is cheap enough to scale. Log the result here when done.

Only steps 2–3 and 5 need you; the rest is one command each.
