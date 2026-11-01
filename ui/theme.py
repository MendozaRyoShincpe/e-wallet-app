#--- Theme and utility functions for the CICO app's UI. ---

import os
import tkinter as tk

# Project folder (the one that contains main.py, CICO.png and CICO.ico)
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_FILE = os.path.join(BASE, "CICO.png")
ICON_FILE = os.path.join(BASE, "CICO.ico")

# Colours
PURPLE = "#7040E8"
DARK_PURPLE = "#5930C7"
LIGHT_PURPLE = "#F0EBFF"
WHITE = "#FFFFFF"
BLACK = "#171A35"
BG = "#F8F7FF"
GRAY = "#777C91"
BORDER = "#E2E0ED"
GREEN = "#16805D"
LIGHT_GREEN = "#E8F7EF"
RED = "#D93650"
LIGHT_RED = "#FDECEF"


def apply_icon(window):
    """Give a window the CICO icon (silently skipped if it can't be loaded)."""
    try:
        if os.path.exists(ICON_FILE):
            window.iconbitmap(ICON_FILE)
    except tk.TclError:
        pass


def load_logo(size):
    """Return the CICO logo as a Tk image that fits in size x size pixels."""
    if not os.path.exists(LOGO_FILE):
        return None

    try:
        from PIL import Image, ImageTk

        image = Image.open(LOGO_FILE).convert("RGBA")
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image)
    except Exception as error:  # the logo is cosmetic, never crash on it
        print(f"Could not load CICO logo: {error}")
        return None


def safe_grab(window, tries=10):
    """Make a window modal.

    Some systems refuse grab_set() until the window is visible, so the
    request is retried a few times instead of crashing.
    """
    try:
        window.grab_set()
    except tk.TclError:
        if tries <= 0:
            return
        try:
            window.after(50, lambda: safe_grab(window, tries - 1))
        except tk.TclError:
            pass


def center_on(window, parent):
    """Place a window in the middle of its parent window."""
    try:
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        if width <= 1:
            width = window.winfo_reqwidth()
        if height <= 1:
            height = window.winfo_reqheight()

        x = parent.winfo_rootx() + (parent.winfo_width() - width) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - height) // 2
        window.geometry(f"+{max(x, 0)}+{max(y, 0)}")
    except tk.TclError:
        pass
