# ============================================================
# Small utility functions for ARPO.
# ============================================================

from datetime import datetime


def timestamp():

    # ============================================================
    # Return a readable timestamp for terminal and log messages.
    # ============================================================

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
