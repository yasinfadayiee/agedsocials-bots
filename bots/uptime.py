"""Hourly uptime check of the pages and APIs buyers depend on. Alerts only when something is down."""
from common import SITE, fetch, notify

CHECKS = [
    ("/", "<title>"),
    ("/aged-telegram-accounts/", "<title>"),
    ("/telegram-virtual-numbers/", "<title>"),
    ("/smm-panel/", "<title>"),
    ("/order/", "<title>"),
    ("/api/shop/status", '"enabled"'),
    ("/api/smm/enabled", '"enabled"'),
]
down = []
for path, must in CHECKS:
    status, body = fetch(SITE + path, timeout=20)
    if status != 200 or must not in body:
        status, body = fetch(SITE + path, timeout=30)  # one retry before alerting
        if status != 200 or must not in body:
            down.append(f"{status} {SITE}{path}")
print("down:", down or "none")
if down:
    notify("🔴 agedsocials.com is DOWN or broken", "\n".join(down))
