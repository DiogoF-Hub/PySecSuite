# integratting the banner grabbe in here to make it simpler to handle
import socket
import csv
import os
from concurrent.futures import ThreadPoolExecutor

import argparse

BANNER = r"""
8888888b.            .d8888b.                    .d8888b.           d8b 888    
888   Y88b          d88P  Y88b                  d88P  Y88b          Y8P 888    
888    888          Y88b.                       Y88b.                   888    
888   d88P 888  888  "Y888b.    .d88b.   .d8888b "Y888b.   888  888 888 888888 
8888888P"  888  888     "Y88b. d8P  Y8b d88P"       "Y88b. 888  888 888 888    
888        888  888       "888 88888888 888           "888 888  888 888 888    
888        Y88b 888 Y88b  d88P Y8b.     Y88b.   Y88b  d88P Y88b 888 888 Y88b.  
888         "Y88888  "Y8888P"   "Y8888   "Y8888P "Y8888P"   "Y88888 888  "Y888 
                888
           Y8b d88P
            "Y88P"
"""


def scan_port(ip, port, timeout=1.0):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            return port, (result == 0)
    except Exception:
        return port, False


def grab_banner(ip, port, timeout=2.0):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((ip, port))
            banner = s.recv(1024)
            return banner.decode(errors="ignore").strip()
    except:
        return ""


def export_to_csv(
    results, ip, filename="Modules/scanner/results/port_scan_results.csv"
):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["IP Address", "Port", "Status", "Banner"])
        for port, is_open, banner in results:
            writer.writerow([ip, port, "Open" if is_open else "Closed", banner])


def parse_port_range(port_range):
    try:
        if "-" in port_range:
            start, end = map(int, port_range.split("-"))
            if start > end or start < 0 or end > 65535:
                raise ValueError
            return list(range(start, end + 1))
        else:
            port = int(port_range)
            if port < 0 or port > 65535:
                raise ValueError
            return [port]
    except ValueError:
        print(
            "[!] Invalid port or port range. Use a number (0–65535) or a range like 0-1024."
        )
        exit(1)


if __name__ == "__main__":
    print(BANNER)
    import argparse

    parser = argparse.ArgumentParser(
        description="Threaded port scanner with banner grabbing"
    )
    parser.add_argument("ip", help="Target IP address")
    parser.add_argument(
        "-a", "--all", action="store_true", help="Scan all ports from 0 to 65535"
    )
    parser.add_argument(
        "ports", nargs="?", help="Port or port range (e.g. 80 or 0-1024)"
    )
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=100,
        help="Number of threads to use (default: 100)",
    )
    args = parser.parse_args()

    ip = args.ip

    # Only call parse_port_range when args.ports is not None
    if args.all:
        ports = list(range(0, 65536))
        print("[+] Scanning all ports from 0 to 65535...")
    elif args.ports:
        ports = parse_port_range(args.ports)
    else:
        print("[!] You must provide either a port/range or use -a to scan all ports.")
        exit(1)

    print("")  # Blank line for readability
    print(
        f"[+] Scanning {ip} ports {ports[0]} to {ports[-1]} using {args.threads} threads..."
    )
    results = []

    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = [executor.submit(scan_port, ip, port) for port in ports]
            for future in futures:
                port, is_open = future.result()
                banner = grab_banner(ip, port) if is_open else ""
                if is_open:
                    print(f"Port {port}: OPEN - {banner}")
                results.append((port, is_open, banner))
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user.")
        exit(1)

    export_to_csv(results, ip)
    print("")  # Blank line for readability
    print("[+] Scan complete.")
