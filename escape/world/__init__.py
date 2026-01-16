"""Game viewport entities - NPCs, objects, players, items visible in 3D world."""

from escape.world.ground_items import GroundItems, groundItems
from escape.world.projection import (
    CameraState,
    EntityConfig,
    EntityTransform,
    Projection,
    TileGrid,
    projection,
)
from escape.world.scene import Scene, VisibleTiles, scene


class World:
    """3D world entities: ground items, scene, and projection utilities."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def groundItems(self) -> GroundItems:
        """Ground items on visible tiles."""
        return groundItems

    @property
    def projection(self) -> Projection:
        """3D to 2D screen projection utilities."""
        return projection

    @property
    def scene(self) -> Scene:
        """Scene and visible tiles management."""
        return scene


# Module-level instance
world = World()


__all__ = [
    "World",
    "world",
    "GroundItems",
    "groundItems",
    "Projection",
    "TileGrid",
    "projection",
    "Scene",
    "scene",
    "VisibleTiles",
    "CameraState",
    "EntityConfig",
    "EntityTransform",
]
