#!/usr/bin/env python3
"""
Fetch RSS feeds in parallel and output structured JSON.
Usage: python3 fetch-rss.py <config.json> [--hours 48] [--output result.json]
"""

import json
import re
import sys
import os
import argparse
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urljoin

TIMEOUT = 15
MAX_WORKERS = 10
MAX_ARTICLES_PER_FEED = 20


def parse_date(s):
    if not s:
        return None
    s = s.strip()
    for fmt in [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]:
        try:
            dt = datetime.strptime(s, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            pass
    # ISO fallback
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt
    except (ValueError, AttributeError):
        pass
    return None


def extract_cdata(text):
    m = re.search(r"<!\[CDATA\[(.*?)\]\]>", text, re.DOTALL)
    return m.group(1) if m else text


def strip_tags(html):
    return re.sub(r"<[^>]+>", "", html).strip()


def get_tag(xml, tag):
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", xml, re.DOTALL | re.IGNORECASE)
    return extract_cdata(m.group(1)).strip() if m else ""


def resolve_link(link, base_url):
    """Resolve relative links against the feed URL."""
    if not link:
        return link
    if link.startswith(("http://", "https://")):
        return link
    return urljoin(base_url, link)


def parse_feed(content, cutoff, feed_url):
    articles = []

    # RSS 2.0 items
    for item in re.finditer(r"<item[^>]*>(.*?)</item>", content, re.DOTALL):
        block = item.group(1)
        title = strip_tags(get_tag(block, "title"))
        link = resolve_link(get_tag(block, "link"), feed_url)
        date_str = get_tag(block, "pubDate") or get_tag(block, "dc:date")
        pub = parse_date(date_str)

        if title and link:
            # Require a valid date — skip articles with no parseable date
            # to avoid including undated old content
            if pub is not None and pub >= cutoff:
                articles.append({
                    "title": title[:200],
                    "link": link,
                    "date": pub.isoformat(),
                })

    # Atom entries fallback
    if not articles:
        for entry in re.finditer(r"<entry[^>]*>(.*?)</entry>", content, re.DOTALL):
            block = entry.group(1)
            title = strip_tags(get_tag(block, "title"))
            link_m = re.search(r'<link[^>]*href=["\']([^"\']+)["\']', block)
            if not link_m:
                link = get_tag(block, "link")
            else:
                link = link_m.group(1)
            link = resolve_link(link, feed_url)
            date_str = get_tag(block, "updated") or get_tag(block, "published")
            pub = parse_date(date_str)

            if title and link:
                if pub is not None and pub >= cutoff:
                    articles.append({
                        "title": title[:200],
                        "link": link,
                        "date": pub.isoformat(),
                    })

    return articles[:MAX_ARTICLES_PER_FEED]


def fetch_feed(feed_info, cutoff):
    name = feed_info["name"]
    url = feed_info["url"]
    priority = feed_info["priority"]
    category = feed_info["category"]

    try:
        req = Request(url, headers={"User-Agent": "TechDigest/1.0"})
        with urlopen(req, timeout=TIMEOUT) as resp:
            final_url = resp.url if hasattr(resp, 'url') else url
            content = resp.read().decode("utf-8", errors="replace")
        articles = parse_feed(content, cutoff, final_url)
        return {
            "name": name,
            "url": url,
            "category": category,
            "priority": priority,
            "status": "ok",
            "count": len(articles),
            "articles": articles,
        }
    except Exception as e:
        return {
            "name": name,
            "url": url,
            "category": category,
            "priority": priority,
            "status": "error",
            "error": str(e)[:100],
            "count": 0,
            "articles": [],
        }


def load_feeds(config_path):
    with open(config_path) as f:
        data = json.load(f)

    feeds = []
    for cat, items in data.items():
        if cat.startswith("_") or not isinstance(items, list):
            continue
        for item in items:
            if "rss" in item:
                feeds.append({
                    "name": item.get("name", ""),
                    "url": item["rss"],
                    "priority": bool(item.get("priority")),
                    "category": cat,
                })
    return feeds


def clean_archive(archive_dir, keep_days=30):
    """Remove archive files older than keep_days."""
    if not os.path.isdir(archive_dir):
        return 0
    cutoff = datetime.now() - timedelta(days=keep_days)
    removed = 0
    for f in os.listdir(archive_dir):
        if not f.endswith(".md"):
            continue
        # Extract date from filename: daily-YYYY-MM-DD.md or weekly-YYYY-MM-DD.md
        m = re.search(r"(\d{4}-\d{2}-\d{2})", f)
        if m:
            try:
                file_date = datetime.strptime(m.group(1), "%Y-%m-%d")
                if file_date < cutoff:
                    os.remove(os.path.join(archive_dir, f))
                    removed += 1
            except ValueError:
                pass
    return removed


def main():
    parser = argparse.ArgumentParser(
        description="Parallel RSS/Atom feed fetcher for tech-digest skill. "
                    "Fetches all feeds from a config JSON, filters by time window, "
                    "and outputs structured article data as JSON.",
        epilog="Example: python3 fetch-rss.py config.json --hours 48 -o results.json"
    )
    parser.add_argument("config", help="Path to tech-digest-rss-feeds.json config file")
    parser.add_argument("--hours", type=int, default=48, help="Time window in hours (default: 48)")
    parser.add_argument("--output", "-o", default=None, help="Output JSON path (default: auto-generated temp file)")
    parser.add_argument("--clean-archive", default=None, metavar="DIR", help="Clean archive files older than 30 days from DIR")
    args = parser.parse_args()

    # Clean archive if requested
    if args.clean_archive:
        removed = clean_archive(args.clean_archive)
        if removed:
            print(f"Cleaned {removed} old archive files", file=sys.stderr)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    feeds = load_feeds(args.config)

    # Auto-generate unique output path if not specified
    if not args.output:
        import tempfile
        fd, args.output = tempfile.mkstemp(prefix="tech-digest-rss-", suffix=".json")
        os.close(fd)

    print(f"Fetching {len(feeds)} RSS feeds (window: {args.hours}h)...", file=sys.stderr)

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(fetch_feed, f, cutoff): f for f in feeds}
        for future in as_completed(futures):
            results.append(future.result())

    # Sort: priority first, then by article count
    results.sort(key=lambda x: (not x.get("priority"), -x.get("count", 0)))

    ok = sum(1 for r in results if r["status"] == "ok")
    total_articles = sum(r.get("count", 0) for r in results)

    output = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "hours": args.hours,
        "feeds_total": len(results),
        "feeds_ok": ok,
        "total_articles": total_articles,
        "feeds": results,
    }

    json_str = json.dumps(output, ensure_ascii=False, indent=2)

    with open(args.output, "w") as f:
        f.write(json_str)

    print(f"Done: {ok}/{len(results)} feeds ok, {total_articles} articles → {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
