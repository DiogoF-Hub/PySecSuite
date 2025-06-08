import requests
from leakcheck import LeakCheckAPI_Public
import json
import sys
import argparse


def get_email_data(email: str) -> dict:
    """
    Returns breach data and linked social platforms for a given email.
    """
    data = {"breaches": [], "social_links": []}

    # Breach lookup
    try:
        api = LeakCheckAPI_Public()
        results = api.lookup(query=email)

        # Only process if we got a list back
        if isinstance(results, list):
            for breach in results:
                if isinstance(breach, dict):
                    data["breaches"].append({
                        "site": breach.get("site"),
                        "date": breach.get("date", "Unknown"),
                        "data": breach.get("data", "Unknown"),
                    })
    except Exception as e:
        data["error"] = f"Failed to fetch breach data: {e}"

    # Social media linkage
    platforms = [
        "https://www.instagram.com/",
        "https://twitter.com/",
        "https://www.facebook.com/",
        "https://www.linkedin.com/",
        "https://www.pinterest.com/",
        "https://github.com/",
    ]
    for base in platforms:
        try:
            resp = requests.get(f"{base}search?q={email}", timeout=5)
            if resp.status_code == 200 and "No results found" not in resp.text:
                data["social_links"].append(base)
        except Exception:
            continue

    return data



# ==================== CLI JSON-wrapper ====================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="OSINT: Email breach and social-link lookup (JSON output)"
    )
    parser.add_argument(
        "--email",
        required=True,
        help="Email address to investigate"
    )
    args = parser.parse_args()
    try:
        result = get_email_data(args.email)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
