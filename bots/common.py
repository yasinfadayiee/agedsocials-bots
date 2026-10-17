"""Shared helpers: fetching, sitemap parsing and notifications (Telegram if configured, else a GitHub issue)."""
import json
import os
import re
import urllib.error
import urllib.request

SITE = os.environ.get("SITE", "https://agedsocials.com")
UA = "agedsocials-bots/1.0 (+https://github.com/yasinfadayiee/agedsocials-bots)"


def fetch(url, method="GET", data=None, headers=None, timeout=30):
    """Return (status, body_text). Network errors return status 0."""
    req = urllib.request.Request(url, data=data, method=method, headers={"User-Agent": UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace") if e.fp else ""
    except Exception as e:  # noqa: BLE001 - any network failure is reported, not raised
        return 0, str(e)


def sitemap_entries():
    """List of (url, lastmod) from sitemap.xml."""
    status, body = fetch(f"{SITE}/sitemap.xml")
    if status != 200:
        raise SystemExit(f"sitemap.xml returned {status}")
    out = []
    for block in re.findall(r"<url>(.*?)</url>", body, re.S):
        loc = re.search(r"<loc>([^<]+)</loc>", block)
        mod = re.search(r"<lastmod>([^<]+)</lastmod>", block)
        if loc:
            out.append((loc.group(1).strip(), mod.group(1).strip() if mod else ""))
    return out


def notify(title, text):
    """Send to Telegram when TG_BOT_TOKEN and TG_CHAT_ID secrets exist; otherwise open a GitHub issue (emails the owner)."""
    token, chat = os.environ.get("TG_BOT_TOKEN"), os.environ.get("TG_CHAT_ID")
    if token and chat:
        body = json.dumps({"chat_id": chat, "text": f"{title}\n\n{text}"[:4000], "disable_web_page_preview": True}).encode()
        fetch(f"https://api.telegram.org/bot{token}/sendMessage", "POST", body, {"content-type": "application/json"})
        return
    gh, repo = os.environ.get("GITHUB_TOKEN"), os.environ.get("GITHUB_REPOSITORY")
    if gh and repo:
        auth = {"authorization": f"Bearer {gh}", "accept": "application/vnd.github+json"}
        st, existing = fetch(f"https://api.github.com/repos/{repo}/issues?state=open&per_page=100", headers=auth)
        if st == 200 and any(i.get("title") == title[:200] for i in json.loads(existing)):
            return  # same alert already open: do not spam
        body = json.dumps({"title": title[:200], "body": text[:60000]}).encode()
        fetch(f"https://api.github.com/repos/{repo}/issues", "POST", body, {"authorization": f"Bearer {gh}", "accept": "application/vnd.github+json", "content-type": "application/json"})
        return
    print(title, text, sep="\n")
