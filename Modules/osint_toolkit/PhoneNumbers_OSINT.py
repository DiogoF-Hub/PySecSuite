import os
import requests


# ================================================ Code =============================================================


# Variables for the phone number information
API_KEY = "your_numverify_api_key_here"  # Your NumVerify API key
BASE_URL = "http://apilayer.net/api/validate"  # Base URL for NumVerify API

# Flags to enable/disable data collection
CHECK_VALIDITY = True  # Check if the phone number is valid
CHECK_LOCATION = True  # Check the location of the phone number
CHECK_CARRIER = True  # Check the carrier information of the phone number


# Function to check phone number via NumVerify API
def check_phone_number(phone_number):
    # Construct the API URL with necessary parameters
    url = f"{BASE_URL}?access_key={API_KEY}&number={phone_number}"

    # Send a request to the API
    response = requests.get(url)
    data = response.json()

    # Check if the number is valid
    if data.get("valid", False):
        print(f"✅ Phone number {phone_number} is valid.")

        # Display additional information based on flags
        if CHECK_LOCATION:
            print(
                f"📍 Location: {data.get('location', 'Not available')}, {data.get('country_name', 'Not available')}"
            )

        if CHECK_CARRIER:
            print(f"📶 Carrier: {data.get('carrier', 'Not available')}")
    else:
        print(f"❌ Phone number {phone_number} is invalid or unreachable.")


# Function to check username or phone number
def check_input(query, is_phone_number=False):
    if is_phone_number:
        check_phone_number(query)
    else:
        check_username(query)  # This would call your username checking function


# Main function to run the OSINT tool
if __name__ == "__main__":
    user_input = input("Enter a username or phone number: ").strip()
    choice = input("Is this a phone number? (yes/no): ").strip().lower()

    if choice == "yes":
        check_input(user_input, is_phone_number=True)
    else:
        check_input(user_input, is_phone_number=False)
