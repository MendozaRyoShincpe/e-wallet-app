import tkinter as tk
from tkinter import messagebox

from ui.account_store import create_account, normalize_phone


PURPLE = "#7040E8"
DARK_PURPLE = "#5930C7"
BACKGROUND = "#F8F7FF"
DARK = "#171A35"
GRAY = "#777C91"
BORDER = "#E2E0ED"
WHITE = "#FFFFFF"


# Handles new user registration and account creation
class RegisterPage:
    def __init__(self, root, on_back, on_registered):
        self.root = root
        self.on_back = on_back
        self.on_registered = on_registered

        self.container = tk.Frame(root, bg=BACKGROUND)
        self.container.pack(fill="both", expand=True, padx=35, pady=15)

        self.build_ui()

    # Builds the registration form and its input fields
    def build_ui(self):
        card = tk.Frame(
            self.container,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )

        card.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
            width=440,
            height=700
        )

        tk.Label(
            card,
            text="CICO",
            font=("Arial", 24, "bold"),
            bg=WHITE,
            fg=PURPLE
        ).pack(pady=(22, 2))

        tk.Label(
            card,
            text="E - W A L L E T",
            font=("Arial", 9, "bold"),
            bg=WHITE,
            fg=GRAY
        ).pack()

        tk.Label(
            card,
            text="Create Account",
            font=("Arial", 21, "bold"),
            bg=WHITE,
            fg=DARK
        ).pack(pady=(15, 5))

        tk.Label(
            card,
            text="Register to start using your CICO wallet.",
            font=("Arial", 10),
            bg=WHITE,
            fg=GRAY
        ).pack(pady=(0, 12))

        self.name_entry = self.add_field(
            card, "Account Name"
        )

        self.email_entry = self.add_field(
            card, "Email Address"
        )

        self.phone_entry = self.add_field(
            card, "Phone Number"
        )

        self.password_entry = self.add_field(
            card, "Password", show="*"
        )

        self.confirm_entry = self.add_field(
            card, "Confirm Password", show="*"
        )

        tk.Button(
            card,
            text="Create Account",
            command=self.register,
            bg=PURPLE,
            fg=WHITE,
            activebackground=DARK_PURPLE,
            activeforeground=WHITE,
            font=("Arial", 11, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2"
        ).pack(
            fill="x",
            padx=42,
            ipady=10,
            pady=(13, 7)
        )

        tk.Button(
            card,
            text="Back to Login",
            command=self.go_back,
            bg=WHITE,
            fg=PURPLE,
            activebackground=WHITE,
            activeforeground=DARK_PURPLE,
            font=("Arial", 9, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2"
        ).pack(pady=4)

        tk.Label(
            card,
            text="CICO E-Wallet | Demo Application",
            font=("Arial", 8),
            bg=WHITE,
            fg=GRAY
        ).pack(side="bottom", pady=12)

        self.name_entry.focus_set()

    # Creates reusable input fields for the registration form
    def add_field(self, parent, label, show=None):
        tk.Label(
            parent,
            text=label,
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=DARK
        ).pack(
            anchor="w",
            padx=42,
            pady=(4, 2)
        )

        entry = tk.Entry(
            parent,
            font=("Arial", 11),
            show=show or "",
            relief="solid",
            bd=1
        )

        entry.pack(
            fill="x",
            padx=42,
            ipady=6,
            pady=(0, 4)
        )

        return entry

    # Validates the user's information before creating an account
    def register(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        phone = self.phone_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()

        if not all([name, email, phone, password, confirm]):
            messagebox.showwarning(
                "Missing Information",
                "Please complete all fields.",
                parent=self.root
            )
            return

        if len(name) < 2:
            messagebox.showwarning(
                "Invalid Account Name",
                "Account name must contain at least 2 characters.",
                parent=self.root
            )
            return

        if (
            "@" not in email
            or "." not in email.split("@")[-1]
            or " " in email
        ):
            messagebox.showwarning(
                "Invalid Email",
                "Please enter a valid email address.",
                parent=self.root
            )
            return

        # Normalizes and validates the Philippine mobile number
        normalized_phone = normalize_phone(phone)

        if (
            not normalized_phone.isascii()
            or not normalized_phone.isdigit()
            or len(normalized_phone) != 11
            or not normalized_phone.startswith("09")
        ):
            messagebox.showwarning(
                "Invalid Phone Number",
                "Please enter a valid 11-digit Philippine mobile number starting with 09.",
                parent=self.root
            )
            return

        if len(password) < 8:
            messagebox.showwarning(
                "Weak Password",
                "Password must contain at least 8 characters.",
                parent=self.root
            )
            return

        if password != confirm:
            messagebox.showerror(
                "Password Mismatch",
                "The passwords do not match.",
                parent=self.root
            )
            return

        # Saves the new account through the account storage module
        try:
            user, error = create_account(
                name,
                email,
                password,
                normalized_phone
            )

        except (ValueError, OSError) as error:
            messagebox.showerror(
                "Registration Error",
                f"Unable to create your account:\n\n{error}",
                parent=self.root
            )
            return

        if error:
            messagebox.showerror(
                "Registration Failed",
                error,
                parent=self.root
            )
            return

        # Displays the generated CICO account number after registration
        messagebox.showinfo(
            "Registration Successful",
            f"Welcome to CICO, {user['name']}!\n\n"
            f"CICO Account Number: {user['account_number']}\n\n"
            "Your registered phone number is now your CICO Account Number.\n\n"
            "Keep this number because you will need it to receive money.",
            parent=self.root
        )

        self.container.destroy()
        self.on_registered(email)

    # Returns the user to the login page
    def go_back(self):
        self.container.destroy()
        self.on_back()