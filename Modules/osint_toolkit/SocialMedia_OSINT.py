import asyncio
import aiohttp
import json
import sys

# ==================== Core Config ====================
SITE_CONFIG = {
    "twitter": {"url": "https://twitter.com/{}"},
    "instagram": {"url": "https://www.instagram.com/{}"},
    "facebook": {"url": "https://www.facebook.com/{}"},
    "linkedin": {"url": "https://www.linkedin.com/in/{}"},
    "github": {"url": "https://github.com/{}"},
}


# ==================== Core Logic ====================
def get_social_data(username: str) -> dict:
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
        "DNT": "1",
    }

    async def fetch(session, platform, template):
        url = template.format(username)
        try:
            resp = await session.get(url, headers=HEADERS, timeout=10)
            status = "found" if resp.status == 200 else "not_found"
        except Exception:
            status = "error"
        return platform, status

    async def runner():
        async with aiohttp.ClientSession() as session:
            tasks = [
                fetch(session, plat, cfg["url"]) for plat, cfg in SITE_CONFIG.items()
            ]
            return await asyncio.gather(*tasks)

    results = asyncio.run(runner())
    return {plat: stat for plat, stat in results}


# ==================== CLI JSON-wrapper ====================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="OSINT: Social-media username lookup (JSON output)"
    )
    parser.add_argument(
        "--username",
        required=True,
        help="Username to investigate (without @)",
    )
    args = parser.parse_args()

    try:
        raw = get_social_data(args.username)

        # build a RESULTS list
        records = []
        for plat, status in raw.items():
            url = SITE_CONFIG[plat]["url"].format(args.username)
            records.append(
                {
                    "platform": plat,
                    "status": status,
                    "username": args.username,
                    "url": url,
                }
            )

        print(json.dumps({"results": records}, indent=2))

    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
