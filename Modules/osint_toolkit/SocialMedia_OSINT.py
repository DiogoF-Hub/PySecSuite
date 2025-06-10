import asyncio
import aiohttp
import json
import sys


# ==================== Core Logic ====================
def get_social_data(username: str) -> dict:
    """
    Checks common social platforms for existence of a given username.
    Returns a dict of {platform: status}.

    """
    SITE_CONFIG = {
        "twitter": {"url": "https://twitter.com/{}"},
        "instagram": {"url": "https://www.instagram.com/{}"},
        "facebook": {"url": "https://www.facebook.com/{}"},
        "linkedin": {"url": "https://www.linkedin.com/in/{}"},
        "github": {"url": "https://github.com/{}"},
        # Add more if needed but carefull how each web handles the usernames
    }
    HEADERS = {"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US"}

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
                fetch(session, platform, cfg["url"])
                for platform, cfg in SITE_CONFIG.items()
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
        result = get_social_data(args.username)
        print(json.dumps(result))
    except Exception as e:
        # Print error to stderr as JSON
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
