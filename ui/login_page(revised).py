import tkinter as tk
from tkinter import messagebox

import session
import users
from ui.theme import (
    PURPLE, DARK_PURPLE, BG, BLACK, GRAY, BORDER, WHITE,
    apply_icon, load_logo, safe_grab, center_on
)


# ---------- Sign Up window ----------
class SignUpWindow(tk.Toplevel):
    def __init__(self, parent, on_created=None):
        super().__init__(parent)
        self.on_created = on_created

        self.title("CICO - Create Account")
        self.configure(bg=WHITE)
        self.resizable(False, False)
        self.transient(parent)
        apply_icon(self)

        body = tk.Frame(self, bg=WHITE, padx=40, pady=26)
        body.pack()

        tk.Label(
            body, text="Create your account",
            font=("Arial", 18, "bold"), bg=WHITE, fg=BLACK
        ).pack(anchor="w")

        tk.Label(
            body,
            text="Log in later with your email, phone number, or wallet ID.",
            font=("Arial", 9), bg=WHITE, fg=GRAY
        ).pack(anchor="w", pady=(2, 16))

        self.name_entry = self.add_field(body, "Full Name")
        self.email_entry = self.add_field(body, "Email Address")
        self.phone_entry = self.add_field(body, "Phone Number")
        self.password_entry = self.add_field(
            body, "Password (at least 8 characters)", secret=True
        )
        self.confirm_entry = self.add_field(
            body, "Confirm Password", secret=True
        )

        self.show_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            body, text="Show passwords", variable=self.show_var,
            command=self.toggle_passwords, font=("Arial", 9),
            bg=WHITE, fg=GRAY, activebackground=WHITE, selectcolor=WHITE
        ).pack(anchor="w", pady=(0, 12))

        tk.Button(
            body, text="Create Account", command=self.submit,
            bg=PURPLE, fg=WHITE, activebackground=DARK_PURPLE,
            activeforeground=WHITE, font=("Arial", 11, "bold"),
            relief="flat", bd=0, cursor="hand2"
        ).pack(fill="x", ipady=10)

        tk.Label(
            body, text="Your wallet ID is created for you automatically.",
            font=("Arial", 8), bg=WHITE, fg=GRAY
        ).pack(pady=(10, 0))

        back_row = tk.Frame(body, bg=WHITE)
        back_row.pack(pady=(8, 0))

        tk.Label(
            back_row, text="Already have an account?",
            font=("Arial", 9), bg=WHITE, fg=GRAY
        ).pack(side="left")

        tk.Button(
            back_row, text="Log In", command=self.close,
            bg=WHITE, fg=PURPLE, activebackground=WHITE,
            activeforeground=DARK_PURPLE, relief="flat", bd=0,
            cursor="hand2", font=("Arial", 9, "bold")
        ).pack(side="left", padx=(4, 0))

        self.bind("<Return>", lambda event: self.submit())
        self.bind("<Escape>", lambda event: self.close())
        self.protocol("WM_DELETE_WINDOW", self.close)

        center_on(self, parent)
        safe_grab(self)
        self.name_entry.focus_set()

    @staticmethod
    def add_field(parent, label, secret=False):
        tk.Label(
            parent, text=label, font=("Arial", 10, "bold"),
            bg=WHITE, fg=BLACK
        ).pack(anchor="w")

        entry = tk.Entry(
            parent, font=("Arial", 11), relief="solid", bd=1,
            show="*" if secret else "", width=34
        )
        entry.pack(fill="x", ipady=7, pady=(4, 12))
        return entry

    def toggle_passwords(self):
        show = "" if self.show_var.get() else "*"
        self.password_entry.config(show=show)
        self.confirm_entry.config(show=show)

    def close(self):
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()

    def submit(self):
        try:
            user = users.register_user(
                self.name_entry.get(),
                self.email_entry.get(),
                self.phone_entry.get(),
                self.password_entry.get(),
                self.confirm_entry.get(),
            )
        except ValueError as error:
            messagebox.showerror("Sign Up Failed", str(error), parent=self)
            return
        except OSError as error:
            messagebox.showerror(
                "Sign Up Failed",
                f"Your account could not be saved:\n{error}",
                parent=self
            )
            return

        messagebox.showinfo(
            "Account Created",
            f"Welcome, {user['account_name']}!\n\n"
            f"Wallet ID: {user['account_number']}\n"
            f"Email: {user['email']}\n"
            f"Phone: {user['phone']}\n\n"
            "You can now log in with your email, phone number, "
            "or wallet ID.",
            parent=self
        )
        self.close()

        if self.on_created:
            self.on_created(user)


