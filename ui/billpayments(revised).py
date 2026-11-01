from decimal import Decimal, InvalidOperation
import tkinter as tk
from tkinter import messagebox

from receipt import issue_receipt
from wallet import wallet
from ui.service_ui import ServiceWindow
from ui.theme import WHITE, BLACK


# Categories and their available service providers
BILLERS = {
    "Electricity": ["Meralco"],
    "Water Bill": ["Maynilad", "Manila Water"],
    "Internet": ["PLDT", "Converge", "Globe At Home"],
    "Telecommunications": ["Globe", "Smart"],
    "Bank": ["BDO", "BPI", "Metrobank", "Other Bank"],
    "Gaming": ["Steam", "Garena", "Riot Games", "Other Provider"],
    "Other Utilities": ["Other Provider"]
}

MAX_AMOUNT = Decimal("100000")


class BillPayments(ServiceWindow):
    def __init__(self, parent, on_balance_change=None):
        super().__init__(
            parent,
            "Pay Bills",
            "Pay your bills using your CICO wallet.",
            on_balance_change=on_balance_change
        )
        self.build_form()

    # Creates the bill payment form
    def build_form(self):
        card = self.build_form_card("Bill Payment Details")

        tk.Label(
            card, text="Bill Category", font=("Arial", 9, "bold"),
            bg=WHITE, fg=BLACK
        ).pack(anchor="w", pady=(0, 4))

        first_category = next(iter(BILLERS))
        self.category_var = tk.StringVar(value=first_category)
        tk.OptionMenu(
            card, self.category_var, *BILLERS.keys(),
            command=self.update_providers
        ).pack(fill="x", pady=(0, 9))

        tk.Label(
            card, text="Company / Service Provider",
            font=("Arial", 9, "bold"), bg=WHITE, fg=BLACK
        ).pack(anchor="w", pady=(0, 4))

        self.provider_var = tk.StringVar(value=BILLERS[first_category][0])
        self.provider_menu = tk.OptionMenu(
            card, self.provider_var, *BILLERS[first_category]
        )
        self.provider_menu.pack(fill="x", pady=(0, 9))

        self.account_entry = self.field(
            card, "Account / Reference Number", "Enter bill account number"
        )
        self.amount_entry = self.field(card, "Amount (PHP)", "Enter amount")

        self.button(card, "Pay Bill", self.review_payment).pack(
            fill="x", pady=(5, 7)
        )

    # Changes the provider options when the category changes
    def update_providers(self, selected_category=None):
        category = selected_category or self.category_var.get()
        providers = BILLERS.get(category, ["Other Provider"])

        self.provider_var.set(providers[0])
        menu = self.provider_menu["menu"]
        menu.delete(0, "end")

        for provider in providers:
            menu.add_command(
                label=provider,
                command=lambda value=provider: self.provider_var.set(value)
            )

    # Validates details before confirming the payment
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

            balance = wallet.get_balance()
            if amount > balance:
                raise ValueError(
                    f"Insufficient balance.\nAvailable: ₱{balance:,.2f}"
                )

        except InvalidOperation:
            self.show_invalid_amount()
            return
        except ValueError as error:
            messagebox.showerror(
                "Invalid Payment", str(error), parent=self.root
            )
            return

        category = self.category_var.get()
        provider = self.provider_var.get()

        if not messagebox.askyesno(
            "Confirm Bill Payment",
            f"Category: {category}\n"
            f"Provider: {provider}\n"
            f"Account / Reference: {account}\n"
            f"Amount: ₱{amount:,.2f}\n\n"
            "Continue with this demo payment?",
            parent=self.root
        ):
            return

        # Verifies the user before completing the payment
        self.verify_password(
            lambda: self.complete_payment(amount, category, provider, account)
        )

    def show_invalid_amount(self):
        messagebox.showerror(
            "Invalid Payment", "Please enter a valid amount.",
            parent=self.root
        )

    # Deducts the amount and issues a receipt
    def complete_payment(self, amount, category, provider, account):
        try:
            new_balance = wallet.withdraw(
                amount,
                transaction_type="Bill Payment",
                description=f"{category} - {provider}: {account}"
            )
        except ValueError as error:
            messagebox.showerror(
                "Payment Failed", str(error), parent=self.root
            )
            self.update_balance()
            return

        self.notify_balance_changed()

        issue_receipt(
            self.root, wallet, "Bill Payment", amount, new_balance,
            details=f"{category} - {provider}: {account}",
            heading="Payment Successful"
        )
        self.root.destroy()

    root.withdraw()
    BillPayments(root)
    root.mainloop()
