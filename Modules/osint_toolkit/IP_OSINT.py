#!/usr/bin/env python3
"""
OSINT Script to gather IP and domain information: geolocation, WHOIS, reverse DNS lookup, DNS records.
Interactive prompt asking for target input.
"""

import requests
import socket
import sys
import ipaddress

try:
    import dns.resolver
except ImportError:
    dns = None

# Domain WHOIS
try:
    import whois as whois_lib
except ImportError:
    whois_lib = None

# IP WHOIS
try:
    from ipwhois import IPWhois
except ImportError:
    IPWhois = None


def get_geolocation(ip):
    """
    Fetch geolocation data for the given IP using ip-api.com (supports IPv4 & IPv6).
    """
    url = f"http://ip-api.com/json/{ip}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get("status") == "success":
            return {
                "Country": data.get("country"),
                "Region": data.get("regionName"),
                "City": data.get("city"),
                "ISP": data.get("isp"),
                "Organization": data.get("org"),
                "AS": data.get("as"),
                "Latitude": data.get("lat"),
                "Longitude": data.get("lon"),
            }
        return {"Error": data.get("message", "Unknown error")}
    except Exception as e:
        return {"Error": str(e)}


def get_reverse_dns(ip):
    """
    Perform a reverse DNS lookup to find the hostname associated with the IP.
    """
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except Exception as e:
        return f"Error: {e}"


def get_ip_whois(ip):
    """
    Retrieve WHOIS (RDAP) information for the IP address.
    """
    try:
        obj = IPWhois(ip)
        result = obj.lookup_rdap(depth=1)
        network = result.get("network", {})
        return {
            "ASN": result.get("asn"),
            "ASN CIDR": result.get("asn_cidr"),
            "ASN Country Code": result.get("asn_country_code"),
            "ASN Registry": result.get("asn_registry"),
            "Network Name": network.get("name"),
            "Network Start": network.get("start_address"),
            "Network End": network.get("end_address"),
            "Network CIDR": network.get("cidr"),
        }
    except Exception as e:
        return {"Error": str(e)}


def get_domain_whois(domain):
    """
    Retrieve WHOIS information for a domain.
    """
    try:
        w = whois_lib.whois(domain)
        return w.text if hasattr(w, "text") else dict(w)
    except Exception as e:
        return {"Error": str(e)}


def get_dns_records(domain):
    """
    Lookup common DNS records (A, AAAA, MX, NS) for a domain.
    """
    records = {}
    if dns is None:
        records["Error"] = "dnspython not installed; install via pip install dnspython"
        return records
    for rtype in ["A", "AAAA", "MX", "NS"]:
        try:
            answers = dns.resolver.resolve(domain, rtype)
            records[rtype] = [rdata.to_text() for rdata in answers]
        except Exception:
            records[rtype] = []
    return records


def print_section(title, content):
    """
    Nicely format and print a section title and its content.
    """
    print(f"\n=== {title} ===")
    if isinstance(content, dict):
        for k, v in content.items():
            print(f"{k}: {v}")
    else:
        print(content)


def main():
    # Prompt the user for the target
    target = input("Enter IP address (IPv4/IPv6) or domain to investigate: ").strip()
    if not target:
        print("[!] No target provided. Exiting.")
        sys.exit(1)
    print(f"[+] Gathering information for: {target}")

    # Determine if target is IP (v4 or v6) or domain
    try:
        ipaddress.ip_address(target)
        is_ip = True
    except ValueError:
        is_ip = False

    if is_ip:
        # Geolocation
        geo = get_geolocation(target)
        print_section("Geolocation", geo)

        # Reverse DNS
        rdns = get_reverse_dns(target)
        print_section("Reverse DNS", rdns)

        # IP WHOIS
        if IPWhois is None:
            print_section(
                "IP WHOIS",
                {"Error": "ipwhois not installed; install via pip install ipwhois"},
            )
        else:
            whois_info = get_ip_whois(target)
            print_section("IP WHOIS", whois_info)
    else:
        # Domain WHOIS
        if whois_lib is None:
            print_section(
                "Domain WHOIS",
                {
                    "Error": "python-whois not installed; install via pip install python-whois"
                },
            )
        else:
            whois_info = get_domain_whois(target)
            print_section("Domain WHOIS", whois_info)

        # DNS Records
        dns_recs = get_dns_records(target)
        print_section("DNS Records", dns_recs)


if __name__ == "__main__":
    main()

# Dependencies:
# pip install requests python-whois dnspython ipwhois
