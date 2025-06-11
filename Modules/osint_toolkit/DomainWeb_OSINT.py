import re
import socket
import sys
import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup


# ==================== Domain Validation ====================
def is_valid_domain(domain: str) -> bool:
    pattern = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.(?:[A-Za-z]{2,})$"
    return bool(re.match(pattern, domain))


# ==================== Format Dates ====================
def format_date(date):
    if isinstance(date, (list, tuple)) and date:
        date = date[0]
    if isinstance(date, datetime):
        return date.strftime("%Y-%m-%d")
    if isinstance(date, str):
        return date
    return "Not available"


# ==================== Raw Socket WHOIS ====================
def _socket_whois(domain: str) -> str:
    # choose default WHOIS server by TLD
    tld = domain.rsplit(".", 1)[-1].lower()
    server = {
        "com": "whois.verisign-grs.com",
        "net": "whois.verisign-grs.com",
        "org": "whois.pir.org",
    }.get(tld, "whois.iana.org")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(10)
    s.connect((server, 43))
    s.send((domain + "\r\n").encode())
    response = b""
    while True:
        data = s.recv(4096)
        if not data:
            break
        response += data
    s.close()
    return response.decode(errors="ignore")


def _parse_whois_text(text: str) -> dict:
    creation = expiration = registrar = None
    nameservers = []
    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith("creation date:"):
            creation = line.split(":", 1)[1].strip()
        elif line.lower().startswith(("registry expiry date:", "expiry date:")):
            expiration = line.split(":", 1)[1].strip()
        elif line.lower().startswith("registrar:"):
            registrar = line.split(":", 1)[1].strip()
        elif line.lower().startswith("name server:"):
            ns = line.split(":", 1)[1].strip()
            nameservers.append(ns)
    return {
        "creation_date": creation,
        "expiration_date": expiration,
        "registrar": registrar,
        "name_servers": nameservers,
    }


# ==================== Core Lookup ====================
def get_domain_data(domain_name: str) -> dict:
    data = {}

    # -- WHOIS via raw socket --
    try:
        raw_text = _socket_whois(domain_name)
        info = _parse_whois_text(raw_text)
    except Exception as e:
        print(f"[WARN] WHOIS lookup failed: {e}", file=sys.stderr)
        info = {
            "creation_date": None,
            "expiration_date": None,
            "registrar": None,
            "name_servers": [],
        }

    data["whois"] = {
        "creation_date": format_date(info.get("creation_date")),
        "expiration_date": format_date(info.get("expiration_date")),
        "registrar": info.get("registrar") or "Not available",
        "nameservers": info.get("name_servers") or [],
    }

    # -- IP & Geo --
    try:
        ip_addr = socket.gethostbyname(domain_name)
        geo = requests.get(f"http://ip-api.com/json/{ip_addr}", timeout=5).json()
        data["ip"] = {
            "address": ip_addr,
            "country": geo.get("country", "N/A"),
            "city": geo.get("city", "N/A"),
            "isp": geo.get("isp", "N/A"),
            "timezone": geo.get("timezone", "N/A"),
        }
    except Exception as e:
        print(f"[WARN] IP lookup failed: {e}", file=sys.stderr)
        data["ip"] = {
            k: "N/A" for k in ("address", "country", "city", "isp", "timezone")
        }

    # -- Website Metadata --
    try:
        resp = requests.get(f"http://{domain_name}", timeout=5)
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string.strip() if soup.title else "N/A"
        desc = soup.find("meta", {"name": "description"})
        description = desc["content"].strip() if desc and desc.get("content") else "N/A"
        data["metadata"] = {"title": title, "description": description}
    except Exception as e:
        print(f"[WARN] Metadata fetch failed: {e}", file=sys.stderr)
        data["metadata"] = {"title": "N/A", "description": "N/A"}

    return data


# ==================== CLI JSON-wrapper ====================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="OSINT: Domain WHOIS, IP & metadata lookup (JSON output)"
    )
    parser.add_argument(
        "--domain", required=True, help="Domain to investigate (e.g., example.com)"
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
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
