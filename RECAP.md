# RECAP — Dinosaur Art Prompt Generator

## System
- **Machine:** Mac mini, Terminal, Python 3.9.6
- **Main files:** `/Users/ericeldridge/dino_art/`
- **Script:** `generate_prompt.py`
- **Database:** `dino_art.db` (gitignored — regenerate with `python3 setup_db.py`)
- **Run with:** `python3 /Users/ericeldridge/dino_art/generate_prompt.py`
- **With references:** `python3 /Users/ericeldridge/dino_art/generate_prompt.py --sref [URL] --cref [URL]`

## Goal
Generate Midjourney images that look like **real wildlife photography** — benchmark is a Cuban crocodile zoo photo, plus komodo dragon hand, ostrich stride, and flamingo foot close-up reference photos. Natural light, animal just existing in habitat, muted color, telephoto bokeh, imperfect focus, film grain. No painterly/illustrated/CGI quality.

## Database Stats
- **30 species** (all with diet + habitat populated)
- **Parameters:** 31 anatomy, 20 behavior, 14 camera, 24 condition, 10 lighting, 15 mood, 1 style, 10 weather

## Current Architecture

### CLI Arguments
| Flag | Default | Purpose |
|------|---------|---------|
| `--style` | `raw` | MJ style mode |
| `--stylize` | `100` | MJ stylize |
| `--chaos` | `0` | MJ chaos |
| `--quality` | `1.0` | MJ quality |
| `--sref` | None | Style reference URL — appended directly to output prompt |
| `--cref` | None | Character reference URL — appended directly to output prompt |
| `--db` | `dino_art.db` | Database path |

### Prompt Assembly — 5-Section Priority Order
No category bleed between sections. Earlier = richer, later = shorter/supportive.

1. **Subject** — species name + size, anatomy, feathering, tail posture, coloration, required params, skin texture, mouth/teeth, behavior, condition, mood, style anchor
2. **Interaction** — feet/ground contact mechanics only (`GROUND_INTERACTION` constant)
3. **Environment** — period + habitat setting, composition framing
4. **Lighting** — one lighting condition + one weather phrase
5. **Camera** — lens spec only

Deduplication pass strips exact repeated clauses before final join.

### Hardcoded Constants
- **Style:** `"hyperrealistic, anatomically accurate, living animal skin texture, subsurface scattering, 8K texture"`
- **Mouth (carnivore):** `"yellowed uneven teeth, wet interior mouth, heavy saliva stranding between teeth"`
- **Mouth (herbivore):** `"wet lips parted, grinding teeth worn flat, saliva catching light along jaw"`
- **Ground interaction:** `"feet fully weight-bearing, each toe contacting ground at a different angle, visible pressure on toe pads, natural keratin wear on claw tips, packed dirt between digits, knuckle joints slightly bent under load"`
- **Negative prompt:** anatomy errors, studio blockers, fossil/skeleton blockers, indoor blockers

### Modular Vary Region Workflow — 4 Steps

Every run outputs four labeled prompts. MJ flags stripped from Steps 2–4 (paste directly into Vary Region field).

| Step | Target | Stylize | Notes |
|------|--------|---------|-------|
| **STEP 1** | Full image | 100 (default) | Includes all MJ flags. Paste into `/imagine`. |
| **STEP 2** | Feet/claws | 20 | Diet + habitat aware. Carnivore → talons + komodo ref. Herbivore → elephant ref. Marine → flipper. |
| **STEP 3** | Background | 30 | Uses same lighting + weather as main. Specifies no animal in frame. |
| **STEP 4** | Mouth/jaw | 20 | Diet + habitat aware. Carnivore → tooth decay, debris, flies, saliva strand, croc jaw ref. Marine → jaw at waterline, algae, water beading. Herbivore → worn molars, plant fibre. |

### Schema Validator
`validate_prompt(prompt, allow_mj_params, label)`:
- Main prompt: raises if no `--` flags found
- Fix prompts: raises if any `--` flags remain after stripping

### `--sref` Behaviour
When `--sref` is passed, forces `"full body visible head to tail"` into subject block regardless of mode — prevents close-up style reference pulling MJ toward feet/detail crops.

### Output Modes (9 total)
`portrait`, `canvas`, `environmental`, `extreme_closeup`, `action_freeze`, `tracking_side`, `ground_level`, `aerial_overhead`, `dusk_long_exp`

---

## All Changes By Session

### Session 1 — Museum Aesthetic Fix
- Replaced `photogrammetry skin detail` with `living animal skin texture` everywhere
- Rewrote all 10 species `skin_texture_type` DB values from specimen to living-animal language
- Added behavior (15), condition (4), weather (10) parameter categories
- Added fossil/skeleton/indoor blockers to negative prompt
- Removed `cinematic`, `chiaroscuro`, `epic scale` from parameter values
- Fixed `species["diet"]` KeyError (sqlite3.Row has no `.get()`)

