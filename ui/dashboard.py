import tkinter as tk
from tkinter import messagebox
from decimal import Decimal

from wallet import wallet
from receipt import TransactionHistory

from ui.theme import (
    PURPLE,
    DARK_PURPLE,
    LIGHT_PURPLE,
    WHITE,
    BLACK,
    BG,
    GRAY,
    BORDER,
    GREEN,
    RED
)

from ui.sendmoney import SendMoney
from ui.billpayments import BillPayments
from ui.cashin import CashIn
from ui.cashout import CashOut


# Manages the main dashboard and connects all wallet services
class Dashboard:
    def __init__(
        self,
        root,
        username="User",
        on_logout=None,
        user=None
    ):
        self.root = root
        self.user = user or {}
        self.on_logout = on_logout

        self.username = self.user.get(
            "name",
            self.user.get("account_name", username)
        )

        self.service_window = None
        self.receipt_window = None

        # Load the logged-in user's wallet and account number
        try:
            wallet.set_user(self.user)

            # The CICO Account Number is the registered phone number
            self.account_number = str(wallet.account_number)

        except (ValueError, OSError, KeyError, TypeError) as error:
            messagebox.showerror(
                "Dashboard Error",
                str(error),
                parent=self.root
            )
            raise

        self.root.configure(bg=BG)

        self.build_dashboard()
        self.refresh_dashboard()

    # Builds the main dashboard layout
    def build_dashboard(self):
        self.main_container = tk.Frame(
            self.root,
            bg=BG
        )
        self.main_container.pack(
            fill="both",
            expand=True
        )

        # Header
        self.header = tk.Frame(
            self.main_container,
            bg=WHITE,
            height=75
        )
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        header_left = tk.Frame(
            self.header,
            bg=WHITE
        )
        header_left.pack(
            side="left",
            padx=30,
            pady=15
        )

        tk.Label(
            header_left,
            text="CICO",
            font=("Arial", 23, "bold"),
            fg=PURPLE,
            bg=WHITE
        ).pack(side="left")

        tk.Label(
            header_left,
            text=" E-WALLET",
            font=("Arial", 12, "bold"),
            fg=BLACK,
            bg=WHITE
        ).pack(side="left", pady=(6, 0))

        header_right = tk.Frame(
            self.header,
            bg=WHITE
        )
        header_right.pack(
            side="right",
            padx=25,
            pady=17
        )

        self.make_button(
            header_right,
            "Receipts",
            self.show_receipt_history,
            bg=LIGHT_PURPLE,
            fg=PURPLE
        ).pack(side="left", padx=5)

        self.make_button(
            header_right,
            "Logout",
            self.logout,
            bg=PURPLE,
            fg=WHITE
        ).pack(side="left", padx=5)

        # Creates a scrollable area for dashboard content
        self.canvas = tk.Canvas(
            self.main_container,
            bg=BG,
            highlightthickness=0
        )

        self.scrollbar = tk.Scrollbar(
            self.main_container,
            orient="vertical",
            command=self.canvas.yview
        )

        self.scrollable_frame = tk.Frame(
            self.canvas,
            bg=BG
        )

        self.scrollable_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw"
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar.set
        )

        self.canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        self.scrollbar.pack(
            side="right",
            fill="y"
        )

        self.canvas.bind(
            "<Configure>",
            self.resize_scrollable_frame
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            self.on_mousewheel
        )

        self.build_content()

    # Organizes the main sections of the dashboard
    def build_content(self):
        content = self.scrollable_frame

        welcome_frame = tk.Frame(
            content,
            bg=BG
        )
        welcome_frame.pack(
            fill="x",
            padx=35,
            pady=(30, 15)
        )

        tk.Label(
            welcome_frame,
            text=f"Welcome back, {self.username}!",
            font=("Arial", 23, "bold"),
            fg=BLACK,
            bg=BG
        ).pack(anchor="w")

        tk.Label(
            welcome_frame,
            text="Manage your money with CICO.",
            font=("Arial", 11),
            fg=GRAY,
            bg=BG
        ).pack(anchor="w", pady=(5, 0))

        self.build_balance_card(content)
        self.build_account_card(content)
        self.build_services(content)
        self.build_transactions(content)

    # Displays the user's current wallet balance
    def build_balance_card(self, parent):
        card = tk.Frame(
            parent,
            bg=PURPLE,
            padx=30,
            pady=25
        )
        card.pack(
            fill="x",
            padx=35,
            pady=12
        )

        tk.Label(
            card,
            text="TOTAL WALLET BALANCE",
            font=("Arial", 11, "bold"),
            fg=WHITE,
            bg=PURPLE
        ).pack(anchor="w")

        self.balance_label = tk.Label(
            card,
            text="₱0.00",
            font=("Arial", 30, "bold"),
            fg=WHITE,
            bg=PURPLE
        )
        self.balance_label.pack(
            anchor="w",
            pady=(10, 5)
        )

        tk.Label(
            card,
            text="Your available CICO balance",
            font=("Arial", 10),
            fg="#E8DEFF",
            bg=PURPLE
        ).pack(anchor="w")

    # Displays the registered account number and user information
    def build_account_card(self, parent):
        card = tk.Frame(
            parent,
            bg=WHITE,
            padx=25,
            pady=22,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        card.pack(
            fill="x",
            padx=35,
            pady=12
        )

        tk.Label(
            card,
            text="MY ACCOUNT INFORMATION",
            font=("Arial", 13, "bold"),
            fg=BLACK,
            bg=WHITE
        ).pack(anchor="w", pady=(0, 18))

        tk.Label(
            card,
            text="CICO ACCOUNT NUMBER",
            font=("Arial", 9, "bold"),
            fg=GRAY,
            bg=WHITE
        ).pack(anchor="w")

        account_row = tk.Frame(
            card,
            bg=WHITE
        )
        account_row.pack(
            fill="x",
            pady=(5, 10)
        )

        tk.Label(
            account_row,
            text=self.account_number,
            font=("Arial", 16, "bold"),
            fg=PURPLE,
            bg=WHITE
        ).pack(side="left")

        self.make_button(
            account_row,
            "Copy",
            self.copy_account_number,
            bg=LIGHT_PURPLE,
            fg=PURPLE
        ).pack(side="right")

        tk.Label(
            card,
            text="This is your registered phone number. Share it with others to receive money.",
            font=("Arial", 9),
            fg=GRAY,
            bg=WHITE,
            wraplength=350,
            justify="left"
        ).pack(anchor="w", pady=(5, 0))

    # Creates buttons for the available wallet services
    def build_services(self, parent):
        section = tk.Frame(
            parent,
            bg=BG
        )
        section.pack(
            fill="x",
            padx=35,
            pady=15
        )

        tk.Label(
            section,
            text="CICO SERVICES",
            font=("Arial", 15, "bold"),
            fg=BLACK,
            bg=BG
        ).pack(anchor="w", pady=(0, 15))

        services_frame = tk.Frame(
            section,
            bg=BG
        )
        services_frame.pack(fill="x")

        services = [
            ("Send Money", self.open_send_money, PURPLE),
            ("Cash In", self.open_cash_in, GREEN),
            ("Cash Out", self.open_cash_out, RED),
            ("Bill Payments", self.open_bill_payments, DARK_PURPLE)
        ]

        for index, (name, command, color) in enumerate(services):
            card = tk.Frame(
                services_frame,
                bg=WHITE,
                padx=15,
                pady=20,
                highlightbackground=BORDER,
                highlightthickness=1
            )

            card.grid(
                row=0,
                column=index,
                padx=6,
                sticky="nsew"
            )

            services_frame.grid_columnconfigure(
                index,
                weight=1
            )

            tk.Label(
                card,
                text=name,
                font=("Arial", 11, "bold"),
                fg=color,
                bg=WHITE
            ).pack(pady=(0, 12))

            self.make_button(
                card,
                "Open",
                command,
                bg=color,
                fg=WHITE
            ).pack(fill="x")

    # Creates the section for displaying recent transactions
    def build_transactions(self, parent):
        section = tk.Frame(
            parent,
            bg=WHITE,
            padx=25,
            pady=20,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        section.pack(
            fill="x",
            padx=35,
            pady=(15, 30)
        )

        heading = tk.Frame(
            section,
            bg=WHITE
        )
        heading.pack(fill="x")

        tk.Label(
            heading,
            text="RECENT TRANSACTIONS",
            font=("Arial", 14, "bold"),
            fg=BLACK,
            bg=WHITE
        ).pack(side="left")

        self.make_button(
            heading,
            "Refresh",
            self.refresh_transactions,
            bg=LIGHT_PURPLE,
            fg=PURPLE
        ).pack(side="right")

        self.transactions_frame = tk.Frame(
            section,
            bg=WHITE
        )
        self.transactions_frame.pack(
            fill="x",
            pady=(15, 0)
        )

    # Updates the balance and transaction history
    def refresh_dashboard(self):
        self.refresh_balance()
        self.refresh_transactions()

    def refresh_balance(self):
        balance = wallet.get_balance()

        self.balance_label.config(
            text=f"₱{balance:,.2f}"
        )

    # Displays the five most recent wallet transactions
    def refresh_transactions(self):
        for widget in self.transactions_frame.winfo_children():
            widget.destroy()

        transactions = wallet.get_transactions()

        if not transactions:
            tk.Label(
                self.transactions_frame,
                text="No transactions yet.",
                font=("Arial", 10),
                fg=GRAY,
                bg=WHITE
            ).pack(anchor="w", pady=10)
            return

        for transaction in reversed(transactions[-5:]):
            row = tk.Frame(
                self.transactions_frame,
                bg=WHITE,
                pady=10
            )
            row.pack(fill="x")

            left = tk.Frame(
                row,
                bg=WHITE
            )
            left.pack(side="left", fill="x", expand=True)

            transaction_type = transaction.get(
                "type",
                "Transaction"
            )

            description = transaction.get(
                "description",
                ""
            )

            date = transaction.get(
                "date",
                ""
            )

            tk.Label(
                left,
                text=transaction_type,
                font=("Arial", 10, "bold"),
                fg=BLACK,
                bg=WHITE
            ).pack(anchor="w")

            tk.Label(
                left,
                text=description or date,
                font=("Arial", 9),
                fg=GRAY,
                bg=WHITE
            ).pack(anchor="w", pady=(3, 0))

            amount = Decimal(
                str(transaction.get("amount", "0.00"))
            )

            transaction_color = (
                GREEN
                if transaction_type.lower() in (
                    "cash in",
                    "received money",
                    "deposit"
                )
                else RED
            )

            tk.Label(
                row,
                text=f"₱{amount:,.2f}",
                font=("Arial", 11, "bold"),
                fg=transaction_color,
                bg=WHITE
            ).pack(side="right")

            tk.Frame(
                self.transactions_frame,
                bg=BORDER,
                height=1
            ).pack(fill="x")

    # Copies the registered account number to the clipboard
    def copy_account_number(self):
        self.copy_to_clipboard(
            self.account_number,
            "CICO Account Number copied!"
        )

    def copy_to_clipboard(self, value, message):
        if not value or value == "N/A":
            messagebox.showwarning(
                "Copy",
                "Account number is not available.",
                parent=self.root
            )
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(value)
        self.root.update()

        messagebox.showinfo(
            "Copied",
            message,
            parent=self.root
        )

    # Opens a service window and prevents duplicate windows
    def open_service(self, service_class):
        if self.service_window is not None:
            try:
                if self.service_window.root.winfo_exists():
                    self.service_window.root.lift()
                    return
            except (tk.TclError, AttributeError):
                self.service_window = None

        try:
            self.service_window = service_class(
                self.root,
                on_balance_change=self.refresh_dashboard
            )

            self.service_window.root.protocol(
                "WM_DELETE_WINDOW",
                self.close_service_window
            )

        except Exception as error:
            self.service_window = None

            messagebox.showerror(
                "Service Error",
                str(error),
                parent=self.root
            )

    # Opens each wallet service using the shared window handler
    def open_send_money(self):
        self.open_service(SendMoney)

    def open_cash_in(self):
        self.open_service(CashIn)

    def open_cash_out(self):
        self.open_service(CashOut)

    def open_bill_payments(self):
        self.open_service(BillPayments)

    # Closes the active service window and refreshes the dashboard
    def close_service_window(self):
        if self.service_window is not None:
            try:
                self.service_window.close()
            except (tk.TclError, AttributeError):
                pass

            self.service_window = None

        self.refresh_dashboard()

    # Opens the user's complete receipt and transaction history
    def show_receipt_history(self):
        try:
            if (
                self.receipt_window is not None
                and self.receipt_window.winfo_exists()
            ):
                self.receipt_window.lift()
                return

        except tk.TclError:
            self.receipt_window = None

        try:
            self.receipt_window = TransactionHistory(
                self.root,
                wallet
            )

            self.receipt_window.protocol(
                "WM_DELETE_WINDOW",
                self.close_receipt_history
            )

        except Exception as error:
            self.receipt_window = None

            messagebox.showerror(
                "Receipt History Error",
                str(error),
                parent=self.root
            )

    def close_receipt_history(self):
        if self.receipt_window is not None:
            try:
                self.receipt_window.destroy()
            except tk.TclError:
                pass

            self.receipt_window = None

    # Reusable static method for creating styled buttons
    @staticmethod
    def make_button(
        parent,
        text,
        command,
        bg=PURPLE,
        fg=WHITE
    ):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            activebackground=DARK_PURPLE,
            activeforeground=WHITE,
            font=("Arial", 9, "bold"),
            relief="flat",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2"
        )

    # Adjusts the scrollable content to match the canvas width
    def resize_scrollable_frame(self, event):
        self.canvas.itemconfig(
            self.canvas_window,
            width=event.width
        )

    # Handles mouse wheel scrolling
    def on_mousewheel(self, event):
        try:
            if self.canvas.winfo_exists():
                self.canvas.yview_scroll(
                    int(-1 * (event.delta / 120)),
                    "units"
                )
        except tk.TclError:
            pass

    # Logs out the user and closes active windows
    def logout(self):
        confirm = messagebox.askyesno(
            "Logout",
            "Are you sure you want to log out?",
            parent=self.root
        )

        if not confirm:
            return

        self.close_receipt_history()

        if self.service_window is not None:
            try:
                self.service_window.close()
            except (tk.TclError, AttributeError):
                pass

            self.service_window = None

        wallet.clear_user()

        try:
            self.canvas.unbind_all("<MouseWheel>")
        except tk.TclError:
            pass

        if self.on_logout:
            self.on_logout()