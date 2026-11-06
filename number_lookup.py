
#!/usr/bin/env python3

import os
import sys
import json
import re
import getpass
import hashlib
import requests
from datetime import datetime

from config import API_URL, PASSWORD_HASH

# ==========================================
# WOLF OSINT | NUMBER LOOKUP TOOL V2.0
# ==========================================

VERSION = "2.0"

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"


history = []


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def banner():

    print(f"""
{CYAN}{BOLD}
╔══════════════════════════════════════════╗
║                                          ║
║       NARESH // WOLF OSINT               ║
║                                          ║
║          NUMBER LOOKUP TOOL              ║
║                                          ║
║              VERSION {VERSION}                ║
║                                          ║
╚══════════════════════════════════════════╝
{MAGENTA}       ADVANCED OSINT TERMINAL{RESET}
""")


def login():

    print(f"{YELLOW}[ SECURITY AUTHENTICATION ]{RESET}")

    for attempt in range(3):

        password = getpass.getpass("Enter Password: ")

        entered_hash = hashlib.sha256(
            password.encode("utf-8")
        ).hexdigest()

        if entered_hash == PASSWORD_HASH:

            print(f"\n{GREEN}[+] Access Granted!{RESET}")
            return

        print(f"{RED}[!] Invalid Password.{RESET}")

    print(f"{RED}[!] Access Denied.{RESET}")
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


def show_result(data):

    print(f"\n{MAGENTA}{BOLD}")
    print("========== LOOKUP RESULT ==========")
    print(RESET)

    print(
        f"{WHITE}" +
        json.dumps(
            data,
            indent=4,
            ensure_ascii=False
        ) +
        RESET
    )

    print(f"{MAGENTA}==================================={RESET}")


def lookup(number):

    url = API_URL.format(number=number)

    print(f"\n{CYAN}[*] Connecting to API...{RESET}")

    try:

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "Naresh-WolfOSINT/2.0",
                "Accept": "application/json"
            }
        )

        print(
            f"{GREEN}[+] HTTP STATUS: "
            f"{response.status_code}{RESET}"
        )

        response.raise_for_status()

        try:
            data = response.json()

        except ValueError:

            print(f"{YELLOW}[!] API returned non-JSON response.{RESET}")
            print(response.text[:10000])
            return

        show_result(data)

        history.append({
            "number": number,
            "time": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "status": response.status_code
        })

    except requests.exceptions.Timeout:

        print(f"{RED}[!] API Request Timed Out.{RESET}")

    except requests.exceptions.HTTPError as error:

        print(f"{RED}[!] HTTP Error: {error}{RESET}")

    except requests.exceptions.ConnectionError:

        print(f"{RED}[!] API Connection Failed.{RESET}")

    except requests.exceptions.RequestException as error:

        print(f"{RED}[!] Request Error: {error}{RESET}")


def show_history():

    print(f"\n{MAGENTA}========== LOOKUP HISTORY =========={RESET}")

    if not history:

        print(f"{YELLOW}No lookup history available.{RESET}")
        return

    for index, item in enumerate(history, 1):

        print(
            f"{GREEN}{index}.{RESET} "
            f"Number: {item['number']} | "
            f"Time: {item['time']} | "
            f"Status: {item['status']}"
        )


def help_menu():

    print(f"""
{CYAN}========== HELP MENU =========={RESET}

1. Enter a valid phone number.
2. API request will be processed.
3. JSON response will be displayed.

COMMANDS:

help     - Show help
history  - Show session history
clear    - Clear terminal
q        - Exit application

{YELLOW}Use only authorized API services
and data you have permission to access.{RESET}
""")


def main():

    clear()
    banner()

    login()

    while True:

        print(f"""
{CYAN}========== MAIN MENU =========={RESET}

{GREEN}[1]{WHITE} Number Lookup
{GREEN}[2]{WHITE} Lookup History
{GREEN}[3]{WHITE} Help
{GREEN}[4]{WHITE} Clear Screen
{GREEN}[5]{WHITE} Exit

{CYAN}==============================={RESET}
""")

        choice = input(
            f"{YELLOW}WOLF OSINT >> {RESET}"
        ).strip().lower()

        if choice in ("1", "lookup"):

            number = input(
                "Enter Phone Number: "
            )

            if number.lower() == "q":
                continue

            number = clean_number(number)

            if not number:

                print(f"{RED}[!] Invalid Phone Number.{RESET}")
                continue

            lookup(number)

        elif choice in ("2", "history"):

            show_history()

        elif choice in ("3", "help"):

            help_menu()

        elif choice in ("4", "clear"):

            clear()
            banner()

        elif choice in ("5", "q", "exit"):

            print(f"{GREEN}[+] WOLF OSINT Shutdown.{RESET}")
            break

        else:

            print(f"{RED}[!] Invalid Option.{RESET}")


if __name__ == "__main__":
    main()
