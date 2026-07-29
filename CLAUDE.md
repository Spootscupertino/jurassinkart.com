# Jurassinkart — Project Index

This is the *index file*. It points at five domains, each with its own CLAUDE.md and its own owning agent. Keep this file under 60 lines.

**If you're starting a session, jump straight to the right domain — don't load this whole repo into context.**

## Domains

| Path | Owner | What lives there |
|---|---|---|
| [`flux/`](./flux/CLAUDE.md) ⭐ | `prompt-crafter` | **Replicate-Flux generation** — cloud Flux-dev image generation + LoRA inference, plus dataset prep for Replicate-hosted LoRA training. |
| [`mj/`](./mj/CLAUDE.md) *(coming Phase 4)* | `prompt-crafter` | Midjourney prompt assembly: `generate_prompt.py` (currently at root), `species/`, anatomy modules. |
| [`refs/`](./refs/CLAUDE.md) *(coming Phase 3)* | `ref-curator` | Reference image library: paleoart / skeletal / wildlife `--sref` and `--cref` JSONs (currently at root). |
| [`db/`](./db/CLAUDE.md) *(coming Phase 5)* | `mj-logger` | SQLite schema + A/B test logging (currently `setup_db.py` and `dino_art.db` at root). |
| [`tools/`](./tools/CLAUDE.md) | (shared infra) | Gallery sync watcher pipeline: `sync_gallery.py`, `sync_and_deploy.sh`, `install_watcher.sh`. |
| [`printify/`](./printify/CLAUDE.md) | `printify-publisher` | Printify → Etsy product publishing pipeline. |
| [`site/`](./site/CLAUDE.md) | `site-custodian` | Astro frontend at jurassinkart.com. |
| [`living_past/`](./living_past/SCOPE.md) 🏛 | (none yet) | **The Living Past** — the 7-volume cross-section poster series. Its own product line, deliberately **outside** the gallery pipeline below. |

## Cross-domain contracts

Every handoff is a **file or DB row**, never a Python import across domains.

**Generation pipeline (Replicate-Flux):**
- `reference.py` intakes refs → `assets/gallery/flux/training_refs/` (+ captions) + `winners.json`
- `flux/export_dataset.py` bundles refs → `flux/datasets/<name>_dataset.zip`
- Replicate `ostris/flux-dev-lora-trainer` (web UI) → trained LoRA → registered in `flux/loras/registry.json`
- `flux/generate.py` reads registry + prompt → calls Replicate Flux-dev (baseline or LoRA version) → PNG + sidecar JSON
- `flux/ab_test_replicate.py` validates each new LoRA (5-pair A/B against baseline)
- Generated images → `assets/gallery/flux/` (same contract as MJ)

**Original pipeline (unchanged):**
- `refs/*.json` → `mj/generate_prompt.py` (read-only)
- `mj/generate_prompt.py` → stdout (you paste into Midjourney)
- (you drop image) → `site/src/assets/gallery/<category>/*.png`
- `tools/sync_gallery.py` → `site/src/data/products.json` + git push
- `printify/printify_publisher.py` reads `site/src/data/products.json` + gallery images → writes `printify/printify_ledger.json`
- `site/` reads `printify/printify_ledger.json` to deep-link Buy buttons
- `db/dino_art.db` is shared SQLite; one agent owns writes per table

## The Living Past is not part of the gallery pipeline

Eric, 2026-07-29: *"we just need to save this poster as its own series, its not like the bulk other
posters we fly through."*

Everything above is a **throughput** pipeline: drop an image in a gallery folder, a watcher syncs
it, Printify drafts it, Vercel ships it — many images, each cheap. `living_past/` is the opposite:
one poster is months of work, 32 individually-composited organisms, and a plate assembled slot by
slot. Running it through the same machinery would be actively wrong — `sync_gallery.py` would strip
its metadata and `printify_publisher.py` would draft a 2.3:1 panoramic as if it were a 3:2 print.

So it is wired to nothing:
- **No watcher touches it.** All four launchd agents watch `site/` only — verified 2026-07-29.
- **Nothing in `site/` or `printify/` reads from it**, and it reads from neither.
- Its own build chain is self-contained: `tools/build_backdrop.py` →
  `living_past/plates/backdrop_vN.png` → `_scene_live.png` → `poster_mockup_live.html`.
- When a volume is ready to sell, that is a **deliberate, manual** hand-off — not an automatic one.

## Migration status

Decomposition is happening in phases (see `RECAP.md` for the full plan). Currently complete: **Phase 1** (CLAUDE.md scoping). Phase 2 (printify/) in progress. Phases 3–6 (refs/, mj/, db/, RECAP split) deferred to dedicated sessions to avoid mid-session refactor risk.

## Top-level facts that stay here

- Live site: https://jurassinkart.com (Vercel, auto-deploys from `main`)
- Two GitHub remotes: `dino-art-studio` (dev mirror) and `jurassinkart.com` (Vercel-connected). `origin` dual-pushes to both.
- Watcher: launchd agent `com.jurassinkart.sync-gallery` watches the 5 gallery subfolders
- Domain DNS: Network Solutions (`ns99.worldnic.com`); Vercel project handles deploys but not DNS
- `.env` at root holds: PRINTIFY_API_KEY, PRINTIFY_SHOP_ID, MIDJOURNEY_*, DISCORD_WEBHOOK_URL
