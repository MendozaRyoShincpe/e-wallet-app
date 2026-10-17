import tkinter as tk
from tkinter import messagebox
from decimal import Decimal, InvalidOperation
from datetime import datetime
import random

PURPLE = "#7040E8"
CATEGORIES = ["Electricity", "Water Bill", "Bank", "Internet", "Gaming"]
PASSWORD = "secure123"  # Demo password from verification.py

class BillPayments:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CICO - Bill Payments")
        self.root.geometry("420x500")
        self.root.configure(bg="#F8F7FF")
        self.category = tk.StringVar(value=CATEGORIES[0])
        self.account = tk.StringVar()
        self.amount = tk.StringVar()

        tk.Label(self.root, text="CICO BILL PAYMENTS", font=("Arial", 18, "bold"), fg=PURPLE, bg="#F8F7FF").pack(pady=18)
        self.field("Biller Category")
        tk.OptionMenu(self.root, self.category, *CATEGORIES).pack(fill="x", padx=30, pady=(0, 12))
        self.field("Bill Reference / Account Number")
        tk.Entry(self.root, textvariable=self.account, font=("Arial", 12)).pack(fill="x", padx=30, pady=(0, 12), ipady=5)
        self.field("Payment Amount (PHP)")
        tk.Entry(self.root, textvariable=self.amount, font=("Arial", 12)).pack(fill="x", padx=30, pady=(0, 18), ipady=5)
        tk.Button(self.root, text="Continue to Verification", bg=PURPLE, fg="white", command=self.pay).pack(fill="x", padx=30, ipady=8)
        tk.Label(self.root, text="Demo only — no real payment is processed.", bg="#F8F7FF", fg="gray").pack(pady=15)
        self.root.mainloop()

    def field(self, text):
        tk.Label(self.root, text=text, anchor="w", bg="#F8F7FF", font=("Arial", 10, "bold")).pack(fill="x", padx=30, pady=(5, 4))

    def pay(self):
        account = self.account.get().strip()
        try:
            amount = Decimal(self.amount.get().strip())
            if not account:
                raise ValueError("Enter the bill reference or account number.")
            if not amount.is_finite() or amount <= 0 or amount > 100000 or amount.as_tuple().exponent < -2:
                raise ValueError("Enter an amount from ₱0.01 to ₱100,000.00, using up to 2 decimals.")
        except (InvalidOperation, ValueError) as error:
            messagebox.showerror("Invalid Details", str(error) or "Enter a valid amount.", parent=self.root)
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Security Verification")
        dialog.geometry("300x150")
        tk.Label(dialog, text="Enter security password").pack(pady=10)
        password = tk.Entry(dialog, show="*")
        password.pack()
        password.focus_set()

        def verify():
            if password.get() != PASSWORD:
                messagebox.showerror("Access Denied", "Incorrect password.", parent=dialog)
                password.delete(0, tk.END)
                return
            dialog.destroy()
            self.receipt(account, amount)

        tk.Button(dialog, text="Verify", command=verify).pack(pady=12)
        dialog.bind("<Return>", lambda event: verify())

    def receipt(self, account, amount):
        receipt = ("CICO E-WALLET - BILL PAYMENT RECEIPT\n"
                   f"Receipt: BILL-{datetime.now():%Y%m%d}-{random.randint(1000, 9999)}\n"
                   f"Date: {datetime.now():%Y-%m-%d %I:%M %p}\n"
                   f"Biller: {self.category.get()}\nAccount: {account}\n"
                   f"Amount: ₱{amount:,.2f}\nStatus: VERIFIED (DEMO)\n"
                   "No real payment was processed.")
        window = tk.Toplevel(self.root)
        window.title("Payment Receipt")
        box = tk.Text(window, width=48, height=10)
        box.pack(padx=12, pady=12)
        box.insert("1.0", receipt)
        box.config(state="disabled")
        tk.Button(window, text="Close", command=window.destroy).pack(pady=(0, 12))

if __name__ == "__main__":
    BillPayments()
