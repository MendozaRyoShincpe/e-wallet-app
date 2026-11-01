import hashlib
import hmac
import secrets
import time


# ---------- Verification Settings ----------

# Configure the verification code and account security limits
CODE_LENGTH = 6
CODE_LIFETIME = 120
MAX_ATTEMPTS = 3
LOCKOUT_SECONDS = 60


# ---------- Code Generation ----------

def generate_code(length=CODE_LENGTH):
    """Generate a random numeric verification code."""

    # Generate a secure random numeric code using the secrets module
    return "".join(
        secrets.choice("0123456789")
        for _ in range(length)
    )


def _digest(code):
    """Convert the verification code into a SHA-256 digest."""

    # Hash the code instead of storing its original value
    return hashlib.sha256(
        code.encode()
    ).hexdigest()


# ---------- Verification Service ----------

class VerificationService:
    """Issues and checks one-time codes for each account."""

    def __init__(self):
        # Store pending codes, failed attempts, and account lockout times
        self._pending = {}
        self._failures = {}
        self._locked_until = {}

    def lock_remaining(self, account_number):
        """Check how many seconds remain before an account is unlocked."""

        # Convert the account number into a dictionary key
        key = str(account_number)

        # Calculate the remaining lockout time using a monotonic clock
        remaining = (
            self._locked_until.get(key, 0)
            - time.monotonic()
        )

        if remaining > 0:
            return int(remaining) + 1

        # Clear expired lockout information and reset failed attempts
        if key in self._locked_until:
            del self._locked_until[key]
            self._failures.pop(key, None)

        return 0

    def issue(self, account_number):
        """Generate a new verification code for an account."""

        key = str(account_number)

        # Prevent code generation while the account is locked
        wait = self.lock_remaining(key)

        if wait:
            raise PermissionError(
                f"Too many failed attempts. "
                f"Try again in {wait} seconds."
            )

        # Generate a new code and store its digest with its expiration time
        code = generate_code()

        self._pending[key] = {
            "digest": _digest(code),
            "expires": time.monotonic() + CODE_LIFETIME
        }

        return code

    def check(self, account_number, entered):
        """Validate a code and return its result and message."""

        key = str(account_number)

        # Check whether the account is currently locked
        wait = self.lock_remaining(key)

        if wait:
            return False, (
                f"Too many failed attempts. "
                f"Try again in {wait} seconds."
            )

        # Retrieve the pending verification code for the account
        entry = self._pending.get(key)

        if entry is None:
            return False, (
                "No active code. Please request a new one."
            )

        # Reject the code if its validity period has expired
        if time.monotonic() > entry["expires"]:
            del self._pending[key]

            return False, (
                "That code expired. Please request a new one."
            )

        # Hash and securely compare the entered code with the stored digest
        if hmac.compare_digest(
            _digest(entered.strip()),
            entry["digest"]
        ):
            # Remove the used code and reset failed attempts
            del self._pending[key]

            self._failures.pop(key, None)

            return True, ""

        # Count incorrect attempts
        self._failures[key] = (
            self._failures.get(key, 0) + 1
        )

        # Lock the account after reaching the maximum number of attempts
        if self._failures[key] >= MAX_ATTEMPTS:
            self._pending.pop(key, None)

            self._locked_until[key] = (
                time.monotonic() + LOCKOUT_SECONDS
            )

            return False, (
                f"Too many failed attempts. "
                f"Locked for {LOCKOUT_SECONDS} seconds."
            )

        # Calculate how many attempts remain
        attempts_left = (
            MAX_ATTEMPTS - self._failures[key]
        )

        return False, (
            f"Incorrect code. "
            f"{attempts_left} attempt(s) left."
        )


# ---------- Shared Verification Instance ----------

# Create one shared verification service for the application
verification = VerificationService()