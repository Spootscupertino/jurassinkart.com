# Pteranodon — Reference Materials

## What this folder is for
This folder holds all scientific reference materials for *Pteranodon longiceps*
and *P. sternbergi*: skeletal diagrams, specimen photographs, wing membrane
studies, crest dimorphism data, and museum specimen images. All content here
supports scientifically accurate prompt engineering.

**CRITICAL TAXONOMY NOTE**: *Pteranodon* is NOT a dinosaur. It is a pterosaur —
a flying reptile on a completely separate evolutionary lineage from dinosaurs.
*Pteranodon* and dinosaurs were contemporaneous but only distantly related
(both are archosaurs). This distinction must be noted in all prompt work.
Do not label *Pteranodon* as a dinosaur in any caption or metadata.

## File naming convention
```
pteranodon_[type]_[source]_[year].[ext]
```
Types: `skeletal`, `fossil`, `reconstruction`, `museum`, `texture`

Examples:
- `pteranodon_skeletal_fhsm_vp2183_scan.tif`
- `pteranodon_fossil_ypm_2473_2001.tif`
- `pteranodon_reconstruction_witton_2013.tif`

Image format: minimum 4K resolution; RAW preferred; TIF for scans.

## Priority reference materials

1. **FHSM VP-2183** — Fort Hays State University, Hays KS
   One of the best-preserved *Pteranodon* specimens. Sternberg Museum of
   Natural History. Includes skull with full crest and partial skeleton.
   Large male (*P. longiceps* morphology).

2. **YPM VP 002473** — Yale Peabody Museum, New Haven CT
   Key specimen from Marsh's original Niobrara Formation collections.
   Peabody has an extensive *Pteranodon* collection critical for wing
   membrane shape and proportions.

3. **Bennett 2001** (Journal of Vertebrate Paleontology)
   Comprehensive monograph on *Pteranodon* taxonomy and sexual dimorphism.
   Males: large crests, narrow pelvis. Females: small/no crests, wider
   pelvis for egg-laying. Essential for sex-specific depiction.

4. **Habib 2008** (Zitteliana)
   Quadrupedal launch biomechanics — *Pteranodon* launched like a pole-
   vaulter, using all four limbs, hindlimbs last. Did NOT run and flap.
   Critical for any take-off or landing pose.

5. **Witton 2013** — *Pterosaurs: Natural History, Evolution, Anatomy*
   Princeton University Press. Best single reference for pterosaur life
   appearance, wing proportions, and locomotion. Includes *Pteranodon*
   chapter with up-to-date reconstruction.

6. **Pycnofibers documentation** — *Pteranodon* and pterosaurs generally
   were covered in pycnofibers: short, hair-like filaments. These are NOT
   feathers. Different structure, different evolutionary origin.

7. **Kellner et al. (various)** — Wing membrane studies
   Actinofibrils (stiff fibres) in the patagium created a semi-rigid wing.
   The wing attached to the ankle or upper hindlimb (debate ongoing).

## What to look for / photograph / scan

- **Crest**: Backward-projecting bony crest on male skulls; highly variable
  between individuals. In life, crest may have extended further with soft
  tissue. No soft-tissue crest evidence in females.
- **Wing membrane**: Attached from elongated fourth finger to body/hindlimb.
  Patagium was not a simple sheet — it had internal actinofibrils for
  stiffness and camber control.
- **Toothless beak**: No teeth — long, pointed beak for catching fish.
- **Body size**: Wingspan ~5–6 m (males); body was relatively small and
  lightweight (~25 kg estimated).
- **Pycnofibers**: Short, stiff fibers cover the body. Photograph any
  pterosaur specimens showing soft-tissue fiber preservation (Sordes,
  Jeholopterus have good examples).
- **Ground posture**: Quadrupedal at rest; wings folded against body.
  Hindlimbs smaller but functional; plantigrade or semi-plantigrade stance.

## Image format guidance
- Minimum 4K (3840×2160)
- RAW preferred for museum photography
- TIF for wing membrane and skeletal diagram scans
- Transmitted or raking light useful for wing membrane specimen photography

## MJ Prompt Notes — Pteranodon

### CLIP-Optimized Shorthand
These comma-separated phrases are what the anatomy module injects into prompts:
```
  long backward-sweeping bony cranial crest
  toothless pointed beak pelican-like
  taut wing membrane to ankles
  fuzzy pycnofiber body covering
  tiny body 7m wingspan 25kg
  quadrupedal on ground folded wings
```

### Recommended --stylize Range
| Low | Default | High |
|-----|---------|------|
| 75 | **125** | 250 |

Use `--stylize 125` as a starting point. Lower values (75) preserve more anatomical accuracy. Higher values (250) allow more MJ artistic interpretation.

### Known MJ Failures
Watch for these common misrenders:
- ❌ teeth — Pteranodon is TOOTHLESS; name literally means 'toothless wing'
- ❌ bat wings — membrane attaches to single elongated fourth finger, not between multiple fingers
- ❌ bipedal running — quadrupedal launch from all fours; walked on folded wings
- ❌ dinosaur — NOT a dinosaur; a pterosaur, completely separate lineage

### --sref Test Results
| sref URL | Stylize | Result | Notes |
|----------|---------|--------|-------|
| *(add test results here)* | | | |
