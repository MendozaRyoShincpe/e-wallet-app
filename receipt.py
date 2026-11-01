import os
import json
import tempfile
import tkinter as tk
from tkinter import messagebox, ttk
from decimal import Decimal
from datetime import datetime

# ---------- CICO Theme ----------

# Define the colors used by the receipt and history windows
PURPLE = "#7040E8"
DARK_PURPLE = "#5930C7"
WHITE = "#FFFFFF"
BLACK = "#171A35"
BG = "#F8F7FF"
GRAY = "#777C91"
BORDER = "#E2E0ED"

# ---------- Database Path ----------

# receipt.py is directly inside the e-wallet-app folder.
BASE = os.path.dirname(os.path.abspath(__file__))

# Define the location of the transaction history database
DATABASE_DIR = os.path.join(BASE, "database")
HISTORY_FILE = os.path.join(
    DATABASE_DIR,
    "transaction_history.json"
)

# Define the date and time format used in receipts
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ---------- Account Information ----------

def get_account_info(wallet):
    """Return the logged-in user's account name and number."""

    # Retrieve the logged-in user's account details
    name = getattr(wallet, "account_name", None)
    number = getattr(wallet, "account_number", None)

    # Ensure an active wallet account is available
    if not name or not number:
        raise ValueError("No user is currently logged in.")

    return name, str(number)


# ---------- Receipt History Storage ----------

def _load_history():
    # Return an empty dictionary if no history file exists
    if not os.path.exists(HISTORY_FILE):
        return {}

    # Read and validate the saved JSON transaction history
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Invalid receipt history format.")

        return data

    except (json.JSONDecodeError, ValueError, OSError) as error:
        # Report an error if the history file cannot be read
        raise ValueError(
            "Receipt history could not be read. "
            "Please check database/transaction_history.json."
        ) from error


def _write_history(history):
    # Create the database directory if it does not exist
    os.makedirs(DATABASE_DIR, exist_ok=True)

    # Create a temporary file for safe database updating
    fd, temp_path = tempfile.mkstemp(
        dir=DATABASE_DIR,
        suffix=".tmp"
    )

    try:
        # Write the updated receipt history into the temporary file
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(
                history,
                file,
                indent=4,
                ensure_ascii=False
            )

        # Replace the old history file with the updated file
        os.replace(temp_path, HISTORY_FILE)

    except Exception:
        # Remove the temporary file if saving fails
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def save_receipt(receipt):
    """Save a receipt under the owner's account number."""

    # Load existing receipt history
    history = _load_history()

    # Identify the account that owns the receipt
    account_number = str(receipt["account_number"])

    # Add the new receipt to the account's transaction records
    history.setdefault(account_number, []).append(receipt)

    # Save the updated receipt history
    _write_history(history)


def get_receipts(account_number):
    """Return the account's receipts, newest first."""

    # Retrieve all receipts belonging to the specified account
    history = _load_history()

    # Reverse the list to display the newest receipt first
    return list(
        reversed(history.get(str(account_number), []))
    )


# ---------- Receipt Creation ----------

def create_receipt(
    wallet,
    transaction,
    remaining_balance,
    details=""
):
    # Retrieve the current user's account information
    name, number = get_account_info(wallet)

    # Build a dictionary containing the transaction receipt details
    return {
        "account_name": name,
        "account_number": number,
        "amount": str(transaction["amount"]),
        "transaction_type": transaction["type"],
        "date": transaction.get(
            "date",
            datetime.now().strftime(DATE_FORMAT)
        ),
        "reference": str(transaction["reference"]),
        "remaining_balance": str(remaining_balance),
        "details": details or transaction.get("description", "")
    }


# ---------- Formatting ----------

def _peso(value):
    # Convert monetary values into Philippine peso currency format
    return f"₱{Decimal(str(value)):,.2f}"


# ---------- Receipt Window ----------

