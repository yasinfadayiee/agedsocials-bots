# agedsocials-bots

Free automation for [agedsocials.com](https://agedsocials.com), run by GitHub Actions (public repo = unlimited free minutes). No private data or keys live in this repository.

| Bot | When | What it does |
|---|---|---|
| `bots/uptime.py` | hourly | Key pages and checkout APIs; alerts only when something is down. |
| `bots/health.py` | daily | Every sitemap URL, share images and APIs; reports problems only. |
| `bots/indexnow.py` | daily | Sends pages changed in the last 3 days to IndexNow (Bing, Yandex). |
| `bots/gsc_report.py` | daily | Search Console 7-day report (needs `GSC_SERVICE_ACCOUNT`). |
| `bots/seo_audit.py` | weekly | Titles, descriptions, H1, canonical, noindex, JSON-LD, image alts, broken internal links. |
| `bots/pagespeed.py` | weekly | Mobile PageSpeed of the money pages (optional `PAGESPEED_API_KEY`). |

Notifications go to Telegram when the `TG_BOT_TOKEN` and `TG_CHAT_ID` secrets are set; otherwise a GitHub issue is opened (GitHub emails the owner; duplicate open alerts are skipped).
