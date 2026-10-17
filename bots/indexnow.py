"""Daily IndexNow ping (Bing, Yandex and partners) for sitemap URLs changed in the last 3 days."""
import datetime as dt
import json

from common import SITE, fetch, sitemap_entries

KEY = "fa6268d76d9782402a67128792db0abb"  # public by design: served at /<key>.txt on the site
cutoff = (dt.date.today() - dt.timedelta(days=3)).isoformat()
changed = [u for u, mod in sitemap_entries() if mod and mod[:10] >= cutoff]
if not changed:
    print("nothing changed")
    raise SystemExit(0)
host = SITE.split("//", 1)[1]
for i in range(0, len(changed), 10000):
    body = json.dumps({"host": host, "key": KEY, "keyLocation": f"{SITE}/{KEY}.txt", "urlList": changed[i:i + 10000]}).encode()
    status, text = fetch("https://api.indexnow.org/indexnow", "POST", body, {"content-type": "application/json; charset=utf-8"})
    print(f"IndexNow {status} for {len(changed[i:i + 10000])} URLs {text[:200]}")
    if status not in (200, 202):
        raise SystemExit(1)
