# Brachiosaurus — Reference Materials

## What this folder is for
This folder holds all scientific reference materials for *Brachiosaurus
altithorax* (Morrison Formation, USA only): skeletal diagrams, fossil
photographs, posture studies, and museum specimen images. All content here
supports scientifically accurate prompt engineering.

**IMPORTANT**: African specimens (Tendaguru Formation, Tanzania) previously
assigned to *Brachiosaurus brancai* are now a separate genus: *Giraffatitan
brancai* (Taylor 2009). The famous Berlin HMN SII skeleton is *Giraffatitan*,
NOT *Brachiosaurus*. True *Brachiosaurus* is known only from the Morrison
Formation, USA. Maintain separate folders if working with both taxa.

## File naming convention
```
brachiosaurus_[type]_[source]_[year].[ext]
```
Types: `skeletal`, `fossil`, `reconstruction`, `museum`, `texture`

Examples:
- `brachiosaurus_skeletal_fmnh_p25107_scan.tif`
- `brachiosaurus_fossil_fruita_co_type_locality.tif`
- `brachiosaurus_reconstruction_taylor_2009.tif`

Image format: minimum 4K resolution; RAW preferred; TIF for scans.

## Priority reference materials

1. **FMNH P25107** — Field Museum of Natural History, Chicago
   Partial skeleton including forelimb, scapulocoracoid, sacrum — key
   material for *B. altithorax*. The type locality is Fruita, Colorado
   (Morrison Formation, Brushy Basin Member, ~150 Ma).

2. **Taylor 2009** (Journal of Vertebrate Paleontology, doi:10.1671/039.029.0401)
   The paper separating *Brachiosaurus* from *Giraffatitan*. Essential
   reading for understanding what's genuinely known about each genus.
   Detailed anatomical differences: pubis shape, dorsal vertebrae, humerus.

3. **HMN SII (Giraffatitan reference)** — Museum für Naturkunde, Berlin
   While this is *Giraffatitan*, it provides the best complete brachiosaur
   body plan reference available. Use cautiously, noting the anatomical
   differences documented by Taylor 2009.

4. **Paul & Christiansen 2000** (Paleobiology)
   Sauropod forelimb and neck posture. Neck was held at elevated angle
   (approximately 45–70° above horizontal) — not horizontal as in older
   depictions and *Jurassic Park*. Supported by osteological neutral pose.

5. **Taylor, Wedel & Naish 2009** (Acta Palaeontologica Polonica)
   Neck posture analysis across sauropods. Confirms elevated neck posture
   as default. Head was held high — this is the defining visual feature.

6. **Carrano 2005** (Journal of Vertebrate Paleontology)
   Locomotion and body mass estimates for large sauropods. Body mass for
   *B. altithorax* estimated ~40,000 kg (40 tonnes).

7. **Greg Paul skeletal** — *The Princeton Field Guide to Dinosaurs* (2010)
   Best widely-available skeletal reconstruction showing elevated neck and
   correct body proportions.

## What to look for / photograph / scan

- **Neck**: Long, elevated at ~45–70° from horizontal. Head small relative
  to body. Not horizontal as in diplodocids. Cervical vertebrae are long
  and pneumatized (air-sac system).
- **Forelimb/hindlimb ratio**: Forelimbs are longer than hindlimbs —
  defining *Brachiosauridae* feature, unlike most other sauropods.
  Results in a distinctly giraffe-like forward shoulder pitch.
- **Forelimbs**: Columnar, near-vertical. Manus (hand) is narrow and
  horseshoe-shaped in prints — no large claws except on first digit.
- **Tail**: Relatively short for a sauropod; tapers to a thin whip end.
  Horizontal, not raised. Not used as a prop.
- **Nostrils**: Bony nares are on the top of the skull, but soft-tissue
  nostrils were likely positioned lower on the snout (Witmer 2001).
- **Skin**: Fragmentary scale impressions known. No osteoderms confirmed.

## Image format guidance
- Minimum 4K (3840×2160)
- RAW preferred for museum photography
- TIF for skeletal and vertebra diagram scans
- Scale reference shots critical given the enormous body size

## MJ Prompt Notes — Brachiosaurus

### CLIP-Optimized Shorthand
These comma-separated phrases are what the anatomy module injects into prompts:
```
  giraffe-proportioned sauropod forequarters higher than rear
  extremely long steep-angled neck
  arched nasal crest above eyes
  columnar elephant-like legs
  small spatulate-toothed head
  22m long 56-tonne giant
```

### Recommended --stylize Range
| Low | Default | High |
|-----|---------|------|
| 100 | **175** | 400 |

Use `--stylize 175` as a starting point. Lower values (100) preserve more anatomical accuracy. Higher values (400) allow more MJ artistic interpretation.

### Known MJ Failures
Watch for these common misrenders:
- ❌ level back — forequarters must be HIGHER than hindquarters (giraffe proportions)
- ❌ Diplodocus-like neck angle — Brachiosaurus neck was steep/upward, not horizontal
- ❌ forelimbs shorter than hindlimbs — opposite: forelimbs LONGER than hindlimbs

### --sref Test Results
| sref URL | Stylize | Result | Notes |
|----------|---------|--------|-------|
| *(add test results here)* | | | |
