# Import os to handle folders and file paths
import os

# Import json to store and retrieve account information
import json

# Import secrets to generate secure random values
# and safely compare password hashes
import secrets

# Import hashlib to securely hash user passwords
import hashlib


# ==================================================
# DATABASE PATHS
# ==================================================

# Get the main project folder by moving one level up
# from the current file's directory
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define the folder where account data will be stored
DATABASE_DIR = os.path.join(BASE, "database")

# Define the file used to store registered user accounts
DATABASE_FILE = os.path.join(DATABASE_DIR, "users.txt")


# ==================================================
# USER DATABASE
# ==================================================

def load_users():
    # Create the database folder if it does not exist
    os.makedirs(DATABASE_DIR, exist_ok=True)

    # Check if the account database file exists
    if not os.path.exists(DATABASE_FILE):

        # Create a new database file with an empty list
        with open(DATABASE_FILE, "w", encoding="utf-8") as file:
            json.dump([], file)

    try:
        # Open the database file in read mode
        with open(DATABASE_FILE, "r", encoding="utf-8") as file:

            # Convert the JSON data into a Python list
            users = json.load(file)

    # Handle errors when the database contains invalid JSON
    except json.JSONDecodeError as error:
        raise ValueError(
            "The account database is damaged. "
            "Please check database/users.txt."
        ) from error

    # Handle errors when the database file cannot be accessed
    except OSError as error:
        raise ValueError(
            "Unable to access the account database."
        ) from error

    # Make sure the loaded account data is stored as a list
    if not isinstance(users, list):
        raise ValueError("Invalid account database format.")

    # Return the list of registered users
    return users


def save_users(users):
    # Make sure the database folder exists
    os.makedirs(DATABASE_DIR, exist_ok=True)

    # Open the database file in write mode
    with open(DATABASE_FILE, "w", encoding="utf-8") as file:

        # Convert the Python user list into formatted JSON data
        # The indent parameter makes the file easier to read
        json.dump(users, file, indent=4)


# ==================================================
# PASSWORD SECURITY
# ==================================================

def hash_password(password, salt=None):
    # Generate a random 16-byte salt if one was not provided
    # The salt adds extra security to the password hashing process
    if salt is None:
        salt = secrets.token_hex(16)

    # Convert the password into a secure hash using PBKDF2
    # SHA-256 is the hashing algorithm used
    # The password is processed through 200,000 iterations
    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        200_000
    ).hex()

    # Return both the salt and the generated password hash
    return salt, password_hash


def verify_password(password, salt, saved_hash):
    # Check whether the entered password matches the saved password hash
    try:

        # Hash the entered password using the original salt
        _, entered_hash = hash_password(password, salt)

        # Compare the generated hash with the saved hash securely
        # Return True if they match and False otherwise
        return secrets.compare_digest(
            entered_hash,
            saved_hash
        )

    # Handle invalid password data or incorrect input types
    except (TypeError, ValueError, AttributeError):
        return False


# ==================================================
# PHONE NUMBER HANDLING
# ==================================================

def normalize_phone(phone):
    """Normalize Philippine mobile numbers"""

    # Return an empty string if no phone number was provided
    if not phone:
        return ""

    # Keep only the numeric digits from the phone number
    # This removes spaces, dashes, and other special characters
    digits = "".join(
        character for character in str(phone)
        if character.isdigit()
    )

    # Convert the Philippine country code 63 into the local 0 format
    # Example: 639171234567 becomes 09171234567
    if digits.startswith("63") and len(digits) == 12:
        digits = "0" + digits[2:]

    # Return the normalized phone number
    return digits


# ==================================================
# ACCOUNT CREATION
# ==================================================

