# PySecSuite
Python Cybersecurity Toolkit: Multi-purpose Security and Penetration Testing Suite

![Image](https://github.com/user-attachments/assets/1873d293-04d0-4e27-9019-f454d0aefc75)

This project is developed for educational purposes only.
# PySecSuite - Python Cybersecurity Toolkit

![PySecSuite](https://img.shields.io/badge/Python-3.x-blue.svg)
![Security](https://img.shields.io/badge/Security-PenTesting-red.svg)

## 🔥 Overview
**PySecSuite** is a modular, Python-based cybersecurity toolkit designed for security analysts and penetration testers. It integrates multiple cybersecurity functions into a single, easy-to-use framework for learning and practical security assessments.

---

## 📌 Table of Contents
- [Objective](#-objective)
- [Features](#-features)
- [Target Audience & Use Cases](#-target-audience--use-cases)
- [Ethical Considerations](#-ethical-considerations)
- [Modules](#-modules)
- [Tools & Libraries](#-tools--libraries)
- [Installation](#-installation)
- [Expected Outcome](#-expected-outcome)
- [License](#-license)
- [Contributors](#-contributors)

---

## 🎯 Objective
The primary goal of PySecSuite is to provide an extendable and practical cybersecurity toolkit for:
- **Network Scanning** & **Vulnerability Assessment**
- **Password Cracking**
- **Forensic Analysis**
- **Wi-Fi Security Auditing**
- **Open-Source Intelligence (OSINT) Investigations**

---

## ⚡ Features
✔️ **Network Scanner & Vulnerability Scanner**
✔️ **Password Cracker**
✔️ **Forensic File Analyzer**
✔️ **Wi-Fi Handshake Cracker**
✔️ **OSINT Toolkit**
✔️ **Modular and Extendable**
✔️ **Command-Line Interface (CLI) with Interactive Output**

---

## 🎯 Target Audience & Use Cases
This toolkit is designed for:
- **Cybersecurity students** seeking hands-on learning.
- **Ethical hackers** conducting penetration testing.
- **System administrators** auditing their networks for vulnerabilities.

---

## ⚠️ Ethical Considerations
This project is **strictly for educational and ethical use**. The developers do **not** condone illegal activities. All tests should be conducted in controlled environments **with explicit permission**. A disclaimer is included to prevent misuse.

---

## 🛠 Modules
### 🔹 Network Scanner & Vulnerability Scanner
- Scans for **active hosts & open ports**
- Identifies **running services & versions**
- Fetches **known vulnerabilities (CVEs)** from NIST NVD API

### 🔹 Password Cracker
- **Brute-force hash guessing** (Supports various algorithms)
- Dictionary attacks using common password lists

### 🔹 Forensic File Analyzer
- Extracts **metadata from suspicious files**
- Detects **timestamp inconsistencies & embedded objects**
- Verifies file integrity using **SHA256 checksum**

### 🔹 Wi-Fi Handshake Cracker
- Cracks **WPA/WPA2 passwords** using external PCAP files
- Supports **Hashcat & wordlists** for password cracking

### 🔹 OSINT Toolkit
- **Social Media Profile Lookups**
- **Domain & IP Information Retrieval**
- **Geolocation & ISP Data Fetching**

---

## 🔧 Tools & Libraries
- **Networking & Scanning**: `socket`, `scapy`
- **Web Scraping & OSINT**: `requests`, `BeautifulSoup`
- **Password Cracking**: `hashlib`, `itertools`, `tqdm`
- **Forensic Analysis**: `pyexiftool`, `pymediainfo`
- **Wi-Fi Auditing**: `PyWiFi`, `Hashcat`
- **Vulnerability Fetching**: `NVD API`, `JSON`
- **CLI & UX**: `Rich`, `Argparse`

---

## 🚀 Installation
```sh
# Clone the repository
git clone https://github.com/yourusername/PySecSuite.git
cd PySecSuite

# Install dependencies
pip install -r requirements.txt

# Run the toolkit
python pysecsuite.py
```

---

## 🎯 Expected Outcome
By the end of the project, we aim to deliver:
- ✅ A **fully functional** Python Cybersecurity Toolkit.
- ✅ A **well-documented** Python codebase following security best practices.
- ✅ A **user guide/README** detailing installation, usage, and limitations.
- ✅ A **final presentation** covering objectives, demonstrations, and challenges faced.

This toolkit will serve as an **educational and practical resource** for cybersecurity professionals and enthusiasts.

---

## 📜 License
This project is licensed under the [MIT License](LICENSE). You are free to use, modify, and distribute this software under the terms of the license.

---

## 👨‍💻 Contributors
- **Liam Wolff** – [wolli689@school.lu](mailto:wolli689@school.lu)
- **Diogo Carvalho Fernandes** – [cardi782@school.lu](mailto:cardi782@school.lu)
- **Rodrigo Marques Sá** – [marro411@school.lu](mailto:marro411@school.lu)

---

🚀 **Let's secure the digital world, one scan at a time!** 🔐

