# The Living Past — Organism Build Runbook

How the 32-organism poster cast gets built, and **who does which part**. The whole point of
this split is usage economics: the expensive model authors the spec and sits at the judgment
gates; a cheap executor grinds the rote loop; the human holds final taste + the one thing
automation can't do yet (image refs).

## Roles

| Role | Who | Does |
|---|---|---|
| **Architect / Gate** | Fable (this session) | Writes/updates this runbook + the prompt recipe; approves or rejects each placed organism; handles anything needing real visual judgment. |
| **Executor** | cheap subagent (Sonnet/Haiku) | Runs the deterministic loop below, one organism at a time; **escalates** at every gate; never makes a taste call. |
| **Human** | Eric | Attaches image/style refs in MJ (the unsolved automation seam); final aesthetic sign-off; remixes. |

> **Superseded for the generation phase (2026-07-27).** Steps 1–3 below are replaced by the
> unattended firehose in [`MJ_FIREHOSE.md`](./MJ_FIREHOSE.md): Claude fires all 32 prompts into
> MJ and stops. **Gate A is gone** — Eric curates natively in his MJ library instead, which is
> what made the loop cheap enough to run unattended. Steps 4–7 (isolate → place → Gate B) still
> stand and pick up from whatever he keeps.

## The per-organism loop (Executor)

For each organism with `status: queued` in `build_queue.json`, in `position` order within the
current batch:

1. **Prompt.** Take the `prompt` field from `build_queue.json` (already the framing-fixed recipe
   from `lp_organism_prompt.py`). Do **not** rewrite it.
2. **Generate.** In the `midjourney.com` tab: set the imagine bar with `form_input`, append the
   row's `ar` as `--ar`, submit (send button ~coord 518,33). Poll with `wait` (≤10s) until the
   4-up renders (~60–90s; often stuck on "Starting…").
3. **GATE A — selection.** Screenshot the grid. **Escalate to the Gate** with the 4 images and
   ask which (if any) is a keeper. Executor never picks. If none pass, log why, leave `queued`.
4. **Upscale** the chosen tile; download/save the upscale to `working/<id>_upscaled.png`.
5. **Isolate + place.** `python3 tools/compose_organism.py <id> --plate working/<id>_upscaled.png`.
   Advance `status → placed`. Save the composite path in `notes`.
6. **GATE B — anatomy/QA.** Escalate the composite to the Gate: whole body in frame? anatomy
   sane (two-finger hands, correct digit count, no melted feet)? scale believable on the plate?
   Gate flips `placed → approved` or bounces to `queued` with a fix note.
7. **Log + advance.** Update the row's `status`/`notes`, re-run `tools/build_queue.py` to refresh
   the board. Move to the next organism.

## Batch strategy

- **One stratum at a time** (Above Ground → Underground → Shoreline → Ocean). Light and style
  stay consistent within a group, and each stratum shares one zone-light (see `mj_recipe.md`).
- **Micro-organisms** (ant 3px, beetle larva 8px, earthworm 27px — below the 60px floor) are
  drawn enlarged per Law #2; `compose_organism.py` handles the scale, but the Gate must confirm
  the enlargement reads and the true size is captured for the key.
- **Ocean stratum** flips the light to cool blue-green from above (already in each prompt) and
  places `mid`/floating, not `feet` — anchors are pre-set in `compose_organism.py`.

## Known seams (do not let the Executor improvise past these)

- **Image refs are NOT automatable yet.** Any run needing an oref/sref (e.g. the T. rex
  detail-dial-in with your own roaring head as a style ref) is a **Human** step until the
  attach flow is solved. `--ow` without an attached oref does nothing. See
  `project_mj_direct_generation` memory.
- **Selection + anatomy are judgment gates**, not executor calls. A cheap model will accept a
  three-fingered hand. Always escalate A and B.
- **Usage note:** live MJ driving is screenshot-heavy (big image tokens) regardless of model, so
  the cheap executor saves reasoning cost but not all image cost — batch tightly, don't re-screenshot.

## Kicking off a batch

Fable spawns one Executor subagent per batch with a cheaper model, pointing it at this runbook
+ `build_queue.json` filtered to the stratum. The Executor runs steps 1–7, pausing at Gates A/B
for Fable. Human is pinged only for ref-attach and final taste.
