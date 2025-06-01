import subprocess
import platform
import ipaddress
import csv
import os
from concurrent.futures import ThreadPoolExecutor

def ping_host(ip):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '-W', '1', str(ip)]
    try:
        result = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return str(ip) if result.returncode == 0 else None
    except Exception:
        return None
    print("ping")

def discover_hosts(ip_range, max_threads=100):
    network = ipaddress.ip_network(ip_range, strict=False)
    alive_hosts = []
    print("hosts")

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        results = executor.map(ping_host, network.hosts())

    for result in results:
        if result:
            alive_hosts.append(result)

    return alive_hosts

def export_to_csv(hosts, filename='Modules/scanner/results/alive_hosts.csv'):
    folder = os.path.dirname(filename)
    os.makedirs(folder, exist_ok=True)

    # Create the file if it doesn't exist
    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['IP Address'])  # write header

    # Append alive hosts to the file
    with open(filename, 'a', newline='') as f:
        writer = csv.writer(f)
        for host in hosts:
            writer.writerow([host])

    print(f"[+] Results exported to {filename}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Ping sweep: scan entire /24 subnet based on a single IP')
    parser.add_argument('ip', help='Any IP within the target subnet (e.g., 192.168.1.5)')
    args = parser.parse_args()

    ip = ipaddress.ip_address(args.ip)
    network = ipaddress.ip_network(f"{ip}/24", strict=False)

    print(f"Scanning network: {network}")
    found_hosts = discover_hosts(str(network))
    print("Alive hosts:")
    for host in found_hosts:
        print(f" - {host}")
    print(f"Scan completed. {len(found_hosts)} hosts found.")

    export_to_csv(found_hosts)