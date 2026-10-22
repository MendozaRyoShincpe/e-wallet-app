from decimal import Decimal, InvalidOperation
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

from wallet import wallet
from ui.service_ui import ServiceWindow, WHITE, BLACK


DESTINATIONS = ["E-wallet", "Bank account", "Cash pickup", "Other"]
MAX_AMOUNT = Decimal("100000")


class CashOut(ServiceWindow):
    def __init__(self, parent, on_balance_change=None):
        super().__init__(
            parent,
            "Cash Out / Withdraw",
            "Withdraw funds from your CICO wallet.",
            on_balance_change=on_balance_change
        )
        self.build_form()

    def build_form(self):
        card = self.build_form_card("Withdrawal Details")

        tk.Label(
            card, text="Withdrawal Destination",
            font=("Arial", 9, "bold"), bg=WHITE, fg=BLACK
        ).pack(anchor="w", pady=(0, 4))

        self.destination_var = tk.StringVar(value=DESTINATIONS[0])
        tk.OptionMenu(card, self.destination_var, *DESTINATIONS).pack(
            fill="x", pady=(0, 9)
        )

        self.account_entry = self.field(
            card, "Account / Reference", "Enter account or reference"
        )
        self.amount_entry = self.field(
            card, "Amount (PHP)", "Enter amount"
        )

        self.button(
            card, "Withdraw Money", self.review_withdrawal
        ).pack(fill="x", pady=(5, 7))

    def review_withdrawal(self):
        try:
            amount = Decimal(self.value(self.amount_entry))
            if not amount.is_finite() or amount <= 0:
                raise ValueError("Amount must be greater than zero.")
            if amount.as_tuple().exponent < -2:
                raise ValueError("Use no more than 2 decimal places.")
            if amount > MAX_AMOUNT:
                raise ValueError("Maximum withdrawal is ₱100,000.00.")
            if amount > wallet.get_balance():
                raise ValueError(
                    f"Insufficient balance.\n"
                    f"Available: ₱{wallet.get_balance():,.2f}"
                )
        except (InvalidOperation, ValueError) as error:
            messagebox.showerror(
                "Invalid Withdrawal", str(error), parent=self.root
            )
            return

        destination = self.destination_var.get()
        account = self.value(self.account_entry) or "Not provided"

        if not messagebox.askyesno(
            "Confirm Withdrawal",
            f"Destination: {destination}\n"
            f"Account / Reference: {account}\n"
            f"Amount: ₱{amount:,.2f}\n\n"
            "Continue with this demo withdrawal?",
            parent=self.root
        ):
            return

        self.verify_password(
            lambda: self.complete_withdrawal(
                amount, destination, account
            )
        )

    def complete_withdrawal(self, amount, destination, account):
        try:
            new_balance = wallet.withdraw(
                amount,
                transaction_type="Cash Out",
                description=f"{destination}: {account}"
            )
        except ValueError as error:
            messagebox.showerror(
                "Withdrawal Failed", str(error), parent=self.root
            )
            self.update_balance()
            return

        self.notify_balance_changed()
        transaction = wallet.get_transactions()[-1]

        self.show_receipt(
            "Withdrawal Successful",
            "Your demo withdrawal was successful!\n\n"
            f"Destination: {destination}\n"
            f"Account / Reference: {account}\n"
            f"Amount: ₱{amount:,.2f}\n"
            f"Transaction Ref: {transaction['reference']}\n"
            f"Date: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
            f"Remaining Balance: ₱{new_balance:,.2f}"
        )
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    CashOut(root)
    root.mainloop()
