"""Global access to Client (deprecated: use escape.client instead)."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from escape._internal.cache.event_cache import EventCache


def getClient():
    """Get the Client instance (deprecated)."""
    from escape.client import client

    return client


def getApi():
    """Get the RuneLiteAPI instance."""
    from escape._internal.api import RuneLiteAPI

    return RuneLiteAPI()


def getEventCache() -> "EventCache":
    """Get the EventCache instance from the Client."""
    from escape.client import client

    return client.cache


# Convenience exports
__all__ = [
    "getApi",
    "getClient",
    "getEventCache",
]
