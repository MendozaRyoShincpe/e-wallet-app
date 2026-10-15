import tkinter as tk
from tkinter import messagebox


PURPLE = "#6A1B9A"
DARK_PURPLE = "#4A148C"
WHITE = "#FFFFFF"


def verify_security_password():

    root = tk.Tk()
    root.title("Security Verification")
    root.geometry("320x240")
    root.resizable(False, False)
    root.configure(bg=WHITE)

    try:
        root.iconbitmap("CICO.ico")
    except Exception:
        print("Icon file not found.")

    # Header
    header = tk.Frame(root, bg=PURPLE, height=60)
    header.pack(fill="x")
    header.pack_propagate(False)

    header_label = tk.Label(
        header,
        text="Security Verification",
        bg=PURPLE,
        fg=WHITE,
        font=("Segoe UI", 14, "bold"),
    )
    header_label.pack(expand=True)

    # Body
    instruction_label = tk.Label(
        root,
        text="Please enter your security password:",
        bg=WHITE,
        fg=PURPLE,
        font=("Segoe UI", 10),
    )
    instruction_label.pack(pady=(20, 10))

    password_entry = tk.Entry(
        root,
        show="*",
        width=25,
        relief="solid",
        bd=1,
        highlightthickness=2,
        highlightbackground=PURPLE,
        highlightcolor=DARK_PURPLE,
    )
    password_entry.pack(pady=5)
    password_entry.focus()

    def check_password():
        password = password_entry.get()
        if password == "secure123":
            messagebox.showinfo("Access Granted", "Welcome! You have successfully verified your security password.")
            root.destroy()
        else:
            messagebox.showerror("Access Denied", "Incorrect password. Please try again.")
            password_entry.delete(0, tk.END)

    submit_button = tk.Button(
        root,
        text="Submit",
        command=check_password,
        width=10,
        bg=PURPLE,
        fg=WHITE,
        activebackground=DARK_PURPLE,
        activeforeground=WHITE,
        font=("Segoe UI", 10, "bold"),
        relief="flat",
        cursor="hand2",
    )
    submit_button.pack(pady=15)

    root.mainloop()


if __name__ == "__main__":
    verify_security_password()