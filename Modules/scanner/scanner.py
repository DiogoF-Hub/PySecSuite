import subprocess
import platform
import ipaddress
import socket
import csv
import os
import argparse
import re
from concurrent.futures import ThreadPoolExecutor


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


def ping_host_with_ttl(ip):
    """
    Ping a host and attempt to extract its TTL value.
    Returns a tuple (ip, ttl) if the host responds, else None.
    Helps in basic OS fingerprinting based on TTL.

    """

    system = platform.system().lower()

    if system == "windows":

        cmd = ["ping", "-n", "1", str(ip)]

    else:

        cmd = ["ping", "-c", "1", "-W", "1", str(ip)]

    try:

        proc = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True
        )

        out = proc.stdout

        if proc.returncode != 0:

            return None

        for line in out.splitlines():

            line_lower = line.lower()

            if "ttl=" in line_lower:

                try:

                    ttl_str = line_lower.split("ttl=")[1].split()[0]

                    ttl_val = int(ttl_str)

                    return str(ip), ttl_val

                except Exception:

                    continue

        return str(ip), None

    except Exception:

        return None


def guess_os_from_ttl(ttl):
    """
    Infers the operating system based on the TTL value.
    Typical defaults: Windows=128, Linux=64, Cisco=255.

    """

    if ttl is None:

        return "Unknown"

    if ttl >= 250:

        return "Cisco/BSD?"

    if ttl >= 120:

        return "Windows"

    if ttl >= 50:

        return "Linux/Unix"

    return "Unknown"


def discover_hosts(target, max_threads=100):
    """
    Performs host discovery.
    Accepts single IP or CIDR subnet. Uses threading to speed up discovery.
    Returns list of (ip, ttl, guessed_os).

    """

    if "/" in target:

        try:

            network = ipaddress.ip_network(target, strict=False)

        except ValueError:

            print(f"[!] '{target}' is not valid CIDR.")

            exit(1)

        candidates = [str(h) for h in network.hosts()]

    else:

        try:

            ipaddress.ip_address(target)

            candidates = [target]

        except ValueError:

            print(f"[!] '{target}' is not a valid IP or subnet.")

            exit(1)

    alive_list = []

    with ThreadPoolExecutor(max_workers=max_threads) as executor:

        for result in executor.map(ping_host_with_ttl, candidates):

            if result:

                ip, ttl = result

                os_guess = guess_os_from_ttl(ttl)

                alive_list.append((ip, ttl, os_guess))

    return alive_list


def parse_port_range(port_range):
    """
    Parses a single port or range string (e.g., "22" or "20-80").
    Returns list of integers.

    """

    try:

        if "-" in port_range:

            start, end = map(int, port_range.split("-", 1))

            if start > end or start < 0 or end > 65535:

                raise ValueError

            return list(range(start, end + 1))

        else:

            p = int(port_range)

            if p < 0 or p > 65535:

                raise ValueError

            return [p]

    except Exception:

        print("[!] Invalid port or port range. Use 065535 or a range like 20-100.")

        exit(1)


def scan_port(ip, port, timeout=1.0):
    """

    Attempt TCP connect to (ip, port). Return (port, True) if open, else (port, False).

    """

    try:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.settimeout(timeout)

            res = s.connect_ex((ip, port))

            return port, (res == 0)

    except Exception:

        return port, False


def grab_banner(ip, port, timeout=2.0):
    """
    Retrieves the banner from an open TCP port (if available).
    Returns decoded string.

    """

    try:

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

            s.settimeout(timeout)

            s.connect((ip, port))

            data = s.recv(1024)

            return data.decode(errors="ignore").strip()

    except Exception:

        return ""


def parse_service_version(banner):
    """
    Attempts to extract (product, version) from a banner string.
    Supports formats like 'OpenSSH_8.4p1' or 'Apache/2.4.41'.

    """

    match = re.search(r"([A-Za-z0-9\-]+)[_/]([0-9]+(?:\.[0-9A-Za-z]+)*)", banner)

    if not match:

        return None, None

    return match.group(1), match.group(2)


def lookup_cves_circl(product, version):
    """
    Queries CIRCL CVE database to find vulnerabilities for the given product/version.
    Returns list of (cve_id, summary).

    """

    if not product or not version:

        return []

    url = f"https://cve.circl.lu/api/search/{product}"

    try:

        resp = requests.get(url, timeout=5)

        resp.raise_for_status()

    except Exception:

        return []

    data = resp.json()

    results = []

    for entry in data:

        cve_id = entry.get("id", "")

        summary = entry.get("summary", "") or ""

        cpes = entry.get("vulnerable_configuration", []) or []

        if version in summary or any(version in c for c in cpes):

            results.append((cve_id, summary))

    return results


