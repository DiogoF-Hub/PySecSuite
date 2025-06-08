import re
import socket
import whois
import requests
import json
import sys
from datetime import datetime
from bs4 import BeautifulSoup

# ==================== Domain Validation ====================
def is_valid_domain(domain: str) -> bool:
    pattern = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.(?:[A-Za-z]{2,})$"
    return bool(re.match(pattern, domain))

# ==================== Format Dates ====================
def format_date(date):
    if isinstance(date, list):
        d = date[0]
        if isinstance(d, datetime):
            return d.strftime("%Y-%m-%d")
        return str(d)
    if isinstance(date, datetime):
        return date.strftime("%Y-%m-%d")
    return "Not available"

# ==================== Core Lookup ====================
def get_domain_data(domain_name: str) -> dict:
    data = {}
    # WHOIS
    w = whois.whois(domain_name)
    data["whois"] = {
        "creation_date": format_date(w.get("creation_date")),
        "expiration_date": format_date(w.get("expiration_date")),
        "registrar": w.get("registrar") or "Not available",
        "nameservers": w.get("name_servers") or []
    }
    # IP & Geo
    ip_addr = socket.gethostbyname(domain_name)
    geo = requests.get(f"http://ip-api.com/json/{ip_addr}", timeout=5).json()
    data["ip"] = {
        "address": ip_addr,
        "country": geo.get("country", "N/A"),
        "city": geo.get("city", "N/A"),
        "isp": geo.get("isp", "N/A"),
        "timezone": geo.get("timezone", "N/A")
    }
    # Website Metadata
    resp = requests.get(f"http://{domain_name}", timeout=5)
    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.title.string.strip() if soup.title else "N/A"
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag["content"].strip() if desc_tag else "N/A"
    data["metadata"] = {
        "title": title,
        "description": description
    }
    return data

# ==================== CLI JSON‐wrapper ====================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="OSINT: Domain WHOIS, IP & metadata lookup (JSON output)"
    )
    parser.add_argument(
        "--domain",
        required=True,
        help="Domain to investigate (e.g., example.com)"
    )
    args = parser.parse_args()

    domain = args.domain.strip().lower()
    if not is_valid_domain(domain):
        print(json.dumps({"error": "Invalid domain format"}))
        sys.exit(1)

    try:
        result = get_domain_data(domain)
        print(json.dumps(result))
    except Exception as e:
        # Print error as JSON on stderr
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
