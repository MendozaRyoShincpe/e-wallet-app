import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image

from ui.login_page import LoginPage
from ui.dashboard import Dashboard

# Get the file path for the application icon.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_FILE = os.path.join(BASE_DIR, "CICO.ico")


class CICOApp:
    def __init__(self):
        # Initialize the main application window.
        self.root = tk.Tk()
        self.root.title("CICO E-Wallet")
        self.root.geometry("1100x700")
        self.root.minsize(850, 600)
        self.root.configure(bg="#F8F7FF")

        # Track the currently displayed screen.
        self.current_screen = None

        # Set the application icon and handle window closing.
        self.set_window_icon()
        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

        # Display the login page when the app starts.
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
        # Clear existing widgets before switching screens.
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

        # Open the login page and proceed to the dashboard on success.
        self.current_screen = LoginPage(
            self.root,
            on_success=self.show_dashboard
        )

    def show_dashboard(self, username):
        """Display the dashboard after login."""
        self.clear_screen()
        self.root.title("CICO E-Wallet - Dashboard")

        try:
            # Pass the username to the dashboard and connect logout navigation.
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

            # Return to the login screen if the dashboard fails to open.
            self.show_login()

    def close_app(self):
        """Close the application safely."""
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def run(self):
        # Start Tkinter's event loop to keep the application running.
        self.root.mainloop()


# Run the application when this file is executed directly.
if __name__ == "__main__":
    app = CICOApp()
    app.run()
