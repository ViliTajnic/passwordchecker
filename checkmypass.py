#!/usr/bin/env python3
import argparse
import getpass
import sys

from passwordchecker_core import (
    APP_NAME,
    APP_VERSION,
    check_password_entries,
    collect_direct_passwords,
    format_result,
    read_passwords_from_file,
)


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
        return collect_direct_passwords(args.passwords)
    return [("Password 1", prompt_for_password())]


def main(argv):
    try:
        args = parse_args(argv)
        passwords_to_check = collect_passwords(args)
    except ValueError as exc:
        print(f"Input error: {exc}", file=sys.stderr)
        return 2

    print(f"{APP_NAME} v{APP_VERSION}")
    print(f"Checking {len(passwords_to_check)} password(s)...")

    try:
        for label, count in check_password_entries(passwords_to_check):
            print(format_result(label, count))
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print("Check completed successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
