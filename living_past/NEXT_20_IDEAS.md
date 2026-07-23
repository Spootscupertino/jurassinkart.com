# The Living Past — 20 Ideas for Next Time (written 2026-07-10)

Plainly written, with how to go about each. The first cluster is the critical path: the
background is now great, so the next leap is putting animals on the stage.

## Put the animals on the stage (start here)
1. **Place the T. rex on the terrace.** Generate CR01 (`lp_organism_prompt.py CR01`), knock out
   the background, size it to ~⅓ the poster width (`scale_calc.py`), and stand it near the
   cliff edge on the flat terrace. This is the moment the whole thing pays off.
2. **Place the Mosasaurus rising from the black abyss.** CR25, floating over the deep-right so
   it looms out of the dark. Two titans in = the scale story is proven end-to-end.
3. **Lock the organism "isolate recipe."** Whatever lighting, edge, and grade make the T. rex
   sit believably becomes the spec for all 32, so they read as one world.

## Finish the geology (the accuracy moat)
4. **Add the organic geology accents.** Roots descending from the topsoil, a visible burrow, and
   the buried egg clutch (CR15) painted/composited into the cliff — the bits MJ can't fake.
5. **Tune strata intensity + feather the deep edge.** They're bold right now (one number in
   `composite_strata.py`); soften if wanted, and gradient-blend where the cliff meets the abyss
   so there's no hard vertical seam.
6. **Show off the accurate strata column.** `_strata_accurate.png` is a genuine geology diagram
   — make it a small poster inset and/or a web element. Nobody else has this.

## Polish the poster to print quality
7. **Fix the volcano crop.** The poster's scene band clips the ash plume; bias the crop upward
   or widen the scene row so the whole volcano shows.
8. **Upscale to master resolution.** Base plate v2 + the 8 textures are ~2688px; the print
   master needs ~10,800px. Upscale before the final composite so it stays crisp at 24×36.
9. **One-world grade pass.** Once organisms are placed, a single light/color pass so 30-plus
   separate pieces read as one world under one sunset.
10. **Rebuild the layered PS file.** Run `build_template_psd.jsx`, drop the graded plates and
    organisms into named zone groups — the master-resolution poster lives here.

## Build out the QR destination (the web half)
11. **Make the organism page a real generator.** Turn today's one page into a template that
    builds all 32 pages from `volume_v.json` with proper slugs and routing.
12. **Wire the real QR redirect.** `jrk.art/x/CR01 → 301 → /late-cretaceous/tyrannosaurus-rex`,
    plus JSON-LD schema and OG images; print one at true 0.5" and scan-test it.
13. **Add real hero videos per organism.** The animated hero slot is built; drop in a short
    clip per species as they're generated (the T. rex rain clip is the template).
14. **Build the "still with us today" survivor module.** A first-class treatment for the gar,
    horseshoe crab, crinoid, and birds — the strongest emotional hook.

## Fill in the facts (never invent — Law #4)
15. **Source the real facts per organism.** Use `source-hunter` / `ref-curator` to fill blurb,
    funFacts, distribution, and references. Start with the `needsRefs:true` swapped-in species.
16. **Wire the Astro pages into the live site.** Copy the staged template + tokens into `site/`,
    build, and preview a few real organism pages.

## Run the organism marathon
17. **Batch-generate the 8 above-ground organisms.** Work one stratum at a time so light and
    style stay consistent within a group.
18. **Stand up an organism tracking board.** `plates/organisms/CR##_name.png` + a `status` field
    (generated → isolated → placed) so the 32-organism run has a clear board.

## Prove and ship
19. **Export the print master + make the Printify draft.** 24×36 landscape poster, drafts only,
    clean front + rolled-tube mockups, user approves before anything hits Etsy.
20. **Final QA pass.** Check every scientific name, size, confidence dot, and the one-world grade
    before it ever goes live.

**Recommended opening move next session:** #1 (the T. rex on the terrace) — the background is
finally ready to hold it, and it's the payoff for everything we built today.
