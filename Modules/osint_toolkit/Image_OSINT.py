import os
import json
import requests


def reverse_image_search(image_path):
    if not os.path.isfile(image_path):
        print("❌ File not found. Please check the path and try again.")
        return

    search_url = "https://yandex.com/images/search"
    files = {"upfile": ("image.jpg", open(image_path, "rb"), "image/jpeg")}
    params = {
        "rpt": "imageview",
        "format": "json",
        "request": '{"blocks":[{"block":"b-page_type_search-by-image__link"}]}',
    }

    print("🔎 Uploading image to Yandex...")
    response = requests.post(search_url, params=params, files=files)
    response.raise_for_status()

    try:
        data = response.json()
        image_url = data["blocks"][0]["params"]["url"]
        result_url = f"{search_url}?{image_url}"
        print(f"✅ Reverse image search URL: {result_url}")
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        print("❌ Failed to parse Yandex response:", e)


# Example usage
image_path = input("Enter the full path to the image you want to search: ").strip()
reverse_image_search(image_path)
