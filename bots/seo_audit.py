"""Weekly on-page SEO audit of the live English pages: titles, descriptions, H1, canonical, noindex, JSON-LD,
missing image alts and broken internal links. Always sends a short summary."""
import concurrent.futures as cf
import html
import json
import re

from common import SITE, fetch, notify, sitemap_entries

LOCALES = ("/tr/", "/ru/", "/fa/", "/he/", "/zh-hans/", "/zh-hant/")
urls = [u for u, _ in sitemap_entries() if not any(l in u for l in LOCALES)]
issues = {k: [] for k in ("title", "description", "h1", "canonical", "noindex", "jsonld", "alt")}
links = set()


def audit(url):
    status, s = fetch(url)
    if status != 200:
        return url, None
    return url, s


with cf.ThreadPoolExecutor(max_workers=12) as pool:
    pages = list(pool.map(audit, urls))

for url, s in pages:
    if s is None:
        continue
    path = url[len(SITE):]
    t = html.unescape((re.search(r"<title>(.*?)</title>", s, re.S) or [None, ""])[1]).strip()
    d = html.unescape((re.search(r'<meta name="description" content="([^"]*)"', s) or [None, ""])[1])
    if not 25 <= len(t) <= 65:
        issues["title"].append(f"{len(t)} chars {path}")
    if not 70 <= len(d) <= 170:
        issues["description"].append(f"{len(d)} chars {path}")
    if len(re.findall(r"<h1[ >]", s)) != 1:
        issues["h1"].append(path)
    c = re.search(r'<link rel="canonical" href="([^"]+)"', s)
    if not c or c.group(1) != url:
        issues["canonical"].append(path)
    if re.search(r'<meta name="robots" content="[^"]*noindex', s):
        issues["noindex"].append(path)
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        try:
            json.loads(m.group(1))
        except ValueError:
            issues["jsonld"].append(path)
    main = re.search(r"<main.*?</main>", s, re.S)
    body = main.group(0) if main else s
    if re.search(r'<img class="cover"[^>]*alt=""', body):
        issues["alt"].append(path)
    links.update(h for h in re.findall(r'href="(/[^"#?]*)"', body) if not h.startswith("/assets/"))

known = {u[len(SITE):] for u in urls}
to_check = sorted(l for l in links if l not in known)


def head(path):
    st, _ = fetch(SITE + path, method="HEAD")
    if st in (405, 0):
        st, _ = fetch(SITE + path)
    return path, st


broken = []
with cf.ThreadPoolExecutor(max_workers=12) as pool:
    for path, st in pool.map(head, to_check):
        if st not in (200, 301, 302, 308):
            broken.append(f"{st} {path}")

lines = [f"Pages audited: {len(urls)} English pages", f"Broken internal links: {len(broken)}"]
lines += [f"{k}: {len(v)}" for k, v in issues.items()]
detail = []
if broken:
    detail.append("BROKEN LINKS\n" + "\n".join(broken[:50]))
for k, v in issues.items():
    if v and k in ("h1", "canonical", "noindex", "jsonld", "alt"):
        detail.append(k.upper() + "\n" + "\n".join(v[:30]))
serious = broken or any(issues[k] for k in ("h1", "canonical", "noindex", "jsonld"))
print("\n".join(lines))
notify(("⚠️" if serious else "✅") + " Weekly SEO audit — agedsocials.com", "\n".join(lines) + ("\n\n" + "\n\n".join(detail) if detail else ""))