def create_account(name, email, password, phone=None):
    """
    Create a CICO account

    The registered phone number is also the
    user's CICO account number
    """

    # Load all existing registered accounts
    users = load_users()

    # Remove unnecessary spaces from the name and email
    # Convert the password into a string
    # Normalize the phone number into the standard format
    name = str(name).strip()
    email = str(email).strip()
    password = str(password)
    phone = normalize_phone(phone)

    # Check if any required registration field is empty
    if not name or not email or not password or not phone:
        return None, "Please complete all required fields."

    # Validate the Philippine mobile number
    # It must contain exactly 11 digits and start with 09
    if len(phone) != 11 or not phone.startswith("09"):
        return None, (
            "Please enter a valid 11-digit Philippine mobile number."
        )

    # Check existing accounts to prevent duplicate email addresses
    # and phone numbers or CICO account numbers
    for user in users:

        # Skip database entries that are not dictionaries
        if not isinstance(user, dict):
            continue

        # Get the existing email and ignore letter capitalization
        existing_email = str(
            user.get("email", "")
        ).strip().casefold()

        # Get and normalize the existing phone number
        existing_phone = normalize_phone(
            user.get("phone", "")
        )

        # Get the existing CICO account number
        existing_account = str(
            user.get("account_number", "")
        ).strip()

        # Reject registration if the email is already used
        if existing_email == email.casefold():
            return None, "This email is already registered."

        # Reject registration if the phone number or account number
        # is already registered
        if existing_phone == phone or existing_account == phone:
            return None, (
                "This phone number / CICO account number "
                "is already registered."
            )

    # Generate a unique salt and securely hash the user's password
    salt, password_hash = hash_password(password)

    # Create a dictionary containing the new user's information
    new_user = {
        "account_number": phone,
        "name": name,
        "email": email,
        "phone": phone,
        "salt": salt,
        "password_hash": password_hash,
        "balance": "0.00",
        "transactions": []
    }

    # Add the newly registered account to the user list
    users.append(new_user)

    try:
        # Save the updated user list into the database file
        save_users(users)

    # Handle errors that occur while saving the account
    except OSError:
        return None, (
            "Unable to save the account. Please try again."
        )

    # Return the newly created account and no error message
    return new_user, None


# ==================================================
# ACCOUNT AUTHENTICATION
# ==================================================

def authenticate(identifier, password):
    """Authenticate using email, phone, or CICO account number"""

    # Remove unnecessary spaces from the login identifier
    # and convert the password into a string
    identifier = str(identifier).strip()
    password = str(password)

    # Reject login attempts if the identifier or password is empty
    if not identifier or not password:
        return None

    # Normalize the identifier in case the user entered a phone number
    normalized_identifier = normalize_phone(identifier)

    # Load all registered accounts and check each user
    for user in load_users():

        # Skip invalid database entries
        if not isinstance(user, dict):
            continue

        # Retrieve the registered email address
        # casefold() allows case-insensitive email comparison
        email = str(
            user.get("email", "")
        ).strip().casefold()

        # Retrieve and normalize the registered phone number
        phone = normalize_phone(
            user.get("phone", "")
        )

        # Retrieve the registered CICO account number
        account_number = str(
            user.get("account_number", "")
        ).strip()

        # Check if the entered identifier matches any
        # registered email, phone number, or account number
        matches = (
            identifier.casefold() == email
            or (
                bool(normalized_identifier)
                and normalized_identifier == phone
            )
            or identifier == account_number
        )

        # Skip the account if the identifier does not match
        if not matches:
            continue

        # Verify the entered password against the saved password hash
        if verify_password(
            password,
            user.get("salt"),
            user.get("password_hash")
        ):

            # Return the account information if authentication succeeds
            return user

    # Return None if no matching account or password is found
    return None


# ==================================================
# FIND ACCOUNT
# ==================================================

def find_user(query):
    """Find a user by CICO account number, email, or phone"""

    # Remove unnecessary spaces from the search input
    query = str(query).strip()

    # Normalize the input in case it is a phone number
    normalized_query = normalize_phone(query)

    # Search through all registered accounts
    for user in load_users():

        # Skip invalid database entries
        if not isinstance(user, dict):
            continue

        # Retrieve the registered email address
        email = str(
            user.get("email", "")
        ).strip().casefold()

        # Retrieve and normalize the registered phone number
        phone = normalize_phone(
            user.get("phone", "")
        )

        # Retrieve the registered CICO account number
        account_number = str(
            user.get("account_number", "")
        ).strip()

        # Check whether the search input matches
        # the account number, email, or phone number
        if (
            query == account_number
            or query.casefold() == email
            or (
                bool(normalized_query)
                and normalized_query == phone
            )
        ):

            # Return the matching user's account information
            return user

    # Return None if no matching account is found
    return None