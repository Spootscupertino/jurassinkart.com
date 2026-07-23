#!/usr/bin/env python3
"""Generate tokens.css from design_tokens.json — the single source of truth.

Emits CSS custom properties (colors, fonts, type scale) that both the poster
mockups and the Astro site import. Run after any edit to design_tokens.json:

    python3 living_past/template/gen_tokens_css.py
"""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
TOK = json.loads((HERE / "design_tokens.json").read_text())


def main() -> None:
    c = TOK["color"]
    faces = TOK["type"]["faces"]
    scale = TOK["type"]["scale"]

    lines = [
        "/* GENERATED from design_tokens.json — do not edit by hand.",
        "   Regenerate: python3 living_past/template/gen_tokens_css.py */",
        ":root{",
        "  /* --- brass + ink --- */",
        f"  --lp-brass: {c['brass_base']};",
        f"  --lp-brass-hi: {c['brass_hi']};",
        f"  --lp-ivory: {c['ink_ivory']};",
        f"  --lp-ivory-2: {c['ink_ivory_2']};",
        f"  --lp-muted: {c['ink_muted']};",
        f"  --lp-bedrock: {c['bedrock']};",
        f"  --lp-abyss: {c['abyss']};",
        f"  --lp-extinction: {c['extinction_red']};",
        f"  --lp-callout-fill: {c['callout_fill']};",
        f"  --lp-callout-numeral: {c['callout_numeral']};",
        f"  --lp-sunset: {', '.join(c['sunset_stops'])};",
        f"  --lp-ground-grad: {', '.join(TOK['layout']['furniture_ground_gradient'])};",
        "  /* --- faces --- */",
        f"  --lp-display: \"{faces['display']['family']}\", {faces['display']['fallback']};",
        f"  --lp-body: \"{faces['body']['family']}\", {faces['body']['fallback']};",
        f"  --lp-sans: \"{faces['sans']['family']}\", {faces['sans']['fallback']};",
        f"  --lp-display-weight: {faces['display']['weight']};",
        "  /* --- type scale (mockup px @ 1180px poster) --- */",
    ]
    for role, s in scale.items():
        r = role.replace("_", "-")
        lines.append(f"  --lp-{r}-size: {s['mockup_px']}px;")
        lines.append(f"  --lp-{r}-track: {s['tracking_em']}em;")
    lines.append(f"  --lp-brass-label-track: {TOK['type']['brass_label']['tracking_em']}em;")
    lines.append("}")

    out = "\n".join(lines) + "\n"
    (HERE / "tokens.css").write_text(out)
    print(f"wrote tokens.css ({len(out)} bytes, {len(scale)} type roles)")


if __name__ == "__main__":
    main()