### Session 2 — Realism Overhaul
- Deleted non-realism DB options: whimsical/eerie moods, bioluminescent lighting, non-realism styles
- Removed silhouette output mode
- Rewrote all mood values for documentary wildlife tone
- Populated diet field for all 30 species
- Added behavior habitat filtering (marine/aerial column)
- Fixed Python 3.9 compatibility
- Added deduplication engine
- Compressed all 31 anatomy blocks ~60%

### Session 3 — Modular Prompts, Validator, Parameter Expansion

#### Bug Fixes
- **`--sref`/`--cref` were never in the argparser** — flags were documented but silently ignored. Now parsed and appended directly to prompt output.
- **Spinosaurus rendered as crocodile** — `"crocodilian body proportions"` triggered MJ's crocodile recognition. Fixed to `"elongated torso with disproportionately small hindlimbs"`.

#### Prompt Assembly Refactor
- Enforced strict 5-section priority order: Subject → Interaction → Environment → Lighting → Camera
- `FEET_CLAWS` renamed `GROUND_INTERACTION`, moved to dedicated section 2, text expanded
- Mood, condition, behavior pulled up into subject (were after camera)
- `"tail posture: ..."` label removed from prompt output

#### Modular Fix Prompts
- `make_feet_fix_prompt()` — diet/habitat aware, `--stylize 20`
- `make_environment_fix_prompt()` — matches main lighting + weather, `--stylize 30`
- `make_mouth_fix_prompt()` — diet/habitat aware, `--stylize 20`, saltwater crocodile jaw reference anchor
- `strip_mj_params()` — truncates at first ` --`
- `validate_prompt()` — schema enforcement on all four outputs

#### Parameter Expansion
- **Lighting** (4 → 10): `blue_hour`, `harsh_midday`, `broken_cloud`, `backlit_haze`, `pre_storm`, `dappled_canopy`
- **Mood** (4 → 15): full documentary wildlife set — `quiet_power`, `alert_scan`, `heat_rest`, `feeding_focus`, `territorial_hold`, `post_kill_pause`, `scent_check`, `wading_slow`, `dust_bath`, `eye_contact` + originals
- **Behavior** (15 → 20): `freeze_detect`, `jaw_clean`, `mud_wallow`, `body_press_thermoreg`, `carcass_pause`
- **Condition** (4 → 24): 10 realism conditions (`mud_caked`, `wet_from_water`, `parasite_load`, `missing_toe`, `moulting_skin`, `blood_on_muzzle`, `algae_on_hide`, `fly_attention`, `lean_season`, `dominant_prime`) + 10 injury conditions (`eye_wound`, `torn_sail`, `jaw_asymmetry`, `hide_bite_flank`, `broken_horn_tip`, `missing_claw_digit`, `patchy_hide`, `embedded_tooth`, `split_claw`, `neck_scar_collar`)

---

## Current Status
- **Anatomy, feathering, body, color palette, bokeh:** Solved.
- **Modular 4-step workflow:** Fully implemented and committed.
- **Results:** Allosaurus images reading as near-wildlife-photography. Lighting and background still the main remaining CGI tell.
- **Remaining CGI tells:** Forest backgrounds too lush/rendered. God-ray lighting reads as game engine. Feet still floating slightly — Vary Region Step 2 not yet tested in practice.

## Next Priorities
1. **Kill the CGI background** — switch to `environmental` mode, Cretaceous riverbank, `overcast` or `broken_cloud` lighting. Open flat habitat with flat light is where these tip into real photography.
2. **Test Step 2 feet-fix in Vary Region** — upscale best image → paint feet → paste Step 2 prompt
3. **Test Step 4 mouth-fix in Vary Region** — reference: saltwater crocodile jaw photo (tooth decay, debris, flies, water glistening)
4. **Try beat-up condition stacks** — `split_claw` + `lean_season` + `freeze_detect` is the target combination
5. **Build `species_reference/` folder** — real animal analogue photos per species (croc skin for theropods, elephant feet for sauropods)
6. **Test `--sref` with komodo/flamingo foot URLs** — confirm full-body framing override works correctly

## Reference Photos to Use as `--sref`
- Komodo dragon foot (digits separated, claws at different angles, leathery pads)
- Ostrich mid-stride (muted color, overcast, telephoto bokeh, messy feathers)
- Flamingo foot close-up (scale transition shin→toe, worn keratin)
- Monitor lizard yawning (wet pink mouth, individual claws, bokeh background)
- **Saltwater crocodile jaw** (tooth decay/staining, twig between teeth, algae on jaw, flies, water glistening) ← new this session
