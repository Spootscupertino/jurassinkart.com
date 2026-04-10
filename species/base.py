"""Base dataclasses and prompt-building helpers for the species anatomy system."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ── Sub-component dataclasses ────────────────────────────────────────

@dataclass
class SkullAnatomy:
    overall_shape: str = ""
    distinctive_features: str = ""
    eye_description: str = ""
    nostril_position: str = ""
    crest_or_horn: str = ""
    beak: str = ""                    # pterosaurs, turtles


@dataclass
class DentitionProfile:
    tooth_shape: str = ""
    tooth_count_note: str = ""
    jaw_mechanics: str = ""
    bite_force_note: str = ""
    visible_teeth: str = ""           # externally-prominent teeth


@dataclass
class LimbStructure:
    forelimb: str = ""
    hindlimb: str = ""
    wing_or_flipper: str = ""         # wings, flippers, fins, paddles, swimming lobes
    stance: str = ""
    digit_count: str = ""
    special_appendage: str = ""       # claws, spines, pincers


@dataclass
class Integument:
    primary_covering: str = ""
    texture_detail: str = ""
    special_structures: str = ""
    membrane: str = ""                # pterosaur wing membrane
    armor: str = ""                   # armored species


@dataclass
class BodyProportions:
    body_length_m: float = 0.0
    body_mass_kg: float = 0.0
    build: str = ""
    neck: str = ""
    tail: str = ""
    silhouette: str = ""
    size_comparison: str = ""


@dataclass
class ColorationEvidence:
    likely_pattern: str = ""
    display_structures: str = ""
    fossil_evidence: str = ""         # confirmed melanosome / iridescence
    additional_notes: str = ""


@dataclass
class LocomotionProfile:
    primary_mode: str = ""
    swimming: str = ""
    flight: str = ""
    gait_detail: str = ""
    speed_note: str = ""
    special: str = ""


@dataclass
class FloraAssociation:
    primary_flora: list[str] = field(default_factory=list)
    ground_cover: str = ""
    canopy: str = ""
    water_plants: str = ""
    banned_flora: list[str] = field(default_factory=list)


# ── Master anatomy dataclass ────────────────────────────────────────

@dataclass
class SpeciesAnatomy:
    species_name: str = ""
    common_name: str = ""
    period: str = ""
    habitat: str = ""                 # terrestrial / marine / aerial / arthropod / plant

    skull: Optional[SkullAnatomy] = None
    dentition: Optional[DentitionProfile] = None
    limbs: Optional[LimbStructure] = None
    integument: Optional[Integument] = None
    body: Optional[BodyProportions] = None
    coloration: Optional[ColorationEvidence] = None
    locomotion: Optional[LocomotionProfile] = None
    flora: Optional[FloraAssociation] = None

    unique_features: list[str] = field(default_factory=list)


# ── Prompt builders ──────────────────────────────────────────────────

def _collect_strings(obj, skip: Optional[set] = None) -> list:
    """Pull all non-empty string fields from a dataclass instance."""
    if obj is None:
        return []
    skip = skip or set()
    parts: list[str] = []
    for f in obj.__dataclass_fields__:
        if f in skip:
            continue
        val = getattr(obj, f)
        if isinstance(val, str) and val:
            parts.append(val)
    return parts


def build_anatomy_prompt(anatomy: SpeciesAnatomy, mode_type: str = "mid") -> str:
    """Build a Midjourney-ready anatomy string.

    mode_type controls detail level:
        "close"  – maximum detail (skull, teeth, integument, limbs, body, coloration)
        "mid"    – moderate detail (integument, body silhouette, key features)
        "wide"   – minimal (2 critical features only, for landscape-dominant shots)
    """
    if mode_type == "wide":
        # Wide shots: just silhouette + 2 most important features
        parts: list[str] = []
        if anatomy.body and anatomy.body.silhouette:
            parts.append(anatomy.body.silhouette)
        for feat in anatomy.unique_features[:2]:
            parts.append(feat)
        return ", ".join(parts)

    # Close / mid share the same pool, close just uses more of it
    sections: list[str] = []

    # Skull
    if anatomy.skull:
        skull_parts = _collect_strings(anatomy.skull)
        if mode_type == "close":
            sections.extend(skull_parts)
        elif skull_parts:
            sections.append(skull_parts[0])  # overall_shape only

    # Dentition
    if anatomy.dentition:
        dent_parts = _collect_strings(anatomy.dentition)
        if mode_type == "close":
            sections.extend(dent_parts)
        elif dent_parts:
            sections.append(dent_parts[0])  # tooth_shape only

    # Integument (always included)
    if anatomy.integument:
        sections.extend(_collect_strings(anatomy.integument))

    # Body proportions
    if anatomy.body:
        skip_body = {"body_length_m", "body_mass_kg"}
        bp = _collect_strings(anatomy.body, skip=skip_body)
        if mode_type == "close":
            sections.extend(bp)
        else:
            # mid: silhouette + build + size_comparison
            for key in ("silhouette", "build", "size_comparison"):
                val = getattr(anatomy.body, key, "")
                if val:
                    sections.append(val)

    # Limbs
    if anatomy.limbs:
        limb_parts = _collect_strings(anatomy.limbs)
        if mode_type == "close":
            sections.extend(limb_parts)
        elif limb_parts:
            sections.append(limb_parts[0])

    # Coloration
    if anatomy.coloration:
        sections.extend(_collect_strings(anatomy.coloration))

    # Locomotion (close only)
    if mode_type == "close" and anatomy.locomotion:
        sections.extend(_collect_strings(anatomy.locomotion))

    # Unique features (always top 3)
    for feat in anatomy.unique_features[:3]:
        sections.append(feat)

    return ", ".join(sections)


def build_anatomy_negative(anatomy: SpeciesAnatomy) -> str:
    """Build negative-prompt additions from banned flora and key inaccuracy notes."""
    negatives: list[str] = []

    if anatomy.flora and anatomy.flora.banned_flora:
        negatives.extend(anatomy.flora.banned_flora)

    return ", ".join(negatives)
