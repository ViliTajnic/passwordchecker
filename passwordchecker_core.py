import hashlib
from pathlib import Path
from urllib import error, request


APP_NAME = "Password Checker"
APP_VERSION = "2.1"
API_URL = "https://api.pwnedpasswords.com/range/{}"
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


def collect_direct_passwords(passwords):
    return [
        (f"Password {index}", password)
        for index, password in enumerate(passwords, start=1)
    ]


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


def check_password_entries(entries):
    return [(label, pwned_api_check(password)) for label, password in entries]
