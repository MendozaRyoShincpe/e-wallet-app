
import tkinter as tk
from tkinter import messagebox


class Dashboard:
    def __init__(self, root, username="User", on_logout=None):
        self.root = root
        self.username = username
        self.on_logout = on_logout

        # CICO colors
        self.purple = "#7040E8"
        self.purple_hover = "#5930C7"
        self.background = "#F8F7FF"
        self.dark = "#171A35"
        self.gray = "#777C91"
        self.border = "#E2E0ED"
        self.white = "#FFFFFF"
        self.light_purple = "#EEE8FF"

        # Sample wallet balance for UI demonstration
        self.balance = 5000.00

        self.frame = tk.Frame(self.root, bg=self.background)
        self.frame.pack(fill="both", expand=True)

        self.show_dashboard()

    def clear_content(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def create_button(
        self, parent, text, command,
        bg=None, fg=None, font_size=10
    ):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg or self.purple,
            fg=fg or self.white,
            activebackground=self.purple_hover,
            activeforeground=self.white,
            font=("Arial", font_size, "bold"),
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=16,
            pady=11
        )
        return button

    def create_header(self, title, subtitle):
        header = tk.Frame(self.frame, bg=self.white)
        header.pack(fill="x")

        title_area = tk.Frame(header, bg=self.white)
        title_area.pack(side="left", padx=30, pady=20)

        tk.Label(
            title_area,
            text="CICO",
            font=("Arial", 23, "bold"),
            bg=self.white,
            fg=self.purple
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text=title,
            font=("Arial", 16, "bold"),
            bg=self.white,
            fg=self.dark
        ).pack(anchor="w", pady=(7, 0))

        tk.Label(
            title_area,
            text=subtitle,
            font=("Arial", 10),
            bg=self.white,
            fg=self.gray
        ).pack(anchor="w", pady=(3, 0))

        self.create_button(
            header,
            "Log Out",
            self.logout,
            bg=self.white,
            fg=self.purple
        ).pack(side="right", padx=25, pady=25)

        tk.Frame(
            self.frame,
            bg=self.border,
            height=1
        ).pack(fill="x")

    def show_dashboard(self):
        self.clear_content()
        self.root.title("CICO E-Wallet - Dashboard")

        self.create_header(
            "Main Menu Dashboard",
            f"Welcome, {self.username}! What would you like to do today?"
        )

        # Scrollable main content
        canvas = tk.Canvas(
            self.frame,
            bg=self.background,
            highlightthickness=0
        )
        scrollbar = tk.Scrollbar(
            self.frame,
            orient="vertical",
            command=canvas.yview
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        content = tk.Frame(canvas, bg=self.background)
        window_id = canvas.create_window(
            (0, 0),
            window=content,
            anchor="nw"
        )

        content.bind(
            "<Configure>",
            lambda event: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )
        canvas.bind(
            "<Configure>",
            lambda event: canvas.itemconfigure(
                window_id, width=event.width
            )
        )

        # Wallet balance card
        balance_card = tk.Frame(
            content,
            bg=self.purple,
            padx=25,
            pady=22
        )
        balance_card.pack(
            fill="x",
            padx=30,
            pady=(25, 30)
        )

        tk.Label(
            balance_card,
            text="AVAILABLE WALLET BALANCE",
            font=("Arial", 10, "bold"),
            bg=self.purple,
            fg="#EAE2FF"
        ).pack(anchor="w")

        tk.Label(
            balance_card,
            text=f"₱{self.balance:,.2f}",
            font=("Arial", 29, "bold"),
            bg=self.purple,
            fg=self.white
        ).pack(anchor="w", pady=(8, 4))

        tk.Label(
            balance_card,
            text="Sample balance for demonstration only",
            font=("Arial", 9),
            bg=self.purple,
            fg="#EAE2FF"
        ).pack(anchor="w")

        # Services heading
        tk.Label(
            content,
            text="Our Services",
            font=("Arial", 19, "bold"),
            bg=self.background,
            fg=self.dark
        ).pack(anchor="w", padx=30)

        tk.Label(
            content,
            text="Select a service to get started.",
            font=("Arial", 10),
            bg=self.background,
            fg=self.gray
        ).pack(anchor="w", padx=30, pady=(5, 15))

        # Four main service cards
        services = [
            (
                "01",
                "Send Money",
                "Transfer money to another CICO user.",
                self.show_send_money
            ),
            (
                "02",
                "Pay Bills",
                "Pay utility bills and other payments.",
                self.show_pay_bills
            ),
            (
                "03",
                "Cash In / Deposit",
                "Add funds to your CICO wallet.",
                self.show_cash_in
            ),
            (
                "04",
                "Cash Out / Withdraw",
                "Withdraw money from your wallet.",
                self.show_cash_out
            ),
        ]

        grid = tk.Frame(content, bg=self.background)
        grid.pack(fill="x", padx=25, pady=(0, 25))

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        for index, service in enumerate(services):
            number, title, description, command = service
            row = index // 2
            column = index % 2

            card = tk.Frame(
                grid,
                bg=self.white,
                highlightbackground=self.border,
                highlightthickness=1,
                padx=20,
                pady=20
            )
            card.grid(
                row=row,
                column=column,
                sticky="nsew",
                padx=6,
                pady=6
            )

            tk.Label(
                card,
                text=number,
                font=("Arial", 11, "bold"),
                bg=self.light_purple,
                fg=self.purple,
                padx=12,
                pady=8
            ).pack(anchor="w")

            tk.Label(
                card,
                text=title,
                font=("Arial", 15, "bold"),
                bg=self.white,
                fg=self.dark,
                wraplength=300,
                justify="left"
            ).pack(anchor="w", pady=(15, 7))

            tk.Label(
                card,
                text=description,
                font=("Arial", 10),
                bg=self.white,
                fg=self.gray,
                wraplength=300,
                justify="left"
            ).pack(anchor="w", pady=(0, 15))

            self.create_button(
                card,
                "Open Service  →",
                command
            ).pack(anchor="w")

        # Bottom information
        tk.Label(
            content,
            text="CICO E-Wallet  |  Your money, made simple.",
            font=("Arial", 9),
            bg=self.background,
            fg=self.gray
        ).pack(pady=(0, 20))

    def show_placeholder(self, title, description):
        self.clear_content()
        self.root.title(f"CICO E-Wallet - {title}")

        self.create_header(
            title,
            "This service is not available yet."
        )

        center = tk.Frame(
            self.frame,
            bg=self.background,
            padx=25,
            pady=30
        )
        center.pack(fill="both", expand=True)

        card = tk.Frame(
            center,
            bg=self.white,
            highlightbackground=self.border,
            highlightthickness=1,
            padx=30,
            pady=35
        )
        card.pack(
            fill="x",
            expand=True,
            padx=10,
            pady=10
        )

        tk.Label(
            card,
            text="CICO",
            font=("Arial", 28, "bold"),
            bg=self.white,
            fg=self.purple
        ).pack(pady=(5, 15))

        tk.Label(
            card,
            text=title,
            font=("Arial", 21, "bold"),
            bg=self.white,
            fg=self.dark,
            wraplength=450
        ).pack(pady=(0, 12))

        tk.Label(
            card,
            text=description,
            font=("Arial", 11),
            bg=self.white,
            fg=self.gray,
            wraplength=450,
            justify="center"
        ).pack(pady=(0, 25))

        tk.Label(
            card,
            text="COMING SOON",
            font=("Arial", 10, "bold"),
            bg=self.light_purple,
            fg=self.purple,
            padx=18,
            pady=10
        ).pack()

        self.create_button(
            card,
            "← Back to Dashboard",
            self.show_dashboard
        ).pack(pady=(25, 5))

    # Step 4: Send Money UI
    def show_send_money(self):
        self.show_placeholder(
            "Send Money",
            "Send money to another CICO user. Recipient details, "
            "transfer amounts, and confirmation will be implemented "
            "in a later step."
        )

    # Step 5: Payment / Pay Bills UI
    def show_pay_bills(self):
        self.show_placeholder(
            "Pay Bills",
            "Choose a biller, enter your account details, and review "
            "your payment. Bill payment functionality will be "
            "implemented in a later step."
        )

    # Step 6A: Cash In / Deposit UI
    def show_cash_in(self):
        self.show_placeholder(
            "Cash In / Deposit",
            "Add money to your CICO wallet using supported funding "
            "methods. Deposit functionality will be implemented "
            "in a later step."
        )

    # Step 6B: Cash Out / Withdraw UI
    def show_cash_out(self):
        self.show_placeholder(
            "Cash Out / Withdraw",
            "Withdraw funds from your CICO wallet using supported "
            "withdrawal methods. Withdrawal functionality will be "
            "implemented in a later step."
        )

    # Step 7: Security Verification placeholder
    def show_security_verification(self):
        self.show_placeholder(
            "Security Verification",
            "Transaction PIN, OTP verification, and other security "
            "checks will be implemented in a later step."
        )

    # Step 8: Transaction Receipt placeholder
    def show_transaction_receipt(self):
        self.show_placeholder(
            "Transaction Receipt",
            "Transaction reference number, amount, date, and "
            "confirmation details will be implemented in a later step."
        )

    def logout(self):
        confirmed = messagebox.askyesno(
            "Log Out",
            "Are you sure you want to log out?",
            parent=self.root
        )

        if confirmed:
            self.frame.destroy()

            if self.on_logout:
                self.on_logout()
