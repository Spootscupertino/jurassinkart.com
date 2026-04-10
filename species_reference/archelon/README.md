# Archelon — Reference Materials

## How to Use
1. Find high-quality photographs matching this species
2. Upload to Midjourney Discord
3. Copy the Discord CDN URL
4. Add to `sref_urls.json` under `"Archelon"`

## MJ Prompt Notes — Archelon

### CLIP-Optimized Shorthand
These comma-separated phrases are what the anatomy module injects into prompts:
```
  leathery ridged shell not hard scutes
  massive front flippers 5m span
  hooked keratinous beak no teeth
  barnacles and algae on shell biofouled
  oversized leatherback turtle body plan
  4.6m largest sea turtle ever
```

### Recommended --stylize Range
| Low | Default | High |
|-----|---------|------|
| 125 | **200** | 350 |

Use `--stylize 200` as a starting point. Lower values (125) preserve more anatomical accuracy. Higher values (350) allow more MJ artistic interpretation.

### Known MJ Failures
Watch for these common misrenders:
- ❌ hard turtle shell — shell is LEATHERY like a leatherback, not hard scutes
- ❌ teeth — Archelon has a beak, NO teeth
- ❌ clean shell — shell should be biofouled with barnacles and algae

### --sref Test Results
| sref URL | Stylize | Result | Notes |
|----------|---------|--------|-------|
| *(add test results here)* | | | |
