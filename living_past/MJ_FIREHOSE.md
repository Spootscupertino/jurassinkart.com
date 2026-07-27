# The Living Past — MJ prompt firehose (unattended runs)

How the 32 organism isolates get fired into Midjourney **without a human present** and without
burning either budget. Supersedes the per-organism loop in `BUILD_RUNBOOK.md` for the generation
phase; the runbook's compositing steps still apply once Eric has curated.

## The insight that makes it cheap

**MJ is the storage, and curation is deferred.** Nothing is downloaded, nothing is upscaled,
nothing is rated during the run. Claude fires prompts; Eric opens his MJ library later and keeps
what he likes. That removes the old **Gate A (selection)** step — which is what forced a
screenshot of every 4-up grid, and screenshots are where Claude usage actually goes. Reasoning is
nearly free here; *images are not*.

So the golden rule of a firehose run is: **no screenshots inside the loop.** Not to check
progress, not to admire a grid, not to confirm a send. Verification is a `get_page_text` call
at the end of a batch, or nothing at all.

## The fire mechanism (validated 2026-07-27)

In the **in-app browser** (`mcp__Claude_Browser__*`), on `midjourney.com/imagine`, logged in:

1. `read_page {filter: "interactive"}` **once per session** → find `textbox "What will you imagine?"`.
2. `form_input {ref, value: <prompt>}` — typing into MJ's editor is flaky; `form_input` is not.
3. `computer {action: "left_click", coordinate: [519, 64]}` — the send/paper-plane button.

Two facts that make the loop viable, both confirmed by live runs:

- **The textbox ref survives submits.** It does *not* need re-reading between organisms even
  though new jobs render above it. Read it once, reuse it all session. (Re-read only if a
  `form_input` starts erroring.)
- **Enter does not submit.** It inserts a newline. The send button click is required.

Cost: **2 tool calls per organism, zero images.** A batch of 4 is 8 calls plus one `mj_firehose.py`
call at each end.

## Pacing

`tools/mj_firehose.py` owns the pacing so a caller can't flood MJ:

```bash
python3 tools/mj_firehose.py status              # progress board per stratum
python3 tools/mj_firehose.py next                # hands out the next batch, or refuses on cooldown
python3 tools/mj_firehose.py fired CR01 CR03     # record + start the cooldown
python3 tools/mj_firehose.py requeue CR07        # a dud came back; fire it again
```

Defaults are 4 prompts per window, 15 min apart — deliberately conservative for a background run.
For an attended session, `--cooldown 3` is fine: a batch of 4 drains in about that long, so the
queue stays busy but never deep. `next` **exits 4 and prints nothing** while the cooldown holds,
so a loop that ignores the cooldown simply gets no prompts to fire.

Order is by stratum (above → underground → shoreline → ocean) so the MJ library ends up grouped
the way the poster is assembled, and each stratum shares one zone-light.

## Pausing between batches

Claude's browser `wait` caps at 10 s and foreground `sleep` is blocked. Use a background timer,
which re-invokes Claude when it fires:

```bash
sleep 170; echo "batch-window-open"
```

(run with `run_in_background: true`)

## Getting pixels back out of MJ (solved 2026-07-27)

Three obvious routes are all closed, so don't burn time re-trying them:

- `curl` the CDN → **Cloudflare 403.** Do not attempt to work around bot detection.
- `fetch()` from the page → **blocked by CORS/COEP.**
- Canvas `toDataURL` → **tainted canvas.**

What works: **click MJ's own download button in the user's real Chrome**
(`mcp__claude-in-chrome__*`), not the in-app browser — the in-app browser saves into sandboxed
storage Bash cannot read, whereas Chrome saves normally to `~/Downloads`. The filename embeds the
job UUID, so it can be matched deterministically:

```bash
cp ~/Downloads/*<job-uuid>*_0.png working/mj_pull/<ID>.png
```

Open a job at `midjourney.com/jobs/<uuid>?index=<0-3>`; the download control sits at
approximately (1315, 113) at a 1456-wide viewport. This closes the loop: generate → download →
knock out → composite, with no human in the middle.

## What still needs a human

- **Image refs.** `--sref` / `--oref` attachment is not automatable; `--ow` without an attached
  ref does nothing. Any run needing refs stays a manual step.
- **Every taste call.** The firehose never judges. Duds are not a failure of the run — they are
  `--sref` fodder for the library flywheel.
- **The personalization profile.** MJ is silently appending `--profile` to every job. See below.

## Open issues

- **`--profile` is on.** Jobs come back stamped `--profile uxjzh3u` (the Chrome session showed
  `tvkq8uu`). A personalization profile pushes every isolate toward a learned aesthetic, which is
  the opposite of what a neutral reference plate wants. Turning it off is an account-settings
  change, so it is Eric's call, not Claude's — but it should be a conscious one.
- **Habitat beats background for airborne/submerged subjects.** The first Quetzalcoatlus run came
  back on open blue sky despite "isolated on flat mid-grey." Fixed by Rule 7 in
  `lp_organism_prompt.py`: a hard `--no background scenery, sky, horizon, …` veto. Watch whether
  it holds on the ocean stratum, where the pull is strongest.
