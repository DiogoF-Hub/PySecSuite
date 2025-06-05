import streamlit as st

st.set_page_config(page_title="About - PySecSuite", layout="centered")

st.title("📖 About PySecSuite")
st.markdown("---")

st.markdown("### 📌 Project Title")
st.write(
    "**Python Cybersecurity Toolkit: Multi-purpose Security and Penetration Testing Suite**"
)

st.markdown("### 🎯 Objective")
st.write(
    """
    The goal of PySecSuite is to create a modular, Python-based cybersecurity toolkit designed for:
    - Learning cybersecurity concepts  
    - Practicing ethical hacking techniques  
    - Performing security assessments in authorized environments  

    It combines multiple tools into a single, easy-to-use application with real-world functionality.
    """
)

st.markdown("### 👥 Target Audience")
st.write(
    """
    - 🧑‍🎓 Cybersecurity students  
    - 🧑‍💻 Ethical hackers  
    - 👨‍🔧 System administrators  
    - 🧠 Anyone interested in cybersecurity tooling  
    """
)

st.markdown("### ⚖️ Ethical Considerations")
st.warning(
    """
    This toolkit is developed **strictly for educational use**.  
    All operations must be carried out in **controlled environments** with **explicit authorization**.

    PySecSuite will display warnings and disclaimers inside each tool to prevent misuse.
    """
)

st.markdown("### 🧱 Modules Overview")
st.markdown(
    """
    - 🔍 **Network & Vulnerability Scanner**: Scans networks, finds open ports & known vulnerabilities  
    - 🔐 **Password Cracker**: Brute-forces hashed passwords or login forms  
    - 📁 **Forensic File Analyzer**: Extracts and compares metadata for tampering detection  
    - 📡 **Wi-Fi Handshake Cracker**: Cracks WPA/WPA2 passwords using PCAP and wordlists  
    - 🌐 **OSINT Toolkit**: Investigates domains, IPs, and public profiles  
    """
)

st.markdown("### 🛠️ Technologies Used")
st.write(
    """
    - Python (core)
    - Streamlit (interface)
    - Scapy, socket (network scanning)
    - Hashlib, itertools (password brute-force)
    - ExifTool, filetype (forensics)
    - Requests, BeautifulSoup (OSINT)
    - Hashcat (Wi-Fi cracking)
    """
)

st.markdown("### 👨‍💻 Authors")
st.markdown(
    """
    - **Liam Wolff** — [wolli689@school.lu](mailto:wolli689@school.lu)  
    - **Diogo Carvalho Fernandes** — [cardi782@school.lu](mailto:cardi782@school.lu)  
    - **Rodrigo Marques Sá** — [marro411@school.lu](mailto:marro411@school.lu)  
    """
)

st.markdown("---")
st.success("Thank you for using PySecSuite!")
