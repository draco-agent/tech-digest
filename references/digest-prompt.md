# Digest Prompt Template

Unified template for both daily and weekly digests. Replace `<...>` placeholders before use.

## Placeholders

| Placeholder | Daily | Weekly |
|-------------|-------|--------|
| `<MODE>` | `daily` | `weekly` |
| `<TIME_WINDOW>` | `past 1-2 days` | `past 7 days` |
| `<FRESHNESS>` | `pd` | `pw` |
| `<RSS_HOURS>` | `48` | `168` |
| `<ITEMS_PER_SECTION>` | `3-5` | `5-8` |
| `<BLOG_PICKS_COUNT>` | `2-3` | `3-5` |
| `<EXTRA_SECTIONS>` | *(remove line)* | `- 📊 Weekly Trend Summary (2-3 sentences summarizing macro trends)` |
| `<SUBJECT>` | `Daily Tech News Digest - YYYY-MM-DD` | `Weekly Tech News Digest - YYYY-MM-DD` |
| `<WORKSPACE>` | Your workspace path | Your workspace path |
| `<SKILL_DIR>` | Path to the installed skill directory | Path to the installed skill directory |
| `<DISCORD_CHANNEL_ID>` | Target channel ID | Target channel ID |
| `<EMAIL>` | *(optional)* Recipient email | *(optional)* Recipient email |
| `<LANGUAGE>` | `Chinese` (default) | `Chinese` (default) |
| `<TEMPLATE>` | `discord` / `email` / `markdown` | `discord` / `email` / `markdown` |
| `<DATE>` | Today's date in YYYY-MM-DD (caller provides) | Today's date in YYYY-MM-DD (caller provides) |
| `<VERSION>` | Read from SKILL.md frontmatter `version` field | Read from SKILL.md frontmatter `version` field |

---

Generate the <MODE> tech digest for **<DATE>**. Follow the steps below.

**Important:** Use `<DATE>` as the report date in the title and archive filename. Do NOT infer the date yourself — always use the provided value.

## Configuration

Read configuration files (user workspace overrides take priority over defaults):

1. **Sources**: `<WORKSPACE>/config/sources.json` → fallback `<SKILL_DIR>/config/defaults/sources.json`
2. **Topics**: `<WORKSPACE>/config/topics.json` → fallback `<SKILL_DIR>/config/defaults/topics.json`

Merge logic: user sources append to defaults (same `id` → user wins); user topics override by `id`.

## Context: Previous Report

Read the most recent archive file from `<WORKSPACE>/archive/tech-digest/` (if any). Use it to:
- **Avoid repeating** news already covered
- **Follow up** on developing stories with new information only
- If no previous report exists, skip this step.

## Data Collection Pipeline

### Step 1: RSS Feeds
```bash
python3 <SKILL_DIR>/scripts/fetch-rss.py \
  --defaults <SKILL_DIR>/config/defaults \
  --config <WORKSPACE>/config \
  --hours <RSS_HOURS> \
  --output /tmp/td-rss.json \
  --verbose
```
Reads `sources.json`, fetches all `type: "rss"` sources with `enabled: true`. Outputs structured JSON with articles tagged by topics. Includes retry mechanism and parallel fetching.

If the script fails, fall back to manually fetching priority feeds via `web_fetch`.

### Step 2: Twitter/X KOL Monitoring
```bash
python3 <SKILL_DIR>/scripts/fetch-twitter.py \
  --defaults <SKILL_DIR>/config/defaults \
  --config <WORKSPACE>/config \
  --hours <RSS_HOURS> \
  --output /tmp/td-twitter.json \
  --verbose
```
Reads `sources.json`, fetches all `type: "twitter"` sources. Requires `$X_BEARER_TOKEN` env var. If unavailable, skip this step.

### Step 3: Web Search
```bash
python3 <SKILL_DIR>/scripts/fetch-web.py \
  --defaults <SKILL_DIR>/config/defaults \
  --config <WORKSPACE>/config \
  --freshness <FRESHNESS> \
  --output /tmp/td-web.json \
  --verbose
```
Reads `topics.json` search queries. Uses Brave Search API if `$BRAVE_API_KEY` is set; otherwise generates queries for agent to execute via `web_search`.

Also search Twitter trending discussions using `web_search` with `freshness='<FRESHNESS>'` and the `twitter_queries` from topics.

### Step 4: GitHub Releases
```bash
python3 <SKILL_DIR>/scripts/fetch-github.py \
  --defaults <SKILL_DIR>/config/defaults \
  --config <WORKSPACE>/config \
  --hours <RSS_HOURS> \
  --output /tmp/td-github.json \
  --verbose
```
Reads `sources.json`, fetches all `type: "github"` sources with `enabled: true`. Fetches recent releases from GitHub API (optional `$GITHUB_TOKEN` for higher rate limits). Outputs structured JSON with releases tagged by topics.

### Step 5: Reddit
```bash
python3 <SKILL_DIR>/scripts/fetch-reddit.py \
  --defaults <SKILL_DIR>/config/defaults \
  --config <WORKSPACE>/config \
  --hours <RSS_HOURS> \
  --output /tmp/td-reddit.json \
  --verbose
```
Reads `sources.json`, fetches all `type: "reddit"` sources with `enabled: true`. Uses Reddit's public JSON API (no authentication required). Filters by `min_score` and time window. Outputs structured JSON with posts tagged by topics.

