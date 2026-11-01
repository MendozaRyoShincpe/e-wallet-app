import os
import sys
import tkinter as tk
from tkinter import messagebox


# ---------- Project Path ----------

# Get the directory containing the main application file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Add the project directory to Python's module search path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)


# ---------- Application Imports ----------

# Import the login and dashboard screens
from ui.login import LoginPage
from ui.dashboard import Dashboard


# ---------- File Paths ----------

# Locate the CICO application icon
ICON_FILE = os.path.join(BASE_DIR, "CICO.ico")


# ---------- Main Application ----------

class CICOApp:

    def __init__(self):
        # Create the main application window
        self.root = tk.Tk()

        self.root.title("CICO E-Wallet")
        self.root.geometry("1100x700")
        self.root.minsize(850, 600)
        self.root.configure(bg="#F8F7FF")

        # Store the currently displayed screen
        self.current_screen = None

        # Set the application icon
        self.set_window_icon()

        # Handle the window's close button
        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close_app
        )

        # Display the login screen when the application starts
        self.show_login()

    # ---------- Window Icon ----------

    def set_window_icon(self):
        # Check whether the application icon exists
        if not os.path.isfile(ICON_FILE):
            print(f"ERROR: Icon file not found: {ICON_FILE}")
            return

        # Apply the CICO icon to the main window
        try:
            self.root.iconbitmap(default=ICON_FILE)
            print(f"CICO window icon loaded: {ICON_FILE}")

        except tk.TclError as error:
            print(f"ERROR: Could not load CICO.ico: {error}")

    # ---------- Screen Management ----------

    def clear_screen(self):
        # Remove all widgets from the current screen
        for widget in self.root.winfo_children():
            try:
                widget.destroy()
            except tk.TclError:
                pass

        # Reset the reference to the current screen
        self.current_screen = None

    # ---------- Login Screen ----------

    def show_login(self):
        # Clear the previous screen before displaying login
        self.clear_screen()

        self.root.title("CICO E-Wallet - Login")

        # Create the login page and connect its success callback
        self.current_screen = LoginPage(
            self.root,
            on_success=self.show_dashboard
        )

    # ---------- Dashboard Screen ----------

    def show_dashboard(self, user):
        # Ensure the received user information is a dictionary
        if not isinstance(user, dict):
            messagebox.showerror(
                "Login Error",
                "Invalid user information.",
                parent=self.root
            )
            self.show_login()
            return

        # Check whether all required account details are available
        required_fields = [
            "account_number",
            "name",
            "phone"
        ]

        missing_fields = [
            field for field in required_fields
            if not user.get(field)
        ]

        if missing_fields:
            messagebox.showerror(
                "Account Error",
                "Missing account information: "
                + ", ".join(missing_fields),
                parent=self.root
            )
            self.show_login()
            return

        # Remove the login screen before opening the dashboard
        self.clear_screen()

        self.root.title("CICO E-Wallet - Dashboard")

        # Initialize the dashboard using the logged-in user's details
        try:
            self.current_screen = Dashboard(
                self.root,
                username=user["name"],
                user=user,
                on_logout=self.show_login
            )

        except Exception as error:
            # Display technical details in the console for debugging
            import traceback
            traceback.print_exc()

            messagebox.showerror(
                "Dashboard Error",
                f"Unable to open the dashboard:\n\n{error}",
                parent=self.root
            )

            # Return to the login screen if dashboard creation fails
            self.show_login()

    # ---------- Close Application ----------

    def close_app(self):
        # Safely destroy the main application window
        try:
            self.root.destroy()

        except tk.TclError:
            pass

    # ---------- Run Application ----------

    def run(self):
        # Start Tkinter's event loop
        self.root.mainloop()


# ---------- Application Entry Point ----------

if __name__ == "__main__":
    # Create the application object and start the program
    app = CICOApp()
    app.run()