
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
# WOLF OSINT NUMBER LOOKUP TOOL V2.1
# ==========================================

VERSION = "2.1"
HISTORY_FILE = "history.json"

# COLORS
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


def load_history():
    global history

    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as file:
                history = json.load(file)

    except (json.JSONDecodeError, OSError):
        history = []


def save_history():
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(history, file, indent=4, ensure_ascii=False)

    except OSError:
        print(f"{RED}[!] Unable to save history.{RESET}")


def banner():
    print(f"""
{CYAN}{BOLD}
╔══════════════════════════════════════════════╗
║                                              ║
║           NARESH // WOLF OSINT               ║
║                                              ║
║           NUMBER LOOKUP TOOL                ║
║                                              ║
║                  V2.1                       ║
║                                              ║
╚══════════════════════════════════════════════╝
{MAGENTA}           ADVANCED OSINT TERMINAL{RESET}
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


def print_json(data, indent=0):

    prefix = " " * indent

    if isinstance(data, dict):

        for key, value in data.items():

            print(
                f"{prefix}{CYAN}{BOLD}{key}{RESET}"
                f"{WHITE} : {RESET}",
                end=""
            )

            if isinstance(value, (dict, list)):
                print()
                print_json(value, indent + 4)
            else:
                print(
                    f"{GREEN}{json.dumps(value, ensure_ascii=False)}{RESET}"
                )

    elif isinstance(data, list):

        for index, value in enumerate(data, 1):

            print(f"{prefix}{YELLOW}[{index}]{RESET}")

            if isinstance(value, (dict, list)):
                print_json(value, indent + 4)
            else:
                print(f"{prefix}{GREEN}{value}{RESET}")

    else:
        print(f"{prefix}{GREEN}{data}{RESET}")


def show_result(data):

    print(f"""
{MAGENTA}{BOLD}
╔══════════════════════════════════════════════╗
║              LOOKUP RESULT                   ║
╚══════════════════════════════════════════════╝
{RESET}""")

    print_json(data)

    print(f"\n{MAGENTA}{'═' * 46}{RESET}")


def lookup(number):

    url = API_URL.format(number=number)

    print(f"\n{CYAN}[*] Connecting to API...{RESET}")

    try:

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent": "Naresh-WolfOSINT/2.1",
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
            print(f"{RED}[!] API returned non-JSON response.{RESET}")
            print(response.text[:5000])
            return

        show_result(data)

        history.append({
            "number": number,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": response.status_code
        })

        save_history()

    except requests.exceptions.Timeout:
        print(f"{RED}[!] API Request Timed Out.{RESET}")

    except requests.exceptions.HTTPError as error:
        print(f"{RED}[!] HTTP Error: {error}{RESET}")

    except requests.exceptions.ConnectionError:
        print(f"{RED}[!] API Connection Failed.{RESET}")

    except requests.exceptions.RequestException as error:
        print(f"{RED}[!] Request Error: {error}{RESET}")


def show_history():

    print(f"""
{MAGENTA}{BOLD}
╔══════════════════════════════════════════════╗
║                LOOKUP HISTORY                ║
╚══════════════════════════════════════════════╝
{RESET}""")

    if not history:
        print(f"{YELLOW}[!] No history available.{RESET}")
        return

    for index, item in enumerate(history, 1):

        print(
            f"{CYAN}{index}.{RESET} "
            f"{GREEN}Number:{RESET} {item.get('number', 'N/A')}  "
            f"{YELLOW}| Time:{RESET} {item.get('time', 'N/A')}  "
            f"{BLUE}| Status:{RESET} {item.get('status', 'N/A')}"
        )

    print(f"\n{MAGENTA}{'═' * 46}{RESET}")


def search_history():

    if not history:
        print(f"{YELLOW}[!] No history available.{RESET}")
        return

    query = input(
        f"\n{CYAN}Search Number: {RESET}"
    ).strip()

    if not query:
        print(f"{RED}[!] Enter a search value.{RESET}")
        return

    results = [
        item for item in history
        if query in str(item.get("number", ""))
    ]

    if not results:
        print(f"{RED}[!] No matching records found.{RESET}")
        return

    print(f"\n{GREEN}[+] {len(results)} Record(s) Found{RESET}")

    for index, item in enumerate(results, 1):

        print(f"""
{CYAN}Record {index}{RESET}
{GREEN}Number :{RESET} {item.get('number', 'N/A')}
{YELLOW}Time   :{RESET} {item.get('time', 'N/A')}
{BLUE}Status :{RESET} {item.get('status', 'N/A')}
""")


def history_menu():

    while True:

        print(f"""
{MAGENTA}========== HISTORY MENU =========={RESET}

{GREEN}[1]{WHITE} Show All History
{GREEN}[2]{WHITE} Search History
{GREEN}[3]{WHITE} Back to Main Menu

{MAGENTA}=================================={RESET}
""")

        choice = input(
            f"{YELLOW}WOLF HISTORY >> {RESET}"
        ).strip().lower()

        if choice in ("1", "show"):
            show_history()

        elif choice in ("2", "search"):
            search_history()

        elif choice in ("3", "back", "q"):
            break

        else:
            print(f"{RED}[!] Invalid Option.{RESET}")


def about():

    print(f"""
{CYAN}{BOLD}
╔══════════════════════════════════════════════╗
║                  ABOUT                       ║
╠══════════════════════════════════════════════╣
║                                              ║
║       PROJECT   : WOLF OSINT                 ║
║       TOOL      : NUMBER LOOKUP              ║
║       VERSION   : 2.1                        ║
║       DEVELOPER : NARESH                     ║
║       YEAR      : 2026                       ║
║                                              ║
╚══════════════════════════════════════════════╝
{MAGENTA}          ADVANCED OSINT TERMINAL{RESET}
""")


def main():

    clear()
    banner()
    login()
    load_history()

    while True:

        print(f"""
{CYAN}{BOLD}
╔══════════════════════════════════════════════╗
║                  MAIN MENU                   ║
╠══════════════════════════════════════════════╣
║                                              ║
║  {GREEN}[1]{WHITE} NUMBER LOOKUP             ║
║  {GREEN}[2]{WHITE} HISTORY                   ║
║  {GREEN}[3]{WHITE} ABOUT                     ║
║  {GREEN}[4]{WHITE} EXIT                      ║
║                                              ║
╚══════════════════════════════════════════════╝
{RESET}""")

        choice = input(
            f"{YELLOW}WOLF OSINT >> {RESET}"
        ).strip().lower()

        if choice in ("1", "lookup"):

            number = input(
                f"\n{CYAN}Enter Phone Number: {RESET}"
            )

            if number.lower() == "q":
                continue

            number = clean_number(number)

            if not number:
                print(f"{RED}[!] Invalid Phone Number.{RESET}")
                continue

            lookup(number)

        elif choice in ("2", "history"):
            history_menu()

        elif choice in ("3", "about"):
            about()

        elif choice in ("4", "q", "exit"):
            print(f"\n{GREEN}[+] WOLF OSINT Shutdown.{RESET}")
            break

        else:
            print(f"{RED}[!] Invalid Option.{RESET}")


if __name__ == "__main__":
    main()
