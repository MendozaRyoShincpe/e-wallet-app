from decimal import Decimal, InvalidOperation
from datetime import datetime
import random


class Wallet:
    """Shared in-memory wallet for the CICO demo application."""

    def __init__(self, initial_balance="1000.00"):
        self.balance = self._validate_amount(
            initial_balance,
            allow_zero=True
        )
        self.transactions = []

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

    def get_balance(self):
        return self.balance

    def deposit(self, amount, description="Cash In"):
        amount = self._validate_amount(amount)
        self.balance += amount

        self._record_transaction(
            "Cash In",
            amount,
            description
        )
        return self.balance

    def withdraw(self, amount, transaction_type="Withdrawal",
                 description=""):
        amount = self._validate_amount(amount)

        if amount > self.balance:
            raise ValueError(
                f"Insufficient balance. "
                f"Available balance: ₱{self.balance:,.2f}"
            )

        self.balance -= amount

        self._record_transaction(
            transaction_type,
            amount,
            description
        )
        return self.balance

    def _record_transaction(self, transaction_type, amount, description):
        now = datetime.now()
        reference = (
            f"CICO{now:%Y%m%d%H%M%S}"
            f"{random.randint(100, 999)}"
        )

        self.transactions.append({
            "reference": reference,
            "type": transaction_type,
            "amount": amount,
            "balance_after": self.balance,
            "description": description,
            "date": now.strftime("%Y-%m-%d %H:%M:%S"),
        })

    def get_transactions(self):
        return list(self.transactions)


# IMPORTANT:
# Import this same object in every service.
# Do not create another Wallet instance in the service files.
wallet = Wallet("1000.00")