import json
import os
import tempfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import session
from ui.theme import (
    BG, WHITE, BLACK, GRAY, PURPLE, apply_icon, center_on, safe_grab
)


# History is stored as {account_number: [receipt, receipt, ...]}
HISTORY_FILE = Path(__file__).resolve().parent / "data" / "transaction_history.json"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ------- USER's ACCOUNT INFO -------
def get_account_info(wallet=None):
    """Return (account_name, account_number) of the logged-in user."""
    user = session.get_user()
    if not user:
        raise ValueError("No user is logged in.")
    return user["account_name"], user["account_number"]


# ------- USER's STORAGE of transaction history -------
def _load_history():
    if not HISTORY_FILE.exists():
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError("Unexpected history format.")
        return data
    except (json.JSONDecodeError, ValueError):
        # Keep the unreadable file instead of overwriting it.
        backup = HISTORY_FILE.with_suffix(
            f".corrupt-{datetime.now():%Y%m%d%H%M%S}.json"
        )
        os.replace(HISTORY_FILE, backup)
        return {}

# ------ RECEIPT CREATION, STORAGE, AND DISPLAY -------
def _write_history(history):
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=HISTORY_FILE.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, HISTORY_FILE)  # atomic swap
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def save_receipt(receipt):
    """Append a receipt under its owner's account number."""
    history = _load_history()
    history.setdefault(receipt["account_number"], []).append(receipt)
    _write_history(history)


def get_receipts(account_number):
    """Return the given account's receipts, newest first."""
    return list(reversed(_load_history().get(str(account_number), [])))


def create_receipt(wallet, transaction_type, amount, reference,
                   remaining_balance, details=""):
    name, number = get_account_info(wallet)
    return {
        "account_name": name,
        "account_number": number,
        "amount": str(amount),
        "transaction_type": transaction_type,
        "date": datetime.now().strftime(DATE_FORMAT),
        "reference": str(reference),
        "remaining_balance": str(remaining_balance),
        "details": details,
    }


# --------- RECEIPT DISPLAY -------
def _peso(value):
    return f"₱{Decimal(value):,.2f}"


class ReceiptWindow(tk.Toplevel):
    FIELDS = (  # (label, receipt key, formatter) in display order
        ("Account Name", "account_name", str),
        ("Account Number", "account_number", str),
        ("Transaction Amount", "amount", _peso),
        ("Transaction Type", "transaction_type", str),
        ("Date & Time", "date", str),
        ("Reference Number", "reference", str),
        ("Remaining Balance", "remaining_balance", _peso),
    )

    def __init__(self, parent, receipt, title="Transaction Receipt",
                 heading="Transaction Successful"):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.transient(parent)
        apply_icon(self)

        card = tk.Frame(self, bg=WHITE, padx=24, pady=20,
                        highlightbackground=GRAY, highlightthickness=1)
        card.pack(padx=20, pady=20)

        tk.Label(card, text="CICO Wallet", font=("Arial", 16, "bold"),
                 bg=WHITE, fg=PURPLE).pack()
        tk.Label(card, text=heading, font=("Arial", 10),
                 bg=WHITE, fg=GRAY).pack(pady=(2, 10))
        ttk.Separator(card).pack(fill="x", pady=(0, 10))

        rows = tk.Frame(card, bg=WHITE)
        rows.pack(fill="x")
        rows.columnconfigure(1, weight=1)

        for i, (label, key, fmt) in enumerate(self.FIELDS):
            tk.Label(rows, text=label, font=("Arial", 9), bg=WHITE,
                     fg=GRAY, anchor="w").grid(row=i, column=0, sticky="w",
                                               pady=4, padx=(0, 24))
            tk.Label(rows, text=fmt(receipt[key]), font=("Arial", 10, "bold"),
                     bg=WHITE, fg=BLACK, anchor="e").grid(row=i, column=1,
                                                          sticky="e", pady=4)

        if receipt.get("details"):
            ttk.Separator(card).pack(fill="x", pady=(10, 6))
            tk.Label(card, text=receipt["details"], font=("Arial", 9),
                     bg=WHITE, fg=GRAY, wraplength=320,
                     justify="left").pack(anchor="w")

        tk.Button(card, text="Close", command=self.destroy, bg=PURPLE,
                  fg=WHITE, relief="flat", font=("Arial", 10, "bold"),
                  pady=6).pack(fill="x", pady=(16, 0))

        self.bind("<Escape>", lambda _e: self.destroy())
        center_on(self, parent)
        safe_grab(self)
        self.focus_set()


def issue_receipt(parent, wallet, transaction_type, amount,
                  remaining_balance, details="", heading="Transaction Successful"):
    """Build, save, and show a receipt for the wallet's latest transaction.

    Blocks until the receipt window is closed (same as the old message box).
    """
    reference = wallet.get_transactions()[-1]["reference"]
    receipt = create_receipt(wallet, transaction_type, amount, reference,
                             remaining_balance, details)
    try:
        save_receipt(receipt)
    except OSError as error:
        messagebox.showwarning(
            "Receipt Not Saved",
            f"The transaction succeeded, but its receipt could not be "
            f"saved to history:\n{error}",
            parent=parent
        )
    window = ReceiptWindow(parent, receipt, heading=heading)
    parent.wait_window(window)


# --------- TRANSACTION HISTORY WINDOW -------
class TransactionHistory(tk.Toplevel):
    """Lists the logged-in user's saved receipts, newest first."""

    def __init__(self, parent, wallet):
        super().__init__(parent)
        self.title("Receipt History")
        self.configure(bg=BG)
        self.minsize(560, 320)
        self.transient(parent)
        apply_icon(self)

        name, self.account_number = get_account_info(wallet)
        self.receipts = get_receipts(self.account_number)

        tk.Label(self, text="Receipt History", font=("Arial", 16, "bold"),
                 bg=BG, fg=BLACK).pack(anchor="w", padx=14, pady=(14, 0))
        tk.Label(self, text=f"{name}  ·  {self.account_number}",
                 font=("Arial", 9), bg=BG, fg=GRAY).pack(anchor="w", padx=14)

        if not self.receipts:
            tk.Label(self, text="No receipts yet.\nYour receipts will appear "
                     "here after your first transaction.",
                     font=("Arial", 10), bg=BG, fg=GRAY,
                     justify="center").pack(expand=True, pady=40)
            return

        table = tk.Frame(self, bg=BG)
        table.pack(fill="both", expand=True, padx=14, pady=(10, 4))

        columns = ("date", "type", "amount", "reference")
        self.tree = ttk.Treeview(table, columns=columns, show="headings",
                                 height=12)
        for col, text, width in (("date", "Date & Time", 150),
                                 ("type", "Type", 110),
                                 ("amount", "Amount", 110),
                                 ("reference", "Reference", 170)):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="w")

        scroll = ttk.Scrollbar(table, orient="vertical",
                               command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        for i, r in enumerate(self.receipts):
            self.tree.insert("", "end", iid=str(i), values=(
                r["date"], r["transaction_type"], _peso(r["amount"]),
                r["reference"]))

        tk.Label(self, text="Double-click a row to open its receipt.",
                 bg=BG, fg=GRAY, font=("Arial", 8)).pack(pady=(0, 10))
        self.tree.bind("<Double-1>", self._open_selected)

    def _open_selected(self, _event):
        selected = self.tree.selection()
        if selected:
            ReceiptWindow(self, self.receipts[int(selected[0])],
                          title="Receipt", heading="Transaction Receipt")
