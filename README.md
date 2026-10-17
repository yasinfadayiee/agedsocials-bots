# agedsocials-bots

Free daily automation for [agedsocials.com](https://agedsocials.com), run by GitHub Actions (public repo = unlimited free minutes).

| Bot | Schedule | What it does |
|---|---|---|
| `bots/health.py` | daily | Checks every sitemap URL, share images and the checkout APIs; reports problems only. |
| `bots/indexnow.py` | daily | Sends pages changed in the last 3 days to IndexNow (Bing, Yandex). |

Reports go to Telegram when the `TG_BOT_TOKEN` and `TG_CHAT_ID` repository secrets are set; otherwise a GitHub issue is opened (GitHub emails the owner). No private data or keys live in this repository.
