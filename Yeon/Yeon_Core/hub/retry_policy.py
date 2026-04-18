"""Simple retry policy for Hub send operations."""
import time

MAX_ATTEMPTS = 3
BACKOFF_SEC = [1, 2, 4]


def attempt(send_fn, *args) -> tuple:
    """Try send_fn up to MAX_ATTEMPTS with exponential backoff.
    Returns (success:bool, attempts:int).
    """
    for i in range(MAX_ATTEMPTS):
        if send_fn(*args):
            return True, i + 1
        if i < MAX_ATTEMPTS - 1:
            time.sleep(BACKOFF_SEC[i])
    return False, MAX_ATTEMPTS
