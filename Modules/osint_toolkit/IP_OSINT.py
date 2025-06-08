#!/usr/bin/env python3
"""
OSINT Script to gather IP and domain information: geolocation, WHOIS, reverse DNS lookup, DNS records.
Now refactored to expose a get_ip_data() function and emit JSON on the CLI.
"""

import requests
import socket
import sys
import ipaddress
import whois
import dns.resolver
import json

from ipwhois import IPWhois

# ==================== Core lookup ====================
def get_ip_data(target: str) -> dict:
    """
    Returns geolocation, reverse DNS, IP WHOIS or domain WHOIS + DNS records.
    """
    out = {}

    # Determine if input is an IP or a domain
    try:
        ipaddress.ip_address(target)
        is_ip = True
    except ValueError:
        is_ip = False

    if is_ip:
        # — Geolocation —
        geo = requests.get(f"http://ip-api.com/json/{target}", timeout=10).json()
        out["geolocation"] = {
            "country": geo.get("country"),
            "city": geo.get("city"),
            "isp": geo.get("isp"),
            "timezone": geo.get("timezone"),
        }

        # — Reverse DNS —
        try:
            out["reverse_dns"] = socket.gethostbyaddr(target)[0]
        except Exception:
            out["reverse_dns"] = None

        # — IP WHOIS (RDAP) —
        try:
            rdap = IPWhois(target).lookup_rdap(depth=1)
            out["ip_whois"] = rdap.get("network", {})
        except Exception:
            out["ip_whois_error"] = "Failed to fetch RDAP"

    else:
        # — Domain WHOIS via python-whois —
        w = whois.whois(target)
        out["domain_whois"] = {
            "registrar": w.registrar,
            "creation_date": w.creation_date,
            "expiration_date": w.expiration_date,
            "nameservers": w.name_servers,
        }

        # — DNS Records —
        recs = {}
        for rtype in ("A", "AAAA", "MX", "NS"):
            try:
                answers = dns.resolver.resolve(target, rtype)
                recs[rtype] = [r.to_text() for r in answers]
            except Exception:
                recs[rtype] = []
        out["dns_records"] = recs

    return out


# ==================== CLI JSON‐wrapper ====================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="OSINT: IP/domain lookup (JSON output)"
    )
    parser.add_argument(
        "--ip",
        required=True,
        help="IP address or domain to investigate"
    )
    args = parser.parse_args()

    try:
        result = get_ip_data(args.ip)
        # Emit structured JSON
        print(json.dumps(result))
    except Exception as e:
        # On error, emit a JSON object with an 'error' key on stderr
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
