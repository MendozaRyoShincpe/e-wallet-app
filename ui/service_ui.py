import tkinter as tk
from tkinter import messagebox

from wallet import wallet
from verification import verification

from receipt import (
    ReceiptWindow,
    create_receipt,
    save_receipt
)

from ui.theme import (
    PURPLE, DARK_PURPLE, WHITE, BLACK, BG, GRAY, BORDER, GREEN,
    apply_icon, load_logo, safe_grab, center_on
)


# Base class: child windows reuse the header, balance card,
# form helpers, and security verification.
class ServiceWindow:

    def __init__(
        self,
        parent,
        title,
        subtitle,
        on_back=None,
        on_balance_change=None
    ):
        # Store parent window and callback functions
        self.parent = parent
        self.on_back = on_back
        self.on_balance_change = on_balance_change
        self.logo_image = None
        self._closed = False

        # Create and configure the service window
        self.root = tk.Toplevel(parent)
        self.root.title(f"CICO - {title}")
        self.root.geometry("420x600")
        self.root.minsize(400, 650)
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        # Apply the CICO application icon.
        apply_icon(self.root)

        # Load the CICO logo and retain its reference.
        self.load_logo()

        # Build the common header and content area
        self.build_header(title, subtitle)

        self.content = tk.Frame(
            self.root,
            bg=BG,
            padx=20,
            pady=15
        )
        self.content.pack(fill="both", expand=True)

        # Display the available wallet balance
        self.build_balance_card()

        tk.Label(
            self.root,
            text="CICO E-Wallet | Demo Application",
            font=("Arial", 8),
            bg=BG,
            fg=GRAY
        ).pack(pady=(0, 8))

        # Make the service window modal.
        self.root.transient(parent)
        center_on(self.root, parent)
        safe_grab(self.root)

    # ---------- Logo ----------

    def load_logo(self):
        # Keep the loaded logo image available for the header
        self.logo_image = load_logo(38)

    # ---------- Header ----------

    def build_header(self, title, subtitle):
        # Create the colored header section
        header = tk.Frame(
            self.root,
            bg=PURPLE,
            padx=20,
            pady=14
        )
        header.pack(fill="x")

        brand_row = tk.Frame(header, bg=PURPLE)
        brand_row.pack(fill="x")

        # Display the logo if the image is available
        if self.logo_image is not None:
            tk.Label(
                brand_row,
                image=self.logo_image,
                bg=PURPLE
            ).pack(side="left", padx=(0, 8))

        # Display the CICO brand name
        tk.Label(
            brand_row,
            text="CICO",
            font=("Arial", 20, "bold"),
            bg=PURPLE,
            fg=WHITE
        ).pack(side="left")

        # Add a close button to the header
        tk.Button(
            brand_row,
            text="✕",
            command=self.close,
            font=("Arial", 12, "bold"),
            bg=PURPLE,
            fg=WHITE,
            activebackground=DARK_PURPLE,
            activeforeground=WHITE,
            relief="flat",
            bd=0,
            cursor="hand2"
        ).pack(side="right")

        # Display the service title and description
        tk.Label(
            header,
            text=title,
            font=("Arial", 17, "bold"),
            bg=PURPLE,
            fg=WHITE
        ).pack(anchor="w", pady=(10, 2))

        tk.Label(
            header,
            text=subtitle,
            font=("Arial", 9),
            bg=PURPLE,
            fg=WHITE
        ).pack(anchor="w")

    # ---------- Balance Card ----------

    def build_balance_card(self):
        # Create the card that displays the current wallet balance
        card = tk.Frame(
            self.content,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=14,
            pady=10
        )
        card.pack(fill="x", pady=(0, 14))

        tk.Label(
            card,
            text="AVAILABLE BALANCE",
            font=("Arial", 9, "bold"),
            bg=WHITE,
            fg=GRAY
        ).pack(anchor="w")

        self.balance_label = tk.Label(
            card,
            text="₱0.00",
            font=("Arial", 21, "bold"),
            bg=WHITE,
            fg=PURPLE
        )
        self.balance_label.pack(anchor="w", pady=(4, 0))

        # Load the actual wallet balance
        self.update_balance()

    def update_balance(self):
        # Refresh the balance label using the wallet object
        try:
            self.balance_label.config(
                text=f"₱{wallet.get_balance():,.2f}"
            )
        except (tk.TclError, AttributeError):
            pass

    # ---------- Form Card ----------

    def build_form_card(self, title):
        # Create a reusable white card for service forms
        card = tk.Frame(
            self.content,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=15,
            pady=14
        )
        card.pack(fill="both", expand=True)

        tk.Label(
            card,
            text=title,
            font=("Arial", 13, "bold"),
            bg=WHITE,
            fg=BLACK
        ).pack(anchor="w", pady=(0, 12))

        self.form_card = card
        return card

    # ---------- Input Fields ----------

    def field(self, parent, label, placeholder):
        # Create a reusable labeled input field
        tk.Label(
            parent,
            text=label,
            font=("Arial", 9, "bold"),
            bg=WHITE,
            fg=BLACK
        ).pack(anchor="w", pady=(0, 4))

        entry = tk.Entry(
            parent,
            font=("Arial", 10),
            bg=WHITE,
            fg=GRAY,
            insertbackground=BLACK,
            relief="solid",
            bd=1
        )
        entry.pack(fill="x", ipady=6, pady=(0, 9))

        # Insert and store the placeholder text
        entry.insert(0, placeholder)
        entry.placeholder = placeholder

        # Remove the placeholder when the user clicks the field
        def focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=BLACK)

        # Restore the placeholder when the field is left empty
        def focus_out(event):
            if not entry.get().strip():
                entry.delete(0, tk.END)
                entry.insert(0, placeholder)
                entry.config(fg=GRAY)

        # Connect the focus events to their functions
        entry.bind("<FocusIn>", focus_in)
        entry.bind("<FocusOut>", focus_out)

        return entry

    @staticmethod
    def value(entry):
        # Return the actual input without its placeholder
        value = entry.get().strip()
        return "" if value == entry.placeholder else value

    # ---------- Buttons ----------

    def button(self, parent, text, command, primary=True):
        # Create reusable buttons with primary and secondary styles
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=PURPLE if primary else WHITE,
            fg=WHITE if primary else PURPLE,
            activebackground=DARK_PURPLE if primary else BG,
            activeforeground=WHITE if primary else DARK_PURPLE,
            font=("Arial", 10, "bold"),
            relief="flat" if primary else "solid",
            bd=0 if primary else 1,
            highlightbackground=BORDER,
            cursor="hand2",
            pady=10
        )

    def back_button(self, parent):
        # Add a reusable button for returning to the dashboard
        self.button(
            parent,
            "Back to Dashboard",
            self.close,
            primary=False
        ).pack(fill="x", pady=(7, 0))

    # ---------- Security Verification ----------

    def verify_password(self, callback, parent=None):
        """
        Verify the user's six-digit code before performing
        a sensitive transaction.
        """

        # Get the account number of the currently logged-in user
        account_number = wallet.account_number

        if not account_number:
            messagebox.showerror(
                "Verification Error",
                "No active wallet account was found.",
                parent=self.root
            )
            return

        # Create a separate verification dialog
        dialog_parent = parent or self.root

        dialog = tk.Toplevel(dialog_parent)
        dialog.title("Security Verification")
        dialog.geometry("340x320")
        dialog.resizable(False, False)
        dialog.configure(bg=BG)
        dialog.transient(dialog_parent)
        apply_icon(dialog)

        tk.Label(
            dialog,
            text="Security Verification",
            font=("Arial", 14, "bold"),
            bg=BG,
            fg=BLACK
        ).pack(pady=(20, 6))

        tk.Label(
            dialog,
            text="Enter the 6-digit verification code.",
            font=("Arial", 9),
            bg=BG,
            fg=GRAY
        ).pack()

        # Demo code is displayed because this application
        # does not yet have SMS or email integration.
        code_label = tk.Label(
            dialog,
            text="",
            font=("Arial", 16, "bold"),
            bg=BG,
            fg=PURPLE
        )
        code_label.pack(pady=10)

        # Accept only numeric input up to six digits.
        def validate_code(value):
            return value == "" or (
                value.isdigit() and len(value) <= 6
            )

        validation = (
            dialog.register(validate_code),
            "%P"
        )

        entry = tk.Entry(
            dialog,
            font=("Arial", 14),
            justify="center",
            validate="key",
            validatecommand=validation
        )
        entry.pack(fill="x", padx=25, ipady=7)

        # Safely close the verification dialog
        def close_dialog():
            try:
                if dialog.winfo_exists():
                    try:
                        dialog.grab_release()
                    except tk.TclError:
                        pass

                    dialog.destroy()

            except tk.TclError:
                pass

        # Generate and display a new verification code
        def new_code():
            try:
                code = verification.issue(account_number)

            except PermissionError as error:
                messagebox.showerror(
                    "Verification Locked",
                    str(error),
                    parent=dialog
                )
                close_dialog()
                return False

            code_label.config(text=f"Demo code: {code}")
            entry.delete(0, tk.END)
            entry.focus_set()

            return True

        # Check the entered code before allowing the transaction
        def verify():
            entered_code = entry.get().strip()

            if len(entered_code) != 6:
                messagebox.showerror(
                    "Verification Failed",
                    "Please enter the complete 6-digit code.",
                    parent=dialog
                )
                entry.focus_set()
                return

            # Compare the entered code with the issued code
            ok, message = verification.check(
                account_number,
                entered_code
            )

            if ok:
                # Close the dialog and execute the requested action
                close_dialog()
                callback()
                return

            messagebox.showerror(
                "Verification Failed",
                message,
                parent=dialog
            )

            entry.delete(0, tk.END)

            # Handle locked, expired, or invalid verification codes
            if "Locked" in message or "Too many" in message:
                close_dialog()

            elif "expired" in message or "No active" in message:
                new_code()

            else:
                entry.focus_set()

        # Prevent the dialog from closing without releasing its grab
        dialog.protocol("WM_DELETE_WINDOW", close_dialog)

        self.button(
            dialog,
            "Verify and Continue",
            verify
        ).pack(fill="x", padx=25, pady=(14, 6))

        self.button(
            dialog,
            "Send New Code",
            new_code,
            primary=False
        ).pack(fill="x", padx=25)

        # Allow the Enter key to submit the verification code
        entry.bind("<Return>", lambda event: verify())

        # Generate the first code.
        if new_code():
            center_on(dialog, dialog_parent)
            safe_grab(dialog)

    # ---------- Receipt ----------

    def show_receipt(self, title, details=""):
        """
        Save and display the latest successful transaction receipt.
        """

        # Do not display a receipt if the service window is already closed
        if self._closed:
            return

        # Retrieve the latest transaction and prepare its receipt
        try:
            transactions = wallet.get_transactions()

            if not transactions:
                messagebox.showerror(
                    "Receipt Error",
                    "No transaction record was found.",
                    parent=self.root
                )
                return

            latest_transaction = transactions[-1]

            # Create and save the transaction receipt
            receipt = create_receipt(
                wallet,
                latest_transaction,
                wallet.get_balance(),
                details
            )

            save_receipt(receipt)

        except (ValueError, OSError, KeyError, TypeError) as error:
            messagebox.showwarning(
                "Receipt Not Saved",
                "Your transaction was completed, but the receipt "
                f"could not be saved:\n\n{error}",
                parent=self.root
            )
            return

        # Open the receipt in a separate window
        try:
            receipt_window = ReceiptWindow(
                self.root,
                receipt,
                title="Transaction Receipt",
                heading=title
            )

            self.root.wait_window(receipt_window)

        except tk.TclError:
            pass

    # ---------- Balance Notification ----------

    def notify_balance_changed(self):
        # Update the service window's displayed balance
        self.update_balance()

        # Notify the dashboard to refresh its balance
        if self.on_balance_change:
            self.on_balance_change()

    # ---------- Closing ----------

    def close(self):
        # Prevent the back callback from running more than once.
        if self._closed:
            return

        self._closed = True

        # Release the window grab and destroy the service window
        try:
            if self.root.winfo_exists():
                try:
                    self.root.grab_release()
                except tk.TclError:
                    pass

                self.root.destroy()

        except tk.TclError:
            pass

        # Notify the dashboard only once.
        if self.on_back:
            self.on_back()