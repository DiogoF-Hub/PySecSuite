import requests
from leakcheck import LeakCheckAPI_Public


# Function to check if an email is in any data breach (public API)
def check_email_breach(email):
    try:
        # Use LeakCheck public API for email breach check
        public_api = LeakCheckAPI_Public()
        result = public_api.lookup(
            query=email
        )  # No need for query_type, LeakCheck auto-detects

        # Check if the email was found in any breaches
        if result and isinstance(result, list):
            print(f"\n🔴 {email} FOUND in {len(result)} breaches:\n")
            for breach in result:
                print(f"🔹 Site: {breach['site']}")
                print(f"🔹 Date: {breach.get('date', 'Unknown')}")
                print(f"🔹 Data Leaked: {breach.get('data', 'Unknown')}")
                print(f"{'-'*40}")
            print(
                "⚠️ This email is compromised! Please change your passwords and take security measures."
            )
        else:
            print(f"\n🟢 {email} is SAFE! No breaches found. ✅\n")
    except Exception as e:
        print(f"⚠️ Error: {str(e)}")


# Function to check if an email is linked to any social media accounts
def check_social_media(email):
    print("\n🔍 Checking if the email is linked to any social media accounts...\n")

    # Define some social media platforms to check
    social_media_platforms = [
        "https://www.instagram.com/",  # Instagram
        "https://twitter.com/",  # Twitter
        "https://www.facebook.com/",  # Facebook
        "https://www.linkedin.com/",  # LinkedIn
        "https://www.pinterest.com/",  # Pinterest
        "https://github.com/",  # GitHub
    ]

    # Flag to check if the email is linked to any social media
    found = False

    # Loop through each platform and search for the email in the profile URL
    for platform in social_media_platforms:
        search_url = platform + "search?q=" + email
        response = requests.get(search_url)

        if response.status_code == 200 and "No results found" not in response.text:
            print(f"🔹 Linked to: {platform} ✅")
            found = True
        else:
            print(f"🔹 No results on {platform} ❌")

    if not found:
        print(f"\n❌ No social media links found for {email}.")


# Main function to get user input and run checks
if __name__ == "__main__":
    email = input(
        "📧 Enter an email to check for breaches and social media links: "
    ).strip()

    # Check email breaches using LeakCheck public API
    check_email_breach(email)

    # Check if the email is linked to any social media accounts
    check_social_media(email)
