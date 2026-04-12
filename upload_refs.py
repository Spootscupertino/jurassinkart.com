#!/usr/bin/env python3
"""Upload reference images to Discord and store CDN URLs in sref_urls.json.

Usage:
    # Upload a single image with a category tag:
    python3 upload_refs.py --file photo.jpg --category waterhole

    # Upload all new images in reference_images/ subfolders:
    python3 upload_refs.py --all

    # List what's already uploaded:
    python3 upload_refs.py --list

Categories map to output modes and species groups:
    waterhole       → waterhole_gather (armored quadrupeds, herbivores)
    migration       → migration_march (herds in motion, telephoto depth)
    family          → family_group (adult + juveniles, size contrast)
    crocodile       → surface_break, terrestrial carnivores (scaly skin, water edge)
    feathered_biped → feathered theropods (cassowary, emu texture proxy)
    tall_predator   → bipedal theropods (secretary bird, shoebill posture)
    komodo          → scaly terrestrial carnivores (ground-level, pebbly skin)
    arthropod_group → arthropod group_herd (massing behavior, armored bodies)
    tortoise_group  → armored species groups (Ankylosaurus, Archelon)
    raptor_flight   → aerial modes (wing detail, flight posture)
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ENV_PATH = SCRIPT_DIR / ".env"
SREF_PATH = SCRIPT_DIR / "sref_urls.json"
REF_DIR = SCRIPT_DIR / "reference_images"

# Category → which species benefit from this reference
CATEGORY_SPECIES_MAP = {
    "waterhole": [
        "Stegosaurus", "Triceratops", "Ankylosaurus", "Brachiosaurus",
        "Parasaurolophus", "Tyrannosaurus rex",
    ],
    "migration": [
        "Parasaurolophus", "Brachiosaurus", "Triceratops", "Stegosaurus",
        "Ankylosaurus",
    ],
    "family": [
        "Tyrannosaurus rex", "Triceratops", "Stegosaurus", "Brachiosaurus",
        "Parasaurolophus", "Ankylosaurus", "Velociraptor",
    ],
    "crocodile": [
        "Tyrannosaurus rex", "Spinosaurus", "Mosasaurus", "Kronosaurus",
        "Liopleurodon", "Dilophosaurus",
    ],
    "feathered_biped": [
        "Tyrannosaurus rex", "Velociraptor", "Dilophosaurus",
    ],
    "tall_predator": [
        "Velociraptor", "Dilophosaurus", "Tyrannosaurus rex",
    ],
    "komodo": [
        "Tyrannosaurus rex", "Velociraptor", "Dilophosaurus",
        "Spinosaurus",
    ],
    "arthropod_group": [
        "Meganeura", "Arthropleura", "Jaekelopterus", "Pulmonoscorpius",
        "Megarachne", "Anomalocaris", "Eurypterus", "Megalograptus",
    ],
    "tortoise_group": [
        "Ankylosaurus", "Archelon", "Stegosaurus", "Triceratops",
    ],
    "raptor_flight": [
        "Pteranodon", "Quetzalcoatlus", "Rhamphorhynchus", "Dimorphodon",
    ],
}


def load_webhook_url() -> str:
    """Read DISCORD_WEBHOOK_URL from .env file."""
    if not ENV_PATH.exists():
        sys.exit("No .env file found. Add DISCORD_WEBHOOK_URL to .env")
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("DISCORD_WEBHOOK_URL="):
            return line.split("=", 1)[1].strip()
    sys.exit("DISCORD_WEBHOOK_URL not found in .env")


def upload_to_discord(webhook_url: str, filepath: Path, category: str) -> str:
    """Upload an image to Discord via webhook, return the CDN URL."""
    boundary = "----DinoArtRefBoundary"
    filename = filepath.name
    content_type = "image/jpeg" if filepath.suffix.lower() in (".jpg", ".jpeg") else "image/png"

    # Build multipart payload
    payload_json = json.dumps({
        "content": f"[dino_art ref] category: {category} | file: {filename}"
    })

    body = []
    # JSON payload part
    body.append(f"--{boundary}".encode())
    body.append(b'Content-Disposition: form-data; name="payload_json"')
    body.append(b"Content-Type: application/json")
    body.append(b"")
    body.append(payload_json.encode())
    # File part
    body.append(f"--{boundary}".encode())
    body.append(f'Content-Disposition: form-data; name="file"; filename="{filename}"'.encode())
    body.append(f"Content-Type: {content_type}".encode())
    body.append(b"")
    body.append(filepath.read_bytes())
    body.append(f"--{boundary}--".encode())

    body_bytes = b"\r\n".join(body)

    req = urllib.request.Request(
        webhook_url + "?wait=true",  # wait=true returns the message with attachments
        data=body_bytes,
        method="POST",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "DinoArtRefUploader/1.0",
        },
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            if data.get("attachments"):
                return data["attachments"][0]["url"]
            else:
                print(f"  WARNING: No attachment in response for {filename}")
                return ""
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"  ERROR uploading {filename}: {e.code} — {error_body}")
        return ""


def load_sref() -> dict:
    if SREF_PATH.exists():
        return json.loads(SREF_PATH.read_text())
    return {}


def save_sref(data: dict):
    SREF_PATH.write_text(json.dumps(data, indent=4) + "\n")


def add_url_to_sref(sref: dict, category: str, url: str, filename: str):
    """Add a URL to all species that benefit from this category."""
    species_list = CATEGORY_SPECIES_MAP.get(category, [])
    entry = {"label": f"{category}/{filename}", "url": url}

    for sp in species_list:
        if sp not in sref:
            sref[sp] = []
        # Skip duplicates
        existing_urls = {e["url"] if isinstance(e, dict) else e for e in sref[sp]}
        if url not in existing_urls:
            sref[sp].append(entry)
            print(f"    + {sp}")


def get_uploaded_urls(sref: dict) -> set:
    """Get all URLs already in sref_urls.json."""
    urls = set()
    for entries in sref.values():
        if isinstance(entries, list):
            for e in entries:
                if isinstance(e, dict):
                    urls.add(e.get("url", ""))
                elif isinstance(e, str):
                    urls.add(e)
    return urls


def cmd_upload_single(args):
    filepath = Path(args.file).resolve()
    if not filepath.exists():
        sys.exit(f"File not found: {filepath}")

    webhook_url = load_webhook_url()
    sref = load_sref()

    print(f"Uploading {filepath.name} [{args.category}]...")
    url = upload_to_discord(webhook_url, filepath, args.category)
    if url:
        print(f"  CDN URL: {url}")
        add_url_to_sref(sref, args.category, url, filepath.name)
        save_sref(sref)
        print(f"  Saved to sref_urls.json")
    else:
        print("  Upload failed.")


def cmd_upload_all(args):
    if not REF_DIR.exists():
        sys.exit(f"No reference_images/ directory found at {REF_DIR}")

    webhook_url = load_webhook_url()
    sref = load_sref()
    already_uploaded = get_uploaded_urls(sref)

    total = 0
    skipped = 0

    for category_dir in sorted(REF_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        category = category_dir.name
        if category not in CATEGORY_SPECIES_MAP:
            print(f"Skipping unknown category: {category}")
            continue

        images = sorted([
            f for f in category_dir.iterdir()
            if f.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp")
        ])

        if not images:
            continue

        print(f"\n[{category}] — {len(images)} image(s)")
        for img in images:
            # Simple duplicate check by filename in existing labels
            existing_labels = set()
            for sp in CATEGORY_SPECIES_MAP.get(category, []):
                for e in sref.get(sp, []):
                    if isinstance(e, dict):
                        existing_labels.add(e.get("label", ""))

            label = f"{category}/{img.name}"
            if label in existing_labels:
                print(f"  SKIP (already uploaded): {img.name}")
                skipped += 1
                continue

            print(f"  Uploading {img.name}...")
            url = upload_to_discord(webhook_url, img, category)
            if url:
                add_url_to_sref(sref, category, url, img.name)
                total += 1
            else:
                print(f"  FAILED: {img.name}")

    save_sref(sref)
    print(f"\nDone. Uploaded {total} images, skipped {skipped}.")


def cmd_list(args):
    sref = load_sref()
    for sp, entries in sorted(sref.items()):
        if sp.startswith("_"):
            continue
        if not entries:
            continue
        print(f"\n{sp}:")
        for e in entries:
            if isinstance(e, dict):
                print(f"  [{e.get('label', '?')}] {e.get('url', '?')}")
            else:
                print(f"  {e}")


def main():
    parser = argparse.ArgumentParser(description="Upload reference images to Discord for MJ --sref")
    sub = parser.add_subparsers(dest="command")

    p_file = sub.add_parser("upload", help="Upload a single image")
    p_file.add_argument("--file", required=True, help="Path to image file")
    p_file.add_argument("--category", required=True, choices=list(CATEGORY_SPECIES_MAP.keys()),
                        help="Reference category")

    sub.add_parser("all", help="Upload all new images from reference_images/ subfolders")
    sub.add_parser("list", help="List all uploaded reference URLs")

    args = parser.parse_args()

    if args.command == "upload":
        cmd_upload_single(args)
    elif args.command == "all":
        cmd_upload_all(args)
    elif args.command == "list":
        cmd_list(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
