# The Living Past — large-format publishing plan (#20, confirmed 2026-07-09)

Confirmed against the existing pipeline (`printify/`) rather than docs.

## ✓ 24×36" landscape IS supported
The poster is **landscape 24×36"** → in the pipeline's portrait-keyed size map that's
the **`36x24`** variant on **blueprint 284 "Matte Horizontal Posters"** (`printify/image_fit.py`
`PRINT_SIZES`, and the locked landscape rule in `printify/CLAUDE.md`). The master-fit
code already targets 36″ @ 300 DPI, matching our 10800-px master. So the large-format
poster is ready to publish with no new plumbing.

## ⚠ Three things to decide/flag (changed since the #20 goal was written)
1. **Wrapped canvas was retired 2026-05-28.** The store now ships **posters + mugs**, not
   canvas. So "poster + canvas" isn't the current pipeline. Options:
   - **(default) Poster only** for the Living Past large-format — cleanest, matches the store.
   - Re-add wrapped canvas as a premium large-format SKU if you want it (requires
     re-bootstrapping the canvas blueprint into `printify_config.yaml`).
2. ~~**Landscape art auto-generates a MUG**~~ **RESOLVED 2026-07-09.** Added a mug exception in
   `printify_publisher.py`: `MUG_EXCLUDED_CATEGORIES = {"living-past"}` plus a per-image
   `no_mug`/`poster_only` flag. Living Past art is now poster-only even though it's landscape.
   (Verified across 5 cases; normal landscape art still gets a mug.)
3. **Auth:** as of 2026-04-29 the `PRINTIFY_API_KEY` returned 401. Re-generate the token in
   the Printify dashboard, then `printify_publisher.py --bootstrap-config` before any publish.

## Discipline (unchanged, locked)
- **Drafts only** — `--dry-run` is default; `--live` explicit; never auto-publish to Etsy;
  user QA-gates each listing (matches project memory).
- Mockups = **clean front + rolled-tube only**, never AI-heavy lifestyle room scenes.
- Free shipping override; price matches existing store products.

## Net
Large-format **24×36 landscape poster is confirmed available and ready.** Recommend
**poster-only** for the Living Past (canvas retired, mug inappropriate). Publish stays a
manual, drafts-first, user-gated step at the end of the build (SCOPE §12 step 8).
