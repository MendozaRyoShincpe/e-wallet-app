import json
import os
import random
import tempfile
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import session

# Balances and transactions for every account, saved between runs.
DATA_FILE = Path(__file__).resolve().parent / "wallet_data.txt"


class Wallet:
    """Shared wallet object for the CICO demo application.

    There is still ONE Wallet object, but every method works on the account
    of the user who is currently logged in (see session.py). Each account has
    its own balance and its own transaction list.
    """

    def __init__(self, initial_balance="1000.00", data_file=DATA_FILE):
        # Starting balance given to every NEW account
        self.initial_balance = self._validate_amount(
            initial_balance,
            allow_zero=True
        )
        self.data_file = Path(data_file)
        self._accounts = self._load()   # {account_number: {balance, transactions}}

# ---------- Internal helpers ----------
    @staticmethod
    def _validate_amount(amount, allow_zero=False):
        try:
            value = Decimal(str(amount))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Please enter a valid amount.")

        if not value.is_finite():
            raise ValueError("Amount must be a valid number.")

        if value < 0 or (value == 0 and not allow_zero):
            raise ValueError("Amount must be greater than zero.")

        if value.as_tuple().exponent < -2:
            raise ValueError(
                "Amount cannot have more than 2 decimal places."
            )

        return value

# ---------- Internal storage ----------
    def _load(self):
        if not self.data_file.exists():
            return {}

        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                raw = json.load(f)

            accounts = {}
            for number, data in raw.items():
                transactions = []
                for t in data["transactions"]:
                    t = dict(t)
                    t["amount"] = Decimal(t["amount"])
                    t["balance_after"] = Decimal(t["balance_after"])
                    transactions.append(t)
                accounts[number] = {
                    "balance": Decimal(data["balance"]),
                    "transactions": transactions,
                }
            return accounts

        except (json.JSONDecodeError, KeyError, InvalidOperation,
                TypeError, AttributeError):
            # Keep the unreadable file instead of overwriting it
            backup = self.data_file.with_suffix(
                f".corrupt-{datetime.now():%Y%m%d%H%M%S}.json"
            )
            os.replace(self.data_file, backup)
            return {}

    def _save(self):
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_path = tempfile.mkstemp(
            dir=self.data_file.parent, suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(self._accounts, f, indent=2, default=str)
            os.replace(tmp_path, self.data_file)    # atomic swap
        except Exception:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            raise

# --------- Internal account access ----------

    def _get_or_create(self, number):
        """Return the account with this number, creating it if it is new."""
        if number not in self._accounts:
            self._accounts[number] = {
                "balance": self.initial_balance,
                "transactions": [],
            }
            self._save()
        return self._accounts[number]

    def _account(self):
        """Return the logged-in user's account, creating it on first use."""
        user = session.get_user()
        if not user:
            raise ValueError("No user is logged in.")
        return self._get_or_create(user["account_number"])

    @property
    def account_name(self):
        user = session.get_user()
        return user["account_name"] if user else None

    @property
    def account_number(self):
        user = session.get_user()
        return user["account_number"] if user else None

    @property
    def balance(self):
        return self.get_balance()

    @property
    def transactions(self):
        return self.get_transactions()

# ---------- Public methods for the logged-in user ----------

    def get_balance(self):
        try:
            return self._account()["balance"]
        except ValueError:                  # nobody logged in
            return Decimal("0.00")

    def deposit(self, amount, description="Cash In"):
        account = self._account()
        amount = self._validate_amount(amount)
        account["balance"] += amount

        self._record_transaction(account, "Cash In", amount, description)
        return account["balance"]

    def withdraw(self, amount, transaction_type="Withdrawal",
                 description=""):
        account = self._account()
        amount = self._validate_amount(amount)

        if amount > account["balance"]:
            raise ValueError(
                f"Insufficient balance. "
                f"Available balance: ₱{account['balance']:,.2f}"
            )

        account["balance"] -= amount

        self._record_transaction(
            account, transaction_type, amount, description
        )
        return account["balance"]

# --------- Public methods for sending money between accounts ----------
    def transfer(self, amount, recipient_account_number,
                 description_out="", description_in=""):
        """Move money from the logged-in user to another account.

        The sender gets a "Send Money" transaction and the recipient gets a
        "Money Received" one. Both are saved together in a single write.
        Returns the sender's new balance.
        """
        sender = self._account()
        amount = self._validate_amount(amount)

        if str(recipient_account_number) == self.account_number:
            raise ValueError("You cannot send money to yourself.")

        if amount > sender["balance"]:
            raise ValueError(
                f"Insufficient balance. "
                f"Available balance: ₱{sender['balance']:,.2f}"
            )

        recipient = self._get_or_create(str(recipient_account_number))

        sender["balance"] -= amount
        self._record_transaction(
            sender, "Send Money", amount, description_out, save=False
        )

        recipient["balance"] += amount
        self._record_transaction(
            recipient, "Money Received", amount, description_in, save=False
        )

        self._save()
        return sender["balance"]

    def _record_transaction(self, account, transaction_type, amount,
                            description, save=True):
        now = datetime.now()
        reference = (
            f"CICO{now:%Y%m%d%H%M%S}"
            f"{random.randint(100, 999)}"
        )

        account["transactions"].append({
            "reference": reference,
            "type": transaction_type,
            "amount": amount,
            "balance_after": account["balance"],
            "description": description,
            "date": now.strftime("%Y-%m-%d %H:%M:%S"),
        })
        if save:
            self._save()

    def get_transactions(self):
        try:
            return list(self._account()["transactions"])
        except ValueError:                  # nobody logged in
            return []


# IMPORTANT:
# Use one shared Wallet object across all services
# so deposits, withdrawals, and transfers update the same balance.
wallet = Wallet("1000.00")
