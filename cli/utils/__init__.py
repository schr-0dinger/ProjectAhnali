"""CLI utilities."""

from __future__ import annotations

import sys


def echo(message: str, error: bool = False):
    """Print a message to stdout/stderr."""
    if error:
        print(f"ERROR: {message}", file=sys.stderr)
    else:
        print(message)


def die(message: str):
    """Print error and exit."""
    echo(message, error=True)
    sys.exit(1)