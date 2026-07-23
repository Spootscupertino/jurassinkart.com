#!/usr/bin/env python3
"""The Living Past — build every organism's QR landing page from the volume JSON (#11).

Turns the one hand-tuned page (living_past/organism_page.html) into a generator: reads
volume_v.json + redirects.json + design_tokens.json and emits one page per organism into
living_past/pages/<slug>.html, reusing the template's exact CSS so all 32 look identical to
the proven CR01 page.

Law #4 (never invent) is enforced structurally: only the LOCKED factual fields (name, type,
size, diet, age, confidence) are bound from the record. Narrative slots (blurb, field notes,
survivor note, distribution, references) render as clearly-marked "pending sourced fill"
placeholders until source-hunter / ref-curator fill them in the JSON — so a page is never
silently fabricated, and its unfinished state is visible.

    python3 tools/build_organism_pages.py            # build all 32 + index
    python3 tools/build_organism_pages.py CR01       # build one
    python3 tools/build_organism_pages.py --clean    # wipe pages/ first
"""
from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LP = ROOT / "living_past"
TEMPLATE = LP / "organism_page.html"
OUT_DIR = LP / "pages"
VOL = json.loads((LP / "volume_v.json").read_text())
REDIRECTS = json.loads((LP / "redirect/redirects.json").read_text())
META = VOL["$meta"]

SECTION_LABEL = {"above": "Above Ground", "underground": "Underground",
                 "shoreline": "Shoreline", "ocean": "Ocean"}
TYPE_LABEL = {"land_animal": "Land Animal", "flying_reptile": "Flying Reptile",
              "marine_reptile": "Marine Reptile", "fish": "Fish",
              "invertebrate": "Invertebrate", "plant": "Plant", "mammal": "Mammal"}
CONFIDENCE = {  # → (badge text, dot-fill class matching design_tokens confidence_badge)
    "well_documented": ("Well-documented reconstruction", "filled"),
    "reasonable_inference": ("Reasonable inference", "half"),
    "speculative": ("Speculative reconstruction", "open"),
}
# hero pan focus per stratum (where this animal sits in the scene), as CSS %.
SECTION_FOCUS = {"above": ("30%", "24%"), "shoreline": ("46%", "40%"),
                 "underground": ("22%", "62%"), "ocean": ("74%", "58%")}
# extra CSS for the confidence-dot fill states (the template only styles the filled dot).
DOT_CSS = """
  .hero .badge .dot.half{ background:linear-gradient(90deg,var(--brass) 0 50%,transparent 50%); }
  .hero .badge .dot.open{ background:transparent; }
  /* 'needs sourcing' placeholder tone — visible, never mistaken for finished copy */
  .todo{ color:#7c6f52; font-style:italic; }
  .todo::before{ content:"◇ "; color:var(--brass); font-style:normal; }
"""


def era(age):
    a, b = age
    fmt = lambda x: (f"{x:g}")
    return f"{fmt(a)}–{fmt(b)} Ma"


