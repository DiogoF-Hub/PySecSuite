import streamlit as st
from Modules.forensic_analyzer.analyzer import analyze_file
from Modules.forensic_analyzer.checksum import verify_file_checksum
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
upload_dir = os.path.join(root_dir, "Uploads")


st.set_page_config(page_title="PySecSuite - Forensic Tools", layout="wide")

st.title("🔍 PySecSuite - Forensic Toolkit")

tabs = st.tabs(["📁 File Analyzer", "🔐 Checksum Verifier"])

# --- File Analyzer Tab ---
with tabs[0]:
    st.header("📁 Metadata & Forensic Analyzer")

    uploaded_file = st.file_uploader(
        "Upload a file (PDF, DOCX, JPG, etc.)",
        type=["pdf", "docx", "docm", "jpg", "jpeg", "png"],
    )

    if uploaded_file is not None:
        file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())
        st.success(f"File saved as: {uploaded_file.name}")

        with st.expander("🔎 Run Metadata Analysis"):
            if st.button("Analyze File"):
                st.text("Running analysis...\n")
                st.code(analyze_file(uploaded_file.name))

# --- Checksum Verifier Tab ---
with tabs[1]:
    st.header("🔐 Checksum Verifier")

    uploaded_checksum_file = st.file_uploader(
        "Upload file for checksum verification", key="checksum", type=None
    )

    hash_type = st.selectbox(
        "Select hash algorithm", ["md5", "sha1", "sha256", "sha512"]
    )
    expected_hash = st.text_input("Expected hash value")

    if uploaded_checksum_file and expected_hash:
        file_path = os.path.join(UPLOAD_DIR, uploaded_checksum_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_checksum_file.read())

        if st.button("Verify Checksum"):
            st.write("Verifying checksum...")
            st.code(verify_file_checksum(file_path, expected_hash, hash_type))
