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
- **18 species** — 8 terrestrial, 6 marine, 4 aerial (all with diet + habitat populated)
- **308 parameters** — exactly 20 per habitat per category (behavior, camera, condition, lighting, mood, weather) + anatomy + style

## Current Architecture

### Interactive Flow
1. **Habitat** — Terrestrial / Marine / Aerial (first choice, gates everything below)
2. **Output mode** — habitat-filtered (e.g. `surface_break` marine-only, `soaring_thermal` aerial-only)
3. **Species** — filtered to selected habitat
4. **Lighting** → **Camera** → **Mood** → **Condition** → **Behavior** → **Weather**
   - All menus show **name only** (no descriptions), **20 options** each, **custom ordered** (ORDER BY id)
   - Weather is filtered by lighting compatibility (sky state grouping)

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
2. **Interaction** — habitat-specific (`HABITAT_INTERACTION` dict):
   - Terrestrial: feet weight-bearing, toe contact, claw wear
   - Marine: body submerged, waterline crossing torso, water tension against skin
   - Aerial: wing membrane taut, finger bones as structural ridges, translucent membrane
3. **Environment** — period + habitat setting, composition framing
4. **Lighting** — one lighting condition + one weather phrase
5. **Camera** — lens spec only

Deduplication pass strips exact repeated clauses before final join.

### Habitat-Specific Realism (`HABITAT_REALISM`)
- **Terrestrial:** National Geographic wildlife photography, telephoto bokeh
- **Marine:** National Geographic ocean wildlife photography, underwater caustics, water surface refraction
- **Aerial:** National Geographic bird-in-flight photography, atmospheric haze

### Habitat-Specific Negative Prompts (`HABITAT_NEGATIVE`)
- **Terrestrial:** (base negative only)
- **Marine:** dry land, standing on ground, desert, forest floor, no water, dry skin, dusty
- **Aerial:** standing on ground, walking, sitting, grounded, feet on dirt, terrestrial pose, folded wings

### Lighting → Weather Compatibility
- Each lighting has a sky state: `clear`, `overcast`, `mixed`, `storm`
- Each weather has compatible sky states (e.g. `monsoon_heavy` → `storm`/`overcast`)
- `pick_weather()` filters weather options to only show compatible choices
- `volcanic_ash_fall` is compatible with any sky state

### Hardcoded Constants
- **Style:** `"hyperrealistic, anatomically accurate, living animal skin texture, subsurface scattering, 8K texture"`
- **Mouth (carnivore):** `"yellowed uneven teeth, wet interior mouth, heavy saliva stranding between teeth"`
- **Mouth (herbivore):** `"wet lips parted, grinding teeth worn flat, saliva catching light along jaw"`
- **Negative prompt:** anatomy errors, studio blockers, fossil/skeleton blockers, indoor blockers + habitat-specific

### Modular Vary Region Workflow — 4 Steps

Every run outputs four labeled prompts. MJ flags stripped from Steps 2–4 (paste directly into Vary Region field).

| Step | Target | Stylize | Notes |
|------|--------|---------|-------|
| **STEP 1** | Full image | 100 (default) | Includes all MJ flags. Paste into `/imagine`. |
| **STEP 2** | Feet/flippers/wings | 20 | Habitat + diet aware. Terrestrial → talons/elephant feet. Marine → flipper. Aerial → wing membrane. |
| **STEP 3** | Background | 30 | Uses same lighting + weather as main. Specifies no animal in frame. |
| **STEP 4** | Mouth/jaw | 20 | Diet + habitat aware. Carnivore → tooth decay, debris, flies, saliva strand, croc jaw ref. Marine → jaw at waterline, algae, water beading. Herbivore → worn molars, plant fibre. |

### Schema Validator
`validate_prompt(prompt, allow_mj_params, label)`:
- Main prompt: raises if no `--` flags found
- Fix prompts: raises if any `--` flags remain after stripping

### `--sref` Behaviour
When `--sref` is passed, forces `"full body visible head to tail"` into subject block regardless of mode — prevents close-up style reference pulling MJ toward feet/detail crops.

### Output Modes (13 total, habitat-filtered)
- **All habitats:** `portrait`, `canvas`, `environmental`, `extreme_closeup`, `action_freeze`, `tracking_side`, `ground_level`, `aerial_overhead`, `dusk_long_exp`
- **Marine only:** `surface_break`, `underwater`
- **Aerial only:** `soaring_thermal`, `dive_strike`

### Species Roster

