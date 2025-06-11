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
st.title("🕵️‍♂️ PySecSuit Network Scanner")

# ──────────────────────────────────────────────────────────────────────────────
# CHOOSE SCAN MODE (outside the form so dynamic fields show immediately)
# ──────────────────────────────────────────────────────────────────────────────
scan_type = st.radio(
    "Scan Mode:",
    options=["Single IP/CIDR", "IP Range"],
    index=0,
    help="Choose whether to scan a single IP/CIDR or specify a start/end IP range.",
)

# ──────────────────────────────────────────────────────────────────────────────
# STREAMLIT FORM FOR USER INPUT
# ──────────────────────────────────────────────────────────────────────────────
with st.form("cli_form"):
    if scan_type == "IP Range":
        col1, col2 = st.columns(2)
        with col1:
            start_ip_input = st.text_input(
                "Start IP",
                value="45.33.32.156",
                help="Beginning of the IP range (IPv4).",
            )
        with col2:
            end_ip_input = st.text_input(
                "End IP",
                value="45.33.32.156",
                help="End of the IP range (IPv4). Must be ≥ Start IP.",
            )
        target_input = None
    else:
        target_input = st.text_input(
            "Target (single IP or CIDR, e.g. 45.33.32.156  or 45.33.32.156/32)",
            value="45.33.32.156/32",
            help="Enter a single IP or a CIDR range.",
        )
        start_ip_input = end_ip_input = None

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
    # CLEAR OUT EXISTING CSVs IN results_folder BEFORE STARTING
    # ──────────────────────────────────────────────────────────────────────────
    results_folder = Path("Modules/scanner/results")

    if results_folder.exists():
        for file_path in results_folder.glob("*"):
            try:
                file_path.unlink()
            except Exception:
                pass
    else:
        results_folder.mkdir(parents=True, exist_ok=True)

    # ──────────────────────────────────────────────────────────────────────────
    # BUILD targets_to_scan: one element (CIDR/IP) or list of IPs from [start, end]
    # ──────────────────────────────────────────────────────────────────────────
    targets_to_scan = []

    if scan_type == "IP Range":
        start_raw = start_ip_input.strip()
        end_raw = end_ip_input.strip()
        # Validate start IP
        try:
            start_addr = ipaddress.IPv4Address(start_raw)
        except Exception:
            st.error(f"⚠️ Start IP '{start_raw}' is not a valid IPv4 address.")
            st.stop()
        # Validate end IP
        try:
            end_addr = ipaddress.IPv4Address(end_raw)
        except Exception:
            st.error(f"⚠️ End IP '{end_raw}' is not a valid IPv4 address.")
            st.stop()

        if int(end_addr) < int(start_addr):
            st.error("⚠️ End IP must be greater than or equal to Start IP.")
            st.stop()

        # Build list from start → end inclusive
        for ip_int in range(int(start_addr), int(end_addr) + 1):
            targets_to_scan.append(str(ipaddress.IPv4Address(ip_int)))
    else:
        tgt = target_input.strip()
        if "/" in tgt:
            # Validate CIDR
            try:
                _ = ipaddress.ip_network(tgt, strict=False)
                targets_to_scan = [tgt]
            except Exception as e:
                st.error(f"⚠️ '{tgt}' is not a valid CIDR: {e}")
                st.stop()
        else:
            # Validate single IP
            try:
                _ = ipaddress.ip_address(tgt)
                targets_to_scan = [tgt]
            except Exception as e:
                st.error(f"⚠️ '{tgt}' is not a valid IP address: {e}")
                st.stop()

    # ──────────────────────────────────────────────────────────────────────────
    # DETERMINE PORT ARGUMENT
    # ──────────────────────────────────────────────────────────────────────────
    pi = port_input.strip().lower()
    if pi == "all":
        port_arg = ["-a"]
    else:
        port_arg = [pi]  # let scanner.py validate format

    # ──────────────────────────────────────────────────────────────────────────
    # RUN scanner.py FOR EACH TARGET
    # ──────────────────────────────────────────────────────────────────────────
    SCANNER_PATH = Path("Modules/scanner/scanner.py")
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    any_error = False
    for tgt in targets_to_scan:
        cmd = (
            [
                sys.executable,
                str(SCANNER_PATH),
                tgt,
            ]
            + port_arg
            + ["-t", str(int(threads))]
        )

        with st.spinner(f"Running scanner.py on {tgt}…"):
            try:
                proc = subprocess.run(
                    cmd,
                    cwd=str(PROJECT_ROOT),
                    capture_output=True,
                    text=True,
                    timeout=3600,
                )
            except subprocess.TimeoutExpired:
                st.error(f"❌ scanner.py timed out on {tgt}.")
                any_error = True
                continue
            except Exception as e:
                st.error(f"❌ Failed to run scanner.py on {tgt}: {e}")
                any_error = True
                continue

        if proc.returncode != 0:
            st.warning(f"⚠️ scanner.py exited with code {proc.returncode} on {tgt}.")
            any_error = True
        else:
            st.success(f"✅ scanner.py finished without errors on {tgt}.")

    if any_error:
        st.info(
            "Some targets returned errors. Check the `<IP>_ports.csv` files below for partial results."
        )
    else:
        st.success("All scans completed successfully.")

    # ──────────────────────────────────────────────────────────────────────────
    # DISPLAY ONLY THE <IP>_ports.csv FILES
    # ──────────────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📄 Scan Results (`<IP>_ports.csv`)")

    if not results_folder.exists():
        st.info(
            "No `Modules/scanner/results/` folder found. (scanner.py may not have created it.)"
        )
        st.stop()

    # Glob only files ending in “_ports.csv”
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
