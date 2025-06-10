import os
import requests
import streamlit as st

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
assets_dir = os.path.join(root_dir, "Assets")
wordlist_dir = os.path.join(assets_dir, "Wordlists")


url = (
    "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt"
)


def download_wordlist(url: str, name: str, wordlist_dir: str) -> str:
    wordlist_path = os.path.join(wordlist_dir, name)

    if os.path.exists(wordlist_path):
        st.info(f"📂 `{name}` already exists.")
        return wordlist_path

    try:
        with st.spinner(f"⬇️ Starting download of `{name}`..."):
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()

            total_length = response.headers.get("content-length")
            total_length = int(total_length) if total_length else None

            downloaded = 0
            progress_bar = st.progress(0)
            progress_msg = st.empty()

            with open(wordlist_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
                        downloaded += len(chunk)
                        if total_length:
                            percent = int((downloaded / total_length) * 100)
                            progress_bar.progress(min(percent, 100))
                            progress_msg.info(f"📦 Downloading... {percent}%")

        st.success(f"✅ `{name}` downloaded successfully.")
        return wordlist_path

    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error downloading `{name}`: {e}")
        return None
