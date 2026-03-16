# topic-feeds

Static RSS feeds for use with Unread on iPhone.

## Current status

Publishing is wired to Mission Control's local news store.

Source file:
- `/Users/itadmin/.openclaw/workspace/agents/coder/projects/MissionControl/app/data/news-monitor.json`

Outputs:
- `feeds/all.xml` — combined feed
- `feeds/<topic>.xml` — one feed per Mission Control topic
- `feeds.opml` — bulk import file for RSS readers

## Local update

```bash
python3 scripts/build_feeds.py
```

## Notes

Mission Control is also configured to regenerate these feeds automatically after topic/article changes.
