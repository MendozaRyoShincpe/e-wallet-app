import tkinter as tk
from tkinter import messagebox

from verification import verification
from wallet import wallet  # shared wallet, so all windows use one balance
from ui.theme import (
    PURPLE, DARK_PURPLE, WHITE, BLACK, BG, GRAY, BORDER,
    apply_icon, load_logo, safe_grab, center_on
)


# Base class: every wallet service window reuses the header, balance card,
# form helpers and security verification defined here.
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
        self.on_back = on_back  # runs when the window is closed with X
        self.on_balance_change = on_balance_change  # refreshes the dashboard

        self.root = tk.Toplevel(parent)
        self.root.title(f"CICO - {title}")
        self.root.geometry("430x680")
        self.root.minsize(400, 680)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        apply_icon(self.root)

        # Keep a reference to the logo so Tkinter doesn't discard it
        self.logo_image = load_logo(38)

        self.build_header(title, subtitle)

        self.content = tk.Frame(self.root, bg=BG, padx=20, pady=15)
        self.content.pack(fill="both", expand=True)

        self.build_balance_card()

        tk.Label(
            self.root,
            text="CICO E-Wallet | Demo Application",
            font=("Arial", 8), bg=BG, fg=GRAY
        ).pack(pady=(0, 8))

        # Modal: the user must finish this window first
        self.root.transient(parent)
        center_on(self.root, parent)
        safe_grab(self.root)

    # ---------- Header and balance ----------
    def build_header(self, title, subtitle):
        header = tk.Frame(self.root, bg=PURPLE, padx=20, pady=14)
        header.pack(fill="x")

        brand_row = tk.Frame(header, bg=PURPLE)
        brand_row.pack(fill="x")

        if self.logo_image is not None:
            tk.Label(
                brand_row, image=self.logo_image, bg=PURPLE
            ).pack(side="left", padx=(0, 8))

        tk.Label(
            brand_row, text="CICO", font=("Arial", 20, "bold"),
            bg=PURPLE, fg=WHITE
        ).pack(side="left")

        tk.Button(
            brand_row, text="✕", command=self.close,
            font=("Arial", 12, "bold"), bg=PURPLE, fg=WHITE,
            activebackground=DARK_PURPLE, activeforeground=WHITE,
            relief="flat", bd=0, cursor="hand2"
        ).pack(side="right")

        tk.Label(
            header, text=title, font=("Arial", 17, "bold"),
            bg=PURPLE, fg=WHITE
        ).pack(anchor="w", pady=(10, 2))

        tk.Label(
            header, text=subtitle, font=("Arial", 9),
            bg=PURPLE, fg=WHITE
        ).pack(anchor="w")

    def build_balance_card(self):
        card = tk.Frame(
            self.content, bg=WHITE,
            highlightbackground=BORDER, highlightthickness=1,
            padx=14, pady=10
        )
        card.pack(fill="x", pady=(0, 14))

        tk.Label(
            card, text="AVAILABLE BALANCE", font=("Arial", 9, "bold"),
            bg=WHITE, fg=GRAY
        ).pack(anchor="w")

        self.balance_label = tk.Label(
            card, text="₱0.00", font=("Arial", 21, "bold"),
            bg=WHITE, fg=PURPLE
        )
        self.balance_label.pack(anchor="w", pady=(4, 0))
        self.update_balance()

    def update_balance(self):
        # Safe to call even if the window was already destroyed
        try:
            self.balance_label.config(text=f"₱{wallet.get_balance():,.2f}")
        except (tk.TclError, AttributeError):
            pass

    # ---------- Form helpers ----------
    def build_form_card(self, title):
        # Card for the child classes to put their fields in
        card = tk.Frame(
            self.content, bg=WHITE,
            highlightbackground=BORDER, highlightthickness=1,
            padx=15, pady=14
        )
        card.pack(fill="both", expand=True)

        tk.Label(
            card, text=title, font=("Arial", 13, "bold"),
            bg=WHITE, fg=BLACK
        ).pack(anchor="w", pady=(0, 12))

        self.form_card = card
        return card

    def field(self, parent, label, placeholder):
        # Labeled input with a simulated placeholder
        tk.Label(
            parent, text=label, font=("Arial", 9, "bold"),
            bg=WHITE, fg=BLACK
        ).pack(anchor="w", pady=(0, 4))

        entry = tk.Entry(
            parent, font=("Arial", 10), bg=WHITE, fg=GRAY,
            insertbackground=BLACK, relief="solid", bd=1
        )
        entry.pack(fill="x", ipady=6, pady=(0, 9))
        entry.insert(0, placeholder)
        entry.placeholder = placeholder  # lets value() detect placeholder text

        def focus_in(event):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=BLACK)

        def focus_out(event):
            if not entry.get().strip():
                entry.delete(0, tk.END)
                entry.insert(0, placeholder)
                entry.config(fg=GRAY)

        entry.bind("<FocusIn>", focus_in)
        entry.bind("<FocusOut>", focus_out)
        return entry

    @staticmethod
    def value(entry):
        # Returns "" if the field only shows the placeholder
        value = entry.get().strip()
        return "" if value == entry.placeholder else value

    def button(self, parent, text, command, primary=True):
        # primary = filled purple, otherwise outlined
        return tk.Button(
            parent, text=text, command=command,
            bg=PURPLE if primary else WHITE,
            fg=WHITE if primary else PURPLE,
            activebackground=DARK_PURPLE if primary else BG,
            activeforeground=WHITE if primary else DARK_PURPLE,
            font=("Arial", 10, "bold"),
            relief="flat" if primary else "solid",
            bd=0 if primary else 1,
            highlightbackground=BORDER,
            cursor="hand2", pady=10
        )

    # ---------- Security verification ----------
    def verify_password(self, callback, parent=None):
        """Ask for a one-time code, then run callback() if it is correct.

        parent is the window the dialog should appear over (defaults to
        this service window).
        """
        parent = parent or self.root
        account_number = wallet.account_number

        dialog = tk.Toplevel(parent)
        dialog.title("Security Verification")
        dialog.geometry("340x320")
        dialog.resizable(False, False)
        dialog.configure(bg=BG)
        dialog.transient(parent)
        apply_icon(dialog)

        tk.Label(
            dialog, text="Security Verification",
            font=("Arial", 14, "bold"), bg=BG, fg=BLACK
        ).pack(pady=(20, 6))

        tk.Label(
            dialog, text="Enter the 6-digit verification code.",
            font=("Arial", 9), bg=BG, fg=GRAY
        ).pack()

        # Demo only: a real app would send this to the user's phone or email
        code_label = tk.Label(
            dialog, text="", font=("Arial", 16, "bold"), bg=BG, fg=PURPLE
        )
        code_label.pack(pady=10)

        entry = tk.Entry(dialog, font=("Arial", 14), justify="center")
        entry.pack(fill="x", padx=25, ipady=7)
        entry.focus_set()

        def new_code():
            try:
                code = verification.issue(account_number)
            except PermissionError as error:  # account is locked out
                messagebox.showerror(
                    "Verification Locked", str(error), parent=dialog
                )
                dialog.destroy()
                return False

            code_label.config(text=f"Demo code: {code}")
            entry.delete(0, tk.END)
            entry.focus_set()
            return True

        def verify():
            ok, message = verification.check(account_number, entry.get())

            if ok:
                dialog.destroy()
                callback()
                return

            messagebox.showerror("Verification Failed", message, parent=dialog)
            entry.delete(0, tk.END)

            # Close on lockout; offer a fresh code if the old one expired
            if "Locked" in message or "Too many" in message:
                dialog.destroy()
            elif "expired" in message or "No active" in message:
                new_code()
            else:
                entry.focus_set()

        self.button(dialog, "Verify and Continue", verify).pack(
            fill="x", padx=25, pady=(14, 6)
        )
        self.button(dialog, "Send New Code", new_code, primary=False).pack(
            fill="x", padx=25
        )
        entry.bind("<Return>", lambda event: verify())

        # Generate the first code; skip the dialog if the account is locked
        if new_code():
            center_on(dialog, parent)
            safe_grab(dialog)

    # ---------- Closing the window ----------
    def show_receipt(self, title, details):
        messagebox.showinfo(title, details, parent=self.root)

    def notify_balance_changed(self):
        # Call after a transaction: refresh here and on the dashboard
        self.update_balance()

        if self.on_balance_change:
            self.on_balance_change()

    def close(self):
        try:
            if self.root.winfo_exists():
                try:
                    self.root.grab_release()  # release the modal lock first
                except tk.TclError:
                    pass

                self.root.destroy()
        except tk.TclError:
            pass

        if self.on_back:
            self.on_back()

        # Run the back callback if one was provided.
        if self.on_back:
            self.on_back()
