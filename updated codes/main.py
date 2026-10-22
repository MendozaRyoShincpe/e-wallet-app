import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image

from ui.login_page import LoginPage
from ui.dashboard import Dashboard

# ---------- File Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_FILE = os.path.join(BASE_DIR, "CICO.ico")


# ---------- Check Icon File ----------
try:
    with Image.open(ICON_FILE) as img:
        print("Icon format:", img.format)
        print("Icon size:", img.size)
        print("Icon file is readable.")
except Exception as error:
    print("Icon file error:", error)


class CICOApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CICO E-Wallet")
        self.root.geometry("1100x700")
        self.root.minsize(850, 600)
        self.root.configure(bg="#F8F7FF")

        self.current_screen = None

        # Load the application icon
        self.set_window_icon()

        # Handle closing the application
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

        # Show login screen
        self.show_login()

    def set_window_icon(self):
        """Load the CICO application icon."""
        if not os.path.isfile(ICON_FILE):
            print(f"ERROR: Icon file not found: {ICON_FILE}")
            return

        try:
            self.root.iconbitmap(default=ICON_FILE)
            print(f"CICO window icon loaded: {ICON_FILE}")
        except tk.TclError as error:
            print(f"ERROR: Could not load CICO.ico: {error}")

    def clear_screen(self):
        """Remove the current screen widgets."""
        for widget in self.root.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

        self.current_screen = None

    def show_login(self):
        """Display the login screen."""
        self.clear_screen()
        self.root.title("CICO E-Wallet - Login")

        self.current_screen = LoginPage(
            self.root,
            on_success=self.show_dashboard
        )

    def show_dashboard(self, username):
        """Display the dashboard after login."""
        self.clear_screen()
        self.root.title("CICO E-Wallet - Dashboard")

        try:
            self.current_screen = Dashboard(
                self.root,
                username=username,
                on_logout=self.show_login
            )
        except Exception as error:
            import traceback
            traceback.print_exc()

            messagebox.showerror(
                "Dashboard Error",
                f"Unable to open the dashboard:\n\n{error}",
                parent=self.root
            )

            self.show_login()

    def close_app(self):
        """Close the application safely."""
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CICOApp()
    app.run()