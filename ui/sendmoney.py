import tkinter as tk
from tkinter import messagebox
from decimal import Decimal, InvalidOperation

from wallet import wallet
from ui.service_ui import ServiceWindow


# Maximum amount allowed for a single money transfer
MAX_AMOUNT = Decimal("100000")


class SendMoney(ServiceWindow):

    def __init__(self, parent, on_balance_change=None):
        # Initialize the reusable service window
        super().__init__(
            parent,
            "Send Money",
            "Transfer funds to another CICO account.",
            on_balance_change=on_balance_change
        )

        self.build_form()

    # --------------------------------------------------
    # TRANSFER FORM
    # --------------------------------------------------

    def build_form(self):
        # Create the transfer details form
        card = self.build_form_card("Transfer Details")

        self.wallet_id_entry = self.field(
            card,
            "Recipient CICO Account Number",
            "Enter registered 11-digit phone number"
        )

        tk.Label(
            card,
            text="Enter the recipient's registered phone number (09XXXXXXXXX).",
            font=("Arial", 8),
            fg="#777C91",
            anchor="w",
            justify="left",
            wraplength=350
        ).pack(
            fill="x",
            padx=4,
            pady=(0, 8)
        )

        self.amount_entry = self.field(
            card,
            "Amount (PHP)",
            "Enter amount"
        )

        self.note_entry = self.field(
            card,
            "Message / Note (Optional)",
            "Enter a message"
        )

        self.button(
            card,
            "Send Money",
            self.review_transfer
        ).pack(
            fill="x",
            padx=4,
            pady=(12, 10)
        )

    # --------------------------------------------------
    # REVIEW TRANSFER
    # --------------------------------------------------

    def review_transfer(self):

        # Retrieve the recipient, amount, and optional message
        recipient_account = self.value(
            self.wallet_id_entry
        )

        raw_amount = self.value(
            self.amount_entry
        )

        note = self.value(
            self.note_entry
        ) or "No message"

        # Validate recipient account number.
        if not recipient_account:
            messagebox.showwarning(
                "Missing Information",
                "Please enter the recipient's CICO Account Number.",
                parent=self.root
            )
            return

        if (
            not recipient_account.isascii()
            or not recipient_account.isdigit()
            or len(recipient_account) != 11
            or not recipient_account.startswith("09")
        ):
            messagebox.showerror(
                "Invalid Account Number",
                "Please enter a valid 11-digit Philippine mobile number starting with 09.",
                parent=self.root
            )
            return

        # Find recipient using account number only.
        try:
            recipient = wallet._find_user(
                recipient_account
            )

        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Lookup Failed",
                str(error),
                parent=self.root
            )
            return

        if not recipient:
            messagebox.showerror(
                "Recipient Not Found",
                "No CICO account is registered with that number.",
                parent=self.root
            )
            return

        recipient_name = recipient.get(
            "name",
            "Unknown User"
        )

        # Prevent self-transfer.
        if recipient_account == str(wallet.account_number):
            messagebox.showerror(
                "Invalid Transfer",
                "You cannot send money to your own account.",
                parent=self.root
            )
            return

        # Validate transfer amount.
        try:
            amount = Decimal(raw_amount)

            if not amount.is_finite() or amount <= 0:
                raise ValueError(
                    "Amount must be greater than zero."
                )

            if amount.as_tuple().exponent < -2:
                raise ValueError(
                    "Amount cannot have more than 2 decimal places."
                )

            if amount > MAX_AMOUNT:
                raise ValueError(
                    "Maximum transfer amount is ₱100,000.00."
                )

            # Check whether the sender has enough balance
            balance = wallet.get_balance()

            if amount > balance:
                raise ValueError(
                    "Insufficient balance.\n"
                    f"Available balance: ₱{balance:,.2f}"
                )

        except (InvalidOperation, ValueError) as error:
            messagebox.showerror(
                "Invalid Transfer",
                str(error) or "Please enter a valid amount.",
                parent=self.root
            )
            return

        # Display transfer details before processing
        confirmed = messagebox.askyesno(
            "Confirm Transfer",
            f"Recipient: {recipient_name}\n"
            f"CICO Account Number: {recipient_account}\n"
            f"Amount: ₱{amount:,.2f}\n"
            f"Message: {note}\n\n"
            "Do you want to continue?",
            parent=self.root
        )

        if not confirmed:
            return

        # Verify password before transferring
        self.verify_password(
            lambda: self.complete_transfer(
                amount,
                recipient_account,
                note
            )
        )

    # --------------------------------------------------
    # COMPLETE TRANSFER
    # --------------------------------------------------

    def complete_transfer(
        self,
        amount,
        recipient_account,
        note
    ):

        # Process the transfer through the shared wallet object
        try:
            result = wallet.transfer(
                recipient_account,
                amount,
                description=note
            )

            # Retrieve the updated transaction details
            new_balance = result["sender_balance"]

            recipient_name = result["recipient_name"]

            recipient_account = result[
                "recipient_account_number"
            ]

            reference = result["reference"]

            # Refresh the displayed wallet balance
            self.notify_balance_changed()

            # Prepare the successful transfer receipt
            receipt = (
                "Your money transfer was successful!\n\n"
                f"Recipient: {recipient_name}\n"
                f"CICO Account Number: {recipient_account}\n"
                f"Amount Sent: ₱{amount:,.2f}\n"
                f"Message: {note}\n"
                f"Transaction Ref: {reference}\n"
                f"Remaining Balance: ₱{new_balance:,.2f}\n\n"
                "The recipient's wallet has been credited."
            )

            self.show_receipt(
                "Transfer Successful",
                receipt
            )

            self.close()

        except (ValueError, OSError) as error:
            # Display errors if the transfer cannot be completed
            messagebox.showerror(
                "Transfer Failed",
                str(error),
                parent=self.root
            )

            self.update_balance()


# --------------------------------------------------
# INDEPENDENT TESTING
# --------------------------------------------------

if __name__ == "__main__":
    # Allow this window to be tested independently
    root = tk.Tk()
    root.withdraw()

    SendMoney(root)

    root.mainloop()