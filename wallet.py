from decimal import Decimal, InvalidOperation
from datetime import datetime
import random


class Wallet:
    """Manages the wallet balance and transaction history."""

    def __init__(self, initial_balance="1000.00"):
        # Initialize the wallet with a starting balance and empty history.
        self.balance = self._validate_amount(
            initial_balance,
            allow_zero=True
        )
        self.transactions = []

    @staticmethod
    def _validate_amount(amount, allow_zero=False):
        # Convert the input into Decimal for accurate money calculations.
        try:
            value = Decimal(str(amount))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("Please enter a valid amount.")

        # Reject invalid numbers, negative amounts, and zero when not allowed.
        if not value.is_finite():
            raise ValueError("Amount must be a valid number.")

        if value < 0 or (value == 0 and not allow_zero):
            raise ValueError("Amount must be greater than zero.")

        # Allow a maximum of two decimal places for monetary values.
        if value.as_tuple().exponent < -2:
            raise ValueError(
                "Amount cannot have more than 2 decimal places."
            )

        return value

    def get_balance(self):
        # Return the current wallet balance.
        return self.balance

    def deposit(self, amount, description="Cash In"):
        # Add money to the wallet and record the transaction.
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
        # Validate the amount and check if the balance is sufficient.
        amount = self._validate_amount(amount)

        if amount > self.balance:
            raise ValueError(
                f"Insufficient balance. "
                f"Available balance: ₱{self.balance:,.2f}"
            )

        # Deduct the amount and record the transaction.
        self.balance -= amount

        self._record_transaction(
            transaction_type,
            amount,
            description
        )
        return self.balance

    def _record_transaction(self, transaction_type, amount, description):
        # Generate a timestamp and a unique-looking transaction reference.
        now = datetime.now()
        reference = (
            f"CICO{now:%Y%m%d%H%M%S}"
            f"{random.randint(100, 999)}"
        )

        # Save the transaction details in the transaction history.
        self.transactions.append({
            "reference": reference,
            "type": transaction_type,
            "amount": amount,
            "balance_after": self.balance,
            "description": description,
            "date": now.strftime("%Y-%m-%d %H:%M:%S"),
        })

    def get_transactions(self):
        # Return a copy of the transaction list to protect the original list.
        return list(self.transactions)


# Use one shared Wallet object across all services
# so deposits, withdrawals, and transfers update the same balance.
wallet = Wallet("1000.00")
