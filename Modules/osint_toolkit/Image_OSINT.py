import os
import requests
import json
import sys
import argparse

def get_image_data(path: str) -> dict:
    """
    Performs a reverse image search on Yandex and returns the result URL.
    """
    if not os.path.isfile(path):
        return {"error": "File not found"}

    search_url = "https://yandex.com/images/search"
    try:
        with open(path, "rb") as f:
            files = {"upfile": (os.path.basename(path), f, "application/octet-stream")}
            params = {
                "rpt": "imageview",
                "format": "json",
                "request": '{"blocks":[{"block":"b-page_type_search-by-image__link"}]}'
            }
            resp = requests.post(search_url, params=params, files=files, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            url = data["blocks"][0]["params"]["url"]
            return {"result_url": f"{search_url}?{url}"}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="OSINT: Image reverse-search (JSON output)"
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Path to image file to analyze"
    )
    args = parser.parse_args()

    try:
        result = get_image_data(args.image)
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
