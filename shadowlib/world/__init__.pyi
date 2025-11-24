"""Type stubs for world namespace."""

from shadowlib.world.ground_items import GroundItems

class World:
    """Namespace for 3D world entities with lazy-loading."""

    ground_items: GroundItems
    # npcs: NPCs  # Add when implemented
    # objects: Objects  # Add when implemented
    # players: Players  # Add when implemented

    def __init__(self, client) -> None: ...

__all__ = ["World"]
