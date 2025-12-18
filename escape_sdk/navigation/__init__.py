"""Navigation module."""

from escape_sdk.navigation.pathfinder import Pathfinder, pathfinder
from escape_sdk.navigation.walker import Walker, walker


class Navigation:
    """
    Namespace for navigation systems - returns singleton instances.

    Example:
        from escape_sdk.client import client

        # Get a path
        path = client.navigation.pathfinder.getPath(3200, 3200, 0)

        # Walk to destination
        client.navigation.walker.walkTo(3165, 3487)

        # Or directly:
        from escape_sdk.navigation.pathfinder import pathfinder
        from escape_sdk.navigation.walker import walker

        path = pathfinder.getPath(3200, 3200, 0)
        walker.walkTo(3165, 3487)
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def pathfinder(self) -> Pathfinder:
        """Get pathfinder singleton."""
        return pathfinder

    @property
    def walker(self) -> Walker:
        """Get walker singleton."""
        return walker


# Module-level singleton instance
navigation = Navigation()


__all__ = ["Navigation", "navigation", "Pathfinder", "pathfinder", "Walker", "walker"]
