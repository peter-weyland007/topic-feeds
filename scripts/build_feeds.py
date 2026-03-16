from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from email.utils import format_datetime, parsedate_to_datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
FEEDS = ROOT / "feeds"
FEEDS.mkdir(parents=True, exist_ok=True)

MISSION_CONTROL_STORE = Path(
    "/Users/itadmin/.openclaw/workspace/agents/coder/projects/MissionControl/app/data/news-monitor.json"
)
SITE = "https://peter-weyland007.github.io/topic-feeds"
NOW = datetime.now(timezone.utc)
ISO = NOW.isoformat()
RFC822 = format_datetime(NOW)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "topic"


def parse_pub_date(value: str | None) -> datetime:
    if not value:
        return NOW
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except Exception:
            return NOW


def item_description(article: dict) -> str:
    parts: list[str] = []
    summary = (article.get("summary") or "").strip()
    source = (article.get("source") or "").strip()
    topic = (article.get("topicName") or "").strip()
    if summary:
        parts.append(summary)
    meta_bits = [bit for bit in [f"Source: {source}" if source else "", f"Topic: {topic}" if topic else ""] if bit]
    if meta_bits:
        parts.append(" | ".join(meta_bits))
    return "\n\n".join(parts) or "Mission Control article"


def build_rss(title: str, description: str, path: Path, items: list[dict]) -> None:
    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0">',
        '<channel>',
        f'<title>{escape(title)}</title>',
        f'<link>{escape(SITE + "/" + path.relative_to(ROOT).as_posix())}</link>',
        f'<description>{escape(description)}</description>',
        '<language>en-us</language>',
        f'<lastBuildDate>{RFC822}</lastBuildDate>',
        '<generator>topic-feeds/scripts/build_feeds.py</generator>',
    ]
    for item in items:
        xml.extend([
            '<item>',
            f'<title>{escape(item["title"])}</title>',
            f'<link>{escape(item["link"])}</link>',
            f'<guid>{escape(item["guid"])}</guid>',
            f'<pubDate>{escape(item["pubDate"])}</pubDate>',
            f'<description>{escape(item["description"])}</description>',
            '</item>',
        ])
    xml.extend(['</channel>', '</rss>'])
    path.write_text("\n".join(xml) + "\n", encoding="utf-8")


state = json.loads(MISSION_CONTROL_STORE.read_text(encoding="utf-8"))
topics = state.get("topics", [])
articles = state.get("articles", [])
articles_by_topic: dict[str, list[dict]] = defaultdict(list)

normalized_items: list[dict] = []
for article in articles:
    pub_dt = parse_pub_date(article.get("publishedAt") or article.get("fetchedAt"))
    item = {
        "title": article.get("title") or "Untitled article",
        "link": article.get("url") or SITE,
        "guid": article.get("id") or article.get("url") or f"generated-{pub_dt.timestamp()}",
        "pubDate": format_datetime(pub_dt),
        "description": item_description(article),
        "topicId": article.get("topicId"),
        "topicName": article.get("topicName") or "Unknown topic",
        "sortKey": pub_dt.timestamp(),
    }
    normalized_items.append(item)
    if item["topicId"]:
        articles_by_topic[item["topicId"]].append(item)

normalized_items.sort(key=lambda item: item["sortKey"], reverse=True)
for values in articles_by_topic.values():
    values.sort(key=lambda item: item["sortKey"], reverse=True)

build_rss(
    "Topic Feeds — All",
    "Combined Mission Control feed for Unread.",
    FEEDS / "all.xml",
    normalized_items,
)

feed_links: list[tuple[str, str]] = [("All", "feeds/all.xml")]
for topic in topics:
    slug = slugify(topic.get("name") or "topic")
    rel_path = f"feeds/{slug}.xml"
    build_rss(
        f"Topic Feeds — {topic.get('name', 'Topic')}",
        f"Mission Control feed for topic: {topic.get('name', 'Topic')}",
        ROOT / rel_path,
        articles_by_topic.get(topic.get("id"), []),
    )
    feed_links.append((topic.get("name") or slug, rel_path))

opml_lines = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<opml version="2.0">',
    '  <head>',
    '    <title>Topic Feeds</title>',
    f'    <dateCreated>{escape(ISO)}</dateCreated>',
    '  </head>',
    '  <body>',
    '    <outline text="Topic Feeds">',
]
for name, rel_path in feed_links:
    opml_lines.append(
        f'      <outline type="rss" text="{escape(name)}" title="{escape(name)}" xmlUrl="{escape(SITE + "/" + rel_path)}" htmlUrl="{escape(SITE + "/")}" />'
    )
opml_lines.extend([
    '    </outline>',
    '  </body>',
    '</opml>',
])
(ROOT / "feeds.opml").write_text("\n".join(opml_lines) + "\n", encoding="utf-8")

list_items = "\n".join(
    f'      <li><a href="{escape(rel_path)}">{escape(name)} feed</a></li>' for name, rel_path in feed_links
)
index = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Topic Feeds</title>
  </head>
  <body>
    <h1>Topic Feeds</h1>
    <p>Static RSS feeds exported from Mission Control for Unread.</p>
    <ul>
{list_items}
      <li><a href="feeds.opml">OPML import</a></li>
    </ul>
    <p>Source: Mission Control news monitor</p>
    <p>Last generated: {escape(ISO)}</p>
  </body>
</html>
'''
(ROOT / "index.html").write_text(index, encoding="utf-8")
