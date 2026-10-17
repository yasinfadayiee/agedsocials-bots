"""Daily Search Console report: last 7 days vs the 7 before, top queries and pages, biggest position moves.
Runs only when the GSC_SERVICE_ACCOUNT secret (service-account JSON with read access to the property) exists."""
import datetime as dt
import json
import os
import sys

from common import notify

raw = os.environ.get("GSC_SERVICE_ACCOUNT", "")
if not raw:
    print("GSC_SERVICE_ACCOUNT not set: skipping")
    sys.exit(0)

from google.oauth2 import service_account  # noqa: E402  (installed by the workflow)
from google.auth.transport.requests import AuthorizedSession  # noqa: E402

PROPERTY = os.environ.get("GSC_PROPERTY", "https://agedsocials.com/")
creds = service_account.Credentials.from_service_account_info(json.loads(raw), scopes=["https://www.googleapis.com/auth/webmasters.readonly"])
s = AuthorizedSession(creds)
API = "https://searchconsole.googleapis.com/webmasters/v3/sites/" + __import__("urllib.parse").parse.quote(PROPERTY, safe="") + "/searchAnalytics/query"
end = dt.date.today() - dt.timedelta(days=3)  # GSC data lags ~2-3 days


def q(start, stop, dims, limit=25):
    r = s.post(API, json={"startDate": start.isoformat(), "endDate": stop.isoformat(), "dimensions": dims, "rowLimit": limit})
    r.raise_for_status()
    return r.json().get("rows", [])


def tot(rows):
    c = sum(r["clicks"] for r in rows); i = sum(r["impressions"] for r in rows)
    pos = sum(r["position"] * r["impressions"] for r in rows) / i if i else 0
    return c, i, pos


cur = q(end - dt.timedelta(days=6), end, ["date"])
prev = q(end - dt.timedelta(days=13), end - dt.timedelta(days=7), ["date"])
c1, i1, p1 = tot(cur); c0, i0, p0 = tot(prev)
lines = [f"Last 7 days (to {end}): {c1} clicks ({c1 - c0:+}), {i1} impressions ({i1 - i0:+}), avg position {p1:.1f} ({p1 - p0:+.1f})", ""]
qc = {r["keys"][0]: r for r in q(end - dt.timedelta(days=6), end, ["query"], 200)}
qp = {r["keys"][0]: r for r in q(end - dt.timedelta(days=13), end - dt.timedelta(days=7), ["query"], 200)}
lines.append("Top queries:")
for k, r in sorted(qc.items(), key=lambda kv: -kv[1]["impressions"])[:10]:
    lines.append(f"• {k} — {r['clicks']} clicks, {r['impressions']} impr, pos {r['position']:.1f}")
moves = [(k, qp[k]["position"] - r["position"], r) for k, r in qc.items() if k in qp and r["impressions"] >= 5]
up = sorted(moves, key=lambda m: -m[1])[:5]
down = sorted(moves, key=lambda m: m[1])[:5]
lines.append("\nBiggest gains:")
lines += [f"↑ {k}: pos {r['position']:.1f} ({d:+.1f})" for k, d, r in up if d > 0] or ["—"]
lines.append("\nBiggest drops:")
lines += [f"↓ {k}: pos {r['position']:.1f} ({d:+.1f})" for k, d, r in down if d < 0] or ["—"]
pages = q(end - dt.timedelta(days=6), end, ["page"], 10)
lines.append("\nTop pages:")
lines += [f"• {r['keys'][0].replace(PROPERTY.rstrip('/'), '')} — {r['clicks']} clicks, {r['impressions']} impr" for r in pages]
print("\n".join(lines))
notify("📊 Search Console daily — agedsocials.com", "\n".join(lines))
