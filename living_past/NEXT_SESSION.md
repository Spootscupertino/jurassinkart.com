# The Living Past — Next Session Launch Prompt

> Paste this into a fresh session to pick up where we left off.

---

We're building **"The Living Past — Sections of Ancient Earth,"** a collectible museum-grade poster series (Volume V = Late Cretaceous first). Read `living_past/SCOPE.md` (esp. §4 design constants and §13 the locked composition). Composition is locked.

## Last session (2026-07-08) — we proved the production workflow

Instead of locking typography, we ran a live de-risking experiment: **can these posters actually be built by compositing separately-generated Midjourney pieces in Photoshop, or does it look pasted?** Answer, decisively: **yes, it works.** Everything is in memory `project_living_past_composite_validated` and in `living_past/experiment/`:

- `scene_composite.psd` — the capstone: a full four-zone cross-section (volcano + sunset sky, root-laced soil cutaway, beach, deep ocean with god rays, and a mosasaur) all composited from separate MJ plates into one believable world.
- `rex_composite.psd` — a T. rex composited onto a clifftop base plate to scale.

**What we learned (carry this forward):**
- **Drive Photoshop by script** — `osascript` running an ExtendScript `.jsx`, exporting a JPEG preview after each step to judge. Fast, cheap, repeatable; this is the real tooling seed.
- **Environment = ONE rich MJ base plate.** The prompt phrase *"cross-section cutaway … as if seen through the glass wall of a giant aquarium, split by the ground-and-water line"* reliably produces the above/below diorama.
- **Modular method:** clean base plate + hero DETAIL tiles posted into each zone (deep-water column, soil cutaway), seams feathered on BOTH axes (waterline = gradient mask; zone-to-zone = second gradient in Darken mode).
- **Organism knockout:** Photoshop **Remove Background** (contextual task-bar button — UI only, NOT scriptable), then scripted place / scale / shadow / clipped grade. Organism plates need "full body, all limbs, isolated on solid background, no shadow, matched light."
- **Prompt craft — lean on content, generous on mood.** Strip invented/fake-scientific subjects (MJ fakes strata/roots/creatures — we composite those in accurately), but pour on light/atmosphere/scale or MJ returns a flat gray slab. Scale comes from the **abyssal void + cliff height, not from lifting the camera** (aerial framing kills the underwater cutaway).
- **Still missing for the real build:** true-scale placement — everything was eyeballed. The meter-grid + auto-size calculator (SCOPE §6) is the first real code.

## Progress — 2026-07-09: 19 of the 20 goals done

The whole 20-goal list was worked end-to-end. **19 are complete; only #16 remains** (it
needs your hands in Midjourney/Photoshop). Every design decision is frozen in `SCOPE.md`
§4/§6/§13, each backed by a rendered audition.

**Design locks #1–10 (auditions rendered):**
- #1–4 Type: **Cinzel** display · **EB Garamond** body · **Optima** utility + 7-role scale + brass labels +.22em (`type_audition.html`; fonts in `fonts/`).
- #5 **Flat brass** (brushed only on large elements) `brass_audition.html`.
- #6 Confidence badge = one brass dot, 3 fill levels.
- #7 Asteroid whisper **IN** (faint top-left point).
- #8 Depth-zone lines **fade from the right edge** `zoneline_audition.html`.
- #9 Seven brass glyphs → `glyphs.svg` (`glyph_audition.html`).
- #10 Metre-ruled scale key, human + largest titan, human never in scene `scalebar_audition.html`.

**Build #11–15:**
- #11 §4 **fully frozen** → `template/` (`design_tokens.json` → `tokens.css`; PSD skeleton `tools/build_template_psd.jsx`).
- #12 **`tools/scale_calc.py`** — px_per_m=270, true-scale + micro-organism rule.
- #13/#18 **`volume_v.json`** — 32 orgs, roster LOCKED to a **tight 66 Ma community** (68–66 Ma); `tools/roster_audit.py` = 0 temporal fails, 8/8/8/8. (Swapped 7 out-of-interval taxa; `needsRefs:true` entries await sourced copy.)
- #14 Redirect layer `redirect/` (gen + map + Astro endpoint).
- #15 Astro page template `astro/[volume]/[slug].astro` + CSS (staged, live site untouched).

**Prove/business #17,19,20:**
- #17 MJ isolate recipe `mj_recipe.md` + `tools/lp_organism_prompt.py`.
- #19 Web-page experience `organism_page.html` (rendered).
- #20 `PRINTIFY_PLAN.md` — 24×36 landscape poster confirmed ready; **flags:** canvas retired (→ poster-only), landscape auto-adds a mug (add exception), API key may need re-auth.

## The one open goal: #16 — T. rex vertical slice
Everything is wired; only the MJ generation + PS placement are yours. Follow
**`VERTICAL_SLICE_CR01.md`** — run `python3 tools/lp_organism_prompt.py CR01`, generate in
MJ, knockout, size to 3510 px, place, and time it. That per-unit time × 32 = the Volume-V estimate.

Nothing else blocks the build. After #16, the sequence is: produce all 32 (SCOPE §10) →
`70_WORLD_GRADE` + export → publish (drafts, user-gated).
