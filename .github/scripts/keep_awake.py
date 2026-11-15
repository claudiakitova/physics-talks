"""Open each live site in a real browser so Streamlit doesn't put apps to sleep.

Exits with an error if a site doesn't load, so the workflow can open an issue.
"""
import sys

from playwright.sync_api import sync_playwright

SITES = [
    # (url, text that appears once the site has loaded)
    ("https://physics-talks.streamlit.app/", "PhysicsTalks"),
    ("https://claudiakitova.github.io/moon-base-fire-evidence/", "Moon"),
]
WAKE_BUTTON = "Yes, get this app back up!"


def page_has_text(page, text):
    return any(frame.locator(f"text={text}").count() > 0 for frame in page.frames)


def check(page, url, expected):
    page.goto(url, wait_until="domcontentloaded", timeout=120_000)
    for _ in range(60):  # up to about 5 minutes
        if page_has_text(page, expected):
            return True
        for frame in page.frames:
            button = frame.get_by_role("button", name=WAKE_BUTTON)
            if button.count() > 0:
                print(f"{url}: app was asleep, waking it up")
                button.first.click()
        page.wait_for_timeout(5_000)
    return False


failed = []
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    for url, expected in SITES:
        ok = check(page, url, expected)
        print(f"{url}: {'OK' if ok else 'FAILED'}")
        if not ok:
            failed.append(url)
    browser.close()

if failed:
    print("Not loading: " + ", ".join(failed))
    sys.exit(1)
