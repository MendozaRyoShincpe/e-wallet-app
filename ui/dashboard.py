import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from decimal import Decimal, InvalidOperation
from datetime import datetime

from wallet import wallet
from ui.sendmoney import SendMoney
from ui.billpayments import BillPayments
from ui.cashin import CashIn
from ui.cashout import CashOut


# ---------- File Paths ----------
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_FILE = os.path.join(BASE, "CICO.png")
ICON_FILE = os.path.join(BASE, "CICO.ico")


# ---------- CICO Theme ----------
PURPLE = "#7040E8"
DARK_PURPLE = "#5930C7"
WHITE = "#FFFFFF"
BLACK = "#171A35"
BG = "#F8F7FF"
GRAY = "#777C91"
BORDER = "#E2E0ED"
GREEN = "#16805D"
RED = "#D93650"
LIGHT_GREEN = "#E8F7EF"
LIGHT_RED = "#FDECEF"


class Dashboard:
    def __init__(self, root, username="User", on_logout=None):
        self.root = root
        self.username = username
        self.on_logout = on_logout

        self.logo_image = None
        self.active_service = None

        self.root.configure(bg=BG)
        self.root.title("CICO E-Wallet - Dashboard")
        self.root.geometry("1100x700")
        self.root.minsize(850, 600)

        try:
            if os.path.exists(ICON_FILE):
                self.root.iconbitmap(ICON_FILE)
        except tk.TclError:
            pass

        self.build_ui()

    # ---------- Main UI ----------
    def build_ui(self):
        self.create_header()
        self.create_main_content()
        self.refresh_dashboard()

    # ---------- Header ----------
    def create_header(self):
        header = tk.Frame(
            self.root,
            bg=PURPLE,
            padx=25,
            pady=15
        )
        header.pack(fill="x")

        brand = tk.Frame(header, bg=PURPLE)
        brand.pack(side="left", anchor="w")

        if os.path.exists(LOGO_FILE):
            try:
                image = Image.open(LOGO_FILE).convert("RGBA")
                image.thumbnail((42, 42), Image.Resampling.LANCZOS)
                self.logo_image = ImageTk.PhotoImage(image)

                tk.Label(
                    brand,
                    image=self.logo_image,
                    bg=PURPLE,
                    bd=0
                ).pack(side="left", padx=(0, 9))

            except Exception as error:
                print(f"Could not load CICO logo: {error}")

        tk.Label(
            brand,
            text="CICO",
            font=("Arial", 22, "bold"),
            bg=PURPLE,
            fg=WHITE
        ).pack(side="left")

        right = tk.Frame(header, bg=PURPLE)
        right.pack(side="right", anchor="e")

        tk.Label(
            right,
            text=f"Welcome, {self.username}!",
            font=("Arial", 10),
            bg=PURPLE,
            fg=WHITE
        ).pack(side="left", padx=(0, 15))

        tk.Button(
            right,
            text="Logout",
            command=self.logout,
            font=("Arial", 9, "bold"),
            bg=WHITE,
            fg=PURPLE,
            activebackground="#F0EBFF",
            activeforeground=DARK_PURPLE,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=7
        ).pack(side="left")

    # ---------- Dashboard Content ----------
    def create_main_content(self):
        outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            outer,
            bg=BG,
            highlightthickness=0
        )

        scrollbar = tk.Scrollbar(
            outer,
            orient="vertical",
            command=self.canvas.yview
        )

        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.content = tk.Frame(
            self.canvas,
            bg=BG,
            padx=30,
            pady=25
        )

        self.content_window = self.canvas.create_window(
            (0, 0),
            window=self.content,
            anchor="nw"
        )

        self.content.bind(
            "<Configure>",
            self.update_scroll_region
        )

        self.canvas.bind(
            "<Configure>",
            self.resize_content
        )

        self.canvas.bind_all(
            "<MouseWheel>",
            self.on_mousewheel
        )

        # Page title
        tk.Label(
            self.content,
            text="Main Menu Dashboard",
            font=("Arial", 22, "bold"),
            bg=BG,
            fg=BLACK
        ).pack(anchor="w")

        tk.Label(
            self.content,
            text="Manage your money with CICO E-Wallet.",
            font=("Arial", 10),
            bg=BG,
            fg=GRAY
        ).pack(anchor="w", pady=(5, 20))

        self.create_balance_card()
        self.create_services_section()
        self.create_recent_transactions()

        tk.Label(
            self.content,
            text="CICO E-Wallet | Demo Application",
            font=("Arial", 8),
            bg=BG,
            fg=GRAY
        ).pack(pady=(22, 5))

    def update_scroll_region(self, event=None):
        self.canvas.configure(
            scrollregion=self.canvas.bbox("all")
        )

    def resize_content(self, event):
        self.canvas.itemconfigure(
            self.content_window,
            width=event.width
        )

    def on_mousewheel(self, event):
        try:
            if self.canvas.winfo_exists():
                self.canvas.yview_scroll(
                    int(-1 * (event.delta / 120)),
                    "units"
                )
        except (tk.TclError, AttributeError):
            pass

    # ---------- Balance Card ----------
    def create_balance_card(self):
        card = tk.Frame(
            self.content,
            bg=PURPLE,
            padx=25,
            pady=22
        )
        card.pack(fill="x", pady=(0, 25))

        tk.Label(
            card,
            text="YOUR AVAILABLE BALANCE",
            font=("Arial", 10, "bold"),
            bg=PURPLE,
            fg=WHITE
        ).pack(anchor="w")

        self.balance_label = tk.Label(
            card,
            text="₱0.00",
            font=("Arial", 30, "bold"),
            bg=PURPLE,
            fg=WHITE
        )
        self.balance_label.pack(anchor="w", pady=(8, 5))

        tk.Label(
            card,
            text="Your CICO wallet balance",
            font=("Arial", 9),
            bg=PURPLE,
            fg="#EEE8FF"
        ).pack(anchor="w")

    def refresh_balance(self):
        try:
            self.balance_label.config(
                text=f"₱{wallet.get_balance():,.2f}"
            )
        except (tk.TclError, AttributeError):
            pass

    # ---------- Services Section ----------
    def create_services_section(self):
        tk.Label(
            self.content,
            text="Our Services",
            font=("Arial", 17, "bold"),
            bg=BG,
            fg=BLACK
        ).pack(anchor="w", pady=(0, 5))

        tk.Label(
            self.content,
            text="Choose a service to continue.",
            font=("Arial", 10),
            bg=BG,
            fg=GRAY
        ).pack(anchor="w", pady=(0, 15))

        services = tk.Frame(self.content, bg=BG)
        services.pack(fill="x")

        services.grid_columnconfigure(
            0, weight=1, uniform="service"
        )
        services.grid_columnconfigure(
            1, weight=1, uniform="service"
        )

        self.create_service_card(
            services, 0, 0,
            "↗", "Send Money",
            "Transfer funds to another wallet.",
            self.show_send_money
        )

        self.create_service_card(
            services, 0, 1,
            "₱", "Pay Bills",
            "Pay electricity, water, internet, and more.",
            self.show_pay_bills
        )

        self.create_service_card(
            services, 1, 0,
            "+", "Cash In / Deposit",
            "Add funds to your CICO wallet.",
            self.show_cash_in
        )

        self.create_service_card(
            services, 1, 1,
            "−", "Cash Out / Withdraw",
            "Withdraw funds from your wallet.",
            self.show_cash_out
        )

    def create_service_card(
        self,
        parent,
        row,
        column,
        symbol,
        title,
        description,
        command
    ):
        card = tk.Frame(
            parent,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1,
            padx=20,
            pady=20
        )

        card.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=7,
            pady=7
        )

        tk.Label(
            card,
            text=symbol,
            font=("Arial", 23, "bold"),
            bg="#F0EBFF",
            fg=PURPLE,
            width=3,
            height=1
        ).pack(anchor="w", pady=(0, 12))

        tk.Label(
            card,
            text=title,
            font=("Arial", 13, "bold"),
            bg=WHITE,
            fg=BLACK
        ).pack(anchor="w")

        tk.Label(
            card,
            text=description,
            font=("Arial", 9),
            bg=WHITE,
            fg=GRAY,
            wraplength=300,
            justify="left"
        ).pack(anchor="w", pady=(6, 14))

        tk.Button(
            card,
            text="Open Service",
            command=command,
            font=("Arial", 9, "bold"),
            bg=PURPLE,
            fg=WHITE,
            activebackground=DARK_PURPLE,
            activeforeground=WHITE,
            relief="flat",
            cursor="hand2",
            padx=14,
            pady=8
        ).pack(anchor="w")

    # ---------- Recent Transactions ----------
    def create_recent_transactions(self):
        section = tk.Frame(self.content, bg=BG)
        section.pack(fill="x", pady=(25, 0))

        # Section heading
        heading = tk.Frame(section, bg=BG)
        heading.pack(fill="x", pady=(0, 5))

        tk.Label(
            heading,
            text="Recent Transactions",
            font=("Arial", 17, "bold"),
            bg=BG,
            fg=BLACK
        ).pack(side="left")

        tk.Label(
            heading,
            text="Latest wallet activity",
            font=("Arial", 9),
            bg=BG,
            fg=GRAY
        ).pack(side="right", padx=(5, 0))

        # White container for the transaction list
        self.transaction_container = tk.Frame(
            section,
            bg=WHITE,
            highlightbackground=BORDER,
            highlightthickness=1
        )
        self.transaction_container.pack(fill="x", pady=(10, 0))

        # This area is rebuilt whenever the wallet changes.
        self.transaction_list = tk.Frame(
            self.transaction_container,
            bg=WHITE
        )
        self.transaction_list.pack(fill="x", padx=15, pady=5)

    def is_money_received(self, transaction):
        """
        Identify incoming transactions using the transaction type.

        Cash In and Deposit are incoming.
        Other transaction types are treated as outgoing.
        """
        transaction_type = str(
            transaction.get("type", "")
        ).strip().lower()

        incoming_types = {
            "cash in",
            "deposit",
            "cash-in",
            "cashin",
            "received",
            "money received"
        }

        return transaction_type in incoming_types

    def format_transaction_date(self, date_string):
        try:
            date_value = datetime.strptime(
                date_string,
                "%Y-%m-%d %H:%M:%S"
            )

            return date_value.strftime("%b %d, %Y · %I:%M %p")

        except (ValueError, TypeError):
            return str(date_string or "Date unavailable")

    def refresh_transactions(self):
        # Remove the old transaction rows.
        for widget in self.transaction_list.winfo_children():
            widget.destroy()

        transactions = wallet.get_transactions()

        # Most recent transactions first; show up to five.
        recent_transactions = list(reversed(transactions[-5:]))

        if not recent_transactions:
            empty_frame = tk.Frame(
                self.transaction_list,
                bg=WHITE,
                pady=25
            )
            empty_frame.pack(fill="x")

            tk.Label(
                empty_frame,
                text="No transactions yet",
                font=("Arial", 13, "bold"),
                bg=WHITE,
                fg=BLACK
            ).pack()

            tk.Label(
                empty_frame,
                text=(
                    "Your Cash In, Cash Out, Send Money, "
                    "and bill payments will appear here."
                ),
                font=("Arial", 9),
                bg=WHITE,
                fg=GRAY,
                wraplength=500,
                justify="center"
            ).pack(pady=(6, 0))

            return

        for index, transaction in enumerate(recent_transactions):
            self.create_transaction_row(
                transaction,
                index
            )

    def create_transaction_row(self, transaction, index):
        received = self.is_money_received(transaction)

        amount = transaction.get("amount", 0)

        try:
            amount = Decimal(str(amount))
        except (InvalidOperation, ValueError, TypeError):
            amount = Decimal("0.00")

        amount_color = GREEN if received else RED
        amount_sign = "+" if received else "−"

        transaction_type = str(
            transaction.get("type", "Transaction")
        )

        description = str(
            transaction.get("description", "")
        ).strip()

        display_description = description or transaction_type

        date_text = self.format_transaction_date(
            transaction.get("date", "")
        )

        row = tk.Frame(
            self.transaction_list,
            bg=WHITE,
            padx=5,
            pady=12
        )
        row.pack(fill="x")

        # Left-side transaction icon.
        icon_bg = LIGHT_GREEN if received else LIGHT_RED
        icon_symbol = "↓" if received else "↑"

        tk.Label(
            row,
            text=icon_symbol,
            font=("Arial", 18, "bold"),
            bg=icon_bg,
            fg=amount_color,
            width=3,
            height=1
        ).pack(side="left", padx=(0, 12))

        # Transaction name and date.
        details = tk.Frame(row, bg=WHITE)
        details.pack(side="left", fill="x", expand=True)

        tk.Label(
            details,
            text=display_description,
            font=("Arial", 10, "bold"),
            bg=WHITE,
            fg=BLACK,
            anchor="w",
            wraplength=350,
            justify="left"
        ).pack(anchor="w")

        tk.Label(
            details,
            text=(
                f"{transaction_type}  •  {date_text}"
            ),
            font=("Arial", 8),
            bg=WHITE,
            fg=GRAY,
            anchor="w",
            wraplength=400,
            justify="left"
        ).pack(anchor="w", pady=(4, 0))

        # Right-side amount.
        tk.Label(
            row,
            text=f"{amount_sign}₱{amount:,.2f}",
            font=("Arial", 11, "bold"),
            bg=WHITE,
            fg=amount_color
        ).pack(side="right", padx=(8, 0))

        # Divider between rows.
        if index < 4:
            tk.Frame(
                self.transaction_list,
                bg=BORDER,
                height=1
            ).pack(fill="x")

    # ---------- Refresh Dashboard ----------
    def refresh_dashboard(self):
        """
        Refresh the balance and transaction history together.
        Pass this method as the callback to wallet services.
        """
        self.refresh_balance()
        self.refresh_transactions()

    # ---------- Open Services ----------
    def open_service(self, service_class):
        if self.active_service is not None:
            try:
                window = self.active_service.root

                if window.winfo_exists():
                    window.lift()
                    window.focus_force()
                    return

            except (tk.TclError, AttributeError):
                self.active_service = None

        try:
            service = service_class(
                self.root,
                on_balance_change=self.refresh_dashboard
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

    # ---------- Logout ----------
    def logout(self):
        if not messagebox.askyesno(
            "Logout",
            "Are you sure you want to log out?",
            parent=self.root
        ):
            return

        service = self.active_service
        self.active_service = None

        if service is not None:
            try:
                window = service.root

                if window.winfo_exists():
                    window.grab_release()
                    window.destroy()

            except (tk.TclError, AttributeError):
                pass

        if self.on_logout:
            self.on_logout()


if __name__ == "__main__":
    root = tk.Tk()

    dashboard = Dashboard(
        root,
        username="Demo User"
    )

    root.mainloop()
