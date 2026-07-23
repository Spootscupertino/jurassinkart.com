# THE LIVING PAST — Sections of Ancient Earth
## Master Scope (v1)

> **Status:** Planning / pre-build. Nothing gets generated or built until this document is whole and the design constants (§4) are locked.
> **Rule of the room:** we build piece by piece, in order. No jumping back and forth. If a decision isn't in this doc, we decide it *here* before touching a canvas.
> **First volume:** Late Cretaceous (chosen for popularity + SEO + warm-start on existing dinosaur assets).

---

## 0. The one-paragraph pitch

A collectible series of museum-grade panoramic posters, each a scientifically accurate cross-section of an entire ancient world — sky to seafloor — with 32 organisms rendered individually at maximum quality and composited to true relative scale. Every organism carries a QR code that routes to an informational page on jurassinkart.com. The poster sells the website; the website sells the poster. Nobody else has built this.

---

## 1. North Star & Laws

**North Star:** *"If I could stand there for five minutes, what would Earth actually have looked like?"* We don't illustrate extinct animals — we reconstruct living worlds.

**Law #1 — Living worlds, not animals.** Every organism belongs to the same geologic interval and functions as part of one community. Temporal guardrail: an organism's age range must overlap the volume's interval or it doesn't belong.

**Law #2 — True to scale within a size tier.** Charismatic macro-organisms are sized honestly against each other in the scene (measured, not eyeballed). Micro-organisms (ants, plankton, worms) are drawn enlarged for visibility, with their *true size stated in the key*. Ocean-depth and root-depth are compressed and labeled, not literal. This law is stated openly on the poster — the honesty is a selling point.

**Law #3 — The scene is precious; the page is infinite.** Anything that doesn't *have* to be on the poster gets demoted to the web page. Protect the immersion of the scene above all.

**Law #4 — Accuracy is the wonder.** Wonder comes from truth, not exaggeration. The confidence level of every reconstruction is disclosed. Conquering the hard/botched anatomy others skip is the moat.

---

## 2. The series system (what makes 7 posters one story)

- **Wordmark:** "THE LIVING PAST · Sections of Ancient Earth" — identical treatment on every volume.
- **Connective tissue #1 — the timeline:** the same thin deep-time line on every poster; only the "you are here" pin moves. Line all seven up and the pin marches across 4.6 billion years.
- **Connective tissue #2 — the paleo-globe:** the same unrolled-globe element; continents drift volume to volume. Seven globes = one continental dance.
- **Collectibility:** volume badge ("Volume ▓ of VII"), consistent template, "collect them all."
- **Planned volumes (order TBD after V1 proves the pipeline):** Cambrian · Age of Fishes · Coal Forests · Rise of Reptiles · Age of Dinosaurs · Age of Mammals · (future). **We start with Late Cretaceous regardless of numbering.**

---

## 3. The poster template (layout)

Horizontal panoramic. Print target: **24×36" landscape @ 300dpi (~10800×7200px).** All "furniture" lives at top and bottom; the **scene bleeds full to the left and right edges** (no side panels — borderless window = maximum immersion).

**Vertical zones, top to bottom:**
1. **Title band** (top) — wordmark left, volume + era right ("LATE CRETACEOUS · 66 million years ago").
2. **The scene** (dominant) — full-bleed cross-section: sky/canopy → land surface → roots/soil/burrows on the left; shoreline → sunlit → twilight → deep → seafloor on the right. Elegant in-scene callout numbers on each organism.
3. **The data band** (bottom, "the sacrifice zone") — the paleo-globe + the 4×8 field guide of QR cards.
4. **The timeline strip** (very bottom, thin, full width) — deep-time line, "you are here" pin, K–Pg extinction mark just past it.

**The field guide:** 4 sections × 8 items = **32 organisms**, sections mapped to the ecological strata: **ABOVE GROUND / UNDERGROUND / SHORELINE / OCEAN.** 8-wide × 4-row card grid at the bottom; each card ≈ thumbnail + name + stats + confidence badge + a ~1" QR code (large enough to scan reliably at reading distance).

