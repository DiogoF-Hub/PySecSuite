import re
import hashlib
import os
from datetime import datetime

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
uploads_dir = os.path.join(root_dir, "Uploads")
result_dir = os.path.join(root_dir, "Modules", "password_cracker", "Results")
assets_dir = os.path.join(root_dir, "Assets")
wordlist_dir = os.path.join(assets_dir, "wordlists")
wordlist_file = os.path.join(wordlist_dir, "rockyou.txt")
Hashes_dir = os.path.join(assets_dir, "Hashes")
hashes_file = os.path.join(Hashes_dir, "hashes.txt")


def identify_hash_type(hash_string):
    if re.match(r"^\$2[aby]\$.{56}$", hash_string):
        print(f"[!] BCRYPT not supported (use Hashcat).")
        return False
    elif re.match(r"^\$argon2(id|i|d)\$", hash_string):
        print(f"[!] ARGON2 not supported (use Hashcat).")
        return False
    elif re.match(r"^[a-fA-F0-9]{32}$", hash_string):
        print("[~] Detected 32-char hash. Assuming MD5.")
        return "md5"
    elif re.match(r"^[a-fA-F0-9]{40}$", hash_string):
        return "sha1"
    elif re.match(r"^[a-fA-F0-9]{64}$", hash_string):
        return "sha256"
    elif re.match(r"^[a-fA-F0-9]{128}$", hash_string):
        return "sha512"
    else:
        return False


def crack_single_hash(hash_line, wordlist_file):
    algorithm = identify_hash_type(hash_line)
    if not algorithm:
        return None

    print(f"[~] Cracking {hash_line} ({algorithm.upper()})...")

    try:
        with open(wordlist_file, "r", encoding="latin-1") as wordlist:
            for idx, word in enumerate(wordlist):
                word = word.strip()
                word_bytes = word.encode("utf-8")

                if algorithm == "md5":
                    hashed = hashlib.md5(word_bytes).hexdigest()
                elif algorithm == "sha1":
                    hashed = hashlib.sha1(word_bytes).hexdigest()
                elif algorithm == "sha256":
                    hashed = hashlib.sha256(word_bytes).hexdigest()
                elif algorithm == "sha512":
                    hashed = hashlib.sha512(word_bytes).hexdigest()
                else:
                    return None

                if hashed.lower() == hash_line.lower():
                    print(f"[+] Match found: {word}")
                    return word

                if idx % 100000 == 0:
                    print(f"[~] Tried {idx} words...")

        return None
    except FileNotFoundError:
        print("[!] Wordlist file not found.")
        return None


def multi_crack_hashes_streamed(wordlist_file, hashes_file, save_results=False):
    if save_results:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_filename = f"cracked_hashes_{timestamp}.txt"
        result_path = os.path.join(result_dir, result_filename)

        if not os.path.exists(result_dir):
            os.makedirs(result_dir)

        print(
            f"[+] Results will be saved to {os.path.join(result_dir, 'cracked_hashes.txt')}"
        )

    try:
        with open(hashes_file, "r") as hash_file:
            for hash_line in hash_file:
                hash_line = hash_line.strip()
                if not hash_line:
                    continue
                result = crack_single_hash(hash_line, wordlist_file)
                if result:
                    print(f"[=] {hash_line} => {result}")
                    if save_results:
                        with open(result_path, "a") as result_file:
                            result_file.write(f"{hash_line} => {result}\n")
                else:
                    print(f"[-] {hash_line} => Not Found")
        print("[~] Finished processing all hashes.")
        return result_path if save_results else None
    except FileNotFoundError:
        print("[!] hashes.txt file not found.")
