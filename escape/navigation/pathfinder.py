"""
Pathfinder for navigation.
"""

from ..types.packed_position import PackedPosition
from ..types.path import Path


class Pathfinder:
    """Pathfinder for calculating routes between locations."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        """Actual initialization, runs once."""
        pass

    def getPath(
        self,
        destination_x: int,
        destination_y: int,
        destination_plane: int,
        use_transport: bool = True,
    ) -> Path | None:
        """Calculate path to destination."""
        from escape.client import client

        dest_packed = PackedPosition(destination_x, destination_y, destination_plane).packed

        result = client.api.invokeCustomMethod(
            target="Pathfinder",
            method="getPathWithObstaclesPacked",
            signature="(I)[B",
            args=[dest_packed],
            async_exec=True,
        )

        if not result or "path" not in result:
            return None

        return Path.fromDict(result)

    def getPathFromPosition(
        self,
        start_x: int,
        start_y: int,
        start_plane: int,
        destination_x: int,
        destination_y: int,
        destination_plane: int,
        use_transport: bool = True,
    ) -> Path | None:
        """Calculate path from specific start position to destination."""
        # For now, use the simpler method
        # TODO: Extend Java bridge to support custom start positions
        return self.getPath(destination_x, destination_y, destination_plane, use_transport)

    def canReach(
        self,
        destination_x: int,
        destination_y: int,
        destination_plane: int,
        use_transport: bool = True,
    ) -> bool:
        """Check if destination is reachable."""
        path = self.getPath(destination_x, destination_y, destination_plane, use_transport)
        return path is not None and not path.isEmpty()


# Module-level instance
pathfinder = Pathfinder()