class ReceiptWindow(tk.Toplevel):

    # Define the receipt fields and their corresponding formatters
    FIELDS = (
        ("Account Name", "account_name", str),
        ("Account Number", "account_number", str),
        ("Transaction Amount", "amount", _peso),
        ("Transaction Type", "transaction_type", str),
        ("Date & Time", "date", str),
        ("Reference Number", "reference", str),
        ("Remaining Balance", "remaining_balance", _peso)
    )

    def __init__(
        self,
        parent,
        receipt,
        title="Transaction Receipt",
        heading="Transaction Successful"
    ):
        # Initialize a separate receipt window
        super().__init__(parent)

        self.title(title)
        self.configure(bg=BG)
        self.resizable(False, False)
        self.transient(parent)

        # Create the main receipt card
        card = tk.Frame(
            self,
            bg=WHITE,
            padx=24,
            pady=20,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        card.pack(padx=20, pady=20)

        # Display the application name and receipt heading
        tk.Label(
            card,
            text="CICO Wallet",
            font=("Arial", 16, "bold"),
            bg=WHITE,
            fg=PURPLE
        ).pack()

        tk.Label(
            card,
            text=heading,
            font=("Arial", 10),
            bg=WHITE,
            fg=GRAY
        ).pack(pady=(2, 10))

        # Add a separator between the heading and receipt details
        ttk.Separator(card).pack(
            fill="x",
            pady=(0, 10)
        )

        # Create a frame for displaying receipt information
        rows = tk.Frame(card, bg=WHITE)
        rows.pack(fill="x")
        rows.columnconfigure(1, weight=1)

        # Generate receipt rows using the predefined field settings
        for i, (label, key, formatter) in enumerate(self.FIELDS):

            tk.Label(
                rows,
                text=label,
                font=("Arial", 9),
                bg=WHITE,
                fg=GRAY,
                anchor="w"
            ).grid(
                row=i,
                column=0,
                sticky="w",
                pady=4,
                padx=(0, 24)
            )

            tk.Label(
                rows,
                text=formatter(receipt[key]),
                font=("Arial", 10, "bold"),
                bg=WHITE,
                fg=BLACK,
                anchor="e"
            ).grid(
                row=i,
                column=1,
                sticky="e",
                pady=4
            )

        # Display additional transaction details when available
        if receipt.get("details"):
            ttk.Separator(card).pack(
                fill="x",
                pady=(10, 6)
            )

            tk.Label(
                card,
                text=receipt["details"],
                font=("Arial", 9),
                bg=WHITE,
                fg=GRAY,
                wraplength=320,
                justify="left"
            ).pack(anchor="w")

        # Add a button for closing the receipt window
        tk.Button(
            card,
            text="Close",
            command=self.destroy,
            bg=PURPLE,
            activebackground=DARK_PURPLE,
            fg=WHITE,
            activeforeground=WHITE,
            relief="flat",
            font=("Arial", 10, "bold"),
            pady=6,
            cursor="hand2"
        ).pack(
            fill="x",
            pady=(16, 0)
        )

        # Allow the Escape key to close the receipt window
        self.bind("<Escape>", lambda event: self.destroy())

        self.update_idletasks()

        # Center the receipt window relative to its parent.
        x = parent.winfo_rootx() + (
            parent.winfo_width() - self.winfo_width()
        ) // 2

        y = parent.winfo_rooty() + (
            parent.winfo_height() - self.winfo_height()
        ) // 2

        self.geometry(f"+{max(0, x)}+{max(0, y)}")

        # Make the receipt window modal and bring it into focus
        self.grab_set()
        self.focus_set()


# ---------- Issue Receipt ----------

def issue_receipt(
    parent,
    wallet,
    transaction_type,
    amount,
    remaining_balance,
    details="",
    heading="Transaction Successful"
):
    """Create, save, and display the latest transaction receipt."""

    # Retrieve the wallet's transaction records
    transactions = wallet.get_transactions()

    if not transactions:
        messagebox.showerror(
            "Receipt Error",
            "No transaction record was found.",
            parent=parent
        )
        return

    # Get the most recent transaction
    latest_transaction = transactions[-1]

    # Generate the receipt using the latest transaction details
    receipt = create_receipt(
        wallet,
        latest_transaction,
        remaining_balance,
        details
    )

    # Attempt to save the receipt before displaying it
    try:
        save_receipt(receipt)

    except (OSError, ValueError) as error:
        messagebox.showwarning(
            "Receipt Not Saved",
            "The transaction was successful, but the receipt "
            f"could not be saved:\n{error}",
            parent=parent
        )

    # Display the generated receipt in a separate window
    window = ReceiptWindow(
        parent,
        receipt,
        heading=heading
    )

    parent.wait_window(window)


# ---------- Transaction History Window ----------

class TransactionHistory(tk.Toplevel):
    """Displays the logged-in user's saved receipts."""

    def __init__(self, parent, wallet):
        # Initialize the transaction history window
        super().__init__(parent)

        self.title("Receipt History")
        self.configure(bg=BG)
        self.minsize(600, 350)
        self.transient(parent)

        # Retrieve the current user's account information
        name, self.account_number = get_account_info(wallet)

        # Load the receipts belonging to the logged-in account
        try:
            self.receipts = get_receipts(self.account_number)

        except ValueError as error:
            messagebox.showerror(
                "History Error",
                str(error),
                parent=self
            )
            self.receipts = []

        # Display the history window title and account information
        tk.Label(
            self,
            text="Receipt History",
            font=("Arial", 16, "bold"),
            bg=BG,
            fg=BLACK
        ).pack(
            anchor="w",
            padx=14,
            pady=(14, 0)
        )

        tk.Label(
            self,
            text=f"{name}  ·  {self.account_number}",
            font=("Arial", 9),
            bg=BG,
            fg=GRAY
        ).pack(anchor="w", padx=14)

        # Display a message if the account has no saved receipts
        if not self.receipts:
            tk.Label(
                self,
                text="No receipts yet.\n"
                     "Your receipts will appear here "
                     "after your first transaction.",
                font=("Arial", 10),
                bg=BG,
                fg=GRAY,
                justify="center"
            ).pack(
                expand=True,
                pady=40
            )

            return

        # Create the table container for transaction records
        table = tk.Frame(self, bg=BG)
        table.pack(
            fill="both",
            expand=True,
            padx=14,
            pady=(10, 4)
        )

        # Define the columns displayed in the transaction history
        columns = (
            "date",
            "type",
            "amount",
            "reference"
        )

        self.tree = ttk.Treeview(
            table,
            columns=columns,
            show="headings",
            height=12
        )

        # Configure the heading labels and column widths
        column_settings = (
            ("date", "Date & Time", 160),
            ("type", "Type", 110),
            ("amount", "Amount", 110),
            ("reference", "Reference", 190)
        )

        for column, heading, width in column_settings:
            self.tree.heading(column, text=heading)

            self.tree.column(
                column,
                width=width,
                anchor="w"
            )

        # Add a scrollbar for navigating transaction records
        scrollbar = ttk.Scrollbar(
            table,
            orient="vertical",
            command=self.tree.yview
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # Insert saved receipts into the transaction history table
        for index, receipt in enumerate(self.receipts):
            self.tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    receipt["date"],
                    receipt["transaction_type"],
                    _peso(receipt["amount"]),
                    receipt["reference"]
                )
            )

        # Inform the user that receipts can be opened by double-clicking
        tk.Label(
            self,
            text="Double-click a row to open its receipt.",
            bg=BG,
            fg=GRAY,
            font=("Arial", 8)
        ).pack(pady=(0, 10))

        # Connect double-click events to the receipt-opening function
        self.tree.bind(
            "<Double-1>",
            self._open_selected
        )

    def _open_selected(self, event):
        # Retrieve the selected transaction from the table
        selected = self.tree.selection()

        if selected:
            receipt = self.receipts[int(selected[0])]

            # Open the selected transaction's receipt
            ReceiptWindow(
                self,
                receipt,
                title="Receipt",
                heading="Transaction Receipt"
            )