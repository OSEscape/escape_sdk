"""Automatic cleanup utilities for RuneLite bridge resources."""

import atexit
import functools
import sys
from collections.abc import Callable

from escape._internal.logger import logger

# Global tracking of resources that need cleanup
_registered_apis = []
_cleanup_registered = False


def registerApiForCleanup(api) -> None:
    """Register a RuneLiteAPI instance for automatic cleanup on exit."""
    global _cleanup_registered

    if api not in _registered_apis:
        _registered_apis.append(api)

    # Register atexit handler on first registration
    if not _cleanup_registered:
        atexit.register(_cleanupAll)
        _cleanup_registered = True


def _cleanupAll():
    """Internal cleanup handler called by atexit."""
    if not _registered_apis:
        return

    logger.info("\n Auto-cleanup: Shutting down RuneLite bridge resources")

    # Event consumer cleanup is handled by Client.disconnect()
    # which is called automatically via context manager or explicit disconnect

    logger.info("Cleanup complete")


def withCleanup(func: Callable) -> Callable:
    """Decorator that ensures cleanup runs even on exception."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            # Ensure cleanup runs even on exception
            _cleanupAll()

    return wrapper


def ensureCleanupOnSignal():
    """Register signal handlers to ensure cleanup on SIGINT and SIGTERM."""
    import signal

    def signalHandler(signum, frame):
        logger.warning(f"\n Received signal {signum}, cleaning up")
        _cleanupAll()
        sys.exit(0)

    signal.signal(signal.SIGINT, signalHandler)
    signal.signal(signal.SIGTERM, signalHandler)
    logger.success("Cleanup registered for SIGINT and SIGTERM")


class CleanupContext:
    """Context manager for automatic cleanup."""

    def __init__(self):
        self.api = None

    def register(self, api) -> None:
        """Register an API instance for cleanup."""
        self.api = api

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup everything."""
        # Don't suppress exceptions
        return False
