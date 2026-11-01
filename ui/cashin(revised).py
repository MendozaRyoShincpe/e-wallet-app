from datetime import datetime
from decimal import Decimal, InvalidOperation
import random
import tkinter as tk
from tkinter import messagebox

from receipt import issue_receipt
from wallet import wallet
from ui.service_ui import ServiceWindow
from ui.theme import (
    BG, WHITE, BLACK, GRAY, PURPLE, BORDER, apply_icon, center_on
)


# Available deposit sources and maximum deposit amount
SOURCES = ["Bank account", "E-wallet", "Cash", "Other"]
MAX_AMOUNT = Decimal("100000")


# Builds the QR code grid for the given text using the "qrcode" package.
# Install it once with:  pip install qrcode
def make_qr(text):
    """Return the QR code for text as rows of booleans (True = dark)."""
    # Imported here so the rest of the app still starts if it is missing
    import qrcode

    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        border=0
    )
    qr.add_data(text)
    qr.make(fit=True)
    return qr.get_matrix()


class CashIn(ServiceWindow):
    def __init__(self, parent, on_balance_change=None):
        super().__init__(
            parent,
            "Cash In / Deposit",
            "Add funds to your CICO wallet.",
            on_balance_change=on_balance_change
        )

        # Keeps track of the QR window and the payment it represents
        self.qr_window = None
        self.qr_session = None

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
        self.amount_entry = self.field(card, "Amount (PHP)", "Enter amount")

        self.button(
            card, "Deposit Money", self.review_deposit
        ).pack(fill="x", pady=(5, 7))

        # Opens the QR code window for this deposit amount
        self.button(
            card, "Cash In via QR Code", self.show_qr, primary=False
        ).pack(fill="x", pady=(0, 7))

    # ---------- Amount checks ----------
    # Checks that an amount is positive, has at most 2 decimals and is
    # within the limit. Returns the amount or raises ValueError.
    @staticmethod
    def check_amount(amount):
        if not amount.is_finite() or amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        if amount.as_tuple().exponent < -2:
            raise ValueError("Use no more than 2 decimal places.")

        if amount > MAX_AMOUNT:
            raise ValueError("Maximum deposit is ₱100,000.00.")

        return amount

    # Reads the amount field and validates it
    def parse_amount(self):
        try:
            amount = Decimal(self.value(self.amount_entry))
        except InvalidOperation:
            raise ValueError("Please enter a valid amount.")

        return self.check_amount(amount)

    # ---------- Normal deposit ----------
    # Validates the deposit amount and asks the user to confirm
    def review_deposit(self):
        try:
            amount = self.parse_amount()
        except ValueError as error:
            messagebox.showerror(
                "Invalid Amount", str(error), parent=self.root
            )
            return

        source = self.source_var.get()
        reference = self.value(self.reference_entry) or "Not provided"

        if not messagebox.askyesno(
            "Confirm Deposit",
            f"Source: {source}\n"
            f"Reference: {reference}\n"
            f"Amount: ₱{amount:,.2f}\n\n"
            "Continue with this demo deposit?",
            parent=self.root
        ):
            return

        # Verifies the user before completing the deposit
        self.verify_password(
            lambda: self.complete_deposit(amount, source, reference)
        )

    # ---------- QR deposit ----------
    # Validates the amount, then shows the QR code in its own window
    def show_qr(self):
        try:
            amount = self.parse_amount()
        except ValueError as error:
            messagebox.showerror(
                "Invalid Amount", str(error), parent=self.root
            )
            return

        source = self.source_var.get()
        user_reference = self.value(self.reference_entry)
        self.open_qr_window(amount, source, user_reference)

    # Builds the QR window with the code and the payment details
    def open_qr_window(self, amount, source, user_reference):
        self.close_qr_window()

        # The QR code carries the logged-in user's real wallet ID
        account_id = wallet.account_number
        qr_reference = (
            f"QR{datetime.now():%Y%m%d%H%M%S}{random.randint(100, 999)}"
        )
        payload = (
            f"CICO-PAY|ACCT:{account_id}|AMT:{amount:.2f}|REF:{qr_reference}"
        )

        try:
            matrix = make_qr(payload)
        except ImportError:
            messagebox.showerror(
                "QR Code Unavailable",
                "The QR code library is not installed.\n\n"
                "Install it by running:\npip install qrcode",
                parent=self.root
            )
            return
        except Exception as error:
            messagebox.showerror(
                "QR Code Error", str(error), parent=self.root
            )
            return

        reference = f"QR {qr_reference}"
        if user_reference:
            reference += f" ({user_reference})"

        # Remember exactly what the QR code represents
        self.qr_session = {
            "amount": amount,
            "source": source,
            "reference": reference,
        }

        win = tk.Toplevel(self.root)
        win.title("CICO - Cash In QR Code")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self.root)
        win.protocol("WM_DELETE_WINDOW", self.close_qr_window)
        apply_icon(win)
        self.qr_window = win

        # Header
        header = tk.Frame(win, bg=PURPLE, padx=20, pady=12)
        header.pack(fill="x")

        tk.Label(
            header, text="Scan to Cash In",
            font=("Arial", 16, "bold"), bg=PURPLE, fg=WHITE
        ).pack(anchor="w")

        tk.Label(
            header, text="Use this QR code to add funds to your CICO wallet.",
            font=("Arial", 9), bg=PURPLE, fg=WHITE
        ).pack(anchor="w")

        body = tk.Frame(win, bg=BG, padx=20, pady=14)
        body.pack(fill="both", expand=True)

        # QR code drawn on a white card (with the required quiet zone)
        qr_card = tk.Frame(
            body, bg=WHITE, highlightbackground=BORDER,
            highlightthickness=1, padx=10, pady=10
        )
        qr_card.pack()

        canvas = tk.Canvas(qr_card, bg=WHITE, highlightthickness=0)
        canvas.pack()
        self.draw_qr(canvas, matrix)

        # Payment details shown under the QR code
        details = tk.Frame(
            body, bg=WHITE, highlightbackground=BORDER,
            highlightthickness=1, padx=14, pady=10
        )
        details.pack(fill="x", pady=(12, 0))

        for name, value in (
            ("Wallet ID", account_id),
            ("Amount", f"₱{amount:,.2f}"),
            ("Reference", qr_reference),
            ("Source", source),
        ):
            row = tk.Frame(details, bg=WHITE)
            row.pack(fill="x", pady=1)

            tk.Label(
                row, text=name, font=("Arial", 9), bg=WHITE, fg=GRAY
            ).pack(side="left")

            tk.Label(
                row, text=value, font=("Arial", 9, "bold"),
                bg=WHITE, fg=BLACK
            ).pack(side="right")

        tk.Label(
            body,
            text="Demo only: a QR code alone does not process a real "
                 "payment. A payment service or gateway is needed for that.",
            font=("Arial", 8), bg=BG, fg=GRAY,
            wraplength=290, justify="center"
        ).pack(pady=(10, 8))

        self.button(
            body, "Simulate Payment Received", self.confirm_qr_payment
        ).pack(fill="x", pady=(0, 6))

        self.button(
            body, "Close", self.close_qr_window, primary=False
        ).pack(fill="x")

        center_on(win, self.root)

    # Draws the QR modules on the canvas (4-module white border around it)
    @staticmethod
    def draw_qr(canvas, matrix, dark="#000000", light=WHITE):
        n = len(matrix)
        quiet = 4
        scale = max(3, 280 // (n + 2 * quiet))
        size = (n + 2 * quiet) * scale

        canvas.config(width=size, height=size)
        canvas.create_rectangle(0, 0, size, size, fill=light, outline="")

        for y, row in enumerate(matrix):
            x = 0
            while x < n:
                if not row[x]:
                    x += 1
                    continue

                # Draw a whole run of dark modules as one rectangle
                start = x
                while x < n and row[x]:
                    x += 1

                canvas.create_rectangle(
                    (quiet + start) * scale, (quiet + y) * scale,
                    (quiet + x) * scale, (quiet + y + 1) * scale,
                    fill=dark, outline=""
                )

    # Closes the QR window if it is open
    def close_qr_window(self):
        window = self.qr_window
        self.qr_window = None
        self.qr_session = None

        if window is not None:
            try:
                window.destroy()
            except tk.TclError:
                pass

    # Simulates the QR payment arriving: validates the amount again,
    # asks for confirmation, then verifies the user before cash in
    def confirm_qr_payment(self):
        session = self.qr_session
        if not session:
            return

        parent = self.qr_window or self.root

        # Uses the amount the QR code was made for, not the field's text
        try:
            amount = self.check_amount(session["amount"])
        except ValueError as error:
            messagebox.showerror(
                "Invalid Amount", str(error), parent=parent
            )
            return

        source = session["source"]
        reference = session["reference"]

        if not messagebox.askyesno(
            "Confirm Cash In",
            f"Source: {source}\n"
            f"Reference: {reference}\n"
            f"Amount: ₱{amount:,.2f}\n\n"
            "Simulate receiving this QR payment and add it to your wallet?",
            parent=parent
        ):
            return

        self.verify_password(
            lambda: self.complete_deposit(amount, source, reference),
            parent=parent
        )

    # ---------- Completing a deposit ----------
    # Adds the amount to the wallet balance, records the transaction and
    # issues a receipt
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

        # The QR window is no longer needed once the money is added
        self.close_qr_window()
        self.notify_balance_changed()

        issue_receipt(
            self.root, wallet, "Cash In", amount, new_balance,
            details=f"{source}: {reference}",
            heading="Deposit Successful"
        )
        self.root.destroy()

    def close(self):
        self.close_qr_window()
        super().close()

