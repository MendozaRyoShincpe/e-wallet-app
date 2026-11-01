import tkinter as tk
from tkinter import messagebox

from ui.account_store import authenticate

from ui.theme import (
    PURPLE,
    DARK_PURPLE,
    BG,
    BLACK,
    GRAY,
    BORDER,
    WHITE,
    apply_icon,
    load_logo
)


# Handles user login and authentication
class LoginPage:
    def __init__(self, root, on_success=None):
        self.root = root
        self.on_success = on_success

        self.show_password = False
        self.current_user = None
        self.logo_image = None
        self.container = None

        self.root.configure(bg=BG)
        self.root.minsize(850, 700)

        apply_icon(self.root)

        self.show_login()

    # Displays the login page and restores previously entered email
    def show_login(self, email=""):
        self.container = tk.Frame(self.root, bg=BG)
        self.container.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=20
        )

        self.show_password = False
        self.build_ui()

        if email:
            self.email_entry.insert(0, email)
            self.password_entry.focus_set()
        else:
            self.email_entry.focus_set()

    # Builds the login interface and its input fields
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
            height=650
        )

        # ---------- Logo ----------
        logo_area = tk.Frame(card, bg=WHITE)
        logo_area.pack(pady=(28, 8))

        self.logo_image = load_logo(120)

        if self.logo_image is not None:
            tk.Label(
                logo_area,
                image=self.logo_image,
                bg=WHITE
            ).pack()

        else:
            tk.Label(
                logo_area,
                text="C",
                font=("Arial", 32, "bold"),
                bg=PURPLE,
                fg=WHITE,
                width=2,
                height=1
            ).pack()

        tk.Label(
            card,
            text="CICO",
            font=("Arial", 24, "bold"),
            bg=WHITE,
            fg=PURPLE
        ).pack(pady=(0, 2))

        tk.Label(
            card,
            text="E - W A L L E T",
            font=("Arial", 9, "bold"),
            bg=WHITE,
            fg=GRAY
        ).pack()

        # ---------- Welcome Message ----------
        tk.Label(
            card,
            text="Welcome back!",
            font=("Arial", 21, "bold"),
            bg=WHITE,
            fg=BLACK
        ).pack(pady=(22, 5))

        tk.Label(
            card,
            text="Log in to continue to your CICO account.",
            font=("Arial", 10),
            bg=WHITE,
            fg=GRAY
        ).pack(pady=(0, 20))

        # ---------- Account Identifier ----------
        tk.Label(
            card,
            text="Email or Phone Number",
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=BLACK
        ).pack(anchor="w", padx=42)

        self.email_entry = tk.Entry(
            card,
            font=("Arial", 11),
            relief="solid",
            bd=1,
            highlightthickness=0
        )

        self.email_entry.pack(
            fill="x",
            padx=42,
            ipady=10,
            pady=(7, 16)
        )

        # ---------- Password ----------
        tk.Label(
            card,
            text="Password",
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=BLACK
        ).pack(anchor="w", padx=42)

        password_row = tk.Frame(card, bg=WHITE)
        password_row.pack(
            fill="x",
            padx=42,
            pady=(7, 8)
        )

        self.password_entry = tk.Entry(
            password_row,
            font=("Arial", 11),
            show="*",
            relief="solid",
            bd=1
        )

        self.password_entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=9
        )

        # ---------- Show / Hide Password ----------
        self.toggle_button = tk.Button(
            password_row,
            text="Show",
            command=self.toggle_password_visibility,
            bg=WHITE,
            fg=PURPLE,
            activebackground=WHITE,
            activeforeground=DARK_PURPLE,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 9, "bold")
        )

        self.toggle_button.pack(
            side="right",
            padx=(5, 0)
        )

        # ---------- Login Button ----------
        tk.Button(
            card,
            text="Log In",
            command=self.login,
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
            ipady=11,
            pady=(8, 0)
        )

        # ---------- Registration ----------
        tk.Button(
            card,
            text="Don't have an account? Sign Up",
            command=self.open_registration,
            bg=WHITE,
            fg=PURPLE,
            activebackground=WHITE,
            activeforeground=DARK_PURPLE,
            font=("Arial", 9, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2"
        ).pack(pady=(14, 0))

        # ---------- Footer ----------
        tk.Label(
            card,
            text="CICO E-Wallet | Demo Application",
            font=("Arial", 8),
            bg=WHITE,
            fg=GRAY
        ).pack(side="bottom", pady=18)

        self.root.bind("<Return>", self.handle_enter)

    # Allows users to log in by pressing the Enter key
    def handle_enter(self, event=None):
        self.login()

    # Toggles password visibility between hidden and visible
    def toggle_password_visibility(self):
        self.show_password = not self.show_password

        if self.show_password:
            self.password_entry.config(show="")
            self.toggle_button.config(text="Hide")

        else:
            self.password_entry.config(show="*")
            self.toggle_button.config(text="Show")

    # Opens the registration page
    def open_registration(self):
        self.root.unbind("<Return>")

        if self.container:
            self.container.destroy()

        from ui.register import RegisterPage

        self.register_page = RegisterPage(
            self.root,
            on_back=self.show_login,
            on_registered=self.show_login
        )

    # Checks the user's credentials and handles login
    def login(self):
        identifier = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not identifier:
            messagebox.showwarning(
                "Missing Information",
                "Please enter your email, phone number, or wallet ID.",
                parent=self.root
            )

            self.email_entry.focus_set()
            return

        if not password.strip():
            messagebox.showwarning(
                "Missing Information",
                "Please enter your password.",
                parent=self.root
            )

            self.password_entry.focus_set()
            return

        try:
            user = authenticate(identifier, password)

        except (OSError, ValueError) as error:
            messagebox.showerror(
                "Login Error",
                str(error),
                parent=self.root
            )
            return

        if user is None:
            messagebox.showerror(
                "Login Failed",
                "Incorrect email, phone number, wallet ID, or password.",
                parent=self.root
            )

            self.password_entry.delete(0, tk.END)
            self.password_entry.focus_set()
            return

        # Saves the authenticated user and opens the dashboard
        self.current_user = user

        self.root.unbind("<Return>")

        messagebox.showinfo(
            "Login Successful",
            f"Welcome, {user.get('name', 'User')}!",
            parent=self.root
        )

        if self.on_success:
            self.on_success(user)

    # Returns the currently logged-in user's information
    def get_current_user(self):
        return self.current_user


# Allows login.py to be tested independently
if __name__ == "__main__":
    root = tk.Tk()
    root.title("CICO E-Wallet - Login")
    root.geometry("1100x700")
    root.minsize(850, 700)

    LoginPage(root)
    root.mainloop()