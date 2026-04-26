# Dino Art — Agent Team

Five focused subagents, one per stage of the pipeline. Claude Code auto-routes work to the right agent based on each agent's `description` field, or you can invoke explicitly with `@agent-name`.

| Agent | Stage | Owns |
|---|---|---|
| [ref-curator](ref-curator.md) | Reference layer | `paleoart_refs.json`, `skeletal_refs.json`, `sref_sources.json`, `sref_urls.json`, `reference_images/`, `species_reference/` |
| [prompt-crafter](prompt-crafter.md) | Prompt assembly | `generate_prompt.py`, parameter rules, A/B variants |
| [mj-logger](mj-logger.md) | MJ result tracking | `prompts` / `results` / `prompt_parameters` / `ab_*` tables |
| [printify-publisher](printify-publisher.md) | Product creation | `drops/`, `printify_api.py` (upcoming), sidecar ledgers |
| [site-custodian](site-custodian.md) | Frontend gallery | `site/` Astro project |

## Why this split

Each stage has a different *failure mode* — anatomy errors at the ref layer, weighting bugs at the prompt layer, missing metadata at the logging layer, pricing bugs at the publish layer, layout bugs at the site layer. Keeping them separate means a problem in one stage doesn't pull in context from the other four.

## How they hand off

```
ref-curator → prompt-crafter → (you generate in MJ) → mj-logger → printify-publisher → site-custodian
```

Each handoff is a file or a DB row, not a conversation. If an agent finds work that belongs to a neighbor, it flags and stops rather than reaching across.

## Adding a sixth agent

Only add one when a sustained class of work doesn't fit any of the five. Each new agent dilutes the routing signal, so the bar should be high.
