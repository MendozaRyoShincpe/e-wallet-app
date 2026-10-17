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


class DepositApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Deposit / Cash In")
        self.root.geometry("460x520")
        self.root.resizable(False, False)
        self.root.configure(bg="#f3f6fb")

        self.balance = load_balance()
        self.amount_var = tk.StringVar()
        self.source_var = tk.StringVar()
        self.account_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Enter the deposit details below.")

        self.build_ui()
        self.update_balance_label()

    def build_ui(self):
        tk.Label(
            self.root, text="DEPOSIT / CASH IN", font=("Segoe UI", 18, "bold"),
            bg="#f3f6fb", fg="#183153"
        ).pack(pady=(22, 4))
        tk.Label(
            self.root, text="Add money to your demo wallet",
            font=("Segoe UI", 10), bg="#f3f6fb", fg="#52647a"
        ).pack(pady=(0, 14))

        balance_card = tk.Frame(self.root, bg="#ffffff", highlightbackground="#d8e1ee", highlightthickness=1)
        balance_card.pack(fill="x", padx=28, pady=4)
        tk.Label(balance_card, text="CURRENT WALLET BALANCE", font=("Segoe UI", 9, "bold"),
                 bg="#ffffff", fg="#66758a").pack(pady=(12, 2))
        self.balance_label = tk.Label(balance_card, text="", font=("Segoe UI", 20, "bold"),
                                      bg="#ffffff", fg="#16805d")
        self.balance_label.pack(pady=(0, 12))

        form = tk.Frame(self.root, bg="#f3f6fb")
        form.pack(fill="x", padx=32, pady=12)

        tk.Label(form, text="Deposit amount (₱)", bg="#f3f6fb", fg="#26364a",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Entry(form, textvariable=self.amount_var, font=("Segoe UI", 11)).pack(fill="x", ipady=5, pady=(4, 12))

        tk.Label(form, text="Source account type", bg="#f3f6fb", fg="#26364a",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        source_box = ttk.Combobox(form, textvariable=self.source_var, state="readonly",
                                  values=("Bank account", "E-wallet", "Cash", "Other"))
        source_box.pack(fill="x", ipady=4, pady=(4, 12))
        source_box.set("Bank account")

        tk.Label(form, text="Dummy source account / reference", bg="#f3f6fb", fg="#26364a",
                 font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Entry(form, textvariable=self.account_var).pack(fill="x", ipady=5, pady=(4, 14))

        tk.Button(form, text="Confirm Deposit", command=self.confirm_deposit,
                  font=("Segoe UI", 11, "bold"), bg="#16805d", fg="white",
                  activebackground="#11684c", activeforeground="white",
                  relief="flat", cursor="hand2").pack(fill="x", ipady=8)

        tk.Label(self.root, textvariable=self.status_var, bg="#f3f6fb", fg="#52647a",
                 font=("Segoe UI", 9), wraplength=390).pack(pady=(8, 0), padx=20)

        tk.Label(self.root, text="Demo project only — no real money is transferred.",
                 bg="#f3f6fb", fg="#8a96a6", font=("Segoe UI", 8)).pack(side="bottom", pady=12)

    def update_balance_label(self):
        self.balance_label.config(text=f"₱{self.balance:,.2f}")

    def confirm_deposit(self):
        raw_amount = self.amount_var.get().strip().replace(",", "")
        reference = self.account_var.get().strip()
        source = self.source_var.get().strip()

        try:
            amount = Decimal(raw_amount)
        except InvalidOperation:
            messagebox.showerror("Invalid amount", "Please enter a valid deposit amount, such as 250 or 250.50.")
            return

        if not amount.is_finite() or amount <= 0:
            messagebox.showerror("Invalid amount", "The deposit amount must be greater than ₱0.00.")
            return
        if not source:
            messagebox.showerror("Missing information", "Please select a source account type.")
            return
        if not reference:
            messagebox.showerror("Missing information", "Please enter a dummy source account or reference.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deposit",
            f"Deposit ₱{amount:,.2f} from {source}?\n"
            f"Reference: {reference}\n\n"
            "This is a demo transaction."
        )
        if not confirm:
            self.status_var.set("Deposit cancelled. No changes were made.")
            return

        self.balance += amount
        save_balance(self.balance)
        self.update_balance_label()
        self.status_var.set(f"Deposit successful: ₱{amount:,.2f} added to your wallet.")
        messagebox.showinfo("Deposit Successful", f"₱{amount:,.2f} was added to your demo wallet.")
        self.amount_var.set("")
        self.account_var.set("")


if __name__ == "__main__":
    root = tk.Tk()
    app = DepositApp(root)
    root.mainloop()
