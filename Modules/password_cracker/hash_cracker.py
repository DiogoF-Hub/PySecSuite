import re
import hashlib


def identify_hash_type(hash_string):
    hash_string = hash_string.strip()

    # Specific patterns for common hash types
    if re.match(r"^\$2[aby]\$.{56}$", hash_string):  # bcrypt
        return "bcrypt"
    elif re.match(r"^\$argon2(id|i|d)\$", hash_string):  # argon2
        return "argon2"
    elif re.match(r"^[a-fA-F0-9]{32}$", hash_string):  # MD5
        return "md5_or_ntlm"
    elif re.match(r"^[a-fA-F0-9]{40}$", hash_string):  # SHA1
        return "sha1"
    elif re.match(r"^[a-fA-F0-9]{64}$", hash_string):  # SHA256
        return "sha256"
    elif re.match(r"^[a-fA-F0-9]{128}$", hash_string):  # SHA512
        return "sha512"
    else:
        return "unknown"


def crack_hash(hash_to_crack, wordlist_path="Assets/wordlists/rockyou.txt"):
    algorithm = identify_hash_type(hash_to_crack)

    if algorithm == "unknown":
        print("[!] Could not identify hash algorithm.")
        return None
    elif algorithm in ["bcrypt", "argon2"]:
        print(f"[!] {algorithm.upper()} is not supported by hashlib (use Hashcat).")
        return None
    elif algorithm == "md5_or_ntlm":
        print("[!] Detected 32-character hex hash (MD5 or NTLM). Defaulting to MD5.")
        algorithm = "md5"

    print(f"[~] Cracking using detected algorithm: {algorithm.upper()}")

    try:
        # Open the wordlist file
        with open(wordlist_path, "r", encoding="latin-1") as f:
            # Read the wordlist file line by line with index
            for idx, word in enumerate(f):
                word = word.strip()
                word_bytes = word.encode("utf-8")

                # Hashing based on algorithm
                if algorithm == "md5":
                    hashed = hashlib.md5(word_bytes).hexdigest()
                elif algorithm == "sha1":
                    hashed = hashlib.sha1(word_bytes).hexdigest()
                elif algorithm == "sha256":
                    hashed = hashlib.sha256(word_bytes).hexdigest()
                elif algorithm == "sha512":
                    hashed = hashlib.sha512(word_bytes).hexdigest()
                else:
                    print(f"[!] Unsupported algorithm: {algorithm}")
                    return None

                if hashed.lower() == hash_to_crack.lower():  # Compare in lowercase
                    # If a match is found, print the password and return it
                    print(f"[+] Password found: {word}")
                    return word

                if idx % 100000 == 0:  # Print progress every 100,000 attempts
                    print(f"[~] Tried {idx} passwords...")

        print("[-] Password not found.")
        return None

    except FileNotFoundError:  # Handle the case where the wordlist file is not found
        print("[!] rockyou.txt file not found!")
        return None
