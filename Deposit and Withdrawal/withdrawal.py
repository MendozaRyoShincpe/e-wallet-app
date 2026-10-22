import os
import random
import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime
from decimal import Decimal, InvalidOperation
from tkinter import messagebox

# ---------- Constants ---------- 
PURPLE = "#7040E8"
DARK_PURPLE = "#5930C7"
WHITE = "#FFFFFF"
BLACK = "#171A35"
BG = "#F8F7FF"
DESTINATIONS = ["E-wallet", "Bank account", "Cash pickup", "Other"]
PASSWORD = "secure123"  
MAX_AMOUNT = Decimal("100000")

# Getting the file for the E-wallet's balance
BASE = os.path.dirname(os.path.abspath(__file__))
BALANCE_FILE = os.path.join(BASE, "wallet_balance.txt")
DEFAULT_BALANCE = Decimal("1000.00")


# Loading the Balance
def load_balance():
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as file:
            return Decimal(file.read().strip())
    except (FileNotFoundError, InvalidOperation, ValueError):
        return DEFAULT_BALANCE

# Saving the Balance
def save_balance(balance):
    with open(BALANCE_FILE, "w", encoding="utf-8") as file:
        file.write(f"{balance:.2f}")

# Class CashOut Function
class CashOut:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CICO - Cash Out")
        self.root.geometry("420x600")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        try:
            self.root.iconbitmap(os.path.join(BASE, "CICO.ico"))
        except Exception:
            print("Icon file not found.")

        self.balance = load_balance()
        self.destination = tk.StringVar(value=DESTINATIONS[0])
        self.account = tk.StringVar()
        self.amount = tk.StringVar()

        self.build_ui()
        self.root.mainloop()

    # Gui Implementation
    def build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(pady=18)

        try:
            img = Image.open(os.path.join(BASE, "CICO.png")).resize((40, 40))
            self.logo = ImageTk.PhotoImage(img)
            tk.Label(header, image=self.logo, bg=BG).pack(side="left", padx=(0, 10))
        except Exception as error:
            print("Logo error:", error)

        tk.Label(
            header, text="CICO WITHDRAWAL",
            font=("Arial", 18, "bold"), fg=PURPLE, bg=BG,
        ).pack(side="left")

        # Balance card
        card = tk.Frame(self.root, bg=WHITE, highlightbackground=PURPLE, highlightthickness=1)
        card.pack(fill="x", padx=30, pady=(0, 14))
        tk.Label(
            card, text="CURRENT WALLET BALANCE",
            font=("Arial", 9, "bold"), bg=WHITE, fg="gray",
        ).pack(pady=(10, 2))
        self.balance_label = tk.Label(
            card, text="", font=("Arial", 20, "bold"), bg=WHITE, fg=PURPLE,
        )
        self.balance_label.pack(pady=(0, 10))
        self.update_balance_label()

        self.field("Withdrawal Amount (PHP)")
        tk.Entry(self.root, textvariable=self.amount, font=("Arial", 12)).pack(
            fill="x", padx=30, pady=(0, 12), ipady=5
        )

        self.field("Cash-Out Destination")
        tk.OptionMenu(self.root, self.destination, *DESTINATIONS).pack(
            fill="x", padx=30, pady=(0, 12)
        )

        self.field("Destination Account / Number (dummy)")
        tk.Entry(self.root, textvariable=self.account, font=("Arial", 12)).pack(
            fill="x", padx=30, pady=(0, 18), ipady=5
        )

        tk.Button(
            self.root, text="Continue to Verification",
            bg=PURPLE, fg="white", command=self.withdraw,
        ).pack(fill="x", padx=30, ipady=8)

        tk.Label(
            self.root, text="Demo only — no real money is transferred.",
            bg=BG, fg="gray",
        ).pack(pady=15)

    def field(self, text):
        tk.Label(
            self.root, text=text, anchor="w", bg=BG, font=("Arial", 10, "bold")
        ).pack(fill="x", padx=30, pady=(5, 4))

    def update_balance_label(self):
        self.balance_label.config(text=f"₱{self.balance:,.2f}")

    # Validation of the amount
    def withdraw(self):
        account = self.account.get().strip()
        try:
            amount = Decimal(self.amount.get().strip().replace(",", ""))
            if (not amount.is_finite() or amount <= 0 or amount > MAX_AMOUNT
                    or amount.as_tuple().exponent < -2):
                raise ValueError(
                    "Enter an amount from ₱0.01 to ₱100,000.00, using up to 2 decimals."
                )
            if amount > self.balance:
                raise ValueError(
                    f"Insufficient balance. You only have ₱{self.balance:,.2f} available."
                )
            if not account:
                raise ValueError("Enter the destination account or number.")
        except (InvalidOperation, ValueError) as error:
            messagebox.showerror(
                "Invalid Details", str(error) or "Enter a valid amount.",
                parent=self.root,
            )
            return

        self.verify_security_password(amount, self.destination.get(), account)

    # Security Verification
    def verify_security_password(self, amount, destination, account):
        dialog = tk.Toplevel(self.root)
        dialog.title("Security Verification")
        dialog.geometry("320x240")
        dialog.resizable(False, False)
        dialog.configure(bg=WHITE)
        dialog.transient(self.root)
        dialog.grab_set()

        try:
            dialog.iconbitmap(os.path.join(BASE, "CICO.ico"))
        except Exception:
            print("Icon file not found.")

        # Header
        header = tk.Frame(dialog, bg=PURPLE, height=60)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text="Security Verification",
            bg=PURPLE, fg=WHITE, font=("Segoe UI", 14, "bold"),
        ).pack(expand=True)

        # Body
        tk.Label(
            dialog, text="Please enter your security password:",
            bg=WHITE, fg=BLACK, font=("Segoe UI", 10),
        ).pack(pady=(20, 10))

        password_entry = tk.Entry(
            dialog, show="*", width=25, relief="solid", bd=1,
            highlightthickness=2,
            highlightbackground=PURPLE, highlightcolor=DARK_PURPLE,
        )
        password_entry.pack(pady=5)
        password_entry.focus()

        # Checking of the password
        def check_password():
            if password_entry.get() == PASSWORD:
                messagebox.showinfo(
                    "Access Granted",
                    "Welcome! You have successfully verified your security password.",
                    parent=dialog,
                )
                dialog.destroy()
                self.complete_withdrawal(amount, destination, account)
            else:
                messagebox.showerror(
                    "Access Denied",
                    "Incorrect password. Please try again.",
                    parent=dialog,
                )
                password_entry.delete(0, tk.END)

        tk.Button(
            dialog, text="Submit", command=check_password, width=10,
            bg=PURPLE, fg=WHITE,
            activebackground=DARK_PURPLE, activeforeground=WHITE,
            font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
        ).pack(pady=15)

        dialog.bind("<Return>", lambda event: check_password())

    # Transaction Complete
    def complete_withdrawal(self, amount, destination, account):
        self.balance -= amount
        save_balance(self.balance)
        self.update_balance_label()
        self.cash_out_receipt(amount, destination, account)
        self.amount.set("")
        self.account.set("")

    # Receipt Generator
    def cash_out_receipt(self, amount, destination, account, customer_name="Customer"):
        now = datetime.now()
        receipt = (
            "CICO E-WALLET - CASH OUT RECEIPT\n"
            f"Receipt: CASHOUT-{now:%Y%m%d}-{random.randint(1000, 9999)}\n"
            f"Date: {now:%Y-%m-%d %I:%M %p}\n"
            f"Destination Type: {destination}\n"
            f"Destination Account: {account}\n"
            f"Customer: {customer_name}\n"
            f"Amount Withdrawn: ₱{amount:,.2f}\n"
            f"New Balance: ₱{self.balance:,.2f}\n"
            "Status: VERIFIED (DEMO)\n"
            "No real money was transferred."
        )

        window = tk.Toplevel(self.root)
        window.title("Cash Out Receipt")
        window.configure(bg=BG)

        try:
            window.iconbitmap(os.path.join(BASE, "CICO.ico"))
        except Exception:
            print("Icon file not found.")


        header = tk.Frame(window, bg=BG)
        header.pack(pady=(12, 0))

        try:
            img = Image.open(os.path.join(BASE, "CICO.png")).resize((32, 32))
            self.receipt_logo = ImageTk.PhotoImage(img)
            tk.Label(header, image=self.receipt_logo, bg=BG).pack(side="left", padx=(0, 10))
        except Exception as error:
            print("Logo error:", error)

        tk.Label(
            header, text="CASH OUT RECEIPT",
            font=("Arial", 14, "bold"), fg=PURPLE, bg=BG,
        ).pack(side="left")

        box = tk.Text(window, width=48, height=11, font=("Courier", 10))
        box.pack(padx=12, pady=12)
        box.insert("1.0", receipt)
        box.config(state="disabled")

        tk.Button(window, text="Close", command=window.destroy).pack(pady=(0, 12))


if __name__ == "__main__":
    CashOut()
