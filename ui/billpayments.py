# Import Decimal and InvalidOperation for accurate monetary calculations
# and handling invalid amount inputs
from decimal import Decimal, InvalidOperation

# Import datetime to record the payment date and time
from datetime import datetime

# Import Tkinter to create the graphical user interface
import tkinter as tk

# Import messagebox to display warnings, confirmations, and errors
from tkinter import messagebox

# Import the shared wallet object to access and update the balance
from wallet import wallet

# Import the ServiceWindow class and color constants
# ServiceWindow provides reusable interface elements for service pages
from ui.service_ui import ServiceWindow, WHITE, BLACK


# ==================================================
# BILLING CATEGORIES AND SERVICE PROVIDERS
# ==================================================

# Store the available bill categories and their corresponding providers
# Each category contains a list of supported companies or services
BILLERS = {
    "Electricity": ["Meralco"],
    "Water Bill": ["Maynilad", "Manila Water"],
    "Internet": ["PLDT", "Converge", "Globe At Home"],
    "Telecommunications": ["Globe", "Smart"],
    "Bank": ["BDO", "BPI", "Metrobank", "Other Bank"],
    "Gaming": ["Steam", "Garena", "Riot Games", "Other Provider"],
    "Other Utilities": ["Other Provider"]
}

# Set the maximum allowed bill payment amount to ₱100,000
MAX_AMOUNT = Decimal("100000")


