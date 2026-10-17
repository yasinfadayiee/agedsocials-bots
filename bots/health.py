"""Daily health check: every sitemap URL answers 200, key APIs respond, and share images load. Reports only problems."""
import concurrent.futures as cf
import re

from common import SITE, fetch, notify, sitemap_entries

problems = []
entries = sitemap_entries()
urls = [u for u, _ in entries]


def check(url):
    status, body = fetch(url)
    issues = []
    if status != 200:
        issues.append(f"{status} {url}")
    elif "<title>" not in body:
        issues.append(f"no <title> {url}")
    images = re.findall(r'<meta property="og:image" content="([^"]+)"', body)[:1]
    return issues, images


images = set()
with cf.ThreadPoolExecutor(max_workers=12) as pool:
    for issues, imgs in pool.map(check, urls):
        problems += issues
        images.update(imgs)

for img in sorted(images):
    status, _ = fetch(img, method="HEAD")
    if status != 200:
        problems.append(f"{status} image {img}")

for path, must in (("/api/shop/status", '"enabled"'), ("/api/smm/enabled", '"enabled"')):
    status, body = fetch(SITE + path)
    if status != 200 or must not in body:
        problems.append(f"API {path} -> {status} {body[:120]}")

print(f"checked {len(urls)} pages, {len(images)} share images: {len(problems)} problems")
if problems:
    notify(f"⚠️ agedsocials.com: {len(problems)} problems found", "\n".join(problems[:150]))