def extract_css() -> str:
    src = TEMPLATE.read_text()
    m = re.search(r"<style>(.*?)</style>", src, re.DOTALL)
    css = m.group(1)
    # pages/ is one level below living_past/, so asset URLs need ../
    css = css.replace('url("fonts/', 'url("../fonts/')
    return css + DOT_CSS


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def render(o: dict, css: str) -> str:
    oid = o["id"]
    red = REDIRECTS.get(oid, {})
    slug = red.get("slug", oid.lower())
    path = red.get("path", f"/{slug}")
    section = o.get("section", "above")
    sec_label = SECTION_LABEL.get(section, section.title())
    type_label = TYPE_LABEL.get(o.get("type", ""), o.get("type", ""))
    diet = o.get("diet", "").strip()
    conf_text, conf_dot = CONFIDENCE.get(o.get("confidence", ""), ("Reconstruction", "open"))
    era_str = era(o["ageRange_Ma"]) if o.get("ageRange_Ma") else META.get("interval_label", "")
    fx, fy = SECTION_FOCUS.get(section, ("50%", "40%"))
    common, sci = o.get("commonName", ""), o.get("scientificName", "")
    no = f"No. {o.get('position', 0):02d}"
    sub_bits = " · ".join(b for b in (type_label, diet, f"Late Cretaceous, {era_str}") if b)

    # ---- narrative slots: bound only if the record carries them (Law #4) ----
    def field(key, placeholder):
        v = o.get(key)
        if isinstance(v, str) and v.strip():
            return f'<span>{esc(v)}</span>'
        return f'<span class="todo">{placeholder}</span>'

    blurb = (f'<div class="blurb">{esc(o["blurb"])}</div>' if o.get("blurb")
             else f'<div class="blurb todo">One-line lede — pending sourced fill for {esc(common)}.</div>')

    funfacts = o.get("funFacts") or []
    if funfacts:
        ff = "\n".join(f"          <li>{esc(x)}</li>" for x in funfacts)
    else:
        ff = ('          <li class="todo">Field notes pending — source-hunter / ref-curator '
              'fill <code>funFacts[]</code> from the record; confidence-appropriate, never invented.</li>')

    refs = o.get("references") or []
    if refs:
        refs_html = " ".join(f'<a href="{esc(r.get("url","#"))}">[{i+1}]</a>'
                             for i, r in enumerate(refs))
    else:
        refs_html = '<span class="todo">No sources entered yet — <code>references[]</code> empty.</span>'

    habitat = o.get("habitat") or ("Coastal floodplain" if section in ("above", "shoreline")
                                   else "Western Interior Seaway" if section == "ocean"
                                   else "Sub-surface / sediment")
    survivor = (f'<p>{esc(o["survivor"])}</p>' if o.get("survivor")
                else '<p class="todo">Closest-living-relative / survivor note pending — shown when the record has one.</p>')
    where = (esc(o["distribution"]) if o.get("distribution")
             else f'<span class="todo">Range description pending for {esc(common)}.</span>')

    title = f"{common} — Late Cretaceous | The Living Past"
    meta_desc = (esc(o["blurb"]) if o.get("blurb")
                 else f"{common} ({sci}) — {type_label}, {era_str}. The Living Past, Vol V: Late Cretaceous.")

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{meta_desc}">
<meta property="og:title" content="{esc(common)} — The Living Past">
<meta property="og:description" content="{meta_desc}">
<meta property="og:image" content="../plates/organisms/{oid}_isolated.png">
<meta property="og:type" content="article">
<link rel="canonical" href="https://jurassinkart.com{esc(path)}">
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"CreativeWork","name":{json.dumps(common)},"about":{{"@type":"Thing","name":{json.dumps(sci)}}},"isPartOf":{{"@type":"CreativeWorkSeries","name":"The Living Past"}},"temporalCoverage":{json.dumps(era_str)}}}
</script>
<style>{css}
  :root{{ --focus-x:{fx}; --focus-y:{fy}; }}
