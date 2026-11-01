# Import Decimal and InvalidOperation for accurate money calculations
# and handling invalid amount inputs
from decimal import Decimal, InvalidOperation

# Import datetime to record the date and time of deposits
from datetime import datetime

# Import Tkinter to create the graphical user interface
import tkinter as tk

# Import messagebox to display warnings, confirmations, and errors
from tkinter import messagebox

# Import random to generate transaction reference numbers
import random

# Import the shared wallet object to access and update the balance
from wallet import wallet

# Import ServiceWindow and color constants for the service interface
from ui.service_ui import (
    ServiceWindow,
    BG,
    WHITE,
    BLACK,
    GRAY,
    PURPLE
)

# Import additional UI utilities for styling and window management
from ui.theme import BORDER, DARK_PURPLE, center_on, apply_icon, safe_grab


# ==================================================
# DEPOSIT SETTINGS
# ==================================================

# List of available sources where users can deposit money
SOURCES = ["Bank account", "E-wallet", "Cash", "Other"]

# Set the maximum allowed deposit amount to ₱100,000
MAX_AMOUNT = Decimal("100000")


# Define the CashIn class for handling wallet deposits
# It inherits reusable interface features from ServiceWindow
class CashIn(ServiceWindow):

    # Constructor that initializes the cash-in window
    def __init__(self, parent, on_balance_change=None):

        # Call the parent class constructor using super()
        # This initializes the common service window components
        super().__init__(
            parent,
            "Cash In / Deposit",
            "Add funds to your CICO wallet.",
            on_balance_change=on_balance_change
        )

        # Store the QR window reference
        # Initially, no QR window is open
        self.qr_window = None

        # Store the current QR payment session information
        self.qr_session = None

        # Build and display the deposit form
        self.build_form()

    # ---------- Deposit Form ----------

    def build_form(self):
        # Create a form card to organize the deposit fields
        card = self.build_form_card("Deposit Details")

        # Display the label for the deposit source dropdown
        tk.Label(
            card,
            text="Deposit Source",
            font=("Arial", 9, "bold"),
            bg=WHITE,
            fg=BLACK
        ).pack(anchor="w", pady=(0, 4))

        # Create a StringVar to store the selected deposit source
        # The first source is selected by default
        self.source_var = tk.StringVar(value=SOURCES[0])

        # Create a dropdown menu containing all deposit sources
        tk.OptionMenu(
            card,
            self.source_var,
            *SOURCES
        ).pack(fill="x", pady=(0, 9))

        # Create an optional input field for the reference or account number
        self.reference_entry = self.field(
            card,
            "Reference / Account (Optional)",
            "Enter reference"
        )

        # Create an input field for the deposit amount
        self.amount_entry = self.field(
            card,
            "Amount (PHP)",
            "Enter amount"
        )

        # Create the Deposit Money button
        # Clicking it starts the normal deposit process
        self.button(
            card,
            "Deposit Money",
            self.review_deposit
        ).pack(fill="x", pady=(5, 7))

        # Create another button for the QR code deposit feature
        # Clicking it opens the QR code payment window
        self.button(
            card,
            "Cash In via QR Code",
            self.show_qr,
            primary=False
        ).pack(fill="x", pady=(0, 5))

    # ---------- Amount Validation ----------

    def get_amount(self):
        # Retrieve the deposit amount entered by the user
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

            # Check whether the deposit exceeds the maximum limit
            if amount > MAX_AMOUNT:
                raise ValueError(
                    "Maximum deposit is ₱100,000.00."
                )

            # Return the validated deposit amount
            return amount

        # Handle invalid decimal values and other validation errors
        except (InvalidOperation, ValueError) as error:
            messagebox.showerror(
                "Invalid Amount",
                str(error),
                parent=self.root
            )

            # Return None if the amount is invalid
            return None

    # ---------- Normal Deposit ----------

    def review_deposit(self):
        # Validate the amount entered by the user
        amount = self.get_amount()

        # Stop the process if the amount is invalid
        if amount is None:
            return

        # Retrieve the selected deposit source
        source = self.source_var.get()

        # Retrieve the optional reference number
        # Use Not provided if the user leaves the field empty
        reference = (
            self.value(self.reference_entry) or "Not provided"
        )

        # Display the deposit details for user confirmation
        if not messagebox.askyesno(
            "Confirm Deposit",
            f"Source: {source}\n"
            f"Reference: {reference}\n"
            f"Amount: ₱{amount:,.2f}\n\n"
            "Continue with this demo deposit?",
            parent=self.root
        ):

            # Stop the process if the user selects No
            return

        # Verify the user's password before adding money
        # The deposit continues only after successful verification
        self.verify_password(
            lambda: self.complete_deposit(
                amount,
                source,
                reference
            )
        )

    # ---------- QR Code Generation ----------

    def make_qr(self, text):
        # Try to import the qrcode package
        # This package is required to generate QR codes
        try:
            import qrcode

        # Display an installation instruction if the package is missing
        except ImportError:
            raise ImportError(
                "The QR Code package is not installed.\n\n"
                "Install it using:\npip install qrcode"
            )

        # Create a QRCode object with the selected settings
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=1,
            border=4
        )

        # Add the payment information to the QR code
        qr.add_data(text)

        # Automatically adjust the QR code size to fit the data
        qr.make(fit=True)

        # Return the QR code as a matrix of True and False values
        return qr.get_matrix()

    def show_qr(self):
        # Validate the deposit amount before generating a QR code
        amount = self.get_amount()

        # Stop if the entered amount is invalid
        if amount is None:
            return

        # Retrieve the selected deposit source
        source = self.source_var.get()

        # Retrieve the optional reference number
        reference = (
            self.value(self.reference_entry) or "Not provided"
        )

        # Open the QR code window using the validated information
        self.open_qr_window(amount, source, reference)

    def open_qr_window(self, amount, source, reference):

        # Close any previously opened QR window
        self.close_qr_window()

        # Retrieve the active wallet account number
        account_number = wallet.account_number

        # Check whether an active wallet account exists
        if not account_number:
            messagebox.showerror(
                "QR Code Error",
                "No active wallet account was found.",
                parent=self.root
            )
            return

        # Generate a QR transaction reference using the current date
        # and a random four-digit number
        qr_reference = (
            f"QR{datetime.now():%Y%m%d%H%M%S}"
            f"{random.randint(1000, 9999)}"
        )

        # Prepare the payment information to be stored in the QR code
        # This contains the account number, amount, and QR reference
        # The information is intended for the demo payment process
        qr_payload = (
            f"CICO-PAY|ACCT:{account_number}"
            f"|AMT:{amount:.2f}"
            f"|REF:{qr_reference}"
        )

        try:
            # Generate the QR code matrix from the payment information
            matrix = self.make_qr(qr_payload)

        # Handle errors if the QR code package is not installed
        except ImportError as error:
            messagebox.showerror(
                "QR Code Package Missing",
                str(error),
                parent=self.root
            )
            return

        # Handle other errors during QR code generation
        except Exception as error:
            messagebox.showerror(
                "QR Code Error",
                f"Unable to generate QR code:\n{error}",
                parent=self.root
            )
            return

        # Store the current QR payment information in a dictionary
        # This information will be used when confirming the payment
        self.qr_session = {
            "amount": amount,
            "source": source,
            "reference": reference,
            "qr_reference": qr_reference
        }

        # Store the main service window as the parent window
        parent = self.root

        # Create a separate window for the QR code
        self.qr_window = tk.Toplevel(parent)
        window = self.qr_window

        # Configure the QR code window title and dimensions
        window.title("CICO - QR Cash In")
        window.geometry("380x590")
        window.minsize(350, 550)

        # Set the background color and prevent resizing
        window.configure(bg=BG)
        window.resizable(False, False)

        # Make the QR window a child of the main service window
        window.transient(parent)

        # Call close_qr_window when the user clicks the close button
        window.protocol(
            "WM_DELETE_WINDOW",
            self.close_qr_window
        )

        # Apply the CICO application icon to the QR window
        apply_icon(window)

        # Display the QR payment heading
        tk.Label(
            window,
            text="Scan to Cash In",
            font=("Arial", 17, "bold"),
            bg=BG,
            fg=BLACK
        ).pack(pady=(20, 5))

        # Display instructions for the QR code
        tk.Label(
            window,
            text="Use this demo QR code for your deposit.",
            font=("Arial", 9),
            bg=BG,
            fg=GRAY
        ).pack()

        # ---------- QR Code Display ----------

        # Create a white frame to contain the QR code
        qr_frame = tk.Frame(
            window,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=12,
            pady=12
        )
        qr_frame.pack(pady=15)

        # Draw the generated QR code inside the frame
        self.draw_qr(qr_frame, matrix)

        # ---------- Payment Information ----------

        # Create a frame to organize the payment details
        details = tk.Frame(
            window,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=15,
            pady=12
        )
        details.pack(fill="x", padx=20)

        # Display the deposit amount
        tk.Label(
            details,
            text=f"Amount: ₱{amount:,.2f}",
            font=("Arial", 12, "bold"),
            bg=WHITE,
            fg=PURPLE
        ).pack(anchor="w", pady=3)

        # Display the wallet account number
        tk.Label(
            details,
            text=f"Account: {account_number}",
            font=("Arial", 9),
            bg=WHITE,
            fg=BLACK
        ).pack(anchor="w", pady=3)

        # Display the selected deposit source
        tk.Label(
            details,
            text=f"Source: {source}",
            font=("Arial", 9),
            bg=WHITE,
            fg=BLACK
        ).pack(anchor="w", pady=3)

        # Display the generated QR transaction reference
        tk.Label(
            details,
            text=f"Reference: {qr_reference}",
            font=("Arial", 8),
            bg=WHITE,
            fg=GRAY
        ).pack(anchor="w", pady=3)

        # Inform the user that the QR payment is only a simulation
        # No actual external payment is processed
        tk.Label(
            window,
            text=(
                "Demo only: No actual payment is processed.\n"
                "Click the button below to simulate payment."
            ),
            font=("Arial", 8),
            bg=BG,
            fg=GRAY,
            justify="center"
        ).pack(pady=12)

        # Create a button to simulate receiving the QR payment
        self.button(
            window,
            "Simulate Payment Received",
            self.confirm_qr_payment
        ).pack(fill="x", padx=20, pady=(0, 7))

        # Create a button to close the QR code window
        self.button(
            window,
            "Close",
            self.close_qr_window,
            primary=False
        ).pack(fill="x", padx=20)

        # Center the QR window relative to its parent window
        center_on(window, parent)

        # Prevent interaction with the parent window
        # until the QR window is closed
        safe_grab(window)

    # ---------- Draw QR Code ----------

    def draw_qr(self, parent, matrix):
        # Set the size of the QR code display area
        canvas_size = 260

        # Define the quiet zone around the QR code
        quiet_zone = 4

        # Create a Canvas widget to draw the QR code
        canvas = tk.Canvas(
            parent,
            width=canvas_size,
            height=canvas_size,
            bg=WHITE,
            highlightthickness=0
        )
        canvas.pack()

        # Get the total number of rows and columns in the QR matrix
        total_size = len(matrix)

        # Calculate the size of each individual QR square
        module_size = canvas_size / total_size

        # Loop through each row of the QR matrix
        for row_index, row in enumerate(matrix):

            # Loop through each column in the current row
            for col_index, is_dark in enumerate(row):

                # Draw a square only when the matrix value is True
                if is_dark:

                    # Calculate the top-left coordinates of the square
                    x1 = col_index * module_size
                    y1 = row_index * module_size

                    # Calculate the bottom-right coordinates of the square
                    x2 = x1 + module_size
                    y2 = y1 + module_size

                    # Draw the QR code square on the Canvas
                    canvas.create_rectangle(
                        x1,
                        y1,
                        x2,
                        y2,
                        fill=BLACK,
                        outline=BLACK
                    )

    # ---------- QR Payment Confirmation ----------

    def confirm_qr_payment(self):
        # Check whether an active QR payment session exists
        if not self.qr_session:
            messagebox.showerror(
                "QR Payment Error",
                "No active QR payment session was found.",
                parent=self.root
            )
            return

        # Retrieve the saved QR payment information
        session = self.qr_session

        # Use the QR window as the parent for confirmation messages
        parent = self.qr_window

        # Ask the user to confirm the simulated QR payment
        if not messagebox.askyesno(
            "Confirm QR Payment",
            f"Simulate receiving ₱{session['amount']:,.2f}?",
            parent=parent
        ):

            # Stop if the user does not confirm the payment
            return

        # Verify the user's password before completing the deposit
        # After successful verification, complete_deposit is called
        self.verify_password(
            lambda: self.complete_deposit(
                session["amount"],
                session["source"],
                session["qr_reference"]
            ),
            parent=parent
        )

    def close_qr_window(self):
        # Check whether a QR window is currently open
        if self.qr_window is not None:
            try:

                # Check whether the QR window still exists
                if self.qr_window.winfo_exists():
                    try:
                        # Release the window grab before destroying it
                        self.qr_window.grab_release()

                    # Ignore errors if the grab was already released
                    except tk.TclError:
                        pass

                    # Destroy the QR window
                    self.qr_window.destroy()

            # Ignore errors if the QR window is already destroyed
            except tk.TclError:
                pass

        # Reset the QR window reference
        self.qr_window = None

        # Clear the saved QR payment session
        self.qr_session = None

    # ---------- Complete Deposit ----------

    def complete_deposit(self, amount, source, reference):
        try:
            # Add the deposit amount to the shared wallet balance
            # Record the source and reference in the transaction history
            new_balance = wallet.deposit(
                amount,
                description=f"{source}: {reference}"
            )

        # Handle errors that occur during the deposit process
        except (ValueError, OSError) as error:
            messagebox.showerror(
                "Deposit Failed",
                str(error),
                parent=self.root
            )
            return

        # Retrieve the latest transaction history
        transactions = wallet.get_transactions()

        # Check whether a transaction record was successfully created
        if not transactions:
            messagebox.showerror(
                "Receipt Error",
                "The transaction was completed, but its receipt "
                "could not be retrieved.",
                parent=self.root
            )

            # Notify the dashboard that the wallet balance has changed
            self.notify_balance_changed()

            # Close the service window
            self.close()
            return

        # Get the most recent transaction from the transaction history
        transaction = transactions[-1]

        # Notify the dashboard to refresh the displayed wallet balance
        self.notify_balance_changed()

        # Close the QR window if the deposit came from QR payment
        self.close_qr_window()

        # Display the deposit receipt with the transaction details
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

        # Close the cash-in service window
        self.close()

    # ---------- Closing ----------

    def close(self):
        # Close the QR window first to prevent leftover windows
        self.close_qr_window()

        # Call the close method from the parent ServiceWindow class
        super().close()


# ---------- Standalone Testing ----------

# Check whether this file is being executed directly
if __name__ == "__main__":

    # Create a Tkinter root window for testing
    root = tk.Tk()

    # Hide the main root window because the service has its own interface
    root.withdraw()

    # Create and display the CashIn window
    CashIn(root)

    # Start the Tkinter event loop to keep the window running
    root.mainloop()
