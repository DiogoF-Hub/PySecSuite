# network_scanner_page.py

import streamlit as st
import ipaddress
import os
import sys
import glob
import subprocess
import pandas as pd
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURE THE PAGE (optional, since main app may override)
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Network Scanner", layout="wide")

# ──────────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────────
st.title("🕵️‍♂️ PySecSuit Network Scanner (CLI‐style)")
st.markdown(
    """
This page runs your existing `scanner.py` exactly as if you typed on the command line:




After it finishes, all generated CSVs (including `alive_hosts.csv` and each `<host>_ports.csv`) will be displayed as tables with Download buttons.
"""
)

# ──────────────────────────────────────────────────────────────────────────────
# DETERMINE PROJECT ROOT AND SCANNER.PY PATH
# ──────────────────────────────────────────────────────────────────────────────
# If this file lives under Pages/, then project_root is one level up:
PAGE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PAGE_DIR.parent  # assumes Pages/ is directly under the project root
SCANNER_PATH = PROJECT_ROOT / "Modules" / "scanner" / "scanner.py"

if not SCANNER_PATH.is_file():
    st.error(
        f"❌ Could not find `scanner.py` at:\n\n  {SCANNER_PATH}\n\n"
        "Please confirm your folder structure. For example:\n\n"
        "project_root/\n"
        "├─ Pages/\n"
        "│  └─ network_scanner_page.py  ← this file\n"
        "└─ Modules/\n"
        "   └─ scanner/\n"
        "      └─ scanner.py\n"
    )
    st.stop()

# ──────────────────────────────────────────────────────────────────────────────
# STREAMLIT FORM FOR USER INPUT
# ──────────────────────────────────────────────────────────────────────────────
with st.form("cli_form"):
    col1, col2 = st.columns([2, 1])
    with col1:
        target_input = st.text_input(
            "Target (single IP or CIDR, e.g. 192.168.1.5 or 192.168.1.0/24)",
            value="192.168.1.0/24",
            help="Enter a single IP (e.g. 192.168.1.5) or a CIDR subnet (e.g. 192.168.1.0/24).",
        )
    with col2:
        port_input = st.text_input(
            "Port, port‐range (e.g. 20-100), or `all`",
            value="80",
            help="Enter a single port (e.g. 22), a range (e.g. 20-100), or `all` (scans 0–65535).",
        )

    threads = st.number_input(
        "Number of threads (1–1000)",
        min_value=1,
        max_value=1000,
        value=100,
        help="Threads for discovery & scanning.",
    )

    run_cli = st.form_submit_button("🚀 Run scanner.py")

if run_cli:
    st.markdown("---")

    # ──────────────────────────────────────────────────────────────────────────
    # VALIDATE TARGET (single IP or CIDR)
    # ──────────────────────────────────────────────────────────────────────────
    try:
        ipaddress.ip_network(target_input, strict=False)
    except Exception as e:
        st.error(f"⚠️ Invalid target '{target_input}': {e}")
        st.stop()

    # ──────────────────────────────────────────────────────────────────────────
    # DETERMINE PORT ARGUMENT
    # ──────────────────────────────────────────────────────────────────────────
    pi = port_input.strip().lower()
    if pi == "all":
        port_arg = ["-a"]
    else:
        port_arg = [pi]  # let the CLI handle format validation

    # ──────────────────────────────────────────────────────────────────────────
    # BUILD THE SUBPROCESS COMMAND
    # ──────────────────────────────────────────────────────────────────────────
    cmd = (
        [
            sys.executable,
            str(SCANNER_PATH),
            target_input,
        ]
        + port_arg
        + ["-t", str(int(threads))]
    )

    # ──────────────────────────────────────────────────────────────────────────
    # RUN scanner.py AS A SUBPROCESS (no terminal output shown directly)
    # ──────────────────────────────────────────────────────────────────────────
    with st.spinner("Running scanner.py... this may take a while"):
        try:
            proc = subprocess.run(
                cmd, cwd=str(PROJECT_ROOT), capture_output=True, text=True, timeout=3600
            )
        except subprocess.TimeoutExpired:
            st.error("❌ scanner.py timed out after 3600 seconds.")
            st.stop()
        except Exception as e:
            st.error(f"❌ Failed to run scanner.py: {e}")
            st.stop()

    if proc.returncode != 0:
        st.warning(
            "⚠️ scanner.py finished with errors. You can still view any CSVs that were created."
        )
    else:
        st.success("✅ scanner.py finished without errors.")

    # ──────────────────────────────────────────────────────────────────────────
    # DISPLAY ONLY THE <IP>_ports.csv FILES
    # ──────────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📄 Scan Results (`<IP>_ports.csv`)")

    results_folder = PROJECT_ROOT / "Modules" / "scanner" / "results"
    if not results_folder.exists():
        st.info(
            "No `Modules/scanner/results/` folder found. (scanner.py may not have created it.)"
        )
        st.stop()

    # Only select files named "*_ports.csv"
    csv_paths = sorted(results_folder.glob("*_ports.csv"))
    if not csv_paths:
        st.info("No `<IP>_ports.csv` files found under `Modules/scanner/results/`.")
        st.stop()

    for csv_file in csv_paths:
        filename = csv_file.name
        st.markdown(f"#### {filename}")

        try:
            df = pd.read_csv(csv_file)
            st.dataframe(df, use_container_width=True)
        except Exception as e:
            st.error(f"Could not read `{filename}`: {e}")
            continue

        with open(csv_file, "rb") as f:
            data_bytes = f.read()
        st.download_button(
            label=f"Download {filename}",
            data=data_bytes,
            file_name=filename,
            mime="text/csv",
        )

        st.markdown("")  # spacer
