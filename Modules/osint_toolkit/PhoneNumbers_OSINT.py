from phonenumbers import (
    parse,
    NumberParseException,
    format_number,
    PhoneNumberFormat,
    geocoder,
    carrier,
    timezone,
    number_type,
    PhoneNumberType,
    region_code_for_number,
)
import json
import sys


def get_phone_data(raw: str) -> dict:
    """
    Returns parsed phone number metadata.

    """
    try:
        num = parse(raw, None)
    except NumberParseException as e:
        return {"error": str(e)}

    info = {
        "E.164": format_number(num, PhoneNumberFormat.E164),
        "International": format_number(num, PhoneNumberFormat.INTERNATIONAL),
        "Region": f"{region_code_for_number(num)} ({geocoder.description_for_number(num, 'en')})",
        "Carrier": carrier.name_for_number(num, "en") or None,
        "Timezones": timezone.time_zones_for_number(num),
    }
    try:
        info["Line type"] = PhoneNumberType(number_type(num)).name
    except Exception:
        info["Line type"] = None

    return info


# ==================== CLI JSON‐wrapper ====================
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="OSINT: Phone number lookup (JSON output)"
    )
    parser.add_argument(
        "--phone",
        required=True,
        help="Phone number to investigate (in international format or with country code)",
    )
    args = parser.parse_args()

    try:
        result = get_phone_data(args.phone)
        print(json.dumps(result))
    except Exception as e:
        # ───────────────────────────────────────────────────────────
        # Print error as JSON on stderr
        # ───────────────────────────────────────────────────────────
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)
