import tkinter as tk
from tkinter import messagebox
from pathlib import Path


class LoginPage:
    def __init__(self, root):
        self.root = root

        # CICO color palette
        self.purple = "#7040E8"
        self.purple_hover = "#5930C7"
        self.background = "#F8F7FF"
        self.dark = "#171A35"
        self.gray = "#777C91"
        self.border = "#E2E0ED"
        self.white = "#FFFFFF"

        # Window settings
        self.root.title("CICO E-Wallet - Login")
        self.root.configure(bg=self.background)

        # Main container
        self.container = tk.Frame(
            self.root,
            bg=self.background
        )

        self.container.pack(
            fill="both",
            expand=True,
            padx=55,
            pady=15
        )

        # Create interface sections
        self.create_header()
        self.create_login_form()
        self.create_footer()

    def create_header(self):
        # Find the logo file
        project_folder = Path(__file__).resolve().parent.parent
        logo_path = project_folder / "assets" / "logo-cico.png"

        print("Logo path:", logo_path)
        print("Logo file exists:", logo_path.exists())

        # Load logo safely
        self.logo_image = None

        try:
            self.logo_image = tk.PhotoImage(
                master=self.root,
                file=str(logo_path)
            )

            # Resize large images using Tkinter
            max_size = 120

            scale = max(
                1,
                (self.logo_image.width() + max_size - 1) // max_size,
                (self.logo_image.height() + max_size - 1) // max_size
            )

            if scale > 1:
                self.logo_image = self.logo_image.subsample(
                    scale,
                    scale
                )

            tk.Label(
                self.container,
                image=self.logo_image,
                bg=self.background
            ).pack(pady=(0, 5))

            print("SUCCESS: Logo loaded!")

        except Exception as error:
            print("LOGO ERROR:", repr(error))

            # Display a fallback logo if the image fails
            tk.Label(
                self.container,
                text="C",
                font=("Arial", 32, "bold"),
                fg=self.white,
                bg=self.purple,
                width=2,
                height=1
            ).pack(pady=(0, 5))

        # CICO branding
        tk.Label(
            self.container,
            text="CICO",
            font=("Arial", 24, "bold"),
            fg=self.dark,
            bg=self.background
        ).pack()

        tk.Label(
            self.container,
            text="E - W A L L E T",
            font=("Arial", 9, "bold"),
            fg=self.purple,
            bg=self.background
        ).pack(pady=(0, 12))

        # Welcome message
        tk.Label(
            self.container,
            text="Welcome back!",
            font=("Arial", 21, "bold"),
            fg=self.dark,
            bg=self.background
        ).pack()

        tk.Label(
            self.container,
            text="Log in to continue to your account",
            font=("Arial", 10),
            fg=self.gray,
            bg=self.background
        ).pack(pady=(5, 15))

    def create_login_form(self):
        # Email or phone number
        tk.Label(
            self.container,
            text="Email or Phone Number",
            font=("Arial", 10, "bold"),
            fg=self.dark,
            bg=self.background,
            anchor="w"
        ).pack(fill="x")

        self.email_entry = tk.Entry(
            self.container,
            font=("Arial", 12),
            bg=self.white,
            fg=self.dark,
            insertbackground=self.dark,
            relief="solid",
            bd=1,
            highlightthickness=1,
            highlightbackground=self.border,
            highlightcolor=self.purple
        )

        self.email_entry.pack(
            fill="x",
            ipady=7,
            pady=(5, 10)
        )

        # Password label
        tk.Label(
            self.container,
            text="Password",
            font=("Arial", 10, "bold"),
            fg=self.dark,
            bg=self.background,
            anchor="w"
        ).pack(fill="x")

        # Password field container
        password_frame = tk.Frame(
            self.container,
            bg=self.white,
            highlightthickness=1,
            highlightbackground=self.border
        )

        password_frame.pack(
            fill="x",
            pady=(5, 8)
        )

        self.password_entry = tk.Entry(
            password_frame,
            font=("Arial", 12),
            bg=self.white,
            fg=self.dark,
            insertbackground=self.dark,
            relief="flat",
            show="*"
        )

        self.password_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(8, 0),
            ipady=7
        )

        # Show or hide password
        self.show_password = False

        self.show_button = tk.Button(
            password_frame,
            text="Show",
            font=("Arial", 9),
            fg=self.purple,
            bg=self.white,
            activebackground=self.white,
            relief="flat",
            cursor="hand2",
            command=self.toggle_password
        )

        self.show_button.pack(
            side="right",
            padx=5
        )

        # Remember me and forgot password
        options_frame = tk.Frame(
            self.container,
            bg=self.background
        )

        options_frame.pack(
            fill="x",
            pady=(0, 12)
        )

        self.remember_var = tk.BooleanVar(value=False)

        tk.Checkbutton(
            options_frame,
            text="Remember me",
            variable=self.remember_var,
            font=("Arial", 9),
            fg=self.dark,
            bg=self.background,
            activebackground=self.background,
            selectcolor=self.white,
            cursor="hand2"
        ).pack(side="left")

        tk.Button(
            options_frame,
            text="Forgot Password?",
            font=("Arial", 9),
            fg=self.purple,
            bg=self.background,
            activebackground=self.background,
            relief="flat",
            cursor="hand2",
            command=self.forgot_password
        ).pack(side="right")

        # Login button
        self.login_button = tk.Button(
            self.container,
            text="Log In",
            font=("Arial", 12, "bold"),
            fg=self.white,
            bg=self.purple,
            activeforeground=self.white,
            activebackground=self.purple_hover,
            relief="flat",
            cursor="hand2",
            command=self.login,
            pady=9
        )

        self.login_button.pack(fill="x")

    def create_footer(self):
        # Social login separator
        tk.Label(
            self.container,
            text="────── or continue with ──────",
            font=("Arial", 9),
            fg=self.gray,
            bg=self.background
        ).pack(pady=12)

        # Social login buttons
        social_frame = tk.Frame(
            self.container,
            bg=self.background
        )

        social_frame.pack(fill="x")

        tk.Button(
            social_frame,
            text="Google",
            font=("Arial", 10, "bold"),
            fg=self.dark,
            bg=self.white,
            activebackground="#F0EEF8",
            relief="solid",
            bd=1,
            cursor="hand2",
            command=lambda: self.not_implemented("Google login")
        ).pack(
            side="left",
            fill="x",
            expand=True,
            ipady=6,
            padx=(0, 5)
        )

        tk.Button(
            social_frame,
            text="Apple",
            font=("Arial", 10, "bold"),
            fg=self.dark,
            bg=self.white,
            activebackground="#F0EEF8",
            relief="solid",
            bd=1,
            cursor="hand2",
            command=lambda: self.not_implemented("Apple login")
        ).pack(
            side="left",
            fill="x",
            expand=True,
            ipady=6,
            padx=(5, 0)
        )

        # Sign-up prompt
        signup_frame = tk.Frame(
            self.container,
            bg=self.background
        )

        signup_frame.pack(pady=12)

        tk.Label(
            signup_frame,
            text="Don't have an account?",
            font=("Arial", 9),
            fg=self.gray,
            bg=self.background
        ).pack(side="left")

        tk.Button(
            signup_frame,
            text="Sign Up",
            font=("Arial", 9, "bold"),
            fg=self.purple,
            bg=self.background,
            activebackground=self.background,
            relief="flat",
            cursor="hand2",
            command=self.open_signup
        ).pack(
            side="left",
            padx=4
        )

    def toggle_password(self):
        # Switch between hidden and visible password
        self.show_password = not self.show_password

        if self.show_password:
            self.password_entry.config(show="")
            self.show_button.config(text="Hide")
        else:
            self.password_entry.config(show="*")
            self.show_button.config(text="Show")

    def login(self):
        # Get the entered information
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        # Check for empty fields
        if not email or not password:
            messagebox.showwarning(
                "Missing Information",
                "Please enter your email or phone number "
                "and password.",
                parent=self.root
            )
            return

        # Database authentication will be added later
        messagebox.showinfo(
            "CICO E-Wallet",
            "The login interface is working!\n\n"
            "Database authentication has not been connected yet.",
            parent=self.root
        )

    def forgot_password(self):
        messagebox.showinfo(
            "Forgot Password",
            "Password recovery will be implemented later.",
            parent=self.root
        )

    def open_signup(self):
        messagebox.showinfo(
            "Create Account",
            "The registration interface will be implemented next.",
            parent=self.root
        )

    def not_implemented(self, feature):
        messagebox.showinfo(
            feature,
            f"{feature} is not connected yet.",
            parent=self.root
        )
