# The Living Past — Astro organism-page template (SCOPE §9, #15)

One templated page per organism, **auto-built from `volume_v.json`** — 32 pages for
Volume V, 224 across the series = an SEO paleo-encyclopedia no competitor has.
Design matches the validated mockup `living_past/organism_page.html` (#19), using the
locked type system (Cinzel · EB Garamond · Optima).

## Files (staging — not yet wired to the live site)
| File | Deploy as |
|---|---|
| `[volume]/[slug].astro` | `site/src/pages/late-cretaceous/[slug].astro` |
| `living-past-tokens.css` | `site/public/styles/living-past-tokens.css` |
| (fonts) `../fonts/*.ttf` | `site/public/fonts/` |
| (data) `../volume_v.json` | import path in the `.astro` (adjust relative import) |

## How it works
- `getStaticPaths()` iterates `volume_v.json.organisms`, one static page per `slug`.
- Renders hero (isolate plate via `o.image` once produced), fast-facts, blurb,
  `funFacts[]`, confidence badge, **buy-CTA (poster + species print — the flywheel)**,
  optional `survivor` / `distribution` / `references[]` panels.
- `<title>`, `<meta description>`, OpenGraph, and JSON-LD are auto-generated per record.
- Empty fields simply don't render — safe to ship before `blurb`/`funFacts`/`references`
  are sourced (Law #4: never fabricate; fill via source-hunter / ref-curator).

## Wire into the live site (when ready)
1. Copy the four items above into `site/`.
2. Add `late-cretaceous/index.astro` (volume landing + poster buy — §9) and the
   redirect endpoint from `living_past/redirect/`.
3. Fix the `.astro` data import to `../../../living_past/volume_v.json` (or copy the
   JSON into `site/src/data/`).
4. `npm run build` in `site/`, preview, then deploy.

Kept in staging so the live jurassinkart.com is untouched until the poster is ready.