# ---------- Login page ----------
class LoginPage:
    def __init__(self, root, on_success=None):
        self.root = root
        self.on_success = on_success
        self.show_password = False
        self.logo_image = None

        session.clear_user()  # nobody is logged in on the login screen

        self.root.configure(bg=BG)
        self.root.minsize(850, 700)  # the login card needs this much height
        apply_icon(self.root)

        self.container = tk.Frame(self.root, bg=BG)
        self.container.pack(fill="both", expand=True, padx=35, pady=20)

        self.build_ui()

    def build_ui(self):
        card = tk.Frame(
            self.container, bg=WHITE,
            highlightbackground=BORDER, highlightthickness=1
        )
        card.place(relx=0.5, rely=0.5, anchor="center", width=440, height=650)

        # Logo (falls back to a letter if the image is missing)
        logo_area = tk.Frame(card, bg=WHITE)
        logo_area.pack(pady=(28, 8))

        self.logo_image = load_logo(120)

        if self.logo_image is not None:
            tk.Label(logo_area, image=self.logo_image, bg=WHITE).pack()
        else:
            tk.Label(
                logo_area, text="C", font=("Arial", 32, "bold"),
                bg=PURPLE, fg=WHITE, width=2, height=1
            ).pack()

        tk.Label(
            card, text="CICO", font=("Arial", 24, "bold"),
            bg=WHITE, fg=PURPLE
        ).pack(pady=(0, 2))

        tk.Label(
            card, text="E - W A L L E T", font=("Arial", 9, "bold"),
            bg=WHITE, fg=GRAY
        ).pack()

        tk.Label(
            card, text="Welcome back!", font=("Arial", 21, "bold"),
            bg=WHITE, fg=BLACK
        ).pack(pady=(22, 5))

        tk.Label(
            card, text="Log in to continue to your CICO account.",
            font=("Arial", 10), bg=WHITE, fg=GRAY
        ).pack(pady=(0, 20))

        # Email / phone / wallet ID
        tk.Label(
            card, text="Email, Phone Number or Wallet ID",
            font=("Arial", 10, "bold"), bg=WHITE, fg=BLACK
        ).pack(anchor="w", padx=42)

        self.email_entry = tk.Entry(
            card, font=("Arial", 11), relief="solid", bd=1,
            highlightthickness=0
        )
        self.email_entry.pack(fill="x", padx=42, ipady=10, pady=(7, 16))

        # Password with a Show / Hide button
        tk.Label(
            card, text="Password", font=("Arial", 10, "bold"),
            bg=WHITE, fg=BLACK
        ).pack(anchor="w", padx=42)

        password_row = tk.Frame(card, bg=WHITE)
        password_row.pack(fill="x", padx=42, pady=(7, 8))

        self.password_entry = tk.Entry(
            password_row, font=("Arial", 11), show="*",
            relief="solid", bd=1
        )
        self.password_entry.pack(side="left", fill="x", expand=True, ipady=9)

        self.toggle_button = tk.Button(
            password_row, text="Show",
            command=self.toggle_password_visibility,
            bg=WHITE, fg=PURPLE, activebackground=WHITE,
            activeforeground=DARK_PURPLE, relief="flat", bd=0,
            cursor="hand2", font=("Arial", 9, "bold")
        )
        self.toggle_button.pack(side="right", padx=(5, 0))

        # Remember me: keeps the email / phone / wallet ID (not the password)
        self.remember_var = tk.BooleanVar(value=False)

        tk.Checkbutton(
            card, text="Remember me", variable=self.remember_var,
            font=("Arial", 9), bg=WHITE, fg=GRAY,
            activebackground=WHITE, selectcolor=WHITE
        ).pack(anchor="w", padx=38, pady=(0, 18))

        tk.Button(
            card, text="Log In", command=self.login,
            bg=PURPLE, fg=WHITE, activebackground=DARK_PURPLE,
            activeforeground=WHITE, font=("Arial", 11, "bold"),
            relief="flat", bd=0, cursor="hand2"
        ).pack(fill="x", padx=42, ipady=11)

        # Sign up link
        signup_row = tk.Frame(card, bg=WHITE)
        signup_row.pack(pady=(14, 0))

        tk.Label(
            signup_row, text="Don't have an account?",
            font=("Arial", 9), bg=WHITE, fg=GRAY
        ).pack(side="left")

        tk.Button(
            signup_row, text="Sign Up", command=self.open_signup,
            bg=WHITE, fg=PURPLE, activebackground=WHITE,
            activeforeground=DARK_PURPLE, relief="flat", bd=0,
            cursor="hand2", font=("Arial", 9, "bold")
        ).pack(side="left", padx=(4, 0))

        tk.Label(
            card, text="CICO E-Wallet | Demo Application",
            font=("Arial", 8), bg=WHITE, fg=GRAY
        ).pack(side="bottom", pady=18)

        # Fill in the remembered account, if there is one
        remembered = users.get_remembered_identifier()
        if remembered:
            self.email_entry.insert(0, remembered)
            self.remember_var.set(True)
            self.password_entry.focus_set()
        else:
            self.email_entry.focus_set()

        self.root.bind("<Return>", lambda event: self.login())

    def open_signup(self):
        SignUpWindow(self.root, on_created=self.account_created)

    def account_created(self, user):
        # Fill in the login form with the new account's email
        self.email_entry.delete(0, tk.END)
        self.email_entry.insert(0, user["email"])
        self.password_entry.delete(0, tk.END)
        self.password_entry.focus_set()

    def toggle_password_visibility(self):
        self.show_password = not self.show_password

        if self.show_password:
            self.password_entry.config(show="")
            self.toggle_button.config(text="Hide")
        else:
            self.password_entry.config(show="*")
            self.toggle_button.config(text="Show")

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

        user = users.authenticate(identifier, password)

        if user is None:
            if users.users_file_exists():
                message = "Incorrect email, phone number, wallet ID, or password."
            else:
                message = f"User file not found:\n{users.USERS_FILE}"

            messagebox.showerror("Login Failed", message, parent=self.root)
            self.password_entry.delete(0, tk.END)
            self.password_entry.focus_set()
            return

        # Remember (or forget) the account for next time
        users.set_remembered_identifier(
            identifier if self.remember_var.get() else ""
        )

        session.set_user(user)
        self.root.unbind("<Return>")

        if self.on_success:
            self.on_success(user["account_name"])
