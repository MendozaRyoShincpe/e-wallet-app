from tkinter import messagebox
from decimal import Decimal, InvalidOperation

from receipt import issue_receipt
from users import find_user
from wallet import wallet
from ui.service_ui import ServiceWindow

# Maximum allowed transfer amount
MAX_AMOUNT = Decimal("1000000")


class SendMoney(ServiceWindow):
    def __init__(self, parent, on_balance_change=None):
        super().__init__(
            parent,
            "Send Money",
            "Transfer funds to another CICO wallet.",
            on_balance_change=on_balance_change
        )
        self.build_form()

    def build_form(self):
        card = self.build_form_card("Transfer Details")

        self.recipient_entry = self.field(
            card, "Recipient Name", "Enter recipient name"
        )
        self.wallet_id_entry = self.field(
            card,
            "Recipient Phone / Wallet ID",
            "Enter phone number or wallet ID"
        )
        self.amount_entry = self.field(card, "Amount (PHP)", "Enter amount")
        self.note_entry = self.field(
            card, "Message / Note (Optional)", "Enter a message"
        )

        self.button(card, "Send Money", self.review_transfer).pack(
            fill="x", padx=4, pady=(12, 10)
        )

    def review_transfer(self):
        recipient = self.value(self.recipient_entry)
        wallet_id = self.value(self.wallet_id_entry)
        raw_amount = self.value(self.amount_entry)
        note = self.value(self.note_entry) or "No message"

        if not recipient:
            messagebox.showwarning(
                "Missing Information",
                "Please enter the recipient's name.",
                parent=self.root
            )
            return

        if not wallet_id:
            messagebox.showwarning(
                "Missing Information",
                "Please enter the recipient's phone number or wallet ID.",
                parent=self.root
            )
            return

        # The recipient must be a registered CICO user
        recipient_user = find_user(wallet_id)

        if recipient_user is None:
            messagebox.showerror(
                "Recipient Not Found",
                "No CICO wallet is registered with that phone number, "
                "email, or wallet ID.",
                parent=self.root
            )
            return

        if recipient_user["account_number"] == wallet.account_number:
            messagebox.showerror(
                "Invalid Transfer",
                "You cannot send money to yourself.",
                parent=self.root
            )
            return

        try:
            amount = Decimal(raw_amount)

            if not amount.is_finite() or amount <= 0:
                raise ValueError("Amount must be greater than zero.")
            if amount.as_tuple().exponent < -2:
                raise ValueError(
                    "Amount cannot have more than 2 decimal places."
                )
            if amount > MAX_AMOUNT:
                raise ValueError("Maximum transfer amount is ₱100,000.00.")

            balance = wallet.get_balance()
            if amount > balance:
                raise ValueError(
                    "Insufficient balance.\n"
                    f"Available balance: ₱{balance:,.2f}"
                )

        except InvalidOperation:
            messagebox.showerror(
                "Invalid Transfer", "Please enter a valid amount.",
                parent=self.root
            )
            return
        except ValueError as error:
            messagebox.showerror(
                "Invalid Transfer", str(error), parent=self.root
            )
            return

        confirmed = messagebox.askyesno(
            "Confirm Transfer",
            f"Recipient: {recipient}\n"
            f"Registered Name: {recipient_user['account_name']}\n"
            f"Phone / Wallet ID: {wallet_id}\n"
            f"Amount: ₱{amount:,.2f}\n"
            f"Message: {note}\n\n"
            "Continue with this demo transfer?",
            parent=self.root
        )

        if not confirmed:
            return

        # Verifies the user before completing the transfer
        self.verify_password(
            lambda: self.complete_transfer(
                amount, recipient, wallet_id, note, recipient_user
            )
        )

    def complete_transfer(
        self, amount, recipient, wallet_id, note, recipient_user
    ):
        try:
            # Moves the money to the recipient's wallet and records the
            # transaction in both histories.
            new_balance = wallet.transfer(
                amount,
                recipient_user["account_number"],
                description_out=(
                    f"To: {recipient} | "
                    f"Wallet ID: {wallet_id} | "
                    f"Note: {note}"
                ),
                description_in=(
                    f"From: {wallet.account_name} | "
                    f"Note: {note}"
                )
            )
        except ValueError as error:
            messagebox.showerror(
                "Transfer Failed", str(error), parent=self.root
            )
            self.update_balance()
            return

        self.notify_balance_changed()

        issue_receipt(
            self.root, wallet, "Send Money", amount, new_balance,
            details=f"To: {recipient} ({wallet_id}) | Note: {note}",
            heading="Transfer Successful"
        )
        self.root.destroy()
