# Modules/osint_toolkit/PhoneNumbers_OSINT.py

import sys
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


def lookup_phone(raw):
    try:
        num = parse(raw, None)
    except NumberParseException as e:
        print(f"❌ Error parsing number: {e}", file=sys.stderr)
        sys.exit(1)

    info = {
        "E.164": format_number(num, PhoneNumberFormat.E164),
        "International": format_number(num, PhoneNumberFormat.INTERNATIONAL),
        "Region": f"{region_code_for_number(num)} ({geocoder.description_for_number(num, 'en')})",
        "Carrier": carrier.name_for_number(num, "en") or "Unknown",
        "Timezones": ", ".join(timezone.time_zones_for_number(num)) or "Unknown",
    }

    # Line type
    try:
        lt = number_type(num)
        info["Line type"] = PhoneNumberType(lt).name
    except Exception:
        info["Line type"] = "Unknown"

    return info


def main():
    raw = input("Enter phone number: ").strip()
    info = lookup_phone(raw)

    # Print metadata
    print("\n📊 Phone Metadata:")
    for label, val in info.items():
        print(f"  • {label:13}: {val}")


if __name__ == "__main__":
    main()
