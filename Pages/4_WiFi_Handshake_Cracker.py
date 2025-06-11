import os
import streamlit as st
from Modules.password_cracker.Utils.download import download_wordlist
from Modules.wifi_cracker.handshake_exctractor import (
    crack_notdoneyet,
    uploads_dir,
    wordlist_dir,
)

st.title("🔐 Wi-Fi Handshake Cracker")

with st.expander("ℹ️ What does this tool do?"):
    st.markdown(
        """
    Upload a captured WPA/WPA2 handshake (PCAP) file and crack it using a dictionary attack.
    """
    )

st.divider()

# --- PCAP Upload ---
st.subheader("📂 Upload Handshake PCAP")
uploaded_pcap = st.file_uploader(
    "Choose a .pcap or .pcapng file", type=["pcap", "pcapng"]
)
pcap_path = None
if uploaded_pcap:
    pcap_path = os.path.join(str(uploads_dir), uploaded_pcap.name)
    with open(pcap_path, "wb") as f:
        f.write(uploaded_pcap.getbuffer())

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

if wordlist_mode == "Select from existing wordlists":
    if not available_wordlists:
        st.warning("⚠️ No wordlists found in wordlist_dir.")
    else:
        choice = st.selectbox("Select a wordlist:", available_wordlists)
        selected_wordlist_path = os.path.join(str(wordlist_dir), choice)

elif wordlist_mode == "Use rockyou.txt (Quick Start)":
    rockyou_url = (
        "https://github.com/brannondorsey/naive-hashcat/"
        "releases/download/data/rockyou.txt"
    )
    rockyou_name = "rockyou.txt"
    selected_wordlist_path = download_wordlist(
        rockyou_url, rockyou_name, str(wordlist_dir)
    )

else:  # Download new
    st.markdown("### 📥 Download Custom Wordlist")
    custom_url = st.text_input("Enter direct download URL", key="wl_url")
    file_name = st.text_input("Save as (e.g., customlist.txt)", key="wl_name")
    if st.button("⬇️ Download Wordlist"):
        if custom_url and file_name:
            downloaded = download_wordlist(custom_url, file_name, str(wordlist_dir))
            if downloaded:
                selected_wordlist_path = downloaded
                st.success(f"Downloaded and selected `{file_name}`")
        else:
            st.warning("Please provide both URL and filename.")

st.divider()

# --- Crack Button ---
crack_disabled = not (
    pcap_path and selected_wordlist_path and os.path.exists(pcap_path)
)
if st.button("🚀 Crack Handshake", disabled=crack_disabled):
    with st.spinner("🔄 Cracking handshake…"):
        try:
            result = crack_notdoneyet(pcap_path, selected_wordlist_path)
            if result:
                st.success(f"✅ Password found: **{result}**")
            else:
                st.error("❌ No match found in wordlist.")
        except Exception as e:
            st.error(f"❌ Error during cracking: {e}")
