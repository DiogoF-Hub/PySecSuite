#!/usr/bin/env python3
import asyncio
import aiohttp
import sys
import re

# Configuration for selected platforms, inspired by Sherlock's data.json
SITE_CONFIG = {
    "Instagram": {
        "url": "https://www.instagram.com/{}/",
        "method": "GET",
        "errorType": "message",
        "errorMsg": [r"Sorry,\s*this\s*page\s*isn'?t\s*available"],
    },
    "Facebook": {
        "url": "https://www.facebook.com/{}",
        "method": "GET",
        "errorType": "message",
        "errorMsg": [r"Content\s*isn'?t\s*available"],
    },
    "TikTok": {
        "url": "https://www.tiktok.com/@{}",
        "method": "GET",
        "errorType": "message",
        "errorMsg": [r"Page\s*Not\s*Found", r"Video\s*doesn't\s*exist"],
    },
    "LinkedIn": {
        "url": "https://www.linkedin.com/mwlite/in/{}",
        "method": "GET",
        "errorType": "status_code",
        "errorCode": [404],
        "loginMsg": [r"log in", r"sign in"],  # detect login gate
    },
    "YouTube": {
        "url": "https://www.youtube.com/user/{}",
        "method": "GET",
        "errorType": "message",
        "errorMsg": [r"404\s*Not\s*Found", r"Something\s*went\s*wrong"],
    },
    "X": {
        "url": "https://x.com/{}",
        "method": "GET",
        "errorType": "message",
        "errorMsg": [r"This\s*account\s*doesn'?t\s*exist"],
    },
    "Reddit": {
        "url": "https://www.reddit.com/user/{}",
        "method": "GET",
        "errorType": "message",
        "errorMsg": [r"nobody\s*on\s*Reddit\s*goes\s*by\s*that\s*name"],
    },
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/112.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


async def fetch(session, platform, handle):
    """
    Checks a single profile URL using the rules from SITE_CONFIG.
    Returns (platform, status, url).
    Status codes: 'found', 'requires_login', 'not_found', 'error'.
    """
    cfg = SITE_CONFIG[platform]
    url = cfg["url"].format(handle)
    try:
        # perform the request (GET)
        method = cfg.get("method", "GET").lower()
        resp = await getattr(session, method)(url, headers=HEADERS, timeout=10)
        text = await resp.text()
        code = resp.status
    except Exception as e:
        return platform, "error", f"{url} ({e})"

    status = None
    # status_code based not_found
    if cfg.get("errorType") == "status_code":
        if code in cfg.get("errorCode", []):
            status = "not_found"
    # message based not_found
    elif cfg.get("errorType") == "message":
        if code == 404:
            status = "not_found"
        else:
            for pat in cfg.get("errorMsg", []):
                if re.search(pat, text, re.IGNORECASE):
                    status = "not_found"
                    break
    # LinkedIn login gate detection
    if platform == "LinkedIn" and code == 200 and not status:
        for pat in cfg.get("loginMsg", []):
            if re.search(pat, text, re.IGNORECASE):
                status = "requires_login"
                break

    # default statuses
    if not status:
        if code == 200:
            status = "found"
        else:
            status = "error"

    return platform, status, url


async def main(username):
    # sanitize input: remove spaces, lowercase only for LinkedIn
    base = username.replace(" ", "")
    print(f"\n🔍 Searching for variants of '{username}'...\n")
    async with aiohttp.ClientSession() as session:
        tasks = []
        for platform in SITE_CONFIG:
            handle = base.lower() if platform == "LinkedIn" else base
            tasks.append(fetch(session, platform, handle))
        results = await asyncio.gather(*tasks)

    # categorize results
    found = [url for plat, st, url in results if st == "found"]
    gated = [url for plat, st, url in results if st == "requires_login"]
    missing = [plat for plat, st, url in results if st == "not_found"]
    errors = [(plat, info) for plat, st, info in results if st == "error"]

    # print summary
    if found:
        print("✅ Public profiles:")
        for url in found:
            print("  ", url)
    if gated:
        print("\n🔒 Login-gated (requires account):")
        for url in gated:
            print("  ", url)
    if missing:
        print("\n❌ Not found:")
        for plat in missing:
            print("  ", plat)
    if errors:
        print("\n⚠️ Errors:")
        for plat, info in errors:
            print(f"  {plat}: {info}")

    print(
        "\nℹ️ Note: 'login-gated' profiles may still be real, and some results could be false positives."
    )


if __name__ == "__main__":
    if sys.version_info < (3, 7):
        sys.exit("Requires Python 3.7+")
    username = input("Enter a username: ").strip()
    if not username:
        sys.exit("No username provided; exiting.")
    asyncio.run(main(username))
