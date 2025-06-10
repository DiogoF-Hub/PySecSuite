import streamlit as st
import subprocess, tempfile, os, sys, json

st.set_page_config(layout="wide")

# ───────────────────────────────────────────────────────────
# Main title styled larger and colored yellow
# ───────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='color:#FFFFFF; font-size:48px; margin-bottom:10px;'>OSINT Toolkit — Friendly UI</h1>",
    unsafe_allow_html=True,
)


# ───────────────────────────────────────────────────────────
# Helper to run a script via CLI and parse JSON output
# ───────────────────────────────────────────────────────────
def run_cli(script, flag, value):
    completed = subprocess.run(
        [sys.executable, script, flag, value],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if completed.stderr:
        return {"error": completed.stderr.strip()}
    try:
        return json.loads(completed.stdout)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON output"}


# ───────────────────────────────────────────────────────────
# Helper to render a metric with blue label and smaller value
# ───────────────────────────────────────────────────────────
def html_metric(label, value):
    st.markdown(
        f"<p style='color:#0000FF; font-size:24px; margin:0;'>{label}</p>"
        f"<p style='font-size:14px; margin:0;'>{value}</p>",
        unsafe_allow_html=True,
    )


# ───────────────────────────────────────────────────────────
# Layout: two columns
# ───────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 2])

# ───────────────────────────────────────────────────────────
# Right column: image uploader & preview
# ───────────────────────────────────────────────────────────
with col2:
    uploaded_img = st.file_uploader(
        "🖼️ Drop an image", type=["png", "jpg", "jpeg", "gif"], key="image"
    )
    if uploaded_img:
        st.image(uploaded_img, width=450, caption="Preview")

# ───────────────────────────────────────────────────────────
# Left column: inputs
# ───────────────────────────────────────────────────────────
with col1:
    with st.form("osint_form", clear_on_submit=True):
        domain = st.text_input("🌐 Domain")
        email = st.text_input("✉️ Email")
        ip_input = st.text_input("🔢 IP Address")
        phone = st.text_input("📱 Phone Number")
        username = st.text_input("👤 Username")
        run_all = st.form_submit_button("🔎 Run all OSINT")

if run_all:

    # ───────────────────────────────────────────────────────────
    # DOMAIN Results
    # ───────────────────────────────────────────────────────────
    if domain:
        st.markdown(
            "<h2 style='color:#FFFF00;'>🌐 Domain Results</h2>", unsafe_allow_html=True
        )
        res = run_cli(
            os.path.join("Modules", "osint_toolkit", "DomainWeb_OSINT.py"),
            "--domain",
            domain,
        )
        if "error" in res:
            st.error(res["error"])
        else:
            whois = res.get("whois", {})
            ip_info = res.get("ip", {})
            metadata = res.get("metadata", {})
            # WHOIS metrics
            c1, c2, c3 = st.columns(3)
            with c1:
                html_metric("Registrar", whois.get("registrar", "N/A"))
            with c2:
                html_metric("Created", whois.get("creation_date", "N/A"))
            with c3:
                html_metric("Expires", whois.get("expiration_date", "N/A"))
            st.markdown(
                f"<p style='font-size:14px;'><strong>Nameservers:</strong> {whois.get('nameservers',[])}</p>",
                unsafe_allow_html=True,
            )
            # IP & Geo metrics
            st.markdown(
                "<h3 style='color:#FFFF00;'>IP & Geo</h3>", unsafe_allow_html=True
            )
            d1, d2, d3 = st.columns(3)
            with d1:
                html_metric("IP Address", ip_info.get("address", "N/A"))
            with d2:
                html_metric(
                    "Location",
                    f"{ip_info.get('city','N/A')}, {ip_info.get('country','N/A')}",
                )
            with d3:
                html_metric("ISP", ip_info.get("isp", "N/A"))
            html_metric("Timezone", ip_info.get("timezone", "N/A"))
            # Metadata
            st.markdown(
                "<h3 style='color:#FFFF00;'>Website Metadata</h3>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='font-size:14px;'><strong>Title:</strong> {metadata.get('title','N/A')}</p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='font-size:14px;'><strong>Description:</strong> {metadata.get('description','N/A')}</p>",
                unsafe_allow_html=True,
            )
        st.markdown("---")

    # ───────────────────────────────────────────────────────────
    # EMAIL Results
    # ───────────────────────────────────────────────────────────
    if email:
        st.markdown(
            "<h2 style='color:#FFFF00;'>✉️ Email Results</h2>", unsafe_allow_html=True
        )
        res = run_cli(
            os.path.join("Modules", "osint_toolkit", "Email_OSINT.py"), "--email", email
        )
        if "error" in res:
            st.error(res["error"])
        else:
            breaches = res.get("breaches", [])
            links = res.get("social_links", [])
            html_metric("Breaches Found", len(breaches))
            if breaches:
                st.markdown(
                    "<p style='font-size:14px;'><strong>Breached Sites:</strong></p>",
                    unsafe_allow_html=True,
                )
                for b in breaches:
                    st.markdown(
                        f"<p style='font-size:12px;'>- {b.get('site')} on {b.get('date')}</p>",
                        unsafe_allow_html=True,
                    )
            st.markdown(
                f"<p style='font-size:14px;'><strong>Social Links:</strong> {links}</p>",
                unsafe_allow_html=True,
            )
        st.markdown("---")

    # ───────────────────────────────────────────────────────────
    # IP Results
    # ───────────────────────────────────────────────────────────
    if ip_input:
        st.markdown(
            "<h2 style='color:#FFFF00;'>🔢 IP Results</h2>", unsafe_allow_html=True
        )
        res = run_cli(
            os.path.join("Modules", "osint_toolkit", "IP_OSINT.py"), "--ip", ip_input
        )
        if "error" in res:
            st.error(res["error"])
        else:
            geo = res.get("geolocation", {})
            rdns = res.get("reverse_dns", "N/A")
            html_metric("IP Address", ip_input)
            html_metric(
                "Location", f"{geo.get('city','N/A')}, {geo.get('country','N/A')}"
            )
            html_metric("ISP", geo.get("isp", "N/A"))
            html_metric("Reverse DNS", rdns)
        st.markdown("---")

    # ───────────────────────────────────────────────────────────
    # PHONE Results
    # ───────────────────────────────────────────────────────────
    if phone:
        st.markdown(
            "<h2 style='color:#FFFF00;'>📱 Phone Results</h2>", unsafe_allow_html=True
        )
        res = run_cli(
            os.path.join("Modules", "osint_toolkit", "PhoneNumbers_OSINT.py"),
            "--phone",
            phone,
        )
        if "error" in res:
            st.error(res["error"])
        else:
            html_metric("E.164", res.get("E.164", "N/A"))
            html_metric("International", res.get("International", "N/A"))
            html_metric("Region", res.get("Region", "N/A"))
            html_metric("Carrier", res.get("Carrier", "N/A"))
            st.markdown(
                f"<p style='font-size:14px;'><strong>Timezones:</strong> {res.get('Timezones',[])}</p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='font-size:14px;'><strong>Line type:</strong> {res.get('Line type','N/A')}</p>",
                unsafe_allow_html=True,
            )
        st.markdown("---")

    # ───────────────────────────────────────────────────────────
    # SOCIAL MEDIA Results
    # ───────────────────────────────────────────────────────────
    if username:
        st.markdown(
            "<h2 style='color:#FFFF00;'>👤 Social Media Results</h2>",
            unsafe_allow_html=True,
        )
        res = run_cli(
            os.path.join("Modules", "osint_toolkit", "SocialMedia_OSINT.py"),
            "--username",
            username,
        )
        if "error" in res:
            st.error(res["error"])
        else:
            for plat, status in res.items():
                html_metric(plat.title(), status)
        st.markdown("---")

    # ───────────────────────────────────────────────────────────
    # IMAGE Results
    # ───────────────────────────────────────────────────────────
    if uploaded_img:
        st.markdown(
            "<h2 style='color:#FFFF00;'>🖼️ Image Results</h2>", unsafe_allow_html=True
        )
        suffix = os.path.splitext(uploaded_img.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_img.getvalue())
            img_path = tmp.name
        res = run_cli(
            os.path.join("Modules", "osint_toolkit", "Image_OSINT.py"),
            "--image",
            img_path,
        )
        link = res.get("result_url") or res.get("url")
        if link:
            st.markdown(
                f"<p style='font-size:14px;'><strong>Image Link:</strong> <a href='{link}' target='_blank'>{link}</a></p>",
                unsafe_allow_html=True,
            )
        else:
            st.error(res.get("error", "Failed to get image link"))
        os.remove(img_path)
