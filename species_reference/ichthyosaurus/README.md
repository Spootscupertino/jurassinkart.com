# Ichthyosaurus — Reference Materials

## What this folder is for
This folder holds all scientific reference materials for *Ichthyosaurus communis*:
skeletal diagrams, fossil photographs, life reconstructions, museum specimen
images, and texture studies. Everything here feeds directly into
scientifically accurate prompt engineering for Ichthyosaurus art generation.

## File naming convention
```
ichthyosaurus_[type]_[source]_[year].[ext]
```
Types: `skeletal`, `fossil`, `reconstruction`, `museum`, `texture`

Examples:
- `ichthyosaurus_skeletal_nhmuk_2015.pdf`
- `ichthyosaurus_fossil_anning_1821.tif`
- `ichthyosaurus_reconstruction_motani_2005.tif`
- `ichthyosaurus_texture_skin_impression_2010.tif`

Image format: minimum 4K resolution; RAW preferred for photography; TIF for
flatbed or photogrammetric scans.

## Real Animal Analogues for --sref

Use photographs of these living animals to supply `--sref` style references
for specific body regions and surface qualities:

- **Dolphin** (*Tursiops* / *Delphinus* spp.) — overall fusiform body shape
  and swimming posture. Photograph full lateral profile underwater and at
  the surface; capture dorsal fin shape and tail fluke orientation
  (note: ichthyosaur tail is vertical, unlike horizontal dolphin fluke --
  use for body contour only).
- **Tuna** (*Thunnus* spp.) — streamlined hydrodynamic body shape and
  smooth skin surface. Photograph lateral profile showing the torpedo-like
  cross-section; detail shots of skin texture for surface quality reference.
- **Porpoise** (*Phocoena* spp.) — snout shape and head proportions.
  Photograph head from lateral and dorsal angles; focus on the blunt,
  rounded rostrum shape and eye placement.

## Image format guidance
- Minimum 4K (3840x2160) for usable reference
- RAW (.CR3, .ARW, .NEF) preferred for fossil and museum photography
- TIF (16-bit, uncompressed) for flatbed scans of skeletal diagrams
- PDF acceptable for published skeletal reconstructions

## MJ Prompt Notes — Ichthyosaurus

### CLIP-Optimized Shorthand
These comma-separated phrases are what the anatomy module injects into prompts:
```
  dolphin-shaped with enormous round eyes
  bony sclerotic eye ring
  smooth scaleless skin like dolphin
  soft-tissue dorsal fin no bone
  crescent tail fluke vertebrae bend down
  2m dolphin-sized marine reptile
```

### Recommended --stylize Range
| Low | Default | High |
|-----|---------|------|
| 100 | **150** | 300 |

Use `--stylize 150` as a starting point. Lower values (100) preserve more anatomical accuracy. Higher values (300) allow more MJ artistic interpretation.

### Known MJ Failures
Watch for these common misrenders:
- ❌ scales — smooth scaleless skin, NOT scaly like a lizard
- ❌ no dorsal fin — dorsal fin is soft-tissue only but DID exist
- ❌ upward tail bend — vertebrae bend DOWNWARD into lower fluke lobe

### --sref Test Results
| sref URL | Stylize | Result | Notes |
|----------|---------|--------|-------|
| *(add test results here)* | | | |