**Icon legend:** small type glyphs (Land Animal / Flying Reptile / Marine Reptile / Fish / Invertebrate / Plant / Mammal) so `type` reads at a glance. **Glyph set designed & LOCKED 2026-07-09** (audition: `glyph_audition.html`; reusable symbols: `glyphs.svg`): seven **brass silhouettes**, single consistent weight, common baseline. Invertebrate = ammonite spiral (catch-all for ammonites/belemnites/crustaceans/insects); fungi rides under Plant. Vector polish (land-animal vs mammal distinction, marine-reptile paddle) happens when furniture is redrawn for the real template (#11). Placement = facts-band legend row.

---

## 4. Design constants to LOCK before any art (frame · font · border · grid)

> These are set *once* and inherited by all seven volumes. This section must be fully filled and frozen before the first image is generated. **[bracketed] = decision still open, to lock in the design pass.**

- **Canvas — LOCKED 2026-07-09:** 24×36" landscape, 300dpi (**10800×7200 px**), **sRGB** (Printify/POD pipeline is sRGB — Adobe RGB would be down-converted and shift), bleed **0.125"** (37.5 px each edge → full bleed 10875×7275), safe margin **0.25"** (75 px). All furniture inside safe margin; scene bleeds to trim.
- **Master scale grid — LOCKED 2026-07-09** (calculator in `tools/scale_calc.py`, #12): the scene depicts **≈40 m of true horizontal world width** across the full 10800 px live area → **px_per_m = 270** (the single constant every organism's on-canvas size derives from). Vertical uses the same 270 px/m for surface giants; root-depth and ocean-depth are **compressed on labeled rulers** (not literal — stated on the poster per Law #2). Grid lives as a locked hidden guide layer. Re-derived per volume from that volume's widest titan.
- **Outer border / frame — LOCKED 2026-07-09:** **none.** Scene bleeds full to left/right/top edges (borderless window = max immersion, §3). Bottom furniture sits on the "fade to depths" gradient, no keyline, no museum mat (§13).
- **Zone dividers — LOCKED 2026-07-09:** **none.** Title floats on sky; scene→data and data→timeline transitions are gradient fades, not ruled lines (§13 "fade to depths"). Only exception: the hairline **above the facts band** already in the mockup (`#b98f4e44`) is allowed as the single faint furniture rule.
- **Typography — LOCKED 2026-07-09** (audition: `living_past/type_audition.html`):
  - **Display / wordmark / stratum headers / callout numerals: Cinzel** (weight 600). Inscriptional Roman-capital face — the museum-monument voice. Currently the free SIL-OFL Cinzel (`living_past/fonts/`); may be swapped for licensed **Trajan Pro** later with zero layout change (same metrics role).
  - **Body serif — blurb + common name + scientific name (italic): EB Garamond** (regular + italic). Free/OFL; renders identically on the Astro web side.
  - **Utility sans — labels · field-guide stats · eyebrows · timeline · depth-zone labels: Optima.** Humanist sans drawn from Roman inscriptions → shares Cinzel's DNA (one-family feel across three roles).
  - **Two weights max** (Cinzel 600 + Optima/Garamond regular). **Locked type scale** (the 7 fixed roles):
    | Role | Face | Size* | Tracking | Case |
    |---|---|---|---|---|
    | Era title | Cinzel 600 | 30 | +.14em | caps |
    | Era date / subtitle | Optima | 12 | +.26em | caps |
    | Stratum header | Cinzel 600 | 14 | +.20em | caps |
    | Common name | EB Garamond italic | 17 | 0 | title |
    | Scientific name | EB Garamond italic | 13 | 0 | title |
    | Stats line | Optima | 12.5 | +.03em | sentence |
    | Callout numeral | Cinzel 600 | 20 | 0 | — |

    *px at the mockup's 1180px poster width; re-expressed as pt on the 24×36" master at template-build (#11).
  - **Brass furniture labels** (stratum heads, panel titles, legend): **Optima, all-caps, +.22em** — engraved-plate spacing, verified legible down to ~0.5cqw print size. Numerals stay Cinzel to tie back to the title.
- **Color system — LOCKED 2026-07-09** (from §13 palette): furniture depths bedrock `#241A10` → abyss `#08151C`; type ink ivory `#F6ECD4` / `#EDE3CE`, muted `#A99C7F`; brass `#B98F4E` base / `#D8B57A` highlight; sunset stops `#24325F → #6A5480 → #C66A34 → #F2A250 → #FFD488`. Confidence badge = one brass color at 3 fill levels (see below). Strata accent tints derive from the four stratum grounds (above=warm terrain, under=bedrock brown, shore=sand `#CDB184`, ocean=teal→abyss).
- **Brass finish — LOCKED 2026-07-09** (audition: `brass_audition.html`): **flat brass** for all small/repeated furniture (confidence dots, per-card rules, callout numerals, QR frames) — highlight `#D8B57A`, base `#B98F4E`. Texture on these just becomes noise/print-banding at true size. A subtle **brushed-metal sheen is allowed only on large brass elements** (master-QR frame, confidence-key plate) as a Photoshop layer-style at build time — not a template constant.
- **Callout number style — LOCKED 2026-07-09:** **circled numeral** — thin brass ring (`#D8B57A`, ~1.3px @ mockup scale) on a near-black fill (`#0b0d0e`), Cinzel 600 ivory numeral (`#E9D7AC`). Sits on the organism in-scene; ties to the field-guide card `id`.
- **Confidence badge — LOCKED 2026-07-09:** one brass dot at **three fill levels**, always with a 1px brass ring so all three read as the same element on one scale:
  - **Filled** brass dot = **Well-documented**
  - **Half** brass dot (left half filled) = **Reasonable inference**
  - **Open** ring (no fill) = **Speculative**
  Legend wording matches §5 exactly (Well-documented / Reasonable inference / Speculative). Appears on both the poster card and the web page. Colors: `#B98F4E` fill, `#B98F4E` ring.
- **QR spec — LOCKED 2026-07-09:** per-card QR **~0.5"** (field-guide "fine print", §13), master QR **~1"** (facts band). **Error-correction level H** (30% — robust at small print size and allows minor tinting). Quiet zone **≥4 modules**. **Encodes the stable ID-redirect** (`jrk.art/x/<id>`), never a page URL (§8). Corner/eye style: standard square eyes. **Scan-reliability gate:** modules must clear a contrast check at true 0.5" print — default is dark modules (`#0d0f10`) on a small ivory quiet-zone tile; brass tint only if a printed scan test passes. (Mockup renders brass-on-dark for look; production validates before lock.)
- **Ocean depth-zone lines — LOCKED 2026-07-09** (audition: `zoneline_audition.html`): **thin brass hairlines that fade in only from the right edge** and dissolve before crossing the open water, with small Optima all-caps labels (SUNLIT / TWILIGHT / DEEP / OCEAN FLOOR) at the right margin. Keeps the accuracy ruler legible where depth is read, without turning the immersive void into an infographic — the marine mirror of the painterly soil strata. (Mockup uses bold dashed lines as a diagram; painted poster uses the fade.)
- **Timeline style — LOCKED 2026-07-09:** **warped / non-linear, explicitly labeled "not to scale"** (recent eras get more room so they're legible; honesty per Law #2). Thin brass line, tick marks at era boundaries, **"you are here" pin** = brass triangle, **K–Pg extinction** = red ✕ (`#C0442F`) just past the pin. Same line on all seven volumes; only the pin moves (§2 connective tissue #1).
- **Globe style — LOCKED 2026-07-09:** **interrupted / peeled projection** (the "unrolled globe", §2 connective tissue #2). Continents drift volume→volume. Land fill brass-brown (`#6F5A34`), sea dark teal (`#0F1A1F`), scene-location **pin = brass dot**. Curl treatment = subtle rounded-rectangle plate as in the mockup.

Deliverable of the design pass: a **blank locked template** (empty PSD + matching Astro theme tokens) with all of the above baked in, ready to receive art.

**§4 FULLY FROZEN 2026-07-09.** Deliverable built in `living_past/template/`: `design_tokens.json` (single source of truth) → `tokens.css` (via `gen_tokens_css.py`); PSD skeleton builder at `tools/build_template_psd.jsx` (run in Photoshop, save as `template/The_Living_Past_V5_template.psd`). No open brackets remain.

---

## 5. The organism data model (the spine)

One record per organism, entered once, feeds **three outputs**: the poster card, the web page, and the reusable asset library. Stored as **one JSON file per volume** (32 entries); Astro reads it to auto-build pages. SQLite (`dino_art.db`) stays for logging/analytics only.

**Fields:**
- **Identity/routing:** `id` (permanent, e.g. `CR14` — the callout number, key position, QR target, page handle; never changes) · `slug` (pretty URL, may change) · `section` (above/underground/shoreline/ocean) · `position` (1–8).
- **Naming:** `scientificName` (italic) · `commonName` · `pronunciation` (page only).
- **Field-guide facts:** `type` · `size` (dual metric/imperial) · `ageRange` (must overlap volume) · `diet` · `habitat`.
- **Web-page body:** `blurb` · `funFacts[]` · `distribution` · `notes`.
- **Integrity:** `confidence` (Well-documented / Reasonable inference / Speculative) · `references[]`.
- **Production:** `image` (isolated asset path) · `status` (generated → placed → page-built).

**Confidence is shown**, not hidden — a small badge on card + page. No competitor admits uncertainty; we make it a trust signal.

---

## 6. The scale system

- **Locked horizon** across the full width = the master ruler (same height every volume).
- **Continuous foreground baseline** = the "you are standing here" plane.
- **Composition = two titans + a cascade + a geological anchor:**
  - Titan 1 (land): T. rex, far left, low camera / worm's-eye, allowed to break the title band.
  - Titan 2 (marine): Mosasaurus (~17 m), far right, floating over the abyss (the void is the scale weapon).
  - **Third anchor = geological, not animal** (volcano / mountain / river / **asteroid-as-whisper**). It recedes, gives the eye a monument, and makes all organic life feel small. For the Late Cretaceous volume: a faint asteroid in the sky as the poster's quiet gut-punch, echoing the K–Pg mark on the timeline. (Final geological choice made at compose time.)
  - **Size cascade** between the titans (micro → anchor → mid → distant hazed herd → mountains) so the *world* reads as vast, not just the heroes.
- **Vertical rulers:** root depth (10 m+) and ocean depth zones (to ~4,000 m) dwarf surface giants — the underrated, under-served scale axis.
- **Human-silhouette scale key — LOCKED 2026-07-09** (audition: `scalebar_audition.html`): a horizontal **metre-ruled "Sense of scale" strip** in the facts band — a 1.8 m human silhouette + the volume's **largest single organism** drawn to true scale on a shared ruler (V-Late-Cretaceous: Mosasaurus at 17 m, "nearly ten people nose to tail"). Two full titans overlap on one ruler, so use one dramatic true-scale reference, not both. Brass silhouettes on the dark ground, labels EB Garamond italic. **The human silhouette lives only in the key — never in the scene** (no anachronistic human in the ancient world). Silhouette sizing comes from the #12 meter-grid calculator.
- **Continuous eye-path** (pterosaur flock arc / shoreline curve / raking light) so the panorama reads as one traveling shot.
- **Meter-grid + auto-size calculator (first real code):** from each record's `size`, compute the exact on-canvas pixel dimensions. Scale becomes an engineering spec, not an art gamble — the core advantage Model B has over any one-shot AI image. **BUILT 2026-07-09: `tools/scale_calc.py`** — reads `px_per_m` from `design_tokens.json`, parses size strings (ranges, `ws` wingspan, cm/m), returns true-scale px + enforces the Law-#2 micro-organism rule (enlarge <~22 cm, report true size + factor for the key). CLI `--demo`/`--roster`; importable `compute_size()`.

---

## 7. The Photoshop layer / group structure (build order)

Estimated **150–250 grouped layers.** The template *is* the group structure — locked before art so we build top group to bottom group without backtracking. Every asset lands in a pre-named home.

**Top-level groups (back to front):**
1. `00_GUIDES` — meter grid, horizon, zone guides, safe/bleed (locked, hidden).
2. `10_SKY` — gradient, clouds, haze, sun/light source, **asteroid whisper**.
3. `20_BACKGROUND` — mountains, distant volcano, hazed herds, horizon atmosphere.
4. `30_LAND_MIDGROUND` — land plane, plants (each conifer/cycad/fern its own asset for scale-truth), water surface.
5. `40_ORGANISMS` — 32 organisms, **~2–3 layers each** (creature + contact shadow + clipped grade), sub-grouped by strata: `ABOVE / UNDER / SHORE / OCEAN`.
6. `50_UNDERGROUND` — soil strata, root web, burrows, fossilization-in-progress, cutaway egg.
7. `60_OCEAN_COLUMN` — depth gradient, light shafts, particulate, seafloor bed, per-zone grade.
8. `70_WORLD_GRADE` — the unifying "one world, one light" pass that defeats the collage look. **A real production stage, not an afterthought** — this is what stops 32 independently-generated assets from looking pasted.
9. `80_FURNITURE` — all vector, fully separate: title, timeline, globe, 32 cards, QR codes, callout numbers, legends, badges, credits. Kept vector so a date fix or reprint never touches the art.

**Naming convention:** `<group#>_<ZONE>/<id>_<commonName>` (e.g. `40_ORGANISMS/ABOVE/CR01_trex`). Strict, or 200 layers becomes unmanageable by layer 60.

---

## 8. The QR + redirect system

- **Never point a QR at a page URL.** Print is forever. Codes encode a **stable, ID-based redirect** we own (e.g. `jrk.art/x/CR14`); the redirect table maps `id → current page`. Restructure the site freely; printed codes never die.
- **Per-item codes** (32) — the magic is "scan *this* animal." Plus one **master QR** (title band/corner) → the volume's digital companion / store, for people who won't scan 32 things.
- **Analytics:** because we own the redirect layer, scan data tells us which organisms are popular → which single-species prints and which next volume to make.

---

## 9. The web-page system

- **Astro**, one templated page per organism, auto-built from the volume JSON (§5). 32 pages/volume, 224 across the series = an SEO paleo-encyclopedia no competitor has.
- Each page: hero asset (reuse the MJ isolate), full field-guide data, `blurb`/`funFacts`/`distribution`/`notes`, confidence badge, **and a "buy this print / buy the poster" CTA** (closes the flywheel).
- Content demoted here from the poster: "Still with us today" survivors panel, deep credits, references, extended anatomy.
- The page is where "maximum interactive viewing pleasure" lives — the poster stays a still, timeless window; the phone is the living layer.

---

## 10. The production pipeline (per organism)

1. **Generate** the organism in Midjourney — maximal descriptive prompting aimed at *one isolated subject* on a clean/knockout-friendly background, max quality, distinct POV per species (brand voice). All prompt-craft firepower on one creature at a time.
2. **Record** — fill the data record (§5); this spawns the page + QR automatically.
3. **Size** — run the isolate through the meter-grid calculator → exact canvas dimensions.
4. **Place** — drop into its pre-named Photoshop group (§7), snap to computed size.
5. **Page** — Astro builds the page from the record; QR wired to the redirect.
6. Repeat ×32, then `70_WORLD_GRADE`, then export.

**The atom is one organism, fully finished across all outputs.** Build the atom before the molecule.

---

## 11. The asset library (long-term moat)

Every organism is a reusable asset with full metadata + the isolated image. Feeds future posters, books, the website, and educational tools. Sourcing/vetting handled by existing agents (`source-hunter`, `ref-curator`, `license-auditor`). This library compounds across all seven volumes.

---

## 12. Build sequence (the order we actually work — no backtracking)

1. **Lock §4 design constants** → produce the blank locked template (empty PSD + Astro theme tokens). *Nothing before this.*
2. **Build the meter-grid + auto-size calculator** (§6) — first code.
3. **Stand up the redirect layer + Astro page template** (§8, §9) — empty but live.
4. **Vertical-slice experiment:** take ONE organism (T. rex hero) the entire distance — MJ isolate → record → size → place → page + QR. Prove the atom; measure time-per-unit; find problems while they're cheap.
5. **Finalize the organism roster** — survey a large candidate list, start with the popular/important, enforce Law #1 (interval) and the 4×8 strata balance.
6. **Produce all 32** through the pipeline (§10).
7. **`70_WORLD_GRADE` + export** the print master.
8. **Publish** — site pages live, Printify large-format products (drafts, user-gated to Etsy).
9. **Retro**, then template the learnings into Volume 2.

---

## 13. Design pass — locked from the v1–v9 mockup (2026-07-08)

The full poster template was mocked end-to-end in HTML/SVG: **`living_past/dummy_v9.html`** (open in a browser to see it). Composition is essentially locked; **typography is the next pass.**

**Locked layout**
- No series wordmark on the poster face (minimal text = max immersion). Only `LATE CRETACEOUS` + `145–66 million years ago` (full-period date), top-right, in light ivory ink over the sky.
- Sky bleeds to the very top; the title floats on it. Top-left deliberately **empty** for the hero / geological drama.
- Scene ≈ **65%** of poster height (verified to true 24×36" scale); furniture ≈ 35%.
- Bottom stack: (a) **field-guide index** = 4 vertical columns, one per stratum (ABOVE GROUND / UNDERGROUND / SHORELINE / OCEAN), 8 entries each, sized to true ~0.5" QR scale = elegant "fine print"; (b) **full-width facts band** = paleo-globe + Fast Facts + "This World" note + Confidence key + master QR; (c) thin **deep-time timeline** baseline (you-are-here pin + K–Pg mark).
- **Series colophon** "The Living Past · No. V" sits discreetly in the facts band (off the artwork, on for collectors).

**Locked "fade to depths" (no divider)**
- The scene dissolves at the bottom into its own depths — bedrock-brown (land) → abyssal blue-black (ocean). The index sits on that darkness; the facts band uses a matching horizontal gradient. No wooden frame, no flat black.

**Locked scene composition**
- Awe **volcanic-sunset** sky: indigo → fire-orange → gold, epic lit clouds, god rays, distant hazed mountains.
- **Geological third anchor = volcano** (lit crater + drifting plume). **Asteroid-whisper LOCKED IN (2026-07-09):** a single faint, cold point of light with a short streak high in the empty top-left indigo sky — subtle enough to miss until you know, echoing the K–Pg timeline mark and the facts-band blurb. Not a competing monument; a whisper.
- Raised horizon → **thick soil cutaway**: topsoil band, 3 wavy strata, deep root systems, burrow, buried egg clutch, pebbles.
- **Deep ocean** with over-exaggerated **depth-zone lines** (SUNLIT / TWILIGHT / DEEP / OCEAN FLOOR) — the marine mirror of the soil strata; every species placed at true depth. Light shafts, particulate, seafloor crinoids.
- **Coastline at ~48%**; land flows into beach + shallows (no hard seam).
- **Two titans**: T. rex hero descending a hill (far left, breaks the horizon); Mosasaurus in the deep water column (right). Size cascade between.

**Concrete palette (from the mockup — candidate lock for §4)**
- Brass accent: `#B98F4E` / `#D8B57A` — rules, numbers, confidence badges, QR.
- Furniture ink: ivory `#F6ECD4` / `#EDE3CE`; muted `#A99C7F`.
- Depths: bedrock `#241A10`, abyss `#08151C`. Sunset stops: `#24325F → #6A5480 → #C66A34 → #F2A250 → #FFD488`.
- Confidence badge = brass dot fill level: filled (well-documented) / half (reasonable) / open (speculative).

**Still open (next session, in priority order)**
1. ~~Typography lock~~ **DONE 2026-07-09** → Cinzel (display) · EB Garamond (body) · Optima (utility). See §4 for the locked scale + brass spacing; audition in `type_audition.html`. Mockup `dummy_v9.html` updated to the locked system.
2. ~~Brass expression: flat vs. aged wood-grain/metal texture~~ **DONE 2026-07-09** → flat brass base; subtle brushed sheen reserved for large elements only. See §4.
3. ~~Zone-line subtlety on the painted version~~ **DONE 2026-07-09** → hairlines fade from the right edge (§4). ~~Final asteroid-whisper decision~~ **DONE 2026-07-09** → whisper IN (faint cold point, top-left). See §6/§13.
4. Then leave the mockup and build the **real locked template** (PSD + Astro theme) from it.

---

## Open decisions parked for their proper stage
- §4: every [bracket] — the full design-constant lock.
- §6: final geological anchor per volume (asteroid whisper leading for Late Cretaceous).
- §6: whether the mid-cascade also gets a soft third *animal* anchor.
- §2: final volume numbering/order after V1.
- §5: any extra record field a buyer would want (discovery year? closest living relative? size-vs-human?).
