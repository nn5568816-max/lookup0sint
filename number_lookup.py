#!/usr/bin/env python3

import json
import re
import sys
import getpass
import hashlib
import requests

from config import API_URL, PASSWORD_HASH


def banner():
    print(r"""
╔══════════════════════════════════════╗
║       NUMBER LOOKUP TOOL v1.1       ║
║          TERMUX EDITION             ║
╚══════════════════════════════════════╝
""")


def login():
    print("🔐 Password Protected")

    for attempt in range(3):

        password = getpass.getpass("Password: ")

        entered_hash = hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()

        if entered_hash == PASSWORD_HASH:
            print("[+] Access granted.\n")
            return True

        remaining = 2 - attempt

        if remaining > 0:
            print(
                f"[!] Wrong password. "
                f"Attempts left: {remaining}"
            )

    print("[!] Access denied.")
    sys.exit(1)


def clean_number(number):

    number = number.strip()

    cleaned = re.sub(r"[^\d+]", "", number)

    if cleaned.startswith("+"):
        digits = cleaned[1:]
    else:
        digits = cleaned

    if not digits.isdigit():
        return None

    if not 7 <= len(digits) <= 15:
        return None

    return cleaned


def lookup(number):

    url = API_URL.format(number=number)

    print("\n[*] Sending authorized API request...")
    print("[*] HTTP endpoint:", url)

    try:

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "NumberLookupTool/1.1",
                "Accept": "application/json"
            }
        )

        print(f"[+] HTTP Status: {response.status_code}")

        try:

            data = response.json()

            print("\n========== RESULT ==========")

            print(
                json.dumps(
                    data,
                    indent=4,
                    ensure_ascii=False
                )
            )

            print("============================")

        except ValueError:

            print("\n========== RESPONSE ==========")
            print(response.text)
            print("==============================")

    except requests.exceptions.Timeout:

        print("[!] API request timed out.")

    except requests.exceptions.ConnectionError:

        print("[!] Could not connect to API.")

    except requests.exceptions.RequestException as error:

        print("[!] Request error:", error)


def main():

    banner()

    login()

    while True:

        number = input(
            "\nEnter phone number (q = quit): "
        )

        if number.lower() == "q":

            print("Bye!")
            break

        number = clean_number(number)

        if not number:

            print("[!] Invalid phone number.")
            continue

        lookup(number)


if name == "main":
    main()
