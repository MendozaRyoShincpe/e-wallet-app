from decimal import Decimal, InvalidOperation
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

from wallet import wallet
from ui.service_ui import ServiceWindow, WHITE, BLACK


# Available bill categories and maximum payment amount
CATEGORIES = [
    "Electricity",
    "Water Bill",
    "Bank",
    "Internet",
    "Gaming"
]

MAX_AMOUNT = Decimal("100000")


# Inherits reusable UI components from ServiceWindow
class BillPayments(ServiceWindow):
    def __init__(self, parent, on_balance_change=None):
        super().__init__(
            parent,
            "Pay Bills",
            "Pay your bills using your CICO wallet.",
            on_balance_change=on_balance_change
        )
        self.build_form()

    # Creates the bill payment form and input fields
    def build_form(self):
        card = self.build_form_card("Bill Payment Details")

        tk.Label(
            card,
            text="Bill Category",
            font=("Arial", 9, "bold"),
            bg=WHITE,
            fg=BLACK
        ).pack(anchor="w", pady=(0, 4))

        self.category_var = tk.StringVar(value=CATEGORIES[0])
        tk.OptionMenu(card, self.category_var, *CATEGORIES).pack(
            fill="x", pady=(0, 9)
        )

        self.account_entry = self.field(
            card, "Account / Reference Number", "Enter bill account number"
        )
        self.amount_entry = self.field(
            card, "Amount (PHP)", "Enter amount"
        )

        self.button(
            card, "Pay Bill", self.review_payment
        ).pack(fill="x", pady=(5, 7))

    # Validates the account number and payment amount before proceeding
    def review_payment(self):
        account = self.value(self.account_entry)

        if not account:
            messagebox.showwarning(
                "Missing Information",
                "Please enter the bill account or reference number.",
                parent=self.root
            )
            return

        try:
            amount = Decimal(self.value(self.amount_entry))

            if not amount.is_finite() or amount <= 0:
                raise ValueError("Amount must be greater than zero.")

            if amount.as_tuple().exponent < -2:
                raise ValueError("Use no more than 2 decimal places.")

            if amount > MAX_AMOUNT:
                raise ValueError("Maximum payment is ₱100,000.00.")

            # Checks whether the wallet has enough funds
            if amount > wallet.get_balance():
                raise ValueError(
                    f"Insufficient balance.\n"
                    f"Available: ₱{wallet.get_balance():,.2f}"
                )

        except (InvalidOperation, ValueError) as error:
            messagebox.showerror(
                "Invalid Payment", str(error), parent=self.root
            )
            return

        category = self.category_var.get()

        # Asks the user to confirm the bill payment details
        if not messagebox.askyesno(
            "Confirm Bill Payment",
            f"Category: {category}\n"
            f"Account / Reference: {account}\n"
            f"Amount: ₱{amount:,.2f}\n\n"
            "Continue with this demo payment?",
            parent=self.root
        ):
            return

        # Verifies the user's password before processing the payment
        self.verify_password(
            lambda: self.complete_payment(
                amount, category, account
            )
        )

    # Deducts the payment from the wallet and records the transaction
    def complete_payment(self, amount, category, account):
        try:
            new_balance = wallet.withdraw(
                amount,
                transaction_type="Bill Payment",
                description=f"{category}: {account}"
            )
        except ValueError as error:
            messagebox.showerror(
                "Payment Failed", str(error), parent=self.root
            )
            self.update_balance()
            return

        # Updates the dashboard balance and retrieves the latest transaction
        self.notify_balance_changed()
        transaction = wallet.get_transactions()[-1]

        # Displays the payment receipt and remaining balance
        self.show_receipt(
            "Payment Successful",
            "Your demo bill payment was successful!\n\n"
            f"Category: {category}\n"
            f"Account / Reference: {account}\n"
            f"Amount: ₱{amount:,.2f}\n"
            f"Transaction Ref: {transaction['reference']}\n"
            f"Date: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
            f"Remaining Balance: ₱{new_balance:,.2f}"
        )
        self.root.destroy()


# Allows the Bill Payments window to run independently for testing
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    BillPayments(root)
    root.mainloop()