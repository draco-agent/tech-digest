---
name: tech-digest
description: Generate daily and weekly tech news digests covering AI/LLM, crypto, and frontier tech. Three-layer data collection from RSS feeds, web search, and Twitter/X KOLs. Outputs to Discord, Telegram, email, or other channels. Use when setting up automated tech news reports, configuring RSS-based monitoring, or generating on-demand tech summaries.
---

# Tech Digest

Automated tech news digest with three-layer data collection: RSS primary sources, web search, and Twitter/X KOL monitoring.

## Setup

1. Copy config files to workspace:
   ```
   config/tech-digest-rss-feeds.json  → <WORKSPACE>/config/
   config/tech-digest-kol-list.json   → <WORKSPACE>/config/
   config/tech-digest-topics.json     → <WORKSPACE>/config/
   ```

2. Read `references/digest-prompt.md` for the unified prompt template. Ask the user for their preferred report language (default: Chinese). Fill in placeholders for daily or weekly mode, then create cron jobs:
   - Daily: `schedule: "0 7 * * *"` (7:00 AM daily)
   - Weekly: `schedule: "0 7 * * 1"` (7:00 AM Monday)

3. (Optional) Set `X_BEARER_TOKEN` env var for Twitter API. Works without it via web search fallback.

4. (Optional) Configure `gog` CLI for email delivery. Remove email line from prompt if not needed.

## Config Files

Both live in `<WORKSPACE>/config/` for easy editing without modifying prompts:

- **`tech-digest-rss-feeds.json`** — RSS feeds by domain. Feeds with `"priority": true` are fetched first. 30+ defaults.
- **`tech-digest-kol-list.json`** — Twitter KOL accounts by domain. 30+ defaults including AI labs, builders, crypto (global + CN), tech leaders.
- **`tech-digest-topics.json`** — Topic definitions: report sections, search keywords, emojis. Drives both data collection and report structure.

See `references/config-schema.md` for field definitions and validation rules.

## Scripts

- **`scripts/fetch-rss.py`** — Parallel RSS fetcher. Pre-fetches all feeds and outputs structured JSON. Used by the digest prompt to avoid slow sequential web_fetch calls.
  ```bash
  python3 scripts/fetch-rss.py config.json --hours 48 --clean-archive ./archive/tech-digest
  ```

## Minimal Setup

Only 3 placeholders are required. Everything else has sensible defaults:

| Required | Example |
|----------|---------|
| `<WORKSPACE>` | `/Users/bot/.openclaw/workspace` |
| `<SKILL_DIR>` | `/Users/bot/.openclaw/workspace/skills/tech-digest` |
| `<DISCORD_CHANNEL_ID>` | `1470806864412414071` |

Optional: `<EMAIL>`, `<TELEGRAM_CHAT_ID>`, `<LANGUAGE>` (default: Chinese).

All other placeholders (`<MODE>`, `<FRESHNESS>`, etc.) have fixed daily/weekly values — see the placeholder table in `references/digest-prompt.md`.

## On-Demand Usage

Tell the agent: "Generate today's tech digest now" or trigger via `cron run <jobId>`.

## Customization

- **Topics/sections**: Edit `tech-digest-topics.json` to add/remove/reorder topics and search keywords
- **RSS feeds**: Edit `tech-digest-rss-feeds.json` (add/remove, toggle priority)
- **KOLs**: Edit `tech-digest-kol-list.json` (add/remove by category)
- **Language**: Change `<LANGUAGE>` placeholder (default: Chinese)
- **Delivery**: Discord, Telegram, email — add/remove delivery lines in prompt
- **Archive**: Reports saved to `<WORKSPACE>/archive/tech-digest/`
