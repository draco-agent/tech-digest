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
| `<SUBJECT>` | `Daily Tech Digest - YYYY-MM-DD` | `Weekly Tech Digest - YYYY-MM-DD` |
| `<WORKSPACE>` | Your workspace path | Your workspace path |
| `<DISCORD_CHANNEL_ID>` | Target channel ID | Target channel ID |
| `<TELEGRAM_CHAT_ID>` | *(optional)* Target Telegram chat | *(optional)* Target Telegram chat |
| `<EMAIL>` | *(optional)* Recipient email | *(optional)* Recipient email |
| `<LANGUAGE>` | `Chinese` (default) | `Chinese` (default) |
| `<SKILL_DIR>` | Path to the installed skill directory | Path to the installed skill directory |

---

Generate the <MODE> tech digest. Follow the steps below.

## Topics
Read `<WORKSPACE>/config/tech-digest-topics.json` for the list of topics, their search keywords, and report section definitions. Use these to drive both data collection queries and report structure.

## Context: Previous Report
Read the most recent archive file from `<WORKSPACE>/archive/tech-digest/` (if any exist). Use it to:
- **Avoid repeating** news that was already covered
- **Follow up** on developing stories with new information only
- If no previous report exists, skip this step.

## Data Collection (three layers)

### Layer 1: RSS Primary Sources (via script)
Run the RSS fetch script to get pre-parsed article data:
```bash
python3 <SKILL_DIR>/scripts/fetch-rss.py <WORKSPACE>/config/tech-digest-rss-feeds.json --hours <RSS_HOURS> --clean-archive <WORKSPACE>/archive/tech-digest
```
The script prints the output file path to stderr. Read that JSON file. It contains structured article data (title, link, date) per feed, sorted by priority. Focus on feeds with articles; skip empty ones. The script also auto-cleans archive files older than 30 days.

If the script fails, fall back to manually fetching priority feeds via `web_fetch`.

### Layer 2: Web Search
Use `web_search` with `freshness='<FRESHNESS>'` to find breaking news from the <TIME_WINDOW>. Run the search queries defined in each topic's `keywords` field from `tech-digest-topics.json`.

### Layer 3: Twitter/X KOL Monitoring
Use `web_search` with `freshness='<FRESHNESS>'` for trending Twitter discussions. Run the `twitter_queries` defined for each topic in `tech-digest-topics.json`.

Also query the Twitter API for KOL tweets (if `$X_BEARER_TOKEN` is available in the environment):
- Read `<WORKSPACE>/config/tech-digest-kol-list.json` for the KOL account list
- Ensure `$X_BEARER_TOKEN` is set (e.g. `source ~/.zshenv` or however the user configured it)
- Endpoint: `curl https://api.x.com/2/tweets/search/recent`
- Header: `"Authorization: Bearer $X_BEARER_TOKEN"`
- Params: `tweet.fields=created_at,author_id,public_metrics,entities&expansions=author_id&user.fields=username&max_results=20`
- Build `from:` queries by grouping handles from each category in the JSON (join with ` OR `), run one query per category
- If the API call fails or token is not set, skip and rely on web search results
- Keep only substantive tweets
- Tweet links: `https://x.com/{username}/status/{tweet_id}`

## Report Requirements
Merge and deduplicate all sources. Write a summary report. Use the sections defined in `tech-digest-topics.json` for topic categories, plus these fixed sections:
- 📢 KOL Updates (Twitter KOLs + notable blog posts from RSS authors)
- 🔥 Twitter/X Trending
- 📝 Blog Picks (<BLOG_PICKS_COUNT> high-quality deep articles discovered from RSS)
<EXTRA_SECTIONS>

### Deduplication Rules
- Same event from multiple sources → keep only the most authoritative source link
- If an event was already covered in the previous report → only include if there is significant new development
- Prefer primary sources (official blogs, first-party announcements) over media re-reporting

### Rules
- **Only include news from the <TIME_WINDOW>**
- **Append source link after each item** (wrap in `<link>` to suppress Discord previews)
- **<ITEMS_PER_SECTION> items per section**
- **Use bullet lists, no markdown tables** (Discord compatibility)

## Archive
Save the report to `<WORKSPACE>/archive/tech-digest/<MODE>-YYYY-MM-DD.md`

## Delivery
1. Send to Discord channel `<DISCORD_CHANNEL_ID>` via `message` tool
2. *(Optional)* Send to Telegram chat `<TELEGRAM_CHAT_ID>` via `message` tool (channel=telegram)
3. *(Optional)* Send email to `<EMAIL>` via `gog` CLI, subject: "<SUBJECT>"

If any delivery channel fails, log the error but continue with remaining channels. Do not retry failed deliveries.

Write the report in <LANGUAGE>.
