#!/usr/bin/env python3
"""The Living Past — knock out organism plates with Photoshop's Select Subject.

This exists because of the Photoshop experiment in `PHOTOSHOP.md` (2026-07-28), which was run to
answer "what can Photoshop do that code can't?" and came back with a blunter answer than expected:
**it does the knockout better, and it is scriptable.**

The flood-fill knockout in `compose_organism.py` is geometric. It can only remove background that
is *connected to the frame border* and *tonally near it*, which means the faint floor plane MJ
keeps adding under the feet — continuous with the animal's contact point, and a different grey
from the field — is not reachable at any tolerance that also spares the silhouette. Select Subject
is an ML segmentation with no such constraint. Measured on the three real plates it removed the
floor plane completely on all three, in ~2 seconds each, with the silhouette intact.

Note this also corrects a standing assumption: `mj_recipe.md` recorded Remove-Background as
"UI-only, not scriptable". Select Subject is reachable from JSX as
`executeAction(stringIDToTypeID("autoCutout"))`, so the whole isolate step automates.

The handoff needs no other changes: this writes PNGs with a real alpha channel, and
`compose_organism.isolate()` already prefers a plate's existing alpha over flood-filling it.

    python3 tools/ps_isolate.py working/mj_pull/*.png
    python3 tools/ps_isolate.py working/mj_pull/CR01_trex.png --out-dir living_past/plates/organisms
    python3 tools/ps_isolate.py --check           # is Photoshop reachable at all?
"""
from __future__ import annotations

import argparse
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "living_past/plates/organisms"
# Photoshop's AppleScript name carries the year, and it moves every release.
PS_NAMES = ("Adobe Photoshop 2026", "Adobe Photoshop 2025", "Adobe Photoshop 2024",
            "Adobe Photoshop")


def _run_jsx(app_name: str, jsx: str, timeout: int) -> tuple[bool, str]:
    with tempfile.NamedTemporaryFile("w", suffix=".jsx", delete=False) as fh:
        fh.write(jsx)
        path = fh.name
    try:
        r = subprocess.run(
            ["osascript", "-e",
             f'tell application "{app_name}" to do javascript '
             f'(read (POSIX file "{path}") as text)'],
            capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0, (r.stdout or r.stderr).strip()
    except subprocess.TimeoutExpired:
        return False, f"timed out after {timeout}s"
    finally:
        pathlib.Path(path).unlink(missing_ok=True)


def find_photoshop() -> str | None:
    """The installed Photoshop that answers a JSX ping. Launches it if it isn't already up."""
    for name in PS_NAMES:
        if not list(pathlib.Path("/Applications").glob(f"{name}*")):
            continue
        ok, out = _run_jsx(name, "app.version;", timeout=180)
        if ok and out:
            return name
    return None


JSX = r"""
var report = [];
app.displayDialogs = DialogModes.NO;
var jobs = %s;
for (var i = 0; i < jobs.length; i++) {
    var rec = {src: jobs[i][0], out: jobs[i][1]};
    try {
        var d = app.open(new File(rec.src));
        // A freshly opened PNG is a locked Background layer; clearing to transparency needs a
        // normal layer, and this is the step whose absence makes the whole script silently no-op.
        d.activeLayer.isBackgroundLayer = false;
        var t0 = new Date().getTime();
        executeAction(stringIDToTypeID("autoCutout"), undefined, DialogModes.NO);
        rec.ms = new Date().getTime() - t0;
        d.selection.invert();
        d.selection.clear();
        d.selection.deselect();
        d.trim(TrimType.TRANSPARENT);
        var o = new ExportOptionsSaveForWeb();
        o.format = SaveDocumentType.PNG; o.PNG8 = false; o.transparency = true;
        d.exportDocument(new File(rec.out), ExportType.SAVEFORWEB, o);
        rec.w = d.width.value; rec.h = d.height.value; rec.ok = true;
        d.close(SaveOptions.DONOTSAVECHANGES);
    } catch (e) {
        rec.ok = false; rec.err = String(e);
        try { app.activeDocument.close(SaveOptions.DONOTSAVECHANGES); } catch (e2) {}
    }
    report.push(rec);
}
JSON_OUT_PLACEHOLDER
"""


def build_jsx(jobs: list[tuple[str, str]]) -> str:
    # ExtendScript has no JSON.stringify in older hosts, so the report is assembled by hand.
    tail = (
        'var s = "";\n'
        'for (var i = 0; i < report.length; i++) {\n'
        '    var r = report[i];\n'
        '    s += (r.ok ? "OK\\t" + r.ms + "\\t" + r.w + "x" + r.h + "\\t" + r.out\n'
        '               : "FAIL\\t0\\t-\\t" + r.src + "\\t" + r.err) + "\\n";\n'
        '}\n'
        's;\n')
    return (JSX % json.dumps([[s, o] for s, o in jobs])).replace("JSON_OUT_PLACEHOLDER", tail)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Knock out plates with Photoshop Select Subject")
    ap.add_argument("plates", nargs="*", type=pathlib.Path, help="plate PNGs to isolate")
    ap.add_argument("--out-dir", type=pathlib.Path, default=DEFAULT_OUT)
    ap.add_argument("--suffix", default="_isolated", help="appended to each output stem")
    ap.add_argument("--check", action="store_true", help="just report whether Photoshop answers")
    ap.add_argument("--timeout", type=int, default=600)
    args = ap.parse_args(argv)

    app_name = find_photoshop()
    if args.check:
        print(f"photoshop: {app_name or 'NOT REACHABLE'}")
        return 0 if app_name else 1
    if not args.plates:
        ap.print_help()
        return 1
    if not app_name:
        print("Photoshop is not reachable — fall back to the flood-fill knockout:\n"
              "  python3 tools/compose_organism.py <ID> --plate <plate.png> --isolate-only",
              file=sys.stderr)
        return 1

    missing = [p for p in args.plates if not p.exists()]
    if missing:
        print(f"missing plate(s): {', '.join(str(m) for m in missing)}", file=sys.stderr)
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(str(p.resolve()), str((args.out_dir / f"{p.stem}{args.suffix}.png").resolve()))
            for p in args.plates]
    print(f"# {app_name} · Select Subject · {len(jobs)} plate(s) -> {args.out_dir}")

    ok, out = _run_jsx(app_name, build_jsx(jobs), timeout=args.timeout)
    if not ok:
        print(f"photoshop call failed: {out}", file=sys.stderr)
        return 1

    failures = 0
    for line in out.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        if parts[0] == "OK":
            print(f"  ok    {parts[1]:>5} ms  {parts[2]:>10}  {pathlib.Path(parts[3]).name}")
        else:
            failures += 1
            print(f"  FAIL  {' '.join(parts[3:])}", file=sys.stderr)
    print(f"\n{len(jobs) - failures}/{len(jobs)} isolated. These carry a real alpha channel, so "
          f"compose_organism/place_on_backdrop use them as-is.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
