import os
import requests

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
assets_dir = os.path.join(root_dir, "Assets")
wordlist_dir = os.path.join(assets_dir, "Wordlists")

if not os.path.exists(assets_dir):
    os.makedirs(assets_dir)

if not os.path.exists(wordlist_dir):
    os.makedirs(wordlist_dir)


url = (
    "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt"
)


def download_wordlist(url, name):
    wordlist_path = os.path.join(wordlist_dir, name)

    if os.path.exists(wordlist_path):
        print(f"Wordlist already exists at {wordlist_path}")
        return

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        with open(wordlist_path, "wb") as file:
            file.write(response.content)
        print(f"Wordlist downloaded successfully and saved to {wordlist_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading wordlist: {e}")
