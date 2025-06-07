import streamlit as st
from Modules.forensic_analyzer.analyzer import analyze_file
from Modules.forensic_analyzer.checksum import verify_file_checksum
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
UPLOAD_DIR = os.path.join(root_dir, "Uploads")

st.set_page_config(page_title="PySecSuite - Forensic Tools", layout="wide")

st.title("🔍 PySecSuite - Forensic Toolkit")

tabs = st.tabs(["📁 File Analyzer", "🔐 Checksum Verifier"])

# --- File Analyzer Tab ---
with tabs[0]:
    st.header("📁 Metadata & Forensic Analyzer")

    uploaded_file = st.file_uploader(
        "Upload a file (PDF, DOCX, JPG, etc.)",
        type=[
            "pdf",
            "docx",
            "docm",
            "jpg",
            "jpeg",
            "png",
            "mp4",
            ".mkv",
            ".m4a",
            ".mp3",
            ".wav",
            ".flac",
            ".aac",
        ],
        key="analyzer",
    )

    if uploaded_file:
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        st.success(f"File saved as: {uploaded_file.name}")

    analyze_button_disabled = uploaded_file is None
    if st.button("Analyze File", disabled=analyze_button_disabled):
        st.markdown("---")
        st.write("Running analysis...")
        analysis_results = analyze_file(uploaded_file.name)

        if analysis_results:
            for line in analysis_results:
                if line.startswith("❌"):
                    st.error(line)
                elif line.startswith("⚠️") or line.startswith("❗"):
                    st.warning(line)
                elif line.startswith("✅") or line.startswith("✔️"):
                    st.success(line)
                elif line.startswith("🚨"):
                    st.warning(line)
                elif (
                    line.startswith("📎")
                    or line.startswith("📷")
                    or line.startswith("🗓️")
                    or line.startswith("📝")
                    or line.startswith("📄")
                    or line.startswith("🧾")
                    or line.startswith("📅")
                    or line.startswith("🕒")
                    or line.startswith("🕓")
                ):
                    st.markdown(f"> {line}")
                elif line.startswith("⏱️"):
                    st.info(line)
                elif line.startswith("**"):
                    st.markdown(line, unsafe_allow_html=True)
                elif line.startswith(" - "):
                    st.markdown(f"• {line[3:]}")
                else:
                    st.markdown(line)


# --- Checksum Verifier Tab ---
with tabs[1]:
    st.header("🔐 Checksum Verifier")

    uploaded_checksum_file = st.file_uploader(
        "Upload file for checksum verification", key="checksum"
    )

    hash_type = st.selectbox(
        "Select hash algorithm", ["md5", "sha1", "sha256", "sha512"]
    )
    expected_hash = st.text_input("Expected hash value")

    if uploaded_checksum_file:
        file_path = os.path.join(UPLOAD_DIR, uploaded_checksum_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_checksum_file.read())

    verify_button_disabled = not (uploaded_checksum_file and expected_hash.strip())
    if st.button("Verify Checksum", disabled=verify_button_disabled):
        st.markdown("---")
        st.write("Verifying checksum...")

        results = verify_file_checksum(file_path, expected_hash, hash_type)

        if results:
            for line in results:
                if line.startswith("❌"):
                    st.error(line)
                elif line.startswith("⚠️"):
                    st.warning(line)
                elif line.startswith("✅"):
                    st.success(line)
                elif line.startswith("**"):
                    st.markdown(line, unsafe_allow_html=True)
                elif line.startswith(" - "):
                    st.markdown(f"\u2022 {line[3:]}")
                else:
                    st.info(line)
