from decimal import Decimal, InvalidOperation
from datetime import datetime
import random
import tkinter as tk
from tkinter import messagebox

from wallet import wallet
from ui.service_ui import ServiceWindow, BG, WHITE, BLACK, GRAY, PURPLE


# Available deposit sources and maximum deposit amount
SOURCES = ["Bank account", "E-wallet", "Cash", "Other"]
MAX_AMOUNT = Decimal("100000")


# Inherits reusable UI components from ServiceWindow
class CashIn(ServiceWindow):
    def __init__(self, parent, on_balance_change=None):
        super().__init__(
            parent,
            "Cash In / Deposit",
            "Add funds to your CICO wallet.",
            on_balance_change=on_balance_change
        )
        self.build_form()

    # Creates the deposit form and its input fields
    def build_form(self):
        card = self.build_form_card("Deposit Details")

        tk.Label(
            card, text="Deposit Source", font=("Arial", 9, "bold"),
            bg=WHITE, fg=BLACK
        ).pack(anchor="w", pady=(0, 4))

        self.source_var = tk.StringVar(value=SOURCES[0])
        tk.OptionMenu(card, self.source_var, *SOURCES).pack(
            fill="x", pady=(0, 9)
        )

        self.reference_entry = self.field(
            card, "Reference / Account (Optional)", "Enter reference"
        )
        self.amount_entry = self.field(
            card, "Amount (PHP)", "Enter amount"
        )

        self.button(
            card, "Deposit Money", self.review_deposit
        ).pack(fill="x", pady=(5, 7))

    # Validates the deposit amount and asks the user to confirm
    def review_deposit(self):
        raw_amount = self.value(self.amount_entry)

        try:
            amount = Decimal(raw_amount)

            if not amount.is_finite() or amount <= 0:
                raise ValueError("Amount must be greater than zero.")

            if amount.as_tuple().exponent < -2:
                raise ValueError("Use no more than 2 decimal places.")

            if amount > MAX_AMOUNT:
                raise ValueError("Maximum deposit is ₱100,000.00.")

        except (InvalidOperation, ValueError) as error:
            messagebox.showerror(
                "Invalid Amount", str(error), parent=self.root
            )
            return

        source = self.source_var.get()
        reference = self.value(self.reference_entry) or "Not provided"

        # Requires confirmation before processing the deposit
        if not messagebox.askyesno(
            "Confirm Deposit",
            f"Source: {source}\n"
            f"Reference: {reference}\n"
            f"Amount: ₱{amount:,.2f}\n\n"
            "Continue with this demo deposit?",
            parent=self.root
        ):
            return

        # Verifies the user's password before completing the deposit
        self.verify_password(
            lambda: self.complete_deposit(amount, source, reference)
        )

    # Adds the amount to the wallet balance and records the transaction
    def complete_deposit(self, amount, source, reference):
        try:
            new_balance = wallet.deposit(
                amount,
                description=f"{source}: {reference}"
            )
        except ValueError as error:
            messagebox.showerror(
                "Deposit Failed", str(error), parent=self.root
            )
            return

        # Updates the dashboard balance
        self.notify_balance_changed()

        # Retrieves the latest transaction for the receipt
        transaction = wallet.get_transactions()[-1]

        # Displays the deposit receipt and updated balance
        self.show_receipt(
            "Deposit Successful",
            "Your demo deposit was successful!\n\n"
            f"Source: {source}\n"
            f"Reference: {reference}\n"
            f"Amount: ₱{amount:,.2f}\n"
            f"Transaction Ref: {transaction['reference']}\n"
            f"Date: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
            f"New Balance: ₱{new_balance:,.2f}"
        )
        self.root.destroy()


# Allows the Cash In window to run independently for testing
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    CashIn(root)
    root.mainloop()