import tkinter as tk
from tkinter import messagebox
from decimal import Decimal, InvalidOperation

from wallet import wallet
from ui.service_ui import ServiceWindow, WHITE, BLACK

MAX_AMOUNT = Decimal("100000")


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
            card,
            "Recipient Name",
            "Enter recipient name"
        )

        self.wallet_id_entry = self.field(
            card,
            "Recipient Phone / Wallet ID",
            "Enter phone number or wallet ID"
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

        # Visible Send Money button
        send_button = self.button(
            card,
            "Send Money",
            self.review_transfer
        )
        send_button.pack(
            fill="x",
            padx=5,
            pady=(12, 10)
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

            if amount > wallet.get_balance():
                raise ValueError(
                    "Insufficient balance.\n"
                    f"Available balance: "
                    f"₱{wallet.get_balance():,.2f}"
                )

        except (InvalidOperation, ValueError) as error:
            messagebox.showerror(
                "Invalid Transfer",
                str(error) or "Please enter a valid amount.",
                parent=self.root
            )
            return

        confirmed = messagebox.askyesno(
            "Confirm Transfer",
            f"Recipient: {recipient}\n"
            f"Phone / Wallet ID: {wallet_id}\n"
            f"Amount: ₱{amount:,.2f}\n"
            f"Message: {note}\n\n"
            "Continue with this demo transfer?",
            parent=self.root
        )

        if not confirmed:
            return

        self.verify_password(
            lambda: self.complete_transfer(
                amount,
                recipient,
                wallet_id,
                note
            )
        )

    def complete_transfer(
        self, amount, recipient, wallet_id, note
    ):
        try:
            new_balance = wallet.withdraw(
                amount,
                transaction_type="Send Money",
                description=(
                    f"To: {recipient} | "
                    f"Wallet ID: {wallet_id} | "
                    f"Note: {note}"
                )
            )

        except ValueError as error:
            messagebox.showerror(
                "Transfer Failed",
                str(error),
                parent=self.root
            )
            self.update_balance()
            return

        self.notify_balance_changed()

        transactions = wallet.get_transactions()
        transaction = transactions[-1] if transactions else {}

        receipt = (
            "Your demo transfer was successful!\n\n"
            f"Recipient: {recipient}\n"
            f"Phone / Wallet ID: {wallet_id}\n"
            f"Amount Sent: ₱{amount:,.2f}\n"
            f"Message: {note}\n"
            f"Transaction Ref: "
            f"{transaction.get('reference', 'N/A')}\n"
            f"Date: {transaction.get('date', 'N/A')}\n"
            f"Remaining Balance: ₱{new_balance:,.2f}\n\n"
            "This is a demo transfer. No real money "
            "was sent to another account."
        )

        self.show_receipt("Transfer Successful", receipt)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()

    SendMoney(root)

    root.mainloop()