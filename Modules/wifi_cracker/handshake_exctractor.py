from scapy.all import rdpcap, EAPOL
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11Elt
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
uploads_dir = os.path.join(root_dir, "Uploads")
assets_dir = os.path.join(root_dir, "Assets")
wordlist_dir = os.path.join(assets_dir, "Wordlists")


def extract_handshakes_packets(pcap_file):
    packets = rdpcap(pcap_file)

    ssid = None
    ap_mac = None
    client_mac = None
    handshake_packets = []

    for pkt in packets:
        if pkt.haslayer(Dot11Beacon) and pkt.haslayer(Dot11Elt):
            if pkt[Dot11Elt].ID == 0:
                ssid = pkt[Dot11Elt].info.decode("utf-8", errors="ignore")
                ap_mac = pkt[Dot11].addr2

        elif pkt.haslayer(EAPOL):
            handshake_packets.append(pkt)
            if not client_mac:
                if pkt[Dot11].addr1 != ap_mac:
                    client_mac = pkt[Dot11].addr1
                elif pkt[Dot11].addr2 != ap_mac:
                    client_mac = pkt[Dot11].addr2

    print(f"[+] SSID: {ssid}")
    print(f"[+] AP MAC: {ap_mac}")
    print(f"[+] Client MAC: {client_mac}")
    print(f"[+] Total EAPOL Packets Found: {len(handshake_packets)}")

    return {
        "ssid": ssid,
        "ap_mac": ap_mac,
        "client_mac": client_mac,
        "handshake_packets": handshake_packets,
    }


def is_valid_handshake(packets, ap_mac, client_mac):
    msg_found = set()

    for pkt in packets:
        if not pkt.haslayer(EAPOL):
            continue

        src = pkt.addr2
        dst = pkt.addr1
        eapol_len = len(pkt[EAPOL].load) if pkt[EAPOL].load else 0

        # Heuristics based on direction and EAPOL payload size
        if src == ap_mac and dst == client_mac:
            if eapol_len < 100:
                msg_found.add(1)  # Likely Message 1
            else:
                msg_found.add(3)  # Likely Message 3
        elif src == client_mac and dst == ap_mac:
            if eapol_len >= 100:
                msg_found.add(2)  # Likely Message 2
            else:
                msg_found.add(4)  # Possibly Message 4

    # Determine if a valid cracking combo is present
    valid = 2 in msg_found and (1 in msg_found or 3 in msg_found)

    # Print detected messages
    msg_names = {1: "Message 1", 2: "Message 2", 3: "Message 3", 4: "Message 4"}
    print("[*] Detected Handshake Messages:")
    for i in sorted(msg_found):
        print(f"    - {msg_names[i]}")

    if valid:
        print("[+] Valid handshake detected and usable for cracking.")
    else:
        print("[-] Incomplete or invalid handshake.")

    return valid


def crack(pcap_path):
    # 1. Check path
    if not os.path.exists(pcap_path):
        print(f"[-] File not found: {pcap_path}")
        return

    # 2. Extract the handshake-related packets and details
    result = extract_handshakes_packets(pcap_path)

    # 3. Check if a valid 4-way handshake is present
    if not result["handshake_packets"]:
        print("[-] No EAPOL packets found.")
        return

    result2 = is_valid_handshake(
        result["handshake_packets"], result["ap_mac"], result["client_mac"]
    )
    if result2:
        print("[✔] Ready to proceed with password cracking.")
        print("⚠️ Cracking feature is not implemented yet.")
        print(
            "   This module currently only validates the PCAP for a usable WPA/WPA2 handshake."
        )
        print(
            "   Cracking with Hashcat is only supported on Linux and was not completed in time."
        )
        print("   🔧 Feature coming soon in a future update!")

    else:
        print("[✘] Handshake not valid for cracking.")
