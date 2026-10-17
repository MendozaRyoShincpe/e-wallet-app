import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal, InvalidOperation

BALANCE_FILE = "wallet_balance.txt"
DEFAULT_BALANCE = Decimal("1000.00")


def load_balance():
    try:
        with open(BALANCE_FILE, "r", encoding="utf-8") as file:
            return Decimal(file.read().strip())
    except (FileNotFoundError, InvalidOperation, ValueError):
        return DEFAULT_BALANCE


def save_balance(balance):
    with open(BALANCE_FILE, "w", encoding="utf-8") as file:
        file.write(f"{balance:.2f}")


class WithdrawalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Withdrawal / Cash Out")
        self.root.geometry("460x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#f3f6fb")

        self.balance = load_balance()
        self.amount_var = tk.StringVar()
        self.destination_var = tk.StringVar()
        self.account_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Enter the withdrawal details below.")

        self.build_ui()
        self.update_balance_label()

    def build_ui(self):
        tk.Label(
            self.root, text="WITHDRAWAL / CASH OUT", font=("Segoe UI", 18, "bold"),
            bg="#f3f6fb", fg="#183153"
        ).pack(pady=(22, 4))
        tk.Label(
            self.root, text="Send money from your demo wallet",
            font=("Segoe UI", 10), bg="#f3f6fb", fg="#52647a"
        ).pack(pady=(0, 14))

        balance_card = tk.Frame(self.root, bg="#ffffff", highlightbackground="#d8e1ee", highlightthickness=1)
        balance_card.pack(fill="x", padx=28, pady=4)
        tk.Label(balance_card, text="CURRENT WALLET BALANCE", font=("Segoe UI", 9, "bold"),
                 bg="#ffffff", fg="#66758a").pack(pady=(12, 2))
        self.balance_label = tk.Label(balance_card, text="", font=("Segoe UI", 20, "bold"),
                                      bg="#ffffff", fg="#183153")
        self.balance_label.pack(pady=(0, 12))

        form = tk.Frame(self.root, bg="#f3f6fb")
        form.pack(fill="x", padx=32, pady=12)

        tk.Label(form, text="Withdrawal amount (₱)", bg="#f3f6fb", fg="#26364a",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Entry(form, textvariable=self.amount_var, font=("Segoe UI", 11)).pack(fill="x", ipady=5, pady=(4, 12))

        tk.Label(form, text="Cash-out destination", bg="#f3f6fb", fg="#26364a",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        destination_box = ttk.Combobox(form, textvariable=self.destination_var, state="readonly",
                                       values=("Bank account", "E-wallet", "Cash pickup", "Other"))
        destination_box.pack(fill="x", ipady=4, pady=(4, 12))
        destination_box.set("E-wallet")

        tk.Label(form, text="Dummy destination account / number", bg="#f3f6fb", fg="#26364a",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Entry(form, textvariable=self.account_var).pack(fill="x", ipady=5, pady=(4, 14))

        tk.Button(form, text="Confirm Withdrawal", command=self.confirm_withdrawal,
                  font=("Segoe UI", 11, "bold"), bg="#2459a9", fg="white",
                  activebackground="#194583", activeforeground="white",
                  relief="flat", cursor="hand2").pack(fill="x", ipady=8)

        tk.Label(self.root, textvariable=self.status_var, bg="#f3f6fb", fg="#52647a",
                 font=("Segoe UI", 9), wraplength=390).pack(pady=(8, 0), padx=20)

        tk.Label(self.root, text="Demo project only — no real money is transferred.",
                 bg="#f3f6fb", fg="#8a96a6", font=("Segoe UI", 8)).pack(side="bottom", pady=12)

    def update_balance_label(self):
        self.balance_label.config(text=f"₱{self.balance:,.2f}")

    def confirm_withdrawal(self):
        raw_amount = self.amount_var.get().strip().replace(",", "")
        account = self.account_var.get().strip()
        destination = self.destination_var.get().strip()

        try:
            amount = Decimal(raw_amount)
        except InvalidOperation:
            messagebox.showerror("Invalid amount", "Please enter a valid withdrawal amount, such as 250 or 250.50.")
            return

        if not amount.is_finite() or amount <= 0:
            messagebox.showerror("Invalid amount", "The withdrawal amount must be greater than ₱0.00.")
            return
        if amount > self.balance:
            messagebox.showerror(
                "Insufficient balance",
                f"You only have ₱{self.balance:,.2f} available in your demo wallet."
            )
            return
        if not destination:
            messagebox.showerror("Missing information", "Please select a cash-out destination.")
            return
        if not account:
            messagebox.showerror("Missing information", "Please enter a dummy destination account or number.")
            return

        confirm = messagebox.askyesno(
            "Confirm Withdrawal",
            f"Withdraw ₱{amount:,.2f} to {destination}?\n"
            f"Destination: {account}\n\n"
            "This is a demo transaction."
        )
        if not confirm:
            self.status_var.set("Withdrawal cancelled. No changes were made.")
            return

        self.balance -= amount
        save_balance(self.balance)
        self.update_balance_label()
        self.status_var.set(f"Withdrawal successful: ₱{amount:,.2f} deducted from your wallet.")
        messagebox.showinfo("Withdrawal Successful", f"₱{amount:,.2f} was deducted from your demo wallet.")
        self.amount_var.set("")
        self.account_var.set("")


if __name__ == "__main__":
    root = tk.Tk()
    app = WithdrawalApp(root)
    root.mainloop()