def export_to_csv(results, host_ip, host_ttl, host_os, filename):
    """
    Append only open-port results to CSV. If new, write header first.
    Each row: IP, TTL, OS_Guess, Port, Status, Banner, Product, Version, CVEs

    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    file_exists = os.path.isfile(filename)

    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(
                [
                    "IP Address",
                    "TTL",
                    "OS Guess",
                    "Port",
                    "Status",
                    "Banner",
                    "Product",
                    "Version",
                    "CVE(s)",
                ]
            )

        for port, is_open, banner, product, version, cves in results:
            # Only write rows for open ports
            if not is_open:
                continue

            cve_cell = ""
            if cves:
                cve_cell = " | ".join(f"{cid}: {summ}" for cid, summ in cves)

            writer.writerow(
                [
                    host_ip,
                    host_ttl if host_ttl is not None else "",
                    host_os,
                    port,
                    "Open",
                    banner,
                    product or "",
                    version or "",
                    cve_cell,
                ]
            )


def main():

    print(BANNER)

    parser = argparse.ArgumentParser(
        description="PySecSuit  Network Scanner: TTL OS Fingerprint + Banner + CVE Lookup"
    )

    parser.add_argument(
        "target",
        help="Either a single IP (e.g. 192.168.1.5) or a CIDR subnet (e.g. 192.168.1.0/24)",
    )

    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Scan all ports from 0 to 65535 on each host",
    )

    parser.add_argument(
        "ports",
        nargs="?",
        help="Port or port range (e.g. 80 or 20-100). Omit if using -a",
    )

    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=100,
        help="Threads for discovery & scanning (11000, default 100)",
    )

    args = parser.parse_args()

    if args.threads < 1 or args.threads > 1000:

        print("[!] Thread count must be between 1 and 1000.")

        exit(1)

    # Step 1: Discover hosts (or single IP)

    print(f"[+] Resolving target: {args.target}")

    alive_hosts = discover_hosts(args.target, max_threads=args.threads)

    if not alive_hosts:

        print("[!] No alive hosts found. Exiting.")

        return

    # Write alive_hosts.csv

    results_dir = "Modules/scanner/results"

    os.makedirs(results_dir, exist_ok=True)

    alive_csv = os.path.join(results_dir, "alive_hosts.csv")

    with open(alive_csv, "w", newline="") as f:

        writer = csv.writer(f)

        writer.writerow(["IP Address", "TTL", "OS Guess"])

        for ip, ttl, os_guess in alive_hosts:

            writer.writerow([ip, ttl if ttl is not None else "", os_guess])

    print(f"[+] Alive hosts (with TTL/OS) saved to {alive_csv}\n")

    # Step 2: Determine port list

    if args.all:

        ports = list(range(0, 65536))

        print("[+] Will scan all ports (065535) on each host.\n")

    else:

        if not args.ports:

            print("[!] You must specify a port/range or use -a.")

            exit(1)

        ports = parse_port_range(args.ports)

        print(f"[+] Will scan ports {ports[0]} to {ports[-1]} on each host.\n")

    # Step 3: For each alive host, scan ports, grab banners, perform CVE lookup

    for host_ip, host_ttl, host_os in alive_hosts:

        print(
            f"[+] Scanning {host_ip} (TTL={host_ttl}, OSH{host_os}) with {len(ports)} ports using {args.threads} threads:"
        )
        print(" ")

        results = []

        with ThreadPoolExecutor(max_workers=args.threads) as executor:

            futures = [executor.submit(scan_port, host_ip, p) for p in ports]

            for future in futures:

                port, is_open = future.result()

                banner = ""

                product = None

                version = None

                cves = []

                if is_open:

                    banner = grab_banner(host_ip, port)

                    product, version = parse_service_version(banner)

                    if product and version:

                        cves = lookup_cves_circl(product, version)

                    print(f"    Port {port}: OPEN  {banner}")

                    if cves:

                        print(f"       Found CVEs: {[cid for cid, _ in cves]}")

                results.append((port, is_open, banner, product, version, cves))

        per_host_file = os.path.join(results_dir, f"{host_ip}_ports.csv")

        export_to_csv(results, host_ip, host_ttl, host_os, filename=per_host_file)

        print(" ")
        print(f"[+] Results for {host_ip} written to {per_host_file}\n")
    print("[+] Full scan complete.")


if __name__ == "__main__":

    main()
