import re
import socket
import whois
import requests
from datetime import datetime
from bs4 import BeautifulSoup


# ==================== Domain Validation ====================
def is_valid_domain(domain):
    """
    Validates if the given domain name is in a correct format.
    """
    pattern = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.(?:[A-Za-z]{2,})$"
    return re.match(pattern, domain)


# ==================== Format Dates ====================
def format_date(date):
    """
    Formats date fields from WHOIS data to a readable format.
    Handles both single datetime and lists of datetimes.
    """
    if isinstance(date, list):
        return (
            date[0].strftime("%Y-%m-%d")
            if isinstance(date[0], datetime)
            else str(date[0])
        )
    elif isinstance(date, datetime):
        return date.strftime("%Y-%m-%d")
    return "Not available"


# ==================== WHOIS Lookup ====================
def check_domain_whois(domain_name):
    """
    Fetches and displays WHOIS data for the given domain.
    Includes registrar, creation/expiration dates, and nameservers.
    """
    try:
        domain_info = whois.whois(domain_name)

        print(f"\n🔍 WHOIS Information for {domain_name}:\n")
        print(f"📅 Creation Date: {format_date(domain_info.get('creation_date'))}")
        print(f"🗓 Expiration Date: {format_date(domain_info.get('expiration_date'))}")
        print(f"📝 Registrar: {domain_info.get('registrar', 'Not available')}")
        print(f"🔧 Nameservers: {domain_info.get('name_servers', 'Not available')}")

    except Exception as e:
        print(f"❌ WHOIS Lookup Failed: {e}")


# ==================== IP & Geo Lookup ====================
def get_ip_info(domain):
    """
    Resolves the domain to an IP address, then uses a geolocation API
    to display country, city, ISP, and timezone info.
    """
    try:
        ip = socket.gethostbyname(domain)
        print(f"\n🌐 IP Address Info for {domain}:\n")
        print(f"🔢 IP Address: {ip}")

        # Use ip-api.com to get IP geolocation data
        geo = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        print(f"📍 Location: {geo.get('country', 'N/A')}, {geo.get('city', 'N/A')}")
        print(f"🏢 ISP: {geo.get('isp', 'N/A')}")
        print(f"🕒 Timezone: {geo.get('timezone', 'N/A')}")

    except Exception as e:
        print(f"❌ IP Lookup Failed: {e}")


# ==================== Website Metadata ====================
def get_site_metadata(domain):
    """
    Fetches the website homepage and extracts the <title> and
    <meta name='description'> tags using BeautifulSoup.
    """
    try:
        url = f"http://{domain}"  # Basic URL (http)
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract <title> tag
        title = soup.title.string.strip() if soup.title else "N/A"

        # Extract <meta name="description"> content
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag["content"].strip() if description_tag else "N/A"

        print(f"\n📰 Website Metadata:\n")
        print(f"📄 Title: {title}")
        print(f"📝 Description: {description}")

    except Exception as e:
        print(f"❌ Website Metadata Fetch Failed: {e}")


# ==================== Main Script ====================
if __name__ == "__main__":
    # Ask the user to enter a domain name
    domain_name = (
        input("🔎 Enter a domain to investigate (e.g., example.com): ").strip().lower()
    )

    # Validate domain format before running checks
    if not is_valid_domain(domain_name):
        print(
            "❌ Invalid domain format. Please enter a valid domain (e.g., example.com)."
        )
    else:
        # Run all OSINT checks
        check_domain_whois(domain_name)
        get_ip_info(domain_name)
        get_site_metadata(domain_name)
