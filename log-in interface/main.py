import tkinter as tk
from ui.login import LoginPage


def main():
    root = tk.Tk()

    # Center the window on the screen
    window_width = 480
    window_height = 700

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    root.geometry(
        f"{window_width}x{window_height}+{x}+{y}"
    )

    # Open the CICO login interface
    LoginPage(root)

    # Start the desktop application
    root.mainloop()


if __name__ == "__main__":
    main()