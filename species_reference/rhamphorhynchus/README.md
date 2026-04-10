# Rhamphorhynchus — Reference Materials

## What this folder is for
This folder holds all scientific reference materials for *Rhamphorhynchus muensteri*:
skeletal diagrams, fossil photographs, life reconstructions, museum specimen
images, and texture studies. Everything here feeds directly into
scientifically accurate prompt engineering for Rhamphorhynchus art generation.

## File naming convention
```
rhamphorhynchus_[type]_[source]_[year].[ext]
```
Types: `skeletal`, `fossil`, `reconstruction`, `museum`, `texture`

Examples:
- `rhamphorhynchus_skeletal_bspg_2015.pdf`
- `rhamphorhynchus_fossil_solnhofen_1847.tif`
- `rhamphorhynchus_reconstruction_witton_2013.tif`
- `rhamphorhynchus_texture_wing_membrane_2016.tif`

Image format: minimum 4K resolution; RAW preferred for photography; TIF for
flatbed or photogrammetric scans.

## Real Animal Analogues for --sref

Use photographs of these living animals to supply `--sref` style references
for specific body regions and surface qualities:

- **Bat** (Chiroptera) — wing membrane structure and attachment points.
  Photograph wing membranes backlit to show vascular patterning and
  translucency; capture how the membrane stretches between elongated
  fingers and attaches to the body and hindlimbs.
- **Swallow** (*Hirundo* spp.) — flight agility and aerial maneuvering
  posture. Photograph or capture high-speed stills of banking turns,
  diving, and rapid directional changes; use for dynamic flight pose
  reference.
- **Flying fox** (*Pteropus* spp.) — membrane texture and surface quality
  at close range. Photograph wing membrane texture at high magnification
  showing the fine, leathery surface; also capture the fur-to-membrane
  transition zone on the body.

## Image format guidance
- Minimum 4K (3840x2160) for usable reference
- RAW (.CR3, .ARW, .NEF) preferred for fossil and museum photography
- TIF (16-bit, uncompressed) for flatbed scans of skeletal diagrams
- PDF acceptable for published skeletal reconstructions

## MJ Prompt Notes — Rhamphorhynchus

### CLIP-Optimized Shorthand
These comma-separated phrases are what the anatomy module injects into prompts:
```
  long bony tail with diamond vane tip
  forward-projecting interlocking needle teeth
  leathery wing membrane to ankles
  dense pycnofiber body fuzz
  crow-sized 1.8m wingspan pterosaur
```

### Recommended --stylize Range
| Low | Default | High |
|-----|---------|------|
| 100 | **150** | 300 |

Use `--stylize 150` as a starting point. Lower values (100) preserve more anatomical accuracy. Higher values (300) allow more MJ artistic interpretation.

### Known MJ Failures
Watch for these common misrenders:
- ❌ no tail — long bony tail with diamond vane is THE defining feature
- ❌ bat wings — membrane on elongated fourth finger, not between multiple fingers

### --sref Test Results
| sref URL | Stylize | Result | Notes |
|----------|---------|--------|-------|
| *(add test results here)* | | | |
