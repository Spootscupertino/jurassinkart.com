# The Living Past — QR redirect layer (SCOPE §8)

**Print is forever.** A printed QR must never encode a page URL — the site will
restructure and the code would die. Instead each QR encodes a stable, ID-based
redirect we own:

```
jrk.art/x/CR14   →  (redirect table)  →  /late-cretaceous/didelphodon
```

Only this table changes when the site moves. The `id` (e.g. `CR14`) is permanent
(SCOPE §5) — it's the callout number, key position, QR target, and page handle.

## Files
| File | Role |
|---|---|
| `gen_redirects.py` | Reads `living_past/volume_*.json` → emits `redirects.json`. Run after any roster/slug change. |
| `redirects.json` | Generated `id → {slug, path, volume}` map. 32 entries for Volume V. |
| `x.[id].ts` | Astro endpoint. Deploy as `site/src/pages/x/[id].ts`; 301s to the current page, 302s to the volume index as a safe fallback for unmapped IDs. |

## Wire into the live site (when ready)
1. `python3 living_past/redirect/gen_redirects.py`
2. `cp living_past/redirect/redirects.json site/src/data/redirects.json`
3. `cp living_past/redirect/x.[id].ts site/src/pages/x/[id].ts`
4. Point the short domain `jrk.art/x/*` at the Vercel deployment (DNS/redirect).

Master QR (title band) → `jrk.art/x/V` → the volume index. Per-item QR → `jrk.art/x/CR##`.

**Analytics:** because we own the redirect hop, scan counts per `id` tell us which
organisms are popular → which single-species prints and which next volume to make (§8).
Left as staging in `living_past/` until the poster is ready to publish — the live
site is untouched.
