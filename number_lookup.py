#!/usr/bin/env python3

import json
import re
import sys
import getpass
import requests

from config import API_URL, PASSWORD_KEY


# ==============================
# 🎨 COLORS
# ==============================
RESET = "\033[0m"
BOLD = "\033[1m"

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"


def banner():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════╗
║       {MAGENTA}NUMBER LOOKUP TOOL v1.0{CYAN}        ║
║          {YELLOW}NARESH_OSINT{CYAN}                ║
╚══════════════════════════════════════╝{RESET}
""")


def login():
    print(f"{BLUE}{BOLD}🔐 Password Protected{RESET}")

    for attempt in range(3):
        password = getpass.getpass(
            f"{YELLOW}Password: {RESET}"
        )

        if password == PASSWORD_KEY:
            print(f"{GREEN}[+] Access granted.{RESET}\n")
            return True

        remaining = 2 - attempt
        print(
            f"{RED}[!] Wrong password. "
            f"Attempts left: {remaining}{RESET}"
        )

    print(f"{RED}[!] Access denied.{RESET}")
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

    # API URL is intentionally NOT displayed
    print(f"\n{CYAN}[*] Sending authorized API request...{RESET}")

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "NumberLookupTool/1.0"
            }
        )

        print(
            f"{GREEN}[+] HTTP Status: "
            f"{response.status_code}{RESET}"
        )

        try:
            data = response.json()

            print(
                f"\n{MAGENTA}{BOLD}"
                f"========== RESULT =========="
                f"{RESET}"
            )

            print(
                f"{WHITE}"
                + json.dumps(
                    data,
                    indent=4,
                    ensure_ascii=False
                )
                + f"{RESET}"
            )

            print(
                f"{MAGENTA}{BOLD}"
                f"============================"
                f"{RESET}"
            )

        except ValueError:
            print(
                f"\n{YELLOW}{BOLD}"
                f"========== RESPONSE =========="
                f"{RESET}"
            )

            print(f"{WHITE}{response.text}{RESET}")

            print(
                f"{YELLOW}{BOLD}"
                f"=============================="
                f"{RESET}"
            )

    except requests.exceptions.Timeout:
        print(
            f"{RED}[!] API request timed out.{RESET}"
        )

    except requests.exceptions.ConnectionError:
        print(
            f"{RED}[!] Could not connect to API.{RESET}"
        )

    except requests.exceptions.RequestException as error:
        print(
            f"{RED}[!] Request error: "
            f"{error}{RESET}"
        )


def main():
    banner()
    login()

    while True:
        number = input(
            f"\n{CYAN}{BOLD}"
            f"Enter phone number"
            f"{RESET} "
            f"{YELLOW}(q = quit): {RESET}"
        )

        if number.lower() == "q":
            print(f"{GREEN}Bye! 👋{RESET}")
            break

        number = clean_number(number)

        if not number:
            print(
                f"{RED}[!] Invalid phone number.{RESET}"
            )
            continue

        lookup(number)


if __name__ == "__main__":
    main()

