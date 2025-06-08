# --- Pages/5_OSINT_Toolkit.py (Streamlit UI) ---
import streamlit as st
import subprocess, tempfile, os, sys, json

st.set_page_config(layout="wide")
st.title("OSINT Toolkit — Friendly UI")

with st.form("osint_form", clear_on_submit=True):
    c1, c2 = st.columns([1, 2])
    with c1:
        domain   = st.text_input("🌐 Domain")
        email    = st.text_input("✉️ Email")
        ip_input = st.text_input("🔢 IP Address")
        phone    = st.text_input("📱 Phone Number")
        username = st.text_input("👤 Username")
    with c2:
        uploaded_img = st.file_uploader(
            "🖼️ Drop an image",
            type=["png", "jpg", "jpeg", "gif"]
        )
        if uploaded_img:
            st.image(uploaded_img, use_column_width=True, caption="Preview")
    run_all = st.form_submit_button("🔎 Run all OSINT")

# helper to run a script via CLI and parse JSON output
def run_cli(script, flag, value):
    completed = subprocess.run(
        [sys.executable, script, flag, value],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if completed.stderr:
        return {"error": completed.stderr.strip()}
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON output"}

if run_all:
    # DOMAIN
    if domain:
        st.header("🌐 Domain Results")
        res = run_cli(
            os.path.join("Modules","osint_toolkit","DomainWeb_OSINT.py"),
            "--domain", domain
        )
        st.json(res)

    # EMAIL
    if email:
        st.header("✉️ Email Results")
        res = run_cli(
            os.path.join("Modules","osint_toolkit","Email_OSINT.py"),
            "--email", email
        )
        st.json(res)

    # IP
    if ip_input:
        st.header("🔢 IP Results")
        res = run_cli(
            os.path.join("Modules","osint_toolkit","IP_OSINT.py"),
            "--ip", ip_input
        )
        st.json(res)

    # PHONE
    if phone:
        st.header("📱 Phone Results")
        res = run_cli(
            os.path.join("Modules","osint_toolkit","PhoneNumbers_OSINT.py"),
            "--phone", phone
        )
        st.json(res)

    # SOCIAL MEDIA
    if username:
        st.header("👤 Social Media Results")
        res = run_cli(
            os.path.join("Modules","osint_toolkit","SocialMedia_OSINT.py"),
            "--username", username
        )
        st.json(res)

    # IMAGE
    if uploaded_img:
        suffix = os.path.splitext(uploaded_img.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_img.getvalue())
            img_path = tmp.name

        st.header("🖼️ Image Results")
        res = run_cli(
            os.path.join("Modules","osint_toolkit","Image_OSINT.py"),
            "--image", img_path
        )
        if "result_url" in res:
            st.markdown(f"**Image result link:** [Click here]({res['result_url']})")
        else:
            st.error(res.get("error", "Failed to get image link"))
        os.remove(img_path)
