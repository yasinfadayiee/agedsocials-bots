"""Weekly PageSpeed (mobile) for the main money pages. Uses the PAGESPEED_API_KEY secret if set (free key from Google Cloud)."""
import json
import os
import urllib.parse

from common import SITE, fetch, notify

PAGES = ["/", "/aged-telegram-accounts/", "/old-telegram-channels/", "/telegram-virtual-numbers/", "/smm-panel/"]
key = os.environ.get("PAGESPEED_API_KEY", "")
rows, slow = [], []
for p in PAGES:
    q = {"url": SITE + p, "strategy": "mobile", "category": "performance"}
    if key:
        q["key"] = key
    st, body = fetch("https://www.googleapis.com/pagespeedonline/v5/runPagespeed?" + urllib.parse.urlencode(q), timeout=120)
    if st != 200:
        rows.append(f"{p}: PageSpeed API {st} (add a free PAGESPEED_API_KEY secret)")
        continue
    lh = json.loads(body).get("lighthouseResult", {})
    score = round(100 * (lh.get("categories", {}).get("performance", {}).get("score") or 0))
    a = lh.get("audits", {})
    lcp = a.get("largest-contentful-paint", {}).get("displayValue", "?")
    cls = a.get("cumulative-layout-shift", {}).get("displayValue", "?")
    rows.append(f"{p}: {score}/100 · LCP {lcp} · CLS {cls}")
    if score < 70:
        slow.append(p)
print("\n".join(rows))
notify(("⚠️" if slow else "📱") + f" Weekly mobile speed {__import__('datetime').date.today()} — agedsocials.com", "\n".join(rows))
