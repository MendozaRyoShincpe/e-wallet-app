import hashlib
import hmac
import os
import re
import secrets

# Project folder (same folder as main.py)
BASE = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE, "users.txt")
REMEMBER_FILE = os.path.join(BASE, "data", "remembered_user.txt")

# ---------- Formatting of the users.txt file ----------
COLUMNS = None

_GUESSED_COLUMNS = {
    2: ["identifier", "password"],
    3: ["account_name", "identifier", "password"],
    4: ["account_number", "account_name", "identifier", "password"],
    5: ["account_number", "account_name", "identifier", "salt", "password_hash"],
    6: ["account_number", "account_name", "email", "phone", "salt", "password_hash"],
}

_PHONE_JUNK = re.compile(r"[\s\-()]")
_EMAIL_RE = re.compile(r"^[^@\s|,;]+@[^@\s|,;]+\.[^@\s|,;]+$")


# ---------- Reading the users file ----------
def _split_line(line):
    """Split on the first delimiter found: | tab ; , (else whitespace)."""
    for delimiter in ("|", "\t", ";", ","):
        if delimiter in line:
            return [part.strip() for part in line.split(delimiter)]
    return line.split()


def _parse_line(line):
    fields = _split_line(line)
    if COLUMNS and len(COLUMNS) == len(fields):
        columns = COLUMNS
    else:
        columns = _GUESSED_COLUMNS.get(len(fields))
    if not columns or len(columns) != len(fields):
        return None
    return dict(zip(columns, fields))


def _is_header(line):
    fields = _split_line(line)
    return ("password" in " ".join(fields).lower()
            and all(re.fullmatch(r"[A-Za-z_ #.]+", f) for f in fields))


def _read_records():
    """Yield every valid line of the users file as a dict."""
    try:
        with open(USERS_FILE, "r", encoding="utf-8-sig") as f:
            lines = [ln.strip() for ln in f if ln.strip()]
    except OSError:
        return

    # Skip a header row such as "email,password"
    if lines and _is_header(lines[0]):
        lines = lines[1:]

    for line in lines:
        record = _parse_line(line)
        if record and (record.get("identifier") or record.get("email")
                       or record.get("phone")):
            yield record


# ---------- Matching the user ----------
def _normalize_phone(value):
    """'+63 917-123-4567' -> '09171234567'. Returns "" if not a phone number."""
    cleaned = _PHONE_JUNK.sub("", value or "")
    if not re.fullmatch(r"\+?\d{10,13}", cleaned):
        return ""
    if cleaned.startswith("+63"):
        cleaned = "0" + cleaned[3:]
    elif cleaned.startswith("63") and len(cleaned) == 12:
        cleaned = "0" + cleaned[2:]
    return cleaned


def _keys(value):
    """Everything a typed value could be compared as (text, or phone number)."""
    value = (value or "").strip().lower()
    return {k for k in (value, _normalize_phone(value)) if k}


def _password_matches(record, password):
    if "password_hash" in record:
        salt = record.get("salt", "")
        attempt = hashlib.sha256((salt + password).encode()).hexdigest()
        return hmac.compare_digest(attempt, record["password_hash"].lower())
    return hmac.compare_digest(
        password.encode(), record.get("password", "").encode()
    )


def _to_user(record):
    """Build the user dict, filling in anything the file doesn't have."""
    ident = record.get("identifier", "")
    email = record.get("email") or (ident if "@" in ident else "")
    phone = record.get("phone") or (
        ident if "@" not in ident and _normalize_phone(ident) else "")
    primary = ident or email or phone

    stable = int(hashlib.sha256(primary.lower().encode()).hexdigest(), 16) % 10**10
    return {
        "account_number": record.get("account_number") or f"CICO-{stable:010d}",
        "account_name": record.get("account_name") or primary,
        "identifier": primary,
        "email": email,
        "phone": phone,
    }


def _user_keys(user):
    """Email, phone number, and wallet ID of a user, ready for comparison."""
    keys = set()
    for field in ("identifier", "email", "phone", "account_number"):
        keys |= _keys(user.get(field))
    return keys


# ---------- Public API ----------
def users_file_exists():
    return os.path.exists(USERS_FILE)


def authenticate(identifier, password):
    """Log in with email, phone number, or wallet ID.

    Returns the user dict or None.
    """
    typed = _keys(identifier)
    for record in _read_records():
        user = _to_user(record)
        if not typed & _user_keys(user):
            continue
        if not _password_matches(record, password):
            return None
        return user
    return None


def find_user(query):
    """Look a user up by email, phone number, or wallet ID (no password).

    Used by Send Money to find the recipient.
    """
    typed = _keys(query)
    if not typed:
        return None
    for record in _read_records():
        user = _to_user(record)
        if typed & _user_keys(user):
            return user
    return None

# ---------- Registering a new user ----------
def register_user(full_name, email, phone, password, confirm=None):

    name = " ".join((full_name or "").split())
    email = (email or "").strip()
    phone = _normalize_phone(phone or "")

    if len(name) < 2 or "|" in name:
        raise ValueError("Please enter your full name.")
    if not _EMAIL_RE.match(email):
        raise ValueError("Please enter a valid email address.")
    if not phone:
        raise ValueError(
            "Please enter a valid phone number, for example 09171234567."
        )
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters.")
    if confirm is not None and password != confirm:
        raise ValueError("Passwords do not match.")

    users = [_to_user(record) for record in _read_records()]
    for user in users:
        keys = _user_keys(user)
        if email.lower() in keys:
            raise ValueError("That email address is already registered.")
        if phone in keys:
            raise ValueError("That phone number is already registered.")

    # Generate a wallet ID that nobody has
    taken = {user["account_number"].lower() for user in users}
    while True:
        wallet_id = "CICO-" + "".join(secrets.choice("0123456789") for _ in range(10))
        if wallet_id.lower() not in taken:
            break

    salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + password).encode()).hexdigest()
    line = "|".join([wallet_id, name, email, phone, salt, digest])

    # If the file doesn't end with a newline, add one first
    needs_newline = False
    if os.path.exists(USERS_FILE) and os.path.getsize(USERS_FILE) > 0:
        with open(USERS_FILE, "rb") as f:
            f.seek(-1, os.SEEK_END)
            needs_newline = f.read(1) != b"\n"

    with open(USERS_FILE, "a", encoding="utf-8") as f:
        if needs_newline:
            f.write("\n")
        f.write(line + "\n")

    return {
        "account_number": wallet_id,
        "account_name": name,
        "identifier": email,
        "email": email,
        "phone": phone,
    }


# ---------- "Remembers the user" ----------
def get_remembered_identifier():
    """The email/phone/wallet ID saved by 'Remember me' (never a password)."""
    try:
        with open(REMEMBER_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def set_remembered_identifier(identifier):
    """Save the identifier, or forget it when given an empty value."""
    try:
        if identifier:
            os.makedirs(os.path.dirname(REMEMBER_FILE), exist_ok=True)
            with open(REMEMBER_FILE, "w", encoding="utf-8") as f:
                f.write(identifier)
        elif os.path.exists(REMEMBER_FILE):
            os.remove(REMEMBER_FILE)
    except OSError:
        pass
