# Kronosaurus — Reference Materials

## What this folder is for
This folder holds all scientific reference materials for *Kronosaurus queenslandicus*:
skeletal diagrams, fossil photographs, life reconstructions, museum specimen
images, and texture studies. Everything here feeds directly into
scientifically accurate prompt engineering for Kronosaurus art generation.

## File naming convention
```
kronosaurus_[type]_[source]_[year].[ext]
```
Types: `skeletal`, `fossil`, `reconstruction`, `museum`, `texture`

Examples:
- `kronosaurus_skeletal_qm_2012.pdf`
- `kronosaurus_fossil_longman_1924.tif`
- `kronosaurus_reconstruction_witton_2020.tif`
- `kronosaurus_texture_skin_study_2018.tif`

Image format: minimum 4K resolution; RAW preferred for photography; TIF for
flatbed or photogrammetric scans.

## Real Animal Analogues for --sref

Use photographs of these living animals to supply `--sref` style references
for specific body regions and surface qualities:

- **Saltwater crocodile** (*Crocodylus porosus*) — jaw structure and scale
  texture. Photograph jaw from lateral and ventral angles showing tooth
  interlocking; close-up of dorsal scale mosaic pattern at high
  magnification for skin texture reference.
- **Orca** (*Orcinus orca*) — body mass distribution and overall bulk.
  Photograph full lateral profile underwater and at the surface; focus on
  the muscular, barrel-shaped torso proportions.
- **Elephant seal** (*Mirounga* spp.) — sheer bulk and mass impression.
  Photograph full body from lateral and three-quarter angles on land to
  capture the heavy, thick-bodied silhouette and skin folding.

## Image format guidance
- Minimum 4K (3840x2160) for usable reference
- RAW (.CR3, .ARW, .NEF) preferred for fossil and museum photography
- TIF (16-bit, uncompressed) for flatbed scans of skeletal diagrams
- PDF acceptable for published skeletal reconstructions

## MJ Prompt Notes — Kronosaurus

### CLIP-Optimized Shorthand
These comma-separated phrases are what the anatomy module injects into prompts:
```
  enormous skull on short thick neck
  four broad powerful paddle flippers
  massive barrel-shaped body
  robust conical 30cm teeth
  smooth scarred marine predator skin
  10m truck-sized pliosaur
```

### Recommended --stylize Range
| Low | Default | High |
|-----|---------|------|
| 100 | **150** | 300 |

Use `--stylize 150` as a starting point. Lower values (100) preserve more anatomical accuracy. Higher values (300) allow more MJ artistic interpretation.

### Known MJ Failures
Watch for these common misrenders:
- ❌ too many vertebrae — original Harvard mount was over-reconstructed
- ❌ long neck — short-necked pliosaur, not a plesiosaur

### --sref Test Results
| sref URL | Stylize | Result | Notes |
|----------|---------|--------|-------|
| *(add test results here)* | | | |
