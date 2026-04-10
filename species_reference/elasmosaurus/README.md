# Elasmosaurus — Reference Materials

## What this folder is for
This folder holds all scientific reference materials for *Elasmosaurus platyurus*:
skeletal diagrams, fossil photographs, life reconstructions, museum specimen
images, and texture studies. Everything here feeds directly into
scientifically accurate prompt engineering for Elasmosaurus art generation.

## File naming convention
```
elasmosaurus_[type]_[source]_[year].[ext]
```
Types: `skeletal`, `fossil`, `reconstruction`, `museum`, `texture`

Examples:
- `elasmosaurus_skeletal_ansp_2010.pdf`
- `elasmosaurus_fossil_cope_1868.tif`
- `elasmosaurus_reconstruction_oneill_2020.tif`
- `elasmosaurus_texture_skin_study_2019.tif`

Image format: minimum 4K resolution; RAW preferred for photography; TIF for
flatbed or photogrammetric scans.

## Real Animal Analogues for --sref

Use photographs of these living animals to supply `--sref` style references
for specific body regions and surface qualities:

- **Sea turtle** (Cheloniidae / *Dermochelys*) — flipper shape, flipper
  stroke mechanics, and underwater swimming posture. Photograph flippers
  mid-stroke from lateral and ventral angles; capture full-body swimming
  profile.
- **Swan** (*Cygnus* spp.) — long neck proportions and curvature. Photograph
  the neck in extended, S-curved, and retracted positions to study the range
  of cervical flexibility. Focus on proportional length of neck vs body.
- **Leatherback turtle** (*Dermochelys coriacea*) — skin texture and
  surface quality. Photograph dorsal and ventral hide at close range to
  capture the smooth, ridged, leathery texture without visible scales.

## Image format guidance
- Minimum 4K (3840x2160) for usable reference
- RAW (.CR3, .ARW, .NEF) preferred for fossil and museum photography
- TIF (16-bit, uncompressed) for flatbed scans of skeletal diagrams
- PDF acceptable for published skeletal reconstructions

## MJ Prompt Notes — Elasmosaurus

### CLIP-Optimized Shorthand
These comma-separated phrases are what the anatomy module injects into prompts:
```
  impossibly long sinuous neck tiny head
  four large paddle-shaped flippers
  needle-like interlocking fish-trap teeth
  compact rounded torso short tail
  smooth countershaded marine hide
  14m plesiosaur neck over half body length
```

### Recommended --stylize Range
| Low | Default | High |
|-----|---------|------|
| 100 | **150** | 300 |

Use `--stylize 150` as a starting point. Lower values (100) preserve more anatomical accuracy. Higher values (300) allow more MJ artistic interpretation.

### Known MJ Failures
Watch for these common misrenders:
- ❌ swan-neck pose — could NOT raise neck high out of water; neck moved horizontally
- ❌ Loch Ness monster pose — classic humped pose is physically impossible
- ❌ on land — fully aquatic, could not move on land

### --sref Test Results
| sref URL | Stylize | Result | Notes |
|----------|---------|--------|-------|
| *(add test results here)* | | | |
