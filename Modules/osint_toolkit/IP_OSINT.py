import os
import requests


# ================================================ Code =============================================================

import requests

# Variables for IP address information
API_KEY = "your_ipinfo_api_key_here"  # Your IPinfo.io API key
BASE_URL = "https://ipinfo.io/{}/json"  # Base URL for IPinfo API

# Flags to enable/disable data collection for the IP
CHECK_GEOLOCATION = True  # Check geolocation (city, country, etc.)
CHECK_ISP = True  # Check ISP (Internet Service Provider)
CHECK_ASN = True  # Check ASN (Autonomous System Number)
CHECK_IP_TYPE = True  # Check whether the IP is IPv4 or IPv6


# Function to check IP address via IPinfo API
def check_ip(ip_address):
    url = f"{BASE_URL}?token={API_KEY}"

    # Send a request to the API
    response = requests.get(url.format(ip_address))
    data = response.json()

    if "error" in data:
        print(f"❌ Error: {data['error']['info']}")
        return

    # Display basic IP information
    print(f"🔍 IP Information for {ip_address}:\n")

    if CHECK_GEOLOCATION:
        print(
            f"📍 Location: {data.get('city', 'Not available')}, {data.get('country', 'Not available')}"
        )

    if CHECK_ISP:
        print(f"🌐 ISP: {data.get('org', 'Not available')}")

    if CHECK_ASN:
        print(f"🔢 ASN: {data.get('asn', 'Not available')}")

    if CHECK_IP_TYPE:
        ip_type = "IPv6" if ":" in ip_address else "IPv4"
        print(f"🆔 IP Type: {ip_type}")


# Main function to run the OSINT tool
if __name__ == "__main__":
    ip_address = input("Enter an IP address to check: ").strip()
    check_ip(ip_address)