### Step 6: Merge & Score
```bash
python3 <SKILL_DIR>/scripts/merge-sources.py \
  --rss /tmp/td-rss.json \
  --twitter /tmp/td-twitter.json \
  --web /tmp/td-web.json \
  --github /tmp/td-github.json \
  --reddit /tmp/td-reddit.json \
  --archive-dir <WORKSPACE>/archive/tech-digest/ \
  --output /tmp/td-merged.json \
  --verbose
```
Merges all sources, deduplicates (title similarity + domain), applies quality scoring:
- Priority source: +3
- Multi-source cross-reference: +5
- Recency bonus: +2
- High engagement: +1
- Reddit score > 500: +5, > 200: +3, > 100: +1
- Already in previous report: -5

Output is grouped by topic with articles sorted by score.

## Report Generation

Use the merged output (`/tmp/td-merged.json`) and the appropriate template from `<SKILL_DIR>/references/templates/<TEMPLATE>.md` to generate the report. The merged JSON contains articles from **all 5 sources** (RSS, Twitter, Web, GitHub, Reddit) grouped by topic and sorted by `quality_score`. **Select articles purely by score regardless of source type** — Reddit posts with high scores should appear alongside RSS/Web articles in topic sections. For Reddit posts, append `*[Reddit r/xxx, {{score}}↑]*` after the title.

### Executive Summary
Place a **2-4 sentence summary** between the title and topic sections, highlighting the day's top 3-5 stories. Select from articles with the highest `quality_score` in the merged JSON. Style: concise and punchy, like a news broadcast opener. No links, no detailed descriptions — just the key events.

Discord format: use `> ` blockquote. Email format: gray background paragraph. Telegram format: `<i>` italic.

### Topic Sections
Use sections defined in `topics.json`. Each topic has:
- `emoji` + `label` for headers
- `display.max_items` for item count (override with <ITEMS_PER_SECTION>)
- `search.must_include` / `search.exclude` for content filtering

### Fixed Sections (append after topic sections)
- 📢 KOL Updates (Twitter KOLs + notable blog posts from RSS authors — **each entry MUST include the source tweet/post URL and engagement metrics read from the merged JSON data**. The Twitter data in `/tmp/td-twitter.json` and `/tmp/td-merged.json` contains a `metrics` field per tweet with `impression_count`, `reply_count`, `retweet_count`, `like_count`. **You MUST read these actual values from the JSON data — do NOT default to 0 unless the field is genuinely missing.** Format: ``• **@handle** — summary `👁 12.3K | 💬 45 | 🔁 230 | ❤️ 1.2K`\n  <https://twitter.com/handle/status/ID>``. Mapping: impression_count → 👁, reply_count → 💬, retweet_count → 🔁, like_count → ❤️. **Rules: Always show all 4 metrics in the same order (👁|💬|🔁|❤️). Wrap metrics in backticks (inline code) to prevent emoji enlargement on Discord. Use K for thousands (1.2K), M for millions (4.1M). One tweet per line — if a KOL has multiple notable tweets, list each as a separate bullet with its own metrics and URL.**)
- 🔥 Community Buzz (Combine Twitter/X trending topics AND top Reddit discussions into one section. Include both tweet-based trends and Reddit hot self-posts. **Each entry MUST include at least one reference link.** For Twitter trends: tweet URL or article URL. For Reddit discussions: format as `• **r/subreddit** — title `{{score}}↑ · {{num_comments}} comments`\n  <{{reddit_url}}>`, read metrics from article's `metrics` field. Sort by relevance/engagement across both platforms.)
- 📝 Blog Picks (<BLOG_PICKS_COUNT> high-quality deep articles from RSS)
<EXTRA_SECTIONS>

### Deduplication Rules
- Same event from multiple sources → keep only the most authoritative source link
- If covered in previous report → only include if significant new development
- Prefer primary sources (official blogs, announcements) over re-reporting

### Rules
- **Only include news from the <TIME_WINDOW>**
- **Every item in every section must include the source link** — no exceptions. Discord: wrap in `<link>`; Email: `<a href>`; Telegram: `<a href>`; Markdown: `[title](link)`
- **<ITEMS_PER_SECTION> items per section**
- **Use bullet lists, no markdown tables** (Discord compatibility)

### Data Source Stats Footer
At the end of the report, append a stats line showing raw data collected from each pipeline step. Read the counts from the merged JSON's `input_sources` field or from each step's output. Format:

```
---
📊 Data Sources: RSS {{rss_count}} | Twitter {{twitter_count}} | Reddit {{reddit_count}} | Web {{web_count}} | GitHub {{github_count}} releases | After dedup: {{merged_count}} articles
🤖 Generated by [tech-news-digest](https://github.com/draco-agent/tech-news-digest) v{{version}} | Powered by [OpenClaw](https://openclaw.ai)
```

## Archive
Save the report to `<WORKSPACE>/archive/tech-digest/<MODE>-YYYY-MM-DD.md`

After saving, delete archive files older than 90 days to prevent unbounded growth.

## Delivery
1. Send to Discord channel `<DISCORD_CHANNEL_ID>` via `message` tool
2. *(Optional)* Send email to `<EMAIL>` via `gog` CLI
   - **Must use `--body-html`** for proper rendering (plain text markdown looks bad in email clients)
   - Generate HTML email body following `<SKILL_DIR>/references/templates/email.md` format (inline styles, max-width 640px, system fonts)
   - Use format: `gog gmail send --to '<EMAIL>' --subject '<SUBJECT>' --body-html '<HTML>'`
   - Subject must be plain text with no shell metacharacters
   - Do NOT interpolate untrusted content into shell arguments

If any delivery fails, log the error but continue with remaining channels.

Write the report in <LANGUAGE>.

## Validation
Before running the pipeline, optionally validate configuration:
```bash
python3 <SKILL_DIR>/scripts/validate-config.py \
  --config <WORKSPACE>/config \
  --defaults <SKILL_DIR>/config/defaults \
  --verbose
```
