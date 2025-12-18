"""
Global access to Client singleton.

Deprecated: Prefer importing directly from escape_sdk.client

    from escape_sdk.client import client

This module is kept for backwards compatibility.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from escape_sdk._internal.cache.event_cache import EventCache


def getClient():
    """
    Get the singleton Client instance.

    Deprecated: Use `from escape_sdk.client import client` instead.

    Returns:
        Client: The singleton client instance
    """
    from escape_sdk.client import client

    return client


def getApi():
    """
    Get the singleton RuneLiteAPI instance.

    Returns:
        RuneLiteAPI: The singleton API instance
    """
    from escape_sdk._internal.api import RuneLiteAPI

    return RuneLiteAPI()


def getEventCache() -> "EventCache":
    """
    Get the EventCache instance from the Client singleton.

    Returns:
        EventCache: The event cache with game state and event history
    """
    from escape_sdk.client import client

    return client.cache


# Convenience exports
__all__ = [
    "getApi",
    "getClient",
    "getEventCache",
]
