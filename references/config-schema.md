# Config File Schema

## tech-digest-rss-feeds.json

```json
{
  "_description": "string (optional, ignored by parser)",
  "_updated": "string (optional, ignored by parser)",
  "<category_name>": [
    {
      "name": "string (required) — display name",
      "rss": "string (required) — RSS/Atom feed URL",
      "priority": "boolean (optional, default false) — fetched first when true",
      "note": "string (optional) — human-readable description"
    }
  ]
}
```

**Category names**: any string not starting with `_`. Recommended: `ai_ml`, `crypto`, `tech_general`, `chinese_tech`.

**Validation rules**:
- Each feed must have `name` and `rss` fields
- `rss` must be a valid HTTP/HTTPS URL
- Category keys starting with `_` are metadata and ignored
- Test new feeds: `curl -sL --max-time 15 "<url>" | head -5` should return XML

## tech-digest-kol-list.json

```json
{
  "_description": "string (optional, ignored by parser)",
  "_updated": "string (optional, ignored by parser)",
  "<category_name>": [
    {
      "handle": "string (required) — Twitter/X username without @",
      "name": "string (required) — display name and affiliation"
    }
  ]
}
```

**Category names**: any string not starting with `_`. Recommended: `ai_labs`, `ai_builders`, `crypto_global`, `crypto_cn`, `tech_leaders`.

**Validation rules**:
- Each KOL must have `handle` and `name` fields
- `handle` should not include the `@` prefix (e.g. `"sama"` not `"@sama"`)
- `name` should include affiliation for context (e.g. `"Sam Altman (OpenAI CEO)"`)
- Handles in the same category are joined into a single `from:` API query
- Keep categories small enough that the combined `from:` query stays under Twitter API limits (~512 chars)

**Example**:
```json
{ "handle": "karpathy", "name": "Andrej Karpathy" }
```

## tech-digest-topics.json

```json
{
  "_description": "string (optional)",
  "topics": [
    {
      "id": "string (required) — unique identifier",
      "emoji": "string (required) — section emoji",
      "label": "string (required) — section heading",
      "keywords": ["string (required) — web search queries for this topic"],
      "twitter_queries": ["string (optional) — web search queries for Twitter trending on this topic"]
    }
  ]
}
```

**Validation rules**:
- Each topic must have `id`, `emoji`, `label`, and `keywords`
- `keywords` is an array of search queries used with `web_search`
- `twitter_queries` (optional) is an array of search queries for finding trending Twitter discussions on this topic
- Topics define both the search strategy and the report section structure
- Order in the array determines section order in the report
