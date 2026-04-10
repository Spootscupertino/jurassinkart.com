# Tyrannosaurus rex — Reference Materials

## What this folder is for
This folder holds all scientific reference materials for *Tyrannosaurus rex*:
skeletal diagrams, fossil photographs, life reconstructions, museum specimen
images, and texture studies. Everything here feeds directly into
scientifically accurate prompt engineering for T. rex art generation.

## File naming convention
```
tyrannosaurus_rex_[type]_[source]_[year].[ext]
```
Types: `skeletal`, `fossil`, `reconstruction`, `museum`, `texture`

Examples:
- `tyrannosaurus_rex_skeletal_fmnh_2017.pdf`
- `tyrannosaurus_rex_fossil_mor_2003.tif`
- `tyrannosaurus_rex_reconstruction_paul_1988.tif`
- `tyrannosaurus_rex_texture_bell_2017.tif`

Image format: minimum 4K resolution; RAW preferred for photography; TIF for
flatbed or photogrammetric scans.

## Priority reference materials

1. **FMNH PR 2081 "Sue"** — Field Museum of Natural History, Chicago
   Most complete T. rex known (~90%). Full mounted skeleton on public display.
   Photograph the skull separately (FMNH has a separate skull display with
   the correct articulation). Note: the mounted skeleton uses an incorrect
   fibula; verified in Brochu 2003.

2. **RSM P.2523.8 "Scotty"** — Royal Saskatchewan Museum, Canada
   Largest T. rex by body mass estimate (~8,800 kg). Good for overall
   proportions of a fully mature individual. Published fully in Scott et al.
   2019 (PeerJ).

3. **MOR 980 "B-rex"** — Museum of the Rockies, Bozeman MT
   Female specimen with medullary bone evidence. Key for understanding
   sexual dimorphism. Horner & Padian 2004 (Proceedings of the Royal Society).

4. **AMNH 5027** — American Museum of Natural History, New York
   Historic specimen; older mount but skull is well-preserved and
   extensively studied. Good early reference for skull shape cross-checking.

5. **Bell et al. 2017 skin study** (PLOS Biology, doi:10.1371/journal.pbio.1002467)
   Describes scales confirmed from neck, abdomen, hips, and tail base.
   Critical: no feather evidence in adults. Source all illustrated body
   regions from this paper.

6. **Persons & Currie 2011** (Acta Palaeontologica Polonica, doi:10.4202/app.2009.0055)
   Tail musculature reconstruction. Confirms M. caudofemoralis bulk —
   tail must be drawn as deeply muscled, horizontal, clear of the ground.

7. **Hutchinson & Garcia 2002** (Nature, doi:10.1038/nature01138)
   Locomotion biomechanics. Max speed 12–25 km/h. T. rex was a slow,
   deliberate mover — not a sprinter. Important for action pose accuracy.

## What to look for / photograph / scan

- **Skull**: Binocular vision orbit orientation; deep postorbital boss;
  serrated, banana-thick teeth (D-shaped cross-section, not blade-like);
  fenestrae proportions; short foreshortened snout of mature adults.
- **Forelimbs**: Two-fingered manus; extreme reduction; palms face each
  other (medially), NOT downward. Supination was anatomically impossible.
- **Hindlimbs**: Proportionally massive femur vs tibia; arctometatarsalian
  foot (third metatarsal pinched at top); four toes, first digit vestigial.
- **Tail**: Deep base reflecting massive M. caudofemoralis; horizontal
  posture confirmed. Avoid any sag or dragging.
- **Integument**: Scales only in all known adult skin patches. Photograph
  the Bell et al. specimen regions. Scale texture is pebbly/mosaic.
- **Size context**: Scan full skeletal mounts alongside human silhouette
  for scale reference. Sue stands ~3.66 m at the hips.

## Image format guidance
- Minimum 4K (3840×2160) for usable reference
- RAW (.CR3, .ARW, .NEF) preferred for fossil and museum photography
- TIF (16-bit, uncompressed) for flatbed scans of skeletal diagrams
- PDF acceptable for published skeletal reconstructions (Greg Paul, Scott
  Hartman)

## MJ Prompt Notes — Tyrannosaurus rex

### CLIP-Optimized Shorthand
These comma-separated phrases are what the anatomy module injects into prompts:
```
  massive deep skull with binocular eyes
  tiny two-fingered arms
  pebbly non-overlapping scales
  thick horizontal tail as counterbalance
  powerful pillar-like biped legs
  serrated banana-shaped teeth
  12m long bus-sized predator
```

### Recommended --stylize Range
| Low | Default | High |
|-----|---------|------|
| 50 | **100** | 200 |

Use `--stylize 100` as a starting point. Lower values (50) preserve more anatomical accuracy. Higher values (200) allow more MJ artistic interpretation.

### Known MJ Failures
Watch for these common misrenders:
- ❌ three-fingered arms — MJ defaults to three fingers; must specify two
- ❌ dragging tail — MJ defaults to tail on ground; must specify horizontal
- ❌ pronated wrists — MJ renders palms-down; correct is palms-inward
- ❌ exposed teeth when mouth closed — lips probable, teeth covered
- ❌ feathered T. rex — adult skin impressions confirm scales, not feathers

### --sref Test Results
| sref URL | Stylize | Result | Notes |
|----------|---------|--------|-------|
| *(add test results here)* | | | |
