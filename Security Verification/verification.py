import tkinter as tk
from tkinter import messagebox

def verify_security_password():
  
    root = tk.Tk()
    root.title("Security Verification")
    root.geometry("300x180")
    root.resizable(False, False)

    try:
        root.iconbitmap("pythonico.ico")
    except Exception:
        print("Icon file not found.")
    
    instruction_label = tk.Label(root, text="Please enter your security password:")
    instruction_label.pack(pady=10)
    

    password_entry = tk.Entry(root, show="*", width=25)
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


    submit_button = tk.Button(root, text="Submit", command=check_password, width=10)
    submit_button.pack(pady=10)
    

    root.mainloop()

if __name__ == "__main__":
    verify_security_password()