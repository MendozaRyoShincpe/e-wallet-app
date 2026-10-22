import tkinter as tk

from ui.login_page import LoginPage
from ui.dashboard import Dashboard


class CICOApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CICO E-Wallet")
        self.root.geometry("1100x700")
        self.root.minsize(850, 600)

        self.show_login()

    def show_login(self):
        self.root.title("CICO E-Wallet - Login")
        LoginPage(
            self.root,
            on_success=self.show_dashboard
        )

    def show_dashboard(self, username):
        Dashboard(
            self.root,
            username=username,
            on_logout=self.show_login
        )

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = CICOApp()
    app.run()
