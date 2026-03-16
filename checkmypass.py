#!/usr/bin/env python3
import argparse
import getpass
import hashlib
import sys
from pathlib import Path
from urllib import error, request


API_URL = "https://api.pwnedpasswords.com/range/{}"
APP_VERSION = "2.0"
REQUEST_HEADERS = {
    "User-Agent": f"passwordchecker/{APP_VERSION}",
    "Add-Padding": "true",
}


def request_api_data(query_char):
    req = request.Request(API_URL.format(query_char), headers=REQUEST_HEADERS)
    try:
        with request.urlopen(req, timeout=10) as response:
            if response.status != 200:
                raise RuntimeError(
                    f"Password API returned status {response.status}. Please try again later."
                )
            return response.read().decode("utf-8")
    except error.HTTPError as exc:
        raise RuntimeError(
            f"Password API returned status {exc.code}. Please try again later."
        ) from exc
    except error.URLError as exc:
        raise RuntimeError(
            "Could not reach the password API. Check your internet connection and try again."
        ) from exc


def get_password_leaks_count(response_text, hash_to_check):
    for line in response_text.splitlines():
        hash_suffix, _, count = line.partition(":")
        if hash_suffix == hash_to_check:
            return int(count)
    return 0


def pwned_api_check(password):
    sha1password = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    first5_char, tail = sha1password[:5], sha1password[5:]
    response_text = request_api_data(first5_char)
    return get_password_leaks_count(response_text, tail)


def prompt_for_password():
    prompt = "Enter the password to check: "

    if sys.stdin.isatty():
        while True:
            password = getpass.getpass(prompt)
            if password:
                return password
            print("Password cannot be empty. Please try again.")

    password = sys.stdin.readline().rstrip("\r\n")
    if not password:
        raise ValueError("No password was provided on standard input.")
    return password


def read_passwords_from_file(file_path):
    path = Path(file_path)
    if not path.is_file():
        raise ValueError(f"Password file not found: {file_path}")

    entries = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            password = raw_line.rstrip("\r\n")
            if password:
                entries.append((f"Line {line_number}", password))

    if not entries:
        raise ValueError("The password file does not contain any non-empty lines.")
    return entries


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description=(
            "Check whether passwords appear in known data breaches using the "
            "Have I Been Pwned range API."
        )
    )
    parser.add_argument(
        "passwords",
        nargs="*",
        help="Passwords to check directly. Avoid this on shared systems because shell history may store them.",
    )
    parser.add_argument(
        "-f",
        "--file",
        help="Check passwords from a text file, one password per line.",
    )
    parser.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help="Prompt for a password without showing it on screen.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {APP_VERSION}",
    )
    return parser.parse_args(argv)


def collect_passwords(args):
    if args.file and args.passwords:
        raise ValueError("Use either direct passwords or --file, not both.")
    if args.interactive and (args.file or args.passwords):
        raise ValueError("Use --interactive by itself.")

    if args.file:
        return read_passwords_from_file(args.file)
    if args.passwords:
        return [(f"Password {index}", password) for index, password in enumerate(args.passwords, start=1)]
    return [("Password 1", prompt_for_password())]


def format_result(label, count):
    if count:
        return (
            f"{label}: found in known breach data {count:,} times. "
            "Do not use this password."
        )
    return (
        f"{label}: not found in the breach corpus checked by this tool. "
        "It may still be weak, so use a long, unique password."
    )


def main(argv):
    try:
        args = parse_args(argv)
        passwords_to_check = collect_passwords(args)
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    print(f"Password Checker v{APP_VERSION}")
    print(f"Checking {len(passwords_to_check)} password(s)...")

    try:
        for label, password in passwords_to_check:
            count = pwned_api_check(password)
            print(format_result(label, count))
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Check completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