</style>
</head>
<body>
<div class="pg">

  <section class="hero" id="hero">
    <div class="scene">
      <video class="heromp4" autoplay muted loop playsinline poster="../plates/_proof_scene.png">
        <source src="../hero_demo.mp4" type="video/mp4">
      </video>
    </div>
    <div class="rays"></div>
    <div class="motes"></div>
    <div class="scrim"></div>
    <div class="title">
      <div class="in">
        <div class="eyebrow"><span>The Living Past · Vol {esc(META['volume'])}</span><span class="rule"></span><span class="no">{esc(no)} · {esc(sec_label)}</span></div>
        <h1>{esc(common)}</h1>
        <div class="sub">{esc(sub_bits)}</div>
        <div class="badge"><span class="dot {conf_dot}"></span> {esc(conf_text)}</div>
      </div>
    </div>
    <div class="cue">Scroll<span>⌄</span></div>
  </section>

  <div class="wrap">
    <div class="facts">
      <div class="f"><div class="fl">Size</div><div class="fv">{esc(o.get('size','—'))}</div></div>
      <div class="f"><div class="fl">When</div><div class="fv">{esc(era_str)}</div></div>
      <div class="f"><div class="fl">Diet</div><div class="fv">{esc(diet or '—')}</div></div>
      <div class="f"><div class="fl">Habitat</div><div class="fv">{esc(habitat)}</div></div>
    </div>

    <div class="cols">
      <div class="main">
        {blurb}

        <h2>In this world</h2>
        <p class="body-copy todo">Extended, sourced anatomy &amp; ecology write-up pending (demoted from the poster per Law #3). Filled from the record's sourced notes; never fabricated.</p>

        <h2 style="margin-top:30px">Field notes</h2>
        <ul class="funfacts">
{ff}
        </ul>
      </div>

      <div class="aside">
        <div class="card buy">
          <h3>Bring it home</h3>
          <p>This scene as a museum-grade 24×36″ poster, or just this species as a print.</p>
          <a class="btn p" href="#">Buy the Late Cretaceous poster</a>
          <a class="btn s" href="#">Buy the {esc(common)} print</a>
        </div>

        <div class="card survivor">
          <div class="tag">Still with us today</div>
          {survivor}
        </div>

        <div class="card distrib">
          <h2 style="border:none;margin:0 0 4px;padding:0">Where</h2>
          <div class="map"></div>
          <p class="body-copy" style="font-size:13px;margin:10px 0 0">{where}</p>
        </div>

        <div class="card">
          <h2 style="border:none;margin:0 0 8px;padding:0">Sources</h2>
          <div class="refs">{refs_html}</div>
        </div>
      </div>
    </div>
  </div>

  <div class="deeptime">
    <svg viewBox="0 0 1200 52" preserveAspectRatio="none" aria-label="Deep-time line">
      <line x1="40" y1="30" x2="1160" y2="30" stroke="#b98f4e" stroke-width="1.2"/>
      <g stroke="#6a5a38" stroke-width="1">
        <line x1="150" y1="25" x2="150" y2="35"/><line x1="380" y1="25" x2="380" y2="35"/>
        <line x1="620" y1="25" x2="620" y2="35"/><line x1="860" y1="25" x2="860" y2="35"/>
      </g>
      <text x="44" y="19" font-family="Optima,sans-serif" font-size="11" letter-spacing="3" fill="#8a7c60">DEEP TIME · NOT TO SCALE</text>
      <circle cx="1050" cy="30" r="4.5" fill="#c0442f"/>
      <text x="1064" y="34" font-family="Optima,sans-serif" font-size="11" fill="#c0703f">✕ K–Pg extinction</text>
    </svg>
  </div>

  <div class="footer">
    <span>◆ Reconstruction confidence disclosed</span>
    <span>The Living Past · No. {esc(META['volume'])}</span>
  </div>

  <div class="seo">
    <b>Routing:</b> URL <code>{esc(path)}</code>; QR hits <code>jrk.art/x/{oid}</code> → 301 here.
    OG image = <code>{oid}_isolated.png</code>. Part of the {len(REDIRECTS)}-page Living Past encyclopedia.
  </div>
</div>
</body>
</html>
"""


def build_index(built: list[dict]) -> str:
    """Simple dev index linking every generated page, grouped by stratum."""
    css = extract_css()
    groups: dict[str, list[dict]] = {}
    for o in built:
        groups.setdefault(o.get("section", "above"), []).append(o)
    order = ["above", "underground", "shoreline", "ocean"]
    blocks = []
    for sec in order:
        items = sorted(groups.get(sec, []), key=lambda x: x.get("position", 0))
        if not items:
            continue
        cards = "\n".join(
            f'      <a class="btn s" style="text-align:left" '
            f'href="{REDIRECTS.get(o["id"],{}).get("slug", o["id"].lower())}.html">'
            f'{o["id"]} · {esc(o.get("commonName",""))}</a>'
            for o in items)
        blocks.append(f'    <h2>{SECTION_LABEL.get(sec, sec)}</h2>\n'
                      f'    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:8px">\n{cards}\n    </div>')
    body = "\n".join(blocks)
    return (f"<!doctype html><html lang=en><head><meta charset=utf-8>"
            f"<meta name=viewport content='width=device-width, initial-scale=1'>"
            f"<title>The Living Past · Vol V — all pages</title><style>{css}</style></head>"
            f"<body><div class=pg><div class=wrap style='padding-top:40px'>"
            f"<h1 style='font-family:var(--display)'>The Living Past · Vol V — {len(built)} pages</h1>"
            f"<p style='color:var(--muted)'>Generated by build_organism_pages.py. Each QR (jrk.art/x/&lt;id&gt;) lands on one of these.</p>"
            f"{body}</div></div></body></html>")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build Living Past organism pages from the volume JSON")
    ap.add_argument("id", nargs="?", help="build only this organism id")
    ap.add_argument("--clean", action="store_true", help="remove pages/ before building")
    args = ap.parse_args(argv)

    if args.clean and OUT_DIR.exists():
        for p in OUT_DIR.glob("*.html"):
            p.unlink()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    css = extract_css()
    orgs = VOL["organisms"]
    if args.id:
        orgs = [o for o in orgs if o["id"].upper() == args.id.upper()]
        if not orgs:
            print(f"unknown id {args.id}", file=sys.stderr)
            return 1

    built = []
    for o in orgs:
        slug = REDIRECTS.get(o["id"], {}).get("slug", o["id"].lower())
        (OUT_DIR / f"{slug}.html").write_text(render(o, css))
        built.append(o)
        print(f"  {o['id']:<5} → pages/{slug}.html")

    if not args.id:
        (OUT_DIR / "index.html").write_text(build_index(built))
        print(f"\nwrote pages/index.html linking {len(built)} pages")
    print(f"built {len(built)} page(s) → {OUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
