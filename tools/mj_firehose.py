#!/usr/bin/env python3
"""The Living Past — MJ prompt firehose (#19).

Fires the 32 organism isolate prompts into Midjourney and stops there. MJ *is* the storage:
nothing is downloaded, nothing is selected, nothing is rated. Eric curates natively in his MJ
library afterwards. That deletes the old Gate-A selection step from BUILD_RUNBOOK.md, which is
what made the loop expensive — without it the whole run is a paced, near-free prompt firehose.

Two budgets have to be respected and they pull in opposite directions:

  * Midjourney — concurrency + fast GPU minutes. Handled by `batch` / `cooldown`: this tool
    simply refuses to hand out more prompts than the window allows, so an over-eager caller
    can't flood the queue.
  * Claude usage — dominated by *screenshots*, not reasoning. So the browser loop must be
    text-only: form_input the prompt, click send, mark it here. No screenshots, no grid reads,
    no polling for completion. Nothing in this tool asks the caller to look at an image.

Usage:
    python3 tools/mj_firehose.py status
    python3 tools/mj_firehose.py next            # prompts eligible right now (respects cooldown)
    python3 tools/mj_firehose.py next --force    # ignore the cooldown (manual runs)
    python3 tools/mj_firehose.py fired CR01 CR02
    python3 tools/mj_firehose.py requeue CR07    # a dud came back — fire it again next window
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LP = ROOT / "living_past"
QUEUE = LP / "build_queue.json"
STATE = LP / "mj_firehose_state.json"

# Conservative by default. MJ standard plans run ~3 concurrent fast jobs; a batch of 4 keeps the
# queue full without a backlog, and 15 min between batches lets each batch finish before the next
# lands. 32 organisms therefore take ~8 windows ≈ 2h — comfortably inside a workday.
DEFAULT_BATCH = 4
DEFAULT_COOLDOWN_MIN = 15

STRATA_ORDER = ["above", "underground", "shoreline", "ocean"]


def now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def load_state() -> dict:
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"fired": {}, "last_batch_at": None}


def save_state(s: dict) -> None:
    STATE.write_text(json.dumps(s, indent=2) + "\n")


def load_queue() -> list[dict]:
    rows = json.loads(QUEUE.read_text())["organisms"]
    rows.sort(key=lambda r: (STRATA_ORDER.index(r["section"]) if r["section"] in STRATA_ORDER
                             else 99, r["position"]))
    return rows


def pending(rows: list[dict], state: dict) -> list[dict]:
    return [r for r in rows if r["id"] not in state["fired"]]


def cooldown_remaining(state: dict, cooldown_min: int) -> float:
    """Minutes left before the next batch may be handed out."""
    last = state.get("last_batch_at")
    if not last:
        return 0.0
    elapsed = (now() - dt.datetime.fromisoformat(last)).total_seconds() / 60
    return max(0.0, cooldown_min - elapsed)


def cmd_status(args) -> int:
    rows, state = load_queue(), load_state()
    left = pending(rows, state)
    done = len(rows) - len(left)
    wait = cooldown_remaining(state, args.cooldown)
    print(f"fired {done}/{len(rows)}   pending {len(left)}")
    for sec in STRATA_ORDER:
        grp = [r for r in rows if r["section"] == sec]
        f = sum(1 for r in grp if r["id"] in state["fired"])
        bar = "#" * f + "." * (len(grp) - f)
        print(f"  {sec:<12} [{bar}] {f}/{len(grp)}")
    if wait > 0:
        print(f"\ncooldown: {wait:.1f} min until the next batch of {args.batch}")
    elif left:
        print(f"\nready: next batch of {min(args.batch, len(left))} can fire now")
    else:
        print("\nall 32 fired — nothing left to do")
    return 0


def cmd_next(args) -> int:
    rows, state = load_queue(), load_state()
    left = pending(rows, state)
    if not left:
        print("# all organisms fired — nothing pending", file=sys.stderr)
        return 3
    wait = cooldown_remaining(state, args.cooldown)
    if wait > 0 and not args.force:
        print(f"# cooldown: {wait:.1f} min remaining — do not fire yet", file=sys.stderr)
        return 4

    batch = left[: args.batch]
    if args.json:
        print(json.dumps([{"id": r["id"], "name": r["commonName"], "prompt": r["prompt"]}
                          for r in batch], indent=2, ensure_ascii=False))
    else:
        for r in batch:
            # one prompt per line, ID-prefixed: the browser loop splits on the first tab
            print(f"{r['id']}\t{r['prompt']}")
    return 0


def cmd_fired(args) -> int:
    state = load_state()
    known = {r["id"] for r in load_queue()}
    stamp = now().isoformat()
    for oid in args.ids:
        oid = oid.upper()
        if oid not in known:
            print(f"unknown id {oid}", file=sys.stderr)
            return 1
        prev = state["fired"].get(oid, {})
        state["fired"][oid] = {"at": stamp, "attempt": prev.get("attempt", 0) + 1}
    state["last_batch_at"] = stamp
    save_state(state)
    rows = load_queue()
    print(f"marked {len(args.ids)} fired — {len(state['fired'])}/{len(rows)} done, "
          f"next batch in {args.cooldown} min")
    return 0


def cmd_requeue(args) -> int:
    state = load_state()
    for oid in args.ids:
        state["fired"].pop(oid.upper(), None)
    save_state(state)
    print(f"requeued {', '.join(i.upper() for i in args.ids)} — will be handed out again")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Living Past MJ prompt firehose")
    ap.add_argument("--batch", type=int, default=DEFAULT_BATCH, help="prompts per window")
    ap.add_argument("--cooldown", type=int, default=DEFAULT_COOLDOWN_MIN, help="minutes between batches")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status").set_defaults(fn=cmd_status)

    p = sub.add_parser("next")
    p.add_argument("--json", action="store_true")
    p.add_argument("--force", action="store_true", help="ignore the cooldown")
    p.set_defaults(fn=cmd_next)

    p = sub.add_parser("fired")
    p.add_argument("ids", nargs="+")
    p.set_defaults(fn=cmd_fired)

    p = sub.add_parser("requeue")
    p.add_argument("ids", nargs="+")
    p.set_defaults(fn=cmd_requeue)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
