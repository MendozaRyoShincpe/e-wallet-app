import os
import tkinter as tk
from tkinter import messagebox
from wallet import wallet

# Define paths for the logo and application icon.
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_FILE = os.path.join(BASE, "CICO.png")
ICON_FILE = os.path.join(BASE, "CICO.ico")

# Define the application's theme colors.
PURPLE = "#7040E8"
DARK_PURPLE = "#5930C7"
WHITE = "#FFFFFF"
BLACK = "#171A35"
BG = "#F8F7FF"
GRAY = "#777C91"
BORDER = "#E2E0ED"
GREEN = "#16805D"

# Demo security password used for transaction verification.
PASSWORD = "secure123"


# Base class containing reusable UI components for wallet services.
class ServiceWindow:
    def __init__(
        self,
        parent,
        title,
        subtitle,
        on_back=None,
        on_balance_change=None
    ):
        self.parent = parent
        self.on_back = on_back
        self.on_balance_change = on_balance_change
        self.logo_image = None

        # Create a separate window for the selected wallet service.
        self.root = tk.Toplevel(parent)
        self.root.title(f"CICO - {title}")
        self.root.geometry("420x600")
        self.root.minsize(400, 650)
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        # Load the application icon if the file exists.
        try:
            if os.path.exists(ICON_FILE):
                self.root.iconbitmap(ICON_FILE)
        except tk.TclError:
            pass

        # Build the shared interface elements.
        self.load_logo()
        self.build_header(title, subtitle)

        self.content = tk.Frame(
            self.root, bg=BG, padx=20, pady=15
        )
        self.content.pack(fill="both", expand=True)

        self.build_balance_card()

        tk.Label(
            self.root,
            text="CICO E-Wallet | Demo Application",
            font=("Arial", 8),
            bg=BG,
            fg=GRAY
        ).pack(pady=(0, 8))

        # Keep the service window connected to its parent window.
        self.root.transient(parent)
        self.root.grab_set()

    def load_logo(self):
        # Load and resize the logo for display in the interface.
        if not os.path.exists(LOGO_FILE):
            print(f"CICO logo not found: {LOGO_FILE}")
            return

        try:
            from PIL import Image, ImageTk

            image = Image.open(LOGO_FILE).convert("RGBA")
            image.thumbnail((38, 38), Image.Resampling.LANCZOS)
            self.logo_image = ImageTk.PhotoImage(image)

        except Exception as error:
            print(f"Could not load CICO logo: {error}")

    def build_header(self, title, subtitle):
        # Create the reusable header with the logo, title, and close button.
        header = tk.Frame(
            self.root, bg=PURPLE, padx=20, pady=14
        )
        header.pack(fill="x")

        brand_row = tk.Frame(header, bg=PURPLE)
        brand_row.pack(fill="x")

        if self.logo_image is not None:
            tk.Label(
                brand_row,
                image=self.logo_image,
                bg=PURPLE
            ).pack(side="left", padx=(0, 8))

        tk.Label(
            brand_row,
            text="CICO",
            font=("Arial", 20, "bold"),
            bg=PURPLE,
            fg=WHITE
        ).pack(side="left")

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

    def build_balance_card(self):
        # Display the wallet's available balance.
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

        # Display the current balance from the shared wallet.
        self.update_balance()

    def update_balance(self):
        # Refresh the displayed balance after a wallet transaction.
        try:
            self.balance_label.config(
                text=f"₱{wallet.get_balance():,.2f}"
            )
        except (tk.TclError, AttributeError):
            pass

    def build_form_card(self, title):
        # Create a reusable card for service forms.
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

    def field(self, parent, label, placeholder):
        # Create an input field with a label and placeholder text.
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
        entry.insert(0, placeholder)
        entry.placeholder = placeholder

        # Clear the placeholder when the user selects the field.
        def focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=BLACK)

        # Restore the placeholder if the field is left empty.
        def focus_out(event):
            if not entry.get().strip():
                entry.insert(0, placeholder)
                entry.config(fg=GRAY)

        entry.bind("<FocusIn>", focus_in)
        entry.bind("<FocusOut>", focus_out)
        return entry

    @staticmethod
    def value(entry):
        # Return the user's input without treating placeholder text as data.
        value = entry.get().strip()
        return "" if value == entry.placeholder else value

    def button(self, parent, text, command, primary=True):
        # Create a reusable button with the application's theme.
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
        # Create a button that closes the service window.
        self.button(
            parent,
            "Back to Dashboard",
            self.close,
            primary=False
        ).pack(fill="x", pady=(7, 0))

    def verify_password(self, callback):
        # Open a dialog requiring the demo security password.
        dialog = tk.Toplevel(self.root)
        dialog.title("Security Verification")
        dialog.geometry("340x220")
        dialog.resizable(False, False)
        dialog.configure(bg=BG)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Security Verification",
            font=("Arial", 14, "bold"),
            bg=BG,
            fg=BLACK
        ).pack(pady=(20, 8))

        tk.Label(
            dialog,
            text="Enter your security password.",
            font=("Arial", 9),
            bg=BG,
            fg=GRAY
        ).pack(pady=(0, 12))

        # Hide the password characters as the user types.
        entry = tk.Entry(
            dialog,
            show="*",
            font=("Arial", 11),
            justify="center"
        )
        entry.pack(fill="x", padx=25, ipady=7)
        entry.focus_set()

        def verify():
            # Check the entered password before continuing.
            if entry.get() != PASSWORD:
                messagebox.showerror(
                    "Verification Failed",
                    "Incorrect security password.",
                    parent=dialog
                )
                entry.delete(0, tk.END)
                entry.focus_set()
                return

            # Close the dialog and execute the requested action.
            dialog.destroy()
            callback()

        self.button(
            dialog, "Verify and Continue", verify
        ).pack(fill="x", padx=25, pady=14)

        # Allow the user to submit the password by pressing Enter.
        entry.bind("<Return>", lambda event: verify())

    def show_receipt(self, title, details):
        # Display a message box containing transaction details.
        messagebox.showinfo(
            title, details, parent=self.root
        )

    def notify_balance_changed(self):
        # Update this window and notify the parent when the balance changes.
        self.update_balance()

        if self.on_balance_change:
            self.on_balance_change()

    def close(self):
        # Safely close the service window and release its input grab.
        try:
            if self.root.winfo_exists():
                try:
                    self.root.grab_release()
                except tk.TclError:
                    pass

                self.root.destroy()
        except tk.TclError:
            pass

        # Run the back callback if one was provided.
        if self.on_back:
            self.on_back()
