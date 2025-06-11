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
from Modules.password_cracker.password_sprayer import run_bruteforce
from Modules.password_cracker.Utils.download import download_wordlist

st.set_page_config(page_title="Password Cracker", layout="centered")

st.title("🔓 Password Cracker")

tab1, tab2 = st.tabs(["🧠 Hash Cracker", "💨 Password Sprayer"])
with tab1:
    st.markdown("Crack hashed passwords using a dictionary attack.")

    with st.expander("ℹ️ What does this tool do?"):
        st.markdown(
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
        selected_wordlist_path = download_wordlist(
            rockyou_url, rockyou_name, wordlist_dir
        )

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

        crack_single_disabled = not (
            single_hash_input.strip() and selected_wordlist_path
        )
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
                        st.success(
                            f"✅ Cracking completed! Results saved to `{result}`"
                        )
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

with tab2:
    st.markdown(
        "Try a list of passwords against a login form using a single known username."
    )

    with st.expander("ℹ️ What does this tool do?"):
        st.markdown(
            """
            ⚠️ **Educational Use Only!** This tool is designed for use in test environments you own or have permission to test.

            **What It Does:**
            - Attempts multiple passwords for a known username.
            - Detects success by searching for a keyword in the response (e.g. "dashboard").

            ❗ Too many rapid attempts may lock accounts or trigger rate-limiting.
            """
        )

    st.divider()

    # --- Target Setup ---
    st.subheader("🔗 Target Setup")
    login_url = st.text_input(
        "🔐 Login URL", placeholder="https://example.com/login", key="sprayer_login_url"
    )
    username = st.text_input("👤 Username", placeholder="admin", key="sprayer_username")

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
        key="sprayer_wordlist_mode",
    )

    selected_wordlist_path = None

    # Option 1: Existing wordlists
    if wordlist_mode == "Select from existing wordlists":
        if not available_wordlists:
            st.warning("⚠️ No wordlists found in the folder.")
        else:
            selected_wordlist = st.selectbox(
                "Select a wordlist from folder:",
                available_wordlists,
                key="sprayer_wordlist_select",
            )
            selected_wordlist_path = os.path.join(wordlist_dir, selected_wordlist)

    # Option 2: Use rockyou.txt directly
    elif wordlist_mode == "Use rockyou.txt (Quick Start)":
        rockyou_url = "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt"
        rockyou_name = "rockyou.txt"
        selected_wordlist_path = download_wordlist(
            rockyou_url, rockyou_name, wordlist_dir
        )

    # Option 3: Download new from custom URL
    elif wordlist_mode == "Download a new wordlist from URL":
        st.markdown("### 📅 Download Wordlist")
        custom_url = st.text_input(
            "Enter direct download URL", key="sprayer_custom_url"
        )
        file_name_input = st.text_input(
            "Save as (e.g., `customlist.txt`)", key="sprayer_custom_filename"
        )

        if st.button("⬇️ Download Wordlist", key="sprayer_download_button"):
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

    # --- Options ---
    st.subheader("⚙️ Spraying Options")
    with st.expander("🛠️ Advanced Settings", expanded=False):
        enable_field_override = st.checkbox(
            "Override form field names (username/password)",
            key="sprayer_override_checkbox",
        )
        user_field_override = ""
        pass_field_override = ""
        if enable_field_override:
            user_field_override = st.text_input(
                "🔤 Username Field Override",
                placeholder="e.g. login_user",
                key="sprayer_user_field",
            )
            pass_field_override = st.text_input(
                "🔒 Password Field Override",
                placeholder="e.g. login_pass",
                key="sprayer_pass_field",
            )

        success_keyword = st.text_input(
            "✅ Success Keyword", value="dashboard", key="sprayer_success_keyword"
        )
        delay = st.slider(
            "⏱️ Delay between attempts (seconds)", 0, 5, 0, key="sprayer_delay"
        )

    st.divider()

    # --- Execution ---
    ready_to_run = all([login_url.strip(), username.strip(), selected_wordlist_path])
    run_button_disabled = not ready_to_run

    progress_bar = st.empty()
    result_output = st.empty()

    if st.button(
        "🚀 Start Spraying", disabled=run_button_disabled, key="sprayer_run_button"
    ):

        def update_progress(percent):
            progress_bar.progress(percent)

        with st.spinner("🔄 Running password sprayer..."):
            result = run_bruteforce(
                login_url=login_url,
                username=username,
                wordlist_path=selected_wordlist_path,
                update_progress=update_progress,
                user_field_override=(
                    user_field_override if enable_field_override else None
                ),
                pass_field_override=(
                    pass_field_override if enable_field_override else None
                ),
                success_keyword=success_keyword,
                delay=delay,
            )

        result_output.markdown(f"**Result:** {result}")
