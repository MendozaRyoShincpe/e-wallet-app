import os
import tkinter as tk
from tkinter import messagebox


# ---------- Paths ----------
BASE = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

LOGO_FILE = os.path.join(BASE, "CICO.png")
ICON_FILE = os.path.join(BASE, "CICO.ico")


# ---------- Theme ----------
PURPLE = "#7040E8"
DARK_PURPLE = "#5930C7"
BACKGROUND = "#F8F7FF"
DARK = "#171A35"
GRAY = "#777C91"
BORDER = "#E2E0ED"
WHITE = "#FFFFFF"


class LoginPage:
    def __init__(self, root, on_success=None):
        self.root = root
        self.on_success = on_success
        self.show_password = False

        self.root.configure(bg=BACKGROUND)

        try:
            if os.path.exists(ICON_FILE):
                self.root.iconbitmap(ICON_FILE)
        except tk.TclError:
            pass

        self.container = tk.Frame(
            self.root,
            bg=BACKGROUND
        )
        self.container.pack(
            fill="both",
            expand=True,
            padx=35,
            pady=20
        )

        self.build_ui()

    def build_ui(self):
        # Main login card
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
            height=610
        )

        # Logo
        logo_area = tk.Frame(card, bg=WHITE)
        logo_area.pack(pady=(28, 8))

        self.logo_image = None

        if os.path.exists(LOGO_FILE):
            try:
                self.logo_image = tk.PhotoImage(
                    file=LOGO_FILE
                )

                # Scale down large logos while retaining aspect ratio.
                width = self.logo_image.width()
                height = self.logo_image.height()
                scale = max(
                    1,
                    (max(width, height) + 119) // 120
                )

                if scale > 1:
                    self.logo_image = self.logo_image.subsample(
                        scale, scale
                    )

                tk.Label(
                    logo_area,
                    image=self.logo_image,
                    bg=WHITE
                ).pack()
            except tk.TclError:
                self.logo_image = None

        if self.logo_image is None:
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

        tk.Label(
            card,
            text="Welcome back!",
            font=("Arial", 21, "bold"),
            bg=WHITE,
            fg=DARK
        ).pack(pady=(22, 5))

        tk.Label(
            card,
            text="Log in to continue to your CICO account.",
            font=("Arial", 10),
            bg=WHITE,
            fg=GRAY
        ).pack(pady=(0, 20))

        # Email / phone
        tk.Label(
            card,
            text="Email or Phone Number",
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=DARK
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

        # Password
        tk.Label(
            card,
            text="Password",
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=DARK
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
        self.toggle_button.pack(side="right", padx=(5, 0))

        # Remember me
        self.remember_var = tk.BooleanVar(value=False)

        tk.Checkbutton(
            card,
            text="Remember me",
            variable=self.remember_var,
            font=("Arial", 9),
            bg=WHITE,
            fg=GRAY,
            activebackground=WHITE,
            selectcolor=WHITE
        ).pack(anchor="w", padx=38, pady=(0, 18))

        # Login button
        login_button = tk.Button(
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
        )
        login_button.pack(
            fill="x",
            padx=42,
            ipady=11
        )

        tk.Label(
            card,
            text="CICO E-Wallet | Demo Application",
            font=("Arial", 8),
            bg=WHITE,
            fg=GRAY
        ).pack(side="bottom", pady=18)

        self.email_entry.focus_set()

        self.root.bind(
            "<Return>",
            lambda event: self.login()
        )

    def toggle_password_visibility(self):
        self.show_password = not self.show_password

        if self.show_password:
            self.password_entry.config(show="")
            self.toggle_button.config(text="Hide")
        else:
            self.password_entry.config(show="*")
            self.toggle_button.config(text="Show")

    def login(self):
        email = self.email_entry.get().strip()
        password = self.password_entry.get()

        if not email:
            messagebox.showwarning(
                "Missing Information",
                "Please enter your email or phone number.",
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

        # Demo login: checks that both fields are filled.
        # This does not authenticate against a real account.
        if messagebox.askyesno(
            "Demo Login",
            "Continue to the CICO dashboard?",
            parent=self.root
        ):
            self.root.unbind("<Return>")

            if self.on_success:
                self.on_success(email)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("CICO E-Wallet - Login")
    root.geometry("1100x700")
    root.minsize(850, 600)

    LoginPage(root)
    root.mainloop()