# Define the BillPayments class
# It inherits from ServiceWindow to reuse common service interface features
class BillPayments(ServiceWindow):

    # Constructor that initializes the bill payment window
    def __init__(self, parent, on_balance_change=None):

        # Call the parent class constructor using super()
        # This initializes the common service window components
        super().__init__(
            parent,
            "Pay Bills",
            "Pay your bills using your CICO wallet.",
            on_balance_change=on_balance_change
        )

        # Create and display the bill payment form
        self.build_form()

    # ---------- Bill Payment Form ----------

    def build_form(self):
        # Create a form card to organize the bill payment fields
        card = self.build_form_card("Bill Payment Details")

        # Display the label for the bill category dropdown
        tk.Label(
            card,
            text="Bill Category",
            font=("Arial", 9, "bold"),
            bg=WHITE,
            fg=BLACK
        ).pack(anchor="w", pady=(0, 4))

        # Get the first available category as the default selection
        first_category = next(iter(BILLERS))

        # Create a StringVar to store the selected bill category
        self.category_var = tk.StringVar(value=first_category)

        # Create a dropdown menu containing all available categories
        # Call update_providers whenever the selected category changes
        tk.OptionMenu(
            card,
            self.category_var,
            *BILLERS.keys(),
            command=self.update_providers
        ).pack(fill="x", pady=(0, 9))

        # Display the label for the service provider dropdown
        tk.Label(
            card,
            text="Company / Service Provider",
            font=("Arial", 9, "bold"),
            bg=WHITE,
            fg=BLACK
        ).pack(anchor="w", pady=(0, 4))

        # Create a StringVar to store the selected service provider
        # The default provider comes from the first bill category
        self.provider_var = tk.StringVar(
            value=BILLERS[first_category][0]
        )

        # Create the provider dropdown using the available providers
        self.provider_menu = tk.OptionMenu(
            card,
            self.provider_var,
            *BILLERS[first_category]
        )

        # Display the provider dropdown
        self.provider_menu.pack(fill="x", pady=(0, 9))

        # Create an input field for the bill account or reference number
        self.account_entry = self.field(
            card,
            "Account / Reference Number",
            "Enter bill account number"
        )

        # Create an input field for the payment amount
        self.amount_entry = self.field(
            card,
            "Amount (PHP)",
            "Enter amount"
        )

        # Create the Pay Bill button
        # Clicking the button starts the payment validation process
        self.button(
            card,
            "Pay Bill",
            self.review_payment
        ).pack(fill="x", pady=(5, 7))

    # ---------- Provider Selection ----------

    def update_providers(self, selected_category=None):
        # Get the selected category from the dropdown
        # Use the current category if no selection was passed
        category = selected_category or self.category_var.get()

        # Retrieve the providers available for the selected category
        # Use Other Provider if the category is not found
        providers = BILLERS.get(
            category,
            ["Other Provider"]
        )

        # Automatically select the first provider in the category
        self.provider_var.set(providers[0])

        # Access the provider dropdown menu
        menu = self.provider_menu["menu"]

        # Remove the previous provider options
        menu.delete(0, "end")

        # Add the providers belonging to the newly selected category
        for provider in providers:
            menu.add_command(
                label=provider,

                # Update the selected provider when an option is clicked
                # The default argument preserves the current provider value
                command=lambda value=provider: self.provider_var.set(value)
            )

    # ---------- Payment Validation ----------

    def review_payment(self):
        # Retrieve the account or reference number entered by the user
        account = self.value(self.account_entry)

        # Check if the account or reference number is empty
        if not account:
            messagebox.showwarning(
                "Missing Information",
                "Please enter the bill account or reference number.",
                parent=self.root
            )
            return

        # Retrieve the payment amount entered by the user
        raw_amount = self.value(self.amount_entry)

        try:
            # Convert the entered amount into a Decimal value
            # for accurate monetary calculations
            amount = Decimal(raw_amount)

            # Reject invalid numbers, zero, and negative amounts
            if not amount.is_finite() or amount <= 0:
                raise ValueError(
                    "Amount must be greater than zero."
                )

            # Check that the amount does not exceed two decimal places
            if amount.as_tuple().exponent < -2:
                raise ValueError(
                    "Use no more than 2 decimal places."
                )

            # Check whether the payment exceeds the maximum limit
            if amount > MAX_AMOUNT:
                raise ValueError(
                    "Maximum payment is ₱100,000.00."
                )

            # Retrieve the user's current wallet balance
            balance = wallet.get_balance()

            # Check whether the wallet has enough money
            if amount > balance:
                raise ValueError(
                    f"Insufficient balance.\n"
                    f"Available: ₱{balance:,.2f}"
                )

        # Handle invalid decimal input
        except InvalidOperation:
            messagebox.showerror(
                "Invalid Payment",
                "Please enter a valid amount.",
                parent=self.root
            )
            return

        # Handle other validation errors
        except ValueError as error:
            messagebox.showerror(
                "Invalid Payment",
                str(error),
                parent=self.root
            )
            return

        # Retrieve the selected bill category and provider
        category = self.category_var.get()
        provider = self.provider_var.get()

        # Ask the user to confirm the payment details
        # before proceeding to password verification
        if not messagebox.askyesno(
            "Confirm Bill Payment",
            f"Category: {category}\n"
            f"Provider: {provider}\n"
            f"Account / Reference: {account}\n"
            f"Amount: ₱{amount:,.2f}\n\n"
            "Continue with this demo payment?",
            parent=self.root
        ):
            # Stop the payment process if the user selects No
            return

        # Verify the user's password before deducting money
        # The payment will only continue after successful verification
        self.verify_password(
            lambda: self.complete_payment(
                amount,
                category,
                provider,
                account
            )
        )

    # ---------- Complete Payment ----------

    def complete_payment(
        self,
        amount,
        category,
        provider,
        account
    ):
        try:
            # Deduct the payment amount from the shared wallet
            # Record the transaction as a Bill Payment
            # Include the bill category, provider, and account number
            new_balance = wallet.withdraw(
                amount,
                transaction_type="Bill Payment",
                description=f"{category} - {provider}: {account}"
            )

        # Handle errors that occur during the payment process
        except (ValueError, OSError) as error:
            messagebox.showerror(
                "Payment Failed",
                str(error),
                parent=self.root
            )

            # Refresh the displayed wallet balance
            self.update_balance()
            return

        # Retrieve the latest transaction history
        transactions = wallet.get_transactions()

        # Check whether a transaction record was successfully created
        if not transactions:
            messagebox.showerror(
                "Receipt Error",
                "The payment was completed, but its receipt "
                "could not be retrieved.",
                parent=self.root
            )

            # Notify the dashboard that the wallet balance has changed
            self.notify_balance_changed()

            # Close the bill payment window
            self.close()
            return

        # Get the most recent transaction from the transaction history
        transaction = transactions[-1]

        # Notify the dashboard to refresh the displayed wallet balance
        self.notify_balance_changed()

        # Display the payment receipt containing the transaction details
        self.show_receipt(
            "Payment Successful",
            "Your demo bill payment was successful!\n\n"
            f"Category: {category}\n"
            f"Provider: {provider}\n"
            f"Account / Reference: {account}\n"
            f"Amount: ₱{amount:,.2f}\n"
            f"Transaction Ref: {transaction['reference']}\n"
            f"Date: {datetime.now():%Y-%m-%d %H:%M:%S}\n"
            f"Remaining Balance: ₱{new_balance:,.2f}"
        )

        # Close the bill payment window after displaying the receipt
        self.close()


# ---------- Standalone Testing ----------

# Check whether this file is being executed directly
if __name__ == "__main__":

    # Create a Tkinter root window for testing
    root = tk.Tk()

    # Hide the main root window because the service has its own interface
    root.withdraw()

    # Create and display the BillPayments window
    BillPayments(root)

    # Start the Tkinter event loop to keep the window running
    root.mainloop()