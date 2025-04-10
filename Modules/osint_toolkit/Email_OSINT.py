import os
import requests

"""
using the <request> we can ask have I been Pwned and get the desire output (using --> API Link: https://emailrep.io)
same thing for the EmailRep.io to check if the email is linked to any social media accounnt (API Link: https://emailrep.io )
"""

from bs4 import BeautifulSoup

# Website & Domain Intelligence
# git clone https://github.com/laramies/theHarvester.git
# cd theHarvester
# pip install -r requirements.txt


# ================================================ Code =============================================================


# ========================== #
# 🔧 CONFIGURABLE VARIABLES 🔧
# ========================== #

HIBP_API_KEY = "your_hibp_api_key"  # Get it from https://haveibeenpwned.com/API/v3
USER_AGENT = "OSINT-Tool"  # Change if needed (HIBP requires a User-Agent)
EMAILREP_URL = "https://emailrep.io/"  # API URL for email reputation checks
HIBP_URL = "https://haveibeenpwned.com/api/v3/breachedaccount/"  # HIBP Breach Check API


# ========================== #
# 🔍 FUNCTION: Check Data Breaches #
# ========================== #
def check_breaches(email):
    url = f"{HIBP_URL}{email}?truncateResponse=false"
    headers = {"hibp-api-key": HIBP_API_KEY, "User-Agent": USER_AGENT}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        breaches = response.json()
        print(f"\n🔴 {email} found in {len(breaches)} breach(es):\n")
        for breach in breaches:
            print(f"🔹 {breach['Name']} - {breach['BreachDate']} - {breach['Domain']}")
    elif response.status_code == 404:
        print(f"\n✅ {email} has NOT been found in any breaches.")
    else:
        print(f"\n⚠️ Error fetching breach data: {response.status_code}")


# ========================== #
# 🔍 FUNCTION: Check Email Reputation #
# ========================== #
def check_email_rep(email):
    url = f"{EMAILREP_URL}{email}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(f"\n🔵 Email Reputation for {email}:")
        print(f"🔹 Reputation: {data['reputation']}")
        print(f"🔹 Suspicious: {data['suspicious']}")
        print(f"🔹 Blacklisted: {data['details']['blacklisted']}")
        print(
            f"🔹 Associated Social Media: {', '.join(data['details']['profiles']) if data['details']['profiles'] else 'None'}"
        )
    else:
        print("\n⚠️ Error retrieving email reputation.")


# ========================== #
# 🚀 MAIN FUNCTION #
# ========================== #
def main():
    email = input("Enter an email to investigate: ").strip()

    print("\n🔍 Running OSINT email checks...")

    check_breaches(email)
    check_email_rep(email)


if __name__ == "__main__":
    main()
