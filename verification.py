import hashlib
import hmac
import secrets
import time

CODE_LENGTH = 6
CODE_LIFETIME = 120     # seconds before a code expires
MAX_ATTEMPTS = 3        # wrong guesses allowed before lockout
LOCKOUT_SECONDS = 60


def generate_code(length=CODE_LENGTH):
    return "".join(secrets.choice("0123456789") for _ in range(length))


def _digest(code):
    return hashlib.sha256(code.encode()).hexdigest()


class VerificationService:
    """Issues and checks one-time codes, keyed by account number."""

    def __init__(self):
        self._pending = {}       # account_number -> {"digest", "expires"}
        self._failures = {}      # account_number -> wrong attempts so far
        self._locked_until = {}  # account_number -> monotonic timestamp

    def lock_remaining(self, account_number):
        key = str(account_number)
        remaining = self._locked_until.get(key, 0) - time.monotonic()
        if remaining > 0:
            return int(remaining) + 1
        if key in self._locked_until:          # lock expired, start fresh
            del self._locked_until[key]
            self._failures.pop(key, None)
        return 0

    def issue(self, account_number):
        """Create a new code for this account. Replaces any earlier one."""
        key = str(account_number)
        wait = self.lock_remaining(key)
        if wait:
            raise PermissionError(
                f"Too many failed attempts. Try again in {wait} seconds."
            )
        code = generate_code()
        self._pending[key] = {
            "digest": _digest(code),
            "expires": time.monotonic() + CODE_LIFETIME,
        }
        return code

    def check(self, account_number, entered):
        """Return (ok, message). A code works once, for its own account only."""
        key = str(account_number)

        wait = self.lock_remaining(key)
        if wait:
            return False, f"Too many failed attempts. Try again in {wait} seconds."

        entry = self._pending.get(key)
        if entry is None:
            return False, "No active code. Please request a new one."

        if time.monotonic() > entry["expires"]:
            del self._pending[key]
            return False, "That code expired. Please request a new one."

        if hmac.compare_digest(_digest(entered.strip()), entry["digest"]):
            del self._pending[key]             # single use
            self._failures.pop(key, None)
            return True, ""

        # Failures are counted per account, not per code, so requesting
        # a new code does not reset the limit.
        self._failures[key] = self._failures.get(key, 0) + 1
        if self._failures[key] >= MAX_ATTEMPTS:
            self._pending.pop(key, None)
            self._locked_until[key] = time.monotonic() + LOCKOUT_SECONDS
            return False, (f"Too many failed attempts. "
                           f"Locked for {LOCKOUT_SECONDS} seconds.")

        left = MAX_ATTEMPTS - self._failures[key]
        return False, f"Incorrect code. {left} attempt(s) left."


verification = VerificationService()   # one shared instance for the app