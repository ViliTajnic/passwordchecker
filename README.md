# Password Checker v2

Password Checker v2 checks whether a password appears in the Have I Been Pwned password database.

It uses the k-anonymity range API:
- Your full password is never sent over the internet.
- The script only sends the first 5 characters of the SHA-1 hash.
- The match happens locally on your computer.

## Why v2 is easier to use

Version 2 is designed for normal terminal users, not just programmers:
- Hidden password entry when you run it without arguments
- Clearer messages
- Better error handling
- Batch checking from a text file
- No external Python packages required

## Requirements

- Python 3
- Internet connection

This version uses only the Python standard library, so you do not need to install `requests`.

## Quick start

Run the script:

```bash
python3 checkmypass.py
```

You will be prompted to enter a password privately. It will not be shown on screen while you type.

## Usage

Show help:

```bash
python3 checkmypass.py --help
```

Check one password interactively:

```bash
python3 checkmypass.py
```

Check one or more passwords directly from the command line:

```bash
python3 checkmypass.py password1 password2
```

This works, but it is less safe because command history may store the password.

Check passwords from a file:

```bash
python3 checkmypass.py --file passwords.txt
```

The file should contain one password per line.

## Example output

```text
Password Checker v2.0
Checking 1 password(s)...
Password 1: found in known breach data 52,256,179 times. Do not use this password.
Check completed successfully.
```

If a password is not found, the script will say so, but that does not guarantee the password is strong. A long, unique password is still the right choice.

## Standalone executables

This repo can now build standalone command-line executables for macOS and Windows.

Local macOS build:

```bash
./scripts/build_macos.sh
```

The executable will be created at `dist/passwordchecker`.

Local Windows build:

```powershell
.\scripts\build_windows.ps1
```

The executable will be created at `dist\passwordchecker.exe`.

Windows binaries should be built on Windows, and macOS binaries should be built on macOS. For that reason, the repo also includes a GitHub Actions workflow that builds both platforms automatically on native runners.

GitHub Actions output:
- `passwordchecker-macos`
- `passwordchecker-windows`

## Notes

- If the API cannot be reached, the script prints a plain-language error message.
- Empty lines in a password file are ignored.
- Direct command-line passwords are supported for convenience, but interactive mode is the safest option.
