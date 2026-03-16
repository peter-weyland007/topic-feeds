from pathlib import Path
from email.utils import format_datetime
from datetime import datetime, timezone
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
FEEDS = ROOT / "feeds"
FEEDS.mkdir(parents=True, exist_ok=True)

now = datetime.now(timezone.utc)
rfc822 = format_datetime(now)
iso = now.isoformat()
site = "https://peter-weyland007.github.io/topic-feeds"

items = [
    {
        "title": "Feed scaffold created",
        "link": f"{site}/",
        "guid": f"{site}/items/scaffold-created",
        "pubDate": rfc822,
        "description": "GitHub Pages + RSS scaffold is live. Discord ingestion still needs to be wired.",
    }
]


def build_rss(title: str, description: str, path: Path, items: list[dict]):
    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0">',
        '<channel>',
        f'<title>{escape(title)}</title>',
        f'<link>{escape(site + "/" + path.relative_to(ROOT).as_posix())}</link>',
        f'<description>{escape(description)}</description>',
        '<language>en-us</language>',
        f'<lastBuildDate>{rfc822}</lastBuildDate>',
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

build_rss(
    "Topic Feeds — All",
    "Combined feed scaffold for iPhone/Unread.",
    FEEDS / "all.xml",
    items,
)

build_rss(
    "Topic Feeds — app-grimoire",
    "Channel/topic feed scaffold for Discord channel #app-grimoire.",
    FEEDS / "app-grimoire.xml",
    items,
)

opml = f'''<?xml version="1.0" encoding="UTF-8"?>
<opml version="2.0">
  <head>
    <title>Topic Feeds</title>
    <dateCreated>{escape(iso)}</dateCreated>
  </head>
  <body>
    <outline text="Topic Feeds">
      <outline type="rss" text="All" title="All" xmlUrl="{site}/feeds/all.xml" htmlUrl="{site}/" />
      <outline type="rss" text="app-grimoire" title="app-grimoire" xmlUrl="{site}/feeds/app-grimoire.xml" htmlUrl="{site}/" />
    </outline>
  </body>
</opml>
'''
(ROOT / "feeds.opml").write_text(opml, encoding="utf-8")

index = f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Topic Feeds</title>
  </head>
  <body>
    <h1>Topic Feeds</h1>
    <p>Static RSS feeds for Unread.</p>
    <ul>
      <li><a href="feeds/all.xml">All feed</a></li>
      <li><a href="feeds/app-grimoire.xml">app-grimoire feed</a></li>
      <li><a href="feeds.opml">OPML import</a></li>
    </ul>
    <p>Last generated: {escape(iso)}</p>
  </body>
</html>
'''
(ROOT / "index.html").write_text(index, encoding="utf-8")
