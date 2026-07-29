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

  /* ============================================================
     RESEARCH-PASS COMPONENTS (2026-07-29)
     Added, not redesigned: every one of these is built from the tokens the
     template already defines (--brass, --panel, --hair, the three fonts). No new
     colour, face or hierarchy is introduced.
     ============================================================ */

  /* "What the fossils tell us" — the epistemic spine of the page.
     It deliberately reuses the CONFIDENCE DOT that SCOPE §4 already locked for
     well-documented / reasonable-inference / speculative, because
     direct-evidence / supported-inference / artistic-reconstruction is the same
     distinction at paragraph scale. Filled, half, open — one vocabulary across
     the poster card, the hero badge and here, so a reader who learns it once
     can read it everywhere. */
  .evidence{ display:grid; gap:1px; background:var(--hair); border:1px solid var(--hair);
    border-radius:10px; overflow:hidden; margin:6px 0 4px; }
  .ev{ background:var(--panel); padding:16px 18px; }
  .ev .evh{ display:flex; align-items:center; gap:9px; margin:0 0 9px; }
  .ev .evd{ width:11px; height:11px; border-radius:50%; border:1px solid var(--brass); flex:none; }
  .ev .evd.filled{ background:var(--brass); }
  .ev .evd.half{ background:linear-gradient(90deg,var(--brass) 0 50%,transparent 50%); }
  .ev .evd.open{ background:transparent; }
  .ev .evt{ font-family:var(--sans); font-size:10.5px; letter-spacing:.18em; text-transform:uppercase;
    color:var(--brass-hi); }
  .ev ul{ list-style:none; margin:0; padding:0; }
  .ev li{ font-family:var(--sans); font-size:14.5px; line-height:1.62; color:#e4dabf;
    padding:6px 0 6px 15px; position:relative; letter-spacing:.005em; }
  .ev li::before{ content:"·"; position:absolute; left:3px; color:var(--brass); }
  .ev.recon li{ color:#cfc3a6; font-style:italic; }

  /* per-fact citation markers, so a claim and its source are never separated */
  .cite{ font-family:var(--sans); font-size:10.5px; letter-spacing:.06em; color:var(--brass);
    vertical-align:super; margin-left:3px; text-decoration:none; }
  .cite:hover{ color:var(--brass-hi); }

  /* Deeper dive — editorially selected further reading. `kind` is shown so a
     reader can tell a paper from a museum before clicking. */
  .dive{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:6px 0 0; }
  @media(max-width:760px){ .dive{ grid-template-columns:1fr; } }
  .dive a{ display:block; text-decoration:none; background:var(--panel); border:1px solid var(--hair);
    border-radius:10px; padding:16px; transition:border-color .15s ease, transform .15s ease; }
  .dive a:hover{ border-color:var(--brass); transform:translateY(-1px); }
  .dive .k{ font-family:var(--sans); font-size:9.5px; letter-spacing:.2em; text-transform:uppercase;
    color:var(--brass); }
  .dive .t{ font-family:var(--body); font-size:16px; line-height:1.34; color:var(--ivory); margin:7px 0 6px; }
  .dive .m{ font-family:var(--sans); font-size:12.5px; line-height:1.55; color:var(--muted); }
  .dive .who{ font-family:var(--sans); font-size:11px; color:#8a7c60; margin-top:8px; }

  /* Scientific status. Deliberately plain: this is the honesty layer, and dressing
     it up would undercut it. */
  .status .row{ display:flex; justify-content:space-between; gap:12px; font-family:var(--sans);
    font-size:12px; color:var(--muted); padding:7px 0; border-top:1px solid var(--hair); }
  .status .row:first-of-type{ border-top:none; }
  .status .row b{ color:#d8cdb0; font-weight:400; }
  .status .note{ font-family:var(--sans); font-size:12.5px; line-height:1.6; color:#bdb094;
    margin:10px 0 0; }

  /* Publication gate — only rendered when a record carries an unresolved
     verification requirement. It must be impossible to miss. */
  .gate{ border:1px solid #c0442f88; background:linear-gradient(160deg,#22110e,#160d0b);
    border-radius:10px; padding:16px 18px; margin:0 0 26px; }
  .gate .gt{ font-family:var(--sans); font-size:10.5px; letter-spacing:.2em; text-transform:uppercase;
    color:#e08a72; }
  .gate p{ font-family:var(--sans); font-size:13.5px; line-height:1.6; color:#e8cfc6; margin:8px 0 0; }

  /* full source list */
  .srclist{ list-style:none; margin:0; padding:0; }
  .srclist li{ font-family:var(--sans); font-size:12px; line-height:1.55; color:var(--muted);
    padding:9px 0 9px 26px; border-top:1px solid var(--hair); position:relative; }
  .srclist li:first-child{ border-top:none; }
  .srclist .n{ position:absolute; left:0; top:9px; color:var(--brass); font-size:11px; }
  .srclist a{ color:var(--brass-hi); text-decoration:none; }
  .srclist a:hover{ text-decoration:underline; }
  .srclist .ty{ color:#6f6552; }

  /* return-to-the-world CTA */
  .backworld{ display:flex; align-items:center; justify-content:space-between; gap:18px; flex-wrap:wrap;
    border:1px solid var(--hair); border-radius:12px; background:var(--panel); padding:18px 20px;
    margin:34px 0 0; }
  .backworld p{ font-family:var(--body); font-style:italic; font-size:17px; color:#e6d9b8; margin:0; }
"""


RESEARCH_DIR = LP / "research"
# ---- the editorial pass, loaded as a SECOND data source -----------------------------------------
# The roster (volume_v.json) and the research records overlap, and which one wins matters, so it is
# declared rather than left to dict-update order.
#
#   volume_v.json is authoritative for anything the POSTER is built from — section, position,
#   confidence, ageRange_Ma, stage, and the `size` string that place_on_backdrop parses into pixels.
#   Letting prose overwrite those would let an editing pass silently move an animal or resize it.
#
#   the research record is authoritative for everything a READER sees — blurb, notes, funFacts,
#   survivor, distribution, fossilEvidence, deeperDive, scientificReview, references — plus two
#   fields the roster never had: `pronunciation` and `habitat`.
#
# `size` is the interesting case. The research copy carries dual metric/imperial ("12–13 m (39–43 ft)")
# which is what SCOPE §5 actually asks a card to show, while the roster's "12-13 m" is what the scale
# maths needs. So they are kept apart: `sizeDisplay` for the page, `size` untouched for geometry.
ROSTER_AUTHORITY = ("section", "position", "confidence", "ageRange_Ma", "stage", "status", "size")
EDITORIAL_FIELDS = ("blurb", "notes", "funFacts", "funFactSources", "survivor", "distribution",
                    "fossilEvidence", "deeperDive", "scientificReview", "contentVersion",
                    "lastReviewed", "references", "pronunciation", "habitat", "slug")
CONFLICTS: list[str] = []

# ---- editorial holds the DATA does not yet carry ------------------------------------------------
# Kept here rather than edited into the research records, so the provenance stays clean: these are
# production decisions about what may publish, not findings from the research pass. A record listed
# here renders the same visible hold banner a record with a non-default review status gets, because
# a caveat only a maintainer can see is not a caveat.
EDITORIAL_HOLDS = {
    "CR03": ("Pending sourced update",
             "This reconstruction predates the 2025 Edmontosaurus mummy work on a midline fleshy "
             "crest and hoof-like foot anatomy. The page will be revised once that material is "
             "cited; nothing has been added here from unsourced artwork."),
}


def load_research() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for f in sorted(RESEARCH_DIR.glob("*_content.json")):
        try:
            rec = json.loads(f.read_text())
        except json.JSONDecodeError as e:
            CONFLICTS.append(f"{f.name}: unreadable JSON — {e}")
            continue
        rid = rec.get("id")
        if not rid:
            CONFLICTS.append(f"{f.name}: no id field")
            continue
        out[rid] = rec
    return out


RESEARCH = load_research()


def merge(vol_rec: dict) -> dict:
    """Roster record + editorial record, with conflicts reported instead of resolved silently."""
    oid = vol_rec["id"]
    res = RESEARCH.get(oid)
    if not res:
        CONFLICTS.append(f"{oid}: no research content record — page renders with placeholders")
        return dict(vol_rec)
    merged = dict(vol_rec)
    # Anything the roster owns is compared, never replaced. A disagreement here means the two files
    # have drifted, which is worth a human look — it is exactly how a confidence badge ends up
    # claiming more than the research behind it supports.
    for k in ROSTER_AUTHORITY:
        if k in res and k in vol_rec and res[k] != vol_rec[k]:
            CONFLICTS.append(f"{oid}.{k}: roster={vol_rec[k]!r} research={res[k]!r} — roster kept")
    for k in EDITORIAL_FIELDS:
        if k in res:
            merged[k] = res[k]
    if res.get("size") and res["size"] != vol_rec.get("size"):
        merged["sizeDisplay"] = res["size"]
    return merged


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
    ref_index = {r.get("id"): i + 1 for i, r in enumerate(refs)}
    if refs:
        items = []
        for i, r in enumerate(refs):
            url = r.get("url") or r.get("doi") or ""
            auth = r.get("authors") or []
            who = auth[0].split()[-1] if auth else ""
            if len(auth) > 1:
                who += " et al."
            yr = r.get("year")
            bits = " · ".join(str(b) for b in (who, yr) if b)
            ty = r.get("sourceType", "")
            ttl = esc(r.get("title", "Untitled"))
            link = f'<a href="{esc(url)}" rel="noopener">{ttl}</a>' if url else ttl
            items.append(f'          <li id="ref{i+1}"><span class="n">{i+1}</span>{link}'
                         + (f'<br>{esc(bits)}' if bits else "")
                         + (f' <span class="ty">· {esc(ty)}</span>' if ty else "")
                         + "</li>")
        refs_html = '<ol class="srclist">\n' + "\n".join(items) + "\n        </ol>"
    else:
        refs_html = '<span class="todo">No sources entered yet — <code>references[]</code> empty.</span>'

    # ---- "In this world": the record already arrives in paragraphs, so keep them ----
    # 4,200 characters is a genuine amount of reading. It survives only because it is written as
    # eight ~540-character paragraphs; rendered as one block it would be a wall on a phone.
    notes_raw = (o.get("notes") or "").strip()
    if notes_raw:
        paras = [p.strip() for p in re.split(r"\n\s*\n", notes_raw) if p.strip()]
        notes_html = "\n        ".join(f'<p class="body-copy">{esc(p)}</p>' for p in paras)
    else:
        notes_html = ('<p class="body-copy todo">Extended, sourced anatomy &amp; ecology write-up '
                      "pending (demoted from the poster per Law #3).</p>")

    # ---- field notes, each carrying its own citation ----
    # funFactSources maps fact index -> referenceIds. Rendering the marker next to the claim keeps a
    # statement and its evidence in the same breath, which is the whole trust proposition.
    src_by_index = {s.get("index"): s for s in (o.get("funFactSources") or [])}
    if funfacts:
        rows = []
        for i, x in enumerate(funfacts):
            marks = ""
            for rid in (src_by_index.get(i, {}).get("referenceIds") or []):
                n = ref_index.get(rid)
                if n:
                    marks += f'<a class="cite" href="#ref{n}">[{n}]</a>'
            rows.append(f"          <li>{esc(x)}{marks}</li>")
        ff = "\n".join(rows)

    # ---- what the fossils tell us ----
    fe = o.get("fossilEvidence") or {}
    EV = (("directEvidence", "filled", "Known from fossils", ""),
          ("supportedInference", "half", "Supported inference", ""),
          ("artisticReconstruction", "open", "Artistic reconstruction", " recon"))
    ev_blocks = []
    for key, dot, label, extra in EV:
        rows = fe.get(key) or []
        if not rows:
            continue
        lis = "\n".join(f"            <li>{esc(r)}</li>" for r in rows)
        ev_blocks.append(
            f'          <div class="ev{extra}">\n'
            f'            <div class="evh"><span class="evd {dot}"></span>'
            f'<span class="evt">{label}</span></div>\n'
            f"            <ul>\n{lis}\n            </ul>\n"
            f"          </div>")
    evidence_html = ('<div class="evidence">\n' + "\n".join(ev_blocks) + "\n        </div>"
                     ) if ev_blocks else '<p class="todo">Evidence breakdown pending.</p>'

    # ---- deeper dive ----
    KIND = {"research": "Research", "museum": "Museum", "public_resource": "Resource"}
    dives = o.get("deeperDive") or []
    if dives:
        cards = []
        for d in dives:
            who = " · ".join(str(b) for b in (d.get("creator"), d.get("year")) if b)
            cards.append(
                f'          <a href="{esc(d.get("url","#"))}" rel="noopener">\n'
                f'            <div class="k">{esc(KIND.get(d.get("kind",""), d.get("kind","")))}</div>\n'
                f'            <div class="t">{esc(d.get("title",""))}</div>\n'
                f'            <div class="m">{esc(d.get("description",""))}</div>\n'
                + (f'            <div class="who">{esc(who)}</div>\n' if who else "")
                + "          </a>")
        dive_html = '<div class="dive">\n' + "\n".join(cards) + "\n        </div>"
    else:
        dive_html = '<p class="todo">Further reading pending.</p>'

    # ---- scientific status, and the publication gate ----
    rev = o.get("scientificReview") or {}
    rev_status = rev.get("status") or "Not externally reviewed"
    reviewers = rev.get("reviewedBy") or []
    # Never imply review that has not happened: a name only appears if the record carries one, and
    # the default state is stated plainly rather than left blank.
    who_rev = ", ".join(esc(r) for r in reviewers) if reviewers else "—"
    status_rows = [
        f'          <div class="row"><span>Review status</span><b>{esc(rev_status)}</b></div>',
        f'          <div class="row"><span>Reviewed by</span><b>{who_rev}</b></div>',
        f'          <div class="row"><span>Content version</span><b>{esc(o.get("contentVersion","—"))}</b></div>',
        f'          <div class="row"><span>Last reviewed</span><b>{esc(o.get("lastReviewed","—"))}</b></div>',
        f'          <div class="row"><span>Reconstruction</span><b>{esc(conf_text)}</b></div>',
    ]
    note = rev.get("editorialNote")
    status_html = "\n".join(status_rows) + (
        f'\n          <p class="note">{esc(note)}</p>' if note else "")

    # A record whose review status is not the ordinary default is carrying an unresolved question.
    # It gets a banner at the top of the page rather than a line in a table at the bottom.
    gate_html = ""
    hold = EDITORIAL_HOLDS.get(oid)
    if rev_status != "Not externally reviewed":
        gate_html = ('<div class="gate">\n'
                     f'          <div class="gt">Editorial hold · {esc(rev_status)}</div>\n'
                     f'          <p>{esc(note or "This record carries an unresolved verification requirement and is not presented as settled fact.")}</p>\n'
                     "        </div>")
    elif hold:
        gate_html = ('<div class="gate">\n'
                     f'          <div class="gt">Editorial hold · {esc(hold[0])}</div>\n'
                     f'          <p>{esc(hold[1])}</p>\n'
                     "        </div>")

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
      <div class="f"><div class="fl">Size</div><div class="fv">{esc(o.get('sizeDisplay') or o.get('size','—'))}</div></div>
      <div class="f"><div class="fl">When</div><div class="fv">{esc(era_str)}</div></div>
      <div class="f"><div class="fl">Diet</div><div class="fv">{esc(diet or '—')}</div></div>
      <div class="f"><div class="fl">Habitat</div><div class="fv">{esc(habitat)}</div></div>
    </div>

    <div class="cols">
      <div class="main">
        {gate_html}
        {blurb}

        <h2>In this world</h2>
        {notes_html}

        <h2 style="margin-top:30px">Field notes</h2>
        <ul class="funfacts">
{ff}
        </ul>

        <h2 style="margin-top:34px">What the fossils tell us</h2>
        {evidence_html}

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

        <div class="card status">
          <h2 style="border:none;margin:0 0 8px;padding:0">Scientific status</h2>
{status_html}
        </div>
      </div>
    </div>
  </div>

  <div class="wrap">
    <h2 style="margin-top:40px">Deeper dive</h2>
    {dive_html}
  </div>

  <div class="wrap">
    <div class="backworld">
      <p>{esc(common)} is one of 32 organisms sharing a single world.</p>
      <a class="btn s" style="margin:0;min-width:210px" href="../poster_mockup_live.html?only=1">Return to the world ↗</a>
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
        rec = merge(o)
        # the record's own slug wins over the redirect table when it has one — the research pass set
        # slugs deliberately, and the redirect layer maps ID -> current page rather than the reverse
        slug = rec.get("slug") or REDIRECTS.get(o["id"], {}).get("slug", o["id"].lower())
        (OUT_DIR / f"{slug}.html").write_text(render(rec, css))
        built.append(rec)
        words = len((rec.get("notes") or "").split())
        flag = "  ⚠ editorial hold" if (rec.get("scientificReview") or {}).get(
            "status", "Not externally reviewed") != "Not externally reviewed" else ""
        print(f"  {o['id']:<5} → pages/{slug}.html   {words:>4} words"
              f"  {len(rec.get('references') or [])} refs{flag}")

    if not args.id:
        (OUT_DIR / "index.html").write_text(build_index(built))
        print(f"\nwrote pages/index.html linking {len(built)} pages")
    print(f"built {len(built)} page(s) → {OUT_DIR}")
    if CONFLICTS:
        print(f"\n{len(CONFLICTS)} data issue(s) — reported, not silently resolved:")
        for c in CONFLICTS:
            print(f"  · {c}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
