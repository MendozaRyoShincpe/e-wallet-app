import tkinter as tk
from tkinter import messagebox
from decimal import Decimal, InvalidOperation
from datetime import datetime

from receipt import TransactionHistory
from wallet import wallet
import session
from ui.sendmoney import SendMoney
from ui.bill_payments import BillPayments
from ui.CashIn import CashIn
from ui.CashOut import CashOut
from ui.theme import (
    PURPLE, DARK_PURPLE, LIGHT_PURPLE, WHITE, BLACK, BG, GRAY, BORDER,
    GREEN, RED, LIGHT_GREEN, LIGHT_RED, apply_icon, load_logo
)


class Dashboard:
    def __init__(self, root, username="User", on_logout=None):
        self.root = root
        self.on_logout = on_logout

        # Greet the logged-in user by name instead of the typed email/phone
        user = session.get_user()
        self.username = user["account_name"] if user else username

        self.logo_image = None
        self.active_service = None
        self.history_window = None

        self.root.configure(bg=BG)
        self.root.title("CICO E-Wallet - Dashboard")
        self.root.geometry("1100x700")
        self.root.minsize(850, 600)
        apply_icon(self.root)

        self.build_ui()

    # ---------- Main UI ----------
    def build_ui(self):
        self.create_header()
        self.create_main_content()
        self.refresh_dashboard()

    # ---------- Header ----------
    def create_header(self):
        header = tk.Frame(self.root, bg=PURPLE, padx=25, pady=15)
        header.pack(fill="x")

        brand = tk.Frame(header, bg=PURPLE)
        brand.pack(side="left", anchor="w")

        self.logo_image = load_logo(42)
        if self.logo_image is not None:
            tk.Label(
                brand, image=self.logo_image, bg=PURPLE, bd=0
            ).pack(side="left", padx=(0, 9))

        tk.Label(
            brand, text="CICO", font=("Arial", 22, "bold"),
            bg=PURPLE, fg=WHITE
        ).pack(side="left")

        right = tk.Frame(header, bg=PURPLE)
        right.pack(side="right", anchor="e")

        tk.Label(
            right, text=f"Welcome, {self.username}!",
            font=("Arial", 10), bg=PURPLE, fg=WHITE
        ).pack(side="left", padx=(0, 15))

        tk.Button(
            right, text="Receipts", command=self.show_receipt_history,
            font=("Arial", 9, "bold"), bg=PURPLE, fg=WHITE,
            activebackground=DARK_PURPLE, activeforeground=WHITE,
            relief="solid", bd=1, cursor="hand2", padx=14, pady=6
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            right, text="Logout", command=self.logout,
            font=("Arial", 9, "bold"), bg=WHITE, fg=PURPLE,
            activebackground=LIGHT_PURPLE, activeforeground=DARK_PURPLE,
            relief="flat", cursor="hand2", padx=14, pady=7
        ).pack(side="left")

    # ---------- Dashboard Content ----------
    def create_main_content(self):
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(outer, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(
            outer, orient="vertical", command=self.canvas.yview
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.content = tk.Frame(self.canvas, bg=BG, padx=30, pady=25)
        self.content_window = self.canvas.create_window(
            (0, 0), window=self.content, anchor="nw"
        )

        self.content.bind("<Configure>", self.update_scroll_region)
        self.canvas.bind("<Configure>", self.resize_content)

        # Mouse wheel scrolling (Windows/macOS use <MouseWheel>, Linux uses
        # buttons 4 and 5). The bindings are removed when the dashboard closes.
        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.root.bind_all(sequence, self.on_mousewheel)
        self.canvas.bind("<Destroy>", self.remove_wheel_bindings, add="+")

        # Page title
        tk.Label(
            self.content, text="Main Menu Dashboard",
            font=("Arial", 22, "bold"), bg=BG, fg=BLACK
        ).pack(anchor="w")

        tk.Label(
            self.content, text="Manage your money with CICO E-Wallet.",
            font=("Arial", 10), bg=BG, fg=GRAY
        ).pack(anchor="w", pady=(5, 20))

        self.create_balance_card()
        self.create_services_section()
        self.create_recent_transactions()

        tk.Label(
            self.content, text="CICO E-Wallet | Demo Application",
            font=("Arial", 8), bg=BG, fg=GRAY
        ).pack(pady=(22, 5))

    def update_scroll_region(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def resize_content(self, event):
        self.canvas.itemconfigure(self.content_window, width=event.width)

    def on_mousewheel(self, event):
        widget = event.widget

        try:
            # Only scroll when the pointer is over the dashboard itself,
            # not over a service, receipt or history window.
            if not isinstance(widget, tk.Misc):
                return
            if widget.winfo_toplevel() is not self.root:
                return

            if event.num == 4:
                step = -1
            elif event.num == 5:
                step = 1
            else:
                step = -1 if event.delta > 0 else 1

            self.canvas.yview_scroll(step, "units")
        except (tk.TclError, AttributeError):
            pass

    def remove_wheel_bindings(self, event=None):
        if event is not None and event.widget is not self.canvas:
            return

        for sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            try:
                self.root.unbind_all(sequence)
            except tk.TclError:
                pass

    # ---------- Balance Card ----------
    def create_balance_card(self):
        card = tk.Frame(self.content, bg=PURPLE, padx=25, pady=22)
        card.pack(fill="x", pady=(0, 25))

        tk.Label(
            card, text="YOUR AVAILABLE BALANCE",
            font=("Arial", 10, "bold"), bg=PURPLE, fg=WHITE
        ).pack(anchor="w")

        self.balance_label = tk.Label(
            card, text="₱0.00", font=("Arial", 30, "bold"),
            bg=PURPLE, fg=WHITE
        )
        self.balance_label.pack(anchor="w", pady=(8, 5))

        # Other users need this ID to send money to you
        tk.Label(
            card, text=f"Wallet ID: {wallet.account_number or '—'}",
            font=("Arial", 9), bg=PURPLE, fg="#EEE8FF"
        ).pack(anchor="w")

    def refresh_balance(self):
        try:
            self.balance_label.config(text=f"₱{wallet.get_balance():,.2f}")
        except (tk.TclError, AttributeError):
            pass

    # ---------- Services Section ----------
    def create_services_section(self):
        tk.Label(
            self.content, text="Our Services",
            font=("Arial", 17, "bold"), bg=BG, fg=BLACK
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            self.content, text="Choose a service to continue.",
            font=("Arial", 10), bg=BG, fg=GRAY
        ).pack(anchor="w", pady=(0, 15))

        services = tk.Frame(self.content, bg=BG)
        services.pack(fill="x")

        services.grid_columnconfigure(0, weight=1, uniform="service")
        services.grid_columnconfigure(1, weight=1, uniform="service")

        self.create_service_card(
            services, 0, 0, "↗", "Send Money",
            "Transfer funds to another wallet.", self.show_send_money
        )
        self.create_service_card(
            services, 0, 1, "₱", "Pay Bills",
            "Pay electricity, water, internet, and more.",
            self.show_pay_bills
        )
        self.create_service_card(
            services, 1, 0, "+", "Cash In / Deposit",
            "Add funds to your CICO wallet.", self.show_cash_in
        )
        self.create_service_card(
            services, 1, 1, "−", "Cash Out / Withdraw",
            "Withdraw funds from your wallet.", self.show_cash_out
        )

    def create_service_card(
        self, parent, row, column, symbol, title, description, command
    ):
        card = tk.Frame(
            parent, bg=WHITE, highlightbackground=BORDER,
            highlightthickness=1, padx=20, pady=20
        )
        card.grid(row=row, column=column, sticky="nsew", padx=7, pady=7)

        tk.Label(
            card, text=symbol, font=("Arial", 23, "bold"),
            bg=LIGHT_PURPLE, fg=PURPLE, width=3, height=1
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            card, text=title, font=("Arial", 13, "bold"),
            bg=WHITE, fg=BLACK
        ).pack(anchor="w")

        tk.Label(
            card, text=description, font=("Arial", 9), bg=WHITE, fg=GRAY,
            wraplength=300, justify="left"
        ).pack(anchor="w", pady=(6, 14))

        tk.Button(
            card, text="Open Service", command=command,
            font=("Arial", 9, "bold"), bg=PURPLE, fg=WHITE,
            activebackground=DARK_PURPLE, activeforeground=WHITE,
            relief="flat", cursor="hand2", padx=14, pady=8
        ).pack(anchor="w")

    # ---------- Recent Transactions ----------
    def create_recent_transactions(self):
        section = tk.Frame(self.content, bg=BG)
        section.pack(fill="x", pady=(25, 0))

        heading = tk.Frame(section, bg=BG)
        heading.pack(fill="x", pady=(0, 5))

        tk.Label(
            heading, text="Recent Transactions",
            font=("Arial", 17, "bold"), bg=BG, fg=BLACK
        ).pack(side="left")

        tk.Label(
            heading, text="Latest wallet activity",
            font=("Arial", 9), bg=BG, fg=GRAY
        ).pack(side="right", padx=(5, 0))

        # White container for the transaction list
        container = tk.Frame(
            section, bg=WHITE, highlightbackground=BORDER,
            highlightthickness=1
        )
        container.pack(fill="x", pady=(10, 0))

        # This area is rebuilt whenever the wallet changes.
        self.transaction_list = tk.Frame(container, bg=WHITE)
        self.transaction_list.pack(fill="x", padx=15, pady=5)

    @staticmethod
    def is_money_received(transaction):
        """Cash In and Money Received add money; everything else deducts it."""
        transaction_type = str(transaction.get("type", "")).strip().lower()

        return transaction_type in {
            "cash in", "deposit", "cash-in", "cashin",
            "received", "money received"
        }

    @staticmethod
    def format_transaction_date(date_string):
        try:
            date_value = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
            return date_value.strftime("%b %d, %Y · %I:%M %p")
        except (ValueError, TypeError):
            return str(date_string or "Date unavailable")

    def refresh_transactions(self):
        # Remove the old transaction rows.
        for widget in self.transaction_list.winfo_children():
            widget.destroy()

        # Most recent transactions first; show up to five.
        recent = list(reversed(wallet.get_transactions()[-5:]))

        if not recent:
            empty = tk.Frame(self.transaction_list, bg=WHITE, pady=25)
            empty.pack(fill="x")

            tk.Label(
                empty, text="No transactions yet",
                font=("Arial", 13, "bold"), bg=WHITE, fg=BLACK
            ).pack()

            tk.Label(
                empty,
                text="Your Cash In, Cash Out, Send Money, "
                     "and bill payments will appear here.",
                font=("Arial", 9), bg=WHITE, fg=GRAY,
                wraplength=500, justify="center"
            ).pack(pady=(6, 0))
            return

        for index, transaction in enumerate(recent):
            self.create_transaction_row(
                transaction, show_divider=index < len(recent) - 1
            )

    def create_transaction_row(self, transaction, show_divider=True):
        received = self.is_money_received(transaction)

        try:
            amount = Decimal(str(transaction.get("amount", 0)))
        except (InvalidOperation, ValueError, TypeError):
            amount = Decimal("0.00")

        amount_color = GREEN if received else RED
        amount_sign = "+" if received else "−"

        transaction_type = str(transaction.get("type", "Transaction"))
        description = str(transaction.get("description", "")).strip()
        display_description = description or transaction_type
        date_text = self.format_transaction_date(transaction.get("date", ""))

        row = tk.Frame(self.transaction_list, bg=WHITE, padx=5, pady=12)
        row.pack(fill="x")

        # Left-side transaction icon
        tk.Label(
            row, text="↓" if received else "↑",
            font=("Arial", 18, "bold"),
            bg=LIGHT_GREEN if received else LIGHT_RED,
            fg=amount_color, width=3, height=1
        ).pack(side="left", padx=(0, 12))

        # Right-side amount (packed before the text so it is never pushed out)
        tk.Label(
            row, text=f"{amount_sign}₱{amount:,.2f}",
            font=("Arial", 11, "bold"), bg=WHITE, fg=amount_color
        ).pack(side="right", padx=(8, 0))

        # Transaction name, type and date
        details = tk.Frame(row, bg=WHITE)
        details.pack(side="left", fill="x", expand=True)

        tk.Label(
            details, text=display_description, font=("Arial", 10, "bold"),
            bg=WHITE, fg=BLACK, anchor="w", wraplength=350, justify="left"
        ).pack(anchor="w")

        tk.Label(
            details, text=f"{transaction_type}  •  {date_text}",
            font=("Arial", 8), bg=WHITE, fg=GRAY, anchor="w",
            wraplength=400, justify="left"
        ).pack(anchor="w", pady=(4, 0))

        # Divider between rows
        if show_divider:
            tk.Frame(self.transaction_list, bg=BORDER, height=1).pack(fill="x")

    # ---------- Refresh Dashboard ----------
    def refresh_dashboard(self):
        """Refresh the balance and transaction list together.

        Passed to every service window as its balance-changed callback.
        """
        try:
            if not self.canvas.winfo_exists():
                return
            self.refresh_balance()
            self.refresh_transactions()
        except (tk.TclError, AttributeError):
            pass  # the dashboard is being closed

    # ---------- Open Services ----------
    def open_service(self, service_class):
        # Only one service window at a time: bring the open one forward
        if self.active_service is not None:
            try:
                window = self.active_service.root

                if window.winfo_exists():
                    window.lift()
                    window.focus_force()
                    return
            except (tk.TclError, AttributeError):
                pass

            self.active_service = None

        try:
            service = service_class(
                self.root, on_balance_change=self.refresh_dashboard
            )
            self.active_service = service

            service.root.bind(
                "<Destroy>",
                lambda event, window=service.root:
                    self.on_service_destroy(event, window),
                add="+"
            )

        except Exception as error:
            import traceback
            traceback.print_exc()

            self.active_service = None

            messagebox.showerror(
                "Could Not Open Service",
                f"Service: {service_class.__name__}\n\n"
                f"Error: {error}\n\n"
                "Check the terminal for the full traceback.",
                parent=self.root
            )

    def on_service_destroy(self, event, service_root):
        # <Destroy> also fires for every child widget, so check the window
        if event.widget == service_root:
            self.active_service = None
            self.refresh_dashboard()

    def show_send_money(self):
        self.open_service(SendMoney)

    def show_pay_bills(self):
        self.open_service(BillPayments)

    def show_cash_in(self):
        self.open_service(CashIn)

    def show_cash_out(self):
        self.open_service(CashOut)

    # ---------- Receipt History ----------
    def show_receipt_history(self):
        # Reuse the window if it is already open
        try:
            if self.history_window is not None and \
                    self.history_window.winfo_exists():
                self.history_window.lift()
                self.history_window.focus_force()
                return
        except tk.TclError:
            pass

        try:
            self.history_window = TransactionHistory(self.root, wallet)
        except Exception as error:
            self.history_window = None
            messagebox.showerror(
                "Receipt History",
                f"Could not open your receipt history:\n{error}",
                parent=self.root
            )

    # ---------- Logout ----------
    def logout(self):
        if not messagebox.askyesno(
            "Logout", "Are you sure you want to log out?",
            parent=self.root
        ):
            return

        if self.history_window is not None:
            try:
                self.history_window.destroy()
            except tk.TclError:
                pass
            self.history_window = None

        service = self.active_service
        self.active_service = None

        if service is not None:
            try:
                if service.root.winfo_exists():
                    service.root.grab_release()
                    service.root.destroy()
            except (tk.TclError, AttributeError):
                pass

        if self.on_logout:
            self.on_logout()
