# topic-feeds

Static RSS feeds for use with Unread on iPhone.

## Current status

Publishing scaffold is ready. Discord ingestion/source automation is not wired yet.

## Planned outputs

- `feeds/all.xml` — combined feed
- `feeds/app-grimoire.xml` — per-topic/per-channel feed
- `feeds.opml` — bulk import file for RSS readers

## Local update

```bash
python3 scripts/build_feeds.py
```
