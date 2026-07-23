# The Living Past — blank locked template (§4 frozen 2026-07-09)

This directory is the **frozen design template** — every §4 design constant baked into machine-readable form, ready to receive art (PSD) and drive the site (Astro).

## Files

| File | Role |
|---|---|
| `design_tokens.json` | **Single source of truth.** Every locked constant: canvas, layout, scale, color, type, brass, badges, QR, timeline, globe. |
| `gen_tokens_css.py` | Generator → `tokens.css`. Run after any edit to the JSON. |
| `tokens.css` | Generated CSS custom properties (`--lp-*`) imported by the mockups and the Astro site. **Do not hand-edit.** |
| `../../tools/build_template_psd.jsx` | Photoshop script that builds the empty §7 layer-group skeleton at the locked master size (10875×7275 @ 300dpi) with trim/safe/row/coastline guides. |

## The two size scales

- **`mockup_px`** — px at the 1180px preview poster (what the HTML mockups use).
- **`master_pt`** — points on the real 24×36" 300dpi master (10800×7200 px).
- Conversion: `master_px = mockup_px × 9.153`, `master_pt = master_px × 0.24`.

## Regenerate the CSS
```
python3 living_past/template/gen_tokens_css.py
```

## Build the blank PSD
Requires Photoshop (GUI). From repo root:
```
osascript -e 'tell application "Adobe Photoshop 2024" to do javascript (read (POSIX file "'"$PWD"'/tools/build_template_psd.jsx"))'
```
Then **Save As** `living_past/template/The_Living_Past_V5_template.psd`. The layer-group **names are the contract** (SCOPE §7) — art lands in a pre-named home so the build goes top group → bottom group with no backtracking.

## What's frozen
All of SCOPE §4 — see that section for rationale and the per-decision auditions
(`type_audition.html`, `brass_audition.html`, `zoneline_audition.html`,
`glyph_audition.html`, `scalebar_audition.html`).
