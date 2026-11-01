import os
import json
import secrets
import tempfile

from decimal import Decimal, InvalidOperation
from datetime import datetime


# ==================================================
# DATABASE LOCATIONS
# ==================================================

# Define the project directory and locations of database files
BASE = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE, "database")
WALLETS_FILE = os.path.join(DATABASE_DIR, "wallets.json")
USERS_FILE = os.path.join(DATABASE_DIR, "users.txt")


class Wallet:
    """Manages CICO account balances and transactions."""

    def __init__(self, initial_balance="0.00"):
        # Initialize the wallet balance using amount validation
        self.balance = self._validate_amount(
            initial_balance,
            allow_zero=True
        )

        # Store the active user's transactions and account information
        self.transactions = []
        self.account_number = None
        self.account_name = None
        self.contact_number = None

    # ==================================================
    # AMOUNT VALIDATION
    # ==================================================

    @staticmethod
    def _validate_amount(amount, allow_zero=False):
        # Convert the entered amount into a Decimal value
        try:
            value = Decimal(str(amount).strip())

        except (InvalidOperation, ValueError, TypeError, AttributeError):
            raise ValueError("Please enter a valid amount.")

        # Reject infinity and NaN values
        if not value.is_finite():
            raise ValueError("Amount must be a valid number.")

        # Prevent negative amounts and zero when not allowed
        if value < 0 or (value == 0 and not allow_zero):
            raise ValueError("Amount must be greater than zero.")

        # Restrict monetary values to two decimal places
        if value.as_tuple().exponent < -2:
            raise ValueError(
                "Amount cannot have more than 2 decimal places."
            )

        return value

    # ==================================================
    # ACCOUNT NUMBER VALIDATION
    # ==================================================

    @staticmethod
    def _validate_account_number(account_number):
        # Convert the account number into a cleaned string
        account_number = str(account_number).strip()

        # Validate the format of the Philippine mobile number
        if (
            not account_number.isascii()
            or not account_number.isdigit()
            or len(account_number) != 11
            or not account_number.startswith("09")
        ):
            raise ValueError(
                "Invalid CICO Account Number. "
                "Please enter an 11-digit Philippine mobile number "
                "starting with 09."
            )

        return account_number

    # ==================================================
    # TRANSACTION HISTORY VALIDATION
    # ==================================================

    @staticmethod
    def _validate_transactions(transactions):
        # Ensure transaction history is stored as a list
        if not isinstance(transactions, list):
            raise ValueError(
                "Wallet transaction history is invalid."
            )

        # Ensure every transaction record is a dictionary
        if not all(isinstance(item, dict) for item in transactions):
            raise ValueError(
                "Wallet transaction records are invalid."
            )

        return transactions

    # ==================================================
    # DATABASE OPERATIONS
    # ==================================================

    def _load_all_wallets(self):
        # Create the database directory if it does not exist
        os.makedirs(DATABASE_DIR, exist_ok=True)

        # Return an empty dictionary when no wallet database exists
        if not os.path.exists(WALLETS_FILE):
            return {}

        # Read and validate all saved wallet records
        try:
            with open(WALLETS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError("Invalid wallet database format.")

            return data

        except (json.JSONDecodeError, OSError) as error:
            raise ValueError(
                "Wallet database could not be read. "
                "Please check database/wallets.json."
            ) from error

    def _save_all_wallets(self, wallets):
        """Save all wallets using atomic file replacement."""

        # Ensure the database directory exists before saving
        os.makedirs(DATABASE_DIR, exist_ok=True)

        temp_path = None

        try:
            # Write updated wallet data into a temporary file first
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=DATABASE_DIR,
                delete=False
            ) as file:

                json.dump(wallets, file, indent=4)
                file.flush()
                os.fsync(file.fileno())

                temp_path = file.name

            # Replace the old database with the completed temporary file
            os.replace(temp_path, WALLETS_FILE)

        except (OSError, TypeError, ValueError) as error:

            # Remove the temporary file if saving fails
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

            raise ValueError(
                "Unable to save wallet data. Please try again."
            ) from error

    def _load_all_users(self):
        """Load registered accounts from users.txt."""

        # Check whether the registered user database exists
        if not os.path.exists(USERS_FILE):
            raise ValueError(
                "User database could not be found. "
                "Please register an account first."
            )

        # Read and validate the registered user records
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as file:
                users = json.load(file)

            if not isinstance(users, list):
                raise ValueError("Invalid user database format.")

            return users

        except (json.JSONDecodeError, OSError) as error:
            raise ValueError(
                "User database could not be read."
            ) from error

    def _find_user(self, account_number):
        """Find a registered user using their CICO Account Number."""

        # Validate the account number before searching
        account_number = self._validate_account_number(
            account_number
        )

        # Search the registered users for the matching account
        for user in self._load_all_users():

            if not isinstance(user, dict):
                continue

            saved_number = str(
                user.get("account_number", "")
            ).strip()

            if saved_number == account_number:
                return user

        return None

    # ==================================================
    # USER MANAGEMENT
    # ==================================================

    def set_user(self, user):
        """Load the wallet belonging to the logged-in user."""

        # Ensure valid user information is provided
        if not isinstance(user, dict):
            raise ValueError("Invalid user information.")

        # Validate the account number of the logged-in user
        account_number = self._validate_account_number(
            user.get("account_number", "")
        )

        # Confirm that the account exists in the registered user database
        registered_user = self._find_user(account_number)

        if registered_user is None:
            raise ValueError(
                "This CICO account number is not registered."
            )

        # Load all existing wallet records
        wallets = self._load_all_wallets()

        # Restore the saved wallet if the account already has one
        if account_number in wallets:

            saved = wallets[account_number]

            if not isinstance(saved, dict):
                raise ValueError(
                    "Invalid saved wallet information."
                )

            balance = self._validate_amount(
                saved.get("balance", "0.00"),
                allow_zero=True
            )

            transactions = self._validate_transactions(
                saved.get("transactions", [])
            )

        else:

            # Initialize wallet information from the registered account
            balance = self._validate_amount(
                registered_user.get("balance", "0.00"),
                allow_zero=True
            )

            transactions = self._validate_transactions(
                registered_user.get("transactions", [])
            )

        # Assign the retrieved information to the active wallet
        self.balance = balance
        self.transactions = transactions
        self.account_number = account_number

        self.account_name = registered_user.get(
            "name",
            registered_user.get("account_name", "User")
        )

        # The registered phone number is the CICO Account Number.
        self.contact_number = str(
            registered_user.get("phone", "")
        )

        # Save the initialized or restored wallet information
        self._save_current_wallet()

    def clear_user(self):
        """Clear the active wallet session."""

        # Reset the wallet information when the user logs out
        self.balance = Decimal("0.00")
        self.transactions = []
        self.account_number = None
        self.account_name = None
        self.contact_number = None

    # ==================================================
    # WALLET SAVING
    # ==================================================

    def _save_current_wallet(self):
        # Prevent saving when no account is currently assigned
        if self.account_number is None:
            raise ValueError(
                "No user is currently assigned to the wallet."
            )

        # Load existing wallets and update the active account
        wallets = self._load_all_wallets()

        wallets[self.account_number] = {
            "balance": str(self.balance),
            "transactions": self.transactions
        }

        self._save_all_wallets(wallets)

    def _save_wallet_state(self, balance, transactions):
        """Save wallet changes before updating memory."""

        # Ensure a user is logged in before modifying wallet information
        if self.account_number is None:
            raise ValueError(
                "Please log in before performing a transaction."
            )

        # Prepare the updated wallet information
        wallets = self._load_all_wallets()

        wallets[self.account_number] = {
            "balance": str(balance),
            "transactions": transactions
        }

        # Save to the database before updating the active wallet
        self._save_all_wallets(wallets)

        self.balance = balance
        self.transactions = transactions

    # ==================================================
    # TRANSACTION REFERENCES
    # ==================================================

    @staticmethod
    def _generate_reference(wallets=None):
        """Generate a unique CICO transaction reference."""

        # Collect existing references to avoid duplicate transaction IDs
        existing_references = set()

        if wallets:

            for saved_wallet in wallets.values():

                if not isinstance(saved_wallet, dict):
                    continue

                for transaction in saved_wallet.get(
                    "transactions", []
                ):

                    if not isinstance(transaction, dict):
                        continue

                    reference = transaction.get("reference")

                    if reference:
                        existing_references.add(reference)

        # Generate a new reference until an unused one is found
        while True:

            now = datetime.now()

            reference = (
                f"CICO{now:%Y%m%d%H%M%S}"
                f"{secrets.randbelow(900000) + 100000}"
            )

            if reference not in existing_references:
                return reference

    # ==================================================
    # TRANSACTION RECORD CREATION
    # ==================================================

    @staticmethod
    def _create_transaction(
        transaction_type,
        amount,
        balance_after,
        description,
        reference
    ):
        # Get the current date and time for the transaction record
        now = datetime.now()

        # Return the transaction details as a dictionary
        return {
            "reference": reference,
            "type": transaction_type,
            "amount": str(amount),
            "balance_after": str(balance_after),
            "description": description,
            "date": now.strftime("%Y-%m-%d %H:%M:%S")
        }

    # ==================================================
    # BALANCE OPERATIONS
    # ==================================================

    def get_balance(self):
        # Return the current wallet balance
        return self.balance

    def deposit(self, amount, description="Cash In"):
        """Add money to the active wallet."""

        # Ensure a user is logged in before depositing money
        if self.account_number is None:
            raise ValueError("Please log in first.")

        # Validate the deposit amount
        amount = self._validate_amount(amount)

        if not isinstance(description, str):
            description = ""

        # Calculate the new balance after the deposit
        new_balance = self.balance + amount

        # Load saved wallets and generate a transaction reference
        wallets = self._load_all_wallets()

        reference = self._generate_reference(wallets)

        # Create a record for the deposit transaction
        transaction = self._create_transaction(
            "Cash In",
            amount,
            new_balance,
            description,
            reference
        )

        # Add the new transaction to the existing transaction history
        new_transactions = self.transactions + [transaction]

        # Save the updated balance and transaction history
        self._save_wallet_state(
            new_balance,
            new_transactions
        )

        return self.balance

    def withdraw(
        self,
        amount,
        transaction_type="Withdrawal",
        description=""
    ):
        """Remove money from the active wallet."""

        # Ensure a user is logged in before withdrawing money
        if self.account_number is None:
            raise ValueError("Please log in first.")

        # Validate the withdrawal amount
        amount = self._validate_amount(amount)

        # Check whether the wallet has enough funds
        if amount > self.balance:
            raise ValueError(
                f"Insufficient balance. "
                f"Available balance: ₱{self.balance:,.2f}"
            )

        if not isinstance(description, str):
            description = ""

        # Calculate the new balance after withdrawal
        new_balance = self.balance - amount

        # Load saved wallets and generate a transaction reference
        wallets = self._load_all_wallets()

        reference = self._generate_reference(wallets)

        # Create a record for the withdrawal transaction
        transaction = self._create_transaction(
            transaction_type,
            amount,
            new_balance,
            description,
            reference
        )

        # Add the withdrawal record to the transaction history
        new_transactions = self.transactions + [transaction]

        # Save the updated wallet information
        self._save_wallet_state(
            new_balance,
            new_transactions
        )

        return self.balance

    # ==================================================
    # TRANSACTION HISTORY
    # ==================================================

    def _record_transaction(
        self,
        transaction_type,
        amount,
        description=""
    ):
        """Record a transaction in the active wallet history."""

        # Ensure a user is logged in before recording a transaction
        if self.account_number is None:
            raise ValueError("Please log in first.")

        # Generate a reference for the transaction
        wallets = self._load_all_wallets()

        reference = self._generate_reference(wallets)

        # Create a transaction record using the current balance
        transaction = self._create_transaction(
            transaction_type,
            amount,
            self.balance,
            description,
            reference
        )

        self.transactions.append(transaction)

    def get_transactions(self):
        """Return transaction amounts as Decimal values."""

        # Create a separate list to avoid modifying stored records
        result = []

        for transaction in self.transactions:

            item = transaction.copy()

            # Convert monetary values from strings into Decimal objects
            for field in ("amount", "balance_after"):

                if field in item:
                    item[field] = Decimal(str(item[field]))

            result.append(item)

        return result

    # ==================================================
    # MONEY TRANSFER
    # ==================================================

    def transfer(
        self,
        recipient_account_number,
        amount,
        description=""
    ):
        """
        Transfer money to another registered CICO account.

        The recipient's registered phone number is their
        CICO Account Number and is the transfer identifier.
        """

        # Ensure the sender is logged in
        if self.account_number is None:
            raise ValueError(
                "Please log in before sending money."
            )

        # Validate the recipient's CICO Account Number
        recipient_account_number = self._validate_account_number(
            recipient_account_number
        )

        # Prevent users from sending money to their own accounts
        if recipient_account_number == self.account_number:
            raise ValueError(
                "You cannot send money to your own account."
            )

        # Validate the amount being transferred
        amount = self._validate_amount(amount)

        if not isinstance(description, str):
            description = ""

        # Confirm that the recipient is a registered CICO user
        recipient = self._find_user(recipient_account_number)

        if recipient is None:
            raise ValueError(
                "Recipient CICO account does not exist."
            )

        # Load the latest wallet records.
        wallets = self._load_all_wallets()

        # Get the sender's latest saved wallet.
        sender_wallet = wallets.get(
            self.account_number,
            {
                "balance": str(self.balance),
                "transactions": self.transactions
            }
        )

        if not isinstance(sender_wallet, dict):
            raise ValueError(
                "Sender wallet data is invalid."
            )

        # Validate the sender's saved balance and transaction history
        sender_balance = self._validate_amount(
            sender_wallet.get("balance", "0.00"),
            allow_zero=True
        )

        sender_transactions = self._validate_transactions(
            sender_wallet.get("transactions", [])
        )

        # Check whether the sender has enough money
        if amount > sender_balance:
            raise ValueError(
                f"Insufficient balance. "
                f"Available balance: ₱{sender_balance:,.2f}"
            )

        # Get the recipient's latest saved wallet.
        recipient_wallet = wallets.get(
            recipient_account_number,
            {
                "balance": str(
                    recipient.get("balance", "0.00")
                ),
                "transactions": recipient.get("transactions", [])
            }
        )

        if not isinstance(recipient_wallet, dict):
            raise ValueError(
                "Recipient wallet data is invalid."
            )

        # Validate the recipient's saved balance and transaction history
        recipient_balance = self._validate_amount(
            recipient_wallet.get("balance", "0.00"),
            allow_zero=True
        )

        recipient_transactions = self._validate_transactions(
            recipient_wallet.get("transactions", [])
        )

        # Calculate new balances.
        sender_new_balance = sender_balance - amount
        recipient_new_balance = recipient_balance + amount

        # Generate one reference for both transactions.
        reference = self._generate_reference(wallets)

        # Get the recipient's registered name
        recipient_name = recipient.get(
            "name",
            recipient.get("account_name", "Recipient")
        )

        # Use the provided description or create a default sender description
        sender_description = description.strip()

        if not sender_description:
            sender_description = (
                f"Money sent to {recipient_name} "
                f"({recipient_account_number})"
            )

        # Prepare the description shown in the recipient's history
        recipient_description = (
            f"Money received from account {self.account_number}"
        )

        # Create sender transaction.
        sender_transaction = self._create_transaction(
            "Send Money",
            amount,
            sender_new_balance,
            sender_description,
            reference
        )

        # Create recipient transaction.
        recipient_transaction = self._create_transaction(
            "Received Money",
            amount,
            recipient_new_balance,
            recipient_description,
            reference
        )

        # Add the new transaction to the sender's history
        sender_transactions = sender_transactions + [
            sender_transaction
        ]

        # Add the new transaction to the recipient's history
        recipient_transactions = recipient_transactions + [
            recipient_transaction
        ]

        # Prepare both wallet records.
        wallets[self.account_number] = {
            "balance": str(sender_new_balance),
            "transactions": sender_transactions
        }

        wallets[recipient_account_number] = {
            "balance": str(recipient_new_balance),
            "transactions": recipient_transactions
        }

        # Save both wallet changes together.
        self._save_all_wallets(wallets)

        # Update the active sender wallet after saving succeeds.
        self.balance = sender_new_balance
        self.transactions = sender_transactions

        # Return transfer details for the interface and receipt
        return {
            "reference": reference,
            "amount": amount,
            "sender_balance": sender_new_balance,
            "recipient_balance": recipient_new_balance,
            "recipient_name": recipient_name,
            "recipient_account_number": recipient_account_number
        }


# ==================================================
# SHARED WALLET INSTANCE
# ==================================================

# Create one shared wallet object used throughout the application
wallet = Wallet()