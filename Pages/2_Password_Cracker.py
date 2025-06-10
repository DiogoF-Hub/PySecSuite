# password_cracker.py (inside /pages)
import streamlit as st
import os
from Modules.password_cracker.hash_cracker import (
    multi_crack_hashes_streamed,
    crack_single_hash,
    wordlist_dir,
    wordlist_file,
    uploads_dir,
    hashes_file as default_hashes_file,
)
from Modules.password_cracker.Utils.download import download_wordlist

st.set_page_config(page_title="Password Cracker", layout="centered")

st.title("🔓 Password Cracker")
st.markdown("Crack hashed passwords using a dictionary attack.")

st.info(
    """
**Supported Hash Types and Lengths:**
- **MD5** → 32 hex characters
- **SHA1** → 40 hex characters
- **SHA256** → 64 hex characters
- **SHA512** → 128 hex characters  
❌ BCRYPT and ARGON2 are **not supported** (please use Hashcat).
"""
)

st.divider()

# --- Wordlist Selection ---
st.subheader("📚 Wordlist Selection")

available_wordlists = [f for f in os.listdir(wordlist_dir) if f.endswith(".txt")]

wordlist_mode = st.radio(
    "Choose how to load the wordlist:",
    [
        "Select from existing wordlists",
        "Use rockyou.txt (Quick Start)",
        "Download a new wordlist from URL",
    ],
    index=0,
)

selected_wordlist_path = None

# Option 1: Existing wordlists
if wordlist_mode == "Select from existing wordlists":
    if not available_wordlists:
        st.warning("⚠️ No wordlists found in the folder.")
    else:
        selected_wordlist = st.selectbox(
            "Select a wordlist from folder:", available_wordlists
        )
        selected_wordlist_path = os.path.join(wordlist_dir, selected_wordlist)

# Option 2: Use rockyou.txt directly
elif wordlist_mode == "Use rockyou.txt (Quick Start)":
    rockyou_url = "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt"
    rockyou_name = "rockyou.txt"
    selected_wordlist_path = download_wordlist(rockyou_url, rockyou_name, wordlist_dir)

# Option 3: Download new from custom URL
elif wordlist_mode == "Download a new wordlist from URL":
    st.markdown("### 📅 Download Wordlist")
    custom_url = st.text_input("Enter direct download URL")
    file_name_input = st.text_input("Save as (e.g., `customlist.txt`)")

    if st.button("⬇️ Download Wordlist"):
        if custom_url and file_name_input:
            downloaded_path = download_wordlist(
                custom_url, file_name_input, wordlist_dir
            )
            if downloaded_path:
                selected_wordlist_path = downloaded_path
                st.info(f"Selected the wordlist to proceed: `{file_name_input}`")
        else:
            st.warning("Please provide both a URL and a filename.")

st.divider()

# --- Cracking Mode ---
st.subheader("🔍 Cracking Mode")

mode = st.radio(
    "Select cracking mode",
    ["Crack a single hash", "Crack all hashes in a file"],
    index=0,
)

if mode == "Crack all hashes in a file":
    save_results = st.toggle("📎 Save cracked results to file", value=True)
else:
    save_results = False

st.divider()

# --- Cracking Logic ---
if mode == "Crack a single hash":
    single_hash_input = st.text_input("Enter a hash to crack")

    crack_single_disabled = not (single_hash_input.strip() and selected_wordlist_path)
    if st.button("🚀 Crack Single Hash", disabled=crack_single_disabled):
        with st.spinner("🔄 Cracking in progress..."):
            result = crack_single_hash(
                single_hash_input.strip(), selected_wordlist_path
            )

        if result:
            st.success(f"✅ Match found: **{result}**")
        else:
            st.warning("❌ No match found.")

else:
    uploaded_hashes = st.file_uploader("Upload a hashes.txt file", type=["txt"])
    selected_hash_path = default_hashes_file

    if uploaded_hashes:
        selected_hash_path = os.path.join(uploads_dir, uploaded_hashes.name)
        with open(selected_hash_path, "wb") as f:
            f.write(uploaded_hashes.read())

    crack_multi_disabled = not selected_wordlist_path or not os.path.exists(
        selected_hash_path
    )

    if st.button("🚀 Crack All Hashes", disabled=crack_multi_disabled):
        with st.spinner("🔄 Cracking multiple hashes..."):
            try:
                result = multi_crack_hashes_streamed(
                    selected_wordlist_path, selected_hash_path, save_results
                )
                if save_results:
                    st.success(f"✅ Cracking completed! Results saved to `{result}`")
                    with st.expander("📄 View and Download Cracked Results"):
                        with open(result, "r", encoding="utf-8") as f:
                            content = f.read()
                            st.code(content, language="text")
                            st.download_button(
                                label="⬇️ Download Results",
                                data=content,
                                file_name=os.path.basename(result),
                                mime="text/plain",
                            )
                else:
                    st.success("✅ Cracking completed! Check the terminal output.")
            except Exception as e:
                st.error(f"❌ Error during cracking: {e}")
