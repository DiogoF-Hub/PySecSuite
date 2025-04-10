import os
import whois

from bs4 import BeautifulSoup

# ================================================ Code =============================================================

import whois
from datetime import datetime

# Variables for WHOIS query
CHECK_CREATION_DATE = True  # Check the domain's creation date
CHECK_EXPIRATION_DATE = True  # Check the domain's expiration date
CHECK_REGISTRAR = True  # Check the domain's registrar
CHECK_NAMESERVERS = True  # Check the nameservers of the domain


# Function to check WHOIS information for a domain
def check_domain_whois(domain_name):
    try:
        # Query WHOIS information for the domain
        domain_info = whois.whois(domain_name)

        # Display domain information
        print(f"🔍 WHOIS Information for {domain_name}:\n")

        if CHECK_CREATION_DATE:
            creation_date = domain_info.get("creation_date", "Not available")
            print(
                f"📅 Creation Date: {creation_date if isinstance(creation_date, datetime) else 'Invalid format'}"
            )

        if CHECK_EXPIRATION_DATE:
            expiration_date = domain_info.get("expiration_date", "Not available")
            print(
                f"🗓 Expiration Date: {expiration_date if isinstance(expiration_date, datetime) else 'Invalid format'}"
            )

        if CHECK_REGISTRAR:
            registrar = domain_info.get("registrar", "Not available")
            print(f"📝 Registrar: {registrar}")

        if CHECK_NAMESERVERS:
            nameservers = domain_info.get("nameservers", "Not available")
            print(f"🔧 Nameservers: {nameservers}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


# Main function to run the domain WHOIS check
if __name__ == "__main__":
    domain_name = input("Enter the domain to check (e.g., example.com): ").strip()
    check_domain_whois(domain_name)
