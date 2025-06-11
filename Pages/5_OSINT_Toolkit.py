import streamlit as st
import subprocess, tempfile, os, sys, json
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")

# ───────────────────────────────────────────────────────────
# Main title styled larger and markdown for info
# ───────────────────────────────────────────────────────────
st.markdown(
    "<h1 style='color:#FFFFFF; font-size:48px; margin-bottom:10px;'>OSINT Toolkit — Friendly UI</h1>",
    unsafe_allow_html=True,
)

with st.expander("ℹ️ About this Toolkit", expanded=False):
    st.markdown(
        """
        <p style='font-size:16px; color:#DDDDDD;'>
        Welcome to the OSINT Toolkit!  This interface lets you drop in a domain, email,
        IP, phone number or username—and get back:
        </p>
        <ul style='font-size:14px; color:#CCCCCC;'>
          <li>WHOIS & DNS for domains</li>
          <li>Geolocation, ISP & timezone for IPs</li>
          <li>Breaches & social footprints for emails</li>
          <li>Carrier, region & line‐type for phones</li>
          <li>Profile status on major platforms for usernames</li>
          <li>Image analysis & reverse image search</li>
        </ul>
        </p>
        """,
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
        f"<p style='color:#FFFFFF; font-size:24px; margin:0;'>{label}</p>"
        f"<p style='font-size:15px; margin:0;'>{value}</p>",
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
            "<h1 style='color:#FFFFFF; font-weight:bold; font-size:3em; text-align:center;'>"
            "🌐🏷️ Domain Results 🏷️🌐</h1>",
            unsafe_allow_html=True,
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
                st.markdown(
                    "<span style='color:#FFFFFF; font-weight:bold;font-size:20px;'>Registrar</span>",
                    unsafe_allow_html=True,
                )
                html_metric("", whois.get("registrar", "N/A"))
            with c2:
                st.markdown(
                    "<span style='color:#FFFFFF; font-weight:bold;font-size:20px;'>Created</span>",
                    unsafe_allow_html=True,
                )
                html_metric("", whois.get("creation_date", "N/A"))
            with c3:
                st.markdown(
                    "<span style='color:#FFFFFF; font-weight:bold;font-size:20px;'>Expires</span>",
                    unsafe_allow_html=True,
                )
                html_metric("", whois.get("expiration_date", "N/A"))

            st.markdown(
                "<p style='font-size:15px;; color:#FFFFFF;'><strong>🖧 Nameservers:</strong> "
                f"{whois.get('nameservers', [])}</p>",
                unsafe_allow_html=True,
            )

            # IP & Geo metrics
            st.markdown(
                "<h2 style='color:#FFFFFF; font-weight:bold;font-size:20px; font-size:1.5em;'>"
                "🛰️ IP & Geo 🛰️</h2>",
                unsafe_allow_html=True,
            )
            d1, d2, d3 = st.columns(3)
            with d1:
                st.markdown(
                    "<span style='color:#FFFFFF; font-weight:bold;font-size:20px;'>IP Address</span>",
                    unsafe_allow_html=True,
                )
                html_metric("", ip_info.get("address", "N/A"))
            with d2:
                st.markdown(
                    "<span style='color:#FFFFFF; font-weight:bold;font-size:20px;'>Location</span>",
                    unsafe_allow_html=True,
                )
                html_metric(
                    "",
                    f"{ip_info.get('city','N/A')}, {ip_info.get('country','N/A')}",
                )
            with d3:
                st.markdown(
                    "<span style='color:#FFFFFF; font-weight:bold;font-size:20px;'>ISP</span>",
                    unsafe_allow_html=True,
                )
                html_metric("", ip_info.get("isp", "N/A"))
            # standalone Timezone metric
            st.markdown(
                "<span style='color:#FFFFFF; font-weight:bold;font-size:20px;'>Timezone</span>",
                unsafe_allow_html=True,
            )
            html_metric("", ip_info.get("timezone", "N/A"))

            # Website Metadata
            st.markdown(
                "<h2 style='color:#FFFFFF; font-weight:bold; font-size:20px;'>"
                "Metadata</h2>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='font-size:15px; color:#FFFFFF;'><strong>📝 Title:</strong> "
                f"{metadata.get('title','N/A')}</p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='font-size:15px; color:#FFFFFF;'><strong>🗒️ Description:</strong> "
                f"{metadata.get('description','N/A')}</p>",
                unsafe_allow_html=True,
            )

        st.markdown("---")

    # ───────────────────────────────────────────────────────────
    # EMAIL Results
    # ───────────────────────────────────────────────────────────
    if email:
        st.markdown(
            # Title: white, bold, 48px, centered
            "<h1 style='color:#FFFFFF; font-weight:bold; font-size:48px; text-align:center;'>"
            "📧✉️ Email Results ✉️📧</h1>",
            unsafe_allow_html=True,
        )
        res = run_cli(
            os.path.join("Modules", "osint_toolkit", "Email_OSINT.py"), "--email", email
        )
        if "error" in res:
            st.error(res["error"])
        else:
            breaches = res.get("breaches", [])
            links = res.get("social_links", [])

            st.markdown(
                f"<p style='color:#FFFFFF; font-size:20px; font-weight:bold;'>🔓 Breaches Found: {len(breaches)}</p>",
                unsafe_allow_html=True,
            )

            if breaches:
                # Breached Sites label: white, bold, 20px
                st.markdown(
                    "<span style='color:#FFFFFF; font-weight:bold; font-size:20px;'>"
                    "🔓 Breached Sites:</span>",
                    unsafe_allow_html=True,
                )
                # Each bullet: white, 18px
                for b in breaches:
                    st.markdown(
                        f"<p style='color:#FFFFFF; font-size:18px;'>• {b.get('site')} on {b.get('date')}</p>",
                        unsafe_allow_html=True,
                    )

            # Social Links label & value: white, 18px
            st.markdown(
                "<p style='color:#FFFFFF; font-size:18px;'>"
                f"<strong>🌐 Social Links:</strong> {links}</p>",
                unsafe_allow_html=True,
            )
        st.markdown("---")

    # ───────────────────────────────────────────────────────────
    # IP Results
    # ───────────────────────────────────────────────────────────
    if ip_input:
        # Title
        st.markdown(
            "<h1 style='color:#FFFFFF; font-weight:bold; font-size:48px; text-align:center;'>"
            "🔢🌐 IP Results 🌐🔢</h1>",
            unsafe_allow_html=True,
        )
        res = run_cli(
            os.path.join("Modules", "osint_toolkit", "IP_OSINT.py"), "--ip", ip_input
        )
        if "error" in res:
            st.error(res["error"])
        else:
            geo = res.get("geolocation", {})
            rdns = res.get("reverse_dns", "N/A")

            # Remove default margins on all p/span
            st.markdown(
                """
                <style>
                p, span { margin: 0 !important; padding: 0 !important; }
                </style>
                """,
                unsafe_allow_html=True,
            )

            # IP Address
            st.markdown(
                "<span style='color:#FFFFFF; font-weight:bold; font-size:20px;'>IP Address</span>",
                unsafe_allow_html=True,
            )
            html_metric("", ip_input)

            # Location
            st.markdown(
                "<span style='color:#FFFFFF; font-weight:bold; font-size:20px;'>Location</span>",
                unsafe_allow_html=True,
            )
            html_metric("", f"{geo.get('city','N/A')}, {geo.get('country','N/A')}")

            # ISP
            st.markdown(
                "<span style='color:#FFFFFF; font-weight:bold; font-size:20px;'>ISP</span>",
                unsafe_allow_html=True,
            )
            html_metric("", geo.get("isp", "N/A"))

            # Reverse DNS
            st.markdown(
                "<span style='color:#FFFFFF; font-weight:bold; font-size:20px;'>Reverse DNS</span>",
                unsafe_allow_html=True,
            )
            html_metric("", rdns)

        st.markdown("---")

    # ───────────────────────────────────────────────────────────
    # PHONE Results
    # ───────────────────────────────────────────────────────────
    if phone:
        # Title
        st.markdown(
            "<h1 style='color:#FFFFFF; font-weight:bold; font-size:48px; text-align:center;'>"
            "📱 Phone Results 📱</h1>",
            unsafe_allow_html=True,
        )

        res = run_cli(
            os.path.join("Modules", "osint_toolkit", "PhoneNumbers_OSINT.py"),
            "--phone",
            phone,
        )
        if "error" in res:
            st.error(res["error"])
        else:
            # Remove default margins on all p/span
            st.markdown(
                """
                <style>
                p, span { margin: 0 !important; padding: 0 !important; }
                </style>
                """,
                unsafe_allow_html=True,
            )

            # E.164
            st.markdown(
                "<span style='color:#FFFFFF; font-weight:bold; font-size:20px;'>E.164</span>",
                unsafe_allow_html=True,
            )
            html_metric("", res.get("E.164", "N/A"))

            # International
            st.markdown(
                "<span style='color:#FFFFFF; font-weight:bold; font-size:20px;'>International</span>",
                unsafe_allow_html=True,
            )
            html_metric("", res.get("International", "N/A"))

            # Region
            st.markdown(
                "<span style='color:#FFFFFF; font-weight:bold; font-size:20px;'>Region</span>",
                unsafe_allow_html=True,
            )
            html_metric("", res.get("Region", "N/A"))

            # Carrier
            st.markdown(
                "<span style='color:#FFFFFF; font-weight:bold; font-size:20px;'>Carrier</span>",
                unsafe_allow_html=True,
            )
            html_metric("", res.get("Carrier", "N/A"))

            # Timezones
            st.markdown(
                "<span style='color:#FFFFFF; font-weight:bold; font-size:20px;'>Timezones</span>",
                unsafe_allow_html=True,
            )
            html_metric("", str(res.get("Timezones", [])))

            # Line type
            st.markdown(
                "<span style='color:#FFFFFF; font-weight:bold; font-size:20px;'>Line type</span>",
                unsafe_allow_html=True,
            )
            html_metric("", res.get("Line type", "N/A"))

        st.markdown("---")

    # ───────────────────────────────────────────────────────────
    # SOCIAL MEDIA Results
    # ───────────────────────────────────────────────────────────

    if username:
        st.markdown("### 👤 Social Media Results", unsafe_allow_html=True)
        raw = run_cli(
            os.path.join("Modules", "osint_toolkit", "SocialMedia_OSINT.py"),
            "--username",
            username,
        )

        if "error" in raw:
            st.error(raw["error"])
        else:
            # build DataFrame
            df = pd.DataFrame(raw["results"])
            df = df.rename(
                columns={
                    "platform": "Platform",
                    "status": "Status",
                    "url": "Profile URL",
                }
            )

            # 1) Keep the raw status around for logic
            df["RawStatus"] = df["Status"]

            # 2) Capitalize & bold the Platform column (vectorized)
            df["Platform"] = "<strong>" + df["Platform"].str.title() + "</strong>"

            # 3) Map statuses to emojis & pretty text (vectorized)
            emoji_map = {"found": "✅", "not_found": "❌", "error": "⚠️"}
            df["Status"] = (
                df["RawStatus"].map(emoji_map).fillna("")
                + " "
                + df["RawStatus"].str.replace("_", " ").str.title()
            )

            # 4) Build the “Visit” link for all URLs (vectorized)
            visit_links = (
                '<a href="' + df["Profile URL"] + '" target="_blank">Visit</a>'
            )
            # 5) Only keep the link where RawStatus is found or error
            mask = df["RawStatus"].isin(["found", "error"])
            df["Profile URL"] = np.where(mask, visit_links, "—")

            # 6) Render as HTML table
            html = df.to_html(
                columns=["Platform", "Status", "Profile URL"],
                index=False,
                escape=False,
                justify="left",
            )
            st.markdown(html, unsafe_allow_html=True)

        st.markdown("---")

    # ───────────────────────────────────────────────────────────
    # IMAGE Results
    # ───────────────────────────────────────────────────────────
    if uploaded_img:
        st.markdown(
            "<h2 style='color:#FFFFFF;'>🖼️ Image Results</h2>", unsafe_allow_html=True
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
                f"<p style='font-size:20px;'><strong>Image Link:</strong> <a href='{link}' target='_blank'>{link}</a></p>",
                unsafe_allow_html=True,
            )
        else:
            st.error(res.get("error", "Failed to get image link"))
        os.remove(img_path)
        st.markdown("---")
