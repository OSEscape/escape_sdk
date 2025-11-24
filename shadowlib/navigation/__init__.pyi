"""Type stubs for navigation namespace."""

from shadowlib.navigation.pathfinder import Pathfinder

class Navigation:
    """Namespace for navigation systems with lazy-loading."""

    pathfinder: Pathfinder
    # walker: Walker  # Add when implemented
    # teleports: Teleports  # Add when implemented

    def __init__(self, client) -> None: ...

__all__ = ["Navigation", "Pathfinder"]