| Habitat | Species |
|---------|---------|
| Terrestrial | T. rex, Velociraptor, Triceratops, Stegosaurus, Ankylosaurus, Brachiosaurus, Parasaurolophus, Dilophosaurus |
| Marine | Mosasaurus, Elasmosaurus, Ichthyosaurus, Liopleurodon, Kronosaurus, Spinosaurus |
| Aerial | Pteranodon, Quetzalcoatlus, Rhamphorhynchus, Dimorphodon |

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

### Session 4 — Habitat-First Architecture

#### Core Change
- **Habitat is now the first interactive choice** — Terrestrial / Marine / Aerial gates every subsequent menu (species, modes, lighting, camera, mood, condition, behavior, weather)

#### Schema
- Added `habitat` column to `species` table (`terrestrial` / `marine` / `aerial`)
- Added `habitats` column to `parameters` table (comma-separated, filtered with `LIKE`)

#### Species Expansion
- Added 5 marine species: Mosasaurus, Elasmosaurus, Ichthyosaurus, Liopleurodon, Kronosaurus
- Added 3 aerial species: Quetzalcoatlus, Rhamphorhynchus, Dimorphodon
- Reclassified Spinosaurus → marine, Pteranodon → aerial

#### Parameter Overhaul
- Every category (behavior, camera, condition, lighting, mood, weather) now has exactly **20 options per habitat**
- All menus display **name only** (no descriptions)
- Custom logical ordering per category (ORDER BY id, insertion order = display order)
- Habitat-specific parameters: e.g. marine behavior includes `breaching_surface`, `deep_dive_descent`; aerial condition includes `torn_membrane`, `wind_worn_crest`

#### Lighting → Weather Filtering
- `LIGHTING_SKY` dict maps each lighting option to a sky state (`clear`/`overcast`/`mixed`/`storm`)
- `WEATHER_SKY_COMPAT` dict defines compatible sky states per weather option
- `pick_weather()` filters weather menu to only show options compatible with chosen lighting
- Example: choosing "harsh midday" hides monsoon/storm weather; choosing "stormy" hides clear/pristine

#### Habitat-Specific Realism
- `HABITAT_INTERACTION` — replaces old single `GROUND_INTERACTION` with per-habitat physics (ground contact / water physics / wing flight)
- `HABITAT_REALISM` — per-habitat National Geographic photography style anchors
- `HABITAT_NEGATIVE` — per-habitat negative prompt additions (marine blocks land, aerial blocks grounded poses)

#### New Output Modes
- `surface_break` and `underwater` (marine only)
- `soaring_thermal` and `dive_strike` (aerial only)

#### Step 2 Labels
- Terrestrial → FEET FIX, Marine → FLIPPER FIX, Aerial → WING FIX

#### Migration
- `migrate_scientific.py` updated with `habitat` column for species and `habitats` column for parameters
- Habitat overrides for Pteranodon (→ aerial) and Spinosaurus (→ marine)

---

## Current Status
- **Habitat-first architecture:** Fully implemented — Terrestrial / Marine / Aerial gates all menus.
- **20 options per category per habitat:** Verified across all 6 parameter categories.
- **Lighting → weather filtering:** Working — incompatible weather hidden based on sky state.
- **All 3 habitat flows tested end-to-end** — terrestrial, marine, aerial all produce 4-step output.
- **Anatomy, feathering, body, color palette, bokeh:** Solved.
- **Modular 4-step workflow:** Fully working with habitat-aware step labels.

## Next Priorities
1. **Test marine species in Midjourney** — run Mosasaurus/Elasmosaurus prompts, verify underwater realism
2. **Test aerial species in Midjourney** — run Pteranodon/Quetzalcoatlus prompts, verify flight realism
3. **Test Vary Region steps** — feet fix (terrestrial), flipper fix (marine), wing fix (aerial)
4. **Kill the CGI background** — `environmental` mode + `overcast`/`broken_cloud` lighting for flat light
5. **Try beat-up condition stacks** — `split_claw` + `lean_season` + `freeze_detect`
6. **Build `species_reference/` folder** — real animal analogue photos per species
7. **Test `--sref` with komodo/flamingo foot URLs** — confirm full-body framing override works

## Reference Photos to Use as `--sref`
- Komodo dragon foot (digits separated, claws at different angles, leathery pads)
- Ostrich mid-stride (muted color, overcast, telephoto bokeh, messy feathers)
- Flamingo foot close-up (scale transition shin→toe, worn keratin)
- Monitor lizard yawning (wet pink mouth, individual claws, bokeh background)
- **Saltwater crocodile jaw** (tooth decay/staining, twig between teeth, algae on jaw, flies, water glistening) ← new this session
