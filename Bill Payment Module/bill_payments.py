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
CATEGORIES = ["Electricity", "Water Bill", "Bank", "Internet", "Gaming"]
PASSWORD = "secure123"  # Demo password from verification.py


class BillPayments:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CICO - Bill Payments")
        self.root.geometry("420x500")
        self.root.configure(bg=BG)

        # Folder where this script lives (CICO.ico are found)
        self.base = os.path.dirname(os.path.abspath(__file__))

        try:
            self.root.iconbitmap(os.path.join(self.base, "CICO.ico"))
        except Exception:
            print("Icon file not found.")

        self.category = tk.StringVar(value=CATEGORIES[0])
        self.account = tk.StringVar()
        self.amount = tk.StringVar()

        self.build_ui()
        self.root.mainloop()

    # ---------- Main window ----------
    def build_ui(self):
        header = tk.Frame(self.root, bg=BG)
        header.pack(pady=18)

        try:
            img = Image.open(os.path.join(self.base, "CICO.png")).resize((40, 40))
            self.logo = ImageTk.PhotoImage(img)
            tk.Label(header, image=self.logo, bg=BG).pack(side="left", padx=(0, 10))
        except Exception as error:
            print("Logo error:", os.error)

        tk.Label(
            header, text="CICO BILL PAYMENTS",
            font=("Arial", 18, "bold"), fg=PURPLE, bg=BG,
        ).pack(side="left")

        self.field("Biller Category")
        tk.OptionMenu(self.root, self.category, *CATEGORIES).pack(
            fill="x", padx=30, pady=(0, 12)
        )

        self.field("Bill Reference / Account Number")
        tk.Entry(self.root, textvariable=self.account, font=("Arial", 12)).pack(
            fill="x", padx=30, pady=(0, 12), ipady=5
        )

        self.field("Payment Amount (PHP)")
        tk.Entry(self.root, textvariable=self.amount, font=("Arial", 12)).pack(
            fill="x", padx=30, pady=(0, 18), ipady=5
        )

        tk.Button(
            self.root, text="Continue to Verification",
            bg=PURPLE, fg="white", command=self.pay,
        ).pack(fill="x", padx=30, ipady=8)

        tk.Label(
            self.root, text="Demo only — no real payment is processed.",
            bg=BG, fg="gray",
        ).pack(pady=15)

    def field(self, text):
        tk.Label(
            self.root, text=text, anchor="w", bg=BG, font=("Arial", 10, "bold")
        ).pack(fill="x", padx=30, pady=(5, 4))

    # ---------- Validation ----------
    def pay(self):
        account = self.account.get().strip()
        try:
            amount = Decimal(self.amount.get().strip())
            if not account:
                raise ValueError("Enter the bill reference or account number.")
            if (not amount.is_finite() or amount <= 0 or amount > 100000
                    or amount.as_tuple().exponent < -2):
                raise ValueError(
                    "Enter an amount from ₱0.01 to ₱100,000.00, using up to 2 decimals."
                )
        except (InvalidOperation, ValueError) as error:
            messagebox.showerror(
                "Invalid Details", str(error) or "Enter a valid amount.",
                parent=self.root,
            )
            return

        self.verify_security_password(amount, account)

    # ---------- Security verification ----------
    def verify_security_password(self, amount, account):
        dialog = tk.Toplevel(self.root)
        dialog.title("Security Verification")
        dialog.geometry("320x240")
        dialog.resizable(False, False)
        dialog.configure(bg=WHITE)
        dialog.transient(self.root)
        dialog.grab_set()

        try:
            dialog.iconbitmap(os.path.join(self.base, "CICO.ico"))
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

        def check_password():
            if password_entry.get() == PASSWORD:
                messagebox.showinfo(
                    "Access Granted",
                    "Welcome! You have successfully verified your security password.",
                    parent=dialog,
                )
                dialog.destroy()
                self.bills_payment_receipt(amount, self.category.get(), account)
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

    # ---------- Receipt ----------
    def bills_payment_receipt(self, amount, biller_name, biller_account,
                              customer_name="Customer"):
        now = datetime.now()
        receipt = (
            "CICO E-WALLET - BILL PAYMENT RECEIPT\n"
            f"Receipt: BILL-{now:%Y%m%d}-{random.randint(1000, 9999)}\n"
            f"Date: {now:%Y-%m-%d %I:%M %p}\n"
            f"Biller Name: {biller_name}\n"
            f"Biller Account: {biller_account}\n"
            f"Customer: {customer_name}\n"
            f"Bill Category: {self.category.get()}\n"
            f"Amount: ₱{amount:,.2f}\n"
            "Status: VERIFIED (DEMO)\n"
            "No real payment was processed."
        )

        window = tk.Toplevel(self.root)
        window.title("Payment Receipt")
        window.configure(bg=BG)

        try:
            window.iconbitmap(os.path.join(self.base, "CICO.ico"))
        except Exception:
            print("Icon file not found.")

        # Header with logo
        header = tk.Frame(window, bg=BG)
        header.pack(pady=(12, 0))

        try:
            img = Image.open(os.path.join(self.base, "CICO.png")).resize((32, 32))
            self.receipt_logo = ImageTk.PhotoImage(img)
            tk.Label(header, image=self.receipt_logo, bg=BG).pack(side="left", padx=(0, 10))
        except Exception as error:
            print("Logo error:", error)

        tk.Label(
            header, text="PAYMENT RECEIPT",
            font=("Arial", 14, "bold"), fg=PURPLE, bg=BG,
        ).pack(side="left")

        box = tk.Text(window, width=48, height=11, font=("Courier", 10))
        box.pack(padx=12, pady=12)
        box.insert("1.0", receipt)
        box.config(state="disabled")

        tk.Button(window, text="Close", command=window.destroy).pack(pady=(0, 12))


if __name__ == "__main__":
    BillPayments()
