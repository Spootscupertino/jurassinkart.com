# Dimorphodon — Reference Materials

## What this folder is for
This folder holds all scientific reference materials for *Dimorphodon macronyx*:
skeletal diagrams, fossil photographs, life reconstructions, museum specimen
images, and texture studies. Everything here feeds directly into
scientifically accurate prompt engineering for Dimorphodon art generation.

## File naming convention
```
dimorphodon_[type]_[source]_[year].[ext]
```
Types: `skeletal`, `fossil`, `reconstruction`, `museum`, `texture`

Examples:
- `dimorphodon_skeletal_nhmuk_2014.pdf`
- `dimorphodon_fossil_buckland_1829.tif`
- `dimorphodon_reconstruction_witton_2015.tif`
- `dimorphodon_texture_wing_membrane_2017.tif`

Image format: minimum 4K resolution; RAW preferred for photography; TIF for
flatbed or photogrammetric scans.

## Real Animal Analogues for --sref

Use photographs of these living animals to supply `--sref` style references
for specific body regions and surface qualities:

- **Puffin** (*Fratercula* spp.) — head proportions and beak shape.
  Photograph head from lateral, frontal, and three-quarter angles; focus on
  the oversized, deep beak relative to skull size and the large, rounded
  head profile.
- **Bat** (Chiroptera) — wing membrane structure and attachment. Photograph
  wing membranes backlit to capture translucency and vascular patterning;
  detail shots of membrane attachment to elongated finger bones and body.
- **Toucan** (*Ramphastos* spp.) — oversized bill proportions. Photograph
  head and bill from lateral and three-quarter angles; capture the dramatic
  bill-to-skull size ratio and the lightweight, hollow bill structure for
  proportional reference.

## Image format guidance
- Minimum 4K (3840x2160) for usable reference
- RAW (.CR3, .ARW, .NEF) preferred for fossil and museum photography
- TIF (16-bit, uncompressed) for flatbed scans of skeletal diagrams
- PDF acceptable for published skeletal reconstructions

## MJ Prompt Notes — Dimorphodon

### CLIP-Optimized Shorthand
These comma-separated phrases are what the anatomy module injects into prompts:
```
  oversized deep puffin-like skull
  two tooth types large front fangs small rear
  short broad maneuverable wings
  pycnofiber-covered compact body
  long stiffened bony tail
  pigeon-sized 1.4m wingspan early pterosaur
```

### Recommended --stylize Range
| Low | Default | High |
|-----|---------|------|
| 100 | **150** | 300 |

Use `--stylize 150` as a starting point. Lower values (100) preserve more anatomical accuracy. Higher values (300) allow more MJ artistic interpretation.

### Known MJ Failures
Watch for these common misrenders:
- ❌ normal-sized head — head must appear OVERSIZED relative to body
- ❌ no tail — has a long stiffened bony tail

### --sref Test Results
| sref URL | Stylize | Result | Notes |
|----------|---------|--------|-------|
| *(add test results here)* | | | |
