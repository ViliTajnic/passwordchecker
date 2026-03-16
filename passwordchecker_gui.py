#!/usr/bin/env python3
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from passwordchecker_core import (
    APP_NAME,
    APP_VERSION,
    check_password_entries,
    format_result,
    read_passwords_from_file,
)


class PasswordCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_NAME} Desktop")
        self.root.geometry("720x520")
        self.root.minsize(640, 460)

        self.result_queue = queue.Queue()
        self.worker = None

        self.password_var = tk.StringVar()
        self.file_var = tk.StringVar(value="No file selected")
        self.status_var = tk.StringVar(
            value="Enter one password or choose a file with one password per line."
        )

        self._build_ui()
        self.root.after(150, self._poll_result_queue)

    def _build_ui(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        frame = ttk.Frame(self.root, padding=18)
        frame.grid(sticky="nsew")
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(5, weight=1)

        title = ttk.Label(
            frame,
            text=f"{APP_NAME} v{APP_VERSION}",
            font=("Helvetica", 20, "bold"),
        )
        title.grid(row=0, column=0, sticky="w")

        intro = ttk.Label(
            frame,
            text=(
                "Checks passwords against known breach data using the Have I Been "
                "Pwned range API. Your full password is never sent."
            ),
            wraplength=660,
            justify="left",
        )
        intro.grid(row=1, column=0, sticky="ew", pady=(8, 18))

        single_frame = ttk.LabelFrame(frame, text="Check one password", padding=14)
        single_frame.grid(row=2, column=0, sticky="ew")
        single_frame.columnconfigure(0, weight=1)

        password_entry = ttk.Entry(
            single_frame,
            textvariable=self.password_var,
            show="*",
        )
        password_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        password_entry.bind("<Return>", self._check_single_password)

        check_button = ttk.Button(
            single_frame,
            text="Check Password",
            command=self._check_single_password,
        )
        check_button.grid(row=0, column=1, sticky="e")

        file_frame = ttk.LabelFrame(frame, text="Check a file", padding=14)
        file_frame.grid(row=3, column=0, sticky="ew", pady=(16, 0))
        file_frame.columnconfigure(0, weight=1)

        file_label = ttk.Label(
            file_frame,
            textvariable=self.file_var,
            wraplength=540,
            justify="left",
        )
        file_label.grid(row=0, column=0, sticky="w")

        file_buttons = ttk.Frame(file_frame)
        file_buttons.grid(row=0, column=1, sticky="e", padx=(12, 0))

        choose_button = ttk.Button(
            file_buttons,
            text="Choose File",
            command=self._choose_file,
        )
        choose_button.grid(row=0, column=0, padx=(0, 8))

        file_check_button = ttk.Button(
            file_buttons,
            text="Check File",
            command=self._check_file_passwords,
        )
        file_check_button.grid(row=0, column=1)

        status = ttk.Label(frame, textvariable=self.status_var, foreground="#1f4f3f")
        status.grid(row=4, column=0, sticky="w", pady=(16, 8))

        self.output = ScrolledText(frame, wrap="word", height=14, state="disabled")
        self.output.grid(row=5, column=0, sticky="nsew")

        footer = ttk.Label(
            frame,
            text="Tip: direct command-line passwords are less private than this desktop UI.",
            foreground="#555555",
        )
        footer.grid(row=6, column=0, sticky="w", pady=(12, 0))

    def _choose_file(self):
        file_path = filedialog.askopenfilename(
            title="Choose password file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if file_path:
            self.file_var.set(file_path)
            self.status_var.set("File selected. Click 'Check File' to run the scan.")

    def _check_single_password(self, event=None):
        password = self.password_var.get()
        if not password:
            messagebox.showwarning(APP_NAME, "Enter a password first.")
            return

        self._start_background_check([("Password 1", password)], clear_password=True)

    def _check_file_passwords(self):
        file_path = self.file_var.get()
        if file_path == "No file selected":
            messagebox.showwarning(APP_NAME, "Choose a file first.")
            return

        try:
            entries = read_passwords_from_file(file_path)
        except ValueError as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return

        self._start_background_check(entries, source=Path(file_path).name)

    def _start_background_check(self, entries, clear_password=False, source=None):
        if self.worker and self.worker.is_alive():
            messagebox.showinfo(APP_NAME, "A check is already running.")
            return

        if clear_password:
            self.password_var.set("")

        self._set_output("")
        count = len(entries)
        target = source or "interactive input"
        self.status_var.set(f"Checking {count} password(s) from {target}...")

        self.worker = threading.Thread(
            target=self._run_check,
            args=(entries,),
            daemon=True,
        )
        self.worker.start()

    def _run_check(self, entries):
        try:
            results = check_password_entries(entries)
            lines = [f"{APP_NAME} v{APP_VERSION}", ""]
            for label, count in results:
                lines.append(format_result(label, count))
            lines.append("")
            lines.append("Check completed successfully.")
            self.result_queue.put(("success", "\n".join(lines)))
        except RuntimeError as exc:
            self.result_queue.put(("error", str(exc)))

    def _poll_result_queue(self):
        try:
            status, payload = self.result_queue.get_nowait()
        except queue.Empty:
            self.root.after(150, self._poll_result_queue)
            return

        if status == "success":
            self._set_output(payload)
            self.status_var.set("Finished.")
        else:
            self._set_output(f"Error: {payload}")
            self.status_var.set("Check failed.")
            messagebox.showerror(APP_NAME, payload)

        self.root.after(150, self._poll_result_queue)

    def _set_output(self, text):
        self.output.configure(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", text)
        self.output.configure(state="disabled")


def main():
    root = tk.Tk()
    PasswordCheckerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
