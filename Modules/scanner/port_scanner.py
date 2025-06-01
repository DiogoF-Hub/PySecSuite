# Scans ports for a given host or list of hosts

import socket
import csv
import os

def scan_port(ip, port, timeout=1.0):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            return result == 0  # True if port is open
    except Exception:
        return False

def export_to_csv(ip, port, is_open, filename='Modules/scanner/results/port_scan_results.csv'):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Create the file if it doesn't exist
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['IP Address', 'Port', 'Status'])  # Header
        writer.writerow([ip, port, 'Open' if is_open else 'Closed'])

    print(f"[+] Result saved: {ip}:{port} - {'Open' if is_open else 'Closed'}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Scan a specific port on a specific IP')
    parser.add_argument('ip', help='Target IP address')
    parser.add_argument('port', type=int, help='Port to scan')
    args = parser.parse_args()

    ip = args.ip
    port = args.port

    print(f"Scanning {ip}:{port}...")
    open_status = scan_port(ip, port)
    print(f"Port {port} on {ip} is {'OPEN' if open_status else 'CLOSED'}")

    export_to_csv(ip, port, open_status)