# Tech Digest 📰🐉

Automated daily & weekly tech news digest system, built as an [OpenClaw](https://github.com/openclaw/openclaw) Agent Skill.

Three-layer data collection covering AI/LLM, cryptocurrency, and frontier tech.

## Features

- **RSS Primary Sources** — 30+ curated tech blogs and news feeds (inspired by [Karpathy's top HN blogs](https://github.com/vigorX777/ai-daily-digest))
- **Web Search** — Real-time hot topic discovery with freshness filters
- **Twitter/X KOL Monitoring** — 30+ KOLs across AI, crypto, and tech (including Chinese crypto KOLs)
- **Multi-channel Delivery** — Discord, Telegram, and Email
- **Report Archiving** — Auto-saved to workspace for future reference
- **Fully Customizable** — RSS feeds, KOL list, topics, language, and delivery channels are all configurable with sensible defaults

## Default Topics

Out of the box, reports cover these topics (customizable via `config/tech-digest-topics.json`):

- 🧠 **LLM / Large Models** — GPT, Claude, Gemini, open-source models, benchmarks
- 🤖 **AI Agent** — autonomous agents, frameworks, tool use
- 💰 **Cryptocurrency** — Bitcoin, Ethereum, DeFi, regulation
- 🔬 **Frontier Tech** — breakthroughs, robotics, quantum, biotech

Plus these fixed sections:

- 📢 **KOL Updates** — Twitter KOLs + notable blog posts
- 🔥 **Twitter/X Trending** — viral discussions
- 📝 **Blog Picks** — deep articles from RSS sources
- 📊 **Weekly Trend Summary** (weekly only)

## Quick Start

### Install via OpenClaw

The easiest way — just tell your OpenClaw bot:

> Install the tech-digest skill from ClawHub and set it up. Send daily and weekly reports at 7:00 AM to Discord channel #news.

Your bot will handle installation, config, and cron job creation automatically.

### Install Manually

**Step 1: Install the skill**

```bash
# Via ClawHub
clawhub install tech-digest

# Or via Git
git clone https://github.com/dracohoard/tech-digest.git ~/.openclaw/workspace/skills/tech-digest
```

**Step 2: Copy config to workspace**

```bash
mkdir -p ~/.openclaw/workspace/config ~/.openclaw/workspace/archive/tech-digest
cp ~/.openclaw/workspace/skills/tech-digest/config/tech-digest-*.json ~/.openclaw/workspace/config/
```

**Step 3: Set up cron jobs**

Open `references/digest-prompt.md` — it's a unified template for both daily and weekly digests. Replace the `<...>` placeholders (see the table in the file), then create cron jobs with the filled-in prompt.

Default schedule: daily & weekly both at 7:00 AM.

**Step 4: (Optional) Twitter/X API**

```bash
echo 'export X_BEARER_TOKEN="your-token"' >> ~/.zshenv
```

**This is optional** — without it, the skill still discovers Twitter trends via web search.

**Step 5: (Optional) Email delivery**

Requires [gog CLI](https://github.com/panyq357/gog) configured with Gmail. Remove the email line from the prompt if not needed.

**Step 6: Verify**

Tell your bot "Run the daily tech digest now", or:

```bash
openclaw cron list        # find job ID
openclaw cron run <id>    # trigger it
```

## Customization

All configs ship with sensible defaults. Edit as needed:

| What | File | Description |
|------|------|-------------|
| **RSS Feeds** | `config/tech-digest-rss-feeds.json` | Add/remove feeds by domain. Set `"priority": true` for must-fetch sources. 30+ defaults. |
| **Twitter KOLs** | `config/tech-digest-kol-list.json` | Add/remove Twitter accounts by category. 30+ defaults across AI, crypto (global + CN), and tech. |
| **Topics & Sections** | `config/tech-digest-topics.json` | Add/remove/reorder topics. Each topic defines emoji, label, and search keywords. |
| **Delivery** | `references/digest-prompt.md` | Discord + Telegram + Email. Add/remove delivery lines as needed. |
| **Schedule** | Cron job config | Default: daily & weekly at 7:00 AM |

## Directory Structure

```
tech-digest/
├── SKILL.md                          # Skill entry point (for agents)
├── README.md                         # This file
├── README_CN.md                      # 中文文档
├── LICENSE                           # MIT License
├── config/
│   ├── tech-digest-rss-feeds.json    # RSS feed config (copy to workspace)
│   ├── tech-digest-kol-list.json     # Twitter KOL config (copy to workspace)
│   └── tech-digest-topics.json       # Topic definitions (copy to workspace)
├── references/
│   ├── digest-prompt.md              # Unified prompt template (daily & weekly)
│   └── config-schema.md             # Config file field definitions
└── scripts/
    └── fetch-rss.py                  # Parallel RSS fetcher + archive cleanup
```

## Credits

- [vigorX777/ai-daily-digest](https://github.com/vigorX777/ai-daily-digest) — RSS feed inspiration
- [Andrej Karpathy](https://x.com/karpathy) — Top HN blog recommendations
- [OpenClaw](https://github.com/openclaw/openclaw) — Agent runtime framework

## License

MIT
