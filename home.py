import streamlit as st

st.set_page_config(page_title="PySecSuite - Home", layout="centered")

st.title("🛡️ Welcome to PySecSuite")
st.subheader("Your all-in-one Python Cybersecurity Toolkit")

st.markdown("---")

st.markdown("### 🔧 What is PySecSuite?")
st.write(
    """
    PySecSuite is a modular Python-based toolkit built for security testing, forensic analysis, and 
    educational purposes in cybersecurity.

    This suite brings together several tools into a unified interface, making it easy for users to:
    - Inspect networks
    - Test password strength
    - Analyze files for metadata or tampering
    - Explore public information using OSINT
    - Crack Wi-Fi handshakes
    """
)

st.markdown("### 🚀 Getting Started")
st.write(
    "Use the sidebar to navigate between tools. Each module has its own page with a specific purpose."
)

st.markdown("### 🧪 Included Tools")
st.markdown(
    """
    - 🔍 Network & Vulnerability Scanner  
    - 🔐 Password Cracker  
    - 📁 Forensic File Analyzer  
    - 📡 Wi-Fi Handshake Cracker  
    - 🌐 OSINT Toolkit  
    """
)

st.markdown("---")
st.info(
    "Visit the **About** page for author info, objectives, ethical use, and technical details."
)
