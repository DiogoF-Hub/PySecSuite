import subprocess
import platform
import ipaddress
import socket
import csv
import os
import argparse
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


def ping_host(ip):
    """
    Ping a single IP once. Returns the IP string if alive, else None.
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    # On Linux/macOS, -W specifies timeout in seconds. On Windows, timeout is implicit.
    timeout_flag = "-W" if platform.system().lower() != "windows" else ""
    # Build command accordingly
    if platform.system().lower() == "windows":
        command = ["ping", param, "1", str(ip)]
    else:
        command = ["ping", param, "1", timeout_flag, "1", str(ip)]
    try:
        result = subprocess.run(
            command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return str(ip) if result.returncode == 0 else None
    except Exception:
        return None


def discover_hosts(ip_sample, max_threads=100):
    """
    Given one IP (e.g., "192.168.1.5"), derives the /24 subnet ("192.168.1.0/24")
    and pings every host in that range using a ThreadPool. Returns a list of alive IPs.
    """
    # Determine the /24 network from the sample IP
    network = ipaddress.ip_network(f"{ip_sample}/24", strict=False)
    alive = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        for result in executor.map(ping_host, network.hosts()):
            if result:
                alive.append(result)
    return alive


def parse_port_range(port_range):
    """
    Given a string like "80" or "20-100", return a list of integers.
    Valid bounds: 0–65535. Exits(1) on invalid input.
    """
    try:
        if "-" in port_range:
            start, end = map(int, port_range.split("-", 1))
            if start > end or start < 0 or end > 65535:
                raise ValueError
            return list(range(start, end + 1))
        else:
            port = int(port_range)
            if port < 0 or port > 65535:
                raise ValueError
            return [port]
    except Exception:
        print(
            "[!] Invalid port or port range. Use a number (0–65535) or a range like 20-100."
        )
        exit(1)


def scan_port(ip, port, timeout=1.0):
    """
    Attempt to connect to (ip, port). Returns (port, True) if open, else (port, False).
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            return port, (result == 0)
    except Exception:
        return port, False


def grab_banner(ip, port, timeout=2.0):
    """
    If (ip, port) is open, connect and attempt to recv() up to 1024 bytes.
    Returns decoded banner string or "" on failure.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            s.connect((ip, port))
            banner = s.recv(1024)
            return banner.decode(errors="ignore").strip()
    except Exception:
        return ""


def export_to_csv(
    results, ip, filename="Modules/scanner/results/port_scan_results.csv"
):
    """
    Writes a CSV file, appending if it already exists.
    `results` is a list of tuples: (port, is_open, banner).
    If the file is new, writes a header row first.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["IP Address", "Port", "Status", "Banner"])
        for port, is_open, banner in results:
            writer.writerow([ip, port, "Open" if is_open else "Closed", banner])


def main():
    # Print ASCII banner
    print(BANNER)

    parser = argparse.ArgumentParser(
        description="PySecSuit — Full-network scan: Host Discovery + Threaded Port Scanner + Banner Grabbing"
    )
    parser.add_argument(
        "ip_sample", help="Any IP in the /24 subnet (e.g., 192.168.1.5)"
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
        help="Number of threads for port scanning (default: 100; max 1000)",
    )
    args = parser.parse_args()

    # Validate thread count
    if args.threads < 1 or args.threads > 1000:
        print("[!] Thread count must be between 1 and 1000.")
        exit(1)

    ip_sample = args.ip_sample

    # Step 1: Host discovery
    print(f"[+] Discovering hosts in network: {ip_sample}/24")
    alive_hosts = discover_hosts(ip_sample, max_threads=args.threads)
    if not alive_hosts:
        print("[!] No alive hosts found. Exiting.")
        return

    # Write alive_hosts.csv
    results_dir = "Modules/scanner/results"
    os.makedirs(results_dir, exist_ok=True)
    alive_csv = os.path.join(results_dir, "alive_hosts.csv")
    with open(alive_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["IP Address"])
        for h in alive_hosts:
            writer.writerow([h])
    print(f"[+] Alive hosts saved to {alive_csv}\n")

    # Determine port list once (same for all hosts)
    if args.all:
        ports = list(range(0, 65536))
        print(f"[+] Will scan ALL ports (0–65535) on each alive host.\n")
    else:
        if not args.ports:
            print("[!] You must specify a port/range or use -a to scan all ports.")
            exit(1)
        ports = parse_port_range(args.ports)
        print(f"[+] Will scan ports {ports[0]} to {ports[-1]} on each alive host.\n")

    # Step 2: For each alive host, run threaded port scan + banner grabbing
    for host in alive_hosts:
        print(
            f"[+] Scanning {host} with {len(ports)} ports using {args.threads} threads:"
        )
        results = []
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = [executor.submit(scan_port, host, p) for p in ports]
            for future in futures:
                port, is_open = future.result()
                banner = ""
                if is_open:
                    banner = grab_banner(host, port)
                    print(f"    Port {port}: OPEN   – {banner}")
                results.append((port, is_open, banner))

        # Step 3: Export per-host results to CSV named <host>_ports.csv
        per_host_file = os.path.join(results_dir, f"{host}_ports.csv")
        export_to_csv(results, host, filename=per_host_file)
        print(f"[+] Results for {host} written to {per_host_file}\n")

    print("[+] Full scan complete.")


if __name__ == "__main__":
    main()
