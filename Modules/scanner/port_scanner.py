import socket
import csv
import os
from concurrent.futures import ThreadPoolExecutor


def scan_port(ip, port, timeout=1.0):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            return port, (result == 0)
    except Exception:
        return port, False


def export_to_csv(
    results, ip, filename="Modules/scanner/results/port_scan_results.csv"
):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    file_exists = os.path.isfile(filename)
    with open(filename, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["IP Address", "Port", "Status"])
        for port, is_open in results:
            writer.writerow([ip, port, "Open" if is_open else "Closed"])


def parse_port_range(port_range):
    try:
        if "-" in port_range:
            start, end = map(int, port_range.split("-"))
            if start > end or start < 1 or end > 65535:
                raise ValueError
            return list(range(start, end + 1))
        else:
            port = int(port_range)
            if port < 1 or port > 65535:
                raise ValueError
            return [port]
    except ValueError:
        print("[!] Invalid port or port range. Use a number or a range like 20-80.")
        exit(1)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Threaded port scanner for a port or port range"
    )
    parser.add_argument("ip", help="Target IP address")
    parser.add_argument("ports", help="Port or port range (e.g. 80 or 20-100)")
    parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=100,
        help="Number of threads to use (default: 100)",
    )
    args = parser.parse_args()

    ip = args.ip
    ports = parse_port_range(args.ports)

    if args.threads < 1 or args.threads > 1000:
        print("[!] Please specify a thread count between 1 and 1000.")
        exit(1)

    print(
        f"[+] Scanning {ip} ports {ports[0]} to {ports[-1]} using {args.threads} threads..."
    )
    results = []

    try:
        with ThreadPoolExecutor(max_workers=args.threads) as executor:
            futures = [executor.submit(scan_port, ip, port) for port in ports]
            for future in futures:
                port, is_open = future.result()
                if is_open:
                    print(f"Port {port}: OPEN")
                results.append((port, is_open))
    except KeyboardInterrupt:
        print("\n[!] Scan interrupted by user.")
        exit(1)

    export_to_csv(results, ip)
    print("[+] Scan complete.")
